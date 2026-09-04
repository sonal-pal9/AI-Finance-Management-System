"""
Smart Recommendation Engine
---------------------------
Generates and dynamically prioritizes financial actions.

Priority is based on:
1. Risk severity
2. Financial impact
3. Urgency
"""

from dataclasses import dataclass


@dataclass
class SmartRecommendation:
    priority: int
    severity: str
    title: str
    amount: float
    reason: str
    action: str
    priority_score: float
    count: int = 0

tax_mismatch_amount=0,
reconciliation_impact=0,

# ============================================================
# PRIORITY CALCULATION
# ============================================================
def calculate_priority_score(
    severity,
    amount=0,
    urgency=0
):
    """
    Calculate a dynamic priority score from 0 to 100.

    Score is based on:
    - Risk severity
    - Actual financial impact
    - Urgency
    """

    severity_scores = {
        "CRITICAL": 55,
        "HIGH": 40,
        "MEDIUM": 25,
        "LOW": 10
    }

    severity_score = severity_scores.get(
        severity.upper(),
        10
    )

    # Financial impact
    if amount <= 0:
        impact_score = 0
    elif amount >= 500000:
        impact_score = 35
    elif amount >= 250000:
        impact_score = 30
    elif amount >= 100000:
        impact_score = 25
    elif amount >= 50000:
        impact_score = 18
    elif amount >= 10000:
        impact_score = 10
    else:
        impact_score = 5

    # Urgency
    urgency_score = min(max(urgency, 0), 10)

    score = (
        severity_score
        + impact_score
        + urgency_score
    )

    return min(round(score, 1), 100.0)
# ============================================================
# GENERATE RECOMMENDATIONS
# ============================================================
def generate_recommendations(
    current_cash,
    total_ar,
    total_ap,
    pending_payroll,
    tax_mismatches,
    mismatched_accounts,
    critical_actions,
    tax_mismatch_amount=0,
    reconciliation_impact=0
):
    """
    Generate dynamically prioritized financial recommendations.
    """

    recommendations = []

    # ========================================================
    # 1. NEGATIVE CASH
    # ========================================================

    if current_cash < 0:

        amount = abs(current_cash)

        score = calculate_priority_score(
            severity="CRITICAL",
            amount=amount,
            urgency=10
        )

        recommendations.append(
            SmartRecommendation(
                priority=0,
                severity="CRITICAL",
                title="Resolve cash deficit",
                amount=amount,
                reason=(
                    f"Current cash position is negative by "
                    f"₹{amount:,.2f}."
                ),
                action=(
                    "Immediately improve liquidity through "
                    "collections, payment scheduling, or "
                    "additional funding."
                ),
                priority_score=score
            )
        )

    # ========================================================
    # 2. CRITICAL LIQUIDITY ACTIONS
    # ========================================================

    if critical_actions > 0:

        score = calculate_priority_score(
            severity="CRITICAL",
            amount=0,
            urgency=9
        )

        recommendations.append(
            SmartRecommendation(
                priority=0,
                severity="CRITICAL",
                title="Execute critical liquidity actions",
                amount=0,
                count=critical_actions,
                reason=(
                    f"{critical_actions} critical liquidity "
                    "action(s) are currently pending."
                ),
                action=(
                    "Review and execute the highest-impact "
                    "liquidity actions immediately."
                ),
                priority_score=score
            )
        )

    # ========================================================
    # 3. RECEIVABLES
    # ========================================================

    if total_ar > 0:

        score = calculate_priority_score(
            severity="HIGH",
            amount=total_ar,
            urgency=7
        )

        recommendations.append(
            SmartRecommendation(
                priority=0,
                severity="HIGH",
                title="Accelerate receivable collection",
                amount=total_ar,
                reason=(
                    f"₹{total_ar:,.2f} is currently outstanding "
                    "from customers."
                ),
                action=(
                    "Prioritize overdue customer collections "
                    "to increase available cash."
                ),
                priority_score=score
            )
        )

    # ========================================================
    # 4. PAYABLES
    # ========================================================

    if total_ap > 0:

        score = calculate_priority_score(
            severity="HIGH",
            amount=total_ap,
            urgency=6
        )

        recommendations.append(
            SmartRecommendation(
                priority=0,
                severity="HIGH",
                title="Review supplier payment obligations",
                amount=total_ap,
                reason=(
                    f"₹{total_ap:,.2f} is outstanding in "
                    "supplier payables."
                ),
                action=(
                    "Review due dates and prioritize payments "
                    "while protecting liquidity."
                ),
                priority_score=score
            )
        )

    # ========================================================
    # 5. TAX
    # ========================================================

    if tax_mismatches > 0:

        score = calculate_priority_score(
            severity="HIGH",
            amount=tax_mismatch_amount,
            urgency=8
        )

        recommendations.append(
            SmartRecommendation(
                priority=0,
                severity="HIGH",
                title="Resolve tax mismatches",
                amount=tax_mismatch_amount,
                count=tax_mismatches,
                reason=(
                    f"{tax_mismatches} tax mismatch(es) were "
                    "detected between financial records and "
                    "reported values."
                ),
                action=(
                    "Verify the affected tax records and correct "
                    "discrepancies before filing or reconciliation."
                ),
                priority_score=score
            )
        )

    # ========================================================
    # 6. RECONCILIATION
    # ========================================================

    if mismatched_accounts > 0:

        score = calculate_priority_score(
            severity="HIGH",
            amount=reconciliation_impact,
            urgency=5
        )

        recommendations.append(
            SmartRecommendation(
                priority=0,
                severity="HIGH",
                title="Resolve reconciliation exceptions",
                amount=reconciliation_impact,
                count=mismatched_accounts,
                reason=(
                    f"{mismatched_accounts} reconciliation "
                    "exception(s) were detected."
                ),
                action=(
                    "Investigate unmatched transactions and "
                    "reconcile the affected accounts."
                ),
                priority_score=score
            )
        )

    # ========================================================
    # 7. PAYROLL
    # ========================================================

    if pending_payroll > 0:

        score = calculate_priority_score(
            severity="MEDIUM",
            amount=pending_payroll,
            urgency=8
        )

        recommendations.append(
            SmartRecommendation(
                priority=0,
                severity="MEDIUM",
                title="Process pending payroll",
                amount=pending_payroll,
                reason=(
                    f"₹{pending_payroll:,.2f} of payroll is "
                    "still pending."
                ),
                action=(
                    "Ensure sufficient funds are available and "
                    "complete pending payroll payments."
                ),
                priority_score=score
            )
        )

    # ========================================================
    # DYNAMIC SORTING
    # ========================================================

    recommendations.sort(
        key=lambda x: x.priority_score,
        reverse=True
    )

    # ========================================================
    # ASSIGN FINAL PRIORITY NUMBERS
    # ========================================================

    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):
        recommendation.priority = index

    return recommendations


# ============================================================
# DISPLAY RECOMMENDATIONS
# ============================================================

def print_recommendations(recommendations):

    print()
    print("=" * 65)
    print("SMART MANAGEMENT PRIORITIES")
    print("=" * 65)

    if not recommendations:

        print()
        print("No significant financial actions detected.")
        print("Financial position appears stable.")

        return

    for recommendation in recommendations:

        print()
        print(
            f"{recommendation.priority}. "
            f"{recommendation.severity} — "
            f"{recommendation.title}"
        )

        print(
            f"   Priority Score : "
            f"{recommendation.priority_score}/100"
        )

        # ----------------------------------------------------
        # Display financial amounts
        # ----------------------------------------------------
        
        if recommendation.title in [
            "Resolve cash deficit",
            "Accelerate receivable collection",
            "Review supplier payment obligations",
            "Process pending payroll"
        ]:

            print(
                f"   Amount         : "
                f"₹{recommendation.amount:,.2f}"
            )

        elif recommendation.title == (
            "Execute critical liquidity actions"
        ):

            print(
                f"   Actions        : "
                f"{recommendation.count}"
            )

        elif recommendation.title == (
            "Resolve tax mismatches"
        ):

            print(
                f"   Mismatches     : "
                f"{recommendation.count}"
            )

        elif recommendation.title == (
            "Resolve reconciliation exceptions"
        ):

            print(
                f"   Exceptions     : "
                f"{recommendation.count}"
            )
# ============================================================
# TOP RECOMMENDATION
# ============================================================

def get_top_recommendation(recommendations):

    if not recommendations:
        return None

    return recommendations[0]


# ============================================================
# SUMMARY
# ============================================================

def recommendation_summary(recommendations):

    if not recommendations:

        return {
            "total_recommendations": 0,
            "highest_severity": "NONE",
            "top_action": None,
            "top_priority_score": 0
        }

    return {
        "total_recommendations": len(
            recommendations
        ),
        "highest_severity": (
            recommendations[0].severity
        ),
        "top_action": (
            recommendations[0].title
        ),
        "top_priority_score": (
            recommendations[0].priority_score
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    recommendations = generate_recommendations(

        current_cash=-382005,

        total_ar=129549,

        total_ap=81500,

        pending_payroll=95400,

        tax_mismatches=2,

        mismatched_accounts=7,

        critical_actions=1
    )

    print_recommendations(
        recommendations
    )

    print()
    print("=" * 65)
    print("TOP PRIORITY")
    print("=" * 65)

    top = get_top_recommendation(
        recommendations
    )

    if top:

        print(
            f"{top.severity}: "
            f"{top.title}"
        )

        print(
            f"Priority Score: "
            f"{top.priority_score}/100"
        )

        print(top.reason)
        print(top.action)