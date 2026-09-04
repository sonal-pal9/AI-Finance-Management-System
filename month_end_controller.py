import pandas as pd
import os


# ============================================================
# NOURISH CAFE - MONTH-END CLOSE CONTROLLER
# ============================================================


print("\n")
print("=" * 70)
print("              NOURISH CAFE")
print("             MONTH-END CLOSE")
print("=" * 70)


# ============================================================
# 1. CONFIGURATION
# ============================================================

REFERENCE_DATE = pd.Timestamp("2026-07-31")


RECON_FILE = "reconciliation_result_v3.csv"
AR_FILE = "accounts_receivable_report.csv"
AP_FILE = "accounts_payable_report.csv"
CASH_FILE = "cash_position_summary_v2.csv"
LIQUIDITY_FILE = "liquidity_action_report.csv"
TAX_FILE = "tax_verification_summary.csv"


# ============================================================
# 2. HELPER FUNCTION
# ============================================================

def load_file(filename):

    if not os.path.exists(filename):

        print(f"\nWARNING: {filename} not found.")

        return None

    return pd.read_csv(filename)


# ============================================================
# 3. LOAD REPORTS
# ============================================================

reconciliation = load_file(RECON_FILE)

ar = load_file(AR_FILE)

ap = load_file(AP_FILE)

cash = load_file(CASH_FILE)

liquidity = load_file(LIQUIDITY_FILE)

tax = load_file(TAX_FILE)


# ============================================================
# 4. INITIALIZE CLOSE CHECKS
# ============================================================

checks = []

blocking_issues = []

warnings = []

passed_checks = []


# ============================================================
# 5. RECONCILIATION CHECK
# ============================================================

print("\n")
print("=" * 70)
print("RECONCILIATION CHECK")
print("=" * 70)


if reconciliation is None:

    checks.append({
        "check": "Reconciliation report",
        "status": "ERROR",
        "reason": "Reconciliation report not found"
    })

    blocking_issues.append(
        "Reconciliation report is missing"
    )

else:

    total_transactions = len(reconciliation)

    if "status" in reconciliation.columns:

        status_counts = (
            reconciliation["status"]
            .astype(str)
            .str.upper()
            .value_counts()
        )

        matched = status_counts.get(
            "MATCHED",
            0
        )

        exceptions = (
            total_transactions - matched
        )

    else:

        matched = 0
        exceptions = total_transactions


    print(
        f"\nTotal records : {total_transactions}"
    )

    print(
        f"Matched       : {matched}"
    )

    print(
        f"Exceptions    : {exceptions}"
    )


    if exceptions == 0:

        passed_checks.append(
            "All transactions reconciled"
        )

        checks.append({
            "check": "Reconciliation",
            "status": "PASS",
            "reason": "No unresolved reconciliation exceptions"
        })

    else:

        blocking_issues.append(
            f"{exceptions} reconciliation exception(s)"
        )

        checks.append({
            "check": "Reconciliation",
            "status": "REVIEW",
            "reason":
                f"{exceptions} exception(s) require review"
        })


# ============================================================
# 6. AR CHECK
# ============================================================

print("\n")
print("=" * 70)
print("ACCOUNTS RECEIVABLE CHECK")
print("=" * 70)


if ar is None:

    blocking_issues.append(
        "Accounts Receivable report missing"
    )

else:

    # Find outstanding column

    if "outstanding_amount" in ar.columns:

        total_ar = ar[
            "outstanding_amount"
        ].sum()

    else:

        total_ar = 0


    # Collection status

    if "collection_status" in ar.columns:

        unpaid = (
            ar["collection_status"]
            .astype(str)
            .str.upper()
            .eq("UNPAID")
            .sum()
        )

        partial = (
            ar["collection_status"]
            .astype(str)
            .str.upper()
            .eq("PARTIALLY PAID")
            .sum()
        )

    else:

        unpaid = 0
        partial = 0


    print(
        f"\nTotal Outstanding AR : "
        f"₹{total_ar:,.2f}"
    )

    print(
        f"Unpaid invoices      : {unpaid}"
    )

    print(
        f"Partial invoices     : {partial}"
    )


    if total_ar == 0:

        passed_checks.append(
            "No outstanding receivables"
        )

        checks.append({
            "check": "Accounts Receivable",
            "status": "PASS",
            "reason": "No outstanding AR"
        })

    else:

        warnings.append(
            f"₹{total_ar:,.2f} accounts receivable outstanding"
        )

        checks.append({
            "check": "Accounts Receivable",
            "status": "REVIEW",
            "reason":
                f"₹{total_ar:,.2f} remains outstanding"
        })


# ============================================================
# 7. AP CHECK
# ============================================================

print("\n")
print("=" * 70)
print("ACCOUNTS PAYABLE CHECK")
print("=" * 70)


if ap is None:

    blocking_issues.append(
        "Accounts Payable report missing"
    )

else:

    if "outstanding_amount" in ap.columns:

        total_ap = ap[
            "outstanding_amount"
        ].sum()

    else:

        total_ap = 0


    if "payment_status" in ap.columns:

        ap_status = (
            ap["payment_status"]
            .astype(str)
            .str.upper()
        )

        unpaid_ap = (
            ap_status == "UNPAID"
        ).sum()

        partial_ap = (
            ap_status == "PARTIALLY PAID"
        ).sum()

        duplicate_ap = (
            ap_status.str.contains(
                "OVERPAID"
            )
        ).sum()

    else:

        unpaid_ap = 0
        partial_ap = 0
        duplicate_ap = 0


    print(
        f"\nTotal Outstanding AP : "
        f"₹{total_ap:,.2f}"
    )

    print(
        f"Unpaid bills         : {unpaid_ap}"
    )

    print(
        f"Partial bills        : {partial_ap}"
    )

    print(
        f"Possible duplicates  : {duplicate_ap}"
    )


    if duplicate_ap > 0:

        blocking_issues.append(
            f"{duplicate_ap} possible duplicate/overpaid supplier payment(s)"
        )


    if total_ap > 0:

        warnings.append(
            f"₹{total_ap:,.2f} accounts payable outstanding"
        )

        checks.append({
            "check": "Accounts Payable",
            "status": "REVIEW",
            "reason":
                f"₹{total_ap:,.2f} remains payable"
        })

    else:

        passed_checks.append(
            "No outstanding payables"
        )

        checks.append({
            "check": "Accounts Payable",
            "status": "PASS",
            "reason": "No outstanding AP"
        })


# ============================================================
# 8. CASH CHECK
# ============================================================

print("\n")
print("=" * 70)
print("CASH POSITION CHECK")
print("=" * 70)


current_cash = 0
cash_gap = 0


if cash is not None:

    if "metric" in cash.columns:

        cash_data = cash.set_index(
            "metric"
        )


        if "Current Cash" in cash_data.index:

            current_cash = float(
                cash_data.loc[
                    "Current Cash",
                    "amount"
                ]
            )


        if "Cash Gap" in cash_data.index:

            cash_gap = float(
                cash_data.loc[
                    "Cash Gap",
                    "amount"
                ]
            )


print(
    f"\nCurrent Cash : ₹{current_cash:,.2f}"
)

print(
    f"Cash Gap     : ₹{cash_gap:,.2f}"
)


if current_cash < 0:

    warnings.append(
        f"Negative cash position: ₹{abs(current_cash):,.2f}"
    )

    checks.append({
        "check": "Cash Position",
        "status": "WARNING",
        "reason":
            f"Negative cash position of "
            f"₹{abs(current_cash):,.2f}"
    })

elif cash_gap > 0:

    warnings.append(
        f"Cash gap of ₹{cash_gap:,.2f}"
    )

    checks.append({
        "check": "Cash Position",
        "status": "WARNING",
        "reason":
            f"Projected cash gap of "
            f"₹{cash_gap:,.2f}"
    })

else:

    passed_checks.append(
        "Cash position is sufficient"
    )

    checks.append({
        "check": "Cash Position",
        "status": "PASS",
        "reason":
            "No immediate cash gap detected"
    })


# ============================================================
# 9. LIQUIDITY CHECK
# ============================================================

print("\n")
print("=" * 70)
print("LIQUIDITY CHECK")
print("=" * 70)


if liquidity is not None:

    critical_actions = 0
    high_actions = 0

    if "priority" in liquidity.columns:

        priority = (
            liquidity["priority"]
            .astype(str)
            .str.upper()
        )

        critical_actions = (
            priority == "CRITICAL"
        ).sum()

        high_actions = (
            priority == "HIGH"
        ).sum()


    print(
        f"\nCritical actions : {critical_actions}"
    )

    print(
        f"High actions     : {high_actions}"
    )


    if critical_actions > 0:

        warnings.append(
            f"{critical_actions} critical liquidity action(s)"
        )

        checks.append({
            "check": "Liquidity",
            "status": "WARNING",
            "reason":
                f"{critical_actions} critical liquidity action(s)"
        })

    else:

        checks.append({
            "check": "Liquidity",
            "status": "PASS",
            "reason":
                "No critical liquidity action detected"
        })


# ============================================================
# 10. PAYROLL CHECK
# ============================================================

print("\n")
print("=" * 70)
print("PAYROLL CHECK")
print("=" * 70)


payroll_file = "data/payroll.csv"


if os.path.exists(payroll_file):

    payroll = pd.read_csv(
        payroll_file
    )


    if "payment_status" in payroll.columns:

        pending_payroll = payroll[
            payroll["payment_status"]
            .astype(str)
            .str.upper() != "PAID"
        ]

        pending_count = len(
            pending_payroll
        )

        pending_amount = pending_payroll[
            "net_salary"
        ].sum()


        print(
            f"\nPending employees : "
            f"{pending_count}"
        )

        print(
            f"Pending payroll   : "
            f"₹{pending_amount:,.2f}"
        )


        if pending_count > 0:

            warnings.append(
                f"₹{pending_amount:,.2f} pending payroll"
            )

            checks.append({
                "check": "Payroll",
                "status": "REVIEW",
                "reason":
                    f"₹{pending_amount:,.2f} payroll pending"
            })

        else:

            passed_checks.append(
                "Payroll fully paid"
            )

            checks.append({
                "check": "Payroll",
                "status": "PASS",
                "reason":
                    "All payroll records marked paid"
            })

else:

    checks.append({
        "check": "Payroll",
        "status": "ERROR",
        "reason": "Payroll file not found"
    })

    blocking_issues.append(
        "Payroll data unavailable"
    )

# ============================================================
# TAX & COMPLIANCE CHECK
# ============================================================

print("\n")
print("=" * 70)
print("TAX & COMPLIANCE CHECK")
print("=" * 70)


tax_mismatches = 0
late_filings = 0
open_tax_issues = 0
tax_score = 0
tax_status = "UNKNOWN"


if tax is None:

    blocking_issues.append(
        "Tax verification report missing"
    )

    checks.append({
        "check": "Tax & Compliance",
        "status": "ERROR",
        "reason": "Tax verification report not found"
    })

else:

    # Convert summary into dictionary

    tax_data = tax.set_index("metric")["value"]


    tax_mismatches = int(
        float(
            tax_data.get(
                "Mismatched Records",
                0
            )
        )
    )


    late_filings = int(
        float(
            tax_data.get(
                "Late Filings",
                0
            )
        )
    )


    open_tax_issues = int(
        float(
            tax_data.get(
                "Open Historical Issues",
                0
            )
        )
    )


    tax_score = float(
        tax_data.get(
            "Tax Readiness Score",
            0
        )
    )


    tax_status = str(
        tax_data.get(
            "Tax Status",
            "UNKNOWN"
        )
    )


    print(
        f"\nTax mismatches       : "
        f"{tax_mismatches}"
    )


    print(
        f"Late filings         : "
        f"{late_filings}"
    )


    print(
        f"Open historical     : "
        f"{open_tax_issues}"
    )


    print(
        f"Tax readiness       : "
        f"{tax_score}/100"
    )


    print(
        f"Tax status          : "
        f"{tax_status}"
    )


    # --------------------------------------------------------
    # Tax mismatch = accounting review issue
    # --------------------------------------------------------

    if tax_mismatches > 0:

        blocking_issues.append(
            f"{tax_mismatches} tax record mismatch(es)"
        )


    # --------------------------------------------------------
    # Open historical issues
    # --------------------------------------------------------

    if open_tax_issues > 0:

        warnings.append(
            f"{open_tax_issues} historical tax issue(s) remain open"
        )


    # --------------------------------------------------------
    # Late filings
    # --------------------------------------------------------

    if late_filings > 0:

        warnings.append(
            f"{late_filings} tax filing(s) were late"
        )


    # --------------------------------------------------------
    # Overall tax check
    # --------------------------------------------------------

    if tax_mismatches > 0:

        checks.append({

            "check": "Tax & Compliance",

            "status": "REVIEW",

            "reason":
                f"{tax_mismatches} tax mismatch(es) detected"
        })

    elif open_tax_issues > 0 or late_filings > 0:

        checks.append({

            "check": "Tax & Compliance",

            "status": "WARNING",

            "reason":
                "Tax records require compliance review"
        })

    else:

        passed_checks.append(
            "Tax records verified"
        )

        checks.append({

            "check": "Tax & Compliance",

            "status": "PASS",

            "reason":
                "No tax exceptions detected"
        })
# ============================================================
# 11. FINANCIAL INTEGRITY CHECK
# ============================================================

print("\n")
print("=" * 70)
print("FINANCIAL INTEGRITY CHECK")
print("=" * 70)


integrity_score = 100


# Deduct points for blocking issues

integrity_score -= (
    len(blocking_issues) * 15
)


# Deduct points for warnings

integrity_score -= (
    len(warnings) * 5
)


integrity_score = max(
    0,
    integrity_score
)


print(
    f"\nFinancial Integrity Score: "
    f"{integrity_score}/100"
)


if integrity_score >= 90:

    integrity_status = "STRONG"

elif integrity_score >= 75:

    integrity_status = "MODERATE"

elif integrity_score >= 50:

    integrity_status = "WEAK"

else:

    integrity_status = "CRITICAL"


print(
    f"Integrity Status: {integrity_status}"
)


# ============================================================
# 12. FINAL CLOSE DECISION
# ============================================================

print("\n")
print("=" * 70)
print("MONTH-END CLOSE DECISION")
print("=" * 70)


if len(blocking_issues) > 0:

    close_status = "REVIEW REQUIRED"

    close_reason = (
        "Blocking financial exceptions remain unresolved."
    )

elif len(warnings) > 0:

    close_status = "REVIEW REQUIRED"

    close_reason = (
        "No hard reconciliation blocker was detected, "
        "but financial conditions require management review."
    )

else:

    close_status = "READY TO CLOSE"

    close_reason = (
        "Required financial checks passed."
    )


print(
    f"\nSTATUS: {close_status}"
)

print(
    f"\nReason:"
)

print(
    close_reason
)


# ============================================================
# 13. BLOCKING ISSUES
# ============================================================

print("\n")
print("=" * 70)
print("BLOCKING ISSUES")
print("=" * 70)


if len(blocking_issues) == 0:

    print(
        "\nNo hard blocking issues detected."
    )

else:

    for i, issue in enumerate(
        blocking_issues,
        1
    ):

        print(
            f"{i}. {issue}"
        )


# ============================================================
# 14. WARNINGS
# ============================================================

print("\n")
print("=" * 70)
print("WARNINGS / MANAGEMENT REVIEW")
print("=" * 70)


if len(warnings) == 0:

    print(
        "\nNo warnings."
    )

else:

    for i, warning in enumerate(
        warnings,
        1
    ):

        print(
            f"{i}. {warning}"
        )


# ============================================================
# 15. PASSED CHECKS
# ============================================================

print("\n")
print("=" * 70)
print("PASSED CHECKS")
print("=" * 70)


if len(passed_checks) == 0:

    print(
        "\nNo checks passed."
    )

else:

    for check in passed_checks:

        print(
            f"✓ {check}"
        )


# ============================================================
# 16. CHECK TABLE
# ============================================================

print("\n")
print("=" * 70)
print("CLOSE CHECK SUMMARY")
print("=" * 70)


checks_df = pd.DataFrame(
    checks
)


print(
    checks_df.to_string(
        index=False
    )
)


# ============================================================
# 17. MANAGEMENT SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("MANAGEMENT SUMMARY")
print("=" * 70)


print(
    f"\nFinancial Integrity Score : "
    f"{integrity_score}/100"
)

print(
    f"Current Cash              : "
    f"₹{current_cash:,.2f}"
)

if ar is not None:

    print(
        f"Accounts Receivable      : "
        f"₹{total_ar:,.2f}"
    )

if ap is not None:

    print(
        f"Accounts Payable         : "
        f"₹{total_ap:,.2f}"
    )


print(
    f"\nMonth-End Status          : "
    f"{close_status}"
)


# ============================================================
# 18. SAVE CLOSE REPORT
# ============================================================

checks_df.to_csv(
    "month_end_check_summary.csv",
    index=False
)


final_summary = pd.DataFrame({

    "metric": [

        "Reference Date",

        "Current Cash",

        "Accounts Receivable",

        "Accounts Payable",

        "Financial Integrity Score",

        "Blocking Issues",

        "Warnings",

        "Close Status"
    ],

    "value": [

        str(REFERENCE_DATE.date()),

        current_cash,

        total_ar if ar is not None else 0,

        total_ap if ap is not None else 0,

        integrity_score,

        len(blocking_issues),

        len(warnings),

        close_status
    ]
})


final_summary.to_csv(
    "month_end_close_report.csv",
    index=False
)


# ============================================================
# 19. FINAL MESSAGE
# ============================================================

print("\n")
print("=" * 70)
print("MONTH-END CLOSE REPORT SAVED")
print("=" * 70)

print(
    "\n1. month_end_check_summary.csv"
)

print(
    "2. month_end_close_report.csv"
)

print("\n")
print("=" * 70)
print("MONTH-END CONTROLLER COMPLETE")
print("=" * 70)