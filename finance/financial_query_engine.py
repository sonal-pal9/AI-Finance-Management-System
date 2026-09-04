# ============================================================
# FINANCIAL QUERY ENGINE
# Nourish Cafe - AI Finance Controller
# ============================================================
#
# Purpose:
# Answer financial questions using the data loaded from CSVs.
#
# Handles:
#   - Cash / liquidity
#   - Customer receivables
#   - Supplier payables
#   - Tax / GST
#   - Payroll
#   - Tally reconciliation
#   - Overall financial health
#
# ============================================================

import re
import pandas as pd


# ============================================================
# GENERIC HELPERS
# ============================================================

def money(value):
    """Format a number as Indian Rupees."""

    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0

    sign = "-" if value < 0 else ""

    return f"{sign}₹{abs(value):,.2f}"


def safe_float(value):
    """Safely convert a value to float."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def safe_int(value):
    """Safely convert a value to integer."""

    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def line():
    print("=" * 65)


def section(title):
    print()
    line()
    print(title)
    print("-" * 40)


def find_column(df, possible_columns):
    """
    Find the first matching column from a list of possible names.
    """

    if df is None or df.empty:
        return None

    for column in possible_columns:

        if column in df.columns:
            return column

    return None


def clean_dataframe(df):
    """Return a safe copy of a dataframe."""

    if df is None:
        return pd.DataFrame()

    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()

    result = df.copy()

    result.columns = [
        str(column).strip()
        for column in result.columns
    ]

    return result


# ============================================================
# COLUMN HELPERS
# ============================================================

def get_customer_column(sales):

    return find_column(
        sales,
        [
            "customer",
            "customer_name",
            "client",
            "client_name"
        ]
    )


def get_invoice_amount_column(sales):

    return find_column(
        sales,
        [
            "invoice_total",
            "invoice_amount",
            "total_amount",
            "amount"
        ]
    )


def get_invoice_status_column(sales):

    return find_column(
        sales,
        [
            "book_status",
            "invoice_status",
            "status"
        ]
    )


def get_invoice_id_column(sales):

    return find_column(
        sales,
        [
            "invoice_id",
            "invoice_no",
            "invoice_number"
        ]
    )


def get_customer_payment_amount_column(customer_payments):

    return find_column(
        customer_payments,
        [
            "payment_amount",
            "amount"
        ]
    )


def get_customer_payment_status_column(customer_payments):

    return find_column(
        customer_payments,
        [
            "payment_status",
            "status"
        ]
    )


def get_customer_payment_invoice_column(customer_payments):

    return find_column(
        customer_payments,
        [
            "invoice_id",
            "invoice_no",
            "invoice_number"
        ]
    )


def get_supplier_column(supplier_bills):

    return find_column(
        supplier_bills,
        [
            "supplier",
            "supplier_name",
            "vendor",
            "vendor_name"
        ]
    )


def get_bill_amount_column(supplier_bills):

    return find_column(
        supplier_bills,
        [
            "bill_amount",
            "invoice_amount",
            "amount"
        ]
    )


def get_bill_id_column(supplier_bills):

    return find_column(
        supplier_bills,
        [
            "bill_id",
            "bill_no",
            "invoice_id"
        ]
    )


def get_supplier_payment_amount_column(supplier_payments):

    return find_column(
        supplier_payments,
        [
            "payment_amount",
            "amount"
        ]
    )


def get_supplier_payment_bill_column(supplier_payments):

    return find_column(
        supplier_payments,
        [
            "bill_id",
            "bill_no",
            "invoice_id"
        ]
    )


def get_tax_books_column(tax):

    return find_column(
        tax,
        [
            "books_tax_amount",
            "books_tax"
        ]
    )


def get_tax_reported_column(tax):

    return find_column(
        tax,
        [
            "reported_tax_amount",
            "reported_tax"
        ]
    )


def get_tax_status_column(tax):

    return find_column(
        tax,
        [
            "filing_status",
            "tax_status",
            "status"
        ]
    )


def get_tax_type_column(tax):

    return find_column(
        tax,
        [
            "tax_type"
        ]
    )


def get_payroll_amount_column(payroll):

    return find_column(
        payroll,
        [
            "net_salary",
            "gross_salary",
            "salary",
            "amount"
        ]
    )


def get_payroll_status_column(payroll):

    return find_column(
        payroll,
        [
            "payment_status",
            "status"
        ]
    )


def get_tally_account_column(tally):

    return find_column(
        tally,
        [
            "account",
            "account_name"
        ]
    )


def get_tally_debit_column(tally):

    return find_column(
        tally,
        [
            "debit"
        ]
    )


def get_tally_credit_column(tally):

    return find_column(
        tally,
        [
            "credit"
        ]
    )


def get_tally_balance_column(tally):

    return find_column(
        tally,
        [
            "closing_balance",
            "balance"
        ]
    )


def get_bank_amount_column(bank):

    return find_column(
        bank,
        [
            "amount"
        ]
    )


def get_bank_direction_column(bank):

    return find_column(
        bank,
        [
            "direction"
        ]
    )


def get_bank_reference_column(bank):

    return find_column(
        bank,
        [
            "reference",
            "transaction_reference",
            "ref"
        ]
    )


# ============================================================
# CASH ANALYSIS
# ============================================================
def analyze_cash(data):
    """
    Analyse current cash position.

    Uses:
    - Opening cash balance
    - Bank transaction inflows
    - Bank transaction outflows
    """

    bank = clean_dataframe(
        data.get("bank")
    )

    # Opening cash used by the existing cash engine
    opening_cash = 250000.0

    if bank.empty:

        current_cash = opening_cash

        return {
            "current_cash": current_cash,
            "risk": "LOW",
            "message": (
                f"Available cash is "
                f"{money(current_cash)}."
            )
        }

    amount_col = get_bank_amount_column(bank)
    direction_col = get_bank_direction_column(bank)

    if amount_col is None:

        return {
            "current_cash": opening_cash,
            "risk": "UNKNOWN",
            "message": (
                "Bank amount column could not be identified."
            )
        }

    bank[amount_col] = pd.to_numeric(
        bank[amount_col],
        errors="coerce"
    ).fillna(0)

    if direction_col is not None:

        bank[direction_col] = (
            bank[direction_col]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        inflows = bank.loc[
            bank[direction_col].isin(
                ["CREDIT", "CR", "IN"]
            ),
            amount_col
        ].sum()

        outflows = bank.loc[
            bank[direction_col].isin(
                ["DEBIT", "DR", "OUT"]
            ),
            amount_col
        ].sum()

        current_cash = (
            opening_cash
            + inflows
            - outflows
        )

    else:

        current_cash = (
            opening_cash
            + bank[amount_col].sum()
        )

    if current_cash < 0:

        risk = "CRITICAL"

        message = (
            f"Negative cash position of "
            f"{money(current_cash)}."
        )

    elif current_cash == 0:

        risk = "HIGH"

        message = "No available cash balance."

    else:

        risk = "LOW"

        message = (
            f"Available cash is "
            f"{money(current_cash)}."
        )

    return {
        "current_cash": float(current_cash),
        "risk": risk,
        "message": message
    }
# ============================================================
# RECEIVABLE ANALYSIS
# ============================================================

def analyze_receivables(data):
    """
    Calculate outstanding customer receivables.

    Uses:
        sales_invoices.csv
        customer_payments.csv
    """

    sales = clean_dataframe(
        data.get("sales")
    )

    payments = clean_dataframe(
        data.get("customer_payments")
    )

    if sales.empty:

        return {
            "total_ar": 0.0,
            "outstanding_invoices": 0,
            "customers": {},
            "risk": "UNKNOWN"
        }

    invoice_id_col = get_invoice_id_column(sales)
    amount_col = get_invoice_amount_column(sales)
    customer_col = get_customer_column(sales)

    if amount_col is None:

        return {
            "total_ar": 0.0,
            "outstanding_invoices": 0,
            "customers": {},
            "risk": "UNKNOWN"
        }

    sales[amount_col] = pd.to_numeric(
        sales[amount_col],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # If payment data is unavailable
    # --------------------------------------------------------

    if payments.empty or invoice_id_col is None:

        total_ar = sales[amount_col].sum()

        return {
            "total_ar": float(total_ar),
            "outstanding_invoices": len(sales),
            "customers": {},
            "risk": "HIGH" if total_ar > 0 else "LOW"
        }

    payment_invoice_col = (
        get_customer_payment_invoice_column(payments)
    )

    payment_amount_col = (
        get_customer_payment_amount_column(payments)
    )

    if (
        payment_invoice_col is None
        or payment_amount_col is None
    ):

        total_ar = sales[amount_col].sum()

        return {
            "total_ar": float(total_ar),
            "outstanding_invoices": len(sales),
            "customers": {},
            "risk": "HIGH" if total_ar > 0 else "LOW"
        }

    payments[payment_amount_col] = pd.to_numeric(
        payments[payment_amount_col],
        errors="coerce"
    ).fillna(0)

    paid_by_invoice = (
        payments
        .groupby(payment_invoice_col)[payment_amount_col]
        .sum()
    )

    sales["_paid_amount"] = (
        sales[invoice_id_col]
        .map(paid_by_invoice)
        .fillna(0)
    )

    sales["_outstanding"] = (
        sales[amount_col]
        - sales["_paid_amount"]
    )

    sales["_outstanding"] = (
        sales["_outstanding"]
        .clip(lower=0)
    )

    outstanding = sales[
        sales["_outstanding"] > 0.01
    ]

    total_ar = outstanding[
        "_outstanding"
    ].sum()

    # --------------------------------------------------------
    # Customer-level balances
    # --------------------------------------------------------

    customers = {}

    if customer_col is not None:

        customer_groups = (
            outstanding
            .groupby(customer_col)["_outstanding"]
            .sum()
            .sort_values(ascending=False)
        )

        for customer, amount in customer_groups.items():

            customers[str(customer)] = float(amount)

    risk = (
        "HIGH"
        if total_ar > 0
        else "LOW"
    )

    return {
        "total_ar": float(total_ar),
        "outstanding_invoices": len(outstanding),
        "customers": customers,
        "risk": risk
    }


# ============================================================
# PAYABLE ANALYSIS
# ============================================================

def analyze_payables(data):
    """
    Calculate outstanding supplier payables.

    Uses:
        supplier_bills.csv
        supplier_payments.csv
    """

    bills = clean_dataframe(
        data.get("supplier_bills")
    )

    payments = clean_dataframe(
        data.get("supplier_payments")
    )

    if bills.empty:

        return {
            "total_ap": 0.0,
            "outstanding_bills": 0,
            "suppliers": {},
            "risk": "UNKNOWN"
        }

    bill_id_col = get_bill_id_column(bills)
    amount_col = get_bill_amount_column(bills)
    supplier_col = get_supplier_column(bills)

    if amount_col is None:

        return {
            "total_ap": 0.0,
            "outstanding_bills": 0,
            "suppliers": {},
            "risk": "UNKNOWN"
        }

    bills[amount_col] = pd.to_numeric(
        bills[amount_col],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # No payment data
    # --------------------------------------------------------

    if payments.empty or bill_id_col is None:

        total_ap = bills[amount_col].sum()

        return {
            "total_ap": float(total_ap),
            "outstanding_bills": len(bills),
            "suppliers": {},
            "risk": "HIGH" if total_ap > 0 else "LOW"
        }

    payment_bill_col = (
        get_supplier_payment_bill_column(payments)
    )

    payment_amount_col = (
        get_supplier_payment_amount_column(payments)
    )

    if (
        payment_bill_col is None
        or payment_amount_col is None
    ):

        total_ap = bills[amount_col].sum()

        return {
            "total_ap": float(total_ap),
            "outstanding_bills": len(bills),
            "suppliers": {},
            "risk": "HIGH" if total_ap > 0 else "LOW"
        }

    payments[payment_amount_col] = pd.to_numeric(
        payments[payment_amount_col],
        errors="coerce"
    ).fillna(0)

    paid_by_bill = (
        payments
        .groupby(payment_bill_col)[payment_amount_col]
        .sum()
    )

    bills["_paid_amount"] = (
        bills[bill_id_col]
        .map(paid_by_bill)
        .fillna(0)
    )

    bills["_outstanding"] = (
        bills[amount_col]
        - bills["_paid_amount"]
    )

    bills["_outstanding"] = (
        bills["_outstanding"]
        .clip(lower=0)
    )

    outstanding = bills[
        bills["_outstanding"] > 0.01
    ]

    total_ap = outstanding[
        "_outstanding"
    ].sum()

    # --------------------------------------------------------
    # Supplier-level balances
    # --------------------------------------------------------

    suppliers = {}

    if supplier_col is not None:

        supplier_groups = (
            outstanding
            .groupby(supplier_col)["_outstanding"]
            .sum()
            .sort_values(ascending=False)
        )

        for supplier, amount in supplier_groups.items():

            suppliers[str(supplier)] = float(amount)

    risk = (
        "HIGH"
        if total_ap > 0
        else "LOW"
    )

    return {
        "total_ap": float(total_ap),
        "outstanding_bills": len(outstanding),
        "suppliers": suppliers,
        "risk": risk
    }


# ============================================================
# TAX ANALYSIS
# ============================================================

def analyze_tax(data):
    """
    Analyse GST/tax records.

    Actual columns:
        books_tax_amount
        reported_tax_amount
        filing_status
    """

    tax = clean_dataframe(
        data.get("tax")
    )

    history = clean_dataframe(
        data.get("tax_history")
    )

    if tax.empty:

        return {
            "tax_records": 0,
            "tax_mismatches": 0,
            "books_tax": 0.0,
            "reported_tax": 0.0,
            "tax_difference": 0.0,
            "late_filings": 0,
            "historical_issues": 0,
            "tax_readiness": 0.0
        }

    books_col = get_tax_books_column(tax)
    reported_col = get_tax_reported_column(tax)
    status_col = get_tax_status_column(tax)

    if books_col is None:

        books_tax = 0.0

    else:

        tax[books_col] = pd.to_numeric(
            tax[books_col],
            errors="coerce"
        ).fillna(0)

        books_tax = tax[books_col].sum()

    if reported_col is None:

        reported_tax = 0.0

    else:

        tax[reported_col] = pd.to_numeric(
            tax[reported_col],
            errors="coerce"
        ).fillna(0)

        reported_tax = tax[reported_col].sum()

    # --------------------------------------------------------
    # Tax mismatches
    # --------------------------------------------------------

    if (
        books_col is not None
        and reported_col is not None
    ):

        difference = (
            tax[books_col]
            - tax[reported_col]
        )

        tax_mismatches = int(
            (difference.abs() > 0.01).sum()
        )

    else:

        tax_mismatches = 0

    # --------------------------------------------------------
    # Late filings
    # --------------------------------------------------------

    late_filings = 0

    if status_col is not None:

        status = (
            tax[status_col]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        late_filings = int(
            status.isin(
                [
                    "LATE",
                    "LATE FILED",
                    "PENDING"
                ]
            ).sum()
        )

    # --------------------------------------------------------
    # Historical issues
    # --------------------------------------------------------

    historical_issues = 0

    if not history.empty:

        history_status_col = find_column(
            history,
            [
                "status"
            ]
        )

        if history_status_col is not None:

            historical_issues = int(
                (
                    history[history_status_col]
                    .astype(str)
                    .str.upper()
                    .str.strip()
                    .isin(
                        [
                            "OPEN",
                            "UNRESOLVED",
                            "PENDING"
                        ]
                    )
                ).sum()
            )

    # --------------------------------------------------------
    # Tax readiness
    # --------------------------------------------------------

    tax_readiness = 100.0

    tax_readiness -= (
        tax_mismatches * 15
    )

    tax_readiness -= (
        late_filings * 10
    )

    tax_readiness -= (
        historical_issues * 10
    )

    tax_readiness = max(
        0.0,
        min(100.0, tax_readiness)
    )

    return {
        "tax_records": len(tax),
        "tax_mismatches": tax_mismatches,
        "books_tax": float(books_tax),
        "reported_tax": float(reported_tax),
        "tax_difference": float(
            books_tax - reported_tax
        ),
        "late_filings": late_filings,
        "historical_issues": historical_issues,
        "tax_readiness": float(tax_readiness)
    }


# ============================================================
# PAYROLL ANALYSIS
# ============================================================

def analyze_payroll(data):
    """
    Analyse pending payroll.
    """

    payroll = clean_dataframe(
        data.get("payroll")
    )

    if payroll.empty:

        return {
            "employees": 0,
            "pending_payroll": 0.0,
            "paid_payroll": 0.0,
            "risk": "UNKNOWN"
        }

    amount_col = get_payroll_amount_column(
        payroll
    )

    status_col = get_payroll_status_column(
        payroll
    )

    if amount_col is None:

        return {
            "employees": len(payroll),
            "pending_payroll": 0.0,
            "paid_payroll": 0.0,
            "risk": "UNKNOWN"
        }

    payroll[amount_col] = pd.to_numeric(
        payroll[amount_col],
        errors="coerce"
    ).fillna(0)

    if status_col is None:

        pending = payroll[amount_col].sum()
        paid = 0.0

    else:

        status = (
            payroll[status_col]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        pending_mask = status.isin(
            [
                "PENDING",
                "UNPAID",
                "DUE",
                "PROCESSING"
            ]
        )

        paid_mask = status.isin(
            [
                "PAID",
                "COMPLETED",
                "SUCCESS"
            ]
        )

        pending = payroll.loc[
            pending_mask,
            amount_col
        ].sum()

        paid = payroll.loc[
            paid_mask,
            amount_col
        ].sum()

    risk = (
        "MEDIUM"
        if pending > 0
        else "LOW"
    )

    return {
        "employees": len(payroll),
        "pending_payroll": float(pending),
        "paid_payroll": float(paid),
        "risk": risk
    }


# ============================================================
# RECONCILIATION ANALYSIS
# ============================================================
def analyze_reconciliation(data):
    """
    Analyse invoice-payment-bank reconciliation
    using the same logic as the existing reconciliation engine.
    """

    invoices = clean_dataframe(
        data.get("sales")
    )

    payments = clean_dataframe(
        data.get("customer_payments")
    )

    bank = clean_dataframe(
        data.get("bank")
    )

    # --------------------------------------------------------
    # Check required data
    # --------------------------------------------------------

    if invoices.empty:

        return {
            "accounts_checked": 0,
            "matched": 0,
            "mismatched": 0,
            "reconciliation_rate": 0.0
        }

    # --------------------------------------------------------
    # Aggregate payments per invoice
    # --------------------------------------------------------

    payment_summary = (
        payments
        .groupby("invoice_id")
        .agg(
            total_payment_amount=(
                "payment_amount",
                "sum"
            ),
            payment_count=(
                "payment_id",
                "count"
            )
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Connect customer payments to bank transactions
    # --------------------------------------------------------

    payment_bank = payments.merge(
        bank,
        left_on="payment_id",
        right_on="reference",
        how="left"
    )

    # --------------------------------------------------------
    # Aggregate bank amount per invoice
    # --------------------------------------------------------

    bank_summary = (
        payment_bank
        .groupby("invoice_id")
        .agg(
            total_bank_amount=(
                "amount",
                "sum"
            ),
            bank_transaction_count=(
                "bank_txn_id",
                "count"
            )
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Merge invoice + payment information
    # --------------------------------------------------------

    result = invoices.merge(
        payment_summary,
        on="invoice_id",
        how="left"
    )

    result = result.merge(
        bank_summary,
        on="invoice_id",
        how="left"
    )

    # --------------------------------------------------------
    # Handle missing values
    # --------------------------------------------------------

    result["total_payment_amount"] = (
        result["total_payment_amount"]
        .fillna(0)
    )

    result["payment_count"] = (
        result["payment_count"]
        .fillna(0)
    )

    result["total_bank_amount"] = (
        result["total_bank_amount"]
        .fillna(0)
    )

    result["bank_transaction_count"] = (
        result["bank_transaction_count"]
        .fillna(0)
    )

    # --------------------------------------------------------
    # Ensure numeric values
    # --------------------------------------------------------

    result["invoice_total"] = pd.to_numeric(
        result["invoice_total"],
        errors="coerce"
    ).fillna(0)

    result["total_payment_amount"] = pd.to_numeric(
        result["total_payment_amount"],
        errors="coerce"
    ).fillna(0)

    result["total_bank_amount"] = pd.to_numeric(
        result["total_bank_amount"],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # Reconciliation status
    # --------------------------------------------------------

    def get_status(row):

        invoice_amount = row["invoice_total"]
        payment_amount = row["total_payment_amount"]
        bank_amount = row["total_bank_amount"]
        payment_count = row["payment_count"]

        # No payment
        if payment_amount == 0:
            return "UNPAID"

        # Partial payment
        elif payment_amount < invoice_amount:
            return "PARTIALLY PAID"

        # Overpaid
        elif payment_amount > invoice_amount:

            if payment_count > 1:
                return "OVERPAID / POSSIBLE DUPLICATE"

            return "OVERPAID"

        # Payment exists but bank transaction missing
        elif bank_amount == 0:
            return "BANK PAYMENT MISSING"

        # Payment and bank amount differ
        elif bank_amount != payment_amount:
            return "BANK MISMATCH"

        # Everything matches
        else:
            return "MATCHED"

    # --------------------------------------------------------
    # Apply reconciliation
    # --------------------------------------------------------

    result["status"] = result.apply(
        get_status,
        axis=1
    )

    # --------------------------------------------------------
    # Calculate summary
    # --------------------------------------------------------

    accounts_checked = len(result)

    matched = (
        result["status"] == "MATCHED"
    ).sum()

    mismatched = (
        accounts_checked - matched
    )

    if accounts_checked > 0:

        reconciliation_rate = (
            matched
            / accounts_checked
            * 100
        )

    else:

        reconciliation_rate = 0.0

    return {
        "accounts_checked": int(accounts_checked),
        "matched": int(matched),
        "mismatched": int(mismatched),
        "reconciliation_rate": float(
            reconciliation_rate
        )
    }
# ============================================================
# OVERALL FINANCIAL QUERY DATA
# ============================================================

def build_financial_snapshot(data):
    """
    Build a single snapshot for the controller.
    """

    cash = analyze_cash(data)
    receivables = analyze_receivables(data)
    payables = analyze_payables(data)
    tax = analyze_tax(data)
    payroll = analyze_payroll(data)
    reconciliation = analyze_reconciliation(data)

    return {

        "current_cash":
            cash["current_cash"],

        "cash_risk":
            cash["risk"],

        "total_ar":
            receivables["total_ar"],

        "outstanding_invoices":
            receivables["outstanding_invoices"],

        "receivable_risk":
            receivables["risk"],

        "total_ap":
            payables["total_ap"],

        "outstanding_bills":
            payables["outstanding_bills"],

        "payable_risk":
            payables["risk"],

        "tax_mismatches":
            tax["tax_mismatches"],

        "tax_readiness":
            tax["tax_readiness"],

        "late_filings":
            tax["late_filings"],

        "historical_tax_issues":
            tax["historical_issues"],

        "pending_payroll":
            payroll["pending_payroll"],

        "payroll_risk":
            payroll["risk"],

        "accounts_checked":
            reconciliation["accounts_checked"],

        "matched":
            reconciliation["matched"],

        "mismatched_accounts":
            reconciliation["mismatched"],

        "reconciliation_rate":
            reconciliation["reconciliation_rate"]
    }


# ============================================================
# PRINT CASH ANALYSIS
# ============================================================

def cash_analysis(data):

    result = analyze_cash(data)

    section("CASH & LIQUIDITY ANALYSIS")

    print(
        f"Current Cash : "
        f"{money(result['current_cash'])}"
    )

    print()

    print(
        f"Risk : {result['risk']}"
    )

    print(
        result["message"]
    )

    print()

    print("Recommendation:")

    if result["current_cash"] < 0:

        print(
            "Prioritize collections and review "
            "immediate supplier payment timing."
        )

    elif result["current_cash"] == 0:

        print(
            "Review immediate funding requirements."
        )

    else:

        print(
            "Maintain sufficient cash reserves "
            "for upcoming obligations."
        )

    return result


# ============================================================
# PRINT RECEIVABLE ANALYSIS
# ============================================================

def receivables_analysis(data):

    result = analyze_receivables(data)

    section("ACCOUNTS RECEIVABLE ANALYSIS")

    print(
        f"Outstanding Receivables : "
        f"{money(result['total_ar'])}"
    )

    print(
        f"Outstanding Invoices : "
        f"{result['outstanding_invoices']}"
    )

    print()

    print(
        f"Risk : {result['risk']}"
    )

    if result["total_ar"] > 0:

        print(
            f"{money(result['total_ar'])} "
            "remains outstanding from customers."
        )

        print()
        print("Recommendation:")

        print(
            "Prioritize collection of overdue "
            "customer balances and follow up "
            "on unpaid invoices."
        )

    else:

        print(
            "No outstanding customer receivables detected."
        )

    # --------------------------------------------------------
    # Customer balances
    # --------------------------------------------------------

    if result["customers"]:

        print()
        print("Customer Collection Priority:")

        for index, (
            customer,
            amount
        ) in enumerate(
            result["customers"].items(),
            start=1
        ):

            print(
                f"{index}. "
                f"{customer} : "
                f"{money(amount)}"
            )

    return result


# ============================================================
# PRINT PAYABLE ANALYSIS
# ============================================================

def payable_analysis(data):

    result = analyze_payables(data)

    section("ACCOUNTS PAYABLE ANALYSIS")

    print(
        f"Outstanding Payables : "
        f"{money(result['total_ap'])}"
    )

    print(
        f"Outstanding Bills : "
        f"{result['outstanding_bills']}"
    )

    print()

    print(
        f"Risk : {result['risk']}"
    )

    if result["total_ap"] > 0:

        print(
            "Supplier obligations remain outstanding."
        )

        print()
        print("Recommendation:")

        print(
            "Review due dates and schedule supplier "
            "payments according to cash availability."
        )

    else:

        print(
            "No outstanding supplier payables detected."
        )

    # --------------------------------------------------------
    # Supplier balances
    # --------------------------------------------------------

    if result["suppliers"]:

        print()
        print("Supplier Payment Priority:")

        for index, (
            supplier,
            amount
        ) in enumerate(
            result["suppliers"].items(),
            start=1
        ):

            print(
                f"{index}. "
                f"{supplier} : "
                f"{money(amount)}"
            )

    return result


# ============================================================
# PRINT TAX ANALYSIS
# ============================================================

def tax_analysis(data):

    result = analyze_tax(data)

    section("TAX & COMPLIANCE ANALYSIS")

    print(
        f"Tax Records : "
        f"{result['tax_records']}"
    )

    print(
        f"Tax Mismatches : "
        f"{result['tax_mismatches']}"
    )

    print(
        f"Books Tax : "
        f"{money(result['books_tax'])}"
    )

    print(
        f"Reported Tax : "
        f"{money(result['reported_tax'])}"
    )

    print(
        f"Tax Difference : "
        f"{money(result['tax_difference'])}"
    )

    print(
        f"Late Filings : "
        f"{result['late_filings']}"
    )

    print(
        f"Historical Issues : "
        f"{result['historical_issues']}"
    )

    print(
        f"Tax Readiness : "
        f"{result['tax_readiness']:.1f}/100"
    )

    print()

    if result["tax_mismatches"] > 0:

        print(
            "Risk : HIGH"
        )

        print(
            "Tax mismatches detected."
        )

        print()
        print("Recommendation:")

        print(
            "Reconcile tax records against the "
            "Tally GST Payable ledger."
        )

    elif result["late_filings"] > 0:

        print(
            "Risk : MEDIUM"
        )

        print(
            "Late tax filings require attention."
        )

    else:

        print(
            "Risk : LOW"
        )

        print(
            "No active tax mismatches detected."
        )

    return result


# ============================================================
# PRINT PAYROLL ANALYSIS
# ============================================================

def payroll_analysis(data):

    result = analyze_payroll(data)

    section("PAYROLL ANALYSIS")

    print(
        f"Employees : "
        f"{result['employees']}"
    )

    print(
        f"Pending Payroll : "
        f"{money(result['pending_payroll'])}"
    )

    print(
        f"Paid Payroll : "
        f"{money(result['paid_payroll'])}"
    )

    print()

    print(
        f"Risk : {result['risk']}"
    )

    if result["pending_payroll"] > 0:

        print(
            "Pending employee payments require review."
        )

        print()
        print("Recommendation:")

        print(
            "Ensure sufficient cash is available "
            "before the payroll due date."
        )

    else:

        print(
            "No pending payroll detected."
        )

    return result


# ============================================================
# PRINT RECONCILIATION ANALYSIS
# ============================================================

def reconciliation_analysis(data):

    result = analyze_reconciliation(data)

    section("TALLY / BANK RECONCILIATION")

    print(
        f"Accounts checked : "
        f"{result['accounts_checked']}"
    )

    print(
        f"Matched : "
        f"{result['matched']}"
    )

    print(
        f"Mismatched : "
        f"{result['mismatched']}"
    )

    print(
        f"Reconciliation rate : "
        f"{result['reconciliation_rate']:.1f}%"
    )

    print()

    if result["mismatched"] > 0:

        print(
            "Risk : HIGH"
        )

        print(
            f"{result['mismatched']} "
            "reconciliation exception(s) "
            "require review."
        )

        print()
        print("Recommendation:")

        print(
            "Review unmatched payments, bank "
            "references and ledger entries."
        )

    else:

        print(
            "Risk : LOW"
        )

        print(
            "All available transactions are reconciled."
        )

    return result


# ============================================================
# OVERALL FINANCIAL ANALYSIS
# ============================================================

def overall_financial_analysis(data):

    snapshot = build_financial_snapshot(data)

    section("OVERALL FINANCIAL ANALYSIS")

    print(
        f"Current Cash : "
        f"{money(snapshot['current_cash'])}"
    )

    print(
        f"Accounts Receivable : "
        f"{money(snapshot['total_ar'])}"
    )

    print(
        f"Accounts Payable : "
        f"{money(snapshot['total_ap'])}"
    )

    print(
        f"Tax Readiness : "
        f"{snapshot['tax_readiness']:.1f}/100"
    )

    print(
        f"Reconciliation Rate : "
        f"{snapshot['reconciliation_rate']:.1f}%"
    )

    print()

    print("Key Issues:")

    issues = []

    if snapshot["current_cash"] < 0:

        issues.append(
            "CRITICAL: Negative cash position."
        )

    if snapshot["total_ar"] > 0:

        issues.append(
            "HIGH: Outstanding customer receivables."
        )

    if snapshot["total_ap"] > 0:

        issues.append(
            "HIGH: Outstanding supplier payables."
        )

    if snapshot["tax_mismatches"] > 0:

        issues.append(
            "HIGH: Tax mismatches detected."
        )

    if snapshot["mismatched_accounts"] > 0:

        issues.append(
            "HIGH: Reconciliation exceptions detected."
        )

    if snapshot["pending_payroll"] > 0:

        issues.append(
            "MEDIUM: Pending payroll detected."
        )

    if not issues:

        issues.append(
            "No major financial issues detected."
        )

    for issue in issues:

        print(
            f"- {issue}"
        )

    return snapshot


# ============================================================
# QUESTION KEYWORD ROUTER
# ============================================================

def classify_question(question):

    q = question.lower().strip()

    # --------------------------------------------------------
    # CASH
    # --------------------------------------------------------

    if (
        "cash" in q
        or "liquidity" in q
        or "bank balance" in q
        or "bank position" in q
    ):

        return "cash"

    # --------------------------------------------------------
    # RECEIVABLES
    # --------------------------------------------------------

    if (
        "receivable" in q
        or "receivables" in q
        or "customer payment" in q
        or "customer collection" in q
        or "collect" in q
        or re.search(r"\bar\b", q)
    ):

        return "receivables"

    # --------------------------------------------------------
    # PAYABLES
    # --------------------------------------------------------

    if (
        "payable" in q
        or "payables" in q
        or "supplier" in q
        or "vendor" in q
        or "supplier payment" in q
        or re.search(r"\bap\b", q)
    ):

        return "payables"

    # --------------------------------------------------------
    # TAX
    # --------------------------------------------------------

    if (
        "tax" in q
        or "gst" in q
        or "compliance" in q
        or "filing" in q
    ):

        return "tax"

    # --------------------------------------------------------
    # RECONCILIATION
    # --------------------------------------------------------

    if (
        "reconciliation" in q
        or "reconcile" in q
        or "tally" in q
        or "ledger" in q
        or "mismatch" in q
        or "unmatched" in q
    ):

        return "reconciliation"

    # --------------------------------------------------------
    # PAYROLL
    # --------------------------------------------------------

    if (
        "payroll" in q
        or "salary" in q
        or "employee payment" in q
        or "staff payment" in q
    ):

        return "payroll"

    # --------------------------------------------------------
    # OVERALL
    # --------------------------------------------------------

    if (
        "overall" in q
        or "financial health" in q
        or "summary" in q
        or "status" in q
        or "how are we doing" in q
        or "how is the business" in q
    ):

        return "overall"

    return "unknown"


# ============================================================
# QUESTION ANSWER FUNCTION
# ============================================================

def answer_financial_question(
    question,
    data
):
    """
    Main entry point for the AI Finance Controller.

    Returns the analysis type and result.
    """

    category = classify_question(
        question
    )

    if category == "cash":

        return {
            "category": category,
            "result": cash_analysis(data)
        }

    if category == "receivables":

        return {
            "category": category,
            "result": receivables_analysis(data)
        }

    if category == "payables":

        return {
            "category": category,
            "result": payable_analysis(data)
        }

    if category == "tax":

        return {
            "category": category,
            "result": tax_analysis(data)
        }

    if category == "reconciliation":

        return {
            "category": category,
            "result": reconciliation_analysis(data)
        }

    if category == "payroll":

        return {
            "category": category,
            "result": payroll_analysis(data)
        }

    if category == "overall":

        return {
            "category": category,
            "result": overall_financial_analysis(data)
        }

    return {
        "category": "unknown",
        "result": None
    }


# ============================================================
# SIMPLE QUERY FUNCTIONS
# ============================================================

def get_current_cash(data):

    return analyze_cash(
        data
    )["current_cash"]


def get_total_receivables(data):

    return analyze_receivables(
        data
    )["total_ar"]


def get_total_payables(data):

    return analyze_payables(
        data
    )["total_ap"]


def get_tax_mismatches(data):

    return analyze_tax(
        data
    )["tax_mismatches"]


def get_tax_readiness(data):

    return analyze_tax(
        data
    )["tax_readiness"]


def get_pending_payroll(data):

    return analyze_payroll(
        data
    )["pending_payroll"]


def get_reconciliation_rate(data):

    return analyze_reconciliation(
        data
    )["reconciliation_rate"]


def get_mismatched_accounts(data):

    return analyze_reconciliation(
        data
    )["mismatched"]


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    print()
    line()
    print("FINANCIAL QUERY ENGINE")
    line()

    print()
    print(
        "This module is intended to be imported "
        "by ai_finance_controller.py."
    )

    print()
    print(
        "Available analyses:"
    )

    print(
        "- Cash / Liquidity"
    )

    print(
        "- Accounts Receivable"
    )

    print(
        "- Accounts Payable"
    )

    print(
        "- Tax / GST"
    )

    print(
        "- Payroll"
    )

    print(
        "- Tally / Bank Reconciliation"
    )

    print(
        "- Overall Financial Analysis"
    )