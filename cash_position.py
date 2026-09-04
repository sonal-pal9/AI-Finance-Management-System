import pandas as pd


# ============================================================
# NOURISH CAFE - CASH POSITION & FORECAST ENGINE V2
# ============================================================


# ============================================================
# 1. LOAD DATA
# ============================================================

bank = pd.read_csv(
    "data/bank_transactions.csv"
)

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
# 2. CONVERT DATES
# ============================================================

bank["txn_date"] = pd.to_datetime(
    bank["txn_date"]
)

invoices["due_date"] = pd.to_datetime(
    invoices["due_date"]
)

supplier_bills["due_date"] = pd.to_datetime(
    supplier_bills["due_date"]
)


# ============================================================
# 3. REFERENCE DATE
# ============================================================

REFERENCE_DATE = pd.Timestamp(
    "2026-07-31"
)


# ============================================================
# 4. OPENING BANK BALANCE
# ============================================================

OPENING_BANK_BALANCE = 250000.00


# ============================================================
# 5. BANK CASH POSITION
# ============================================================

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
# 6. ACCOUNTS RECEIVABLE
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


# Days relative to month-end

ar["days_difference"] = (
    REFERENCE_DATE
    - ar["due_date"]
).dt.days


# Positive = overdue
ar["days_overdue"] = (
    ar["days_difference"].clip(lower=0)
)


# Positive = days remaining
ar["days_until_due"] = (
    -ar["days_difference"].clip(upper=0)
)


# Only unpaid/partially-paid invoices

open_ar = ar[
    ar["outstanding_amount"] > 0
].copy()


# ============================================================
# 7. AR CATEGORIES
# ============================================================

overdue_ar = open_ar[
    open_ar["days_overdue"] > 0
].copy()


due_next_7_ar = open_ar[
    (open_ar["days_until_due"] >= 0)
    &
    (open_ar["days_until_due"] <= 7)
].copy()


current_ar = open_ar[
    open_ar["days_until_due"] > 7
].copy()


total_ar = open_ar[
    "outstanding_amount"
].sum()


overdue_ar_amount = overdue_ar[
    "outstanding_amount"
].sum()


due_next_7_ar_amount = due_next_7_ar[
    "outstanding_amount"
].sum()


current_ar_amount = current_ar[
    "outstanding_amount"
].sum()


# ============================================================
# 8. ACCOUNTS PAYABLE
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


# Days relative to month-end

ap["days_difference"] = (
    REFERENCE_DATE
    - ap["due_date"]
).dt.days


ap["days_overdue"] = (
    ap["days_difference"].clip(lower=0)
)


ap["days_until_due"] = (
    -ap["days_difference"].clip(upper=0)
)


# Open bills

open_ap = ap[
    ap["outstanding_amount"] > 0
].copy()


# ============================================================
# 9. AP CATEGORIES
# ============================================================

overdue_ap = open_ap[
    open_ap["days_overdue"] > 0
].copy()


due_next_7_ap = open_ap[
    (open_ap["days_until_due"] >= 0)
    &
    (open_ap["days_until_due"] <= 7)
].copy()


future_ap = open_ap[
    open_ap["days_until_due"] > 7
].copy()


total_ap = open_ap[
    "outstanding_amount"
].sum()


overdue_ap_amount = overdue_ap[
    "outstanding_amount"
].sum()


due_next_7_ap_amount = due_next_7_ap[
    "outstanding_amount"
].sum()


future_ap_amount = future_ap[
    "outstanding_amount"
].sum()


# ============================================================
# 10. PAYROLL
# ============================================================

pending_payroll = payroll[
    payroll["payment_status"].str.lower() != "paid"
].copy()


pending_payroll_amount = pending_payroll[
    "net_salary"
].sum()


# For our synthetic dataset, pending payroll is assumed
# to be payable within the next 7 days.


# ============================================================
# 11. COLLECTION ASSUMPTIONS
# ============================================================

# We do NOT assume that every receivable will be collected.
#
# Conservative:
#   50% of overdue + 30% of due-soon receivables
#
# Base:
#   75% of overdue + 70% of due-soon receivables
#
# Optimistic:
#   100% of overdue + 100% of due-soon receivables


CONSERVATIVE_OVERDUE_COLLECTION_RATE = 0.50
CONSERVATIVE_DUE_COLLECTION_RATE = 0.30

BASE_OVERDUE_COLLECTION_RATE = 0.75
BASE_DUE_COLLECTION_RATE = 0.70

OPTIMISTIC_OVERDUE_COLLECTION_RATE = 1.00
OPTIMISTIC_DUE_COLLECTION_RATE = 1.00


# ============================================================
# 12. CASH FORECAST FUNCTION
# ============================================================

def calculate_projected_cash(
    overdue_rate,
    due_rate
):

    expected_collections = (
        overdue_ar_amount * overdue_rate
        +
        due_next_7_ar_amount * due_rate
    )

    expected_outflows = (
        overdue_ap_amount
        +
        due_next_7_ap_amount
        +
        pending_payroll_amount
    )

    projected_cash = (
        current_cash
        +
        expected_collections
        -
        expected_outflows
    )

    return (
        expected_collections,
        expected_outflows,
        projected_cash
    )


# ============================================================
# 13. SCENARIO CALCULATIONS
# ============================================================

(
    conservative_collections,
    conservative_outflows,
    conservative_cash
) = calculate_projected_cash(
    CONSERVATIVE_OVERDUE_COLLECTION_RATE,
    CONSERVATIVE_DUE_COLLECTION_RATE
)


(
    base_collections,
    base_outflows,
    base_cash
) = calculate_projected_cash(
    BASE_OVERDUE_COLLECTION_RATE,
    BASE_DUE_COLLECTION_RATE
)


(
    optimistic_collections,
    optimistic_outflows,
    optimistic_cash
) = calculate_projected_cash(
    OPTIMISTIC_OVERDUE_COLLECTION_RATE,
    OPTIMISTIC_DUE_COLLECTION_RATE
)


# ============================================================
# 14. CASH RISK
# ============================================================

MINIMUM_CASH_BUFFER = 100000


def get_cash_status(projected_cash):

    if projected_cash < 0:
        return "CRITICAL"

    elif projected_cash < MINIMUM_CASH_BUFFER:
        return "LOW BUFFER"

    else:
        return "HEALTHY"


conservative_status = get_cash_status(
    conservative_cash
)

base_status = get_cash_status(
    base_cash
)

optimistic_status = get_cash_status(
    optimistic_cash
)


# ============================================================
# 15. IMMEDIATE CASH OBLIGATIONS
# ============================================================

immediate_obligations = (
    overdue_ap_amount
    +
    due_next_7_ap_amount
    +
    pending_payroll_amount
)


# ============================================================
# 16. CASH GAP
# ============================================================

cash_gap = max(
    0,
    immediate_obligations - current_cash
)


# ============================================================
# 17. RECOMMENDED ACTION
# ============================================================

if base_cash < 0:

    recommended_action = (
        "URGENT: Cash shortfall expected. "
        "Prioritize collections, review supplier payment "
        "timing, and escalate cash planning."
    )

elif base_cash < MINIMUM_CASH_BUFFER:

    recommended_action = (
        "Cash buffer is low. Accelerate collections "
        "and carefully schedule non-critical payments."
    )

elif overdue_ap_amount > 0:

    recommended_action = (
        "Cash is currently manageable, but overdue "
        "supplier obligations require review."
    )

else:

    recommended_action = (
        "Cash position is healthy. Continue monitoring "
        "collections and scheduled payments."
    )


# ============================================================
# 18. CREATE CASH SUMMARY
# ============================================================

cash_summary = pd.DataFrame({

    "metric": [

        "Opening Bank Balance",

        "Bank Inflows",

        "Bank Outflows",

        "Current Cash",

        "Total Accounts Receivable",

        "Overdue Receivables",

        "Receivables Due Next 7 Days",

        "Future Receivables",

        "Total Accounts Payable",

        "Overdue Payables",

        "Payables Due Next 7 Days",

        "Future Payables",

        "Pending Payroll",

        "Immediate Cash Obligations",

        "Cash Gap"
    ],

    "amount": [

        OPENING_BANK_BALANCE,

        total_inflows,

        total_outflows,

        current_cash,

        total_ar,

        overdue_ar_amount,

        due_next_7_ar_amount,

        current_ar_amount,

        total_ap,

        overdue_ap_amount,

        due_next_7_ap_amount,

        future_ap_amount,

        pending_payroll_amount,

        immediate_obligations,

        cash_gap
    ]
})


# ============================================================
# 19. SCENARIO SUMMARY
# ============================================================

scenario_summary = pd.DataFrame({

    "scenario": [
        "CONSERVATIVE",
        "BASE",
        "OPTIMISTIC"
    ],

    "expected_collections": [
        conservative_collections,
        base_collections,
        optimistic_collections
    ],

    "expected_outflows": [
        conservative_outflows,
        base_outflows,
        optimistic_outflows
    ],

    "projected_cash": [
        conservative_cash,
        base_cash,
        optimistic_cash
    ],

    "status": [
        conservative_status,
        base_status,
        optimistic_status
    ]
})


# ============================================================
# 20. PRINT MAIN REPORT
# ============================================================

print("\n")
print("=" * 60)
print("NOURISH CAFE - CASH POSITION & FORECAST")
print("=" * 60)


print("\nCURRENT CASH POSITION")
print("-" * 60)

for _, row in cash_summary.iterrows():

    print(
        f"{row['metric']:<35}"
        f" ₹{row['amount']:,.2f}"
    )


# ============================================================
# 21. PRINT AR BREAKDOWN
# ============================================================

print("\n")
print("=" * 60)
print("RECEIVABLES BREAKDOWN")
print("=" * 60)

print(
    f"Total AR              : ₹{total_ar:,.2f}"
)

print(
    f"Overdue AR            : ₹{overdue_ar_amount:,.2f}"
)

print(
    f"Due next 7 days       : ₹{due_next_7_ar_amount:,.2f}"
)

print(
    f"Future AR             : ₹{current_ar_amount:,.2f}"
)


# ============================================================
# 22. PRINT AP BREAKDOWN
# ============================================================

print("\n")
print("=" * 60)
print("PAYABLES BREAKDOWN")
print("=" * 60)

print(
    f"Total AP              : ₹{total_ap:,.2f}"
)

print(
    f"Overdue AP            : ₹{overdue_ap_amount:,.2f}"
)

print(
    f"Due next 7 days       : ₹{due_next_7_ap_amount:,.2f}"
)

print(
    f"Future AP             : ₹{future_ap_amount:,.2f}"
)


# ============================================================
# 23. PRINT PAYROLL
# ============================================================

print("\n")
print("=" * 60)
print("PAYROLL")
print("=" * 60)

print(
    f"Pending Payroll       : ₹{pending_payroll_amount:,.2f}"
)


# ============================================================
# 24. PRINT SCENARIOS
# ============================================================

print("\n")
print("=" * 60)
print("7-DAY CASH FORECAST SCENARIOS")
print("=" * 60)

for _, row in scenario_summary.iterrows():

    print(
        f"\n{row['scenario']}"
    )

    print(
        f"Expected Collections : "
        f"₹{row['expected_collections']:,.2f}"
    )

    print(
        f"Expected Outflows    : "
        f"₹{row['expected_outflows']:,.2f}"
    )

    print(
        f"Projected Cash       : "
        f"₹{row['projected_cash']:,.2f}"
    )

    print(
        f"Status               : "
        f"{row['status']}"
    )


# ============================================================
# 25. PRINT CASH RISK
# ============================================================

print("\n")
print("=" * 60)
print("CASH RISK ASSESSMENT")
print("=" * 60)

print(
    f"\nBase Case Status: {base_status}"
)

print(
    f"Base Case Projected Cash: "
    f"₹{base_cash:,.2f}"
)

print(
    f"\nCash Gap: ₹{cash_gap:,.2f}"
)

print(
    f"\nRecommended Action:"
)

print(
    recommended_action
)


# ============================================================
# 26. SAVE REPORTS
# ============================================================

cash_summary.to_csv(
    "cash_position_summary_v2.csv",
    index=False
)


scenario_summary.to_csv(
    "cash_forecast_scenarios.csv",
    index=False
)


print("\n")
print("=" * 60)
print("REPORTS SAVED SUCCESSFULLY")
print("=" * 60)

print(
    "\n1. cash_position_summary_v2.csv"
)

print(
    "2. cash_forecast_scenarios.csv"
)