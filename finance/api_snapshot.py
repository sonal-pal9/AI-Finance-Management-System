"""
API Snapshot
------------
Creates one complete financial snapshot
for the future website/API.
"""

from finance.data_loader import load_all_data

from finance.financial_query_engine import (
    build_financial_snapshot
)

from finance.financial_health import (
    calculate_financial_health
)

from finance.smart_recommendation_engine import (
    generate_recommendations
)
from liquidity_action_engine import critical_actions

def build_api_snapshot():

    # --------------------------------------------------------
    # Load financial data
    # --------------------------------------------------------

    data = load_all_data()

    # --------------------------------------------------------
    # Existing financial snapshot
    # --------------------------------------------------------

    snapshot = build_financial_snapshot(data)

    # --------------------------------------------------------
    # Financial Health
    # --------------------------------------------------------
    #
    # Use the same financial-health calculation
    # used by the controller.
    #
    # critical_actions is currently not exposed by
    # build_financial_snapshot(), so use 0 temporarily.
    #
    # We will connect the real liquidity-engine value
    # separately.
    # --------------------------------------------------------

    financial_health = calculate_financial_health(

        current_cash=snapshot["current_cash"],

        total_ar=snapshot["total_ar"],

        total_ap=snapshot["total_ap"],

        tax_readiness=snapshot["tax_readiness"],

        reconciliation_rate=snapshot[
            "reconciliation_rate"
        ],

        mismatched_accounts=snapshot[
            "mismatched_accounts"
        ],

        tax_mismatches=snapshot[
            "tax_mismatches"
        ],

        critical_actions=critical_actions,

        pending_payroll=snapshot[
            "pending_payroll"
        ]
    )

    # --------------------------------------------------------
    # Add financial health to snapshot
    # --------------------------------------------------------

    snapshot["financial_integrity"] = (
        financial_health.integrity_score
    )

    snapshot["integrity_status"] = (
        financial_health.integrity_status
    )

    snapshot["month_end_status"] = (
        financial_health.month_end_status
    )

    # --------------------------------------------------------
    # Smart recommendations
    # --------------------------------------------------------

    recommendations = generate_recommendations(

        current_cash=snapshot["current_cash"],

        total_ar=snapshot["total_ar"],

        total_ap=snapshot["total_ap"],

        pending_payroll=snapshot[
            "pending_payroll"
        ],

        tax_mismatches=snapshot[
            "tax_mismatches"
        ],

        mismatched_accounts=snapshot[
            "mismatched_accounts"
        ],

        critical_actions=critical_actions
    )

    # --------------------------------------------------------
    # Convert recommendations to dictionaries
    # --------------------------------------------------------

    recommendation_data = []

    for recommendation in recommendations:

        recommendation_data.append({

            "priority":
                recommendation.priority,

            "severity":
                recommendation.severity,

            "title":
                recommendation.title,

            "amount":
                recommendation.amount,

            "reason":
                recommendation.reason,

            "action":
                recommendation.action,

            "priority_score":
                recommendation.priority_score
        })

    snapshot["recommendations"] = (
        recommendation_data
    )

    return snapshot


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    financial_snapshot = (
        build_api_snapshot()
    )

    print()

    print("=" * 65)

    print(
        "API-READY FINANCIAL SNAPSHOT"
    )

    print("=" * 65)

    print()

    for key, value in financial_snapshot.items():

        if key != "recommendations":

            print(
                f"{key:<25}: {value}"
            )

    print()

    print("Recommendations:")

    print("-" * 40)

    for recommendation in financial_snapshot[
        "recommendations"
    ]:

        print(

            f"{recommendation['priority']}. "

            f"{recommendation['severity']} - "

            f"{recommendation['title']} "

            f"({recommendation['priority_score']}/100)"
        )