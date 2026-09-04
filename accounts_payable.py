import pandas as pd


# ==========================================
# 1. LOAD DATA
# ==========================================

bills = pd.read_csv("data/supplier_bills.csv")
payments = pd.read_csv("data/supplier_payments.csv")


# ==========================================
# 2. CONVERT DATE COLUMNS
# ==========================================

bills["bill_date"] = pd.to_datetime(bills["bill_date"])
bills["due_date"] = pd.to_datetime(bills["due_date"])

payments["payment_date"] = pd.to_datetime(
    payments["payment_date"]
)


# ==========================================
# 3. AGGREGATE PAYMENTS PER BILL
# ==========================================

payment_summary = payments.groupby("bill_id").agg(
    total_paid=("payment_amount", "sum"),
    payment_count=("payment_id", "count")
).reset_index()


# ==========================================
# 4. MERGE BILLS + PAYMENTS
# ==========================================

ap = bills.merge(
    payment_summary,
    on="bill_id",
    how="left"
)


# Bills without payments

ap["total_paid"] = ap["total_paid"].fillna(0)

ap["payment_count"] = ap["payment_count"].fillna(0)


# ==========================================
# 5. CALCULATE OUTSTANDING
# ==========================================

ap["outstanding_amount"] = (
    ap["bill_amount"] - ap["total_paid"]
)


# Keep track of overpayment separately

ap["overpayment_amount"] = (
    ap["total_paid"] - ap["bill_amount"]
).clip(lower=0)


# Outstanding cannot be negative

ap["outstanding_amount"] = ap[
    "outstanding_amount"
].clip(lower=0)


# ==========================================
# 6. REFERENCE DATE
# ==========================================

REFERENCE_DATE = pd.Timestamp("2026-07-31")


# ==========================================
# 7. CALCULATE DUE STATUS
# ==========================================

ap["days_difference"] = (
    REFERENCE_DATE - ap["due_date"]
).dt.days


# Positive = overdue

ap["days_overdue"] = ap[
    "days_difference"
].clip(lower=0)


# Negative = days until due

ap["days_until_due"] = (
    -ap["days_difference"]
).clip(lower=0)


# ==========================================
# 8. PAYMENT STATUS
# ==========================================

def get_payment_status(row):

    if row["overpayment_amount"] > 0:
        return "OVERPAID / POSSIBLE DUPLICATE"

    elif row["total_paid"] == 0:
        return "UNPAID"

    elif row["total_paid"] < row["bill_amount"]:
        return "PARTIALLY PAID"

    else:
        return "PAID"


ap["payment_status"] = ap.apply(
    get_payment_status,
    axis=1
)


# ==========================================
# 9. PAYMENT PRIORITY SCORE
# ==========================================

def calculate_payment_score(row):

    score = 0

    outstanding = row["outstanding_amount"]
    days_overdue = row["days_overdue"]
    days_until_due = row["days_until_due"]


    # --------------------------------------
    # AMOUNT FACTOR
    # --------------------------------------

    if outstanding >= 30000:
        score += 30

    elif outstanding >= 20000:
        score += 25

    elif outstanding >= 10000:
        score += 15

    else:
        score += 10


    # --------------------------------------
    # DUE DATE FACTOR
    # --------------------------------------

    if days_overdue > 30:
        score += 40

    elif days_overdue > 0:
        score += 30

    elif days_until_due <= 3:
        score += 20

    elif days_until_due <= 7:
        score += 10


    return score


# Only score bills with money still owed

ap["payment_score"] = 0

open_bills = ap[
    ap["outstanding_amount"] > 0
].copy()

open_bills["payment_score"] = open_bills.apply(
    calculate_payment_score,
    axis=1
)


# ==========================================
# 10. PAYMENT PRIORITY
# ==========================================

def get_payment_priority(score):

    if score >= 50:
        return "HIGH"

    elif score >= 25:
        return "MEDIUM"

    else:
        return "LOW"


open_bills["payment_priority"] = (
    open_bills["payment_score"].apply(
        get_payment_priority
    )
)


# ==========================================
# 11. RECOMMENDED ACTION
# ==========================================

def get_payment_action(row):

    if row["days_overdue"] > 0:

        return (
            "Prioritize payment or contact supplier "
            "to avoid disruption"
        )

    elif row["days_until_due"] <= 3:

        return (
            "Schedule payment immediately"
        )

    elif row["days_until_due"] <= 7:

        return (
            "Plan payment in current cash cycle"
        )

    else:

        return (
            "Schedule payment before due date"
        )


open_bills["recommended_action"] = (
    open_bills.apply(
        get_payment_action,
        axis=1
    )
)


# ==========================================
# 12. CREATE FINAL AP REPORT
# ==========================================

ap_report = ap[
    [
        "bill_id",
        "supplier",
        "bill_date",
        "due_date",
        "bill_amount",
        "total_paid",
        "outstanding_amount",
        "overpayment_amount",
        "payment_count",
        "days_overdue",
        "days_until_due",
        "payment_status"
    ]
].copy()


# ==========================================
# 13. PRINT RECONCILIATION RESULTS
# ==========================================

print("\n============================================")
print("NOURISH CAFE - ACCOUNTS PAYABLE")
print("============================================\n")

print(ap_report)


# ==========================================
# 14. STATUS SUMMARY
# ==========================================

print("\n============================================")
print("PAYMENT STATUS SUMMARY")
print("============================================\n")

print(
    ap_report["payment_status"]
    .value_counts()
)


# ==========================================
# 15. OPEN PAYABLES
# ==========================================

print("\n============================================")
print("OPEN PAYABLES - PAYMENT PRIORITY")
print("============================================\n")

priority_order = {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3
}


open_bills["priority_order"] = (
    open_bills["payment_priority"]
    .map(priority_order)
)


open_bills = open_bills.sort_values(
    by=[
        "priority_order",
        "payment_score",
        "outstanding_amount"
    ],
    ascending=[
        True,
        False,
        False
    ]
)


print(
    open_bills[
        [
            "bill_id",
            "supplier",
            "bill_amount",
            "total_paid",
            "outstanding_amount",
            "days_overdue",
            "days_until_due",
            "payment_priority",
            "recommended_action"
        ]
    ]
)


# ==========================================
# 16. TOTAL PAYABLE
# ==========================================

total_payable = open_bills[
    "outstanding_amount"
].sum()


print("\n============================================")
print("TOTAL ACCOUNTS PAYABLE")
print("============================================\n")

print(f"₹{total_payable:,.2f}")


# ==========================================
# 17. SAVE REPORTS
# ==========================================

ap_report.to_csv(
    "accounts_payable_report.csv",
    index=False
)


open_bills.to_csv(
    "payment_priority_report.csv",
    index=False
)


print("\nReports saved successfully!")