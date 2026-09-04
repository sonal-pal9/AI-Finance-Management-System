# ============================================================
# NOURISH CAFE - AI FINANCE CONTROLLER
# MASTER CONTROLLER
# ============================================================

import os
import sys
import re
import io
import contextlib
import runpy


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ============================================================
# IMPORT DATA LOADER
# ============================================================

from finance.data_loader import load_all_data


# ============================================================
# IMPORT FINANCIAL HEALTH ENGINE
# ============================================================

from finance.financial_health import (
    calculate_financial_health
)


# ============================================================
# IMPORT RISK ENGINE
# ============================================================

from finance.risk_engine import (
    get_risks,
    get_highest_priority_risk
)


# ============================================================
# IMPORT RECOMMENDATION ENGINE
# ============================================================

from finance.recommendation_engine import (
    get_recommendations
)


# ============================================================
# IMPORT EXPLANATION ENGINE
# ============================================================

from finance.explanation_engine import (
    explain_cash,
    explain_tax,
    explain_reconciliation,
    explain_receivables,
    explain_payables,
    explain_month_end,
    explain_overall_risk,
    explain_top_recommendation
)
from finance.query_engine import parse_question
from finance.financial_query_engine import (
    answer_financial_question,
    analyze_tax,
    tax_analysis as financial_tax_analysis
)
from finance.smart_recommendation_engine import (
    generate_recommendations,
    print_recommendations
)

# ============================================================
# GLOBAL DATA
# ============================================================

data = {}


# ============================================================
# FINANCIAL METRICS
# ============================================================

current_cash = 0.0

total_ar = 0.0

total_ap = 0.0

tax_readiness = 100.0

reconciliation_rate = 100.0


# ============================================================
# RISK METRICS
# ============================================================

mismatched_accounts = 0

tax_mismatches = 0

critical_actions = 0

pending_payroll = 0.0


# ============================================================
# ENGINE RESULTS
# ============================================================

financial_health = None

risks = []

recommendations = []


# ============================================================
# UTILITY - LINE
# ============================================================

def line():

    print("=" * 70)


# ============================================================
# UTILITY - MONEY FORMAT
# ============================================================

def money(value):

    return f"₹{float(value):,.2f}"


# ============================================================
# RUN EXISTING MODULE
# ============================================================

def run_module(filename):

    """
    Execute one of the existing finance modules.

    The old modules were originally written as standalone
    scripts. We execute them here and capture their variables
    without displaying their large reports.
    """

    path = os.path.join(
        BASE_DIR,
        filename
    )

    if not os.path.exists(path):

        print(
            f"WARNING: {filename} not found."
        )

        return {}


    namespace = {}

    old_dir = os.getcwd()


    try:

        os.chdir(BASE_DIR)

        with contextlib.redirect_stdout(
            io.StringIO()
        ):

            namespace = runpy.run_path(
                path,
                run_name="finance_module"
            )


    except SystemExit:

        pass


    except Exception as e:

        print(
            f"WARNING: Could not run "
            f"{filename}: {e}"
        )


    finally:

        os.chdir(old_dir)


    return namespace


# ============================================================
# LOAD FINANCIAL DATA
# ============================================================

def load_data():

    global data


    try:

        data = load_all_data()

        return True


    except Exception as e:

        print(
            f"ERROR loading financial data: {e}"
        )

        return False


# ============================================================
# RUN ALL FINANCIAL ENGINES
# ============================================================

def run_finance_modules():

    global current_cash
    global total_ar
    global total_ap
    global tax_readiness
    global reconciliation_rate
    global mismatched_accounts
    global tax_mismatches
    global critical_actions
    global pending_payroll


    # ========================================================
    # ACCOUNTS RECEIVABLE
    # ========================================================

    ar = run_module(
        "accounts_receivable.py"
    )


    if "total_ar" in ar:

        try:

            total_ar = float(
                ar["total_ar"]
            )

        except Exception:

            total_ar = 0.0


    # ========================================================
    # ACCOUNTS PAYABLE
    # ========================================================

    ap = run_module(
        "accounts_payable.py"
    )


    if "total_payable" in ap:

        try:

            total_ap = float(
                ap["total_payable"]
            )

        except Exception:

            total_ap = 0.0


    # ========================================================
    # CASH POSITION
    # ========================================================

    cash = run_module(
        "cash_position.py"
    )


    if "current_cash" in cash:

        try:

            current_cash = float(
                cash["current_cash"]
            )

        except Exception:

            current_cash = 0.0


    if "pending_payroll_amount" in cash:

        try:

            pending_payroll = float(
                cash["pending_payroll_amount"]
            )

        except Exception:

            pending_payroll = 0.0


    # ========================================================
    # LIQUIDITY ACTIONS
    # ========================================================

    liquidity = run_module(
        "liquidity_action_engine.py"
    )


    if "actions_df" in liquidity:

        actions_df = liquidity[
            "actions_df"
        ]


        if (
            actions_df is not None
            and not actions_df.empty
            and "priority" in actions_df.columns
        ):

            try:

                critical_actions = int(
                    (
                        actions_df[
                            "priority"
                        ]
                        .astype(str)
                        .str.upper()
                        == "CRITICAL"
                    ).sum()
                )

            except Exception:

                critical_actions = 0


    # ========================================================
    # RECONCILIATION
    # ========================================================

    reconciliation = run_module(
        "reconciliation.py"
    )


    if "final_result" in reconciliation:

        result = reconciliation[
            "final_result"
        ]


        if result is not None and len(result) > 0:

            try:

                matched = int(
                    (
                        result[
                            "status"
                        ]
                        .astype(str)
                        .str.upper()
                        == "MATCHED"
                    ).sum()
                )


                total_records = len(
                    result
                )


                mismatched_accounts = (
                    total_records - matched
                )


                if total_records > 0:

                    reconciliation_rate = (
                        matched
                        / total_records
                        * 100
                    )

                else:

                    reconciliation_rate = 100.0


            except Exception:

                matched = 0

                mismatched_accounts = 0

                reconciliation_rate = 100.0


    # ========================================================
    # TAX VERIFICATION
    # ========================================================

    tax = run_module(
        "tax_verification.py"
    )


    if "mismatch_count" in tax:

        try:

            tax_mismatches = int(
                tax["mismatch_count"]
            )

        except Exception:

            tax_mismatches = 0


    if "tax_score" in tax:

        tax_result = analyze_tax(data)

        tax_readiness = tax_result["tax_readiness"]


# ============================================================
# FINANCIAL HEALTH
# ============================================================
def calculate_health():

    global financial_health

    financial_health = calculate_financial_health(

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

    return financial_health
# ============================================================
# RISK CALCULATION
# ============================================================

def calculate_risks():

    global risks


    risks = get_risks(

        current_cash=current_cash,

        total_ar=total_ar,

        total_ap=total_ap,

        tax_mismatches=tax_mismatches,

        mismatched_accounts=mismatched_accounts,

        critical_actions=critical_actions,

        pending_payroll=pending_payroll
    )


    return risks


# ============================================================
# RECOMMENDATION CALCULATION
# ============================================================

def calculate_recommendations():

    global recommendations


    recommendations = get_recommendations(

        current_cash=current_cash,

        total_ar=total_ar,

        total_ap=total_ap,

        tax_mismatches=tax_mismatches,

        mismatched_accounts=mismatched_accounts,

        critical_actions=critical_actions,

        pending_payroll=pending_payroll
    )


    return recommendations


# ============================================================
# HEADER
# ============================================================

def header():

    print()

    line()

    print(
        "                 NOURISH CAFE"
    )

    print(
        "             AI FINANCE CONTROLLER"
    )

    line()


# ============================================================
# SUMMARY ANALYSIS
# ============================================================

def summary_analysis():

    health = financial_health


    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        "FINANCIAL SUMMARY"
    )

    print(
        "-" * 40
    )


    print(
        f"Financial Integrity : "
        f"{health.integrity_score:.1f}/100"
    )


    print(
        f"Financial Status    : "
        f"{health.integrity_status}"
    )


    print(
        f"Current Cash        : "
        f"{money(health.current_cash)}"
    )


    print(
        f"Accounts Receivable : "
        f"{money(health.total_ar)}"
    )


    print(
        f"Accounts Payable    : "
        f"{money(health.total_ap)}"
    )


    print(
        f"Tax Readiness       : "
        f"{health.tax_readiness:.1f}/100"
    )


    print(
        f"Reconciliation Rate : "
        f"{health.reconciliation_rate:.1f}%"
    )


    print(
        f"Month-End Status    : "
        f"{health.month_end_status}"
    )


# ============================================================
# BIGGEST RISK
# ============================================================

def biggest_risk():

    health = financial_health


    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        "OVERALL FINANCIAL RISK ANALYSIS"
    )

    print(
        "-" * 40
    )


    print(
        f"Financial Integrity : "
        f"{health.integrity_score:.1f}/100"
    )


    print(
        f"Financial Status    : "
        f"{health.integrity_status}"
    )


    print(
        f"Month-End Status    : "
        f"{health.month_end_status}"
    )


    print()

    print(
        "Major Risks:"
    )


    if not risks:

        print(
            "- No major financial risks detected."
        )

    else:

        for risk in risks:

            print(
                f"- {risk.level}: "
                f"{risk.message}"
            )


    print()

    print(
        "Recommended Priority:"
    )


    highest = get_highest_priority_risk(
        risks
    )


    if highest is not None:

        print(
            f"1. {highest.message}"
        )

    else:

        print(
            "1. Review overall financial controls."
        )


# ============================================================
# CASH ANALYSIS
# ============================================================

def cash_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        "CASH & LIQUIDITY ANALYSIS"
    )

    print(
        "-" * 40
    )


    print(
        f"Current Cash : "
        f"{money(current_cash)}"
    )


    if current_cash < 0:

        print()

        print(
            "Risk : CRITICAL"
        )


        print(
            f"Negative cash position of "
            f"{money(abs(current_cash))}"
        )


        print()

        print(
            "Recommendation:"
        )


        print(
            "Prioritize collections and "
            "review immediate supplier "
            "payment timing."
        )


    elif critical_actions > 0:

        print()

        print(
            "Risk : HIGH"
        )


        print(
            f"{critical_actions} critical "
            f"liquidity action(s) detected."
        )


        print()

        print(
            "Recommendation:"
        )


        print(
            "Resolve critical liquidity "
            "actions before non-essential spending."
        )


    else:

        print()

        print(
            "Risk : LOW"
        )


        print(
            "Current cash position does not "
            "show a critical liquidity issue."
        )


# ============================================================
# RECEIVABLE ANALYSIS
# ============================================================

def receivables_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        "ACCOUNTS RECEIVABLE ANALYSIS"
    )

    print(
        "-" * 40
    )


    print(
        f"Outstanding Receivables : "
        f"{money(total_ar)}"
    )


    if total_ar > 0:

        print()

        print(
            "Risk : HIGH"
        )


        print(
            "Customer collections should "
            "be prioritized."
        )


        print()

        print(
            "Recommendation:"
        )


        print(
            "Follow up on overdue invoices "
            "and accelerate high-value collections."
        )


    else:

        print()

        print(
            "Risk : LOW"
        )


        print(
            "No outstanding customer "
            "receivables detected."
        )


# ============================================================
# PAYABLE ANALYSIS
# ============================================================

def payable_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        "ACCOUNTS PAYABLE ANALYSIS"
    )

    print(
        "-" * 40
    )


    print(
        f"Outstanding Payables : "
        f"{money(total_ap)}"
    )


    if total_ap > 0:

        print()

        print(
            "Risk : HIGH"
        )


        print(
            "Supplier obligations remain "
            "outstanding."
        )


        print()

        print(
            "Recommendation:"
        )


        print(
            "Review due dates and schedule "
            "supplier payments according to "
            "cash availability."
        )


    else:

        print()

        print(
            "Risk : LOW"
        )


        print(
            "No outstanding supplier "
            "payables detected."
        )


# ============================================================
# TAX ANALYSIS
# ============================================================

def tax_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        "TAX & COMPLIANCE ANALYSIS"
    )

    print(
        "-" * 40
    )


    print(
        f"Tax mismatches : "
        f"{tax_mismatches}"
    )


    print(
        f"Tax readiness  : "
        f"{tax_readiness:.1f}/100"
    )


    if tax_mismatches > 0:

        print()

        print(
            "Risk : TAX MISMATCHES DETECTED"
        )


        print()

        print(
            "Recommendation:"
        )


        print(
            "Reconcile tax records against "
            "the Tally GST payable ledger."
        )


    elif tax_readiness < 90:

        print()

        print(
            "Risk : REVIEW REQUIRED"
        )


        print()

        print(
            "Recommendation:"
        )


        print(
            "Review tax filing records and "
            "historical compliance issues."
        )


    else:

        print()

        print(
            "Risk : LOW"
        )


        print(
            "Tax records currently appear "
            "ready for routine review."
        )


# ============================================================
# RECONCILIATION ANALYSIS
# ============================================================

def reconciliation_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        "TALLY / BANK RECONCILIATION"
    )

    print(
        "-" * 40
    )


    reconciliation = run_module(
        "reconciliation.py"
    )


    if "final_result" not in reconciliation:

        print(
            "Reconciliation result unavailable."
        )

        return


    result = reconciliation[
        "final_result"
    ]


    if result is None:

        print(
            "Reconciliation result unavailable."
        )

        return


    total_records = len(result)


    if total_records == 0:

        print(
            "No reconciliation records found."
        )

        return


    try:

        matched = int(
            (
                result[
                    "status"
                ]
                .astype(str)
                .str.upper()
                == "MATCHED"
            ).sum()
        )

    except Exception:

        matched = 0


    mismatched = (
        total_records - matched
    )


    rate = (
        matched
        / total_records
        * 100
    )


    print(
        f"Accounts checked    : "
        f"{total_records}"
    )


    print(
        f"Matched             : "
        f"{matched}"
    )


    print(
        f"Mismatched          : "
        f"{mismatched}"
    )


    print(
        f"Reconciliation rate : "
        f"{rate:.1f}%"
    )


    if mismatched > 0:

        print()

        print(
            "Risk : HIGH"
        )


        print(
            f"{mismatched} reconciliation "
            f"exception(s) require review."
        )


        print()

        print(
            "Recommendation:"
        )


        print(
            "Review unmatched payments, "
            "bank references and ledger entries."
        )


    else:

        print()

        print(
            "Risk : LOW"
        )


        print(
            "All reconciliation records matched."
        )


# ============================================================
# PAYROLL ANALYSIS
# ============================================================

def payroll_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        "PAYROLL ANALYSIS"
    )

    print(
        "-" * 40
    )


    print(
        f"Pending Payroll : "
        f"{money(pending_payroll)}"
    )


    if pending_payroll > 0:

        print()

        print(
            "Risk : MEDIUM"
        )


        print()

        print(
            "Recommendation:"
        )


        print(
            "Reserve sufficient cash for "
            "employee payroll before "
            "non-critical payments."
        )


    else:

        print()

        print(
            "Risk : LOW"
        )


        print(
            "No pending payroll detected."
        )


# ============================================================
# MANAGEMENT ACTIONS
# ============================================================
def management_actions():

    recommendations = generate_recommendations(
        current_cash=current_cash,
        total_ar=total_ar,
        total_ap=total_ap,
        pending_payroll=pending_payroll,
        tax_mismatches=tax_mismatches,
        mismatched_accounts=mismatched_accounts,
        critical_actions=critical_actions
    )

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()

    print()

    print_recommendations(recommendations)
# ============================================================
# EXPLANATION - CASH
# ============================================================

def explain_cash_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        explain_cash(
            current_cash=current_cash,
            total_ar=total_ar,
            total_ap=total_ap
        )
    )


# ============================================================
# EXPLANATION - TAX
# ============================================================

def explain_tax_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        explain_tax(
            tax_mismatches=tax_mismatches,
            tax_readiness=tax_readiness
        )
    )


# ============================================================
# EXPLANATION - RECONCILIATION
# ============================================================

def explain_reconciliation_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        explain_reconciliation(
            mismatched_accounts=mismatched_accounts,
            reconciliation_rate=reconciliation_rate
        )
    )


# ============================================================
# EXPLANATION - RECEIVABLES
# ============================================================

def explain_receivables_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        explain_receivables(
            total_ar=total_ar
        )
    )


# ============================================================
# EXPLANATION - PAYABLES
# ============================================================

def explain_payables_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        explain_payables(
            total_ap=total_ap
        )
    )


# ============================================================
# EXPLANATION - MONTH END
# ============================================================

def explain_month_end_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        explain_month_end(
            month_end_status=(
                financial_health.month_end_status
            ),

            current_cash=current_cash,

            mismatched_accounts=(
                mismatched_accounts
            ),

            tax_mismatches=(
                tax_mismatches
            )
        )
    )


# ============================================================
# EXPLANATION - OVERALL RISK
# ============================================================

def explain_overall_risk_analysis():

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()


    print()

    print(
        explain_overall_risk(

            integrity_score=(
                financial_health.integrity_score
            ),

            integrity_status=(
                financial_health.integrity_status
            ),

            current_cash=current_cash,

            total_ar=total_ar,

            total_ap=total_ap,

            tax_mismatches=tax_mismatches,

            mismatched_accounts=(
                mismatched_accounts
            ),

            critical_actions=(
                critical_actions
            ),

            pending_payroll=(
                pending_payroll
            )
        )
    )

#smart
def smart_management_actions():
    """
    Generate and display smart financial recommendations
    using the current financial data.
    """

    recommendations = generate_recommendations(
        current_cash=current_cash,
        total_ar=total_ar,
        total_ap=total_ap,
        pending_payroll=pending_payroll,
        tax_mismatches=tax_mismatches,
        mismatched_accounts=mismatched_accounts,
        critical_actions=critical_actions
    )

    print_recommendations(recommendations)

def explain_top_priority_analysis():

    recommendations = generate_recommendations(
        current_cash=current_cash,
        total_ar=total_ar,
        total_ap=total_ap,
        pending_payroll=pending_payroll,
        tax_mismatches=tax_mismatches,
        mismatched_accounts=mismatched_accounts,
        critical_actions=critical_actions
    )

    print()

    line()

    print(
        "AI FINANCE CONTROLLER RESPONSE"
    )

    line()

    print()

    if not recommendations:

        print(
            "No financial recommendation is currently available."
        )

        return

    top_recommendation = recommendations[0]

    print(
        explain_top_recommendation(
            recommendation=top_recommendation,
            current_cash=current_cash,
            total_ar=total_ar,
            total_ap=total_ap,
            pending_payroll=pending_payroll,
            critical_actions=critical_actions
        )
    )
#ques-ans
def answer_question(question):

    query = parse_question(question)

    if query.query_type == "exit":
        return False

    elif query.query_type == "risk":

        explain_overall_risk_analysis()

    elif query.query_type == "cash":

        cash_analysis()

    elif query.query_type == "receivables":

        receivables_analysis()

    elif query.query_type == "payables":

        payable_analysis()

    elif query.query_type == "tax":

        financial_tax_analysis(data)

    elif query.query_type == "reconciliation":

        reconciliation_analysis()

    elif query.query_type == "payroll":

        payroll_analysis()

    elif query.query_type == "summary":

        summary_analysis()

    elif query.query_type == "actions":

        management_actions()

    else:

        print()

        line()

        print(
            "AI FINANCE CONTROLLER RESPONSE"
        )

        line()

        print()

        print(
            "I could not identify the financial area."
        )

        print()

        print(
            "Try asking about:"
        )

        print(
            "- Risk"
        )

        print(
            "- Cash"
        )

        print(
            "- Receivables"
        )

        print(
            "- Payables"
        )

        print(
            "- Tax / GST"
        )

        print(
            "- Reconciliation"
        )

        print(
            "- Payroll"
        )

        print(
            "- Financial health"
        )

        print(
            "- Management actions"
        )

    return True

# ============================================================
# INITIALIZE CONTROLLER
# ============================================================

def initialize():

    print()

    print(
        "Loading Nourish Cafe financial data..."
    )


    if not load_data():

        return False


    print(
        "Running financial engines..."
    )


    # --------------------------------------------------------
    # Run existing financial modules
    # --------------------------------------------------------

    run_finance_modules()


    # --------------------------------------------------------
    # Calculate financial health
    # --------------------------------------------------------

    calculate_health()


    # --------------------------------------------------------
    # Calculate risks
    # --------------------------------------------------------

    calculate_risks()


    # --------------------------------------------------------
    # Calculate recommendations
    # --------------------------------------------------------

    calculate_recommendations()


    return True


# ============================================================
# MAIN
# ============================================================

def main():

    if not initialize():

        print(
            "Controller initialization failed."
        )

        return


    # ========================================================
    # HEADER
    # ========================================================

    header()


    print()

    print(
        f"Financial Integrity : "
        f"{financial_health.integrity_score:.1f}/100"
    )


    print(
        f"Financial Status    : "
        f"{financial_health.integrity_status}"
    )


    print(
        f"Current Cash        : "
        f"{money(current_cash)}"
    )


    print()

    print(
        "AI FINANCE CONTROLLER READY"
    )

    line()


    print(
        "Ask a financial question."
    )


    print(
        "Type 'exit' to stop."
    )


    # ========================================================
    # INTERACTIVE LOOP
    # ========================================================

    while True:

        try:

            question = input(
                "\nYou: "
            )


        except KeyboardInterrupt:

            print()

            break


        except EOFError:

            print()

            break


        if not answer_question(
            question
        ):

            print()

            print(
                "AI Finance Controller stopped."
            )

            break


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    main()