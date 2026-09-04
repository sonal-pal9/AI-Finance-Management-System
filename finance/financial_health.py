# ============================================================
# FINANCIAL HEALTH ENGINE
# Nourish Cafe - AI Finance Controller
# ============================================================

from dataclasses import dataclass


# ============================================================
# FINANCIAL HEALTH RESULT
# ============================================================

@dataclass
class FinancialHealth:

    integrity_score: float

    integrity_status: str

    current_cash: float

    total_ar: float

    total_ap: float

    tax_readiness: float

    reconciliation_rate: float

    month_end_status: str


# ============================================================
# FINANCIAL STATUS
# ============================================================

def get_financial_status(score):
    """
    Convert financial integrity score into a status.
    """

    if score >= 90:
        return "STRONG"

    elif score >= 75:
        return "MODERATE"

    elif score >= 50:
        return "WEAK"

    else:
        return "CRITICAL"


# ============================================================
# MONTH-END STATUS
# ============================================================

def get_month_end_status(
    mismatched_accounts,
    tax_mismatches,
    current_cash,
    critical_actions,
    total_ar,
    total_ap,
    pending_payroll
):
    """
    Determine whether the books can be closed.
    """

    # --------------------------------------------------------
    # Blocking issues
    # --------------------------------------------------------

    if mismatched_accounts > 0:
        return "REVIEW REQUIRED"

    if tax_mismatches > 0:
        return "REVIEW REQUIRED"

    # --------------------------------------------------------
    # Critical cash / liquidity issues
    # --------------------------------------------------------

    if current_cash < 0:
        return "REVIEW REQUIRED"

    if critical_actions > 0:
        return "REVIEW REQUIRED"

    # --------------------------------------------------------
    # Non-critical outstanding items
    # --------------------------------------------------------

    if total_ar > 0:
        return "REVIEW RECOMMENDED"

    if total_ap > 0:
        return "REVIEW RECOMMENDED"

    if pending_payroll > 0:
        return "REVIEW RECOMMENDED"

    # --------------------------------------------------------
    # Everything clear
    # --------------------------------------------------------

    return "READY TO CLOSE"


# ============================================================
# FINANCIAL INTEGRITY SCORE
# ============================================================
def calculate_integrity_score(
    mismatched_accounts,
    tax_mismatches,
    current_cash,
    total_ar,
    total_ap,
    critical_actions
):
    """
    Calculate a practical financial integrity score.

    Higher score = healthier financial position.
    """

    score = 100.0

    # -------------------------------------------------
    # 1. CASH POSITION — biggest financial concern
    # -------------------------------------------------
    if current_cash < 0:
        score -= 35
    elif current_cash == 0:
        score -= 20
    elif current_cash < 50000:
        score -= 10

    # -------------------------------------------------
    # 2. RECONCILIATION
    # -------------------------------------------------
    reconciliation_penalty = min(mismatched_accounts * 1.5, 15)
    score -= reconciliation_penalty

    # -------------------------------------------------
    # 3. TAX MISMATCHES
    # -------------------------------------------------
    tax_penalty = min(tax_mismatches * 3, 10)
    score -= tax_penalty

    # -------------------------------------------------
    # 4. CRITICAL ACTIONS
    # -------------------------------------------------
    action_penalty = min(critical_actions * 3, 10)
    score -= action_penalty

    # -------------------------------------------------
    # 5. OUTSTANDING RECEIVABLES
    # Normal business activity, so small penalty
    # -------------------------------------------------
    if total_ar > 0:
        score -= 2

    # -------------------------------------------------
    # 6. OUTSTANDING PAYABLES
    # Normal business activity, so small penalty
    # -------------------------------------------------
    if total_ap > 0:
        score -= 2

    # -------------------------------------------------
    # Keep score between 0 and 100
    # -------------------------------------------------
    score = max(0.0, min(100.0, score))

    return round(score, 1)

# ============================================================
# MAIN FINANCIAL HEALTH CALCULATION
# ============================================================

def calculate_financial_health(
    current_cash,
    total_ar,
    total_ap,
    tax_readiness,
    reconciliation_rate,
    mismatched_accounts,
    tax_mismatches,
    critical_actions,
    pending_payroll
):
    """
    Calculate complete financial health.

    All values are passed into this function, which means
    the controller does not need to know how each metric
    was calculated.
    """

    # --------------------------------------------------------
    # Integrity score
    # --------------------------------------------------------

    integrity_score = calculate_integrity_score(
        mismatched_accounts=mismatched_accounts,
        tax_mismatches=tax_mismatches,
        current_cash=current_cash,
        total_ar=total_ar,
        total_ap=total_ap,
        critical_actions=critical_actions
    )

    # --------------------------------------------------------
    # Financial status
    # --------------------------------------------------------

    integrity_status = get_financial_status(
        integrity_score
    )

    # --------------------------------------------------------
    # Month-end status
    # --------------------------------------------------------

    month_end_status = get_month_end_status(
        mismatched_accounts=mismatched_accounts,
        tax_mismatches=tax_mismatches,
        current_cash=current_cash,
        critical_actions=critical_actions,
        total_ar=total_ar,
        total_ap=total_ap,
        pending_payroll=pending_payroll
    )

    # --------------------------------------------------------
    # Return complete result
    # --------------------------------------------------------

    return FinancialHealth(

        integrity_score=integrity_score,

        integrity_status=integrity_status,

        current_cash=float(current_cash),

        total_ar=float(total_ar),

        total_ap=float(total_ap),

        tax_readiness=float(tax_readiness),

        reconciliation_rate=float(
            reconciliation_rate
        ),

        month_end_status=month_end_status
    )


# ============================================================
# SIMPLE DICTIONARY VERSION
# ============================================================

def financial_health_dict(
    current_cash,
    total_ar,
    total_ap,
    tax_readiness,
    reconciliation_rate,
    mismatched_accounts,
    tax_mismatches,
    critical_actions,
    pending_payroll
):
    """
    Return financial health as a normal dictionary.

    Useful for:
    - AI controller
    - CSV reports
    - JSON
    - APIs
    """

    result = calculate_financial_health(

        current_cash=current_cash,

        total_ar=total_ar,

        total_ap=total_ap,

        tax_readiness=tax_readiness,

        reconciliation_rate=reconciliation_rate,

        mismatched_accounts=mismatched_accounts,

        tax_mismatches=tax_mismatches,

        critical_actions=critical_actions,

        pending_payroll=pending_payroll
    )

    return {
        "integrity_score":
            result.integrity_score,

        "integrity_status":
            result.integrity_status,

        "current_cash":
            result.current_cash,

        "total_ar":
            result.total_ar,

        "total_ap":
            result.total_ap,

        "tax_readiness":
            result.tax_readiness,

        "reconciliation_rate":
            result.reconciliation_rate,

        "month_end_status":
            result.month_end_status
    }