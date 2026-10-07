import os
import sqlite3
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
    roc_auc_score, roc_curve, confusion_matrix
)
from sklearn.cluster import KMeans

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CLEAN_DIR = os.path.join(DATA_DIR, 'cleaned')
NB_DIR = os.path.join(BASE_DIR, 'notebooks')
SCREENSHOTS_DIR = os.path.join(BASE_DIR, 'screenshots')

os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(NB_DIR, exist_ok=True)

print("--- STEP 1: DATA CLEANING ---")

# Load raw datasets
df_cust = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
df_subs = pd.read_csv(os.path.join(DATA_DIR, "subscriptions.csv"))
df_act = pd.read_csv(os.path.join(DATA_DIR, "customer_activity.csv"))
df_tickets = pd.read_csv(os.path.join(DATA_DIR, "support_tickets.csv"))
df_payments = pd.read_csv(os.path.join(DATA_DIR, "payments.csv"))
df_fb = pd.read_csv(os.path.join(DATA_DIR, "customer_feedback.csv"))

print(f"Raw Customers shape: {df_cust.shape}")

# 1. Clean Customers
# Remove duplicates
dup_count = df_cust.duplicated(subset=['customer_id']).sum()
df_cust_clean = df_cust.drop_duplicates(subset=['customer_id']).copy()

# Standardize casing in customer_name
df_cust_clean['customer_name'] = df_cust_clean['customer_name'].astype(str).str.title()

# Handle missing values
df_cust_clean['city'] = df_cust_clean['city'].fillna('Unknown')
df_cust_clean['state'] = df_cust_clean['state'].fillna('Unknown')
df_cust_clean['acquisition_channel'] = df_cust_clean['acquisition_channel'].fillna('Direct/Unknown')

# Data types
df_cust_clean['signup_date'] = pd.to_datetime(df_cust_clean['signup_date'])
df_cust_clean['age'] = df_cust_clean['age'].astype(int)

# 2. Clean Subscriptions
df_subs_clean = df_subs.copy()
df_subs_clean['subscription_start_date'] = pd.to_datetime(df_subs_clean['subscription_start_date'])
df_subs_clean['subscription_end_date'] = pd.to_datetime(df_subs_clean['subscription_end_date'])
df_subs_clean['monthly_fee'] = df_subs_clean['monthly_fee'].astype(float)
df_subs_clean['discount_percentage'] = df_subs_clean['discount_percentage'].astype(float)

# 3. Clean Activity
df_act_clean = df_act.copy()
df_act_clean['activity_month'] = pd.to_datetime(df_act_clean['activity_month'] + '-01')
for col in ['login_count', 'active_days', 'session_count', 'features_used', 'projects_created', 'files_uploaded', 'api_usage_count']:
    df_act_clean[col] = df_act_clean[col].astype(int)
df_act_clean['avg_session_minutes'] = df_act_clean['avg_session_minutes'].astype(float)

# 4. Clean Support Tickets
df_tickets_clean = df_tickets.copy()
# Parse diverse date formats
df_tickets_clean['ticket_date'] = pd.to_datetime(df_tickets_clean['ticket_date'], format='mixed')
# Treat resolution time outliers (e.g. 999.9 anomaly)
median_res_time = df_tickets_clean[df_tickets_clean['resolution_time_hours'] < 200]['resolution_time_hours'].median()
df_tickets_clean.loc[df_tickets_clean['resolution_time_hours'] > 200, 'resolution_time_hours'] = median_res_time
df_tickets_clean['satisfaction_score'] = df_tickets_clean['satisfaction_score'].astype(int)

# 5. Clean Payments
df_payments_clean = df_payments.copy()
df_payments_clean['payment_date'] = pd.to_datetime(df_payments_clean['payment_date'])
# Clean negative and extreme outlier amounts
df_payments_clean['amount'] = df_payments_clean['amount'].abs()
# Cap amounts above 20,000 (typical enterprise annual is <$6,000)
df_payments_clean.loc[df_payments_clean['amount'] > 15000, 'amount'] = 5988.0 # $499*12
df_payments_clean['days_overdue'] = df_payments_clean['days_overdue'].astype(int)

# 6. Clean Feedback
df_fb_clean = df_fb.copy()
df_fb_clean['feedback_date'] = pd.to_datetime(df_fb_clean['feedback_date'])
df_fb_clean['nps_score'] = df_fb_clean['nps_score'].astype(int)
df_fb_clean['satisfaction_score'] = df_fb_clean['satisfaction_score'].astype(int)

# Save Clean Datasets
df_cust_clean.to_csv(os.path.join(CLEAN_DIR, "customers_clean.csv"), index=False)
df_subs_clean.to_csv(os.path.join(CLEAN_DIR, "subscriptions_clean.csv"), index=False)
df_act_clean.to_csv(os.path.join(CLEAN_DIR, "customer_activity_clean.csv"), index=False)
df_tickets_clean.to_csv(os.path.join(CLEAN_DIR, "support_tickets_clean.csv"), index=False)
df_payments_clean.to_csv(os.path.join(CLEAN_DIR, "payments_clean.csv"), index=False)
df_fb_clean.to_csv(os.path.join(CLEAN_DIR, "customer_feedback_clean.csv"), index=False)

print(f"Cleaned datasets saved. Unique clean customers: {len(df_cust_clean)}")

# Create SQLite DB for SQL queries verification
DB_PATH = os.path.join(DATA_DIR, "cloudsync.db")
conn = sqlite3.connect(DB_PATH)
df_cust_clean.to_sql("customers", conn, if_exists="replace", index=False)
df_subs_clean.to_sql("subscriptions", conn, if_exists="replace", index=False)
df_act_clean.to_sql("customer_activity", conn, if_exists="replace", index=False)
df_tickets_clean.to_sql("support_tickets", conn, if_exists="replace", index=False)
df_payments_clean.to_sql("payments", conn, if_exists="replace", index=False)
df_fb_clean.to_sql("customer_feedback", conn, if_exists="replace", index=False)
conn.close()
print("SQLite database created at data/cloudsync.db")

print("\n--- STEP 2: KPI CALCULATION & EDA ---")

total_customers = len(df_cust_clean)
active_customers = len(df_subs_clean[df_subs_clean['subscription_status'] == 'Active'])
churned_customers = len(df_subs_clean[df_subs_clean['subscription_status'] == 'Churned'])
paused_customers = len(df_subs_clean[df_subs_clean['subscription_status'] == 'Paused'])
overall_churn_rate = (churned_customers / total_customers) * 100
retention_rate = ((total_customers - churned_customers) / total_customers) * 100

mrr = df_subs_clean[df_subs_clean['subscription_status'] == 'Active']['monthly_fee'].sum()
arr = mrr * 12
arpu = mrr / active_customers if active_customers > 0 else 0

# Tenure calculation in months
CURRENT_DT = pd.to_datetime("2024-12-31")
df_merged = df_cust_clean.merge(df_subs_clean, on='customer_id', how='inner')
df_merged['effective_end_date'] = df_merged['subscription_end_date'].fillna(CURRENT_DT)
df_merged['tenure_months'] = ((df_merged['effective_end_date'] - df_merged['subscription_start_date']).dt.days / 30.4).round(1)
avg_tenure = df_merged['tenure_months'].mean()
avg_tenure_active = df_merged[df_merged['subscription_status'] == 'Active']['tenure_months'].mean()
avg_tenure_churned = df_merged[df_merged['subscription_status'] == 'Churned']['tenure_months'].mean()

revenue_lost_monthly = df_subs_clean[df_subs_clean['subscription_status'] == 'Churned']['monthly_fee'].sum()
revenue_lost_annual = revenue_lost_monthly * 12
avg_monthly_rev = df_subs_clean['monthly_fee'].mean()

# Customer Lifetime Value (CLTV = ARPU * Avg Customer Lifespan in months)
cltv = arpu * avg_tenure_active

avg_nps = df_fb_clean['nps_score'].mean()
avg_csat = df_fb_clean['satisfaction_score'].mean()

print(f"=== CLOUDSYNC CORE SAAS KPIS ===")
print(f"Total Customers: {total_customers:,}")
print(f"Active Customers: {active_customers:,}")
print(f"Churned Customers: {churned_customers:,} ({overall_churn_rate:.2f}%)")
print(f"Retention Rate: {retention_rate:.2f}%")
print(f"Monthly Recurring Revenue (MRR): ${mrr:,.2f}")
print(f"Annual Recurring Revenue (ARR): ${arr:,.2f}")
print(f"Average Revenue Per User (ARPU): ${arpu:.2f}")
print(f"Customer Lifetime Value (LTV): ${cltv:,.2f}")
print(f"Average Tenure: {avg_tenure:.1f} months (Active: {avg_tenure_active:.1f} mo, Churned: {avg_tenure_churned:.1f} mo)")
print(f"Monthly Revenue Lost to Churn: ${revenue_lost_monthly:,.2f}")
print(f"Annualized Revenue Lost to Churn: ${revenue_lost_annual:,.2f}")
print(f"Average NPS: {avg_nps:.2f} / 10")
print(f"Average CSAT: {avg_csat:.2f} / 5")

# Generate High Quality Visualizations for Portfolio / Reports
# 1. Executive Churn & Revenue Overview Dashboard
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("CloudSync Executive SaaS Overview & Churn Dynamics", fontsize=18, fontweight='bold', y=0.98)

# Churn by Contract Type
contract_churn = df_merged.groupby('contract_type')['subscription_status'].apply(lambda x: (x == 'Churned').mean() * 100)
sns.barplot(x=contract_churn.index, y=contract_churn.values, ax=axes[0, 0], color='#2b5c8f')
axes[0, 0].set_title("Churn Rate by Contract Type (%)", fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel("Churn Rate (%)")
for i, v in enumerate(contract_churn.values):
    axes[0, 0].text(i, v + 0.8, f"{v:.1f}%", ha='center', fontweight='bold')

# Churn by Plan
plan_churn = df_merged.groupby('plan_name')['subscription_status'].apply(lambda x: (x == 'Churned').mean() * 100).reindex(['Basic', 'Professional', 'Business', 'Enterprise'])
sns.barplot(x=plan_churn.index, y=plan_churn.values, ax=axes[0, 1], color='#6b486b')
axes[0, 1].set_title("Churn Rate by Subscription Plan (%)", fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel("Churn Rate (%)")
for i, v in enumerate(plan_churn.values):
    axes[0, 1].text(i, v + 0.8, f"{v:.1f}%", ha='center', fontweight='bold')

# Churn by Customer Segment
seg_churn = df_merged.groupby('customer_segment')['subscription_status'].apply(lambda x: (x == 'Churned').mean() * 100)
sns.barplot(x=seg_churn.index, y=seg_churn.values, ax=axes[0, 2], color='#1b9e77')
axes[0, 2].set_title("Churn Rate by Customer Segment (%)", fontsize=12, fontweight='bold')
axes[0, 2].set_ylabel("Churn Rate (%)")
for i, v in enumerate(seg_churn.values):
    axes[0, 2].text(i, v + 0.8, f"{v:.1f}%", ha='center', fontweight='bold')

# Revenue Contribution by Segment
seg_rev = df_merged[df_merged['subscription_status'] == 'Active'].groupby('customer_segment')['monthly_fee'].sum()
axes[1, 0].pie(seg_rev.values, labels=seg_rev.index, autopct='%1.1f%%', colors=['#4A90E2', '#50E3C2', '#B8E986'], startangle=140, explode=(0.02, 0.02, 0.05))
axes[1, 0].set_title("Active MRR Distribution by Segment", fontsize=12, fontweight='bold')

# Churn by Acquisition Channel
chan_churn = df_merged.groupby('acquisition_channel')['subscription_status'].apply(lambda x: (x == 'Churned').mean() * 100).sort_values()
sns.barplot(x=chan_churn.values, y=chan_churn.index, ax=axes[1, 1], color='#d95f02')
axes[1, 1].set_title("Churn Rate by Acquisition Channel (%)", fontsize=12, fontweight='bold')
axes[1, 1].set_xlabel("Churn Rate (%)")

# Tenure Distribution Churned vs Active
sns.histplot(data=df_merged, x='tenure_months', hue='subscription_status', kde=True, ax=axes[1, 2], palette={'Active': '#2ecc71', 'Churned': '#e74c3c', 'Paused': '#f39c12'}, bins=25)
axes[1, 2].set_title("Customer Tenure Distribution (Months)", fontsize=12, fontweight='bold')
axes[1, 2].set_xlabel("Tenure (Months)")

plt.tight_layout()
fig.savefig(os.path.join(SCREENSHOTS_DIR, "01_executive_overview.png"), bbox_inches='tight')
plt.close(fig)

print("Saved screenshots/01_executive_overview.png")

# 2. Monthly Cohort Retention Analysis
df_merged['signup_cohort'] = df_merged['subscription_start_date'].dt.to_period('Q').astype(str)
cohort_sizes = df_merged.groupby('signup_cohort')['customer_id'].nunique()
cohort_status = df_merged.groupby(['signup_cohort', 'subscription_status'])['customer_id'].nunique().unstack(fill_value=0)
cohort_retention = (cohort_status.get('Active', 0) / cohort_sizes * 100).round(1)

fig, ax = plt.subplots(figsize=(12, 5))
cohort_retention.plot(kind='bar', color='#3498db', ax=ax, edgecolor='black', alpha=0.85)
ax.set_title("Active Customer Retention Rate by Signup Cohort Quarter (%)", fontsize=14, fontweight='bold')
ax.set_ylabel("Retention Rate (%)")
ax.set_xlabel("Signup Cohort")
for i, v in enumerate(cohort_retention):
    ax.text(i, v + 1.0, f"{v:.1f}%", ha='center', fontweight='bold', fontsize=10)
plt.xticks(rotation=45)
plt.tight_layout()
fig.savefig(os.path.join(SCREENSHOTS_DIR, "02_cohort_retention.png"), bbox_inches='tight')
plt.close(fig)

print("Saved screenshots/02_cohort_retention.png")

print("\n--- STEP 3: CUSTOMER SEGMENTATION & HEALTH SCORE ---")

# Build Aggregate Customer Metrics
# Recency: Months since last activity
# Frequency: Total login sessions across history
# Monetary: Total revenue paid to date
pay_agg = df_payments_clean[df_payments_clean['payment_status'] == 'Successful'].groupby('customer_id').agg(
    total_paid=('amount', 'sum'),
    successful_payments=('payment_id', 'count')
).reset_index()

pay_fail_agg = df_payments_clean[df_payments_clean['payment_status'] == 'Failed'].groupby('customer_id').agg(
    failed_payments=('payment_id', 'count')
).reset_index()

act_agg = df_act_clean.groupby('customer_id').agg(
    total_logins=('login_count', 'sum'),
    avg_monthly_logins=('login_count', 'mean'),
    avg_active_days=('active_days', 'mean'),
    avg_session_mins=('avg_session_minutes', 'mean'),
    avg_features_used=('features_used', 'mean'),
    total_files_uploaded=('files_uploaded', 'sum'),
    total_projects=('projects_created', 'sum'),
    latest_activity_month=('activity_month', 'max')
).reset_index()

tck_agg = df_tickets_clean.groupby('customer_id').agg(
    ticket_count=('ticket_id', 'count'),
    unresolved_tickets=('ticket_status', lambda x: (x.isin(['Pending', 'Escalated'])).sum()),
    avg_resolution_hours=('resolution_time_hours', 'mean'),
    avg_ticket_sat=('satisfaction_score', 'mean')
).reset_index()

fb_agg = df_fb_clean.groupby('customer_id').agg(
    nps_score=('nps_score', 'mean'),
    feedback_csat=('satisfaction_score', 'mean')
).reset_index()

df_features = df_merged.merge(pay_agg, on='customer_id', how='left')
df_features = df_features.merge(pay_fail_agg, on='customer_id', how='left')
df_features = df_features.merge(act_agg, on='customer_id', how='left')
df_features = df_features.merge(tck_agg, on='customer_id', how='left')
df_features = df_features.merge(fb_agg, on='customer_id', how='left')

# Fill NAs
df_features['total_paid'] = df_features['total_paid'].fillna(df_features['monthly_fee'])
df_features['successful_payments'] = df_features['successful_payments'].fillna(1)
df_features['failed_payments'] = df_features['failed_payments'].fillna(0)
df_features['total_logins'] = df_features['total_logins'].fillna(5)
df_features['avg_monthly_logins'] = df_features['avg_monthly_logins'].fillna(5)
df_features['avg_active_days'] = df_features['avg_active_days'].fillna(4)
df_features['avg_session_mins'] = df_features['avg_session_mins'].fillna(15)
df_features['avg_features_used'] = df_features['avg_features_used'].fillna(2)
df_features['total_files_uploaded'] = df_features['total_files_uploaded'].fillna(0)
df_features['total_projects'] = df_features['total_projects'].fillna(0)
df_features['ticket_count'] = df_features['ticket_count'].fillna(0)
df_features['unresolved_tickets'] = df_features['unresolved_tickets'].fillna(0)
df_features['avg_resolution_hours'] = df_features['avg_resolution_hours'].fillna(15.0)
df_features['avg_ticket_sat'] = df_features['avg_ticket_sat'].fillna(3.5)
df_features['nps_score'] = df_features['nps_score'].fillna(df_features['nps_score'].median())
df_features['feedback_csat'] = df_features['feedback_csat'].fillna(df_features['feedback_csat'].median())

# Calculate Recency in months from CURRENT_DT
df_features['recency_months'] = ((CURRENT_DT - df_features['latest_activity_month']).dt.days / 30.4).fillna(1.0).round(1)

# RFM Scoring
# Recency: Lower is better (1-5)
df_features['R_Score'] = pd.qcut(df_features['recency_months'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1]).astype(int)
# Frequency: Higher logins is better (1-5)
df_features['F_Score'] = pd.qcut(df_features['avg_monthly_logins'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
# Monetary: Higher total paid is better (1-5)
df_features['M_Score'] = pd.qcut(df_features['total_paid'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
df_features['RFM_Score'] = df_features['R_Score'].astype(str) + df_features['F_Score'].astype(str) + df_features['M_Score'].astype(str)

# Customer Health Score (0 - 100)
# Formula components:
# 1. Engagement (Logins + Active Days + Features): 35%
# 2. NPS & CSAT: 25%
# 3. Payment Reliability (No Failed Payments): 15%
# 4. Support Experience (Low unresolved & fast resolution): 15%
# 5. Tenure Stability: 10%

norm_eng = np.clip(df_features['avg_monthly_logins'] / 40.0 * 100, 0, 100)
norm_sat = (df_features['nps_score'] / 10.0 * 50 + df_features['feedback_csat'] / 5.0 * 50)
norm_pay = np.clip(100 - df_features['failed_payments'] * 35, 0, 100)
norm_supp = np.clip(100 - df_features['unresolved_tickets'] * 30 - np.clip(df_features['avg_resolution_hours'] - 10, 0, 50), 0, 100)
norm_tenure = np.clip(df_features['tenure_months'] / 24.0 * 100, 0, 100)

df_features['health_score'] = (
    norm_eng * 0.35 +
    norm_sat * 0.25 +
    norm_pay * 0.15 +
    norm_supp * 0.15 +
    norm_tenure * 0.10
).round(1)

# Business Segmentation Definition
# High Value: Monthly Fee >= median or Enterprise/Business
val_threshold = df_features['monthly_fee'].median()
df_features['is_high_value'] = df_features['monthly_fee'] >= val_threshold

def assign_segment(row):
    is_hv = row['is_high_value']
    health = row['health_score']
    status = row['subscription_status']
    
    if status == 'Churned':
        return 'Inactive Customers'
    elif is_hv and health >= 60:
        return 'High Value – Low Risk'
    elif is_hv and health < 60:
        return 'High Value – High Risk'
    elif not is_hv and health >= 60:
        return 'Low Value – Low Risk'
    elif not is_hv and health < 45:
        return 'Low Value – High Risk'
    elif health >= 75:
        return 'Engaged Customers'
    else:
        return 'At-Risk Customers'

df_features['customer_health_segment'] = df_features.apply(assign_segment, axis=1)

print("Customer Health Segments Distribution:")
print(df_features['customer_health_segment'].value_counts())

# Segmentation Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
seg_counts = df_features['customer_health_segment'].value_counts()
sns.barplot(x=seg_counts.values, y=seg_counts.index, ax=ax1, color='#2c7bb6')
ax1.set_title("Customer Distribution across Strategic Segments", fontsize=13, fontweight='bold')
ax1.set_xlabel("Number of Customers")

sns.scatterplot(
    data=df_features.sample(2000, random_state=42),
    x='avg_monthly_logins',
    y='health_score',
    hue='customer_health_segment',
    alpha=0.7,
    palette='tab10',
    ax=ax2
)
ax2.set_title("Engagement (Monthly Logins) vs Health Score", fontsize=13, fontweight='bold')
ax2.set_xlabel("Avg Monthly Logins")
ax2.set_ylabel("Health Score (0-100)")
ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)

plt.tight_layout()
fig.savefig(os.path.join(SCREENSHOTS_DIR, "03_customer_segmentation.png"), bbox_inches='tight')
plt.close(fig)
print("Saved screenshots/03_customer_segmentation.png")

print("\n--- STEP 4: CHURN PREDICTION MODELING ---")

# Prepare modeling dataset
# Avoid data leakage: only use features available during active lifecycle
df_model = df_features.copy()
df_model['target_churn'] = (df_model['subscription_status'] == 'Churned').astype(int)

feature_cols_num = [
    'tenure_months', 'monthly_fee', 'discount_percentage',
    'avg_monthly_logins', 'avg_active_days', 'avg_session_mins',
    'avg_features_used', 'ticket_count', 'unresolved_tickets',
    'failed_payments', 'nps_score', 'feedback_csat'
]
feature_cols_cat = ['contract_type', 'plan_name', 'customer_segment', 'acquisition_channel', 'auto_renew']

X = df_model[feature_cols_num + feature_cols_cat]
y = df_model['target_churn']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

# Preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), feature_cols_num),
        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), feature_cols_cat)
    ]
)

# 1. Logistic Regression Model
lr_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=1000, random_state=42, C=1.0))
])
lr_pipeline.fit(X_train, y_train)

# 2. Random Forest Model
rf_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=150, max_depth=10, min_samples_leaf=5, random_state=42))
])
rf_pipeline.fit(X_train, y_train)

# Evaluation
y_pred_lr = lr_pipeline.predict(X_test)
y_prob_lr = lr_pipeline.predict_proba(X_test)[:, 1]

y_pred_rf = rf_pipeline.predict(X_test)
y_prob_rf = rf_pipeline.predict_proba(X_test)[:, 1]

lr_acc = accuracy_score(y_test, y_pred_lr)
lr_prec = precision_score(y_test, y_pred_lr)
lr_rec = recall_score(y_test, y_pred_lr)
lr_f1 = f1_score(y_test, y_pred_lr)
lr_auc = roc_auc_score(y_test, y_prob_lr)

rf_acc = accuracy_score(y_test, y_pred_rf)
rf_prec = precision_score(y_test, y_pred_rf)
rf_rec = recall_score(y_test, y_pred_rf)
rf_f1 = f1_score(y_test, y_pred_rf)
rf_auc = roc_auc_score(y_test, y_prob_rf)

print(f"\nModel Performance Metrics:")
print(f"--- Logistic Regression (Interpretable Baseline) ---")
print(f"Accuracy:  {lr_acc:.4f}")
print(f"Precision: {lr_prec:.4f}")
print(f"Recall:    {lr_rec:.4f}")
print(f"F1 Score:  {lr_f1:.4f}")
print(f"ROC-AUC:   {lr_auc:.4f}")

print(f"\n--- Random Forest Classifier ---")
print(f"Accuracy:  {rf_acc:.4f}")
print(f"Precision: {rf_prec:.4f}")
print(f"Recall:    {rf_rec:.4f}")
print(f"F1 Score:  {rf_f1:.4f}")
print(f"ROC-AUC:   {rf_auc:.4f}")

# Extract Feature Importances / Coefficients
cat_encoder = lr_pipeline.named_steps['preprocessor'].named_transformers_['cat']
cat_feature_names = list(cat_encoder.get_feature_names_out(feature_cols_cat))
all_feature_names = feature_cols_num + cat_feature_names

lr_coefs = lr_pipeline.named_steps['classifier'].coef_[0]
df_coefs = pd.DataFrame({
    'Feature': all_feature_names,
    'Coefficient': lr_coefs,
    'Odds_Ratio': np.exp(lr_coefs)
}).sort_values(by='Coefficient', ascending=False)

rf_importances = rf_pipeline.named_steps['classifier'].feature_importances_
df_rf_imp = pd.DataFrame({
    'Feature': all_feature_names,
    'Importance': rf_importances
}).sort_values(by='Importance', ascending=False)

# Predict probabilities on entire dataset for dashboard & risk table
all_probs = rf_pipeline.predict_proba(X)[:, 1]
df_features['churn_probability'] = np.round(all_probs, 4)

def assign_risk_category(prob):
    if prob >= 0.70:
        return 'High Risk'
    elif prob >= 0.35:
        return 'Medium Risk'
    else:
        return 'Low Risk'

df_features['risk_category'] = df_features['churn_probability'].apply(assign_risk_category)

# Save Master Enriched Customer Profile
df_features.to_csv(os.path.join(CLEAN_DIR, "customer_churn_master.csv"), index=False)
print(f"Master enriched dataset saved with {len(df_features)} records.")

# Plot ROC Curves & Feature Importance
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# ROC Curves
fpr_lr, tpr_lr, _ = roc_curve(y_test, y_prob_lr)
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_prob_rf)
axes[0].plot(fpr_lr, tpr_lr, label=f'Logistic Regression (AUC = {lr_auc:.3f})', color='#e67e22', lw=2)
axes[0].plot(fpr_rf, tpr_rf, label=f'Random Forest (AUC = {rf_auc:.3f})', color='#2980b9', lw=2)
axes[0].plot([0, 1], [0, 1], 'k--', lw=1.5)
axes[0].set_title('Receiver Operating Characteristic (ROC) Curve', fontsize=12, fontweight='bold')
axes[0].set_xlabel('False Positive Rate')
axes[0].set_ylabel('True Positive Rate')
axes[0].legend(loc='lower right')

# Random Forest Top 10 Feature Importance
top_rf = df_rf_imp.head(10)
sns.barplot(x=top_rf['Importance'], y=top_rf['Feature'], ax=axes[1], color='#2b5c8f')
axes[1].set_title('Top 10 Churn Drivers (Random Forest Importance)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Relative Importance')

# Logistic Regression Top Coefficients
top_lr = pd.concat([df_coefs.head(5), df_coefs.tail(5)])
colors_lr = ['#e74c3c' if c > 0 else '#2ecc71' for c in top_lr['Coefficient']]
axes[2].barh(top_lr['Feature'], top_lr['Coefficient'], color=colors_lr)
axes[2].set_title('Key Churn Risk Factors (Logistic Regression Coef)', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Log-Odds (+ Increases Churn, - Reduces Churn)')
axes[2].axvline(0, color='grey', linestyle='--', linewidth=0.8)

plt.tight_layout()
fig.savefig(os.path.join(SCREENSHOTS_DIR, "04_model_evaluation.png"), bbox_inches='tight')
plt.close(fig)
print("Saved screenshots/04_model_evaluation.png")

# Confusion Matrix Heatmap
fig, ax = plt.subplots(figsize=(6, 5))
cm = confusion_matrix(y_test, y_pred_rf)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Retained', 'Churned'], yticklabels=['Retained', 'Churned'], ax=ax)
ax.set_title('Confusion Matrix - Random Forest Churn Model', fontsize=12, fontweight='bold')
ax.set_xlabel('Predicted Label')
ax.set_ylabel('Actual Label')
plt.tight_layout()
fig.savefig(os.path.join(SCREENSHOTS_DIR, "05_confusion_matrix.png"), bbox_inches='tight')
plt.close(fig)
print("Saved screenshots/05_confusion_matrix.png")

print("\n--- Pipeline Completed Successfully! ---")
