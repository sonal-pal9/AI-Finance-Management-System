from flask import Flask, jsonify

from finance.api_snapshot import build_api_snapshot


app = Flask(__name__)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "application": "Nourish Cafe AI Finance Controller",
        "status": "running"
    })


# ============================================================
# FINANCIAL SUMMARY
# ============================================================

@app.route("/api/financial-summary")
def financial_summary():

    snapshot = build_api_snapshot()

    return jsonify(snapshot)


# ============================================================
# RECOMMENDATIONS
# ============================================================

@app.route("/api/recommendations")
def recommendations():

    snapshot = build_api_snapshot()

    return jsonify(
        snapshot["recommendations"]
    )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )