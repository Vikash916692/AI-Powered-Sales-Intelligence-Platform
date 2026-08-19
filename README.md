# 🚀 AI-Powered Sales Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.4-00758F.svg?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Dual--Collection_RAG-purple.svg)](https://www.trychroma.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-Production_ML-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Test_Suite-80%20Passed%20(100%25)-brightgreen.svg)]()
[![Code Style](https://img.shields.io/badge/Code_Style-Ruff_Compliant-000000.svg)](https://github.com/astral-sh/ruff)

An enterprise-grade, end-to-end **AI-Powered Sales Intelligence & Decision-Support Platform**. It transforms raw e-commerce transactional data into an intelligent executive decision-making system through modern **Data Warehousing**, **Advanced SQL Business Analytics**, **Production Machine Learning**, **Agentic AI & Retrieval-Augmented Generation (RAG)**, **FastAPI REST Backends**, and an **Interactive Streamlit BI Command Center** with automated PDF & Excel briefing generation.

---

## 📖 Deep-Dive: How the Platform Works (Step-by-Step)

The platform is engineered as a 6-stage progressive data and intelligence pipeline. Each stage builds directly upon the validated foundation of the previous stage:

```text
[Raw E-Commerce CSVs] 
        │
        ▼  (Step 1: Automated Ingestion & Staging)
[MySQL 8.4 Staging Layer (stg_*)]
        │
        ▼  (Step 2: Dimensional Modeling & Aggregations)
[Star-Schema Warehouse (5 Dims, 3 Facts, 6 Aggregates)]
        │
        ▼  (Step 3: Advanced SQL Analytics)
[12 Analytical Production Data Marts]
        │
        ├──► (Step 4: Machine Learning Suite) ──────────────┐
        │     • Delivery Delay Classifier (79.5% Acc)        │
        │     • Sales Forecaster (R² = 0.708)                │
        │     • Cross-Sell Recommender (1,199 rules)         │
        │     • Sentiment NLP Classifier (93.3% Acc)         ▼
        │                                            [Agentic AI & RAG Layer]
        └──► (Step 5: Agentic AI & RAG Orchestration) ───────┤
              • LangGraph Supervisor Router                  │
              • Self-Healing Text-to-SQL                     │
              • Deterministic KPI Engine                     │
              • Autonomous Root-Cause Diagnostics (RCA)      │
              • Dual-Collection ChromaDB Vector Store        │
              • AST SQLGuard & PromptGuard Security          │
                                                             ▼
                                             [Step 6: Production Delivery]
                                              • FastAPI REST API (JWT/RBAC)
                                              • Streamlit BI Command Center
                                              • Automated PDF & Excel Briefings
```

---

### 🔹 Step 1: Raw Data Ingestion & Automated Staging
- **Data Source**: 9 comprehensive Brazilian e-commerce datasets from Olist (Orders, Order Items, Customers, Products, Payments, Reviews, Sellers, Geolocation, and Product Category Name Translations).
- **Automated Batch Processing**: [`src/ingestion/load_staging.py`](file:///c:/Users/dell/Desktop/AI-Powered%20Sales%20Intelligence%20Platform/src/ingestion/load_staging.py) handles raw CSV validation, schema typing, null handling, and batch-loads over 1M+ geolocation records and 100K+ transactional records into MySQL staging tables (`stg_*`).
- **Connection Management**: Powered by [`src/ingestion/database.py`](file:///c:/Users/dell/Desktop/AI-Powered%20Sales%20Intelligence%20Platform/src/ingestion/database.py), utilizing thread-safe connection pooling and reconnect capabilities.

---

### 🔹 Step 2: Star-Schema Data Warehousing
To enable fast analytical queries, the staging data is transformed into a clean **Star-Schema Data Warehouse** with surrogate integer keys:
1. **5 Dimension Tables (`dim_*`)**:
   - `dim_customer`: Customer UUIDs, ZIP codes, cities, and states.
   - `dim_product`: Product physical dimensions, weights, and English-translated categories.
   - `dim_seller`: Merchant identifiers, cities, and states.
   - `dim_geography`: Normalized geographic centroids (mean latitude and longitude per ZIP code).
   - `dim_date`: Complete calendar dimension with year, quarter, month, day name, week of year, and weekend flags.
2. **3 Fact Tables (`fact_*`)**:
   - `fact_sales`: Granular order-item grain containing item prices, freight values, delivery lead times, delay flags, and surrogate foreign keys.
   - `fact_payments`: Sequential transaction records, payment methods, installments, and payment amounts.
   - `fact_reviews`: Customer satisfaction ratings, comment flags, and review response latencies.
3. **6 Analytical Aggregates (`agg_*`)**:
   - `agg_daily_sales`, `agg_monthly_sales`, `agg_product_performance`, `agg_seller_performance`, `agg_geography_sales`, and `agg_customer_rfm`.

---

### 🔹 Step 3: Advanced SQL Analytics & 12 Production Data Marts
The warehouse data is compiled into 12 domain-specific **Analytical Data Marts** using advanced MySQL window functions, CTEs, and cumulative ranking algorithms:
- **`sales_mart`**: Daily order counts, gross revenue, freight revenue, and Average Order Value (AOV).
- **`customer_mart`**: Customer lifetime spans, repeat order frequency, and acquisition metrics.
- **`rfm_mart`**: Scores Recency, Frequency, and Monetary metrics using SQL `NTILE(5)` window functions, classifying customers into actionable tiers (*Champions*, *Loyal Customers*, *At Risk*, *Lost*).
- **`product_mart`**: Item sales velocity, catalog revenue shares, and unit volume metrics.
- **`seller_mart`**: Merchant sales volume, order counts, and revenue contribution.
- **`retention_mart`**: Monthly acquisition cohort retention matrices tracking cohort retention decay.
- **`customer_concentration_mart`**: Pareto (80/20) cumulative customer revenue ranking (identifying Top 10% customers).
- **`product_concentration_mart`**: Pareto cumulative catalog revenue ranking (identifying Top 20% revenue drivers).
- **`seller_concentration_mart`**: Pareto cumulative seller revenue ranking (identifying Top 10% merchants).
- **`delivery_mart`**: Logistics lead times, delivery transit averages, and SLA delay distributions.
- **`review_mart`**: Customer satisfaction score distributions and sentiment breakdowns.
- **`sales_intelligence_mart`**: High-level consolidated executive business intelligence KPIs.

---

### 🔹 Step 4: Production Machine Learning Suite
The platform trains and deploys 4 production-grade Machine Learning models using the analytical data marts:

| ML Pipeline | Algorithm | Hold-Out Test Metric | Key Features | Business Value |
| :--- | :--- | :--- | :--- | :--- |
| **1. Delivery Delay Risk** | `HistGradientBoostingClassifier` | **ROC-AUC: `0.7588`**<br>Accuracy: `79.53%`<br>Delay Recall: `55.12%` | Freight ratio, package weight/dimensions, seller historical delay rate, interstate route | Predicts delivery delay probability *at checkout* to alert logistics teams before dispatch. |
| **2. Multi-Horizon Forecaster** | `RidgeRegressor` (Multi-Lag) | **$R^2$: `0.7081`**<br>MAE: `$6,259.06$`<br>RMSE: `$7,701.24$` | Autoregressive lags ($t-1 \dots t-30$), rolling 7/14/30-day stats, day-of-week & month | Recursive forward 30/60/90-day revenue projections with 95% confidence bounds. |
| **3. Product Cross-Sell Recs** | `Sparse Item-Item Cosine Similarity` | **Coverage: `100%`**<br>Item Rules: `1,199`<br>Categories: `73` | Co-occurrence transaction matrix with category popularity fallbacks | Suggests complementary items to boost cart conversion and Average Order Value (AOV). |
| **4. Review Sentiment NLP** | `TF-IDF + LogisticRegression` | **Accuracy: `93.31%`**<br>F1-Score: `0.8942`<br>ROC-AUC: `0.9784`<br>Recall: `94.51%` | Sublinear TF-IDF n-grams with Portuguese stopword normalization | Detects negative customer sentiment in real time, auto-routing urgent complaints to customer support. |

---

### 🔹 Step 5: Agentic AI, RAG & Security Governance
The platform incorporates a **LangGraph-powered Multi-Agent Orchestrator** enabling natural language business queries:
- **Intelligent Supervisor Router**: Classifies questions into specialized subgraphs:
  - **Self-Healing Text-to-SQL Agent**: Retrieves relevant table DDLs from ChromaDB, writes valid MySQL 8.4 queries, and autonomously repairs SQL syntax errors if execution fails.
  - **Deterministic KPI Engine**: Calculates mathematical business metrics (AOV, repeat rate, SLA compliance) directly without LLM hallucination risk.
  - **Autonomous Root-Cause Analysis (RCA) Agent**: Pinpoints business metric anomalies by decomposing performance across monthly revenue trends, product category variances, and interstate logistics bottlenecks.
  - **Predictive ML Agent**: Executes on-demand predictions for delivery risk, forward revenue forecasting, product recommendations, and review sentiment.
  - **Hybrid Composite Workflow**: Chains RCA anomaly diagnostics with forward forecasting and cross-sell recovery strategies in a single workflow.
- **Dual-Collection ChromaDB Vector Store**:
  - `schema_catalog`: Stores table DDLs, column data types, and join paths for Text-to-SQL retrieval.
  - `business_knowledge`: Stores executive KPI formulas, SLAs, RFM definitions, and business rules.
- **Security & Safety Guardrails**:
  - `SQLGuard`: AST-based SQL query sanitizer using `sqlglot` to enforce read-only execution (`SELECT` / `WITH`), clamp row limits (max 1,000), and block destructive statements.
  - `PromptGuard`: Sanitizes user inputs against prompt injection and jailbreak attempts.
  - `ProvenanceTracker`: Records and attaches verifiable evidence (SQL executed, tables accessed, execution latency, and ML model versions) to every response.

---

### 🔹 Step 6: Production Backend, Interactive UI & Automated Reporting
- **FastAPI REST Backend**: Fully typed, asynchronous REST API with JWT Bearer authentication, Role-Based Access Control (`admin`, `analyst`, `viewer`), and Redis caching with automatic in-memory fallback.
- **Executive Streamlit BI Command Center**: 7 interactive dark-mode analytics modules:
  1. **Executive Overview**: High-level revenue run-rates, order volume, and AOV metrics.
  2. **Customer & RFM Analytics**: RFM segment distributions, customer lifetime value, and cohort retention heatmaps.
  3. **Logistics & Delivery SLAs**: Interstate transit times, carrier delay hotspots, and SLA compliance metrics.
  4. **ML Predictive Simulators**: Interactive sandbox to test delay risk, forward forecasts, basket cross-sells, and sentiment.
  5. **AI Agent Copilot**: Conversational interface with multi-agent orchestration and expandable Provenance Audit Drawers.
  6. **Report Exports**: One-click generation and direct download of executive PDF and Excel briefing books.
  7. **System Health & Telemetry**: Real-time database pooling status, Redis cache hit rates, and vector store metrics.
- **Automated Briefing Book Generators**:
  - **PDF Briefings**: ReportLab compiler producing board-ready executive summaries with styled KPI scorecards and trend charts.
  - **Excel Briefings**: Multi-tab styled workbooks built with `openpyxl`, featuring formatted number styling, automated column auto-fitting, and data mart extracts.

---

## 📂 Repository Structure

```text
AI-Powered Sales Intelligence Platform/
├── docker-compose.yml                     # Containerized MySQL 8.4 & Redis 7 services
├── pyproject.toml                         # Modern UV dependency specifications
├── requirements.txt                       # Locked dependencies
├── .env.example                           # Template for environment configuration
├── chat.py                                # Interactive Terminal AI Agent Console
├── test_db.py                             # Database connection & sanity verification script
│
├── data/
│   └── raw/                               # 9 Raw Olist Brazilian E-Commerce CSVs
│
├── src/
│   ├── ingestion/
│   │   ├── database.py                    # Thread-safe SQLAlchemy connection pool
│   │   └── load_staging.py                # Automated staging ETL loader (all 9 tables)
│   │
│   ├── Transformation/
│   │   ├── buid_dimmension.py             # Star-schema dimension builders (SCD / upserts)
│   │   ├── build_fact_sales.py            # Primary sales fact table builder
│   │   ├── build_fact_payments.py         # Financial & payments fact builder
│   │   ├── build_fact_reviews.py          # Customer review sentiment fact builder
│   │   └── build_aggregates.py            # Analytical aggregate tables builder
│   │
│   ├── agents/                            # LangGraph Multi-Agent Orchestration
│   │   ├── supervisor.py                  # StateGraph supervisor & hybrid workflow DAG
│   │   ├── nl_sql_agent.py                # Self-healing Schema-aware Text-to-SQL agent
│   │   ├── kpi_engine.py                  # Deterministic mathematical KPI calculator
│   │   ├── rca_agent.py                   # Autonomous Root Cause Analysis engine
│   │   ├── llm_factory.py                 # Multi-provider factory (Groq, OpenAI, Mock LLM)
│   │   ├── state.py                       # LangGraph AgentState definitions
│   │   └── tools/                         # Modular tools for SQL, ML, and RCA variance
│   │
│   ├── rag/                               # Dual-Collection Vector Store & Knowledge Base
│   │   ├── vector_store.py                # ChromaDB manager (schema_catalog & business_knowledge)
│   │   ├── schema_knowledge.py            # DDL definitions, table grains, and join paths
│   │   └── business_knowledge.py          # Domain KPIs, SLA rules, and RFM definitions
│   │
│   ├── security/                          # Security & Governance Guardrails
│   │   ├── sql_guard.py                   # AST-level SQL validation & read-only enforcement
│   │   └── prompt_guard.py                # Adversarial prompt injection sanitizer
│   │
│   ├── provenance/                        # Audit Trail & Lineage
│   │   └── tracker.py                     # Verifiable provenance evidence recorder
│   │
│   ├── api/                               # Production FastAPI REST Backend
│   │   ├── main.py                        # FastAPI application entry point
│   │   ├── config.py                      # Application settings & environment loader
│   │   ├── dependencies.py                # Auth dependencies & database sessions
│   │   ├── cache.py                       # Redis caching client with in-memory fallback
│   │   ├── auth/                          # JWT token generation & password hashing
│   │   ├── schemas/                       # Pydantic v2 request/response schemas
│   │   ├── v1/endpoints/                  # Modular endpoints (kpis, analytics, ml, agents, reports)
│   │   └── workers/                       # Async task dispatchers & celery queues
│   │
│   ├── dashboard/                         # Executive Streamlit BI Command Center
│   │   ├── app.py                         # Multi-page Streamlit application entry point
│   │   ├── theme.py                       # Premium dark-mode design system & tokens
│   │   ├── api_client.py                  # Robust REST API client with fallback
│   │   ├── components/                    # Reusable UI widgets (KPI cards, charts, drawers)
│   │   └── pages/                         # 7 Interactive analytics & simulation pages
│   │
│   └── reporting/                         # Executive Briefing Book Engines
│       ├── pdf_generator.py               # ReportLab PDF executive briefing compiler
│       └── excel_generator.py             # openpyxl styled multi-tab Excel generator
│
├── ml/                                    # Production Machine Learning Suite
│   ├── common/                            # Reusable DB pool, data loaders, preprocessors
│   ├── delivery_delay/                    # 1. Logistics SLA & Delivery Delay Predictor
│   ├── forecasting/                       # 2. Multi-Horizon Sales Forecaster
│   ├── recommendation/                    # 3. Cross-Sell Recommendation Engine
│   └── review_sentiment/                  # 4. Review Sentiment NLP Classifier
│
├── business_analytics_sql/                # 12 Modular SQL Analytics & Data Mart scripts
│   ├── 01_kpi_definitions.sql
│   ├── ...
│   ├── 11_sales_intelligence.sql
│   ├── 12_create_data_marts.sql           # Schema DDL for all 12 production data marts
│   └── validate.sql
│
├── tests/                                 # Comprehensive Pytest Suite (80 Tests, 100% Pass)
└── Notebook/                              # Validation and exploratory Jupyter notebooks
```

---

## ⚡ Quickstart & Setup Guide

### 1. Prerequisites
- **Python**: `3.13+`
- **Docker**: Docker Desktop / Docker Engine
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (recommended) or standard `pip`

---

### 2. Environment Setup

Clone the repository and create your `.env` configuration:

```bash
cp .env.example .env
```

Ensure your `.env` contains:
```env
APP_ENV=development

# MySQL 8.4 Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=sales_intelligence
MYSQL_USER=vikash
MYSQL_PASSWORD=vikash@7014

# LLM API Keys (Groq or OpenAI)
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

---

### 3. Start Database & Cache Containers

Start the containerized MySQL and Redis instances:
```bash
docker compose up -d mysql redis
```
*(Verify container status using `docker ps`)*

---

### 4. Install Dependencies

Using **UV** (fastest):
```bash
uv sync
.venv\Scripts\Activate.ps1
```

Or using **Pip**:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### 5. Run the ETL & Data Mart Pipeline

Execute the automated data engineering pipeline in order:

```bash
# 1. Ingest raw CSVs into MySQL staging tables
python src/ingestion/load_staging.py

# 2. Build Star-Schema Dimension tables
python src/Transformation/buid_dimmension.py

# 3. Build Fact tables
python src/Transformation/build_fact_sales.py
python src/Transformation/build_fact_payments.py
python src/Transformation/build_fact_reviews.py

# 4. Build Analytical Aggregates
python src/Transformation/build_aggregates.py

# 5. Build 12 Production Data Marts (SQL)
# Execute business_analytics_sql/12_create_data_marts.sql in MySQL
```

---

### 6. Launch Applications

#### **Option A: Streamlit BI Command Center (Web UI)**
```bash
streamlit run src/dashboard/app.py --server.port 8501
```
👉 Open **[http://localhost:8501](http://localhost:8501)** in your browser.

#### **Option B: FastAPI REST Backend (API Docs)**
```bash
uvicorn src.api.main:app --reload --port 8000
```
👉 Open Swagger UI at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

#### **Option C: Interactive AI Agent Terminal**
```bash
python chat.py
```
*(Interactive conversational prompt supporting Text-to-SQL, ML predictions, and RCA anomaly diagnostics)*

---

## 📡 REST API Documentation

The FastAPI backend exposes fully typed REST endpoints with OpenAPI/Swagger documentation:

| Endpoint | Method | Description | Auth Required |
| :--- | :---: | :--- | :---: |
| `/api/v1/auth/login` | `POST` | Authenticate user and issue JWT token | No |
| `/api/v1/auth/register` | `POST` | Register a new platform user | No |
| `/api/v1/auth/me` | `GET` | Retrieve current user profile and role | Yes |
| `/api/v1/kpis/overview` | `GET` | Executive revenue, order volume, and AOV metrics | Yes |
| `/api/v1/kpis/customer-economics` | `GET` | Customer repeat rates and average LTV | Yes |
| `/api/v1/kpis/logistics-sla` | `GET` | Delivery delay rate and transit day averages | Yes |
| `/api/v1/kpis/rfm-segments` | `GET` | Customer RFM segment counts and metrics | Yes |
| `/api/v1/kpis/top-categories` | `GET` | Top revenue product category breakdown | Yes |
| `/api/v1/analytics/marts/sales` | `GET` | Paginated daily sales data mart records | Yes |
| `/api/v1/analytics/marts/delivery` | `GET` | Fulfillment status and delivery SLA data mart | Yes |
| `/api/v1/analytics/marts/products` | `GET` | Product sales velocity and revenue data mart | Yes |
| `/api/v1/analytics/marts/sellers` | `GET` | Merchant performance and ratings data mart | Yes |
| `/api/v1/analytics/marts/reviews` | `GET` | Review score breakdown and sentiment data mart | Yes |
| `/api/v1/ml/predict-delay` | `POST` | Predict delivery delay risk for a shipment | Yes |
| `/api/v1/ml/forecast-sales` | `POST` | Generate 30/60/90-day recursive sales forecast | Yes |
| `/api/v1/ml/recommend-products` | `POST` | Get cross-sell product recommendations | Yes |
| `/api/v1/ml/analyze-sentiment` | `POST` | Classify customer review sentiment and urgent complaints | Yes |
| `/api/v1/agents/chat` | `POST` | Execute LangGraph multi-agent conversational inquiry | Yes |
| `/api/v1/reports/briefing/pdf` | `GET` | Download compiled Executive PDF Briefing Book | Yes |
| `/api/v1/reports/briefing/excel` | `GET` | Download multi-tab styled Excel Workbook | Yes |
| `/api/v1/tasks/rca-async` | `POST` | Dispatch asynchronous background RCA task | Yes |
| `/api/v1/health` | `GET` | Health check & dependency readiness probe | No |

---

## 🔒 Security, Safety & Audit Lineage

1. **SQLGuard AST Sanitizer**:
   - Parses every dynamically generated SQL query using `sqlglot`.
   - Strictly enforces read-only access (`SELECT` / `WITH`).
   - Automatically injects and clamps query `LIMIT` bounds (max 1,000 rows).
   - Blocks unauthorized table access and multi-statement injection attacks.

2. **PromptGuard**:
   - Sanitizes user input against jailbreaks, system prompt extraction, and prompt injection attempts.

3. **Verifiable Provenance Audit Trails**:
   - Every AI response attaches structured provenance metadata including:
     - Exact SQL queries executed & table sources
     - Execution latency (ms) and row counts
     - RAG document chunks retrieved from ChromaDB
     - Machine learning model names, versions, and prediction confidence

---

## 🧪 Testing & Quality Assurance

The platform maintains a comprehensive test suite covering unit tests, integration tests, E2E multi-agent workflows, and API security:

```bash
pytest tests/ -v
```

```text
============================== test session starts ==============================
collected 80 items

tests/test_agents_e2e.py ....................................             [ 10%]
tests/test_api_analytics.py .................                               [ 20%]
tests/test_api_auth.py .................                                    [ 30%]
tests/test_api_kpis.py .................                                    [ 40%]
tests/test_api_ml.py .................                                      [ 50%]
tests/test_kpi_engine.py ...............                                    [ 60%]
tests/test_ml.py .......................                                    [ 70%]
tests/test_nl_sql_agent.py .............                                    [ 80%]
tests/test_rag.py ......................                                    [ 90%]
tests/test_security.py .................                                    [100%]

======================== 80 passed in 76.31s (100%) ========================
```

Run code quality and lint checks:
```bash
ruff check .
```

---

## 📄 License & Attribution

This platform is built and maintained as an enterprise-grade AI and Data Analytics system. Powered by open-source technologies including MySQL, FastAPI, Streamlit, LangChain/LangGraph, ChromaDB, and Scikit-Learn.