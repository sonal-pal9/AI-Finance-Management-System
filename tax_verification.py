import pandas as pd
import os


# ============================================================
# NOURISH CAFE - TAX VERIFICATION ENGINE
# ============================================================


print("\n")
print("=" * 70)
print("              NOURISH CAFE")
print("          TAX VERIFICATION ENGINE")
print("=" * 70)


# ============================================================
# 1. FILES
# ============================================================

TAX_FILE = "data/tax_records.csv"
HISTORY_FILE = "data/tax_history.csv"


# ============================================================
# 2. LOAD FILES
# ============================================================

if not os.path.exists(TAX_FILE):

    print("\nERROR: tax_records.csv not found.")

    exit()


if not os.path.exists(HISTORY_FILE):

    print("\nERROR: tax_history.csv not found.")

    exit()


tax = pd.read_csv(TAX_FILE)

history = pd.read_csv(HISTORY_FILE)


# ============================================================
# 3. CLEAN NUMERIC COLUMNS
# ============================================================

numeric_tax_columns = [

    "books_taxable_amount",
    "books_tax_amount",
    "reported_taxable_amount",
    "reported_tax_amount",
    "late_days",
    "penalty_amount",
    "interest_amount"
]


for column in numeric_tax_columns:

    tax[column] = pd.to_numeric(
        tax[column],
        errors="coerce"
    ).fillna(0)


history["amount"] = pd.to_numeric(
    history["amount"],
    errors="coerce"
).fillna(0)


# ============================================================
# 4. CALCULATE DIFFERENCES
# ============================================================

tax["taxable_difference"] = (
    tax["books_taxable_amount"]
    -
    tax["reported_taxable_amount"]
)


tax["tax_difference"] = (
    tax["books_tax_amount"]
    -
    tax["reported_tax_amount"]
)


tax["absolute_tax_difference"] = (
    tax["tax_difference"].abs()
)


tax["absolute_taxable_difference"] = (
    tax["taxable_difference"].abs()
)


# ============================================================
# 5. DETERMINE TAX STATUS
# ============================================================

TOLERANCE = 1.00


def determine_tax_status(row):

    taxable_difference = (
        abs(row["taxable_difference"])
    )

    tax_difference = (
        abs(row["tax_difference"])
    )


    # Tax values match within tolerance

    if (
        taxable_difference <= TOLERANCE
        and
        tax_difference <= TOLERANCE
    ):

        return "MATCHED"


    # Taxable amount differs

    elif taxable_difference > TOLERANCE:

        return "TAXABLE AMOUNT MISMATCH"


    # Tax amount differs

    else:

        return "TAX AMOUNT MISMATCH"


tax["verification_status"] = (
    tax.apply(
        determine_tax_status,
        axis=1
    )
)


# ============================================================
# 6. FILING STATUS
# ============================================================

tax["filing_status"] = (
    tax["filing_status"]
    .astype(str)
    .str.upper()
)


tax["late_status"] = tax.apply(

    lambda row:
        "LATE"
        if row["late_days"] > 0
        else "ON TIME",

    axis=1
)


# ============================================================
# 7. TOTAL TAX DIFFERENCE
# ============================================================

total_tax_difference = tax[
    "absolute_tax_difference"
].sum()


total_taxable_difference = tax[
    "absolute_taxable_difference"
].sum()


# ============================================================
# 8. MATCH / MISMATCH COUNTS
# ============================================================

matched_count = (
    tax["verification_status"]
    == "MATCHED"
).sum()


mismatch_count = (
    tax["verification_status"]
    != "MATCHED"
).sum()


late_count = (
    tax["late_days"] > 0
).sum()


# ============================================================
# 9. PENALTIES + INTEREST
# ============================================================

total_penalties = tax[
    "penalty_amount"
].sum()


total_interest = tax[
    "interest_amount"
].sum()


total_historical_penalties = history[
    history["issue_type"]
    .astype(str)
    .str.upper()
    .isin(
        [
            "LATE_FILING",
            "TAX_MISMATCH"
        ]
    )
]["amount"].sum()


# ============================================================
# 10. HISTORICAL ISSUES
# ============================================================

history["status"] = (
    history["status"]
    .astype(str)
    .str.upper()
)


historical_total = len(history)


historical_open = (
    history["status"]
    == "OPEN"
).sum()


historical_resolved = (
    history["status"]
    == "RESOLVED"
).sum()


# ============================================================
# 11. HISTORICAL ISSUE TYPES
# ============================================================

historical_late = (
    history["issue_type"]
    .astype(str)
    .str.upper()
    == "LATE_FILING"
).sum()


historical_mismatch = (
    history["issue_type"]
    .astype(str)
    .str.upper()
    == "TAX_MISMATCH"
).sum()


historical_missing_docs = (
    history["issue_type"]
    .astype(str)
    .str.upper()
    == "DOCUMENT_MISSING"
).sum()


# ============================================================
# 12. TAX READINESS SCORE
# ============================================================

# Start at 100

tax_score = 100


# Current tax mismatches

tax_score -= (
    mismatch_count * 15
)


# Late filings

tax_score -= (
    late_count * 5
)


# Open historical issues

tax_score -= (
    historical_open * 10
)


# Clamp between 0 and 100

tax_score = max(
    0,
    min(
        100,
        tax_score
    )
)


# ============================================================
# 13. TAX STATUS
# ============================================================

if tax_score >= 90:

    tax_status = "READY"

elif tax_score >= 75:

    tax_status = "MINOR REVIEW"

elif tax_score >= 50:

    tax_status = "REVIEW REQUIRED"

else:

    tax_status = "HIGH RISK"


# ============================================================
# 14. BUILD EXCEPTION LIST
# ============================================================

exceptions = []


# Current tax mismatches

for _, row in tax[
    tax["verification_status"]
    != "MATCHED"
].iterrows():

    exceptions.append({

        "severity": "HIGH",

        "source": "CURRENT TAX RECORD",

        "reference": row["tax_record_id"],

        "period": row["period"],

        "issue":
            row["verification_status"],

        "difference":
            row["tax_difference"],

        "explanation":
            (
                f"Books tax = "
                f"₹{row['books_tax_amount']:,.2f}, "
                f"reported tax = "
                f"₹{row['reported_tax_amount']:,.2f}"
            ),

        "recommended_action":
            "Review source records and reconcile "
            "before relying on the reported figure"

    })


# ============================================================
# 15. LATE FILINGS
# ============================================================

for _, row in tax[
    tax["late_days"] > 0
].iterrows():

    exceptions.append({

        "severity": "MEDIUM",

        "source": "CURRENT TAX RECORD",

        "reference": row["tax_record_id"],

        "period": row["period"],

        "issue": "LATE FILING",

        "difference":
            row["penalty_amount"]
            +
            row["interest_amount"],

        "explanation":
            (
                f"Filing was "
                f"{int(row['late_days'])} day(s) late"
            ),

        "recommended_action":
            "Verify filing date, penalty and interest "
            "against supporting records"

    })


# ============================================================
# 16. OPEN HISTORICAL ISSUES
# ============================================================

for _, row in history[
    history["status"] == "OPEN"
].iterrows():

    exceptions.append({

        "severity": "HIGH",

        "source": "HISTORICAL RECORD",

        "reference": row["record_id"],

        "period": row["period"],

        "issue":
            row["issue_type"],

        "difference":
            row["amount"],

        "explanation":
            (
                f"Historical issue remains "
                f"{row['status']}"
            ),

        "recommended_action":
            "Investigate and document resolution "
            "before treating tax records as complete"

    })


# ============================================================
# 17. CREATE EXCEPTION DATAFRAME
# ============================================================

exceptions_df = pd.DataFrame(
    exceptions
)


# ============================================================
# 18. PRINT CURRENT TAX VERIFICATION
# ============================================================

print("\n")
print("=" * 70)
print("CURRENT TAX VERIFICATION")
print("=" * 70)


print(
    f"\nTax records checked : {len(tax)}"
)

print(
    f"Matched             : {matched_count}"
)

print(
    f"Mismatches           : {mismatch_count}"
)

print(
    f"Late filings         : {late_count}"
)


print(
    f"\nTax difference       : "
    f"₹{total_tax_difference:,.2f}"
)


print(
    f"Taxable difference   : "
    f"₹{total_taxable_difference:,.2f}"
)


print(
    f"Penalties            : "
    f"₹{total_penalties:,.2f}"
)


print(
    f"Interest             : "
    f"₹{total_interest:,.2f}"
)


# ============================================================
# 19. PRINT HISTORICAL COMPLIANCE
# ============================================================

print("\n")
print("=" * 70)
print("HISTORICAL TAX COMPLIANCE")
print("=" * 70)


print(
    f"\nHistorical records   : "
    f"{historical_total}"
)


print(
    f"Resolved             : "
    f"{historical_resolved}"
)


print(
    f"Open                 : "
    f"{historical_open}"
)


print(
    f"Late filing issues   : "
    f"{historical_late}"
)


print(
    f"Tax mismatch issues  : "
    f"{historical_mismatch}"
)


print(
    f"Missing documents    : "
    f"{historical_missing_docs}"
)


# ============================================================
# 20. TAX READINESS
# ============================================================

print("\n")
print("=" * 70)
print("TAX READINESS")
print("=" * 70)


print(
    f"\nTax Readiness Score : "
    f"{tax_score}/100"
)


print(
    f"Status              : "
    f"{tax_status}"
)


# ============================================================
# 21. EXCEPTIONS
# ============================================================

print("\n")
print("=" * 70)
print("TAX EXCEPTIONS")
print("=" * 70)


if len(exceptions_df) == 0:

    print(
        "\nNo tax exceptions detected."
    )

else:

    for _, row in exceptions_df.iterrows():

        print("\n------------------------------------------")

        print(
            f"Severity       : "
            f"{row['severity']}"
        )

        print(
            f"Source         : "
            f"{row['source']}"
        )

        print(
            f"Reference      : "
            f"{row['reference']}"
        )

        print(
            f"Period         : "
            f"{row['period']}"
        )

        print(
            f"Issue          : "
            f"{row['issue']}"
        )

        print(
            f"Difference     : "
            f"₹{row['difference']:,.2f}"
        )

        print(
            f"Explanation    : "
            f"{row['explanation']}"
        )

        print(
            f"Recommendation : "
            f"{row['recommended_action']}"
        )


# ============================================================
# 22. TAX SUMMARY
# ============================================================

tax_summary = pd.DataFrame({

    "metric": [

        "Tax Records Checked",

        "Matched Records",

        "Mismatched Records",

        "Late Filings",

        "Tax Difference",

        "Taxable Difference",

        "Penalties",

        "Interest",

        "Historical Issues",

        "Open Historical Issues",

        "Tax Readiness Score",

        "Tax Status"
    ],

    "value": [

        len(tax),

        matched_count,

        mismatch_count,

        late_count,

        total_tax_difference,

        total_taxable_difference,

        total_penalties,

        total_interest,

        historical_total,

        historical_open,

        tax_score,

        tax_status
    ]
})


# ============================================================
# 23. SAVE REPORTS
# ============================================================

tax.to_csv(
    "tax_verification_detail.csv",
    index=False
)


exceptions_df.to_csv(
    "tax_exceptions.csv",
    index=False
)


tax_summary.to_csv(
    "tax_verification_summary.csv",
    index=False
)


# ============================================================
# 24. FINAL MESSAGE
# ============================================================

print("\n")
print("=" * 70)
print("TAX VERIFICATION COMPLETE")
print("=" * 70)


print(
    "\nReports saved:"
)

print(
    "1. tax_verification_detail.csv"
)

print(
    "2. tax_exceptions.csv"
)

print(
    "3. tax_verification_summary.csv"
)