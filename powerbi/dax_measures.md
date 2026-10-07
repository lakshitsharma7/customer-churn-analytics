# 📐 CloudSync Power BI DAX Measures & Formulas Repository

This document contains all production-grade Data Analysis Expressions (DAX) used to build the 6-page interactive **CloudSync Customer Churn & Retention Analytics Power BI Dashboard**.

---

## 1. Core Subscriber Base & Volume Measures

### `[Total Customers]`
```dax
Total Customers = 
DISTINCTCOUNT(DimCustomer[customer_id])
```

### `[Active Customers]`
```dax
Active Customers = 
CALCULATE(
    DISTINCTCOUNT(FactSubscriptions[customer_id]),
    FactSubscriptions[subscription_status] = "Active"
)
```

### `[Churned Customers]`
```dax
Churned Customers = 
CALCULATE(
    DISTINCTCOUNT(FactSubscriptions[customer_id]),
    FactSubscriptions[subscription_status] = "Churned"
)
```

### `[Paused Customers]`
```dax
Paused Customers = 
CALCULATE(
    DISTINCTCOUNT(FactSubscriptions[customer_id]),
    FactSubscriptions[subscription_status] = "Paused"
)
```

---

## 2. Retention & Churn Rates

### `[Overall Churn Rate %]`
```dax
Overall Churn Rate % = 
DIVIDE(
    [Churned Customers],
    [Total Customers],
    0
)
```

### `[Customer Retention Rate %]`
```dax
Customer Retention Rate % = 
1 - [Overall Churn Rate %]
```

### `[MoM Churn Growth %]`
```dax
MoM Churn Growth % = 
VAR CurrentMonthChurn = [Churned Customers]
VAR PriorMonthChurn = 
    CALCULATE(
        [Churned Customers],
        DATEADD(DimDate[Date], -1, MONTH)
    )
RETURN
DIVIDE(
    CurrentMonthChurn - PriorMonthChurn,
    PriorMonthChurn,
    0
)
```

---

## 3. Financial & Revenue Metrics (MRR, ARR, ARPU, LTV)

### `[Monthly Recurring Revenue (MRR)]`
```dax
MRR = 
CALCULATE(
    SUM(FactSubscriptions[monthly_fee]),
    FactSubscriptions[subscription_status] = "Active"
)
```

### `[Annual Recurring Revenue (ARR)]`
```dax
ARR = 
[MRR] * 12
```

### `[Average Revenue Per User (ARPU)]`
```dax
ARPU = 
DIVIDE(
    [MRR],
    [Active Customers],
    0
)
```

### `[Monthly Revenue Lost to Churn]`
```dax
Monthly Revenue Lost = 
CALCULATE(
    SUM(FactSubscriptions[monthly_fee]),
    FactSubscriptions[subscription_status] = "Churned"
)
```

### `[Annualized Revenue Lost to Churn]`
```dax
Annualized Revenue Lost = 
[Monthly Revenue Lost] * 12
```

### `[Average Active Customer Tenure]`
```dax
Avg Active Tenure (Months) = 
CALCULATE(
    AVERAGE(FactSubscriptions[tenure_months]),
    FactSubscriptions[subscription_status] = "Active"
)
```

### `[Customer Lifetime Value (LTV)]`
```dax
Customer Lifetime Value = 
[ARPU] * [Avg Active Tenure (Months)]
```

---

## 4. Product Engagement & Telemetry Measures

### `[Avg Monthly Logins]`
```dax
Avg Monthly Logins = 
AVERAGE(FactActivity[login_count])
```

### `[Avg Active Days per Month]`
```dax
Avg Active Days = 
AVERAGE(FactActivity[active_days])
```

### `[Avg Session Duration]`
```dax
Avg Session Duration (Mins) = 
AVERAGE(FactActivity[avg_session_minutes])
```

### `[Avg Feature Breadth]`
```dax
Avg Feature Breadth = 
AVERAGE(FactActivity[features_used])
```

---

## 5. Support & Customer Service Quality Measures

### `[Total Support Tickets]`
```dax
Total Support Tickets = 
COUNT(FactSupport[ticket_id])
```

### `[Avg Resolution Time (Hours)]`
```dax
Avg Resolution Time (Hours) = 
AVERAGE(FactSupport[resolution_time_hours])
```

### `[Unresolved Support Tickets]`
```dax
Unresolved Tickets = 
CALCULATE(
    COUNT(FactSupport[ticket_id]),
    FactSupport[ticket_status] IN {"Pending", "Escalated"}
)
```

### `[Average Support CSAT]`
```dax
Avg Support CSAT = 
AVERAGE(FactSupport[satisfaction_score])
```

---

## 6. Feedback & Voice of Customer Measures

### `[Average NPS Score]`
```dax
Avg NPS = 
AVERAGE(DimCustomer[nps_score])
```

### `[NPS Promoters Count]`
```dax
NPS Promoters = 
CALCULATE(
    COUNTROWS(DimCustomer),
    DimCustomer[nps_score] >= 9
)
```

### `[NPS Detractors Count]`
```dax
NPS Detractors = 
CALCULATE(
    COUNTROWS(DimCustomer),
    DimCustomer[nps_score] <= 6
)
```

### `[Net Promoter Score Index %]`
```dax
NPS Index % = 
VAR TotalFeedback = COUNTROWS(FILTER(DimCustomer, NOT(ISBLANK(DimCustomer[nps_score]))))
RETURN
DIVIDE([NPS Promoters] - [NPS Detractors], TotalFeedback, 0) * 100
```

---

## 7. Predictive Risk & Customer Health Scoring Measures

### `[Customer Health Score (Avg)]`
```dax
Avg Health Score = 
AVERAGE(DimCustomer[health_score])
```

### `[High Risk Customers Count]`
```dax
High Risk Customers = 
CALCULATE(
    [Active Customers],
    DimCustomer[risk_category] = "High Risk"
)
```

### `[High Risk MRR at Stake]`
```dax
High Risk MRR = 
CALCULATE(
    [MRR],
    DimCustomer[risk_category] = "High Risk"
)
```

### `[Risk Level Indicator Format]` (for Conditional Formatting)
```dax
Risk Color Code = 
SWITCH(
    SELECTEDVALUE(DimCustomer[risk_category]),
    "High Risk", "#E53E3E",
    "Medium Risk", "#DD6B20",
    "Low Risk", "#38A169",
    "#718096"
)
```
