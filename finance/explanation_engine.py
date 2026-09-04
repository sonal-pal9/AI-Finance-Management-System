# ============================================================
# EXPLANATION ENGINE
# Nourish Cafe - AI Finance Controller
# ============================================================


# ============================================================
# CASH EXPLANATION
# ============================================================

def explain_cash(
    current_cash,
    total_ar,
    total_ap
):

    current_cash = float(current_cash)
    total_ar = float(total_ar)
    total_ap = float(total_ap)

    if current_cash < 0:

        return f"""
CASH RISK EXPLANATION
----------------------------------------

Current Cash : ₹{current_cash:,.2f}
Risk Level   : CRITICAL

Why:
The business currently has a negative cash position
of ₹{abs(current_cash):,.2f}.

Impact:
Available cash is insufficient to cover immediate
financial obligations.

Supporting Information:
Outstanding Receivables : ₹{total_ar:,.2f}
Outstanding Payables    : ₹{total_ap:,.2f}

Recommended Action:
Prioritize customer collections, review supplier
payment timing, and evaluate immediate funding needs.
"""

    elif current_cash == 0:

        return """
CASH RISK EXPLANATION
----------------------------------------

Current Cash : ₹0.00
Risk Level   : HIGH

Why:
The business has no available cash buffer.

Recommended Action:
Prioritize collections and review upcoming payments.
"""

    else:

        return f"""
CASH POSITION EXPLANATION
----------------------------------------

Current Cash : ₹{current_cash:,.2f}
Risk Level   : LOW

The business currently has a positive cash position.

Recommended Action:
Continue monitoring cash inflows and upcoming
financial obligations.
"""


# ============================================================
# TAX EXPLANATION
# ============================================================

def explain_tax(
    tax_mismatches,
    tax_readiness
):

    tax_mismatches = int(tax_mismatches)
    tax_readiness = float(tax_readiness)

    if tax_mismatches > 0:

        return f"""
TAX RISK EXPLANATION
----------------------------------------

Tax Mismatches : {tax_mismatches}
Tax Readiness  : {tax_readiness:.1f}/100
Risk Level     : HIGH

Why:
Tax records contain {tax_mismatches} mismatch(es)
that require reconciliation.

Impact:
Incorrect tax records may result in inaccurate
GST liability reporting or filing errors.

Recommended Action:
Reconcile tax records against the Tally GST Payable
ledger and verify tax liabilities before filing.
"""

    return f"""
TAX COMPLIANCE EXPLANATION
----------------------------------------

Tax Mismatches : 0
Tax Readiness  : {tax_readiness:.1f}/100
Risk Level     : LOW

No tax mismatches were detected.

Recommended Action:
Continue routine tax monitoring and reconciliation.
"""


# ============================================================
# RECONCILIATION EXPLANATION
# ============================================================

def explain_reconciliation(
    mismatched_accounts,
    reconciliation_rate
):

    mismatched_accounts = int(mismatched_accounts)
    reconciliation_rate = float(reconciliation_rate)

    if mismatched_accounts > 0:

        return f"""
RECONCILIATION EXPLANATION
----------------------------------------

Exceptions          : {mismatched_accounts}
Reconciliation Rate : {reconciliation_rate:.1f}%
Risk Level          : HIGH

Why:
{mismatched_accounts} account-level reconciliation
exception(s) remain unresolved.

Impact:
Operational records do not completely agree with
the Tally ledger.

Recommended Action:
Review the underlying transactions and reconcile
operational records against the Tally ledger.
"""

    return f"""
RECONCILIATION EXPLANATION
----------------------------------------

Exceptions          : 0
Reconciliation Rate : {reconciliation_rate:.1f}%
Risk Level          : LOW

All checked accounts are currently reconciled.

Recommended Action:
Continue routine reconciliation monitoring.
"""


# ============================================================
# RECEIVABLES EXPLANATION
# ============================================================

def explain_receivables(
    total_ar
):

    total_ar = float(total_ar)

    if total_ar > 0:

        return f"""
ACCOUNTS RECEIVABLE EXPLANATION
----------------------------------------

Outstanding AR : ₹{total_ar:,.2f}
Risk Level     : HIGH

Why:
₹{total_ar:,.2f} remains outstanding from customers.

Impact:
Cash is tied up in unpaid customer balances and
may contribute to liquidity pressure.

Recommended Action:
Prioritize collection of overdue customer balances
and follow up on unpaid invoices.
"""

    return """
ACCOUNTS RECEIVABLE EXPLANATION
----------------------------------------

Outstanding AR : ₹0.00
Risk Level     : LOW

No outstanding customer receivables were detected.

Recommended Action:
Continue monitoring customer collections.
"""


# ============================================================
# PAYABLES EXPLANATION
# ============================================================

def explain_payables(
    total_ap
):

    total_ap = float(total_ap)

    if total_ap > 0:

        return f"""
ACCOUNTS PAYABLE EXPLANATION
----------------------------------------

Outstanding AP : ₹{total_ap:,.2f}
Risk Level     : HIGH

Why:
₹{total_ap:,.2f} remains payable to suppliers.

Impact:
Upcoming supplier obligations may create additional
pressure on available cash.

Recommended Action:
Review supplier due dates, verify invoice validity,
and prioritize payments according to cash availability.
"""

    return """
ACCOUNTS PAYABLE EXPLANATION
----------------------------------------

Outstanding AP : ₹0.00
Risk Level     : LOW

No outstanding supplier payables were detected.

Recommended Action:
Continue routine supplier payment monitoring.
"""


# ============================================================
# MONTH-END EXPLANATION
# ============================================================

def explain_month_end(
    month_end_status,
    current_cash,
    mismatched_accounts,
    tax_mismatches
):

    current_cash = float(current_cash)
    mismatched_accounts = int(mismatched_accounts)
    tax_mismatches = int(tax_mismatches)

    reasons = []

    if current_cash < 0:
        reasons.append(
            f"Negative cash position of "
            f"₹{abs(current_cash):,.2f}"
        )

    if mismatched_accounts > 0:
        reasons.append(
            f"{mismatched_accounts} reconciliation "
            f"exception(s)"
        )

    if tax_mismatches > 0:
        reasons.append(
            f"{tax_mismatches} tax mismatch(es)"
        )

    if month_end_status == "REVIEW REQUIRED":

        reason_text = "\n".join(
            f"- {reason}"
            for reason in reasons
        )

        return f"""
MONTH-END EXPLANATION
----------------------------------------

Status : {month_end_status}

Why:
The books require management review before
month-end close.

Blocking Issues:
{reason_text}

Recommended Action:
Resolve the blocking financial exceptions before
closing the reporting period.
"""

    elif month_end_status == "REVIEW RECOMMENDED":

        return f"""
MONTH-END EXPLANATION
----------------------------------------

Status : {month_end_status}

Why:
No immediate blocking exception prevents closing,
but outstanding financial items still require
management attention.

Recommended Action:
Review outstanding balances and complete routine
month-end controls before final close.
"""

    return f"""
MONTH-END EXPLANATION
----------------------------------------

Status : {month_end_status}

The financial controls currently indicate that
the books are ready for month-end close.

Recommended Action:
Complete the standard final close checklist.
"""


# ============================================================
# OVERALL RISK EXPLANATION
# ============================================================

def explain_overall_risk(
    integrity_score,
    integrity_status,
    current_cash,
    total_ar,
    total_ap,
    tax_mismatches,
    mismatched_accounts,
    critical_actions,
    pending_payroll
):

    integrity_score = float(integrity_score)
    current_cash = float(current_cash)
    total_ar = float(total_ar)
    total_ap = float(total_ap)
    tax_mismatches = int(tax_mismatches)
    mismatched_accounts = int(mismatched_accounts)
    critical_actions = int(critical_actions)
    pending_payroll = float(pending_payroll)

    risks = []

    if current_cash < 0:

        risks.append(
            f"- CRITICAL: Negative cash position of "
            f"₹{abs(current_cash):,.2f}"
        )

    if critical_actions > 0:

        risks.append(
            f"- CRITICAL: {critical_actions} "
            f"critical liquidity action(s)"
        )

    if total_ar > 0:

        risks.append(
            f"- HIGH: ₹{total_ar:,.2f} "
            f"outstanding receivables"
        )

    if total_ap > 0:

        risks.append(
            f"- HIGH: ₹{total_ap:,.2f} "
            f"outstanding payables"
        )

    if tax_mismatches > 0:

        risks.append(
            f"- HIGH: {tax_mismatches} "
            f"tax mismatch(es)"
        )

    if mismatched_accounts > 0:

        risks.append(
            f"- HIGH: {mismatched_accounts} "
            f"reconciliation exception(s)"
        )

    if pending_payroll > 0:

        risks.append(
            f"- MEDIUM: ₹{pending_payroll:,.2f} "
            f"pending payroll"
        )

    if not risks:

        risk_text = "- No major financial risks detected."

    else:

        risk_text = "\n".join(risks)

    return f"""
OVERALL FINANCIAL RISK EXPLANATION
----------------------------------------

Financial Integrity : {integrity_score:.1f}/100
Financial Status    : {integrity_status}

Major Risks:
{risk_text}

Overall Assessment:
The current financial condition is classified as
{integrity_status} based on the available financial
control indicators.

Recommended Priority:
Address the highest-severity financial risks first,
starting with critical cash and liquidity issues.
"""
# ============================================================
# SMART RECOMMENDATION EXPLANATION
# ============================================================

def explain_top_recommendation(
    recommendation,
    current_cash,
    total_ar,
    total_ap,
    pending_payroll,
    critical_actions
):
    """
    Explain why the selected recommendation
    received its priority.
    """

    supporting_risks = []

    # --------------------------------------------------------
    # Supporting financial risks
    # --------------------------------------------------------

    if current_cash < 0:
        supporting_risks.append(
            f"- Negative cash position: "
            f"₹{abs(current_cash):,.2f}"
        )

    if total_ar > 0:
        supporting_risks.append(
            f"- Outstanding receivables: "
            f"₹{total_ar:,.2f}"
        )

    if total_ap > 0:
        supporting_risks.append(
            f"- Outstanding payables: "
            f"₹{total_ap:,.2f}"
        )

    if pending_payroll > 0:
        supporting_risks.append(
            f"- Pending payroll: "
            f"₹{pending_payroll:,.2f}"
        )

    if critical_actions > 0:
        supporting_risks.append(
            f"- Critical liquidity actions: "
            f"{critical_actions}"
        )

    if supporting_risks:
        supporting_text = "\n".join(supporting_risks)
    else:
        supporting_text = (
            "- No additional supporting risks detected."
        )

    # --------------------------------------------------------
    # Priority reasoning
    # --------------------------------------------------------

    priority_reasons = []

    if recommendation.severity == "CRITICAL":
        priority_reasons.append(
            "- Critical risk severity"
        )

    elif recommendation.severity == "HIGH":
        priority_reasons.append(
            "- High financial risk severity"
        )

    elif recommendation.severity == "MEDIUM":
        priority_reasons.append(
            "- Medium financial risk severity"
        )

    if recommendation.amount > 0:
        priority_reasons.append(
            f"- Financial impact of "
            f"₹{recommendation.amount:,.2f}"
        )

    priority_reasons.append(
        "- Urgency was considered in the priority score"
    )

    priority_text = "\n".join(priority_reasons)

    # --------------------------------------------------------
    # Financial impact explanation
    # --------------------------------------------------------

    if recommendation.title == "Resolve cash deficit":

        financial_impact = (
            f"The business currently has a cash deficit of "
            f"₹{abs(current_cash):,.2f}, creating immediate "
            f"liquidity pressure."
        )

    elif recommendation.title == "Accelerate receivable collection":

        financial_impact = (
            f"₹{total_ar:,.2f} is tied up in outstanding "
            f"customer receivables and could be converted "
            f"into cash through collection."
        )

    elif recommendation.title == "Review supplier payment obligations":

        financial_impact = (
            f"₹{total_ap:,.2f} is outstanding to suppliers "
            f"and may create additional pressure on available cash."
        )

    elif recommendation.title == "Process pending payroll":

        financial_impact = (
            f"₹{pending_payroll:,.2f} of payroll remains pending "
            f"and requires sufficient liquidity."
        )

    elif recommendation.title == "Execute critical liquidity actions":

        financial_impact = (
            f"{critical_actions} critical liquidity action(s) "
            f"require immediate management attention."
        )

    elif recommendation.title == "Resolve tax mismatches":

        financial_impact = (
            f"{recommendation.count} tax mismatch(es) require "
            f"verification before financial reporting or filing."
        )

    elif recommendation.title == "Resolve reconciliation exceptions":

        financial_impact = (
            f"{recommendation.count} reconciliation exception(s) "
            f"remain unresolved and may affect financial accuracy."
        )

    else:

        financial_impact = (
            "The recommendation represents a financial "
            "control issue requiring management attention."
        )

    # --------------------------------------------------------
    # Final explanation
    # --------------------------------------------------------

    return f"""
TOP PRIORITY EXPLANATION
----------------------------------------

Priority       : {recommendation.priority}
Risk Level     : {recommendation.severity}
Priority Score : {recommendation.priority_score:.1f}/100

Recommendation:
{recommendation.title}

WHY:
{recommendation.reason}

FINANCIAL IMPACT:
{financial_impact}

WHY THIS RECEIVED THIS PRIORITY:
{priority_text}

SUPPORTING FINANCIAL RISKS:
{supporting_text}

RECOMMENDED ACTION:
{recommendation.action}
"""