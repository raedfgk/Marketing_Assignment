# Marketing Analytics Assignment — Cross-Channel Dashboard

## Overview

This project simulates a real-world marketing analytics workflow: ingesting multi-platform advertising data, unifying it into a clean data model, and delivering actionable insights through an interactive dashboard.

The solution integrates campaign data from **Facebook Ads, Google Ads, and TikTok Ads** into a standardized reporting layer built on **DuckDB**, and visualizes performance using a **Streamlit dashboard**.

The objective is to demonstrate:
- Data modeling across heterogeneous sources
- Metric standardization and validation
- Analytical reasoning on marketing performance
- Clear, decision-oriented visualization

---

## Live Deliverables

- 📊 **Dashboard**: (add your Streamlit link here)
- 🎥 **Walkthrough Video**: (add your video link here)

---

## Project Structure

marketing_assignment/
│
├── README.md
├── requirements.txt
│
├── app/
│ └── dashboard.py # Streamlit dashboard
│
├── data/
│ ├── 01_facebook_ads.csv
│ ├── 02_google_ads.csv
│ ├── 03_tiktok_ads.csv
│ ├── ads_unified.csv # Cleaned + standardized dataset
│ └── ads_reporting.csv # Final reporting dataset
│
├── db/
│ └── marketing.db # DuckDB database
│
└── src/
├── download_data.py # Fetch raw datasets
├── build_database.py # Load + unify data in DuckDB
├── inspect_data.py # Initial exploration
├── explore_results.py # Aggregations / sanity checks
├── validate_metrics.py # Metric validation
└── qa_checks.py # Data quality checks


---

## Data Pipeline

### 1. Data Ingestion
Raw CSV files are downloaded and stored locally:
- Facebook Ads
- Google Ads
- TikTok Ads

Each source has different schemas and platform-specific fields.

---

### 2. Data Unification

A unified dataset (`ads_unified.csv`) is created with:

- Standardized column names:
  - `spend`, `impressions`, `clicks`, `conversions`, `conversion_value`
- Platform identifier (`platform`)
- Campaign name normalization
- Inclusion of platform-specific fields (e.g., video metrics, search metrics)

Missing fields are preserved as `NULL` (not forced to zero).

---

### 3. Reporting Layer

A second dataset (`ads_reporting.csv`) is built for analytics:

Includes derived metrics:

- CTR = clicks / impressions  
- CPC = spend / clicks  
- CPM = spend / impressions * 1000  
- CPA = spend / conversions  
- Conversion Rate = conversions / clicks  
- ROAS = conversion_value / spend  

Also includes:
- Platform-specific KPIs:
  - Video completion rate (TikTok)
  - Social engagement rate (Facebook/TikTok)
  - Search impression share & quality score (Google)

This separation ensures:
- **Unified dataset = clean source of truth**
- **Reporting dataset = analytics-ready layer**

---

### 4. DuckDB Integration

All datasets are loaded into a DuckDB database: 

db/marketing.db



DuckDB is used for:
- Fast local querying
- SQL-based validation
- Scalable analytical workflows

---

## Dashboard

Built with **Streamlit + Plotly**, the dashboard provides a structured analytical view:

### 1. Executive Summary
- Core KPIs:
  - Spend, Revenue, Impressions, Clicks, Conversions
  - CTR, CPC, CPM, CPA, Conversion Rate, ROAS
- Interactive tooltips explaining each metric

---

### 2. Channel Overview
- Spend share vs conversion share
- Efficiency comparison across platforms
- Time-series performance trends

---

### 3. Campaign Analysis
- Top campaigns by selected metric
- Fully sortable and filterable
- Clean labeling for readability

---

### 4. Platform Diagnostics

#### Google (Search-focused)
- CPA, ROAS, Impression Share
- Quality Score (weighted)

#### Social & Video (Facebook + TikTok)
- Video completion rate
- Engagement rate
- Cost per reach

Platform-specific metrics are displayed **only when relevant** (no misleading zeros).

---

## Key Insights

### 1. Retargeting Efficiency (Facebook)
- High share of total conversions
- Competitive CPA relative to other platforms
- Acts as a **bottom-of-funnel conversion driver**

→ Interpretation:  
Retargeting efficiently captures demand rather than generating it.

---

### 2. Google Ads — High ROAS Channel
- Strong revenue generation
- High conversion efficiency
- Balanced cost structure

→ Interpretation:  
Google Search is the primary **performance driver**.

---

### 3. TikTok — Scale with Lower Efficiency
- Highest spend and impressions
- Strong traffic generation
- Higher CPA and weaker conversion efficiency

→ Interpretation:  
TikTok is primarily **top-of-funnel**, feeding downstream conversions.

---

### 4. Funnel Structure

The ecosystem behaves as:

- TikTok → Demand generation  
- Google → High-intent capture  
- Facebook Retargeting → Conversion closure  

---

## Data Quality & Validation

Several checks were implemented:

- No division-by-zero errors in metric calculations
- Null-safe aggregation (`min_count=1`)
- Platform-specific fields handled correctly
- Cross-platform metric consistency
- DuckDB validation queries

---

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt


### 2. Build Database

python src/build_database.py

### 3. Run Dashboard

streamlit run app/dashboard.py
```


---
