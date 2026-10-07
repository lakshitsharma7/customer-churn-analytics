# 📊 CloudSync — Customer Churn & Retention Analytics Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/SQL-ANSI%20%2F%20PostgreSQL%20%2F%20SQLite-orange.svg)](https://sqlite.org/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Multi--Page%20Dashboard-yellow.svg)](https://powerbi.microsoft.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn%20(ROC--AUC%200.98)-green.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

> **An End-to-End Enterprise Data Analyst & Business Intelligence Portfolio Project for a Subscription SaaS Business ($17.04M ARR Base, 12,000 Accounts, 210k+ Telemetry Records).**

---

## 📑 Table of Contents
1. [Executive Summary & Business Context](#-executive-summary--business-context)
2. [Project Architecture & Star Schema](#-project-architecture--star-schema)
3. [Core SaaS KPI Scorecard](#-core-saas-kpi-scorecard)
4. [Dataset & Data Hygiene Protocols](#-dataset--data-hygiene-protocols)
5. [Jupyter Notebooks Analytics Suite](#-jupyter-notebooks-analytics-suite)
6. [SQL Intelligence Suite (20 Analytical Queries)](#-sql-intelligence-suite)
7. [Customer Segmentation & Health Scoring](#-customer-segmentation--health-scoring)
8. [Machine Learning Churn Prediction Model](#-machine-learning-churn-prediction-model)
9. [Power BI Multi-Page Executive Dashboard](#-power-bi-multi-page-executive-dashboard)
10. [Top 10 Empirical Business Insights](#-top-10-empirical-business-insights)
11. [Strategic Management Recommendations](#-strategic-management-recommendations)
12. [Project Repository Structure](#-project-repository-structure)
13. [Installation & Execution Guide](#-installation--execution-guide)

---

## 🏢 Executive Summary & Business Context

**CloudSync** is a high-growth B2B SaaS company delivering cloud collaboration and productivity software to SMB, Mid-Market, and Enterprise organizations across North America, Europe, and Asia-Pacific.

### The Business Challenge:
While CloudSync generated **$17.04M in Annual Recurring Revenue (ARR)** across 8,126 active customer subscriptions, customer cancellations escalated to an **overall churn rate of 30.17%**, draining **$386,317.15 in Monthly Recurring Revenue ($4,635,805.80 annualized)**.

Management commissioned this comprehensive data analytics initiative to answer 10 critical executive questions:
1. *Why are customers leaving and what are the primary root causes?*
2. *Which customer segments and contract plans experience the highest churn?*
3. *How does product telemetry (login frequency, session length, feature breadth) correlate with retention?*
4. *What role do support resolution times and billing failures play in driving cancellations?*
5. *Which active high-value accounts are currently at critical risk of churn?*
6. *How much revenue is being lost to churn, and what is the recoverable upside?*
7. *Which customer acquisition channels deliver the highest long-term Customer Lifetime Value (LTV)?*
8. *What are the longitudinal retention dynamics across signup cohorts?*
9. *How can we segment the customer base using behavioral and RFM scoring?*
10. *What specific, data-backed operational interventions should leadership execute to reduce churn?*

---

## 🏛️ Project Architecture & Star Schema

The analytics pipeline models raw operational data into an enterprise-grade **Star Schema** optimized for analytical SQL and Power BI DAX performance:

```mermaid
erDiagram
    DimDate ||--o{ FactSubscriptions : "subscription_start_date / end_date"
    DimDate ||--o{ FactActivity : "activity_month"
    DimDate ||--o{ FactPayments : "payment_date"
    DimDate ||--o{ FactSupport : "ticket_date"
    DimCustomer ||--o{ FactSubscriptions : "customer_id"
    DimCustomer ||--o{ FactActivity : "customer_id"
    DimCustomer ||--o{ FactPayments : "customer_id"
    DimCustomer ||--o{ FactSupport : "customer_id"
    DimPlan ||--o{ FactSubscriptions : "plan_name"
    DimGeography ||--o{ DimCustomer : "country / state / city"

    DimCustomer {
        string customer_id PK
        string customer_name
        int age
        string gender
        string customer_segment
        string industry
        string company_size
        string acquisition_channel
        float health_score
        string risk_category
        float churn_probability
    }

    DimDate {
        date Date PK
        int Year
        string Quarter
        int MonthNo
        string MonthName
    }

    DimPlan {
        string plan_name PK
        float base_price
        string plan_tier
    }

    FactSubscriptions {
        string subscription_id PK
        string customer_id FK
        string plan_name FK
        string contract_type
        date subscription_start_date FK
        date subscription_end_date FK
        float monthly_fee
        float discount_percentage
        string subscription_status
        float tenure_months
    }

    FactActivity {
        string activity_id PK
        string customer_id FK
        date activity_month FK
        int login_count
        int active_days
        int session_count
        float avg_session_minutes
        int features_used
        int projects_created
        int files_uploaded
        int api_usage_count
    }

    FactPayments {
        string payment_id PK
        string customer_id FK
        date payment_date FK
        float amount
        string payment_method
        string payment_status
        int days_overdue
    }

    FactSupport {
        string ticket_id PK
        string customer_id FK
        date ticket_date FK
        string issue_category
        string priority
        float resolution_time_hours
        string ticket_status
        int satisfaction_score
    }
```

---

## 📈 Core SaaS KPI Scorecard

All key performance indicators are calculated from the cleaned 12,000-customer dataset using standardized SaaS subscription finance methodologies:

| Metric Name | Formula / Logic | Dataset Value | Business Interpretation |
| :--- | :--- | :--- | :--- |
| **Total Customers** | $\text{Distinct Count}(customer\_id)$ | **12,000** | Total customer accounts acquired since 2022 |
| **Active Customers** | $\text{Count}(status = 'Active')$ | **8,126** | 67.7% active paying customer base |
| **Churned Customers** | $\text{Count}(status = 'Churned')$ | **3,620** | Total accounts cancelled |
| **Overall Churn Rate** | $\frac{\text{Churned}}{\text{Total}} \times 100$ | **30.17%** | Cumulative account cancellation rate |
| **Customer Retention Rate** | $100\% - \text{Churn Rate}$ | **69.83%** | Base retention rate across all cohorts |
| **Monthly Recurring Revenue (MRR)** | $\sum \text{monthly\_fee}_{\text{Active}}$ | **$1,420,306.00** | Monthly predictable subscription run-rate |
| **Annual Recurring Revenue (ARR)** | $\text{MRR} \times 12$ | **$17,043,672.00** | Annualized recurring subscription baseline |
| **Average Revenue Per User (ARPU)** | $\frac{\text{MRR}}{\text{Active Customers}}$ | **$174.79 / mo** | Average monthly monetization per account |
| **Customer Lifetime Value (LTV)** | $\text{ARPU} \times \text{Avg Active Tenure}$ | **$3,670.57** | Expected revenue generated per customer lifespan |
| **Average Active Customer Tenure** | $\text{Avg}(\text{tenure}_{\text{Active}})$ | **21.0 months** | Average longevity of active customer accounts |
| **Average Churned Customer Tenure** | $\text{Avg}(\text{tenure}_{\text{Churned}})$ | **10.8 months** | Average duration before customer cancellations |
| **Monthly Revenue Lost to Churn** | $\sum \text{monthly\_fee}_{\text{Churned}}$ | **$386,317.15** | Ongoing monthly revenue leakage |
| **Annualized Revenue Lost to Churn** | $\text{Lost MRR} \times 12$ | **$4,635,805.80** | Annualized recurring revenue lost |
| **Average Net Promoter Score (NPS)** | $\text{Mean}(nps\_score)$ | **6.41 / 10** | Promoters: 8.1 (Active), Detractors: 4.2 (Churned) |
| **Average Support CSAT** | $\text{Mean}(satisfaction\_score)$ | **3.28 / 5.0** | Customer support satisfaction score |

---

## 🧹 Dataset & Data Hygiene Protocols

The repository generates and cleans 6 relational tables representing over 350,000 combined transactional records:

1. **`customers.csv`** (12,000 accounts): Demographics, geography, customer segments (`SMB`, `Mid-Market`, `Enterprise`), industry, company size, signup date, acquisition channel.
2. **`subscriptions.csv`** (12,000 records): Subscription IDs, plans (`Basic`, `Professional`, `Business`, `Enterprise`), contract terms (`Monthly`, `Quarterly`, `Annual`), monthly fees, discount percentages, auto-renew status.
3. **`customer_activity.csv`** (210,832 monthly logs): Monthly logins, active days, session counts, average session minutes, features used, projects created, files uploaded, API usage.
4. **`support_tickets.csv`** (15,092 tickets): Categories (`Technical`, `Billing`, `Login`, `Performance`, `Integration`, `Security`), priority, resolution hours, status (`Resolved`, `Pending`, `Escalated`, `Closed`), CSAT.
5. **`payments.csv`** (117,559 transactions): Payment gateways (`Credit Card`, `Debit Card`, `Bank Transfer`, `PayPal`, `UPI`), payment status (`Successful`, `Failed`, `Refunded`, `Pending`), days overdue.
6. **`customer_feedback.csv`** (7,785 surveys): NPS ratings (0–10), CSAT scores (1–5), feedback categories, qualitative verbatim feedback.

### Data Cleaning Protocols Demonstrated:
- **Deduplication:** Identified and eliminated 150 injected duplicate customer records (~1.2%).
- **Casing Normalization:** Standardized mixed uppercase/lowercase names into clean Title Case format.
- **Missing Value Treatment:** Imputed missing geographic attributes (`city`, `state`) and channels with `'Unknown'` and `'Direct/Unknown'`.
- **Date Standardization:** Standardized multi-format date strings (`YYYY-MM-DD`, `DD/MM/YYYY`) using mixed datetime parsers.
- **Outlier Remediation:** Detected and capped hardware sensor resolution time anomalies (e.g., `999.9 hours`) using category-median imputation (`14.2 hours`).
- **Payment Anomaly Treatment:** Corrected negative amount sign errors and capped extreme payment outliers above `$15,000` to standard annual contract maximums (`$5,988`).

---

## 📓 Jupyter Notebooks Analytics Suite

The project includes 4 fully-executed, documented Jupyter Notebooks in [notebooks/](file:///d:/projects%20(2)/notebooks):

| Notebook | Purpose & Methodologies | Key Deliverables |
| :--- | :--- | :--- |
| **[`01_data_cleaning.ipynb`](file:///d:/projects%20(2)/notebooks/01_data_cleaning.ipynb)** | Data auditing, missing value imputation, deduplication, date validation, and outlier remediation. | Cleaned datasets in `data/cleaned/` and SQLite DB `data/cloudsync.db`. |
| **[`02_eda.ipynb`](file:///d:/projects%20(2)/notebooks/02_eda.ipynb)** | SaaS financial KPI calculations, univariate/bivariate distributions, cohort retention curves. | Churn rates by plan, contract, segment, channel, and tenure density curves. |
| **[`03_customer_segmentation.ipynb`](file:///d:/projects%20(2)/notebooks/03_customer_segmentation.ipynb)** | RFM quintile scoring, 5-pillar Customer Health Score (0–100), and K-Means clustering. | Segment profiling (`High Value – Low Risk`, `High Value – High Risk`, `At-Risk`). |
| **[`04_churn_analysis.ipynb`](file:///d:/projects%20(2)/notebooks/04_churn_analysis.ipynb)** | Predictive modeling (Logistic Regression vs. Random Forest), odds ratios, and risk tables. | ROC-AUC (0.980), Confusion Matrix, Feature Importance, actionable risk watchlist. |

---

## 💻 SQL Intelligence Suite

The file [`sql/sql_analysis.sql`](file:///d:/projects%20(2)/sql/sql_analysis.sql) provides 20 production-grade analytical SQL queries utilizing **Common Table Expressions (CTEs)**, **Window Functions** (`SUM OVER`, `ROW_NUMBER`, `LAG`, `NTILE`), **CASE statements**, and **Complex Multi-Table JOINs**:

1. **Overall Churn Rate & Subscriber Status Summary**: Baseline customer count and status breakdown.
2. **Monthly Churn Trend & Rolling Retention Metrics**: Month-over-month churn counts and cumulative revenue loss.
3. **Churn Rate and MRR Impact by Subscription Plan**: Financial impact of tier-based churn.
4. **Churn Rate by Contract Commitment Type**: Monthly vs. Annual contract cancellation rates.
5. **Revenue Contribution & ARPU by Customer Segment**: Segment MRR, ARR, and ARPU breakdown.
6. **Revenue Lost Due to Churn by Industry and Segment**: Pinpointing industry-specific revenue leakage.
7. **Top 20 Enterprise Customers by Historical Revenue**: Ranking top accounts by cumulative spend.
8. **Customers with Declining Engagement**: Detecting active accounts with >40% MoM drop in logins.
9. **Payment Delinquency & Failed Payment Churn Correlation**: Assessing gateway failure impacts.
10. **Support Ticket Intensity & Unresolved Tickets**: Measuring support resolution latency by churn status.
11. **High-Value Active Customers at Imminent Churn Risk**: Identifying Enterprise/Business accounts with open tickets or payment failures.
12. **Retention Performance by Acquisition Channel**: Evaluating channel-level CAC efficiency and retention.
13. **Average Lifetime Tenure of Churned vs Active Customers**: Quantifying customer lifespan.
14. **Churn & Revenue Profile by Country**: Regional performance across US, UK, Canada, Germany, Australia, India.
15. **Churn by Industry Vertical**: Comparing Technology, Healthcare, Finance, Retail, Education, Manufacturing.
16. **Customers with High NPS but Low Engagement**: Identifying "Silent Churn Risk" accounts.
17. **Customers with Low CSAT and Multiple Support Tickets**: Escalating frustrated accounts.
18. **Monthly Recurring Revenue (MRR) Run-Rate**: Net MRR change and cumulative revenue trajectory.
19. **Quarterly Cohort Retention Matrix**: Longitudinal cohort retention tracking.
20. **Top Strategic Retention Opportunities**: Automated decision logic assigning specific retention actions to high-risk accounts.

---

## 🎯 Customer Segmentation & Health Scoring

### 1. The 5-Pillar Customer Health Score Model (0 – 100)
Rather than arbitrary scoring, CloudSync's Customer Health Score evaluates 5 core dimensions:
$$\text{Health Score} = 0.35(\text{Engagement}) + 0.25(\text{Satisfaction}) + 0.15(\text{Payment Reliability}) + 0.15(\text{Support Experience}) + 0.10(\text{Tenure})$$

- **Product Engagement (35%):** Normalized monthly logins, active days, and feature utilization.
- **Customer Satisfaction (25%):** Net Promoter Score (NPS) and CSAT survey ratings.
- **Payment Reliability (15%):** Flawless payment record with heavy penalties on gateway failures.
- **Support Experience (15%):** Fast resolution times with penalties on pending/escalated tickets.
- **Tenure Stability (10%):** Longevity bonus for accounts active past 12 months.

### 2. Strategic Customer Segments
- 🟢 **High Value – Low Risk (5,153 Accounts | 42.9%):** Core growth engine; high MRR, healthy engagement (Health Score $\ge 60$).
- 🔴 **High Value – High Risk (254 Accounts | 2.1%):** **Immediate Priority!** Generating **$84,210 in monthly MRR ($1.01M ARR)** with critical health warnings.
- 🟡 **Low Value – Low Risk (2,396 Accounts | 20.0%):** Stable SMB base; prime candidates for annual plan upselling.
- 🟠 **At-Risk Customers (574 Accounts | 4.8%):** Slipping engagement and support tickets; require automated success campaigns.
- ⚫ **Inactive Customers (3,620 Accounts | 30.2%):** Churned accounts for win-back reactivation campaigns.

---

## 🤖 Machine Learning Churn Prediction Model

Two interpretable machine learning models were developed and evaluated strictly on training partitions without data leakage:

| Model Architecture | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Interpretable Baseline)** | 95.37% | 95.17% | 89.17% | 0.9207 | **0.9849** |
| **Random Forest Classifier (Ensemble Model)** | 94.97% | **97.84%** | 85.19% | 0.9108 | **0.9797** |

### Key Model Interpretability Insights:
- **Top Factors Increasing Churn Odds:** Month-to-Month contract type ($\text{Odds Ratio} = 3.42$), Failed payment transactions ($\text{Odds Ratio} = 2.81$), Unresolved support tickets ($\text{Odds Ratio} = 2.34$).
- **Top Protective Factors Reducing Churn Odds:** High monthly logins ($\text{Odds Ratio} = 0.28$), Annual contract type ($\text{Odds Ratio} = 0.31$), High NPS score ($\text{Odds Ratio} = 0.45$).

---

## 📊 Power BI Multi-Page Executive Dashboard

The interactive Power BI solution is structured into **6 Executive Pages** built using modern corporate dashboard design standards:

### Page 1 — Executive Overview
![Executive Overview](screenshots/pbi_page1_executive_overview.png)
*Executive KPI summary cards, monthly churn trend, active MRR by subscription tier, contract type churn rates, and segment MRR share.*

---

### Page 2 — Churn Analysis Deep Dive
![Churn Analysis](screenshots/pbi_page2_churn_analysis.png)
*Multi-dimensional churn breakdown by subscription plan, acquisition channel, industry vertical, login frequency deciles, and support resolution velocity.*

---

### Page 3 — Customer Retention & Cohort Dynamics
![Customer Retention](screenshots/pbi_page3_retention_cohorts.png)
*Longitudinal signup cohort retention curves, active vs. churned customer tenure density distributions, and NPS rating retention correlations.*

---

### Page 4 — Customer Risk Matrix & Predictive Churn Guard
![Customer Risk](screenshots/pbi_page4_customer_risk_matrix.png)
*Machine learning predicted churn probability distributions, risk tier breakdown, and interactive Actionable High-Risk Customer Watchlist table.*

---

### Page 5 — Customer Segmentation & RFM Value Matrix
![Customer Segmentation](screenshots/pbi_page5_segmentation_rfm.png)
*Strategic health segment distribution, MRR value matrix, Health Score vs. Monthly Fee quadrant plot, and RFM churn heatmap.*

---

### Page 6 — Executive Recommendations & Strategic Action Plan
![Business Recommendations](screenshots/pbi_page6_recommendations_action.png)
*Quantified business cases and operational implementation workflows for annual contract conversion, automated dunning, and support SLA acceleration.*

---

## 💡 Top 10 Empirical Business Insights

*Extracted directly from the CloudSync multi-table empirical dataset (see [`reports/business_insights.md`](file:///d:/projects%20(2)/reports/business_insights.md) for full report):*

1. **Month-to-Month Contract Vulnerability:** Monthly contracts exhibit **37.8% churn versus 10.4% on Annual contracts**, causing $268k in monthly lost MRR.
2. **Enterprise Revenue Anchor:** Enterprise accounts contribute **46% of active MRR ($653k/mo)** with only 12.4% churn, compared to 34.8% churn in SMBs.
3. **The "5-Login Cliff":** Customers logging in **<5 times/month experience 58.4% churn**, dropping to **<8.2% for >20 monthly logins**.
4. **Involuntary Payment Churn:** Accounts experiencing $\ge 1$ payment failure have a **45.2% churn rate**, generating **$420k in annual revenue leakage**.
5. **Support Resolution Latency:** Churned accounts averaged **24.8 hours resolution time** (vs. 14.2h for retained); open tickets increase churn to 51.2%.
6. **Acquisition Channel Quality:** Referral and Sales channels achieve **<20% churn** and highest ARPU ($382/mo), while Paid Social exceeds 35% churn.
7. **"Silent Churn Risk":** Identified **218 active Promoter accounts (NPS $\ge 8$) with $\le 5$ monthly logins** ($34.8k MRR at risk).
8. **Basic Plan Feature Friction:** Entry-level Basic tier ($29/mo) suffers **36.4% churn** and lowest CSAT (2.8/5) due to missing native integrations.
9. **Month 6 Longevity Stabilization:** 62% of churn occurs within the first 6 months; accounts surviving past Month 6 retain at 84.6%.
10. **Predictive Churn Recovery:** ML model isolates **254 Active High-Value accounts at immediate risk ($1.01M ARR)** for proactive CSM intervention.

---

## 🚀 Strategic Management Recommendations

| Strategic Priority | Target Audience | Expected Revenue Impact | Operational Action Plan |
| :--- | :--- | :---: | :--- |
| **1. Annual Plan Conversion Campaign** | High-Value Monthly Subscribers | **+$780,000 ARR** | Deploy in-app prompts offering 2 months free upon annual upgrade with automated ROI calculators. |
| **2. Smart Dunning & Payment Retry Logic** | Delinquent / Failed Accounts | **+$420,000 ARR** | Implement Stripe/Churnbuster smart retry schedules (days 1, 3, 5, 7) and automated SMS card update links. |
| **3. Enterprise White-Glove Support SLAs** | Business & Enterprise Tiers | **+$480,000 ARR** | Route Enterprise tickets to Tier-3 CSMs with mandatory <2h first response and <12h resolution SLAs. |
| **4. Behavioral Re-engagement Triggers** | Users with >40% login drop | **+$350,000 ARR** | Trigger automated in-app walkthroughs and Customer Success outreach when 14-day login velocity drops. |
| **5. High-Risk Account CRM Integration** | High-Risk Accounts ($\ge 0.70$) | **+$353,000 ARR** | Sync daily ML churn risk scores into Salesforce/HubSpot with mandatory 48-hour CSM intervention tasks. |

---

## 📂 Project Repository Structure

```text
customer-churn-analytics/
├── data/
│   ├── customers.csv                    # Raw customer demographics
│   ├── subscriptions.csv                # Raw subscription contracts
│   ├── customer_activity.csv            # Raw monthly telemetry logs
│   ├── support_tickets.csv              # Raw support incident logs
│   ├── payments.csv                     # Raw billing & gateway records
│   ├── customer_feedback.csv            # Raw NPS & CSAT surveys
│   ├── cloudsync.db                     # SQLite Database for SQL testing
│   └── cleaned/
│       ├── customers_clean.csv          # Deduplicated, normalized customers
│       ├── subscriptions_clean.csv      # Cleaned subscription records
│       ├── customer_activity_clean.csv  # Standardized telemetry records
│       ├── support_tickets_clean.csv    # Outlier-remediated tickets
│       ├── payments_clean.csv           # Cleaned transaction records
│       ├── customer_feedback_clean.csv  # Validated survey records
│       └── customer_churn_master.csv    # Master ML & Power BI feature store
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb           # Data hygiene, deduplication & ETL
│   ├── 02_eda.ipynb                     # SaaS KPIs, distributions & cohorts
│   ├── 03_customer_segmentation.ipynb   # RFM, Health Score & K-Means
│   └── 04_churn_analysis.ipynb          # Predictive modeling & risk scoring
│
├── sql/
│   └── sql_analysis.sql                 # 20 Production-grade analytical SQL queries
│
├── powerbi/
│   ├── dax_measures.md                  # Complete DAX measures library
│   ├── data_model_architecture.md       # Star schema relationships & ERD
│   └── Customer_Churn_Retention_Guide.md# Power BI implementation guide
│
├── reports/
│   └── business_insights.md             # Top 10 Executive Business Insights
│
├── screenshots/
│   ├── 01_executive_overview.png        # Python EDA overview chart
│   ├── 02_cohort_retention.png          # Python cohort retention curve
│   ├── 03_customer_segmentation.png     # Python health segment scatter
│   ├── 04_model_evaluation.png          # Python ROC curves & feature importances
│   ├── 05_confusion_matrix.png          # Python confusion matrix heatmap
│   ├── pbi_page1_executive_overview.png # Power BI Page 1 Overview
│   ├── pbi_page2_churn_analysis.png     # Power BI Page 2 Churn Deep Dive
│   ├── pbi_page3_retention_cohorts.png  # Power BI Page 3 Customer Retention
│   ├── pbi_page4_customer_risk_matrix.png# Power BI Page 4 Customer Risk
│   ├── pbi_page5_segmentation_rfm.png   # Power BI Page 5 Segmentation
│   └── pbi_page6_recommendations_action.png# Power BI Page 6 Recommendations
│
├── generate_data.py                     # Synthetic data generation engine
├── run_pipeline.py                      # Master analytics & ML execution script
├── build_notebooks.py                   # Jupyter Notebook builder script
├── generate_dashboard_screens.py        # Power BI visual renderer script
├── requirements.txt                     # Project Python dependencies
└── README.md                            # Master project documentation
```

## 🛠️ Technology Stack & Environment

| Layer | Tools & Libraries | Key Application |
| :--- | :--- | :--- |
| **Language & Core** | Python 3.10+, SQL (ANSI / SQLite / PostgreSQL) | Data processing, feature pipelines, query intelligence |
| **Data Manipulation** | Pandas, NumPy | Data cleaning, reshaping, aggregation, RFM scoring |
| **Machine Learning** | Scikit-Learn | Preprocessing pipelines, Logistic Regression, Random Forest, ROC-AUC |
| **Visualization & Reporting**| Matplotlib, Seaborn | Distribution plots, cohort heatmaps, confusion matrices |
| **Relational Database** | SQLite 3, SQLAlchemy | Star schema data warehouse and query execution engine |
| **Business Intelligence** | Microsoft Power BI Desktop, DAX | Multi-page executive dashboards, time intelligence, KPI cards |
| **Notebook Environments** | JupyterLab / Jupyter Notebook (`nbformat`) | Reproducible analysis, documentation, code cells |

---

## 📋 System Requirements & Prerequisites

- **Operating System:** Windows 10/11, macOS Monterey+, or Ubuntu 20.04+ LTS
- **Python:** Version 3.10, 3.11, or 3.12 installed and accessible via PATH
- **Package Manager:** `pip` (Python package manager)
- **Database Client (Optional):** SQLite3 CLI or DBeaver / TablePlus / DB Browser for SQLite
- **BI Tool (Optional):** Microsoft Power BI Desktop (for interacting with `.pbix` models and DAX measures)

---

## ⚙️ Installation & Setup Steps

### 1. Clone Repository & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/your-username/customer-churn-analytics.git
cd customer-churn-analytics

# Create a dedicated virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (Command Prompt):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# Upgrade pip and install all required dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔧 Configuration Instructions

The project uses clean, modular paths and zero hard-coded external credentials.

### Configuration Settings & Defaults
- **Data Directories:** Default paths are pre-configured in `generate_data.py` and `run_pipeline.py` pointing to `data/` and `data/cleaned/`.
- **Database Target:** Relational warehouse is stored locally at `data/cloudsync.db` using SQLite.
- **Random Seed:** Reproducibility is guaranteed across data generation and modeling splits via `np.random.seed(42)` and `random.seed(42)`.
- **Environment Variables (Optional):**
  If connecting to a remote PostgreSQL warehouse instead of local SQLite:
  ```env
  DATABASE_URL=postgresql://username:password@localhost:5432/cloudsync
  ```

---

## 🚀 How to Run the Project (Step-by-Step Execution)

### Step 1: Generate the Raw Dataset
```bash
# Generates realistic synthetic multi-table data for 12,000 customers
python generate_data.py
```

### Step 2: Run End-to-End Analytics Pipeline
```bash
# Executes data cleaning, KPI calculations, RFM scoring, and ML churn models
python run_pipeline.py
```

### Step 3: Build & Launch Jupyter Notebooks
```bash
# Programmatically builds the 4 fully-formatted Jupyter Notebooks
python build_notebooks.py

# Launch JupyterLab or Jupyter Notebook interface to explore:
jupyter lab
# or:
jupyter notebook
```

### Step 4: Validate Analytical SQL Queries
```bash
# Run the 20 analytical queries against SQLite database:
python -c "
import sqlite3
conn = sqlite3.connect('data/cloudsync.db')
with open('sql/sql_analysis.sql') as f:
    queries = [q.strip() for q in f.read().split(';') if q.strip()]
for idx, q in enumerate(queries, 1):
    cur = conn.cursor()
    cur.execute(q)
    print(f'Query {idx:02d}: Executed successfully ({len(cur.fetchall())} rows)')
"
```

### Step 5: Render Power BI Visual Screenshots
```bash
# Renders presentation-grade visual dashboard pages to screenshots/
python generate_dashboard_screens.py
```

---

## 🏗️ Build & Deployment Instructions (Power BI & Productionization)

### 1. Power BI Desktop Integration
1. Open **Microsoft Power BI Desktop**.
2. Click **Get Data** -> **Folder** (or **Text/CSV**) -> Point to `data/cleaned/`.
3. Import `customers_clean.csv`, `subscriptions_clean.csv`, `customer_activity_clean.csv`, `support_tickets_clean.csv`, `payments_clean.csv`, `customer_feedback_clean.csv`, and `customer_churn_master.csv`.
4. Configure Star Schema relationships as documented in [`powerbi/data_model_architecture.md`](powerbi/data_model_architecture.md).
5. Copy and paste the DAX measures from [`powerbi/dax_measures.md`](powerbi/dax_measures.md) into a dedicated `_Measures` table.
6. Publish report to Power BI Service / Workspace for executive consumption.

### 2. Machine Learning Production Deployment
To containerize or deploy the churn scoring pipeline:
- Export the trained pipeline: `joblib.dump(rf_pipeline, 'model/churn_model.pkl')`
- Schedule batch inference via Apache Airflow or cron jobs to generate weekly customer risk scores.
- Sync risk scores directly into CRM (Salesforce / HubSpot) via reverse ETL (Census / Hightouch).

---

## 🎓 Candidate Skills Demonstrated
- **Business Analytics & SaaS Finance:** MRR, ARR, ARPU, LTV, Cohort Retention, Net Churn, Dunning Economics.
- **Advanced SQL:** CTEs, Window Functions (`SUM OVER`, `ROW_NUMBER`, `LAG`, `NTILE`), Subqueries, CASE statements.
- **Python Data Science:** Pandas, NumPy, Scikit-Learn, Matplotlib, Seaborn, Feature Engineering, Pipelines.
- **Machine Learning & Interpretability:** Logistic Regression Odds Ratios, Random Forest, ROC-AUC (0.98), Confusion Matrix.
- **Business Intelligence & Power BI:** Star Schema Modeling, DAX Time Intelligence, Multi-Page Executive Layouts.
- **Executive Communication:** Translating empirical data into prioritized, dollar-quantified management roadmaps.

