import pandas as pd


# ==========================================
# 1. LOAD DATA
# ==========================================

invoices = pd.read_csv("data/sales_invoices.csv")
payments = pd.read_csv("data/customer_payments.csv")


# ==========================================
# 2. CONVERT DATES
# ==========================================

invoices["invoice_date"] = pd.to_datetime(
    invoices["invoice_date"]
)

invoices["due_date"] = pd.to_datetime(
    invoices["due_date"]
)


# ==========================================
# 3. AGGREGATE PAYMENTS PER INVOICE
# ==========================================

payment_summary = payments.groupby("invoice_id").agg(
    total_paid=("payment_amount", "sum")
).reset_index()


# ==========================================
# 4. MERGE INVOICES + PAYMENTS
# ==========================================

ar = invoices.merge(
    payment_summary,
    on="invoice_id",
    how="left"
)


# Invoices with no payment should have 0 paid

ar["total_paid"] = ar["total_paid"].fillna(0)


# ==========================================
# 5. CALCULATE OUTSTANDING AMOUNT
# ==========================================

ar["outstanding_amount"] = (
    ar["invoice_total"]
    - ar["total_paid"]
)


# ==========================================
# 6. HANDLE OVERPAYMENTS
# ==========================================

# Outstanding should never become negative.
# Any extra payment is treated separately.

ar["outstanding_amount"] = ar[
    "outstanding_amount"
].clip(lower=0)


# ==========================================
# 7. SET A REFERENCE DATE
# ==========================================

# Our dataset represents July 2026.
# We use July 31 as the month-end close date.

REFERENCE_DATE = pd.Timestamp("2026-07-31")


# ==========================================
# 8. CALCULATE DAYS OVERDUE
# ==========================================

ar["days_overdue"] = (
    REFERENCE_DATE - ar["due_date"]
).dt.days


# If due date is in the future,
# days overdue should be 0.

ar["days_overdue"] = ar[
    "days_overdue"
].clip(lower=0)


# ==========================================
# 9. CREATE AGING BUCKET
# ==========================================

def get_aging_bucket(row):

    outstanding = row["outstanding_amount"]
    days = row["days_overdue"]

    # Nothing left to collect
    if outstanding == 0:
        return "PAID"

    # Not overdue yet
    if days == 0:
        return "CURRENT"

    elif days <= 30:
        return "1-30 DAYS"

    elif days <= 60:
        return "31-60 DAYS"

    elif days <= 90:
        return "61-90 DAYS"

    else:
        return "90+ DAYS"


ar["aging_bucket"] = ar.apply(
    get_aging_bucket,
    axis=1
)


# ==========================================
# 10. CREATE COLLECTION STATUS
# ==========================================

def get_collection_status(row):

    outstanding = row["outstanding_amount"]
    paid = row["total_paid"]

    if outstanding == 0:
        return "FULLY PAID"

    if paid == 0:
        return "UNPAID"

    return "PARTIALLY PAID"


ar["collection_status"] = ar.apply(
    get_collection_status,
    axis=1
)


# ==========================================
# 11. FINAL AR REPORT
# ==========================================

ar_report = ar[
    [
        "invoice_id",
        "customer",
        "invoice_date",
        "due_date",
        "invoice_total",
        "total_paid",
        "outstanding_amount",
        "days_overdue",
        "aging_bucket",
        "collection_status"
    ]
]


# ==========================================
# 12. SHOW ONLY MONEY TO COLLECT
# ==========================================

open_receivables = ar_report[
    ar_report["outstanding_amount"] > 0
]


print("\n======================================")
print("NOURISH CAFE - ACCOUNTS RECEIVABLE")
print("======================================\n")

print(open_receivables)


# ==========================================
# 13. AR SUMMARY
# ==========================================

print("\n======================================")
print("AR SUMMARY")
print("======================================\n")

print(
    open_receivables.groupby(
        "aging_bucket"
    )["outstanding_amount"].sum()
)


# ==========================================
# 14. TOTAL MONEY TO COLLECT
# ==========================================

total_ar = open_receivables[
    "outstanding_amount"
].sum()

print("\n======================================")
print("TOTAL ACCOUNTS RECEIVABLE")
print("======================================\n")

print(f"₹{total_ar:,.2f}")


# ==========================================
# 15. SAVE REPORT
# ==========================================

ar_report.to_csv(
    "accounts_receivable_report.csv",
    index=False
)

print("\nAR report saved successfully!")