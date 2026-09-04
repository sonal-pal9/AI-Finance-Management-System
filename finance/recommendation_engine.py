# ============================================================
# RECOMMENDATION ENGINE
# Nourish Cafe - AI Finance Controller
# ============================================================


# ============================================================
# RECOMMENDATION OBJECT
# ============================================================

class Recommendation:

    def __init__(
        self,
        priority,
        title,
        reason,
        action,
        risk_level
    ):

        self.priority = priority
        self.title = title
        self.reason = reason
        self.action = action
        self.risk_level = risk_level


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

class RecommendationEngine:

    def __init__(
        self,
        current_cash,
        total_ar,
        total_ap,
        tax_mismatches,
        mismatched_accounts,
        critical_actions,
        pending_payroll
    ):

        self.current_cash = float(current_cash)

        self.total_ar = float(total_ar)

        self.total_ap = float(total_ap)

        self.tax_mismatches = int(
            tax_mismatches
        )

        self.mismatched_accounts = int(
            mismatched_accounts
        )

        self.critical_actions = int(
            critical_actions
        )

        self.pending_payroll = float(
            pending_payroll
        )


    # ========================================================
    # NEGATIVE CASH
    # ========================================================

    def cash_recommendation(self):

        if self.current_cash < 0:

            return Recommendation(

                priority=1,

                title="Resolve negative cash position",

                reason=(
                    f"Current cash is "
                    f"₹{abs(self.current_cash):,.2f} "
                    f"below zero."
                ),

                action=(
                    "Review bank transactions, "
                    "expected collections, upcoming "
                    "payments and immediate funding "
                    "requirements."
                ),

                risk_level="CRITICAL"
            )

        return None


    # ========================================================
    # LIQUIDITY
    # ========================================================

    def liquidity_recommendation(self):

        if self.critical_actions > 0:

            return Recommendation(

                priority=2,

                title="Execute critical liquidity actions",

                reason=(
                    f"{self.critical_actions} "
                    f"critical liquidity action(s) "
                    f"require attention."
                ),

                action=(
                    "Review and execute the highest "
                    "priority liquidity actions to "
                    "protect near-term cash availability."
                ),

                risk_level="CRITICAL"
            )

        return None


    # ========================================================
    # ACCOUNTS RECEIVABLE
    # ========================================================

    def receivable_recommendation(self):

        if self.total_ar > 0:

            return Recommendation(

                priority=3,

                title="Collect outstanding receivables",

                reason=(
                    f"₹{self.total_ar:,.2f} "
                    f"remains outstanding from customers."
                ),

                action=(
                    "Prioritize collection of overdue "
                    "customer balances and follow up "
                    "on unpaid invoices."
                ),

                risk_level="HIGH"
            )

        return None


    # ========================================================
    # ACCOUNTS PAYABLE
    # ========================================================

    def payable_recommendation(self):

        if self.total_ap > 0:

            return Recommendation(

                priority=4,

                title="Review outstanding supplier payments",

                reason=(
                    f"₹{self.total_ap:,.2f} "
                    f"remains payable to suppliers."
                ),

                action=(
                    "Review supplier due dates, verify "
                    "invoice validity and prioritize "
                    "payments according to cash availability."
                ),

                risk_level="HIGH"
            )

        return None


    # ========================================================
    # TAX
    # ========================================================

    def tax_recommendation(self):

        if self.tax_mismatches > 0:

            return Recommendation(

                priority=5,

                title="Resolve tax mismatches",

                reason=(
                    f"{self.tax_mismatches} "
                    f"tax mismatch(es) were detected."
                ),

                action=(
                    "Reconcile tax records with the "
                    "Tally GST Payable ledger and verify "
                    "tax liability before filing."
                ),

                risk_level="HIGH"
            )

        return None


    # ========================================================
    # RECONCILIATION
    # ========================================================

    def reconciliation_recommendation(self):

        if self.mismatched_accounts > 0:

            return Recommendation(

                priority=6,

                title="Resolve reconciliation exceptions",

                reason=(
                    f"{self.mismatched_accounts} "
                    f"account-level reconciliation "
                    f"exception(s) require review."
                ),

                action=(
                    "Review the underlying transactions "
                    "and reconcile operational records "
                    "against the Tally ledger."
                ),

                risk_level="HIGH"
            )

        return None


    # ========================================================
    # PAYROLL
    # ========================================================

    def payroll_recommendation(self):

        if self.pending_payroll > 0:

            return Recommendation(

                priority=7,

                title="Review pending payroll",

                reason=(
                    f"₹{self.pending_payroll:,.2f} "
                    f"of payroll remains pending."
                ),

                action=(
                    "Review pending employee payments "
                    "and ensure sufficient cash is "
                    "available before the payroll due date."
                ),

                risk_level="MEDIUM"
            )

        return None


    # ========================================================
    # GENERATE ALL RECOMMENDATIONS
    # ========================================================

    def get_recommendations(self):

        recommendations = []

        functions = [

            self.cash_recommendation,

            self.liquidity_recommendation,

            self.receivable_recommendation,

            self.payable_recommendation,

            self.tax_recommendation,

            self.reconciliation_recommendation,

            self.payroll_recommendation

        ]

        for function in functions:

            recommendation = function()

            if recommendation is not None:

                recommendations.append(
                    recommendation
                )

        # ----------------------------------------------------
        # Ensure priority order
        # ----------------------------------------------------

        recommendations.sort(
            key=lambda x: x.priority
        )

        return recommendations


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def get_recommendations(
    current_cash,
    total_ar,
    total_ap,
    tax_mismatches,
    mismatched_accounts,
    critical_actions,
    pending_payroll
):

    engine = RecommendationEngine(

        current_cash=current_cash,

        total_ar=total_ar,

        total_ap=total_ap,

        tax_mismatches=tax_mismatches,

        mismatched_accounts=mismatched_accounts,

        critical_actions=critical_actions,

        pending_payroll=pending_payroll
    )

    return engine.get_recommendations()


# ============================================================
# PRINT RECOMMENDATIONS
# ============================================================

def print_recommendations(
    recommendations
):

    if not recommendations:

        print()
        print(
            "No immediate management actions required."
        )

        return


    for recommendation in recommendations:

        print()
        print(
            f"{recommendation.priority}. "
            f"{recommendation.title}"
        )

        print(
            f"   Risk Level : "
            f"{recommendation.risk_level}"
        )

        print(
            f"   Reason     : "
            f"{recommendation.reason}"
        )

        print(
            f"   Action     : "
            f"{recommendation.action}"
        )


# ============================================================
# TOP PRIORITY
# ============================================================

def get_top_recommendation(
    recommendations
):

    if not recommendations:

        return None

    return min(
        recommendations,
        key=lambda x: x.priority
    )


# ============================================================
# RECOMMENDATION SUMMARY
# ============================================================

def recommendation_summary(
    recommendations
):

    return {

        "total":
            len(recommendations),

        "critical":
            sum(
                1
                for r in recommendations
                if r.risk_level == "CRITICAL"
            ),

        "high":
            sum(
                1
                for r in recommendations
                if r.risk_level == "HIGH"
            ),

        "medium":
            sum(
                1
                for r in recommendations
                if r.risk_level == "MEDIUM"
            ),

        "low":
            sum(
                1
                for r in recommendations
                if r.risk_level == "LOW"
            )
    }
