from flask import Flask, jsonify, render_template

from finance.api_snapshot import build_api_snapshot

app = Flask(__name__)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


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
    return jsonify(snapshot["recommendations"])


if __name__ == "__main__":
    app.run(debug=True)