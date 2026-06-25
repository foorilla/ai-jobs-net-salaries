# CONTEXT

Glossary of domain terms for the AI/ML Global Salary dataset project.

## Data Source

- **aijobs.net salaries**: Anonymous salary survey collected weekly at [aijobs.net/salaries](https://aijobs.net/salaries/) from 2020 to 2025. Published under CC0 (public domain). 151,445 records, 11 fields.

## Fields

- **salary_in_usd**: Annual gross salary converted to USD (exchange rate at time of collection). This is the canonical salary field used in all analyses; the raw `salary` + `salary_currency` pair is retained for provenance.
- **experience_level**: EN (Entry), MI (Mid), SE (Senior), EX (Executive). Self-reported by survey respondents.
- **employment_type**: FT (Full-time), PT (Part-time), CT (Contract), FL (Freelance). Heavily skewed toward FT (~99%).
- **remote_ratio**: 0 (on-site), 50 (hybrid), 100 (fully remote). Treated as categorical. Hybrid is rare (~0.2%).
- **company_size**: S (<50 employees), M (50–250), L (>250). Heavily skewed toward M (~97%).
- **company_location**: ISO 3166-1 alpha-2 country code where the employer is based.
- **employee_residence**: ISO 3166-1 alpha-2 country code where the employee lives.

## Salary Bins

Five tiers used for Sankey and categorical analysis:

| Tier | Range (USD) | Label |
|------|-------------|-------|
| Entry | < $80,000 | 入门 |
| Junior | $80,000 – $120,000 | 初级 |
| Mid | $120,000 – $160,000 | 中级 |
| Senior | $160,000 – $220,000 | 高级 |
| Top | > $220,000 | 顶级 |

## Job Categories

422 raw job titles are mapped to 9 categories via keyword-priority rules. Categories are ranked by commercial specificity: AI/ML-specialized roles take priority over generic engineering or analyst roles.

| Category | Covers |
|----------|--------|
| **AI/ML Specialist** | ML Engineer, AI Engineer, ML Researcher, ML Scientist, AI Architect, Applied Scientist |
| **Data Scientist** | Data Scientist (standalone — largest single title at 12% of dataset) |
| **Data Engineer** | Data Engineer, Analytics Engineer, Data Architect, Platform Engineer |
| **Software Engineer** | Software Engineer, Engineer, Developer, Backend Engineer, Systems Engineer, DevOps, SRE |
| **Data Analyst** | Data Analyst, Analyst, BI Analyst, Business Analyst, Research Analyst, BI Developer |
| **Management** | Manager, Director, Head of Data, Engineering Manager, Data Manager, Data Lead |
| **Research** | Research Scientist, Research Engineer |
| **Product & Consulting** | Product Manager, Consultant, Data Product Manager, Associate, Solutions Architect |
| **Other** | All remaining titles not matched by the above rules (~9% of records) |

## Data Types

Three data types are targeted to meet assignment requirements:

- **定性数据 (Qualitative)**: job_title, experience_level, company_size, employment_type — categorical variables used for grouping and comparison.
- **时间序列 (Time-series)**: work_year (2020–2025) — used for trend analysis and the Timeline interactive chart.
- **空间数据 (Spatial)**: company_location (ISO alpha-2) — used for the global salary choropleth map.

## Related Documents

- `大作业内容结构.md` — Required notebook structure and chart specifications
- `eda_plan_salaries.md` — Initial EDA plan (some decisions superseded by this context)
- `DATASET.md` — Field distribution summaries
