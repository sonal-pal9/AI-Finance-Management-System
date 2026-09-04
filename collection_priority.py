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
# 3. AGGREGATE PAYMENTS
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

ar["total_paid"] = ar["total_paid"].fillna(0)


# ==========================================
# 5. CALCULATE OUTSTANDING
# ==========================================

ar["outstanding_amount"] = (
    ar["invoice_total"] - ar["total_paid"]
)

ar["outstanding_amount"] = ar[
    "outstanding_amount"
].clip(lower=0)


# ==========================================
# 6. REFERENCE DATE
# ==========================================

REFERENCE_DATE = pd.Timestamp("2026-07-31")


# ==========================================
# 7. CALCULATE DAYS OVERDUE
# ==========================================

ar["days_overdue"] = (
    REFERENCE_DATE - ar["due_date"]
).dt.days

ar["days_overdue"] = ar[
    "days_overdue"
].clip(lower=0)


# ==========================================
# 8. KEEP ONLY OPEN RECEIVABLES
# ==========================================

open_receivables = ar[
    ar["outstanding_amount"] > 0
].copy()


# ==========================================
# 9. COLLECTION PRIORITY SCORE
# ==========================================

def calculate_risk_score(row):

    score = 0

    outstanding = row["outstanding_amount"]
    days_overdue = row["days_overdue"]


    # --------------------------------------
    # AMOUNT RISK
    # --------------------------------------

    if outstanding >= 50000:
        score += 40

    elif outstanding >= 20000:
        score += 30

    elif outstanding >= 10000:
        score += 20

    else:
        score += 10


    # --------------------------------------
    # OVERDUE RISK
    # --------------------------------------

    if days_overdue > 90:
        score += 60

    elif days_overdue > 60:
        score += 50

    elif days_overdue > 30:
        score += 40

    elif days_overdue > 0:
        score += 30

    else:
        score += 10


    return score


open_receivables["risk_score"] = (
    open_receivables.apply(
        calculate_risk_score,
        axis=1
    )
)


# ==========================================
# 10. PRIORITY LEVEL
# ==========================================

def get_priority(score):

    if score >= 70:
        return "HIGH"

    elif score >= 40:
        return "MEDIUM"

    else:
        return "LOW"


open_receivables["priority"] = (
    open_receivables["risk_score"].apply(
        get_priority
    )
)


# ==========================================
# 11. RECOMMENDED ACTION
# ==========================================

def get_recommended_action(row):

    priority = row["priority"]
    days_overdue = row["days_overdue"]

    if priority == "HIGH":

        if days_overdue > 0:
            return "Send reminder and schedule collection follow-up"

        return "Monitor closely before due date"


    elif priority == "MEDIUM":

        if days_overdue > 0:
            return "Send payment reminder"

        return "Monitor until due date"


    else:

        return "No immediate action - monitor"


open_receivables["recommended_action"] = (
    open_receivables.apply(
        get_recommended_action,
        axis=1
    )
)


# ==========================================
# 12. FINAL COLLECTION REPORT
# ==========================================

collection_report = open_receivables[
    [
        "invoice_id",
        "customer",
        "invoice_date",
        "due_date",
        "invoice_total",
        "total_paid",
        "outstanding_amount",
        "days_overdue",
        "risk_score",
        "priority",
        "recommended_action"
    ]
]


# ==========================================
# 13. SORT BY PRIORITY + AMOUNT
# ==========================================

priority_order = {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3
}

collection_report = collection_report.copy()

collection_report["priority_order"] = (
    collection_report["priority"].map(
        priority_order
    )
)

collection_report = collection_report.sort_values(
    by=[
        "priority_order",
        "risk_score",
        "outstanding_amount"
    ],
    ascending=[
        True,
        False,
        False
    ]
)

collection_report = collection_report.drop(
    columns="priority_order"
)


# ==========================================
# 14. PRINT REPORT
# ==========================================

print("\n========================================")
print("NOURISH CAFE - COLLECTION PRIORITY")
print("========================================\n")

print(collection_report)


# ==========================================
# 15. PRIORITY SUMMARY
# ==========================================

print("\n========================================")
print("PRIORITY SUMMARY")
print("========================================\n")

print(
    collection_report.groupby("priority")[
        "outstanding_amount"
    ].agg(
        ["count", "sum"]
    )
)


# ==========================================
# 16. SAVE REPORT
# ==========================================

collection_report.to_csv(
    "collection_priority_report.csv",
    index=False
)

print("\nCollection priority report saved successfully!")