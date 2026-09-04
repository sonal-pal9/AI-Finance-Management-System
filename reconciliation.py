import pandas as pd


# ==========================================
# 1. LOAD DATA
# ==========================================

invoices = pd.read_csv("data/sales_invoices.csv")
payments = pd.read_csv("data/customer_payments.csv")
bank = pd.read_csv("data/bank_transactions.csv")


# ==========================================
# 2. AGGREGATE PAYMENTS PER INVOICE
# ==========================================

# One invoice can have one or multiple payments

payment_summary = payments.groupby("invoice_id").agg(
    total_payment_amount=("payment_amount", "sum"),
    payment_count=("payment_id", "count")
).reset_index()


# ==========================================
# 3. CONNECT PAYMENTS TO BANK TRANSACTIONS
# ==========================================

# customer_payments:
#
# payment_id       invoice_id
# PAY0001    →     INV0001
#
# bank_transactions:
#
# reference
# PAY0001

payment_bank = payments.merge(
    bank,
    left_on="payment_id",
    right_on="reference",
    how="left"
)


# ==========================================
# 4. AGGREGATE BANK AMOUNT PER INVOICE
# ==========================================

bank_summary = payment_bank.groupby("invoice_id").agg(
    total_bank_amount=("amount", "sum"),
    bank_transaction_count=("bank_txn_id", "count")
).reset_index()


# ==========================================
# 5. MERGE EVERYTHING
# ==========================================

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


# ==========================================
# 6. HANDLE MISSING VALUES
# ==========================================

result["total_payment_amount"] = (
    result["total_payment_amount"].fillna(0)
)

result["payment_count"] = (
    result["payment_count"].fillna(0)
)

result["total_bank_amount"] = (
    result["total_bank_amount"].fillna(0)
)

result["bank_transaction_count"] = (
    result["bank_transaction_count"].fillna(0)
)


# ==========================================
# 7. RECONCILIATION LOGIC
# ==========================================

def get_status(row):

    invoice_amount = row["invoice_total"]
    payment_amount = row["total_payment_amount"]
    bank_amount = row["total_bank_amount"]
    payment_count = row["payment_count"]

    # --------------------------------------
    # CASE 1: No payment
    # --------------------------------------

    if payment_amount == 0:
        return "UNPAID"


    # --------------------------------------
    # CASE 2: Partial payment
    # --------------------------------------

    elif payment_amount < invoice_amount:
        return "PARTIALLY PAID"


    # --------------------------------------
    # CASE 3: Overpaid
    # --------------------------------------

    elif payment_amount > invoice_amount:

        if payment_count > 1:
            return "OVERPAID / POSSIBLE DUPLICATE"

        return "OVERPAID"


    # --------------------------------------
    # CASE 4: Payment matches invoice,
    # but bank amount is missing
    # --------------------------------------

    elif bank_amount == 0:
        return "BANK PAYMENT MISSING"


    # --------------------------------------
    # CASE 5: Payment and bank differ
    # --------------------------------------

    elif bank_amount != payment_amount:
        return "BANK MISMATCH"


    # --------------------------------------
    # CASE 6: Everything matches
    # --------------------------------------

    else:
        return "MATCHED"


# ==========================================
# 8. APPLY RECONCILIATION LOGIC
# ==========================================

result["status"] = result.apply(
    get_status,
    axis=1
)


# ==========================================
# 9. SELECT FINAL COLUMNS
# ==========================================

final_result = result[
    [
        "invoice_id",
        "invoice_total",
        "total_payment_amount",
        "payment_count",
        "total_bank_amount",
        "bank_transaction_count",
        "status"
    ]
]


# ==========================================
# 10. PRINT RESULTS
# ==========================================

print("\n================================")
print("NOURISH CAFE RECONCILIATION")
print("================================\n")

print(final_result)


# ==========================================
# 11. STATUS COUNT
# ==========================================

print("\n================================")
print("STATUS COUNT")
print("================================\n")

print(final_result["status"].value_counts())


# ==========================================
# 12. PROBLEMATIC RECORDS
# ==========================================

problems = final_result[
    final_result["status"] != "MATCHED"
]

print("\n================================")
print("PROBLEMATIC RECORDS")
print("================================\n")

print(problems)


# ==========================================
# 13. SAVE RESULT
# ==========================================

final_result.to_csv(
    "reconciliation_result_v3.csv",
    index=False
)

print("\nReconciliation complete!")
print("Result saved as reconciliation_result_v3.csv")