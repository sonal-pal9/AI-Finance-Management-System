import pandas as pd


# ============================================================
# NOURISH CAFE - LIQUIDITY ACTION ENGINE
# ============================================================


# ============================================================
# 1. LOAD DATA
# ============================================================

invoices = pd.read_csv(
    "data/sales_invoices.csv"
)

customer_payments = pd.read_csv(
    "data/customer_payments.csv"
)

supplier_bills = pd.read_csv(
    "data/supplier_bills.csv"
)

supplier_payments = pd.read_csv(
    "data/supplier_payments.csv"
)

payroll = pd.read_csv(
    "data/payroll.csv"
)


# ============================================================
# 2. REFERENCE DATE
# ============================================================

REFERENCE_DATE = pd.Timestamp(
    "2026-07-31"
)


# ============================================================
# 3. CURRENT CASH
# ============================================================

# Same opening balance used in cash_position.py

OPENING_BANK_BALANCE = 250000.00


# We don't need the bank file here because we can
# calculate current cash from the existing transactions.

bank = pd.read_csv(
    "data/bank_transactions.csv"
)

total_inflows = bank[
    bank["direction"] == "CREDIT"
]["amount"].sum()

total_outflows = bank[
    bank["direction"] == "DEBIT"
]["amount"].sum()

current_cash = (
    OPENING_BANK_BALANCE
    + total_inflows
    - total_outflows
)


# ============================================================
# 4. BUILD ACCOUNTS RECEIVABLE
# ============================================================

payment_summary = customer_payments.groupby(
    "invoice_id"
).agg(
    total_paid=("payment_amount", "sum")
).reset_index()


ar = invoices.merge(
    payment_summary,
    on="invoice_id",
    how="left"
)


ar["total_paid"] = (
    ar["total_paid"].fillna(0)
)


ar["outstanding_amount"] = (
    ar["invoice_total"]
    - ar["total_paid"]
)


ar["outstanding_amount"] = (
    ar["outstanding_amount"].clip(lower=0)
)


# ============================================================
# 5. AR DUE DATE ANALYSIS
# ============================================================

ar["days_difference"] = (
    REFERENCE_DATE
    - pd.to_datetime(ar["due_date"])
).dt.days


ar["days_overdue"] = (
    ar["days_difference"].clip(lower=0)
)


ar["days_until_due"] = (
    -ar["days_difference"].clip(upper=0)
)


# Only open invoices

open_ar = ar[
    ar["outstanding_amount"] > 0
].copy()


# ============================================================
# 6. BUILD ACCOUNTS PAYABLE
# ============================================================

supplier_payment_summary = supplier_payments.groupby(
    "bill_id"
).agg(
    total_paid=("payment_amount", "sum")
).reset_index()


ap = supplier_bills.merge(
    supplier_payment_summary,
    on="bill_id",
    how="left"
)


ap["total_paid"] = (
    ap["total_paid"].fillna(0)
)


ap["outstanding_amount"] = (
    ap["bill_amount"]
    - ap["total_paid"]
)


ap["outstanding_amount"] = (
    ap["outstanding_amount"].clip(lower=0)
)


# ============================================================
# 7. AP DUE DATE ANALYSIS
# ============================================================

ap["days_difference"] = (
    REFERENCE_DATE
    - pd.to_datetime(ap["due_date"])
).dt.days


ap["days_overdue"] = (
    ap["days_difference"].clip(lower=0)
)


ap["days_until_due"] = (
    -ap["days_difference"].clip(upper=0)
)


open_ap = ap[
    ap["outstanding_amount"] > 0
].copy()


# ============================================================
# 8. PENDING PAYROLL
# ============================================================

pending_payroll = payroll[
    payroll["payment_status"].str.lower() != "paid"
].copy()


pending_payroll_amount = pending_payroll[
    "net_salary"
].sum()


# ============================================================
# 9. CREATE ACTION LIST
# ============================================================

actions = []


# ============================================================
# ACTION TYPE 1
# HIGH PRIORITY CUSTOMER COLLECTION
# ============================================================

for _, row in open_ar.iterrows():

    outstanding = row["outstanding_amount"]
    overdue = row["days_overdue"]
    due_soon = row["days_until_due"]


    # High-value overdue receivable

    if overdue > 0 and outstanding >= 20000:

        actions.append({

            "priority": "HIGH",

            "action_type": "ACCELERATE COLLECTION",

            "reference": row["invoice_id"],

            "counterparty": row["customer"],

            "cash_impact": outstanding,

            "reason":
                f"₹{outstanding:,.2f} is outstanding "
                f"and {int(overdue)} days overdue",

            "recommended_action":
                "Immediate collection follow-up and "
                "confirm payment commitment"

        })


    # High-value invoice due soon

    elif due_soon <= 7 and outstanding >= 30000:

        actions.append({

            "priority": "HIGH",

            "action_type": "ACCELERATE COLLECTION",

            "reference": row["invoice_id"],

            "counterparty": row["customer"],

            "cash_impact": outstanding,

            "reason":
                f"₹{outstanding:,.2f} remains outstanding "
                f"and is due within {int(due_soon)} days",

            "recommended_action":
                "Contact customer before due date "
                "and confirm payment"

        })


# ============================================================
# ACTION TYPE 2
# OVERDUE SUPPLIER PAYMENTS
# ============================================================

for _, row in open_ap.iterrows():

    outstanding = row["outstanding_amount"]
    overdue = row["days_overdue"]


    if overdue > 0:

        actions.append({

            "priority": "HIGH",

            "action_type": "REVIEW OVERDUE PAYABLE",

            "reference": row["bill_id"],

            "counterparty": row["supplier"],

            "cash_impact": -outstanding,

            "reason":
                f"₹{outstanding:,.2f} supplier obligation "
                f"is {int(overdue)} days overdue",

            "recommended_action":
                "Review supplier terms and determine "
                "whether payment can be scheduled"

        })


# ============================================================
# ACTION TYPE 3
# UPCOMING LARGE SUPPLIER PAYMENTS
# ============================================================

for _, row in open_ap.iterrows():

    outstanding = row["outstanding_amount"]
    due_soon = row["days_until_due"]


    if (
        due_soon >= 0
        and due_soon <= 7
        and outstanding >= 20000
    ):

        actions.append({

            "priority": "MEDIUM",

            "action_type": "PLAN SUPPLIER PAYMENT",

            "reference": row["bill_id"],

            "counterparty": row["supplier"],

            "cash_impact": -outstanding,

            "reason":
                f"₹{outstanding:,.2f} supplier bill "
                f"is due within {int(due_soon)} days",

            "recommended_action":
                "Include in cash planning and "
                "schedule payment according to terms"

        })


# ============================================================
# ACTION TYPE 4
# PENDING PAYROLL
# ============================================================

if pending_payroll_amount > 0:

    actions.append({

        "priority": "CRITICAL",

        "action_type": "FUND PAYROLL",

        "reference": "PAYROLL",

        "counterparty": "Employees",

        "cash_impact": -pending_payroll_amount,

        "reason":
            f"₹{pending_payroll_amount:,.2f} "
            "in employee salaries remains pending",

        "recommended_action":
            "Reserve funds for payroll before "
            "non-critical payments"

    })


# ============================================================
# 10. CONVERT ACTIONS TO DATAFRAME
# ============================================================

actions_df = pd.DataFrame(actions)


# ============================================================
# 11. PRIORITY ORDER
# ============================================================

priority_order = {

    "CRITICAL": 1,

    "HIGH": 2,

    "MEDIUM": 3,

    "LOW": 4

}


actions_df["priority_order"] = (
    actions_df["priority"].map(
        priority_order
    )
)
# ============================================================
# CALCULATE NUMBER OF CRITICAL ACTIONS
# ============================================================

critical_actions = (
    actions_df["priority"]
    .astype(str)
    .str.upper()
    .eq("CRITICAL")
    .sum()
)

critical_actions = int(critical_actions)

# ============================================================
# 12. SORT ACTIONS
# ============================================================

actions_df = actions_df.sort_values(
    by=[
        "priority_order",
        "cash_impact"
    ],
    ascending=[
        True,
        False
    ]
)


actions_df = actions_df.drop(
    columns="priority_order"
)


# ============================================================
# 13. CALCULATE TOTAL POSITIVE COLLECTION OPPORTUNITY
# ============================================================

collection_actions = actions_df[
    actions_df["action_type"] == "ACCELERATE COLLECTION"
]


potential_collections = collection_actions[
    "cash_impact"
].sum()


# ============================================================
# 14. CALCULATE CRITICAL OUTFLOWS
# ============================================================

critical_outflows = actions_df[
    actions_df["cash_impact"] < 0
]["cash_impact"].abs().sum()


# ============================================================
# 15. CASH GAP
# ============================================================

immediate_cash_requirement = critical_outflows

cash_gap = max(
    0,
    immediate_cash_requirement - current_cash
)


# ============================================================
# 16. PRINT MAIN REPORT
# ============================================================

print("\n")
print("=" * 65)
print("NOURISH CAFE - LIQUIDITY ACTION ENGINE")
print("=" * 65)


print("\nCURRENT CASH")
print("-" * 65)

print(
    f"Current Cash: ₹{current_cash:,.2f}"
)


print("\n")
print("=" * 65)
print("PRIORITIZED ACTIONS")
print("=" * 65)


if len(actions_df) == 0:

    print("\nNo immediate liquidity actions detected.")

else:

    for index, row in actions_df.iterrows():

        print("\n---------------------------------------------")

        print(
            f"Priority       : {row['priority']}"
        )

        print(
            f"Action         : {row['action_type']}"
        )

        print(
            f"Reference      : {row['reference']}"
        )

        print(
            f"Counterparty   : {row['counterparty']}"
        )

        print(
            f"Cash Impact    : ₹{row['cash_impact']:,.2f}"
        )

        print(
            f"Reason         : {row['reason']}"
        )

        print(
            f"Recommendation : "
            f"{row['recommended_action']}"
        )


# ============================================================
# 17. LIQUIDITY SUMMARY
# ============================================================

print("\n")
print("=" * 65)
print("LIQUIDITY SUMMARY")
print("=" * 65)


print(
    f"\nPotential accelerated collections : "
    f"₹{potential_collections:,.2f}"
)


print(
    f"Critical / required outflows      : "
    f"₹{critical_outflows:,.2f}"
)


print(
    f"Current cash                      : "
    f"₹{current_cash:,.2f}"
)


print(
    f"Estimated cash gap                : "
    f"₹{cash_gap:,.2f}"
)


# ============================================================
# 18. OVERALL LIQUIDITY STATUS
# ============================================================

if current_cash < 0:

    liquidity_status = "CRITICAL"

elif cash_gap > 0:

    liquidity_status = "HIGH RISK"

else:

    liquidity_status = "MANAGEABLE"


print("\n")
print("=" * 65)
print("LIQUIDITY STATUS")
print("=" * 65)

print(
    f"\n{liquidity_status}"
)


# ============================================================
# 19. MANAGEMENT RECOMMENDATION
# ============================================================

print("\n")
print("=" * 65)
print("MANAGEMENT RECOMMENDATION")
print("=" * 65)


if liquidity_status == "CRITICAL":

    print(
        "\n1. Prioritize customer collections."
    )

    print(
        "2. Reserve funds for employee payroll."
    )

    print(
        "3. Review overdue supplier obligations."
    )

    print(
        "4. Defer non-critical payments where "
        "commercially permissible."
    )

    print(
        "5. Review short-term cash funding options."
    )


elif liquidity_status == "HIGH RISK":

    print(
        "\n1. Accelerate receivable collections."
    )

    print(
        "2. Closely monitor upcoming obligations."
    )

    print(
        "3. Protect minimum cash buffer."
    )


else:

    print(
        "\nCash position is currently manageable."
    )

    print(
        "Continue monitoring collections and "
        "upcoming obligations."
    )


# ============================================================
# 20. SAVE ACTION REPORT
# ============================================================

actions_df.to_csv(
    "liquidity_action_report.csv",
    index=False
)


print("\n")
print("=" * 65)
print("LIQUIDITY ACTION REPORT SAVED")
print("=" * 65)

print(
    "\nFile: liquidity_action_report.csv"
)