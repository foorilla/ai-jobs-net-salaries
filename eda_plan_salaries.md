# EDA Plan for Global Salaries in AI/ML/Data Science Dataset

## 1. Data Loading & Initial Inspection

```python
import pandas as pd
import numpy as np
import pyecharts
from pyecharts import options as opts
from pyecharts.charts import Bar, Map, Line, Pie, Sankey, Scatter
import seaborn as sns
import matplotlib.pyplot as plt

# Load CSV (recommended for pyecharts compatibility)
df = pd.read_csv('salaries.csv')

# Initial inspection
df.shape, df.columns.tolist(), df.dtypes
df.isnull().sum() / len(df) * 100  # Missing rate
```

## 2. Data Cleaning Tasks

| Task | Method | Reason |
|------|--------|--------|
| Currency unification | Convert all to USD | Handle mixed currencies (EUR, GBP, etc.) |
| Outlier removal | IQR method (Q1-1.5*IQR, Q3+1.5*IQR) | Remove extreme values skewing distributions |
| Duplicate check | `df.drop_duplicates()` | Ensure unique records |
| Missing value strategy | Mode for categorical, median for salary | Preserve distribution shape |
| Experience normalization | Standardize levels (Entry/Mid/Senior/Exec → 0/2/4/6) | Enable numerical analysis |
| Country code standardization | ISO 3166-1 alpha-3 codes | Required for pyecharts Map |

## 3. Statistical Summaries

### a. Salary Distribution by Key Dimensions

```python
# Basic stats
salary_stats = df.groupby(['job_role', 'experience_level'])['salary'].agg(['mean', 'median', 'std', 'count'])

# Skewness & Kurtosis per region
df.groupby('company_location')['salary'].agg(['skew', 'kurt'])

# Correlation matrix
numerical_cols = ['salary', 'years_experience', 'company_size']
corr_matrix = df[numerical_cols].corr()
```

### b. Geographical Analysis

```python
# Top 10 countries by salary
top10_salary = df.groupby('company_location')['salary'].median().nlargest(10)

# Salary range by region
df.groupby('region')['salary'].agg(['min', 'max', 'mean', 'median'])
```

## 4. Pyecharts Visualization Suite

### a. Global Salary Heat Map & Bar Chart

```python
# World map - median salary by country
median_salaries = df.groupby('company_location')['salary'].median().to_dict()
c = (Map()
     .add("Median Salary (USD)", 
          list(median_salaries.items()), 
          maptype="world")
     .set_global_opts(
         visualmap_opts=opts.VisualMapOpts(max_=300000)))
```

### b. Experience Level Impact (Bar + Line Timeline)

```python
# Timeline showing experience vs salary trend over years
exp_trend = df.groupby(['work_year', 'experience_level'])['salary'].mean().reset_index()
```

### c. Job Role Salary Distribution (Sankey)

```python
# Flow: Region → Job Role → Experience → Salary Range
# Prepare nodes and links for Sankey diagram
```

### d. Remote Work Mode Comparison (Stacked Bar + Pie)

```python
remote_pivot = df.pivot_table(index='experience_level', 
                              columns='work_mode', 
                              values='salary', 
                              aggfunc='median')
```

### e. Scatter - Experience vs Salary (Regression)

```python
# Scatter with trendline
# Points colored by job role, sized by company size
```

## 5. Seaborn Statistical Visualizations

### a. Salary Distribution Boxplot

```python
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x='job_role', y='salary', hue='experience_level')
plt.xticks(rotation=45)
plt.tight_layout()
```

### b. Remote Work Trend Heatmap

```python
pivot_table = df.pivot_table(index='work_year', 
                              columns='work_mode', 
                              values='salary', 
                              aggfunc='count')
sns.heatmap(pivot_table, annot=True, fmt='d', cmap='YlOrRd')
```

### c. Geographical Outlier Detection

```python
sns.scatterplot(data=df, x='years_experience', y='salary', 
                hue='company_location', style='experience_level')
```

## 6. Key Questions to Answer

| Dimension | Analysis Goal | Chart Type |
|-----------|---------------|------------|
| Global distribution | Which countries pay most? | Map + Bar (top 15) |
| Remote work shift | 2020-2025 远程/现场比例变化 | Timeline + Pie |
| Role hierarchy | 不同岗位薪资梯度及变动 | Bar + Sankey |
| Experience impact | 各经验等级薪资分布 | Boxplot + Violin |
| Company size effect | 大公司薪资优势 | Bar + Scatter |
| Temporal trends | 薪资年增长率 | Line (YoY % change) |

## 7. Deliverables

1. Cleaned dataset (salaries_clean.csv)
2. Jupyter notebook with full EDA code
3. Pyecharts HTML dashboard (4+ interactive charts)
4. Seaborn statistical report (3+ plots)
5. Summary insights markdown (key findings + recommendations)