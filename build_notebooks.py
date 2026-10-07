import os
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NB_DIR = os.path.join(BASE_DIR, 'notebooks')
os.makedirs(NB_DIR, exist_ok=True)

# Helper function to create executed notebook
def save_notebook(nb, filename):
    filepath = os.path.join(NB_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Created notebook: {filepath}")

# ==============================================================================
# NOTEBOOK 1: 01_data_cleaning.ipynb
# ==============================================================================
nb1 = new_notebook()
nb1.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}

nb1.cells.append(new_markdown_cell("""# 📊 CloudSync SaaS Analytics: 01. Data Cleaning & Integrity Audit

**Author:** Antigravity Data Intelligence & Business Analytics Team  
**Dataset:** CloudSync Enterprise Customer & Subscription Ecosystem (12,000+ Accounts)  
**Objective:** Perform enterprise-grade data auditing, missing value treatment, deduplication, casing standardization, date validation, outlier remediation, and export clean star-schema datasets.

---

### Business Context
Data quality directly impacts strategic retention decisions and ML reliability. Prior to modeling customer lifetime behavior and churn drivers, we execute systematic data hygiene protocols across all 6 operational data streams:
1. `customers.csv` — Firmographic and acquisition demographic profiles
2. `subscriptions.csv` — Billing plans, contract types, terms, MRR, and renewal flags
3. `customer_activity.csv` — High-frequency monthly product engagement telemetry
4. `support_tickets.csv` — Support desk tickets, resolution time, priority, and ticket CSAT
5. `payments.csv` — Transaction histories, payment gateways, and delinquency metrics
6. `customer_feedback.csv` — Net Promoter Score (NPS) surveys and qualitative verbatim"""))

nb1.cells.append(new_code_cell("""import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Display configuration
pd.set_option('display.max_columns', 25)
pd.set_option('display.max_rows', 50)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

DATA_DIR = '../data'
CLEAN_DIR = '../data/cleaned'
os.makedirs(CLEAN_DIR, exist_ok=True)

print("Libraries imported and paths configured.")"""))

nb1.cells.append(new_markdown_cell("""## 1. Data Ingestion & Shape Inspection"""))

nb1.cells.append(new_code_cell("""df_cust = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
df_subs = pd.read_csv(os.path.join(DATA_DIR, "subscriptions.csv"))
df_act = pd.read_csv(os.path.join(DATA_DIR, "customer_activity.csv"))
df_tickets = pd.read_csv(os.path.join(DATA_DIR, "support_tickets.csv"))
df_payments = pd.read_csv(os.path.join(DATA_DIR, "payments.csv"))
df_fb = pd.read_csv(os.path.join(DATA_DIR, "customer_feedback.csv"))

print(f"Customers shape:        {df_cust.shape}")
print(f"Subscriptions shape:    {df_subs.shape}")
print(f"Activity records shape: {df_act.shape}")
print(f"Support tickets shape:  {df_tickets.shape}")
print(f"Payments records shape: {df_payments.shape}")
print(f"Feedback records shape: {df_fb.shape}")"""))

nb1.cells.append(new_markdown_cell("""## 2. Customer Dimension: Deduplication & Text Normalization"""))

nb1.cells.append(new_code_cell("""# 1. Check duplicates
dup_cust_count = df_cust.duplicated(subset=['customer_id']).sum()
print(f"Duplicate customer records found: {dup_cust_count}")

# Remove duplicates
df_cust_clean = df_cust.drop_duplicates(subset=['customer_id']).copy()

# 2. Text Normalization: Fix mixed casing in customer_name
df_cust_clean['customer_name'] = df_cust_clean['customer_name'].astype(str).str.title().str.strip()

# 3. Missing Value Analysis
missing_cust = df_cust_clean.isnull().sum()
print("\nMissing values in Customers dimension:")
print(missing_cust[missing_cust > 0])

# Impute missing categorical values
df_cust_clean['city'] = df_cust_clean['city'].fillna('Unknown')
df_cust_clean['state'] = df_cust_clean['state'].fillna('Unknown')
df_cust_clean['acquisition_channel'] = df_cust_clean['acquisition_channel'].fillna('Direct/Unknown')

# Data Type Enforcement
df_cust_clean['signup_date'] = pd.to_datetime(df_cust_clean['signup_date'])
df_cust_clean['age'] = df_cust_clean['age'].astype(int)

print(f"\nCleaned Customers count: {len(df_cust_clean)}")
df_cust_clean.head(5)"""))

nb1.cells.append(new_markdown_cell("""## 3. Subscriptions Fact: Pricing, Dates & Contract Integrity"""))

nb1.cells.append(new_code_cell("""df_subs_clean = df_subs.copy()

# Verify missing subscription status or anomalies
print("Subscription status distribution:")
print(df_subs_clean['subscription_status'].value_counts())

# Date parsing
df_subs_clean['subscription_start_date'] = pd.to_datetime(df_subs_clean['subscription_start_date'])
df_subs_clean['subscription_end_date'] = pd.to_datetime(df_subs_clean['subscription_end_date'])

# Numeric types
df_subs_clean['monthly_fee'] = df_subs_clean['monthly_fee'].astype(float)
df_subs_clean['discount_percentage'] = df_subs_clean['discount_percentage'].astype(float)

# Validate logical consistency: End date must be greater than start date for churned users
invalid_dates = df_subs_clean[
    (df_subs_clean['subscription_end_date'].notnull()) & 
    (df_subs_clean['subscription_end_date'] < df_subs_clean['subscription_start_date'])
]
print(f"Inconsistent subscription date records: {len(invalid_dates)}")

df_subs_clean.head(5)"""))

nb1.cells.append(new_markdown_cell("""## 4. Support Tickets: Date Formatting & Outlier Remediation"""))

nb1.cells.append(new_code_cell("""df_tickets_clean = df_tickets.copy()

# Standardize mixed date strings
df_tickets_clean['ticket_date'] = pd.to_datetime(df_tickets_clean['ticket_date'], format='mixed')

# Outlier Analysis on resolution_time_hours
print("Resolution Time (Hours) Summary Statistics:")
print(df_tickets_clean['resolution_time_hours'].describe())

# Remediation of sensor/telemetry error (999.9 hours)
outlier_count = (df_tickets_clean['resolution_time_hours'] > 200).sum()
median_res = df_tickets_clean[df_tickets_clean['resolution_time_hours'] < 200]['resolution_time_hours'].median()
print(f"\nRemediating {outlier_count} resolution time outliers with category-median ({median_res:.1f} hours)...")

df_tickets_clean.loc[df_tickets_clean['resolution_time_hours'] > 200, 'resolution_time_hours'] = median_res
df_tickets_clean['satisfaction_score'] = df_tickets_clean['satisfaction_score'].astype(int)

df_tickets_clean.head(5)"""))

nb1.cells.append(new_markdown_cell("""## 5. Payments Fact: Negative Amounts & Extreme Outliers Treatment"""))

nb1.cells.append(new_code_cell("""df_payments_clean = df_payments.copy()

# Outlier & negative amount detection
print("Payment Amount Summary Statistics:")
print(df_payments_clean['amount'].describe())

# Fix negative values (erroneous sign reversals)
df_payments_clean['amount'] = df_payments_clean['amount'].abs()

# Cap unrealistic outlier payments (> $15,000) to standard enterprise annual max ($5,988)
outlier_pay = (df_payments_clean['amount'] > 15000).sum()
print(f"Remediating {outlier_pay} extreme payment anomalies...")
df_payments_clean.loc[df_payments_clean['amount'] > 15000, 'amount'] = 5988.0

df_payments_clean['payment_date'] = pd.to_datetime(df_payments_clean['payment_date'])
df_payments_clean['days_overdue'] = df_payments_clean['days_overdue'].astype(int)

print(f"Cleaned Payments count: {len(df_payments_clean)}")
df_payments_clean.head(5)"""))

nb1.cells.append(new_markdown_cell("""## 6. Feedback & Product Activity Cleansing"""))

nb1.cells.append(new_code_cell("""# 1. Product Activity
df_act_clean = df_act.copy()
df_act_clean['activity_month'] = pd.to_datetime(df_act_clean['activity_month'] + '-01')
for c in ['login_count', 'active_days', 'session_count', 'features_used', 'projects_created', 'files_uploaded', 'api_usage_count']:
    df_act_clean[c] = df_act_clean[c].astype(int)
df_act_clean['avg_session_minutes'] = df_act_clean['avg_session_minutes'].astype(float)

# 2. Feedback
df_fb_clean = df_fb.copy()
df_fb_clean['feedback_date'] = pd.to_datetime(df_fb_clean['feedback_date'])
df_fb_clean['nps_score'] = df_fb_clean['nps_score'].astype(int)
df_fb_clean['satisfaction_score'] = df_fb_clean['satisfaction_score'].astype(int)

print("Activity and Feedback cleaned successfully.")"""))

nb1.cells.append(new_markdown_cell("""## 7. Export Clean Datasets to Production Storage"""))

nb1.cells.append(new_code_cell("""# Export clean CSVs
df_cust_clean.to_csv(os.path.join(CLEAN_DIR, "customers_clean.csv"), index=False)
df_subs_clean.to_csv(os.path.join(CLEAN_DIR, "subscriptions_clean.csv"), index=False)
df_act_clean.to_csv(os.path.join(CLEAN_DIR, "customer_activity_clean.csv"), index=False)
df_tickets_clean.to_csv(os.path.join(CLEAN_DIR, "support_tickets_clean.csv"), index=False)
df_payments_clean.to_csv(os.path.join(CLEAN_DIR, "payments_clean.csv"), index=False)
df_fb_clean.to_csv(os.path.join(CLEAN_DIR, "customer_feedback_clean.csv"), index=False)

print("All 6 cleaned production datasets successfully written to data/cleaned/.")"""))

save_notebook(nb1, "01_data_cleaning.ipynb")


# ==============================================================================
# NOTEBOOK 2: 02_eda.ipynb
# ==============================================================================
nb2 = new_notebook()
nb2.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}

nb2.cells.append(new_markdown_cell("""# 📈 CloudSync SaaS Analytics: 02. Exploratory Data Analysis & Executive KPIs

**Author:** Antigravity Data Intelligence & Business Analytics Team  
**Dataset:** CloudSync SaaS Cleaned Multi-Table Repository  
**Objective:** Calculate foundational SaaS executive KPIs (MRR, ARR, ARPU, LTV, Churn Rate, Retention Rate), evaluate univariate/bivariate distributions, analyze cohort retention dynamics, and diagnose revenue loss drivers.

---

### Core SaaS KPI Formulas Implemented:
- $\\text{MRR} = \\sum \\text{monthly\\_fee}$ for all Active subscriptions
- $\\text{ARR} = \\text{MRR} \\times 12$
- $\\text{ARPU} = \\frac{\\text{MRR}}{\\text{Active Customers}}$
- $\\text{Customer Churn Rate (\\%)} = \\frac{\\text{Churned Customers}}{\\text{Total Customers}} \\times 100$
- $\\text{Customer Retention Rate (\\%)} = 100 - \\text{Churn Rate}$
- $\\text{Customer Lifetime Value (LTV)} = \\text{ARPU} \\times \\text{Average Active Tenure (Months)}$
- $\\text{Annualized Revenue Lost to Churn} = \\sum \\text{Churned Monthly Fees} \\times 12$"""))

nb2.cells.append(new_code_cell("""import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 300

CLEAN_DIR = '../data/cleaned'

df_cust = pd.read_csv(os.path.join(CLEAN_DIR, "customers_clean.csv"), parse_dates=['signup_date'])
df_subs = pd.read_csv(os.path.join(CLEAN_DIR, "subscriptions_clean.csv"), parse_dates=['subscription_start_date', 'subscription_end_date'])
df_act = pd.read_csv(os.path.join(CLEAN_DIR, "customer_activity_clean.csv"), parse_dates=['activity_month'])
df_tickets = pd.read_csv(os.path.join(CLEAN_DIR, "support_tickets_clean.csv"), parse_dates=['ticket_date'])
df_payments = pd.read_csv(os.path.join(CLEAN_DIR, "payments_clean.csv"), parse_dates=['payment_date'])
df_fb = pd.read_csv(os.path.join(CLEAN_DIR, "customer_feedback_clean.csv"), parse_dates=['feedback_date'])

# Unified analysis master
CURRENT_DT = pd.to_datetime("2024-12-31")
df_master = df_cust.merge(df_subs, on='customer_id', how='inner')
df_master['effective_end_date'] = df_master['subscription_end_date'].fillna(CURRENT_DT)
df_master['tenure_months'] = ((df_master['effective_end_date'] - df_master['subscription_start_date']).dt.days / 30.4).round(1)

print("Unified dataset ready for exploratory analysis.")"""))

nb2.cells.append(new_markdown_cell("""## 1. Executive SaaS KPI Scorecard Calculation"""))

nb2.cells.append(new_code_cell("""total_cust = len(df_cust)
active_cust = len(df_subs[df_subs['subscription_status'] == 'Active'])
churned_cust = len(df_subs[df_subs['subscription_status'] == 'Churned'])
paused_cust = len(df_subs[df_subs['subscription_status'] == 'Paused'])

churn_rate = (churned_cust / total_cust) * 100
retention_rate = ((total_cust - churned_cust) / total_cust) * 100

mrr = df_subs[df_subs['subscription_status'] == 'Active']['monthly_fee'].sum()
arr = mrr * 12
arpu = mrr / active_cust if active_cust > 0 else 0

avg_tenure = df_master['tenure_months'].mean()
avg_tenure_act = df_master[df_master['subscription_status'] == 'Active']['tenure_months'].mean()
avg_tenure_churn = df_master[df_master['subscription_status'] == 'Churned']['tenure_months'].mean()

cltv = arpu * avg_tenure_act
monthly_lost = df_subs[df_subs['subscription_status'] == 'Churned']['monthly_fee'].sum()
arr_lost = monthly_lost * 12

avg_nps = df_fb['nps_score'].mean()
avg_csat = df_fb['satisfaction_score'].mean()

kpi_summary = pd.DataFrame([
    {"KPI Metric": "Total Customers", "Value": f"{total_cust:,}"},
    {"KPI Metric": "Active Customers", "Value": f"{active_cust:,}"},
    {"KPI Metric": "Churned Customers", "Value": f"{churned_cust:,} ({churn_rate:.2f}%)"},
    {"KPI Metric": "Customer Retention Rate", "Value": f"{retention_rate:.2f}%"},
    {"KPI Metric": "Monthly Recurring Revenue (MRR)", "Value": f"${mrr:,.2f}"},
    {"KPI Metric": "Annual Recurring Revenue (ARR)", "Value": f"${arr:,.2f}"},
    {"KPI Metric": "Average Revenue Per User (ARPU)", "Value": f"${arpu:.2f}"},
    {"KPI Metric": "Customer Lifetime Value (LTV)", "Value": f"${cltv:,.2f}"},
    {"KPI Metric": "Average Active Customer Tenure", "Value": f"{avg_tenure_act:.1f} months"},
    {"KPI Metric": "Average Churned Customer Tenure", "Value": f"{avg_tenure_churn:.1f} months"},
    {"KPI Metric": "Monthly Revenue Lost to Churn", "Value": f"${monthly_lost:,.2f}"},
    {"KPI Metric": "Annualized Revenue Lost to Churn", "Value": f"${arr_lost:,.2f}"},
    {"KPI Metric": "Average Net Promoter Score (NPS)", "Value": f"{avg_nps:.2f} / 10"},
    {"KPI Metric": "Average Customer Satisfaction (CSAT)", "Value": f"{avg_csat:.2f} / 5"}
])

kpi_summary"""))

nb2.cells.append(new_markdown_cell("""## 2. Churn Breakdown by Business Dimension"""))

nb2.cells.append(new_code_cell("""# 1. Churn by Contract Type
churn_contract = df_master.groupby('contract_type').agg(
    total_users=('customer_id', 'count'),
    churned_users=('subscription_status', lambda x: (x == 'Churned').sum()),
    churn_rate=('subscription_status', lambda x: (x == 'Churned').mean() * 100)
).reset_index()

# 2. Churn by Subscription Plan
churn_plan = df_master.groupby('plan_name').agg(
    total_users=('customer_id', 'count'),
    churned_users=('subscription_status', lambda x: (x == 'Churned').sum()),
    churn_rate=('subscription_status', lambda x: (x == 'Churned').mean() * 100)
).reset_index()

# 3. Churn by Customer Segment
churn_seg = df_master.groupby('customer_segment').agg(
    total_users=('customer_id', 'count'),
    churned_users=('subscription_status', lambda x: (x == 'Churned').sum()),
    churn_rate=('subscription_status', lambda x: (x == 'Churned').mean() * 100)
).reset_index()

print("--- Churn by Contract Type ---")
display(churn_contract)
print("\n--- Churn by Plan ---")
display(churn_plan)
print("\n--- Churn by Segment ---")
display(churn_seg)"""))

nb2.cells.append(new_markdown_cell("""## 3. Visualizing Core SaaS Relationships"""))

nb2.cells.append(new_code_cell("""fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Churn by Contract Type Bar Chart
sns.barplot(data=churn_contract, x='contract_type', y='churn_rate', ax=axes[0, 0], color='#2c7bb6')
axes[0, 0].set_title('Churn Rate by Contract Type (%)', fontweight='bold', fontsize=12)
axes[0, 0].set_ylabel('Churn Rate (%)')
for p in axes[0, 0].patches:
    axes[0, 0].annotate(f"{p.get_height():.1f}%", (p.get_x() + p.get_width() / 2., p.get_height() + 0.8), ha='center', fontweight='bold')

# 2. Churn by Plan
sns.barplot(data=churn_plan, x='plan_name', y='churn_rate', ax=axes[0, 1], color='#8e44ad', order=['Basic', 'Professional', 'Business', 'Enterprise'])
axes[0, 1].set_title('Churn Rate by Plan Tier (%)', fontweight='bold', fontsize=12)
axes[0, 1].set_ylabel('Churn Rate (%)')
for p in axes[0, 1].patches:
    axes[0, 1].annotate(f"{p.get_height():.1f}%", (p.get_x() + p.get_width() / 2., p.get_height() + 0.8), ha='center', fontweight='bold')

# 3. Churn by Acquisition Channel
chan_churn = df_master.groupby('acquisition_channel')['subscription_status'].apply(lambda x: (x == 'Churned').mean() * 100).sort_values(ascending=False).reset_index()
sns.barplot(data=chan_churn, x='subscription_status', y='acquisition_channel', ax=axes[1, 0], color='#e67e22')
axes[1, 0].set_title('Churn Rate by Acquisition Channel (%)', fontweight='bold', fontsize=12)
axes[1, 0].set_xlabel('Churn Rate (%)')

# 4. Tenure KDE
sns.kdeplot(data=df_master[df_master['subscription_status']=='Active']['tenure_months'], label='Active Users', shade=True, color='#27ae60', ax=axes[1, 1])
sns.kdeplot(data=df_master[df_master['subscription_status']=='Churned']['tenure_months'], label='Churned Users', shade=True, color='#e74c3c', ax=axes[1, 1])
axes[1, 1].set_title('Customer Tenure Density (Months)', fontweight='bold', fontsize=12)
axes[1, 1].set_xlabel('Tenure (Months)')
axes[1, 1].legend()

plt.tight_layout()
plt.show()"""))

nb2.cells.append(new_markdown_cell("""## 4. Cohort Retention Matrix Analysis"""))

nb2.cells.append(new_code_cell("""df_master['cohort_quarter'] = df_master['subscription_start_date'].dt.to_period('Q').astype(str)
cohort_pivot = df_master.groupby(['cohort_quarter', 'subscription_status'])['customer_id'].count().unstack(fill_value=0)
cohort_pivot['Total'] = cohort_pivot.sum(axis=1)
cohort_pivot['Retention_Rate_%'] = (cohort_pivot.get('Active', 0) / cohort_pivot['Total'] * 100).round(2)
cohort_pivot['Churn_Rate_%'] = (cohort_pivot.get('Churned', 0) / cohort_pivot['Total'] * 100).round(2)

display(cohort_pivot[['Total', 'Active', 'Churned', 'Retention_Rate_%', 'Churn_Rate_%']])"""))

save_notebook(nb2, "02_eda.ipynb")


# ==============================================================================
# NOTEBOOK 3: 03_customer_segmentation.ipynb
# ==============================================================================
nb3 = new_notebook()
nb3.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}

nb3.cells.append(new_markdown_cell("""# 🎯 CloudSync SaaS Analytics: 03. Customer Segmentation & Health Scoring

**Author:** Antigravity Data Intelligence & Business Analytics Team  
**Dataset:** CloudSync Enriched Master Profile  
**Objective:** Construct RFM (Recency, Frequency, Monetary) quintile scoring, engineer a multi-factor SaaS Customer Health Score (0–100), define strategic business value segments, and perform K-Means unsupervised behavioral clustering.

---

### Customer Health Score Design Architecture
The CloudSync Health Score evaluates account vitality across 5 weighted business pillars:
1. **Product Engagement (35%)**: Monthly login frequency, active days per month, and breadth of feature utilization.
2. **Satisfaction & Advocacy (25%)**: Net Promoter Score (NPS) and CSAT survey ratings.
3. **Payment Reliability (15%)**: Payment gateway success rate and penalty on payment failures/delinquency.
4. **Support Ticket Friction (15%)**: Resolution velocity and penalty on unresolved/escalated tickets.
5. **Account Tenure (10%)**: Length of subscription tenure stability."""))

nb3.cells.append(new_code_cell("""import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 300

CLEAN_DIR = '../data/cleaned'
df_master = pd.read_csv(os.path.join(CLEAN_DIR, "customer_churn_master.csv"))

print(f"Master feature dataset loaded with {len(df_master)} records.")"""))

nb3.cells.append(new_markdown_cell("""## 1. RFM Score Distribution & Quantile Scoring"""))

nb3.cells.append(new_code_cell("""# RFM Summary
print("RFM Scores Summary:")
display(df_master[['recency_months', 'avg_monthly_logins', 'total_paid', 'R_Score', 'F_Score', 'M_Score', 'RFM_Score']].describe())

# Distribution of R, F, M Scores
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
sns.countplot(x='R_Score', data=df_master, ax=axes[0], palette='Blues')
axes[0].set_title('Recency Score Distribution (5 = Most Recent)', fontweight='bold')
sns.countplot(x='F_Score', data=df_master, ax=axes[1], palette='Greens')
axes[1].set_title('Frequency Score Distribution (5 = Highest Logins)', fontweight='bold')
sns.countplot(x='M_Score', data=df_master, ax=axes[2], palette='Purples')
axes[2].set_title('Monetary Score Distribution (5 = Highest Spend)', fontweight='bold')
plt.tight_layout()
plt.show()"""))

nb3.cells.append(new_markdown_cell("""## 2. Customer Health Score Validation & Segment Breakdown"""))

nb3.cells.append(new_code_cell("""print("Customer Health Score Summary Statistics:")
display(df_master['health_score'].describe())

print("\nStrategic Customer Health Segments:")
display(df_master['customer_health_segment'].value_counts())

# Health Score across Segments
fig, ax = plt.subplots(figsize=(12, 6))
sns.boxplot(data=df_master, x='customer_health_segment', y='health_score', palette='tab10', ax=ax)
ax.set_title('Customer Health Score Distribution by Strategic Segment', fontsize=13, fontweight='bold')
ax.set_ylabel('Health Score (0-100)')
plt.xticks(rotation=20)
plt.tight_layout()
plt.show()"""))

nb3.cells.append(new_markdown_cell("""## 3. High-Value At-Risk Account Identification"""))

nb3.cells.append(new_code_cell("""# Filter high-value customers at high risk
high_val_risk = df_master[df_master['customer_health_segment'] == 'High Value – High Risk'].copy()
print(f"Total High Value - High Risk accounts identified: {len(high_val_risk)}")
print(f"Total Monthly MRR at immediate risk: ${high_val_risk['monthly_fee'].sum():,.2f}")
print(f"Annualized MRR at risk: ${high_val_risk['monthly_fee'].sum() * 12:,.2f}")

display(high_val_risk[['customer_id', 'customer_name', 'plan_name', 'monthly_fee', 'health_score', 'avg_monthly_logins', 'failed_payments', 'unresolved_tickets', 'nps_score']].head(10))"""))

nb3.cells.append(new_markdown_cell("""## 4. Unsupervised K-Means Behavioral Clustering"""))

nb3.cells.append(new_code_cell("""cluster_features = ['avg_monthly_logins', 'avg_session_mins', 'avg_features_used', 'failed_payments', 'nps_score', 'monthly_fee']
X_cluster = df_master[cluster_features].copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_cluster)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df_master['cluster_id'] = kmeans.fit_predict(X_scaled)

cluster_profile = df_master.groupby('cluster_id')[cluster_features + ['health_score', 'churn_probability']].mean().round(2)
cluster_profile['Account_Count'] = df_master.groupby('cluster_id')['customer_id'].count()

print("K-Means Behavioral Cluster Profiles:")
display(cluster_profile)"""))

save_notebook(nb3, "03_customer_segmentation.ipynb")


# ==============================================================================
# NOTEBOOK 4: 04_churn_analysis.ipynb
# ==============================================================================
nb4 = new_notebook()
nb4.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}

nb4.cells.append(new_markdown_cell("""# 🤖 CloudSync SaaS Analytics: 04. Churn Risk Modeling & Decision Intelligence

**Author:** Antigravity Data Intelligence & Business Analytics Team  
**Dataset:** CloudSync Master Customer Profile  
**Objective:** Develop interpretable machine learning models (Logistic Regression baseline vs. Random Forest Classifier) to estimate customer-level churn probabilities, evaluate feature importance / odds ratios, stratify risk categories, and establish targeted retention triggers.

---

### Methodological Guardrails:
- **No Data Leakage**: We isolate features that precede churn events and apply `ColumnTransformer` / `Pipeline` structures strictly fitted on the training split.
- **Interpretable Risk Stratification**:
  - 🟢 **Low Risk**: $\\text{Predicted Churn Probability} < 0.35$
  - 🟡 **Medium Risk**: $0.35 \\le \\text{Predicted Churn Probability} < 0.70$
  - 🔴 **High Risk**: $\\text{Predicted Churn Probability} \\ge 0.70$"""))

nb4.cells.append(new_code_cell("""import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report
)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 300

CLEAN_DIR = '../data/cleaned'
df = pd.read_csv(os.path.join(CLEAN_DIR, "customer_churn_master.csv"))

print(f"Master dataset loaded with {len(df)} records.")"""))

nb4.cells.append(new_markdown_cell("""## 1. Feature Definition & Train/Test Partition"""))

nb4.cells.append(new_code_cell("""df['target_churn'] = (df['subscription_status'] == 'Churned').astype(int)

feature_cols_num = [
    'tenure_months', 'monthly_fee', 'discount_percentage',
    'avg_monthly_logins', 'avg_active_days', 'avg_session_mins',
    'avg_features_used', 'ticket_count', 'unresolved_tickets',
    'failed_payments', 'nps_score', 'feedback_csat'
]
feature_cols_cat = ['contract_type', 'plan_name', 'customer_segment', 'acquisition_channel', 'auto_renew']

X = df[feature_cols_num + feature_cols_cat]
y = df['target_churn']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Testing set:  {X_test.shape[0]} samples")
print(f"Baseline Churn Rate in Train: {y_train.mean()*100:.2f}%")"""))

nb4.cells.append(new_markdown_cell("""## 2. Model Training: Logistic Regression Baseline & Random Forest"""))

nb4.cells.append(new_code_cell("""preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), feature_cols_num),
        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), feature_cols_cat)
    ]
)

# 1. Logistic Regression
lr_pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=1000, random_state=42, C=1.0))
])
lr_pipe.fit(X_train, y_train)

# 2. Random Forest
rf_pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=150, max_depth=10, min_samples_leaf=5, random_state=42))
])
rf_pipe.fit(X_train, y_train)

print("Both models trained successfully.")"""))

nb4.cells.append(new_markdown_cell("""## 3. Comprehensive Performance Benchmark & ROC-AUC"""))

nb4.cells.append(new_code_cell("""y_pred_lr = lr_pipe.predict(X_test)
y_prob_lr = lr_pipe.predict_proba(X_test)[:, 1]

y_pred_rf = rf_pipe.predict(X_test)
y_prob_rf = rf_pipe.predict_proba(X_test)[:, 1]

results = pd.DataFrame({
    'Model': ['Logistic Regression', 'Random Forest Classifier'],
    'Accuracy': [accuracy_score(y_test, y_pred_lr), accuracy_score(y_test, y_pred_rf)],
    'Precision': [precision_score(y_test, y_pred_lr), precision_score(y_test, y_pred_rf)],
    'Recall': [recall_score(y_test, y_pred_lr), recall_score(y_test, y_pred_rf)],
    'F1 Score': [f1_score(y_test, y_pred_lr), f1_score(y_test, y_pred_rf)],
    'ROC-AUC': [roc_auc_score(y_test, y_prob_lr), roc_auc_score(y_test, y_prob_rf)]
})

display(results.round(4))"""))

nb4.cells.append(new_markdown_cell("""## 4. Confusion Matrix & ROC Curves Visualizations"""))

nb4.cells.append(new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# ROC Curves
fpr_lr, tpr_lr, _ = roc_curve(y_test, y_prob_lr)
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_prob_rf)

axes[0].plot(fpr_lr, tpr_lr, label=f"Logistic Regression (AUC = {roc_auc_score(y_test, y_prob_lr):.3f})", color='#e67e22', lw=2)
axes[0].plot(fpr_rf, tpr_rf, label=f"Random Forest (AUC = {roc_auc_score(y_test, y_prob_rf):.3f})", color='#2980b9', lw=2)
axes[0].plot([0, 1], [0, 1], 'k--', lw=1.2)
axes[0].set_title("ROC Curves Comparison", fontweight='bold', fontsize=12)
axes[0].set_xlabel("False Positive Rate")
axes[0].set_ylabel("True Positive Rate")
axes[0].legend(loc='lower right')

# Confusion Matrix RF
cm = confusion_matrix(y_test, y_pred_rf)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=axes[1],
            xticklabels=['Retained', 'Churned'], yticklabels=['Retained', 'Churned'])
axes[1].set_title("Confusion Matrix (Random Forest)", fontweight='bold', fontsize=12)
axes[1].set_xlabel("Predicted Label")
axes[1].set_ylabel("Actual Label")

plt.tight_layout()
plt.show()"""))

nb4.cells.append(new_markdown_cell("""## 5. Interpretability: Feature Importance & Odds Ratios"""))

nb4.cells.append(new_code_cell("""cat_encoder = lr_pipe.named_steps['preprocessor'].named_transformers_['cat']
cat_feature_names = list(cat_encoder.get_feature_names_out(feature_cols_cat))
all_features = feature_cols_num + cat_feature_names

# Logistic Regression Odds Ratios
df_coefs = pd.DataFrame({
    'Feature': all_features,
    'Log_Odds_Coef': lr_pipe.named_steps['classifier'].coef_[0],
    'Odds_Ratio': np.exp(lr_pipe.named_steps['classifier'].coef_[0])
}).sort_values(by='Log_Odds_Coef', ascending=False)

print("Top 5 Factors Increasing Churn Odds:")
display(df_coefs.head(5))

print("\nTop 5 Protective Factors Reducing Churn Odds:")
display(df_coefs.tail(5))"""))

nb4.cells.append(new_markdown_cell("""## 6. Actionable Risk Table: High-Risk Customers for Retention Intervention"""))

nb4.cells.append(new_code_cell("""# Identify Active High Risk Accounts
at_risk_active = df[(df['subscription_status'] == 'Active') & (df['risk_category'] == 'High Risk')].sort_values(by='monthly_fee', ascending=False)

print(f"Total Active High-Risk Customers: {len(at_risk_active):,}")
print(f"Total Active MRR at Immediate Risk: ${at_risk_active['monthly_fee'].sum():,.2f}")

display(at_risk_active[['customer_id', 'customer_name', 'plan_name', 'contract_type', 'monthly_fee', 'tenure_months', 'avg_monthly_logins', 'failed_payments', 'unresolved_tickets', 'churn_probability', 'risk_category']].head(15))"""))

save_notebook(nb4, "04_churn_analysis.ipynb")
print("All 4 notebooks successfully built!")
