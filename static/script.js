async function loadDashboard() {

    try {

        const summaryResponse =
            await fetch("/api/financial-summary");

        const summary =
            await summaryResponse.json();


        document.getElementById("currentCash").textContent =
            "₹" + Number(summary.current_cash).toLocaleString("en-IN");

        document.getElementById("cashGap").textContent =
            "₹" + Number(
                Math.abs(summary.current_cash)
            ).toLocaleString("en-IN");

        document.getElementById("financialIntegrity").textContent =
            summary.financial_integrity;

        document.getElementById("outstandingInvoices").textContent =
            summary.outstanding_invoices;


        document.getElementById("liquidityStatus").textContent =
            summary.cash_risk;


        document.getElementById("cashRisk").textContent =
            summary.cash_risk;

        document.getElementById("receivableRisk").textContent =
            summary.receivable_risk;

        document.getElementById("payableRisk").textContent =
            summary.payable_risk;

        document.getElementById("payrollRisk").textContent =
            summary.payroll_risk;


        const recommendationsResponse =
            await fetch("/api/recommendations");

        const recommendations =
            await recommendationsResponse.json();


        const container =
            document.getElementById("recommendations");

        container.innerHTML = "";


        recommendations.forEach((item, index) => {

            const div = document.createElement("div");

            div.className = "recommendation";

            div.innerHTML = `
                <div class="priority">
                    Priority ${item.priority}
                </div>

                <h3>${item.title}</h3>

                <p>${item.action}</p>

                <small>
                    ${item.reason}
                </small>
            `;

            container.appendChild(div);

        });

    }

    catch (error) {

        console.error(error);

    }

}


loadDashboard();