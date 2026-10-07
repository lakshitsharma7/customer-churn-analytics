import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set seeds for reproducibility
np.random.seed(42)
random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, 'cleaned'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'notebooks'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'sql'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'powerbi'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'reports'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'screenshots'), exist_ok=True)

N_CUSTOMERS = 12000

print(f"Generating realistic SaaS dataset for {N_CUSTOMERS} customers...")

# 1. GENERATE CUSTOMERS
first_names = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
    "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
    "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra",
    "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa", "Edward", "Deborah",
    "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon", "Jeffrey", "Laura", "Ryan", "Cynthia",
    "Jacob", "Kathleen", "Gary", "Amy", "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen",
    "Stephen", "Anna", "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Gregory", "Christine", "Frank", "Debra", "Alexander", "Rachel"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]

countries_states_cities = {
    "United States": {
        "California": ["San Francisco", "Los Angeles", "San Jose", "San Diego"],
        "New York": ["New York", "Buffalo", "Rochester", "Albany"],
        "Texas": ["Austin", "Dallas", "Houston", "San Antonio"],
        "Washington": ["Seattle", "Bellevue", "Tacoma", "Spokane"],
        "Illinois": ["Chicago", "Naperville", "Rockford", "Peoria"],
        "Massachusetts": ["Boston", "Cambridge", "Worcester", "Lowell"],
        "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"]
    },
    "United Kingdom": {
        "England": ["London", "Manchester", "Birmingham", "Leeds", "Bristol"],
        "Scotland": ["Edinburgh", "Glasgow", "Aberdeen"],
        "Wales": ["Cardiff", "Swansea"]
    },
    "Canada": {
        "Ontario": ["Toronto", "Ottawa", "Mississauga"],
        "British Columbia": ["Vancouver", "Victoria", "Burnaby"],
        "Quebec": ["Montreal", "Quebec City", "Laval"]
    },
    "Germany": {
        "Bavaria": ["Munich", "Nuremberg", "Augsburg"],
        "Berlin": ["Berlin"],
        "North Rhine-Westphalia": ["Cologne", "Dusseldorf", "Dortmund"]
    },
    "Australia": {
        "New South Wales": ["Sydney", "Newcastle", "Wollongong"],
        "Victoria": ["Melbourne", "Geelong"],
        "Queensland": ["Brisbane", "Gold Coast"]
    },
    "India": {
        "Karnataka": ["Bengaluru", "Mysuru"],
        "Maharashtra": ["Mumbai", "Pune"],
        "Telangana": ["Hyderabad"],
        "Delhi NCR": ["New Delhi", "Gurugram", "Noida"]
    }
}

segments = ["SMB", "Mid-Market", "Enterprise"]
segment_weights = [0.55, 0.32, 0.13]

industries = [
    "Technology", "Finance", "Healthcare", "Retail",
    "Professional Services", "Manufacturing", "Education"
]
industry_weights = [0.28, 0.18, 0.14, 0.13, 0.12, 0.09, 0.06]

channels = [
    "Organic", "Google Ads", "LinkedIn", "Referral",
    "Website", "Sales Team", "Partner", "Facebook Ads"
]
channel_weights = [0.22, 0.20, 0.16, 0.14, 0.11, 0.08, 0.05, 0.04]

company_sizes = {
    "SMB": ["1-10 employees", "11-50 employees"],
    "Mid-Market": ["51-200 employees", "201-500 employees"],
    "Enterprise": ["501-1000 employees", "1000+ employees"]
}

# Date range: Signup between 2022-01-01 and 2024-06-30
start_date_range = datetime(2022, 1, 1)
end_date_range = datetime(2024, 6, 30)
days_between = (end_date_range - start_date_range).days

customers_list = []
country_keys = list(countries_states_cities.keys())
country_weights = [0.42, 0.18, 0.12, 0.10, 0.08, 0.10]

for i in range(1, N_CUSTOMERS + 1):
    c_id = f"CUST-{i:06d}"
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    c_name = f"{fname} {lname}"
    
    # Age between 21 and 65
    age = int(np.random.normal(38, 9))
    age = max(21, min(68, age))
    gender = random.choices(["Male", "Female", "Other"], weights=[0.51, 0.46, 0.03])[0]
    
    country = random.choices(country_keys, weights=country_weights)[0]
    state = random.choice(list(countries_states_cities[country].keys()))
    city = random.choice(countries_states_cities[country][state])
    
    segment = random.choices(segments, weights=segment_weights)[0]
    industry = random.choices(industries, weights=industry_weights)[0]
    co_size = random.choice(company_sizes[segment])
    
    # Enterprise more likely via Sales Team / Referral / LinkedIn
    if segment == "Enterprise":
        acq_channel = random.choices(channels, weights=[0.05, 0.10, 0.25, 0.20, 0.05, 0.30, 0.05, 0.00])[0]
    else:
        acq_channel = random.choices(channels, weights=channel_weights)[0]
        
    signup_dt = start_date_range + timedelta(days=random.randint(0, days_between))
    signup_str = signup_dt.strftime("%Y-%m-%d")
    
    customers_list.append({
        "customer_id": c_id,
        "customer_name": c_name,
        "age": age,
        "gender": gender,
        "country": country,
        "state": state,
        "city": city,
        "customer_segment": segment,
        "industry": industry,
        "company_size": co_size,
        "signup_date": signup_str,
        "acquisition_channel": acq_channel
    })

df_cust = pd.DataFrame(customers_list)

# 2. GENERATE SUBSCRIPTIONS & CHURN LOGIC
# Base plan characteristics:
# Basic: $29/mo, Professional: $79/mo, Business: $179/mo, Enterprise: $499/mo
plan_mapping = {
    "SMB": (["Basic", "Professional", "Business"], [0.45, 0.40, 0.15]),
    "Mid-Market": (["Professional", "Business", "Enterprise"], [0.25, 0.55, 0.20]),
    "Enterprise": (["Business", "Enterprise"], [0.15, 0.85])
}

plan_pricing = {
    "Basic": 29.0,
    "Professional": 79.0,
    "Business": 179.0,
    "Enterprise": 499.0
}

contract_options = ["Monthly", "Quarterly", "Annual"]

subscriptions_list = []
activity_list = []
support_tickets_list = []
payments_list = []
feedback_list = []

CURRENT_DATE = datetime(2024, 12, 31)

ticket_id_counter = 1
payment_id_counter = 1
feedback_id_counter = 1
activity_id_counter = 1

for idx, row in df_cust.iterrows():
    c_id = row["customer_id"]
    segment = row["customer_segment"]
    signup_dt = datetime.strptime(row["signup_date"], "%Y-%m-%d")
    
    # Choose plan based on segment
    avail_plans, p_weights = plan_mapping[segment]
    plan = random.choices(avail_plans, weights=p_weights)[0]
    base_fee = plan_pricing[plan]
    
    # Contract type preference by segment
    if segment == "Enterprise":
        contract = random.choices(contract_options, weights=[0.10, 0.15, 0.75])[0]
    elif segment == "Mid-Market":
        contract = random.choices(contract_options, weights=[0.35, 0.25, 0.40])[0]
    else: # SMB
        contract = random.choices(contract_options, weights=[0.65, 0.20, 0.15])[0]
        
    discount = 0.0
    if contract == "Annual":
        discount = random.choice([0.10, 0.15, 0.20])
    elif contract == "Quarterly":
        discount = random.choice([0.00, 0.05, 0.10])
    elif random.random() < 0.20:
        discount = random.choice([0.05, 0.10])
        
    monthly_fee = round(base_fee * (1 - discount), 2)
    billing_cycle = "Monthly" if contract == "Monthly" else ("Quarterly" if contract == "Quarterly" else "Annual")
    auto_renew = "Yes" if random.random() < (0.92 if contract == "Annual" else 0.78) else "No"
    
    # Tenure calculation
    potential_tenure_months = max(1, int((CURRENT_DATE - signup_dt).days / 30.4))
    
    # Churn probability model logic (Realistic Business Dynamics):
    # Base churn baseline: ~22%
    churn_prob = 0.20
    
    # Contract effect: Monthly has significantly higher churn
    if contract == "Monthly":
        churn_prob += 0.14
    elif contract == "Quarterly":
        churn_prob += 0.04
    else: # Annual
        churn_prob -= 0.12
        
    # Segment effect: SMB higher churn, Enterprise sticky
    if segment == "SMB":
        churn_prob += 0.08
    elif segment == "Enterprise":
        churn_prob -= 0.11
        
    # Plan effect: Basic higher churn
    if plan == "Basic":
        churn_prob += 0.06
    elif plan == "Enterprise":
        churn_prob -= 0.07
        
    # Auto-renew No increases churn
    if auto_renew == "No":
        churn_prob += 0.15
        
    # Acquisition channel effect: Organic/Referral/Sales lower churn, Paid Ads higher
    if row["acquisition_channel"] in ["Referral", "Sales Team", "Organic"]:
        churn_prob -= 0.05
    elif row["acquisition_channel"] in ["Facebook Ads", "Google Ads"]:
        churn_prob += 0.04
        
    # Introduce latent engagement factor (-1.0 to 1.0)
    engagement_factor = np.random.normal(0, 0.35)
    churn_prob -= engagement_factor * 0.25
    
    # Introduce latent support friction factor
    support_friction = np.random.normal(0, 0.3)
    churn_prob += support_friction * 0.20
    
    # Add random noise
    churn_prob += np.random.normal(0, 0.07)
    churn_prob = max(0.02, min(0.95, churn_prob))
    
    is_churned = np.random.binomial(1, churn_prob) == 1
    
    if is_churned:
        status = "Churned"
        # Churn happens after at least 1 month, up to potential tenure
        tenure_months = random.randint(1, potential_tenure_months)
        end_dt = signup_dt + timedelta(days=int(tenure_months * 30.4))
        if end_dt > CURRENT_DATE:
            end_dt = CURRENT_DATE - timedelta(days=random.randint(5, 60))
        end_str = end_dt.strftime("%Y-%m-%d")
    else:
        if random.random() < 0.03:
            status = "Paused"
            end_str = ""
            tenure_months = potential_tenure_months
        else:
            status = "Active"
            end_str = ""
            tenure_months = potential_tenure_months
            
    sub_id = f"SUB-{idx+1:06d}"
    subscriptions_list.append({
        "subscription_id": sub_id,
        "customer_id": c_id,
        "plan_name": plan,
        "contract_type": contract,
        "subscription_start_date": row["signup_date"],
        "subscription_end_date": end_str,
        "monthly_fee": monthly_fee,
        "discount_percentage": round(discount * 100, 1),
        "billing_cycle": billing_cycle,
        "auto_renew": auto_renew,
        "subscription_status": status
    })
    
    # 3. GENERATE MONTHLY CUSTOMER ACTIVITY
    # Number of months of history to generate
    # For churned users, engagement drops towards the end
    n_active_months = tenure_months
    for m in range(n_active_months):
        act_dt = signup_dt + timedelta(days=int(m * 30.4))
        if act_dt > CURRENT_DATE:
            break
        act_month_str = act_dt.strftime("%Y-%m")
        
        # Base engagement baseline driven by plan & engagement_factor
        plan_eng_mult = 1.0 if plan == "Basic" else (1.5 if plan == "Professional" else (2.2 if plan == "Business" else 3.5))
        base_logins = 12 * plan_eng_mult * (1.0 + engagement_factor)
        
        # Decay engagement if nearing churn
        if is_churned and m >= n_active_months - 3:
            decay = (n_active_months - m) / 4.0
            base_logins *= max(0.15, decay)
            
        base_logins = max(2.0, base_logins)
        login_cnt = max(1, int(np.random.normal(base_logins, max(0.5, base_logins * 0.25))))
        active_dys = max(1, min(30, int(login_cnt * 0.7 + np.random.normal(0, 1.5))))
        sessions = max(login_cnt, int(login_cnt * np.random.uniform(1.1, 2.2)))
        avg_sess_mins = round(max(3.5, np.random.normal(max(10.0, 24.0 * (1.0 + max(-0.6, engagement_factor * 0.5))), 4.5)), 1)
        features_cnt = max(1, min(20, int(3 * plan_eng_mult + max(-2, engagement_factor * 2) + np.random.normal(0, 1.5))))
        proj_created = max(0, int((features_cnt * 0.6 + np.random.normal(1, 1)) * (0.3 if is_churned and m == n_active_months-1 else 1.0)))
        files_up = max(0, int(proj_created * np.random.uniform(3, 12) + np.random.normal(5, 3)))
        api_cnt = int(max(0, np.random.normal(50 * plan_eng_mult, 30)) if plan in ["Business", "Enterprise"] else (random.choice([0, 0, 5]) if plan == "Professional" else 0))
        
        activity_list.append({
            "activity_id": f"ACT-{activity_id_counter:07d}",
            "customer_id": c_id,
            "activity_month": act_month_str,
            "login_count": login_cnt,
            "active_days": active_dys,
            "session_count": sessions,
            "avg_session_minutes": avg_sess_mins,
            "features_used": features_cnt,
            "projects_created": proj_created,
            "files_uploaded": files_up,
            "api_usage_count": api_cnt
        })
        activity_id_counter += 1
        
    # 4. GENERATE SUPPORT TICKETS
    # More friction / churn correlation
    n_tickets = max(0, int(np.random.poisson(0.8 + (0.9 if is_churned else 0.0) + max(0, support_friction * 1.5))))
    ticket_cats = ["Technical", "Billing", "Login", "Performance", "Integration", "Feature Request", "Security"]
    cat_weights = [0.30, 0.22, 0.15, 0.13, 0.10, 0.06, 0.04]
    
    for _ in range(n_tickets):
        t_offset = random.randint(5, max(10, int(tenure_months * 30.4)))
        t_dt = signup_dt + timedelta(days=t_offset)
        if t_dt > CURRENT_DATE:
            t_dt = CURRENT_DATE - timedelta(days=random.randint(1, 45))
            
        cat = random.choices(ticket_cats, weights=cat_weights)[0]
        prio = random.choices(["Low", "Medium", "High", "Critical"], weights=[0.35, 0.40, 0.18, 0.07])[0]
        
        # Resolution time hours (longer for churned / critical)
        res_time = round(max(0.5, np.random.exponential(14.0 + (10.0 if is_churned else 0.0) + (15.0 if prio in ["High", "Critical"] else 0.0))), 1)
        
        if is_churned and random.random() < 0.25:
            t_status = random.choice(["Pending", "Escalated"])
            sat_score = random.choices([1, 2, 3], weights=[0.5, 0.35, 0.15])[0]
        else:
            t_status = random.choices(["Resolved", "Closed"], weights=[0.75, 0.25])[0]
            sat_score = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.10, 0.20, 0.35, 0.30] if not is_churned else [0.35, 0.30, 0.20, 0.10, 0.05])[0]
            
        support_tickets_list.append({
            "ticket_id": f"TCK-{ticket_id_counter:06d}",
            "customer_id": c_id,
            "ticket_date": t_dt.strftime("%Y-%m-%d"),
            "issue_category": cat,
            "priority": prio,
            "resolution_time_hours": res_time,
            "ticket_status": t_status,
            "satisfaction_score": sat_score
        })
        ticket_id_counter += 1
        
    # 5. GENERATE PAYMENTS
    # Number of payment cycles
    if contract == "Annual":
        cycles = max(1, int(tenure_months / 12) + 1)
        p_interval = 365
        p_amount = monthly_fee * 12
    elif contract == "Quarterly":
        cycles = max(1, int(tenure_months / 3) + 1)
        p_interval = 91
        p_amount = monthly_fee * 3
    else: # Monthly
        cycles = tenure_months
        p_interval = 30
        p_amount = monthly_fee
        
    methods = ["Credit Card", "Debit Card", "Bank Transfer", "PayPal", "UPI"]
    method_weights = [0.55, 0.15, 0.15, 0.10, 0.05]
    if segment == "Enterprise":
        method = random.choices(["Bank Transfer", "Credit Card"], weights=[0.7, 0.3])[0]
    else:
        method = random.choices(methods, weights=method_weights)[0]
        
    for c_idx in range(cycles):
        p_dt = signup_dt + timedelta(days=int(c_idx * p_interval))
        if p_dt > CURRENT_DATE:
            break
            
        # Failed payment chances higher for churned users at their final cycle
        fail_prob = 0.03
        if is_churned and c_idx == cycles - 1:
            fail_prob = 0.42
            
        is_failed = random.random() < fail_prob
        if is_failed:
            p_status = random.choices(["Failed", "Refunded", "Pending"], weights=[0.70, 0.15, 0.15])[0]
            days_over = random.randint(3, 45)
        else:
            p_status = "Successful"
            days_over = 0
            
        payments_list.append({
            "payment_id": f"PAY-{payment_id_counter:07d}",
            "customer_id": c_id,
            "payment_date": p_dt.strftime("%Y-%m-%d"),
            "amount": round(p_amount, 2),
            "payment_method": method,
            "payment_status": p_status,
            "days_overdue": days_over
        })
        payment_id_counter += 1
        
    # 6. GENERATE CUSTOMER FEEDBACK
    if random.random() < 0.65: # 65% of customers left feedback
        fb_dt = signup_dt + timedelta(days=random.randint(15, max(20, int(tenure_months * 25))))
        if fb_dt > CURRENT_DATE:
            fb_dt = CURRENT_DATE - timedelta(days=random.randint(1, 60))
            
        # NPS score (0-10) correlated with churn and support
        if is_churned:
            nps = int(np.clip(np.random.normal(4.2 - support_friction * 2, 2.2), 0, 10))
            csat = int(np.clip(np.random.normal(2.3 - support_friction * 0.8, 1.0), 1, 5))
        else:
            nps = int(np.clip(np.random.normal(8.1 + engagement_factor * 1.5, 1.6), 0, 10))
            csat = int(np.clip(np.random.normal(4.4 + engagement_factor * 0.4, 0.8), 1, 5))
            
        fb_cats = ["Product usability", "Pricing", "Performance", "Customer support", "Missing features", "Integration", "Mobile experience"]
        
        comments_by_cat = {
            "Product usability": [
                "Intuitive interface and team adopted it within days.",
                "UI navigation can be cluttered for new team members.",
                "Great dashboard layout, simplifies our daily standup.",
                "Steep learning curve for non-technical users."
            ],
            "Pricing": [
                "Great value for money compared to enterprise alternatives.",
                "Monthly plan feels a bit expensive without annual discounts.",
                "Pricing is fair, but add-on user seats add up quickly.",
                "Renewal rate increase was unexpected."
            ],
            "Performance": [
                "Blazing fast sync speeds across distributed teams.",
                "Occasional lag during peak hours in large file exports.",
                "Reliable uptime with minimal disruptions.",
                "Slow loading times on large dataset syncs."
            ],
            "Customer support": [
                "Support team resolved our critical issue in under an hour!",
                "Took too long to get a response on an urgent billing ticket.",
                "Helpful customer success manager during onboarding.",
                "Ticket was escalated multiple times without a clear resolution."
            ],
            "Missing features": [
                "Would love to see more granular role-based permissions.",
                "Missing advanced analytics export to warehouse.",
                "The core features cover 90% of our workflow needs.",
                "Awaiting native integration with Jira and Slack."
            ],
            "Integration": [
                "Seamless integration with Google Workspace and Salesforce.",
                "Webhook latency caused duplicate entries in our CRM.",
                "API documentation is top notch and easy to implement.",
                "Custom connector setup was frustrating."
            ],
            "Mobile experience": [
                "Mobile app is lightweight and perfect for on-the-go approvals.",
                "Mobile notifications sometimes get delayed.",
                "Needs iPad tablet optimization.",
                "Clean mobile UI, very responsive."
            ]
        }
        
        fb_cat = random.choice(fb_cats)
        if nps >= 8:
            comment_pool = [c for c in comments_by_cat[fb_cat] if "Intuitive" in c or "Great" in c or "Blazing" in c or "fast" in c or "resolved" in c or "Helpful" in c or "Seamless" in c or "lightweight" in c or "Clean" in c or "cover" in c or "fair" in c or "Reliable" in c or "top notch" in c]
        else:
            comment_pool = [c for c in comments_by_cat[fb_cat] if "cluttered" in c or "expensive" in c or "lag" in c or "Took too long" in c or "escalated" in c or "Missing" in c or "frustrating" in c or "delayed" in c or "Slow" in c or "unexpected" in c or "Steep" in c or "latency" in c or "optimization" in c]
            
        comment = random.choice(comment_pool if comment_pool else comments_by_cat[fb_cat])
        
        feedback_list.append({
            "feedback_id": f"FBK-{feedback_id_counter:06d}",
            "customer_id": c_id,
            "feedback_date": fb_dt.strftime("%Y-%m-%d"),
            "nps_score": nps,
            "satisfaction_score": csat,
            "feedback_category": fb_cat,
            "comment": comment
        })
        feedback_id_counter += 1

df_subs = pd.DataFrame(subscriptions_list)
df_act = pd.DataFrame(activity_list)
df_tickets = pd.DataFrame(support_tickets_list)
df_payments = pd.DataFrame(payments_list)
df_fb = pd.DataFrame(feedback_list)

print(f"Data generated:")
print(f"  Customers: {len(df_cust)}")
print(f"  Subscriptions: {len(df_subs)}")
print(f"  Activity records: {len(df_act)}")
print(f"  Support tickets: {len(df_tickets)}")
print(f"  Payments: {len(df_payments)}")
print(f"  Feedback records: {len(df_fb)}")

# 7. INJECT REALISTIC DATA QUALITY DEFECTS INTO RAW CSVs FOR CLEANING
print("Injecting realistic data-quality problems for data cleaning demonstration...")

# a) Inconsistent text casing in customers
casing_indices = np.random.choice(df_cust.index, size=int(len(df_cust) * 0.05), replace=False)
for idx in casing_indices[:len(casing_indices)//2]:
    df_cust.loc[idx, "customer_name"] = str(df_cust.loc[idx, "customer_name"]).upper()
for idx in casing_indices[len(casing_indices)//2:]:
    df_cust.loc[idx, "customer_name"] = str(df_cust.loc[idx, "customer_name"]).lower()

# b) Missing values in city, state, acquisition_channel, and feedback comments
null_city_idx = np.random.choice(df_cust.index, size=int(len(df_cust) * 0.03), replace=False)
df_cust.loc[null_city_idx, "city"] = np.nan

null_state_idx = np.random.choice(df_cust.index, size=int(len(df_cust) * 0.02), replace=False)
df_cust.loc[null_state_idx, "state"] = np.nan

null_channel_idx = np.random.choice(df_cust.index, size=int(len(df_cust) * 0.015), replace=False)
df_cust.loc[null_channel_idx, "acquisition_channel"] = np.nan

# c) Duplicate customer records (~1.2% duplicates)
dup_cust_idx = np.random.choice(df_cust.index, size=150, replace=False)
dup_cust_rows = df_cust.loc[dup_cust_idx].copy()
df_cust_raw = pd.concat([df_cust, dup_cust_rows], ignore_index=True)

# d) Outliers in support ticket resolution time (e.g. 999.0 hours anomaly)
outlier_tck_idx = np.random.choice(df_tickets.index, size=25, replace=False)
df_tickets.loc[outlier_tck_idx, "resolution_time_hours"] = 999.9

# e) Payment anomalies: a few negative amounts or extreme outliers
anomaly_pay_idx = np.random.choice(df_payments.index, size=15, replace=False)
df_payments.loc[anomaly_pay_idx[:8], "amount"] = -df_payments.loc[anomaly_pay_idx[:8], "amount"].abs()
df_payments.loc[anomaly_pay_idx[8:], "amount"] = 99999.0

# f) Date formatting variations in some tables (e.g. YYYY/MM/DD or DD-MM-YYYY in a small slice)
fmt_tck_idx = np.random.choice(df_tickets.index, size=int(len(df_tickets) * 0.03), replace=False)
for idx in fmt_tck_idx:
    dt_val = df_tickets.loc[idx, "ticket_date"]
    try:
        df_tickets.loc[idx, "ticket_date"] = datetime.strptime(dt_val, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        pass

# Save Raw CSV Files
df_cust_raw.to_csv(os.path.join(DATA_DIR, "customers.csv"), index=False)
df_subs.to_csv(os.path.join(DATA_DIR, "subscriptions.csv"), index=False)
df_act.to_csv(os.path.join(DATA_DIR, "customer_activity.csv"), index=False)
df_tickets.to_csv(os.path.join(DATA_DIR, "support_tickets.csv"), index=False)
df_payments.to_csv(os.path.join(DATA_DIR, "payments.csv"), index=False)
df_fb.to_csv(os.path.join(DATA_DIR, "customer_feedback.csv"), index=False)

print("Raw CSV datasets successfully generated and saved to data/ directory!")
