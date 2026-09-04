import pandas as pd
import numpy as np
import os


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REPORT_PERIOD = "2026-07"

DATA_DIR = os.path.join(BASE_DIR, "data")

SALES_FILE = os.path.join(DATA_DIR, "sales_invoices.csv")
PAYROLL_FILE = os.path.join(DATA_DIR, "payroll.csv")
TAX_FILE = os.path.join(DATA_DIR, "tax_records.csv")
TALLY_FILE = os.path.join(DATA_DIR, "tally_ledger.csv")

BANK_FILE = os.path.join(DATA_DIR, "bank_transactions.csv")

AR_REPORT_FILE = os.path.join(
    BASE_DIR,
    "accounts_receivable_report.csv"
)

AP_REPORT_FILE = os.path.join(
    BASE_DIR,
    "accounts_payable_report.csv"
)

OUTPUT_DETAIL = os.path.join(
    BASE_DIR,
    "tally_books_verification.csv"
)

OUTPUT_SUMMARY = os.path.join(
    BASE_DIR,
    "tally_books_summary.csv"
)


# ============================================================
# DISPLAY HELPERS
# ============================================================

def money(value):
    if pd.isna(value):
        value = 0

    return f"₹{float(value):,.2f}"


def line():
    print("=" * 70)


def section(title):
    print()
    line()
    print(title)
    line()


# ============================================================
# DATA HELPERS
# ============================================================

def numeric(series):
    """
    Safely convert values to numeric.
    Handles commas, ₹ symbols, blanks and NaN.
    """

    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.strip()
        .replace({
            "": np.nan,
            "nan": np.nan,
            "None": np.nan
        }),
        errors="coerce"
    ).fillna(0)


def clean_columns(df):

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    return df


def load_csv(filename, required_columns=None):

    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"Required file not found: {filename}"
        )

    df = pd.read_csv(filename)

    df = clean_columns(df)

    if required_columns:

        missing = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing:
            raise ValueError(
                f"\nFile: {filename}\n"
                f"Missing columns: {missing}\n"
                f"Available columns: {list(df.columns)}"
            )

    return df


# ============================================================
# PERIOD HELPERS
# ============================================================

def filter_date_period(df, date_column, period):

    if df.empty:
        return df.copy()

    if date_column not in df.columns:

        print(
            f"WARNING: '{date_column}' not found. "
            f"Using empty period dataset."
        )

        return df.iloc[0:0].copy()

    temp = df.copy()

    temp[date_column] = pd.to_datetime(
        temp[date_column],
        errors="coerce"
    )

    start_date = pd.Timestamp(
        f"{period}-01"
    )

    end_date = (
        start_date
        + pd.offsets.MonthEnd(1)
    )

    temp = temp[
        (temp[date_column] >= start_date)
        &
        (temp[date_column] <= end_date)
    ]

    return temp


def filter_period_column(df, period_column, period):

    if df.empty:
        return df.copy()

    if period_column not in df.columns:

        print(
            f"WARNING: '{period_column}' not found. "
            f"Using empty period dataset."
        )

        return df.iloc[0:0].copy()

    temp = df.copy()

    temp[period_column] = (
        temp[period_column]
        .astype(str)
        .str.strip()
        .str[:7]
    )

    return temp[
        temp[period_column] == str(period)
    ].copy()


# ============================================================
# ACCOUNT NORMALIZATION
# ============================================================

def normalize_account(value):

    if pd.isna(value):
        return ""

    value = str(value).strip().lower()

    replacements = {

        "sales":
            "sales revenue",

        "sales revenue":
            "sales revenue",

        "accounts receivable":
            "accounts receivable",

        "account receivable":
            "accounts receivable",

        "ar":
            "accounts receivable",

        "accounts payable":
            "accounts payable",

        "account payable":
            "accounts payable",

        "ap":
            "accounts payable",

        "staff expense":
            "staff expense",

        "salary expense":
            "staff expense",

        "employee expense":
            "staff expense",

        "salaries":
            "staff expense",

        "gst payable":
            "gst payable",

        "gst":
            "gst payable",

        "bank":
            "bank account",

        "bank account":
            "bank account"
    }

    return replacements.get(
        value,
        value
    )


# ============================================================
# START
# ============================================================

print()
line()
print("                 NOURISH CAFE")
print("        PERIOD-AWARE TALLY VERIFICATION")
line()

print()
print(
    f"Reporting Period : {REPORT_PERIOD}"
)


# ============================================================
# LOAD DATA
# ============================================================

try:

    sales = load_csv(
        SALES_FILE,
        [
            "invoice_date",
            "invoice_total"
        ]
    )

    payroll = load_csv(
        PAYROLL_FILE,
        [
            "gross_salary",
            "net_salary"
        ]
    )

    tax = load_csv(
        TAX_FILE,
        [
            "period",
            "books_tax_amount",
            "reported_tax_amount"
        ]
    )

    tally = load_csv(
        TALLY_FILE,
        [
            "period",
            "account",
            "closing_balance"
        ]
    )

except Exception as e:

    print()
    print("ERROR WHILE LOADING DATA")
    print("----------------------------------------")
    print(e)

    raise SystemExit(1)


# ============================================================
# PERIOD FILTERING
# ============================================================

sales_period = filter_date_period(
    sales,
    "invoice_date",
    REPORT_PERIOD
)

tax_period = filter_period_column(
    tax,
    "period",
    REPORT_PERIOD
)

tally_period = filter_period_column(
    tally,
    "period",
    REPORT_PERIOD
)

# Payroll dataset does not contain a period/date column
payroll_period = payroll.copy()


# ============================================================
# PERIOD CHECK
# ============================================================

section("PERIOD CHECK")

print(
    f"Sales records in period   : {len(sales_period)}"
)

print(
    f"Payroll records            : {len(payroll_period)}"
)

print(
    f"Tax records in period      : {len(tax_period)}"
)

print(
    f"Tally records in period    : {len(tally_period)}"
)


# ============================================================
# PERIOD DATA VALIDATION
# ============================================================

if len(sales_period) == 0:

    print(
        "\nWARNING: No sales transactions found "
        f"for {REPORT_PERIOD}"
    )

if len(tax_period) == 0:

    print(
        "\nWARNING: No tax records found "
        f"for {REPORT_PERIOD}"
    )

if len(tally_period) == 0:

    print(
        "\nWARNING: No Tally records found "
        f"for {REPORT_PERIOD}"
    )


# ============================================================
# OPERATIONAL ACCOUNT VALUES
# ============================================================

# ------------------------------------------------------------
# SALES REVENUE
# ------------------------------------------------------------

operational_sales = numeric(
    sales_period["invoice_total"]
).sum()


# ------------------------------------------------------------
# STAFF EXPENSE
# ------------------------------------------------------------

# Gross salary represents salary expense.
# Pending payroll is NOT used here.

operational_staff_expense = numeric(
    payroll_period["gross_salary"]
).sum()


# ------------------------------------------------------------
# GST
# ------------------------------------------------------------

operational_gst = numeric(
    tax_period["books_tax_amount"]
).sum()


# ============================================================
# PREPARE TALLY
# ============================================================

tally_period = tally_period.copy()

tally_period["normalized_account"] = (
    tally_period["account"]
    .apply(normalize_account)
)

tally_period["closing_balance"] = numeric(
    tally_period["closing_balance"]
)

if "debit" in tally_period.columns:

    tally_period["debit"] = numeric(
        tally_period["debit"]
    )

else:

    tally_period["debit"] = 0.0


if "credit" in tally_period.columns:

    tally_period["credit"] = numeric(
        tally_period["credit"]
    )

else:

    tally_period["credit"] = 0.0


if "account_type" in tally_period.columns:

    tally_period["account_type"] = (
        tally_period["account_type"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

else:

    tally_period["account_type"] = ""


# ============================================================
# TALLY ACCOUNT HELPERS
# ============================================================

def get_tally_rows(account_name):

    normalized = normalize_account(
        account_name
    )

    return tally_period[
        tally_period["normalized_account"]
        == normalized
    ].copy()


def tally_closing_balance(account_name):

    rows = get_tally_rows(account_name)

    if rows.empty:
        return 0.0

    return float(
        rows["closing_balance"].sum()
    )


def tally_period_movement(account_name):

    """
    Calculate period movement from debit/credit.

    Revenue accounts:
        Credit - Debit

    Expense accounts:
        Debit - Credit

    Liability / asset accounts:
        handled separately using closing balance.
    """

    rows = get_tally_rows(account_name)

    if rows.empty:
        return 0.0

    debit = rows["debit"].sum()
    credit = rows["credit"].sum()

    account_types = (
        rows["account_type"]
        .astype(str)
        .str.upper()
        .tolist()
    )

    if any(
        "REVENUE" in x
        for x in account_types
    ):

        return float(
            credit - debit
        )

    if any(
        "EXPENSE" in x
        for x in account_types
    ):

        return float(
            debit - credit
        )

    return float(
        credit - debit
    )


# ============================================================
# TALLY VALUES
# ============================================================

tally_sales = tally_period_movement(
    "sales revenue"
)

tally_ar = tally_closing_balance(
    "accounts receivable"
)

tally_ap = tally_closing_balance(
    "accounts payable"
)

tally_staff = tally_period_movement(
    "staff expense"
)

tally_gst = tally_closing_balance(
    "gst payable"
)

tally_bank = tally_closing_balance(
    "bank account"
)


# ============================================================
# OPERATIONAL AR
# ============================================================

operational_ar = 0.0

if os.path.exists(AR_REPORT_FILE):

    ar_report = pd.read_csv(
        AR_REPORT_FILE
    )

    ar_report = clean_columns(
        ar_report
    )

    if "outstanding_amount" in ar_report.columns:

        operational_ar = numeric(
            ar_report["outstanding_amount"]
        ).sum()

else:

    print(
        "\nWARNING: AR report not found."
    )


# ============================================================
# OPERATIONAL AP
# ============================================================

operational_ap = 0.0

if os.path.exists(AP_REPORT_FILE):

    ap_report = pd.read_csv(
        AP_REPORT_FILE
    )

    ap_report = clean_columns(
        ap_report
    )

    if "outstanding_amount" in ap_report.columns:

        operational_ap = numeric(
            ap_report["outstanding_amount"]
        ).sum()

    elif "bill_amount" in ap_report.columns:

        operational_ap = numeric(
            ap_report["bill_amount"]
        ).sum()

else:

    print(
        "\nWARNING: AP report not found."
    )


# ============================================================
# BANK POSITION
# ============================================================

operational_bank = None

if os.path.exists(BANK_FILE):

    bank = pd.read_csv(
        BANK_FILE
    )

    bank = clean_columns(
        bank
    )

    if (
        "amount" in bank.columns
        and "direction" in bank.columns
    ):

        bank["amount"] = numeric(
            bank["amount"]
        )

        bank["direction"] = (
            bank["direction"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        bank_period = filter_date_period(
            bank,
            "txn_date",
            REPORT_PERIOD
        )

        inflows = bank_period.loc[
            bank_period["direction"] == "CREDIT",
            "amount"
        ].sum()

        outflows = bank_period.loc[
            bank_period["direction"] == "DEBIT",
            "amount"
        ].sum()

        # Net movement only.
        operational_bank = (
            inflows - outflows
        )

else:

    print(
        "\nWARNING: Bank transaction file not found."
    )


# ============================================================
# ACCOUNT-LEVEL VERIFICATION
# ============================================================

section("ACCOUNT-LEVEL VERIFICATION")

records = []


def verify_account(
    account,
    operational_amount,
    tally_amount,
    tolerance=1.0
):

    if operational_amount is None:

        return

    difference = (
        float(operational_amount)
        - float(tally_amount)
    )

    if abs(difference) <= tolerance:

        status = "MATCH"

    else:

        status = "MISMATCH"

    records.append({

        "reporting_period":
            REPORT_PERIOD,

        "account":
            account,

        "operational_amount":
            round(
                float(operational_amount),
                2
            ),

        "tally_amount":
            round(
                float(tally_amount),
                2
            ),

        "difference":
            round(
                float(difference),
                2
            ),

        "status":
            status
    })


# ============================================================
# VERIFY FLOW ACCOUNTS
# ============================================================

verify_account(
    "Sales Revenue",
    operational_sales,
    tally_sales
)

verify_account(
    "Staff Expense",
    operational_staff_expense,
    tally_staff
)


# ============================================================
# VERIFY BALANCE ACCOUNTS
# ============================================================

verify_account(
    "Accounts Receivable",
    operational_ar,
    tally_ar
)

verify_account(
    "Accounts Payable",
    operational_ap,
    tally_ap
)

verify_account(
    "GST Payable",
    operational_gst,
    tally_gst
)


# ============================================================
# BANK
# ============================================================

# IMPORTANT:
# Bank transaction data gives period movement,
# while Tally bank gives closing balance.
#
# Therefore they must NOT be directly compared.
# Bank reconciliation is reported separately.

verification = pd.DataFrame(
    records
)


# ============================================================
# PRINT ACCOUNT TABLE
# ============================================================

print()

if not verification.empty:

    print(
        verification[
            [
                "account",
                "operational_amount",
                "tally_amount",
                "difference",
                "status"
            ]
        ].to_string(
            index=False
        )
    )

else:

    print(
        "No account verification records."
    )


# ============================================================
# BANK RECONCILIATION
# ============================================================

section("BANK RECONCILIATION")

print(
    f"Tally closing bank balance : "
    f"{money(tally_bank)}"
)

if operational_bank is not None:

    print(
        f"Bank movement in period   : "
        f"{money(operational_bank)}"
    )

    print(
        "\nBank Status               : "
        "MOVEMENT CHECK ONLY"
    )

    print(
        "Reason                    : "
        "Bank transactions provide period movement, "
        "while Tally provides closing balance."
    )

else:

    print(
        "Bank transaction movement : NOT AVAILABLE"
    )


# ============================================================
# SUMMARY
# ============================================================

total_accounts = len(
    verification
)

matched = int(
    (
        verification["status"]
        == "MATCH"
    ).sum()
) if total_accounts else 0


mismatched = int(
    (
        verification["status"]
        == "MISMATCH"
    ).sum()
) if total_accounts else 0


missing_from_tally = 0

if total_accounts:

    for _, row in verification.iterrows():

        if (
            row["operational_amount"] != 0
            and row["tally_amount"] == 0
        ):

            missing_from_tally += 1


if total_accounts > 0:

    consistency_score = (
        matched / total_accounts
    ) * 100

else:

    consistency_score = 0


if consistency_score >= 90:

    overall_status = "HEALTHY"

elif consistency_score >= 75:

    overall_status = "REVIEW RECOMMENDED"

else:

    overall_status = "REVIEW REQUIRED"


# ============================================================
# BOOKS CONSISTENCY REPORT
# ============================================================

section("BOOKS CONSISTENCY REPORT")


exceptions = verification[
    verification["status"] == "MISMATCH"
].copy()


if exceptions.empty:

    print(
        "No books reconciliation exceptions."
    )

else:

    for _, row in exceptions.iterrows():

        print("-" * 45)

        print(
            f"Account       : {row['account']}"
        )

        print(
            f"Operational   : "
            f"{money(row['operational_amount'])}"
        )

        print(
            f"Tally         : "
            f"{money(row['tally_amount'])}"
        )

        print(
            f"Difference    : "
            f"{money(abs(row['difference']))}"
        )

        print(
            f"Status        : {row['status']}"
        )

        print()

        print(
            "Recommended action:"
        )

        if row["account"] == "Sales Revenue":

            print(
                "Review July sales transactions "
                "and reconcile revenue postings "
                "against the Tally Sales Revenue ledger."
            )

        elif row["account"] == "Staff Expense":

            print(
                "Reconcile July gross salary expense "
                "against the Tally Staff Expense ledger. "
                "Pending payroll should not be treated "
                "as total staff expense."
            )

        elif row["account"] == "Accounts Receivable":

            print(
                "Reconcile customer invoices and "
                "collections against the Tally "
                "Accounts Receivable balance."
            )

        elif row["account"] == "Accounts Payable":

            print(
                "Reconcile supplier bills and payments "
                "against the Tally Accounts Payable balance."
            )

        elif row["account"] == "GST Payable":

            print(
                "Reconcile July GST liability with "
                "tax records and the Tally GST Payable balance."
            )


# ============================================================
# SUMMARY
# ============================================================

section("BOOKS VERIFICATION SUMMARY")

print(
    f"Reporting Period       : {REPORT_PERIOD}"
)

print(
    f"Accounts checked       : {total_accounts}"
)

print(
    f"Matched                : {matched}"
)

print(
    f"Mismatched             : {mismatched}"
)

print(
    f"Missing from Tally     : {missing_from_tally}"
)

print()

print(
    f"Books Consistency Score: "
    f"{consistency_score:.1f}/100"
)

print(
    f"Status                 : "
    f"{overall_status}"
)


# ============================================================
# BOOKS EXCEPTIONS
# ============================================================

section("BOOKS EXCEPTIONS")


if exceptions.empty:

    print(
        "No books reconciliation exceptions."
    )

else:

    for _, row in exceptions.iterrows():

        print("-" * 45)

        print(
            f"Account       : {row['account']}"
        )

        print(
            f"Status        : {row['status']}"
        )

        print(
            f"Operational   : "
            f"{money(row['operational_amount'])}"
        )

        print(
            f"Tally         : "
            f"{money(row['tally_amount'])}"
        )

        print(
            f"Difference    : "
            f"{money(abs(row['difference']))}"
        )


# ============================================================
# MANAGEMENT INTERPRETATION
# ============================================================

section("MANAGEMENT INTERPRETATION")


if mismatched == 0:

    print(
        "All verified accounts are consistent "
        "with the Tally ledger for the reporting period."
    )

    print(
        "Books appear ready for the next "
        "month-end close review."
    )

else:

    print(
        f"{mismatched} account-level discrepancy/"
        f"discrepancies detected."
    )

    print(
        "The books should be reviewed before "
        "month-end close."
    )

    print()

    print(
        "Priority accounts requiring review:"
    )

    for _, row in exceptions.iterrows():

        print(
            f"- {row['account']}: "
            f"{money(abs(row['difference']))} difference"
        )


# ============================================================
# PERIOD ALIGNMENT SUMMARY
# ============================================================

section("PERIOD ALIGNMENT SUMMARY")

print(
    f"Reporting Period : {REPORT_PERIOD}"
)

print(
    "Sales            : July transactions"
)

print(
    "Payroll          : Reporting-period payroll dataset"
)

print(
    "GST              : July tax records"
)

print(
    "AR               : Balance for reporting period"
)

print(
    "AP               : Balance for reporting period"
)

print(
    "Tally            : Tally records where period "
    f"= {REPORT_PERIOD}"
)

print(
    "Bank             : Period movement reported separately"
)


# ============================================================
# SAVE REPORTS
# ============================================================

verification.to_csv(
    OUTPUT_DETAIL,
    index=False
)


summary = pd.DataFrame({

    "reporting_period": [
        REPORT_PERIOD
    ],

    "accounts_checked": [
        total_accounts
    ],

    "matched": [
        matched
    ],

    "mismatched": [
        mismatched
    ],

    "missing_from_tally": [
        missing_from_tally
    ],

    "books_consistency_score": [
        round(
            consistency_score,
            2
        )
    ],

    "status": [
        overall_status
    ]
})


summary.to_csv(
    OUTPUT_SUMMARY,
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

section(
    "PERIOD-AWARE TALLY VERIFICATION COMPLETE"
)

print()

print("Reports saved:")

print(
    f"1. {os.path.basename(OUTPUT_DETAIL)}"
)

print(
    f"2. {os.path.basename(OUTPUT_SUMMARY)}"
)

print()

print(
    "Tally verification completed successfully."
)