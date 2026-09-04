import os
import pandas as pd


# ============================================================
# DATA LOADER
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(BASE_DIR, "data")


# ============================================================
# FILE PATHS
# ============================================================

FILES = {
    "sales": "sales_invoices.csv",
    "payroll": "payroll.csv",
    "tax": "tax_records.csv",
    "tally": "tally_ledger.csv",
    "supplier_bills": "supplier_bills.csv",
    "supplier_payments": "supplier_payments.csv",
    "customer_payments": "customer_payments.csv",
    "bank": "bank_transactions.csv",
    "tax_history": "tax_history.csv"
}


# ============================================================
# LOAD ONE CSV
# ============================================================

def load_file(filename):
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    try:
        return pd.read_csv(path)

    except Exception as e:
        raise RuntimeError(
            f"Could not read {filename}: {e}"
        )


# ============================================================
# LOAD ALL FINANCIAL DATA
# ============================================================

def load_all_data():

    data = {}

    for name, filename in FILES.items():

        try:
            data[name] = load_file(filename)

        except FileNotFoundError as e:

            print(
                f"WARNING: {e}"
            )

            data[name] = pd.DataFrame()

        except Exception as e:

            print(
                f"WARNING: Error loading {filename}: {e}"
            )

            data[name] = pd.DataFrame()

    return data


# ============================================================
# DATA SUMMARY
# ============================================================

def data_summary(data):

    summary = {}

    for name, df in data.items():

        summary[name] = len(df)

    return summary