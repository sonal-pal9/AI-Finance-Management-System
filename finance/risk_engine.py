# ============================================================
# RISK ENGINE
# Nourish Cafe - AI Finance Controller
# ============================================================

from dataclasses import dataclass


# ============================================================
# RISK OBJECT
# ============================================================

@dataclass
class Risk:

    level: str

    message: str

    priority: int


# ============================================================
# RISK ENGINE
# ============================================================

class RiskEngine:

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

    def negative_cash_risk(self):

        if self.current_cash < 0:

            return Risk(
                level="CRITICAL",
                message=(
                    f"Negative cash position of "
                    f"₹{abs(self.current_cash):,.2f}"
                ),
                priority=1
            )

        return None


    # ========================================================
    # LIQUIDITY
    # ========================================================

    def liquidity_risk(self):

        if self.critical_actions > 0:

            return Risk(
                level="CRITICAL",
                message=(
                    f"{self.critical_actions} "
                    f"critical liquidity action(s)"
                ),
                priority=2
            )

        return None


    # ========================================================
    # ACCOUNTS RECEIVABLE
    # ========================================================

    def receivable_risk(self):

        if self.total_ar > 0:

            return Risk(
                level="HIGH",
                message=(
                    f"₹{self.total_ar:,.2f} "
                    f"outstanding receivables"
                ),
                priority=3
            )

        return None


    # ========================================================
    # ACCOUNTS PAYABLE
    # ========================================================

    def payable_risk(self):

        if self.total_ap > 0:

            return Risk(
                level="HIGH",
                message=(
                    f"₹{self.total_ap:,.2f} "
                    f"outstanding payables"
                ),
                priority=4
            )

        return None


    # ========================================================
    # TAX
    # ========================================================

    def tax_risk(self):

        if self.tax_mismatches > 0:

            return Risk(
                level="HIGH",
                message=(
                    f"{self.tax_mismatches} "
                    f"tax mismatch(es)"
                ),
                priority=5
            )

        return None


    # ========================================================
    # RECONCILIATION
    # ========================================================

    def reconciliation_risk(self):

        if self.mismatched_accounts > 0:

            return Risk(
                level="HIGH",
                message=(
                    f"{self.mismatched_accounts} "
                    f"reconciliation exception(s)"
                ),
                priority=6
            )

        return None


    # ========================================================
    # PAYROLL
    # ========================================================

    def payroll_risk(self):

        if self.pending_payroll > 0:

            return Risk(
                level="MEDIUM",
                message=(
                    f"₹{self.pending_payroll:,.2f} "
                    f"pending payroll"
                ),
                priority=7
            )

        return None


    # ========================================================
    # GET ALL RISKS
    # ========================================================

    def get_risks(self):

        risks = []

        risk_functions = [

            self.negative_cash_risk,

            self.liquidity_risk,

            self.receivable_risk,

            self.payable_risk,

            self.tax_risk,

            self.reconciliation_risk,

            self.payroll_risk

        ]

        for function in risk_functions:

            risk = function()

            if risk is not None:

                risks.append(risk)

        # ----------------------------------------------------
        # Sort by priority
        # ----------------------------------------------------

        risks.sort(
            key=lambda x: x.priority
        )

        return risks


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def get_risks(
    current_cash,
    total_ar,
    total_ap,
    tax_mismatches,
    mismatched_accounts,
    critical_actions,
    pending_payroll
):

    engine = RiskEngine(

        current_cash=current_cash,

        total_ar=total_ar,

        total_ap=total_ap,

        tax_mismatches=tax_mismatches,

        mismatched_accounts=mismatched_accounts,

        critical_actions=critical_actions,

        pending_payroll=pending_payroll
    )

    return engine.get_risks()


# ============================================================
# PRINT RISKS
# ============================================================

def print_risks(risks):

    if not risks:

        print()
        print("No major financial risks detected.")
        return

    for risk in risks:

        print(
            f"- {risk.level}: "
            f"{risk.message}"
        )


# ============================================================
# GET HIGHEST PRIORITY RISK
# ============================================================

def get_highest_priority_risk(risks):

    if not risks:

        return None

    return min(
        risks,
        key=lambda x: x.priority
    )


# ============================================================
# RISK SUMMARY
# ============================================================

def risk_summary(risks):

    critical = 0
    high = 0
    medium = 0
    low = 0

    for risk in risks:

        if risk.level == "CRITICAL":
            critical += 1

        elif risk.level == "HIGH":
            high += 1

        elif risk.level == "MEDIUM":
            medium += 1

        elif risk.level == "LOW":
            low += 1

    return {

        "total": len(risks),

        "critical": critical,

        "high": high,

        "medium": medium,

        "low": low

    }