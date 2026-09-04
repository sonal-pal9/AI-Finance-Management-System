# Nourish Cafe — AI Finance Controller

An AI-powered financial monitoring and decision-support dashboard designed for small businesses.

##  Problem

Small businesses often manage their finances using spreadsheets and manual processes.

This makes it difficult to quickly identify:

- Cash flow problems
- Outstanding customer invoices
- Supplier payment risks
- Pending payroll
- Tax discrepancies
- Account reconciliation issues

Businesses may not have a dedicated finance team to continuously monitor these risks.

##  Solution

Nourish Cafe — AI Finance Controller analyzes financial data and converts it into actionable management recommendations.

The system provides:

- Financial health monitoring
- Cash flow analysis
- Liquidity risk detection
- Receivable and payable analysis
- Payroll monitoring
- Tax issue detection
- Account reconciliation monitoring
- Priority-based financial recommendations

Instead of simply displaying financial data, the system identifies the most important problems and tells management what should be addressed first.

##  Key Features

###  Financial Dashboard

The dashboard displays important financial indicators including:

- Current Cash
- Estimated Cash Gap
- Financial Integrity Score
- Outstanding Invoices
- Liquidity Status

###  Risk Detection

The system identifies critical financial risks such as:

- Negative cash position
- High receivable risk
- High payable risk
- Pending payroll
- Tax mismatches
- Reconciliation exceptions

###  AI-Driven Recommendations

Financial issues are converted into prioritized actions.

Each recommendation contains:

- Priority
- Priority Score
- Severity
- Financial Impact
- Reason
- Recommended Action

Example:

> Resolve cash deficit

> Immediately improve liquidity through collections, payment scheduling, or additional funding.

###  Liquidity Management

The system evaluates:

- Current cash
- Expected inflows
- Required outflows
- Customer receivables
- Supplier payables
- Payroll obligations

It then determines the overall liquidity status.

###  Financial Integrity

The system checks financial records for inconsistencies including:

- Account mismatches
- Tax mismatches
- Reconciliation exceptions
- Historical tax issues

##  Technology Stack

- Python
- Flask
- HTML5
- CSS3
- JavaScript
- JSON APIs
- CSV-based financial data processing

##  Architecture

```text
                 Financial Data
                       │
                       ▼
              ┌─────────────────┐
              │ Financial Engine │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Risk Detection  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Recommendation  │
              │     Engine      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Flask REST API  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Web Dashboard   │
              └─────────────────┘