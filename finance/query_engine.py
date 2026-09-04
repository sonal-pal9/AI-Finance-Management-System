# ============================================================
# NATURAL LANGUAGE QUERY ENGINE
# Nourish Cafe - AI Finance Controller
# ============================================================

import re


# ============================================================
# QUERY CATEGORIES
# ============================================================

RISK_KEYWORDS = [
    "risk",
    "danger",
    "problem",
    "issue",
    "threat",
    "concern"
]

CASH_KEYWORDS = [
    "cash",
    "liquidity",
    "bank balance",
    "bank position",
    "cash position",
    "afford cash"
]

AR_KEYWORDS = [
    "receivable",
    "receivables",
    "customer",
    "customers",
    "collection",
    "collect",
    "money owed",
    "owe us"
]

AP_KEYWORDS = [
    "payable",
    "payables",
    "supplier",
    "suppliers",
    "vendor",
    "vendors",
    "payment"
]

TAX_KEYWORDS = [
    "tax",
    "gst",
    "compliance",
    "filing",
    "filings"
]

RECONCILIATION_KEYWORDS = [
    "reconciliation",
    "reconcile",
    "tally",
    "ledger",
    "mismatch",
    "mismatches"
]

PAYROLL_KEYWORDS = [
    "payroll",
    "salary",
    "salaries",
    "employee",
    "employees",
    "staff"
]

SUMMARY_KEYWORDS = [
    "summary",
    "overall",
    "financial health",
    "how are we doing",
    "status",
    "health"
]

ACTION_KEYWORDS = [
    "what should we do",
    "what do we do",
    "what needs attention",
    "next step",
    "next steps",
    "recommendation",
    "recommendations",
    "action",
    "actions",
    "management",
    "fix first",
    "priority",
    "priorities"
]
PRIORITY_EXPLANATION_KEYWORDS = [
    "why is this the top priority",
    "why is this priority",
    "why this priority",
    "why this recommendation",
    "why should i do this first",
    "why is cash the top priority",
    "explain top priority",
    "explain this recommendation",
    "why was this prioritized",
    "why was this ranked first"
]

# ============================================================
# HELPER
# ============================================================

def contains_keyword(question, keywords):

    question = question.lower()

    for keyword in keywords:

        if keyword in question:
            return True

    return False


# ============================================================
# NORMALIZE QUESTION
# ============================================================

def normalize_question(question):

    question = question.lower().strip()

    question = re.sub(
        r"\s+",
        " ",
        question
    )

    return question


# ============================================================
# DETECT QUESTION TYPE
# ============================================================
def detect_query_type(question):

    q = normalize_question(question)

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if q in ["exit", "quit", "q"]:
        return "exit"


    # --------------------------------------------------------
    # PRIORITY EXPLANATION
    # IMPORTANT: Must come before ACTION_KEYWORDS
    # because ACTION_KEYWORDS contains "priority"
    # --------------------------------------------------------

    if contains_keyword(
        q,
        PRIORITY_EXPLANATION_KEYWORDS
    ):
        return "priority_explanation"


    # --------------------------------------------------------
    # MANAGEMENT ACTIONS
    # --------------------------------------------------------

    if contains_keyword(
        q,
        ACTION_KEYWORDS
    ):
        return "actions"


    # --------------------------------------------------------
    # BIGGEST / MAJOR RISK
    # --------------------------------------------------------

    if contains_keyword(
        q,
        RISK_KEYWORDS
    ):
        return "risk"


    # --------------------------------------------------------
    # TAX
    # --------------------------------------------------------

    if contains_keyword(
        q,
        TAX_KEYWORDS
    ):
        return "tax"


    # --------------------------------------------------------
    # RECONCILIATION
    # --------------------------------------------------------

    if contains_keyword(
        q,
        RECONCILIATION_KEYWORDS
    ):
        return "reconciliation"


    # --------------------------------------------------------
    # PAYROLL
    # --------------------------------------------------------

    if contains_keyword(
        q,
        PAYROLL_KEYWORDS
    ):
        return "payroll"


    # --------------------------------------------------------
    # RECEIVABLES
    # --------------------------------------------------------

    if contains_keyword(
        q,
        AR_KEYWORDS
    ):
        return "receivables"


    # --------------------------------------------------------
    # PAYABLES
    # --------------------------------------------------------

    if contains_keyword(
        q,
        AP_KEYWORDS
    ):
        return "payables"


    # --------------------------------------------------------
    # CASH
    # --------------------------------------------------------

    if contains_keyword(
        q,
        CASH_KEYWORDS
    ):
        return "cash"


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    if contains_keyword(
        q,
        SUMMARY_KEYWORDS
    ):
        return "summary"


    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return "unknown"

# ============================================================
# EXTRACT POSSIBLE ENTITY
# ============================================================

def extract_entity(question):

    q = normalize_question(question)

    entities = []

    if contains_keyword(
        q,
        AR_KEYWORDS
    ):
        entities.append("accounts_receivable")

    if contains_keyword(
        q,
        AP_KEYWORDS
    ):
        entities.append("accounts_payable")

    if contains_keyword(
        q,
        CASH_KEYWORDS
    ):
        entities.append("cash")

    if contains_keyword(
        q,
        TAX_KEYWORDS
    ):
        entities.append("tax")

    if contains_keyword(
        q,
        RECONCILIATION_KEYWORDS
    ):
        entities.append("reconciliation")

    if contains_keyword(
        q,
        PAYROLL_KEYWORDS
    ):
        entities.append("payroll")

    if not entities:
        return None

    return entities[0]


# ============================================================
# QUERY OBJECT
# ============================================================

class FinancialQuery:

    def __init__(
        self,
        question,
        query_type,
        entity
    ):

        self.question = question

        self.query_type = query_type

        self.entity = entity


    def to_dict(self):

        return {
            "question": self.question,
            "query_type": self.query_type,
            "entity": self.entity
        }


# ============================================================
# PARSE QUESTION
# ============================================================

def parse_question(question):

    query_type = detect_query_type(
        question
    )

    entity = extract_entity(
        question
    )

    return FinancialQuery(
        question=question,
        query_type=query_type,
        entity=entity
    )


# ============================================================
# FRIENDLY DESCRIPTION
# ============================================================

def describe_query(query):

    descriptions = {

        "risk":
            "Overall financial risk analysis",

        "cash":
            "Cash and liquidity analysis",

        "receivables":
            "Accounts receivable analysis",

        "payables":
            "Accounts payable analysis",

        "tax":
            "Tax and compliance analysis",

        "reconciliation":
            "Tally and reconciliation analysis",

        "payroll":
            "Payroll analysis",

        "summary":
            "Overall financial health summary",

        "actions":
            "Recommended management actions",

        "exit":
            "Exit controller",

        "unknown":
            "Unknown financial query"
    }

    return descriptions.get(
        query.query_type,
        "Unknown financial query"
    )


# ============================================================
# TEST QUERY ENGINE
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("NATURAL LANGUAGE QUERY ENGINE")
    print("=" * 60)

    test_questions = [

        "What are the biggest risks?",

        "Why is our cash negative?",

        "Can we afford payroll?",

        "Which customers owe us money?",

        "What suppliers should we pay?",

        "Are there any tax problems?",

        "Why is reconciliation a problem?",

        "What should we do?",

        "How are we doing financially?"
    ]

    for question in test_questions:

        result = parse_question(
            question
        )

        print()
        print(
            f"Question : {question}"
        )

        print(
            f"Type     : {result.query_type}"
        )

        print(
            f"Entity   : {result.entity}"
        )

        print(
            f"Meaning  : {describe_query(result)}"
        )