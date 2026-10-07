-- =====================================================================================
-- CloudSync SaaS Customer Churn & Retention Analytics
-- Comprehensive SQL Intelligence Suite (20 Production-Grade Analytical Queries)
-- =====================================================================================
-- Author: Antigravity Data Intelligence & Business Analytics Team
-- Database: CloudSync SaaS Data Warehouse (Star Schema Architecture)
-- Dialect: ANSI SQL / SQLite / PostgreSQL Compatible
-- =====================================================================================

-- -------------------------------------------------------------------------------------
-- 1. OVERALL CHURN RATE & SUBSCRIBER STATUS SUMMARY
-- Business Question: What is the overall customer base distribution and baseline churn rate?
-- -------------------------------------------------------------------------------------
WITH subscriber_summary AS (
    SELECT 
        COUNT(DISTINCT customer_id) AS total_customers,
        SUM(CASE WHEN subscription_status = 'Active' THEN 1 ELSE 0 END) AS active_customers,
        SUM(CASE WHEN subscription_status = 'Churned' THEN 1 ELSE 0 END) AS churned_customers,
        SUM(CASE WHEN subscription_status = 'Paused' THEN 1 ELSE 0 END) AS paused_customers
    FROM subscriptions
)
SELECT 
    total_customers,
    active_customers,
    churned_customers,
    paused_customers,
    ROUND(CAST(churned_customers AS FLOAT) / total_customers * 100, 2) AS overall_churn_rate_pct,
    ROUND(CAST(active_customers AS FLOAT) / total_customers * 100, 2) AS active_retention_rate_pct
FROM subscriber_summary;


-- -------------------------------------------------------------------------------------
-- 2. MONTHLY CHURN TREND & ROLLING RETENTION METRICS
-- Business Question: How has churn volume and rate evolved month-over-month?
-- -------------------------------------------------------------------------------------
WITH monthly_churns AS (
    SELECT 
        SUBSTR(subscription_end_date, 1, 7) AS churn_month,
        COUNT(customer_id) AS monthly_churned_customers,
        ROUND(SUM(monthly_fee), 2) AS monthly_revenue_lost
    FROM subscriptions
    WHERE subscription_status = 'Churned' 
      AND subscription_end_date IS NOT NULL
    GROUP BY SUBSTR(subscription_end_date, 1, 7)
)
SELECT 
    churn_month,
    monthly_churned_customers,
    monthly_revenue_lost,
    SUM(monthly_churned_customers) OVER (ORDER BY churn_month) AS cumulative_churned_customers,
    SUM(monthly_revenue_lost) OVER (ORDER BY churn_month) AS cumulative_revenue_lost,
    LAG(monthly_churned_customers, 1) OVER (ORDER BY churn_month) AS prev_month_churn_count,
    ROUND(
        (monthly_churned_customers - LAG(monthly_churned_customers, 1) OVER (ORDER BY churn_month)) 
        * 100.0 / NULLIF(LAG(monthly_churned_customers, 1) OVER (ORDER BY churn_month), 0), 
        2
    ) AS mom_churn_growth_pct
FROM monthly_churns
ORDER BY churn_month;


-- -------------------------------------------------------------------------------------
-- 3. CHURN RATE AND MRR IMPACT BY SUBSCRIPTION PLAN
-- Business Question: Which subscription plan tier experiences the highest churn?
-- -------------------------------------------------------------------------------------
SELECT 
    plan_name,
    COUNT(customer_id) AS total_subscribers,
    SUM(CASE WHEN subscription_status = 'Active' THEN 1 ELSE 0 END) AS active_subscribers,
    SUM(CASE WHEN subscription_status = 'Churned' THEN 1 ELSE 0 END) AS churned_subscribers,
    ROUND(SUM(CASE WHEN subscription_status = 'Churned' THEN 1.0 ELSE 0.0 END) / COUNT(customer_id) * 100, 2) AS churn_rate_pct,
    ROUND(SUM(CASE WHEN subscription_status = 'Active' THEN monthly_fee ELSE 0 END), 2) AS active_mrr,
    ROUND(SUM(CASE WHEN subscription_status = 'Churned' THEN monthly_fee ELSE 0 END), 2) AS lost_mrr
FROM subscriptions
GROUP BY plan_name
ORDER BY churn_rate_pct DESC;


-- -------------------------------------------------------------------------------------
-- 4. CHURN RATE BY CONTRACT COMMITMENT TYPE
-- Business Question: How does commitment length (Monthly vs Annual) influence retention?
-- -------------------------------------------------------------------------------------
SELECT 
    contract_type,
    COUNT(customer_id) AS total_accounts,
    SUM(CASE WHEN subscription_status = 'Churned' THEN 1 ELSE 0 END) AS churned_accounts,
    ROUND(CAST(SUM(CASE WHEN subscription_status = 'Churned' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(customer_id) * 100, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_fee), 2) AS avg_contract_fee,
    ROUND(AVG(discount_percentage), 2) AS avg_discount_pct
FROM subscriptions
GROUP BY contract_type
ORDER BY churn_rate_pct DESC;


-- -------------------------------------------------------------------------------------
-- 5. REVENUE CONTRIBUTION & ARPU BY CUSTOMER SEGMENT
-- Business Question: What is the active MRR, ARR, and ARPU across SMB, Mid-Market, and Enterprise?
-- -------------------------------------------------------------------------------------
SELECT 
    c.customer_segment,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    SUM(CASE WHEN s.subscription_status = 'Active' THEN 1 ELSE 0 END) AS active_customers,
    ROUND(SUM(CASE WHEN s.subscription_status = 'Active' THEN s.monthly_fee ELSE 0 END), 2) AS active_mrr,
    ROUND(SUM(CASE WHEN s.subscription_status = 'Active' THEN s.monthly_fee * 12 ELSE 0 END), 2) AS active_arr,
    ROUND(
        SUM(CASE WHEN s.subscription_status = 'Active' THEN s.monthly_fee ELSE 0 END) / 
        NULLIF(SUM(CASE WHEN s.subscription_status = 'Active' THEN 1 ELSE 0 END), 0), 
        2
    ) AS arpu
FROM customers c
INNER JOIN subscriptions s ON c.customer_id = s.customer_id
GROUP BY c.customer_segment
ORDER BY active_mrr DESC;


-- -------------------------------------------------------------------------------------
-- 6. REVENUE LOST DUE TO CHURN BY INDUSTRY AND SEGMENT
-- Business Question: Where is revenue leakage most severe in terms of industry & company tier?
-- -------------------------------------------------------------------------------------
SELECT 
    c.industry,
    c.customer_segment,
    COUNT(s.customer_id) AS churned_accounts,
    ROUND(SUM(s.monthly_fee), 2) AS monthly_revenue_lost,
    ROUND(SUM(s.monthly_fee * 12), 2) AS annual_revenue_lost,
    ROUND(
        SUM(s.monthly_fee) * 100.0 / 
        SUM(SUM(s.monthly_fee)) OVER(), 
        2
    ) AS pct_of_total_churn_revenue_loss
FROM customers c
INNER JOIN subscriptions s ON c.customer_id = s.customer_id
WHERE s.subscription_status = 'Churned'
GROUP BY c.industry, c.customer_segment
ORDER BY monthly_revenue_lost DESC
LIMIT 15;


-- -------------------------------------------------------------------------------------
-- 7. TOP 20 ENTERPRISE CUSTOMERS BY CUMULATIVE REVENUE CONTRIBUTIONS
-- Business Question: Who are our highest-value accounts across their entire lifecycle?
-- -------------------------------------------------------------------------------------
WITH customer_spending AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.customer_segment,
        c.industry,
        c.country,
        s.plan_name,
        s.subscription_status,
        ROUND(SUM(p.amount), 2) AS total_historical_spend,
        COUNT(p.payment_id) AS total_payments_made
    FROM customers c
    INNER JOIN subscriptions s ON c.customer_id = s.customer_id
    INNER JOIN payments p ON c.customer_id = p.customer_id
    WHERE p.payment_status = 'Successful'
    GROUP BY c.customer_id, c.customer_name, c.customer_segment, c.industry, c.country, s.plan_name, s.subscription_status
)
SELECT 
    DENSE_RANK() OVER (ORDER BY total_historical_spend DESC) AS revenue_rank,
    customer_id,
    customer_name,
    customer_segment,
    industry,
    plan_name,
    subscription_status,
    total_historical_spend,
    total_payments_made
FROM customer_spending
LIMIT 20;


-- -------------------------------------------------------------------------------------
-- 8. CUSTOMERS WITH DECLINING ENGAGEMENT (MONTH-OVER-MONTH ACTIVITY DROP)
-- Business Question: Which active accounts show a >40% drop in login activity over consecutive months?
-- -------------------------------------------------------------------------------------
WITH monthly_engagement AS (
    SELECT 
        a.customer_id,
        a.activity_month,
        a.login_count,
        a.active_days,
        LAG(a.login_count, 1) OVER (PARTITION BY a.customer_id ORDER BY a.activity_month) AS prev_month_logins
    FROM customer_activity a
    INNER JOIN subscriptions s ON a.customer_id = s.customer_id
    WHERE s.subscription_status = 'Active'
),
engagement_drops AS (
    SELECT 
        customer_id,
        activity_month,
        login_count,
        prev_month_logins,
        ROUND((login_count - prev_month_logins) * 100.0 / NULLIF(prev_month_logins, 0), 2) AS login_drop_pct
    FROM monthly_engagement
    WHERE prev_month_logins IS NOT NULL 
      AND prev_month_logins >= 10
      AND login_count < prev_month_logins * 0.60
)
SELECT 
    e.customer_id,
    c.customer_name,
    c.customer_segment,
    s.plan_name,
    s.monthly_fee,
    e.activity_month,
    e.prev_month_logins,
    e.login_count AS current_logins,
    e.login_drop_pct
FROM engagement_drops e
INNER JOIN customers c ON e.customer_id = c.customer_id
INNER JOIN subscriptions s ON e.customer_id = s.customer_id
ORDER BY e.login_drop_pct ASC, s.monthly_fee DESC
LIMIT 25;


-- -------------------------------------------------------------------------------------
-- 9. PAYMENT DELINQUENCY & FAILED PAYMENT CHURN CORRELATION
-- Business Question: How do payment failures relate to churn status and overdue cycles?
-- -------------------------------------------------------------------------------------
SELECT 
    s.subscription_status,
    COUNT(DISTINCT p.customer_id) AS total_customers_with_payments,
    SUM(CASE WHEN p.payment_status = 'Failed' THEN 1 ELSE 0 END) AS total_failed_transactions,
    ROUND(SUM(CASE WHEN p.payment_status = 'Failed' THEN 1.0 ELSE 0.0 END) / COUNT(p.payment_id) * 100, 2) AS payment_failure_rate_pct,
    ROUND(AVG(p.days_overdue), 2) AS avg_days_overdue,
    ROUND(SUM(CASE WHEN p.payment_status = 'Failed' THEN p.amount ELSE 0 END), 2) AS total_failed_amount
FROM payments p
INNER JOIN subscriptions s ON p.customer_id = s.customer_id
GROUP BY s.subscription_status;


-- -------------------------------------------------------------------------------------
-- 10. SUPPORT TICKET INTENSITY AND UNRESOLVED TICKETS BY CHURN STATUS
-- Business Question: Do churned customers experience longer resolution times and more open tickets?
-- -------------------------------------------------------------------------------------
SELECT 
    s.subscription_status,
    COUNT(DISTINCT t.customer_id) AS customers_submitting_tickets,
    COUNT(t.ticket_id) AS total_tickets_logged,
    ROUND(COUNT(t.ticket_id) * 1.0 / COUNT(DISTINCT t.customer_id), 2) AS avg_tickets_per_customer,
    ROUND(AVG(t.resolution_time_hours), 2) AS avg_resolution_time_hours,
    SUM(CASE WHEN t.ticket_status IN ('Pending', 'Escalated') THEN 1 ELSE 0 END) AS unresolved_tickets,
    ROUND(AVG(t.satisfaction_score), 2) AS avg_support_csat
FROM support_tickets t
INNER JOIN subscriptions s ON t.customer_id = s.customer_id
GROUP BY s.subscription_status;


-- -------------------------------------------------------------------------------------
-- 11. HIGH-VALUE ACTIVE CUSTOMERS AT IMMINENT CHURN RISK
-- Business Question: Which active Enterprise & Business customers have high risk factors?
-- -------------------------------------------------------------------------------------
WITH active_customer_risk AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.customer_segment,
        s.plan_name,
        s.monthly_fee,
        s.contract_type,
        COUNT(DISTINCT CASE WHEN p.payment_status = 'Failed' THEN p.payment_id END) AS failed_payments_cnt,
        COUNT(DISTINCT CASE WHEN t.ticket_status IN ('Pending', 'Escalated') THEN t.ticket_id END) AS open_tickets_cnt,
        AVG(t.satisfaction_score) AS avg_csat_score,
        AVG(f.nps_score) AS nps_score
    FROM customers c
    INNER JOIN subscriptions s ON c.customer_id = s.customer_id
    LEFT JOIN payments p ON c.customer_id = p.customer_id
    LEFT JOIN support_tickets t ON c.customer_id = t.customer_id
    LEFT JOIN customer_feedback f ON c.customer_id = f.customer_id
    WHERE s.subscription_status = 'Active' 
      AND s.plan_name IN ('Business', 'Enterprise')
    GROUP BY c.customer_id, c.customer_name, c.customer_segment, s.plan_name, s.monthly_fee, s.contract_type
)
SELECT 
    customer_id,
    customer_name,
    customer_segment,
    plan_name,
    contract_type,
    monthly_fee,
    failed_payments_cnt,
    open_tickets_cnt,
    ROUND(avg_csat_score, 1) AS avg_support_csat,
    ROUND(nps_score, 1) AS nps_score,
    CASE 
        WHEN failed_payments_cnt >= 1 AND open_tickets_cnt >= 1 THEN 'CRITICAL RISK'
        WHEN failed_payments_cnt >= 1 OR nps_score <= 4 THEN 'HIGH RISK'
        ELSE 'ELEVATED RISK'
    END AS risk_priority_flag
FROM active_customer_risk
WHERE failed_payments_cnt >= 1 OR open_tickets_cnt >= 1 OR nps_score <= 5
ORDER BY monthly_fee DESC, failed_payments_cnt DESC
LIMIT 20;


-- -------------------------------------------------------------------------------------
-- 12. RETENTION & CHURN PERFORMANCE BY ACQUISITION CHANNEL
-- Business Question: Which go-to-market channels bring the highest quality, sticky accounts?
-- -------------------------------------------------------------------------------------
SELECT 
    c.acquisition_channel,
    COUNT(c.customer_id) AS total_acquired_customers,
    SUM(CASE WHEN s.subscription_status = 'Active' THEN 1 ELSE 0 END) AS active_retained_customers,
    SUM(CASE WHEN s.subscription_status = 'Churned' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN s.subscription_status = 'Active' THEN 1.0 ELSE 0.0 END) / COUNT(c.customer_id) * 100, 2) AS retention_rate_pct,
    ROUND(SUM(CASE WHEN s.subscription_status = 'Churned' THEN 1.0 ELSE 0.0 END) / COUNT(c.customer_id) * 100, 2) AS churn_rate_pct,
    ROUND(AVG(s.monthly_fee), 2) AS avg_monthly_fee
FROM customers c
INNER JOIN subscriptions s ON c.customer_id = s.customer_id
GROUP BY c.acquisition_channel
ORDER BY retention_rate_pct DESC;


-- -------------------------------------------------------------------------------------
-- 13. AVERAGE LIFETIME TENURE OF CHURNED VS ACTIVE CUSTOMERS
-- Business Question: What is the average duration before a customer cancels vs currently active tenure?
-- -------------------------------------------------------------------------------------
SELECT 
    s.subscription_status,
    s.plan_name,
    COUNT(s.customer_id) AS customer_count,
    ROUND(AVG(
        (JULIANDAY(COALESCE(s.subscription_end_date, '2024-12-31')) - JULIANDAY(s.subscription_start_date)) / 30.4
    ), 1) AS avg_tenure_months,
    ROUND(MIN(
        (JULIANDAY(COALESCE(s.subscription_end_date, '2024-12-31')) - JULIANDAY(s.subscription_start_date)) / 30.4
    ), 1) AS min_tenure_months,
    ROUND(MAX(
        (JULIANDAY(COALESCE(s.subscription_end_date, '2024-12-31')) - JULIANDAY(s.subscription_start_date)) / 30.4
    ), 1) AS max_tenure_months
FROM subscriptions s
GROUP BY s.subscription_status, s.plan_name
ORDER BY s.subscription_status, avg_tenure_months DESC;


-- -------------------------------------------------------------------------------------
-- 14. CHURN & REVENUE PROFILE BY GEOGRAPHIC REGION (COUNTRY)
-- Business Question: Which countries represent our highest market share and lowest churn?
-- -------------------------------------------------------------------------------------
SELECT 
    c.country,
    COUNT(c.customer_id) AS total_customers,
    SUM(CASE WHEN s.subscription_status = 'Active' THEN 1 ELSE 0 END) AS active_customers,
    SUM(CASE WHEN s.subscription_status = 'Churned' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN s.subscription_status = 'Churned' THEN 1.0 ELSE 0.0 END) / COUNT(c.customer_id) * 100, 2) AS churn_rate_pct,
    ROUND(SUM(CASE WHEN s.subscription_status = 'Active' THEN s.monthly_fee ELSE 0 END), 2) AS active_mrr
FROM customers c
INNER JOIN subscriptions s ON c.customer_id = s.customer_id
GROUP BY c.country
ORDER BY total_customers DESC;


-- -------------------------------------------------------------------------------------
-- 15. CHURN BY INDUSTRY VERTICAL
-- Business Question: Which industry verticals exhibit the highest subscription churn?
-- -------------------------------------------------------------------------------------
SELECT 
    c.industry,
    COUNT(c.customer_id) AS total_accounts,
    SUM(CASE WHEN s.subscription_status = 'Churned' THEN 1 ELSE 0 END) AS churned_accounts,
    ROUND(SUM(CASE WHEN s.subscription_status = 'Churned' THEN 1.0 ELSE 0.0 END) / COUNT(c.customer_id) * 100, 2) AS churn_rate_pct,
    ROUND(SUM(CASE WHEN s.subscription_status = 'Active' THEN s.monthly_fee ELSE 0 END), 2) AS active_mrr
FROM customers c
INNER JOIN subscriptions s ON c.customer_id = s.customer_id
GROUP BY c.industry
ORDER BY churn_rate_pct DESC;


-- -------------------------------------------------------------------------------------
-- 16. CUSTOMERS WITH HIGH NPS (PROMOTERS) BUT LOW ENGAGEMENT (SILENT CHURN RISK)
-- Business Question: Who are the "Happy but Inactive" accounts at risk of sudden abandonment?
-- -------------------------------------------------------------------------------------
WITH customer_activity_agg AS (
    SELECT 
        customer_id,
        AVG(login_count) AS avg_monthly_logins,
        AVG(active_days) AS avg_active_days,
        AVG(features_used) AS avg_features_used
    FROM customer_activity
    GROUP BY customer_id
)
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    s.plan_name,
    s.monthly_fee,
    f.nps_score,
    ROUND(a.avg_monthly_logins, 1) AS avg_logins,
    ROUND(a.avg_active_days, 1) AS avg_active_days
FROM customers c
INNER JOIN subscriptions s ON c.customer_id = s.customer_id
INNER JOIN customer_feedback f ON c.customer_id = f.customer_id
INNER JOIN customer_activity_agg a ON c.customer_id = a.customer_id
WHERE s.subscription_status = 'Active'
  AND f.nps_score >= 8
  AND a.avg_monthly_logins <= 5
ORDER BY s.monthly_fee DESC
LIMIT 20;


-- -------------------------------------------------------------------------------------
-- 17. CUSTOMERS WITH LOW SATISFACTION (DETRACTORS) AND MULTIPLE SUPPORT TICKETS
-- Business Question: Which active accounts are severely frustrated by support bottlenecks?
-- -------------------------------------------------------------------------------------
WITH support_summary AS (
    SELECT 
        customer_id,
        COUNT(ticket_id) AS total_tickets,
        SUM(CASE WHEN ticket_status IN ('Pending', 'Escalated') THEN 1 ELSE 0 END) AS unresolved_tickets,
        AVG(resolution_time_hours) AS avg_resolution_hours,
        AVG(satisfaction_score) AS avg_ticket_csat
    FROM support_tickets
    GROUP BY customer_id
)
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    s.plan_name,
    s.monthly_fee,
    sup.total_tickets,
    sup.unresolved_tickets,
    ROUND(sup.avg_resolution_hours, 1) AS avg_res_hours,
    ROUND(sup.avg_ticket_csat, 1) AS avg_csat
FROM customers c
INNER JOIN subscriptions s ON c.customer_id = s.customer_id
INNER JOIN support_summary sup ON c.customer_id = sup.customer_id
WHERE s.subscription_status = 'Active'
  AND sup.total_tickets >= 3
  AND sup.avg_ticket_csat <= 2.5
ORDER BY s.monthly_fee DESC, sup.total_tickets DESC
LIMIT 20;


-- -------------------------------------------------------------------------------------
-- 18. MONTHLY RECURRING REVENUE (MRR) RUN-RATE & GROWTH TRAJECTORY
-- Business Question: What is our net historical MRR growth month by month?
-- -------------------------------------------------------------------------------------
WITH new_mrr AS (
    SELECT 
        SUBSTR(subscription_start_date, 1, 7) AS month,
        SUM(monthly_fee) AS added_mrr
    FROM subscriptions
    GROUP BY SUBSTR(subscription_start_date, 1, 7)
),
lost_mrr AS (
    SELECT 
        SUBSTR(subscription_end_date, 1, 7) AS month,
        SUM(monthly_fee) AS churned_mrr
    FROM subscriptions
    WHERE subscription_status = 'Churned' AND subscription_end_date IS NOT NULL
    GROUP BY SUBSTR(subscription_end_date, 1, 7)
)
SELECT 
    n.month,
    ROUND(n.added_mrr, 2) AS new_mrr_added,
    ROUND(COALESCE(l.churned_mrr, 0), 2) AS churned_mrr_lost,
    ROUND(n.added_mrr - COALESCE(l.churned_mrr, 0), 2) AS net_mrr_change,
    ROUND(SUM(n.added_mrr - COALESCE(l.churned_mrr, 0)) OVER (ORDER BY n.month), 2) AS cumulative_ending_mrr
FROM new_mrr n
LEFT JOIN lost_mrr l ON n.month = l.month
ORDER BY n.month;


-- -------------------------------------------------------------------------------------
-- 19. QUARTERLY COHORT RETENTION MATRIX
-- Business Question: How do customer cohorts retain over subsequent quarterly intervals?
-- -------------------------------------------------------------------------------------
WITH cohort_base AS (
    SELECT 
        customer_id,
        SUBSTR(subscription_start_date, 1, 4) || '-Q' || ((CAST(SUBSTR(subscription_start_date, 6, 2) AS INT) - 1) / 3 + 1) AS signup_cohort,
        subscription_status,
        ROUND((JULIANDAY(COALESCE(subscription_end_date, '2024-12-31')) - JULIANDAY(subscription_start_date)) / 30.4, 1) AS tenure_months
    FROM subscriptions
)
SELECT 
    signup_cohort,
    COUNT(customer_id) AS total_cohort_size,
    SUM(CASE WHEN subscription_status = 'Active' THEN 1 ELSE 0 END) AS active_retained,
    SUM(CASE WHEN subscription_status = 'Churned' THEN 1 ELSE 0 END) AS churned_count,
    ROUND(SUM(CASE WHEN subscription_status = 'Active' THEN 1.0 ELSE 0.0 END) / COUNT(customer_id) * 100, 2) AS retention_rate_pct,
    ROUND(AVG(tenure_months), 1) AS avg_cohort_tenure_months
FROM cohort_base
GROUP BY signup_cohort
ORDER BY signup_cohort;


-- -------------------------------------------------------------------------------------
-- 20. TOP STRATEGIC RETENTION INTERVENTION OPPORTUNITIES
-- Business Question: Rank active customers who should be immediately enrolled in proactive Customer Success workflows.
-- -------------------------------------------------------------------------------------
WITH customer_health_calc AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.customer_segment,
        s.plan_name,
        s.monthly_fee,
        s.contract_type,
        AVG(a.login_count) AS avg_logins,
        COALESCE(SUM(CASE WHEN p.payment_status = 'Failed' THEN 1 ELSE 0 END), 0) AS failed_payments,
        COALESCE(SUM(CASE WHEN t.ticket_status IN ('Pending', 'Escalated') THEN 1 ELSE 0 END), 0) AS open_tickets,
        COALESCE(AVG(f.nps_score), 7) AS nps_score
    FROM customers c
    INNER JOIN subscriptions s ON c.customer_id = s.customer_id
    LEFT JOIN customer_activity a ON c.customer_id = a.customer_id
    LEFT JOIN payments p ON c.customer_id = p.customer_id
    LEFT JOIN support_tickets t ON c.customer_id = t.customer_id
    LEFT JOIN customer_feedback f ON c.customer_id = f.customer_id
    WHERE s.subscription_status = 'Active'
    GROUP BY c.customer_id, c.customer_name, c.customer_segment, s.plan_name, s.monthly_fee, s.contract_type
)
SELECT 
    customer_id,
    customer_name,
    customer_segment,
    plan_name,
    contract_type,
    monthly_fee,
    ROUND(avg_logins, 1) AS avg_monthly_logins,
    failed_payments,
    open_tickets,
    ROUND(nps_score, 1) AS nps_score,
    CASE 
        WHEN contract_type = 'Monthly' AND monthly_fee >= 150 AND avg_logins < 10 THEN 'Action: Executive Outreach & Annual Plan Conversion Incentive'
        WHEN failed_payments >= 1 THEN 'Action: Automated Billing Update & Dunning Workflow'
        WHEN open_tickets >= 1 AND nps_score <= 5 THEN 'Action: CSM Escalation & Technical Ticket Resolution'
        ELSE 'Action: Proactive Feature Enablement Webinar'
    END AS recommended_retention_action
FROM customer_health_calc
WHERE (contract_type = 'Monthly' AND avg_logins < 10) OR failed_payments >= 1 OR (open_tickets >= 1 AND nps_score <= 6)
ORDER BY monthly_fee DESC, failed_payments DESC
LIMIT 25;
