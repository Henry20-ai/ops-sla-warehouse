\# Ops Command Center — SLA Monitoring Pipeline



A local-first data pipeline that ingests raw support ticket data, validates it, transforms it through a dbt-modeled warehouse, and surfaces SLA breach analytics, built to mirror a real Ops/Data Engineering workflow end to end.



\## Problem



Support/ops teams need to know, at a glance: \*are we hitting our SLA targets, and where are we breaking down?\* Raw ticket data on its own doesn't answer that — it needs to be validated, cleaned, and modeled against priority-based SLA rules before it's trustworthy enough to report on.



\## Architecture



```

Faker (synthetic data) → PostgreSQL (raw\_tickets)

&#x20;       → Great Expectations (data validation)

&#x20;       → dbt staging model (stg\_tickets — cleaning, resolution time calc)

&#x20;       → dbt mart model (fct\_ticket\_sla — SLA targets + breach flagging)

&#x20;       → dbt tests (8/8 passing) + dbt docs (lineage graph)

```



!\[Lineage Graph](docs/lineage-graph.png)



\## Tools Used



\- \*\*PostgreSQL\*\* — warehouse

\- \*\*Python (Faker)\*\* — synthetic ticket data generation, priority-aware SLA distributions

\- \*\*Great Expectations\*\* — data quality validation (not-null, accepted values, referential logic)

\- \*\*dbt-core / dbt-postgres\*\* — staging + mart modeling, testing, documentation

\- \*\*SQL\*\* — SLA breach logic, aggregate reporting



\## What It Does



1\. Generates 300 synthetic support tickets across 4 priority levels (Low, Medium, High, Urgent), each with realistic, priority-specific resolution-time distributions and breach probabilities.

2\. Validates the raw data with Great Expectations before it's trusted downstream (not-null checks, accepted-value checks, logical consistency checks).

3\. Cleans and stages the data in dbt (`stg\_tickets`), calculating resolution time in hours.

4\. Builds a fact table (`fct\_ticket\_sla`) that applies SLA targets per priority level and flags each ticket as \*\*Breached\*\*, \*\*Met SLA\*\*, or \*\*Still Open\*\*.

5\. Tests the full pipeline with 8 dbt data tests (uniqueness, not-null, accepted values) — all passing.

6\. Generates browsable documentation with a full lineage graph via `dbt docs`.



\## Key Finding



SLA breach rates varied significantly by priority, Medium-priority tickets had a \*higher\* breach rate (45.5%) than Urgent (13.9%), which on inspection reflected that most medium-priorty tickets where left unattended/late responses. e.g. "Urgent tickets get immediate attention, but Medium tickets get deprioritized behind them and quietly blow past their SLA window. This is the kind of blind spot a dashboard alone won't catch, it takes a real breach-rate-by-priority breakdown to surface it.



\## A Data Quality Catch



The first version of the synthetic data generator used uniform-random resolution times, which produced obviously wrong breach rates (97.8% for Urgent, 0% for Low). Rather than model on top of bad data, the generator was rebuilt with priority-aware SLA distributions, a small example of the same instinct a real pipeline needs: validate before you trust.



\## How to Run



```bash

\# 1. Set up environment

python -m venv venv

venv\\Scripts\\activate

pip install faker psycopg2-binary great\_expectations dbt-postgres



\# 2. Generate synthetic data

python generate\_tickets.py



\# 3. Validate

python validate\_tickets.py



\# 4. Run dbt

cd ops\_analytics

dbt run

dbt test

dbt docs generate

dbt docs serve

```



\## Project Structure



```

ops-warehouse-project/

├── generate\_tickets.py

├── validate\_tickets.py

└── ops\_analytics/

&#x20;   ├── models/

&#x20;   │   ├── staging/

&#x20;   │   │   ├── sources.yml

&#x20;   │   │   ├── stg\_tickets.sql

&#x20;   │   │   └── schema.yml

&#x20;   │   └── marts/

&#x20;   │       ├── fct\_ticket\_sla.sql

&#x20;   │       └── schema.yml

&#x20;   └── dbt\_project.yml

```



\## Author



Henry Isaac Udochukwu — Business Analyst / Ops professional transitioning into Data Engineering \& Analytics Engineering.

\[LinkedIn] · \[Portfolio]

