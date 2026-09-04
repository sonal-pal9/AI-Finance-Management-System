import pandas as pd


# ==========================================
# 1. LOAD DATA
# ==========================================

invoices = pd.read_csv("data/sales_invoices.csv")
payments = pd.read_csv("data/customer_payments.csv")


# ==========================================
# 2. CONVERT DATE COLUMNS
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
    total_paid=("payment_amount", "sum"),
    payment_count=("payment_id", "count")
).reset_index()


# ==========================================
# 4. MERGE INVOICES + PAYMENTS
# ==========================================

ar = invoices.merge(
    payment_summary,
    on="invoice_id",
    how="left"
)


# Invoices without payments
ar["total_paid"] = ar["total_paid"].fillna(0)

ar["payment_count"] = ar["payment_count"].fillna(0)


# ==========================================
# 5. CALCULATE OUTSTANDING AMOUNT
# ==========================================

ar["outstanding_amount"] = (
    ar["invoice_total"]
    - ar["total_paid"]
)

# Prevent negative outstanding values
ar["outstanding_amount"] = ar[
    "outstanding_amount"
].clip(lower=0)


# ==========================================
# 6. PAYMENT COMPLETION %
# ==========================================

ar["payment_completion_percentage"] = (
    ar["total_paid"]
    / ar["invoice_total"]
    * 100
)

# Cap at 100% in case of overpayment
ar["payment_completion_percentage"] = ar[
    "payment_completion_percentage"
].clip(upper=100)


# ==========================================
# 7. REFERENCE DATE
# ==========================================

REFERENCE_DATE = pd.Timestamp("2026-07-31")


# ==========================================
# 8. CALCULATE DAYS OVERDUE
# ==========================================

ar["days_difference"] = (
    REFERENCE_DATE - ar["due_date"]
).dt.days


# Positive → overdue
ar["days_overdue"] = ar[
    "days_difference"
].clip(lower=0)


# Negative → days remaining until due
ar["days_until_due"] = (
    -ar["days_difference"]
).clip(lower=0)


# ==========================================
# 9. KEEP ONLY OPEN RECEIVABLES
# ==========================================

open_receivables = ar[
    ar["outstanding_amount"] > 0
].copy()


# ==========================================
# 10. COLLECTION RISK SCORE
# ==========================================

def calculate_collection_score(row):

    score = 0

    outstanding = row["outstanding_amount"]
    days_overdue = row["days_overdue"]
    days_until_due = row["days_until_due"]
    completion = row["payment_completion_percentage"]


    # --------------------------------------
    # FACTOR 1: OUTSTANDING AMOUNT
    # Maximum: 30 points
    # --------------------------------------

    if outstanding >= 50000:
        score += 30

    elif outstanding >= 30000:
        score += 25

    elif outstanding >= 10000:
        score += 15

    else:
        score += 10


    # --------------------------------------
    # FACTOR 2: OVERDUE RISK
    # Maximum: 40 points
    # --------------------------------------

    if days_overdue > 90:
        score += 40

    elif days_overdue > 60:
        score += 35

    elif days_overdue > 30:
        score += 30

    elif days_overdue > 0:
        score += 25


    # --------------------------------------
    # FACTOR 3: CLOSE TO DUE DATE
    # Maximum: 15 points
    # --------------------------------------

    elif days_until_due <= 3:
        score += 15

    elif days_until_due <= 7:
        score += 10

    elif days_until_due <= 15:
        score += 5


    # --------------------------------------
    # FACTOR 4: PAYMENT COMPLETENESS
    # Maximum: 15 points
    # --------------------------------------

    # Nothing has been paid
    if completion == 0:
        score += 15

    # Less than half has been paid
    elif completion < 50:
        score += 10

    # Partially paid
    elif completion < 100:
        score += 5


    return score


open_receivables["collection_score"] = (
    open_receivables.apply(
        calculate_collection_score,
        axis=1
    )
)


# ==========================================
# 11. ASSIGN PRIORITY
# ==========================================

def get_priority(score):

    if score >= 50:
        return "HIGH"

    elif score >= 25:
        return "MEDIUM"

    else:
        return "LOW"


open_receivables["priority"] = (
    open_receivables["collection_score"].apply(
        get_priority
    )
)


# ==========================================
# 12. CREATE EXPLAINABLE REASON
# ==========================================

def get_reason(row):

    reasons = []

    outstanding = row["outstanding_amount"]
    days_overdue = row["days_overdue"]
    days_until_due = row["days_until_due"]
    completion = row["payment_completion_percentage"]


    # Amount reason

    if outstanding >= 50000:
        reasons.append(
            f"High outstanding balance of ₹{outstanding:,.2f}"
        )

    elif outstanding >= 30000:
        reasons.append(
            f"Significant outstanding balance of ₹{outstanding:,.2f}"
        )


    # Payment status reason

    if completion == 0:
        reasons.append(
            "No payment has been received"
        )

    elif completion < 100:
        reasons.append(
            f"Only {completion:.1f}% of the invoice has been paid"
        )


    # Due date reason

    if days_overdue > 0:
        reasons.append(
            f"{int(days_overdue)} days overdue"
        )

    elif days_until_due <= 3:
        reasons.append(
            f"Due in {int(days_until_due)} days"
        )

    elif days_until_due <= 7:
        reasons.append(
            f"Due soon in {int(days_until_due)} days"
        )

    else:
        reasons.append(
            "Invoice is not yet due"
        )


    return "; ".join(reasons)


open_receivables["reason"] = (
    open_receivables.apply(
        get_reason,
        axis=1
    )
)


# ==========================================
# 13. RECOMMENDED ACTION
# ==========================================

def get_recommended_action(row):

    priority = row["priority"]
    days_overdue = row["days_overdue"]
    days_until_due = row["days_until_due"]
    completion = row["payment_completion_percentage"]


    # HIGH PRIORITY

    if priority == "HIGH":

        if days_overdue > 0:
            return (
                "Immediate follow-up: send reminder "
                "and assign collection owner"
            )

        return (
            "Contact customer before due date "
            "and confirm payment commitment"
        )


    # MEDIUM PRIORITY

    elif priority == "MEDIUM":

        if days_overdue > 0:
            return (
                "Send payment reminder and review "
                "again in 3 days"
            )

        elif days_until_due <= 7:
            return (
                "Send pre-due payment reminder"
            )

        return (
            "Monitor and schedule reminder "
            "before due date"
        )


    # LOW PRIORITY

    else:

        if completion < 100:
            return (
                "Monitor remaining balance and "
                "send reminder before due date"
            )

        return "No immediate action required"


open_receivables["recommended_action"] = (
    open_receivables.apply(
        get_recommended_action,
        axis=1
    )
)


# ==========================================
# 14. SELECT FINAL REPORT COLUMNS
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
        "payment_completion_percentage",
        "days_until_due",
        "days_overdue",
        "collection_score",
        "priority",
        "reason",
        "recommended_action"
    ]
].copy()


# ==========================================
# 15. SORT BY PRIORITY
# ==========================================

priority_order = {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3
}


collection_report["priority_order"] = (
    collection_report["priority"].map(
        priority_order
    )
)


collection_report = collection_report.sort_values(
    by=[
        "priority_order",
        "collection_score",
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
# 16. PRINT REPORT
# ==========================================

print("\n============================================")
print("NOURISH CAFE - SMART COLLECTION PRIORITY")
print("============================================\n")

print(collection_report)


# ==========================================
# 17. PRINT PRIORITY SUMMARY
# ==========================================

print("\n============================================")
print("PRIORITY SUMMARY")
print("============================================\n")

priority_summary = (
    collection_report
    .groupby("priority")["outstanding_amount"]
    .agg(["count", "sum"])
)

print(priority_summary)


# ==========================================
# 18. SHOW HIGH PRIORITY CASES
# ==========================================

high_priority = collection_report[
    collection_report["priority"] == "HIGH"
]

print("\n============================================")
print("HIGH PRIORITY COLLECTION ACTIONS")
print("============================================\n")

print(
    high_priority[
        [
            "invoice_id",
            "customer",
            "outstanding_amount",
            "days_overdue",
            "collection_score",
            "reason",
            "recommended_action"
        ]
    ]
)


# ==========================================
# 19. SAVE REPORT
# ==========================================

collection_report.to_csv(
    "smart_collection_priority_report.csv",
    index=False
)


print(
    "\nSmart collection priority report "
    "saved successfully!"
)