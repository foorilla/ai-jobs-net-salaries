#!/usr/bin/env python
# coding: utf-8

# # AI/ML 全球薪资数据可视化分析——数字经济发展与人才战略洞察

# ## 一、选题背景

# ### 1.1 选题意义
# 
# 数字经济已成为全球经济增长的核心引擎。根据中国《“十四五”数字经济发展规划》，到 2025 年数字经济核心产业增加值占 GDP 比重将达到 10%。AI（人工智能）和 ML（机器学习）人才是数字经济发展的关键驱动力，其薪资水平直接反映了市场对数字技术人才的需求强度和各国数字经济的竞争态势。
# 
# 本分析基于 2020—2025 年全球 AI/ML/Big Data 领域的匿名薪资调查数据（151,445 条记录），从地理分布、时间趋势、岗位结构、经验溢价和公司规模等多维度进行可视化分析，旨在揭示：
# 
# - AI 人才市场的岗位构成与薪资结构特征
# - 全球 AI 人才薪资的地理分布与各国数字经济发展水平的关系
# - 2020—2025 年间 AI 人才薪资的增长趋势及远程工作模式的变迁
# - 不同经验等级、岗位类别和公司规模对薪资的影响机制
# - 数字经济发展中的人才结构特征与启示

# ### 1.2 数据来源及伦理说明
# 
# **数据来源**：本数据集来源于 [aijobs.net/salaries](https://aijobs.net/salaries/)，通过每周匿名调查收集全球 AI/ML/Big Data 领域从业者的薪资信息，时间跨度为 2020 年至 2025 年，共 151,445 条记录。数据以 CC0（公共领域）协议发布，可自由使用、修改和分发，包括商业用途。
# 
# **数据伦理**：
# - **匿名性**：所有数据均为匿名收集，不包含任何个人身份信息（姓名、邮箱、具体公司名称等），严格保护受访者隐私
# - **合规性**：数据采集遵循相关隐私法规，受访者自愿提交，体现了数据伦理中“知情同意”原则
# - **社会责任**：薪资透明度有助于消除就业市场信息不对称，促进公平薪酬实践。通过公开分析薪资数据，可以帮助求职者、招聘方和政策制定者做出更明智的决策
# - **数据公正**：分析中注意避免因样本分布不均（如美国占比较高）而导致的误导性结论，在解读时标注数据局限性

# ## 二、数据理解

# 本数据集共 151,445 条记录，11 个字段，覆盖 2020—2025 年全球 AI/ML/Data Science 领域薪资数据。
# 
# | 字段 | 说明 | 数据类型 |
# |------|------|----------|
# | work_year | 薪资对应年份（2020—2025） | 时间序列 |
# | experience_level | 经验等级：EN(入门) / MI(中级) / SE(高级) / EX(高管) | 定性 |
# | employment_type | 就业类型：FT(全职) / PT(兼职) / CT(合同) / FL(自由职业) | 定性 |
# | job_title | 岗位名称（原始 422 种） | 定性 |
# | salary | 原始薪资（当地货币） | 数值 |
# | salary_currency | 薪资货币代码（USD/EUR/GBP 等 26 种） | 定性 |
# | salary_in_usd | 折合美元薪资（统一分析基准） | 数值 |
# | employee_residence | 员工居住国家/地区（ISO 3166-1 alpha-2） | 空间 |
# | remote_ratio | 远程工作比例：0(现场) / 50(混合) / 100(远程) | 定性 |
# | company_location | 公司所在国家/地区（ISO 3166-1 alpha-2） | 空间 |
# | company_size | 公司规模：S(小) / M(中) / L(大) | 定性 |

# ## 三、分析目的

# 围绕”数字经济”主题，设定以下 6 个分析目标，每个目标对应一个图表：
#
# | # | 分析目标 | 图表类型 | 核心问题 |
# |---|----------|----------|----------|
# | 1 | 岗位构成与薪资结构占比 | Pyecharts 嵌套饼图 | AI 人才市场由哪些岗位构成？薪资结构如何分布？ |
# | 2 | 全球 AI 人才薪资地理分布 | Pyecharts 世界地图 + 柱状图自动切换 | 哪些国家 AI 人才薪资最高？Top 15 排名如何？ |
# | 3 | 薪资年度趋势与远程工作变迁 | Pyecharts 折线图 | 2020—2025 年薪资增长多少？远程工作占比如何变化？ |
# | 4 | 经验等级与远程模式对薪资的影响 | Seaborn 箱线图 | 经验溢价有多大？远程工作是否影响薪资水平？ |
# | 5 | 经验→岗位→公司规模流向分析 | Pyecharts 桑基图 | 不同经验的人才流向哪些岗位和公司？人才结构如何？ |
# | 6 | 岗位薪资年度动态对比 | Pyecharts Timeline 柱状图 | 各岗位薪资排名随时间如何变化？（动态交互） |

# ## 四、数据分析与可视化过程

# ### 1. 导入需要的库

# In[18]:


from pyecharts_exporter import display_chart, display_transition_chart

import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from collections import Counter

from pyecharts import options as opts
from pyecharts.charts import Map, Line, Bar, Sankey, Pie, Timeline, Grid
from pyecharts.commons.utils import JsCode

warnings.filterwarnings('ignore')

# 中文字体设置
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Droid Sans Fallback', 'Noto Sans CJK SC', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(
    style='whitegrid',
    palette='Set2',
    rc={
        'font.sans-serif': ['WenQuanYi Micro Hei', 'Droid Sans Fallback', 'Noto Sans CJK SC', 'SimHei', 'DejaVu Sans'],
        'axes.unicode_minus': False
    }
)


# ### 2. 数据加载与预处理

# In[19]:


df = pd.read_csv('salaries.csv')
print(f'数据集规模: {df.shape[0]:,} 条记录, {df.shape[1]} 个字段')
print(f'时间范围: {df["work_year"].min()} — {df["work_year"].max()}')
df.head()


# In[20]:


df.shape, df.columns.tolist(), df.dtypes


# #### 数据质量检查

# In[21]:


# 缺失值检查
print('=== 缺失值统计 ===')
print(df.isnull().sum())
print()

# 重复值检查
dup_count = df.duplicated().sum()
print(f'完全重复行: {dup_count:,} / {len(df):,} ({dup_count/len(df)*100:.1f}%)')
print('说明: 重复行是不同受访者具有相同履历（同岗位+同级+同薪资），保留全量')
print()

# 各字段基本信息
print('=== 分类字段分布 ===')
print(f'experience_level: {df["experience_level"].value_counts().to_dict()}')
print(f'remote_ratio: {df["remote_ratio"].value_counts().to_dict()}')
print(f'company_size: {df["company_size"].value_counts().to_dict()}')
print(f'employment_type: {df["employment_type"].value_counts().to_dict()}')
print(f'岗位种类数: {df["job_title"].nunique()}')


# #### 岗位归类
# 
# 将 422 种原始岗位按关键词优先级规则映射为 9 大类。分类优先级从高到低：AI/ML 专用岗位 > 数据科学家 > 数据工程师 > 软件工程师 > 数据分析师 > 管理层 > 研究岗 > 产品与咨询 > 其他。

# In[22]:


def classify_job(title):
    """将原始岗位名称映射到 9 大类。按优先级匹配，先匹配到的类别优先。"""
    t = title.lower()
    # 1. AI/ML 专用岗位
    if any(k in t for k in ['machine learning', 'ml engineer', 'ml scientist', 'ml researcher',
                              'ai engineer', 'ai architect', 'ai researcher',
                              'applied scientist', 'nlp', 'computer vision',
                              'deep learning', 'data science manager']):
        return 'AI/ML Specialist'
    # 2. 数据科学家（独立大类）
    if 'data scientist' in t:
        return 'Data Scientist'
    # 3. 数据工程师
    if any(k in t for k in ['data engineer', 'analytics engineer', 'data architect',
                              'platform engineer', 'data infrastructure', 'etl ']):
        return 'Data Engineer'
    # 4. 软件工程师
    if any(k in t for k in ['software engineer', 'engineer', 'developer', 'backend',
                              'frontend', 'full stack', 'fullstack', 'devops', 'sre',
                              'site reliability', 'systems engineer', 'cloud engineer',
                              'infrastructure engineer', 'security engineer']):
        return 'Software Engineer'
    # 5. 数据分析师
    if any(k in t for k in ['data analyst', 'analyst', 'bi ', 'business intelligence']):
        return 'Data Analyst'
    # 6. 管理层
    if any(k in t for k in ['manager', 'director', 'head of', 'lead', 'chief', 'vp ']):
        return 'Management'
    # 7. 研究岗
    if 'research' in t:
        return 'Research'
    # 8. 产品与咨询
    if any(k in t for k in ['product manager', 'product owner', 'consultant',
                              'architect', 'solutions architect', 'solution architect']):
        return 'Product & Consulting'
    # 9. 其他
    return 'Other'

df['job_category'] = df['job_title'].apply(classify_job)
print('=== 岗位分类结果 ===')
cat_counts = df['job_category'].value_counts()
for cat, cnt in cat_counts.items():
    print(f'  {cat}: {cnt:,} ({cnt/len(df)*100:.1f}%)')


# #### 薪资分箱
# 
# 为桑基图分析需要，将连续薪资数据离散化为 5 个区间。

# In[23]:


def bin_salary(s):
    if s < 80000:
        return '<$80K'
    elif s < 120000:
        return '$80-120K'
    elif s < 160000:
        return '$120-160K'
    elif s < 220000:
        return '$160-220K'
    else:
        return '>$220K'

df['salary_bin'] = df['salary_in_usd'].apply(bin_salary)
print('=== 薪资分箱分布 ===')
bin_order = ['<$80K', '$80-120K', '$120-160K', '$160-220K', '>$220K']
for b in bin_order:
    cnt = (df['salary_bin'] == b).sum()
    print(f'  {b}: {cnt:,} ({cnt/len(df)*100:.1f}%)')

# 添加标签映射
exp_labels = {'EN': 'Entry', 'MI': 'Mid', 'SE': 'Senior', 'EX': 'Executive'}
size_labels = {'S': 'Small', 'M': 'Medium', 'L': 'Large'}
remote_labels = {0: 'On-site', 50: 'Hybrid', 100: 'Remote'}
df['experience_label'] = df['experience_level'].map(exp_labels)
df['company_label'] = df['company_size'].map(size_labels)
df['remote_label'] = df['remote_ratio'].map(remote_labels)


# ### 3. 岗位构成与薪资结构占比（Pyecharts 嵌套饼图）
#
# **分析目标**：展示 AI/ML 人才市场的岗位类别构成（内圈）与整体薪资区间分布（外圈），为后续分析提供全局概览。

# In[24]:


# 计算内圈数据：各岗位类别的人数
inner_counts = df['job_category'].value_counts()
inner_data = [{"value": int(v), "name": k} for k, v in inner_counts.items()]

# 计算外圈数据：各薪资区间的人数
bin_order = ['<$80K', '$80-120K', '$120-160K', '$160-220K', '>$220K']
outer_counts = df['salary_bin'].value_counts().reindex(bin_order)
outer_data = [{"value": int(v), "name": k} for k, v in outer_counts.items()]

print('=== 岗位类别分布 ===')
for d in inner_data:
    print(f"  {d['name']}: {d['value']:,} ({d['value']/len(df)*100:.1f}%)")
print()
print('=== 薪资区间分布 ===')
for d in outer_data:
    print(f"  {d['name']}: {d['value']:,} ({d['value']/len(df)*100:.1f}%)")


# In[25]:


# 蓝绿色系配色：前 9 个用于内圈岗位，后 5 个用于外圈薪资区间
pie_colors = [
    '#5470c6', '#6e8cd6', '#91cc75', '#73c0de', '#3ba272',
    '#fac858', '#fc8452', '#9a60b4', '#ea7ccc',
    '#d4e6f1', '#a9cce3', '#5499c7', '#2e86c1', '#1b4f72',
]

# 富文本格式化函数
rich_formatter = """function(params) {
    return '{a|' + params.seriesName + '}{abg|}\\n{hr|}\\n  {b|' +
           params.name + '：}' + params.value + '  {per|' +
           params.percent + '%}  ';
}"""

pie = (
    Pie(init_opts=opts.InitOpts(
        width='1000px',
        height='700px',
        theme='light',
    ))
    .add(
        series_name='岗位类别',
        data_pair=[(d['name'], d['value']) for d in inner_data],
        radius=['10%', '40%'],      # 内圈：从10%到40%（原来是0到30%，整体放大并外移）
        selected_mode='single',
        selected_offset=10,
        label_opts=opts.LabelOpts(
            position='inner',
            font_size=12,
        ),
        center=['50%', '45%'],      # 饼图中心位置：水平居中，垂直上移（默认50%）
    )
    .add(
        series_name='薪资区间',
        data_pair=[(d['name'], d['value']) for d in outer_data],
        radius=['48%', '60%'],      # 外圈：从48%到60%（原来是45%到60%，整体放大）
        center=['50%', '45%'],      # 与外圈使用相同的中心位置
        label_opts=opts.LabelOpts(
            formatter=JsCode(rich_formatter),
            background_color='#F6F8FC',
            border_color='#8C8D8E',
            border_width=1,
            border_radius=4,
            rich={
                'a': {
                    'color': '#6E7079',
                    'lineHeight': 22,
                    'align': 'center',
                },
                'hr': {
                    'borderColor': '#8C8D8E',
                    'width': '100%',
                    'borderWidth': 1,
                    'height': 0,
                },
                'b': {
                    'color': '#2e86c1',
                    'fontSize': 14,
                    'fontWeight': 'bold',
                    'lineHeight': 33,
                },
                'per': {
                    'color': '#fff',
                    'backgroundColor': '#3ba272',
                    'padding': [3, 4],
                    'borderRadius': 4,
                },
            },
        ),
    )
    .set_colors(pie_colors)
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title='AI/ML 人才市场：岗位构成与薪资结构',
            subtitle='内圈：岗位类别占比 | 外圈：薪资区间分布 | 点击内圈可选中岗位',
            pos_left='center',
            pos_top='2%',
            item_gap=8,
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=18,
                font_weight='bold',
            ),
            subtitle_textstyle_opts=opts.TextStyleOpts(
                font_size=11,
                color='#666',
            ),
            padding=[5, 10],
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger='item',
            formatter='{a}<br/>{b}: {c} ({d}%)',
        ),
        legend_opts=opts.LegendOpts(
            type_='plain',
            orient='horizontal',
            pos_left='center',
            pos_bottom='5%',
            item_gap=20,
            background_color='rgba(255, 255, 255, 0.85)',
            border_color='#ccc',
            border_width=1,
            padding=[8, 15],
            textstyle_opts=opts.TextStyleOpts(font_size=11),
        ),
        graphic_opts=[
            opts.GraphicGroup(
                graphic_item=opts.GraphicItem(
                    left='center',
                    bottom='10px',
                    z=100,
                ),
                children=[
                    opts.GraphicText(
                        graphic_item=opts.GraphicItem(
                            left='center',
                            bottom='20px',
                        ),
                        graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                            text='数据来源: aijobs.net (2020-2025)',
                            font_size=12,
                            text_align='center',
                        ),
                    ),
                ],
            ),
        ],
    )
)

# 通过 options 字典直接设置 labelLine
pie.options.get('series', [{}])[0].update({'labelLine': {'show': False}})
pie.options.get('series', [{}])[1].update({'labelLine': {'show': True, 'length': 30, 'length2': 50}})

# 注入 JavaScript 来设置默认选中
pie.add_js_funcs("""
    setTimeout(function() {
        var chartDom = document.querySelector('.chart-container');
        var chartInstance = echarts.getInstanceByDom(chartDom);
        if (chartInstance) {
            chartInstance.dispatchAction({
                type: 'pieSelect',
                seriesIndex: 0,
                name: 'AI/ML Specialist'
            });
        }
    }, 200);
""")

display_chart(pie)


# #### 饼图分析
#
# - **岗位构成**：Software Engineer 以 27.0%（40,874 人）居首，是 AI/ML 人才市场规模最大的岗位群体。Data Analyst（15.6%）、Data Engineer（14.2%）和 Data Scientist（12.4%）紧随其后，三者合计占 42.2%。AI/ML Specialist 占 10.3%，作为核心算法研发岗位，占比虽不占优但薪资溢价显著。Management（7.4%）、Research（4.5%）和 Product & Consulting（2.5%）构成管理与专业服务梯队。岗位分布呈现出"软件工程为底座、数据科学为核心、管理研究为塔尖"的金字塔结构
# - **薪资结构**：薪资区间分布较为均匀，$160-220K 区间占比最高（25.4%），$120-160K（23.6%）和 $80-120K（21.2%）次之。>$220K 的高薪群体占 17.9%（约 2.7 万人），主要由 Executive 级别和资深 AI 专家构成。<$80K 的入门薪资群体占 11.9%，集中于 Entry 和 Mid 级别的 Data Analyst 岗位。整体薪资中位数约 $145K，呈右偏分布，高薪长尾特征明显
# - **数字经济启示**：岗位构成的多样性和薪资的分层结构，反映了 AI 产业的完���人才链条——从基础软件开发（Software Engineer）、数据工程（Data Engineer），到核心算法（AI/ML Specialist）和战略管理（Management）。约 43.3% 的人才年薪超过 $160K，表明 AI 行业整体薪酬水平显著高于多数行业

# ### 4. 全球 AI 人才薪资地理分布（Pyecharts 世界地图）
#
# **分析目标**：展示全球各国 AI/ML 人才薪资中位数的地理分布，间接反映各国数字经济发展水平和 AI 产业成熟度。

# In[26]:


# 按公司所在地统计薪资中位数
country_salary = df.groupby('company_location').agg(
    median_salary=('salary_in_usd', 'median'),
    count=('salary_in_usd', 'count')
).reset_index()

# 过滤样本量过少的国家（至少 5 条记录以保证统计意义）
country_salary = country_salary[country_salary['count'] >= 5]

# ISO alpha-2 -> 英文国名映射（pyecharts world map 使用英文名称）
# 直接使用 ISO 代码，pyecharts v2+ 的 world map 支持 ISO-3166-1 alpha-2
# 但部分版本需要英文全名，这里做一个兼容映射
iso_to_name = {
    'US': 'United States', 'CA': 'Canada', 'GB': 'United Kingdom',
    'DE': 'Germany', 'FR': 'France', 'NL': 'Netherlands',
    'AU': 'Australia', 'IN': 'India', 'BR': 'Brazil',
    'ES': 'Spain', 'IT': 'Italy', 'SE': 'Sweden',
    'PL': 'Poland', 'CH': 'Switzerland', 'AT': 'Austria',
    'BE': 'Belgium', 'DK': 'Denmark', 'FI': 'Finland',
    'NO': 'Norway', 'IE': 'Ireland', 'PT': 'Portugal',
    'GR': 'Greece', 'CZ': 'Czech Republic', 'RO': 'Romania',
    'HU': 'Hungary', 'BG': 'Bulgaria', 'HR': 'Croatia',
    'RS': 'Serbia', 'SK': 'Slovakia', 'SI': 'Slovenia',
    'EE': 'Estonia', 'LV': 'Latvia', 'LT': 'Lithuania',
    'UA': 'Ukraine', 'RU': 'Russia', 'TR': 'Turkey',
    'IL': 'Israel', 'AE': 'United Arab Emirates', 'SA': 'Saudi Arabia',
    'QA': 'Qatar', 'OM': 'Oman', 'JO': 'Jordan',
    'JP': 'Japan', 'KR': 'South Korea', 'CN': 'China',
    'HK': 'Hong Kong', 'TW': 'Taiwan', 'SG': 'Singapore',
    'MY': 'Malaysia', 'TH': 'Thailand', 'VN': 'Vietnam',
    'ID': 'Indonesia', 'PH': 'Philippines', 'PK': 'Pakistan',
    'MX': 'Mexico', 'AR': 'Argentina', 'CL': 'Chile',
    'CO': 'Colombia', 'PE': 'Peru', 'VE': 'Venezuela',
    'ZA': 'South Africa', 'NG': 'Nigeria', 'EG': 'Egypt',
    'KE': 'Kenya', 'GH': 'Ghana', 'MU': 'Mauritius',
    'NZ': 'New Zealand', 'LU': 'Luxembourg', 'MT': 'Malta',
    'CY': 'Cyprus', 'MD': 'Moldova', 'MK': 'North Macedonia',
    'BA': 'Bosnia and Herz.', 'XK': 'Kosovo', 'AD': 'Andorra',
    'GI': 'Gibraltar', 'PR': 'Puerto Rico', 'DO': 'Dominican Rep.',
    'CR': 'Costa Rica', 'GT': 'Guatemala', 'HN': 'Honduras',
    'SV': 'El Salvador', 'PA': 'Panama', 'JM': 'Jamaica',
    'BS': 'Bahamas', 'BM': 'Bermuda', 'AM': 'Armenia',
    'GE': 'Georgia', 'LB': 'Lebanon', 'IQ': 'Iraq',
    'IR': 'Iran', 'DZ': 'Algeria', 'ML': 'Mali',
    'CD': 'Dem. Rep. Congo', 'CF': 'Central African Rep.',
    'ZM': 'Zambia', 'LS': 'Lesotho', 'UG': 'Uganda',
    'AS': 'American Samoa', 'KW': 'Kuwait',
}

country_salary['country_name'] = country_salary['company_location'].map(iso_to_name)
country_salary = country_salary.dropna(subset=['country_name'])

# 准备地图数据（按薪资升序排列，同时用于地图和柱状图切换）
map_data = [
    (row['country_name'], int(row['median_salary']))
    for _, row in country_salary.iterrows()
]
map_data.sort(key=lambda x: x[1])

print(f'参与地图绘制的国家/地区数: {len(map_data)}')
print(f'薪资最高国家: {max(map_data, key=lambda x: x[1])}')
print(f'薪资最低国家: {min(map_data, key=lambda x: x[1])}')

# 取 Top 15 用于柱状图排名（地图仍用完整数据）
map_data_top15 = map_data[-15:]


# In[27]:


salary_map = (
    Map(init_opts=opts.InitOpts(width='1200px', height='700px', theme='light'))
    .add(
        series_name='薪资中位数 (USD)',
        data_pair=map_data,
        maptype='world',
        is_map_symbol_show=False,
        label_opts=opts.LabelOpts(is_show=False),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title='全球 AI/ML 人才薪资中位数分布',
            subtitle='仅展示 ≥5 条记录的国家/地区',
            pos_left='center',
            pos_top='2%',
            item_gap=8,
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=18,
                font_weight='bold'
            ),
            subtitle_textstyle_opts=opts.TextStyleOpts(
                font_size=11
            ),
            padding=[5, 10],
        ),
        legend_opts=opts.LegendOpts(is_show=False),
        graphic_opts=[
            opts.GraphicGroup(
                graphic_item=opts.GraphicItem(
                    left="center",
                    bottom="10px",
                    z=100
                ),
                children=[
                    opts.GraphicText(
                        graphic_item=opts.GraphicItem(
                            left="center",
                            bottom="20px"
                        ),
                        graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                            text="数据来源: aijobs.net (2020-2025)",
                            font_size=12,
                            text_align="center",
                        )
                    )
                ]
            )
        ],
        visualmap_opts=opts.VisualMapOpts(
            min_=int(country_salary['median_salary'].min()),
            max_=int(country_salary['median_salary'].max()),
            range_text=['高薪资', '低薪资'], 
            range_color=['#4575b4', '#91bfdb', '#ffffbf', '#fc8d59', '#d73027'],
            is_piecewise=False,
            pos_left='3%',
            pos_bottom='8%',
            orient='vertical',
            textstyle_opts=opts.TextStyleOpts(font_size=11),
            item_width=15,
            item_height=200,
            padding=[5, 10],
        ),
        tooltip_opts=opts.TooltipOpts(
            formatter='{b}: ${c}',
        ),
        toolbox_opts=opts.ToolboxOpts(
            is_show=True,
            feature={
                'saveAsImage': {'title': '保存为图片'}, 
                'restore': {'title': '还原'}
            },
            pos_top='2%',
            pos_right='5%',
        ),
    )
    .set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
    )
)

bar_chart = (
    Bar()
    .add_xaxis([name for name, _ in map_data_top15])
    .add_yaxis('薪资中位数 (USD)', [val for _, val in map_data_top15])
    .reversal_axis()
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title='全球 AI/ML 人才薪资中位数 Top 15',
            subtitle='按薪资中位数降序排列',
            pos_left='center',
            pos_top='2%',
            item_gap=8,
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=18,
                font_weight='bold'
            ),
            subtitle_textstyle_opts=opts.TextStyleOpts(
                font_size=11,
                color='#666'
            ),
            padding=[5, 10],
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger='axis',
            formatter='{b}: ${c:,}',
        ),
        graphic_opts=[
            opts.GraphicGroup(
                graphic_item=opts.GraphicItem(
                    left="center",
                    bottom="10px",
                    z=100
                ),
                children=[
                    opts.GraphicText(
                        graphic_item=opts.GraphicItem(
                            left="center",
                            bottom="20px"
                        ),
                        graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                            text="数据来源: aijobs.net (2020-2025)",
                            font_size=12,
                            text_align="center",
                        )
                    )
                ]
            )
        ],
    )
)

# ========== 👇 新增：定义柱状图的 JS 配置 ==========
bar_option_override = {
    "title": {
        "text": "全球 AI/ML 人才薪资中位数 Top 15",
        "subtext": "按薪资中位数降序排列，仅展示前 15 名",
        "left": "center",
        "top": "2%",
        "itemGap": 8,
        "textStyle": {
            "fontSize": 18,
            "fontWeight": "bold"
        },
        "subtextStyle": {
            "fontSize": 11,
            "color": "#666"
        },
        "padding": [5, 10]
    },
    "grid": {
        "left": "18%",
        "right": "12%",
        "bottom": "12%",
        "top": "18%"
    },
    "xAxis": {
        "type": "value",
        "min": 90000,
        "name": "薪资中位数 (USD)",
        "nameLocation": "center",
        "nameGap": 35
    },
    "series": [{
        "itemStyle": {"color": "#4575b4"},
        "label": {
            "show": True,
            "position": "right"
        }
    }],
    "graphic": [
        {
            "type": "group",
            "left": "center",
            "bottom": "5px",
            "z": 100,
            "children": [
                {
                    "type": "text",
                    "left": "center",
                    "bottom": "10px",
                    "style": {
                        "text": "数据来源: aijobs.net (2020-2025)",
                        "fontSize": 12,
                        "textAlign": "center",
                        "fill": "#999"
                    }
                }
            ]
        }
    ]
}

display_transition_chart(
    salary_map, 
    bar_chart, 
    map_data_top15,
    bar_option_override=bar_option_override,
    interval=5000,
)

# #### 地图与柱状图分析
#
# - **交互切换**：图表每 5 秒在地理分布图和 Top 15 薪资排名柱状图之间自动切换，利用 ECharts universalTransition 实现平滑动画过渡。地图展示 68 个国家/地区的全局格局（筛选条件：样本量 ≥ 5），柱状图聚焦薪资最高的 15 个国家进行横向对比
# - **Top 15 排名**：美国以 $151,200 的中位薪资位居榜首，与其全球 AI 产业中心地位一致（样本量 13.6 万，占数据集 89.5%）。加拿大（$120,000，第 5）、澳大利亚（$117,363，第 7）和瑞士（$115,909，第 10）构成第二梯队。新加坡（$113,208，第 11）是亚洲薪资最高的国家。需注意 Top 15 中部分国家样本量极小（如香港 5 条、约旦 6 条、保加利亚 5 条），其中位数估计的统计可靠性较低，解读时应谨慎
# - **北美领先**：美国 AI 人才薪资中位数位居全球第一，硅谷、纽约、西雅图等科技中心集聚了大量 AI 企业，推高了整体薪资水平。加拿大薪资约为美国的 79%，在北美自由贸易和人才流动背景下仍有显著差距
# - **欧洲分化**：西欧国家（瑞士、比利时、爱尔兰、丹麦）薪资较高（$95K—$116K），东欧国家（如波兰、罗马尼亚、匈牙利）薪资明显偏低，反映了欧洲内部数字经济发展程度的不均衡。值得注意的是保加利亚以 $111,111 进入 Top 15，但其样本仅 5 条，可能不具代表性
# - **亚太格局**：新加坡（$113K）领跑亚洲，澳大利亚（$117K）和新西兰（$118K）薪资接近北美水平。日本（$85K）和韩国（$91K）处于中间梯队。中国（$60K）和印度（$45K）薪资较低，但考虑到购买力平价和生活成本差异，实际差距可能小于名义薪资比
# - **数字鸿沟**：薪资最低的国家集中在非洲（如尼日利亚、埃及、肯尼亚）和南亚（如巴基斯坦），中位数多在 $30K—$50K 区间。Top 1（美国）与最低薪资国家的差距超过 3 倍，揭示了全球 AI 产业链中技术和资本密集度不均等导致的人才定价分化
# - **数字经济启示**：AI 人才薪资的地理分布与各国数字经济发展水平高度正相关。高薪资国家集中在 AI 研发投入高、科技企业密集的地区。对发展中国家而言，培养本土 AI 人才、吸引技术转移是缩小数字鸿沟的关键路径

# ### 5. 薪资年度趋势与远程工作模式变迁（Pyecharts 双轴折线图）
# 
# **分析目标**：展示 2020—2025 年 AI 人才薪资的变化趋势，以及远程工作占比的同步变迁，反映数字经济驱动下的就业形态变革。

# In[28]:


# 按年度统计薪资均值和远程工作占比
yearly = df.groupby('work_year').agg(
    avg_salary=('salary_in_usd', 'mean'),
    median_salary=('salary_in_usd', 'median'),
    remote_pct=('remote_ratio', lambda x: (x == 100).sum() / len(x) * 100),
    hybrid_pct=('remote_ratio', lambda x: (x == 50).sum() / len(x) * 100),
    onsite_pct=('remote_ratio', lambda x: (x == 0).sum() / len(x) * 100),
    count=('salary_in_usd', 'count'),
).reset_index()

years = yearly['work_year'].astype(str).tolist()

print('=== 年度薪资统计 ===')
for _, r in yearly.iterrows():
    print(f"{int(r['work_year'])}: 均值=${r['avg_salary']:,.0f}  中位=${r['median_salary']:,.0f}  "
          f"远程={r['remote_pct']:.1f}%  混合={r['hybrid_pct']:.1f}%  现场={r['onsite_pct']:.1f}%  样本={int(r['count']):,}")

# 计算 YOY 增长率
yearly['yoy_growth'] = yearly['median_salary'].pct_change() * 100


# In[29]:


# 创建双轴折线图
line_chart = (
    Line(init_opts=opts.InitOpts(width='1100px', height='650px', theme='light'))
    .add_xaxis(xaxis_data=years)
    .add_yaxis(
        series_name='薪资中位数 (USD)',
        y_axis=yearly['median_salary'].round(0).astype(int).tolist(),
        yaxis_index=0,
        is_smooth=True,
        symbol='circle',
        symbol_size=10,
        label_opts=opts.LabelOpts(is_show=True, formatter='${@[1]}'),
        linestyle_opts=opts.LineStyleOpts(width=3),
        itemstyle_opts=opts.ItemStyleOpts(color='#5470c6'),
    )
    .add_yaxis(
        series_name='远程工作占比 (%)',
        y_axis=yearly['remote_pct'].round(1).tolist(),
        yaxis_index=1,
        is_smooth=True,
        symbol='diamond',
        symbol_size=10,
        label_opts=opts.LabelOpts(is_show=True, formatter='{@[1]}%'),
        linestyle_opts=opts.LineStyleOpts(width=3, type_='dashed'),
        itemstyle_opts=opts.ItemStyleOpts(color='#91cc75'),
    )
    .extend_axis(
        yaxis=opts.AxisOpts(
            name='远程工作占比 (%)',
            type_='value',
            min_=10,
            max_=60,
            axislabel_opts=opts.LabelOpts(formatter='{value}%', color='#91cc75'),
            axistick_opts=opts.AxisTickOpts(
                linestyle_opts=opts.LineStyleOpts(color='#91cc75', width=1)
            ),
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(color='#999', width=1)
            ),
            splitline_opts=opts.SplitLineOpts(is_show=False),
        )
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title='AI 人才薪资中位数与远程工作占比年度趋势 (2020—2025)',
            subtitle='薪资反映数字经济人才价值增长 | 远程工作体现就业形态变革',
            pos_left='center',
            pos_top='2%',
            item_gap=8,
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=18,
                font_weight='bold'
            ),
            subtitle_textstyle_opts=opts.TextStyleOpts(
                font_size=11
            ),
            padding=[5, 10],
        ),
        legend_opts=opts.LegendOpts(
            type_='plain',
            pos_right='10%',
            pos_bottom='15%',       # 从底部向上移动，进入坐标轴内部
            orient='vertical',
            background_color='rgba(255, 255, 255, 0.85)',
            border_color='#ccc',
            border_width=1,
            textstyle_opts=opts.TextStyleOpts(font_size=12),
        ),
        graphic_opts=[
            opts.GraphicGroup(
                graphic_item=opts.GraphicItem(
                    left="center",
                    bottom="10px",
                    z=100
                ),
                children=[
                    opts.GraphicText(
                        graphic_item=opts.GraphicItem(
                            left="center",
                            bottom="20px"
                        ),
                        graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                            text="数据来源: aijobs.net (2020-2025)",
                            font_size=12,
                            text_align="center",
                        )
                    )
                ]
            )
        ],
        yaxis_opts=opts.AxisOpts(
            name='薪资 (USD)',
            type_='value',
            min_=70000,
            max_=160000,
            axislabel_opts=opts.LabelOpts(formatter='${value}', color='#5470c6'),
            axistick_opts=opts.AxisTickOpts(
                linestyle_opts=opts.LineStyleOpts(color='#5470c6', width=1)
            ),
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(color='#999', width=1)
            ),
            splitline_opts=opts.SplitLineOpts(
                is_show=True,
                linestyle_opts=opts.LineStyleOpts(type_='dashed', color='#eee')
            ),
        ),
        tooltip_opts=opts.TooltipOpts(trigger='axis'),
        toolbox_opts=opts.ToolboxOpts(
            is_show=True, 
            feature={
                'saveAsImage': {'title': '保存为图片'}, 
                'dataView': {'title': '数据视图'}, 
                'restore': {'title': '还原'}
            },
            pos_top='2%',
            pos_right='5%',
        ),
    )
)

display_chart(line_chart)


# #### 趋势分析
#
# - **数据质量警示**：2020 年和 2021 年的样本量极小（分别为 75 条和 218 条），其统计值波动较大，不具备可靠的年度比较意义。以下分析以 2022 年（样本 1,661 条）为可信起点
# - **薪资增长**：从 2022 年到 2025 年，薪资中位数由 $131,300 增长至 $145,100，累计增幅约 10.5%，年均增长约 3.4%。2024 年达到峰值 $148,945 后，2025 年小幅回落至 $145,100（降幅 2.6%），可能反映了科技行业在 2024 年招聘高峰后的市场回调。若以 2020 年数据为参考（$79,833），名义增幅达 81.8%，但该数字受早期样本偏差影响，不宜直接解读为市场增长
# - **远程工作演变**：远程工作占比在 2022 年达到峰值 53.4%，此后逐年下降：2023 年降至 31.4%，2024—2025 年稳定在约 20%。这一趋势与直观预期（”疫情后远程工作会持续增加”）相反。但需注意数据集的样本构成在 2023—2025 年发生了显著变化——美国样本占比从约 50% 急剧上升至约 90%，而美国企业的远程政策相对保守。因此，远程占比的下降可能主要反映了样本构成变化，而非全球远程工作模式的真实逆转
# - **混合模式持续边缘化**：混合办公（50% 远程）占比在所有年份均低于 5%，2025 年仅 0.1%，表明 AI 行业的企业在办公模式选择上倾向于”完全远程”或”完全现场”的二元决策，中间路线未成为主流
# - **数字经济启示**：AI 人才薪资在 2022—2025 年间保持温和增长，表明市场对 AI 人才的需求持续旺盛但增速趋于理性。远程工作的演变受多种因素（企业政策、样本构成、宏观经济）交织影响，仅凭调查数据难以得出因果结论

# ### 6. 经验等级与远程工作对薪资的影响（Seaborn 分面箱线图）
# 
# **分析目标**：结合经验等级和远程工作模式，从统计角度展示不同群体的薪资分布差异。

# In[30]:


# 筛选数据：remote_ratio 以 0 和 100 为主，50 极少，合并展示
box_df = df[['salary_in_usd', 'experience_label', 'remote_label']].copy()

# 设置画布 - 分面箱线图
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# 子图1: 经验等级 vs 薪资
exp_order = ['Entry', 'Mid', 'Senior', 'Executive']
sns.boxplot(
    ax=axes[0],
    data=box_df,
    x='experience_label',
    y='salary_in_usd',
    order=exp_order,
    palette='Blues_r',
    linewidth=1.2,
    fliersize=2,
)
axes[0].set_title('经验等级 vs 薪资分布', fontsize=14, fontweight='bold')
axes[0].set_xlabel('经验等级', fontsize=12)
axes[0].set_ylabel('薪资 (USD)', fontsize=12)
axes[0].yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'${x:,.0f}'))

# 标注中位数
for i, level in enumerate(exp_order):
    med = box_df[box_df['experience_label'] == level]['salary_in_usd'].median()
    axes[0].annotate(f'${med:,.0f}', xy=(i, med), xytext=(i+0.3, med+15000),
                    fontsize=9, color='darkblue', fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='darkblue', lw=0.8))

# 子图2: 远程模式 vs 薪资
remote_order = ['On-site', 'Hybrid', 'Remote']
sns.boxplot(
    ax=axes[1],
    data=box_df,
    x='remote_label',
    y='salary_in_usd',
    order=remote_order,
    palette='Greens_r',
    linewidth=1.2,
    fliersize=2,
)
axes[1].set_title('远程模式 vs 薪资分布', fontsize=14, fontweight='bold')
axes[1].set_xlabel('工作模式', fontsize=12)
axes[1].set_ylabel('薪资 (USD)', fontsize=12)
axes[1].yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'${x:,.0f}'))

# 标注中位数
for i, mode in enumerate(remote_order):
    med = box_df[box_df['remote_label'] == mode]['salary_in_usd'].median()
    axes[1].annotate(f'${med:,.0f}', xy=(i, med), xytext=(i+0.3, med+15000),
                    fontsize=9, color='darkgreen', fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='darkgreen', lw=0.8))

plt.suptitle('AI/ML 人才薪资：经验等级与远程模式的影响', fontsize=16, fontweight='bold', y=1.02)
plt.subplots_adjust(bottom=0.1)

# 添加数据来源标注
fig.text(0.5, 0.01, '数据来源: aijobs.net (2020-2025)', ha='center', fontsize=10, color='gray', style='italic', transform=fig.transFigure)

plt.show()


# #### 箱线图分析
#
# **经验等级视角**：
# - 经验溢价呈现清晰的阶梯式递增：Entry $86,600 → Mid $130,000（+50.1%）→ Senior $161,000（+23.8%）→ Executive $189,370（+17.6%）。Executive 的薪资中位数是 Entry 的 2.2 倍。从 Entry 到 Mid 的跨度和涨幅最大，表明初级人才在积累 2—5 年经验后进入市场价值跃升期
# - 离散度差异：Executive 薪资的箱体最长（IQR 约 $100K），反映了高管层级薪资的结构性分化——行业、公司规模和岗位职责对高管薪酬的影响远大于初中级。Entry 的箱体最短（IQR 约 $40K），薪资区间相对集中，入门级人才的市场定价较为统一
# - 离群值分布：所有经验等级均存在向上离群值，Executive 的高端离群值可达 $300K 以上。这些极端值主要来自美国大型科技公司的高管岗位，是 AI 人才市场"赢者通吃"特征的体现
# - 数字经济启示：数字技能的经验积累有清晰且可量化的回报曲线。Entry→Mid 阶段是职业价值的最大跃升期，持续学习和技能提升是 AI 人才职业发展的核心驱动力
#
# **远程模式视角**：
# - 远程（$145,000）与现场（$147,000）的薪资中位数仅差 $2,000（1.4%），在统计上不构成显著差异。这一发现表明远程工作并未系统性地降低 AI 人才的薪酬水平——企业按技能和市场价值定价，而非按工作地点
# - 混合模式样本仅 329 条（0.2%），其中位数 $69,999 显著偏低，可能受到样本构成（以发展中国家兼职和合同工为主）的混淆，不宜直接与远程/现场对比
# - 数字经济启示：远程工作在 AI 行业中已成为与现场工作薪酬对等的可行模式。这为人才打破了地域壁垒，使企业可以在全球范围内竞争人才，同时也为不同地域、不同背景的从业者提供了更平等的就业机会

# ### 7. 经验等级 → 岗位类别 → 公司规模 流向分析（Pyecharts 桑基图）
# 
# **分析目标**：展示不同经验等级的人才流向哪些岗位和公司规模，揭示 AI 行业的人才结构特征。

# In[31]:


from pyecharts.charts import Grid

# 构建三层桑基图: 经验等级 → 岗位类别 → 公司规模
sankey_df = df.groupby(['experience_label', 'job_category', 'company_label']).size().reset_index(name='count')

# 筛选主要流向（过滤掉流量 < 200 的边，保持图可读性）
sankey_df = sankey_df[sankey_df['count'] >= 200]

# 收集所有节点
layers = [
    sorted(sankey_df['experience_label'].unique()),
    sorted(sankey_df['job_category'].unique()),
    sorted(sankey_df['company_label'].unique()),
]

all_nodes = []
for layer in layers:
    all_nodes.extend(layer)

node_to_idx = {node: i for i, node in enumerate(all_nodes)}

# 构建 links: source -> target -> count
links = []
for _, row in sankey_df.iterrows():
    links.append({
        'source': node_to_idx[row['experience_label']],
        'target': node_to_idx[row['job_category']],
        'value': int(row['count']),
    })

# 第二层到第三层
layer2_df = df.groupby(['job_category', 'company_label']).size().reset_index(name='count')
layer2_df = layer2_df[layer2_df['count'] >= 200]
for _, row in layer2_df.iterrows():
    if row['job_category'] in node_to_idx and row['company_label'] in node_to_idx:
        links.append({
            'source': node_to_idx[row['job_category']],
            'target': node_to_idx[row['company_label']],
            'value': int(row['count']),
        })

print(f'节点数: {len(all_nodes)}')
print(f'边数: {len(links)}')

# 优化标题间距的桑基图，隐藏图例，居中显示
sankey = (
    Sankey(init_opts=opts.InitOpts(
        width='1200px', 
        height='750px', 
        theme='light',
    ))
    .add(
        series_name='人才流向',
        nodes=[{'name': n} for n in all_nodes],
        links=links,
        node_width=25,
        node_gap=12,
        node_align='justify',      # 节点对齐方式
        layout_iterations=0,
        orient='horizontal',
        label_opts=opts.LabelOpts(
            position='right', 
            font_size=11,
            # 设置标签与节点的距离
            distance=10,
        ),
        linestyle_opt=opts.LineStyleOpts(opacity=0.3, curve=0.5, color='source'),
        pos_top='10%',
        pos_left='10%',            # 增大左侧留白，平衡左右空间
        pos_right='10%',           # 增大右侧留白，平衡左右空间
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title='AI 人才流向：经验等级 → 岗位类别 → 公司规模',
            subtitle='带宽代表人才流量 | 仅展示流量 ≥ 200 的边',
            pos_left='center',
            pos_top='3%',
            item_gap=8,
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=18,
                font_weight='bold'
            ),
            subtitle_textstyle_opts=opts.TextStyleOpts(
                font_size=11,
                color='#666'
            ),
            padding=[5, 10],
        ),
        legend_opts=opts.LegendOpts(is_show=False),
        graphic_opts=[
            opts.GraphicGroup(
                graphic_item=opts.GraphicItem(
                    left="center",
                    bottom="10px",
                    z=100
                ),
                children=[
                    opts.GraphicText(
                        graphic_item=opts.GraphicItem(
                            left="center",
                            bottom="20px"
                        ),
                        graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                            text="数据来源: aijobs.net (2020-2025)",
                            font_size=12,
                            text_align="center",
                        )
                    )
                ]
            )
        ],
    )
)

display_chart(sankey)


# #### 桑基图分析
#
# - **经验等级→岗位流向**：
#   - Senior（高级）人才是最大流量群体，主导了主要岗位的供给：流向 Software Engineer 25,437 人（占全体 16.8%），Data Engineer 13,834 人（9.1%），Data Scientist 11,883 人（7.8%），AI/ML Specialist 10,839 人（7.2%）。Senior 人才是 AI 行业的中坚力量，覆盖了从工程到算法的全技术栈
#   - Mid（中级）人才的最大流向是 Software Engineer（12,994 人，8.6%）和 Management（6,115 人，4.0%），部分中级从业者开始转向管理轨道
#   - Entry（入门）人才集中流向 Data Analyst（8,324 人，5.5%），表明数据分析是 AI 行业最常见的入门岗位。Software Engineer 也是 Entry 的重要去向
#   - Executive（高管）人才近半数流向 Management 岗位，其余分布于 Data Scientist 和 AI/ML Specialist，反映了高管群体的双重路径——纯管理 vs 技术管理
# - **岗位→公司规模流向**：
#   - Medium（中型）公司在所有岗位中占绝对主导：Software Engineer（39,877 人，26.3%）、Data Analyst（23,357 人，15.4%）、Data Engineer（21,088 人，13.9%）、Data Scientist（18,324 人，12.1%）、Management（14,642 人，9.7%）。这与数据集中 M 类公司占 97.3% 的分布一致，但也反映了中型科技公司是 AI 人才的主要雇主
#   - Large（大型）公司主要吸引 Software Engineer 和 Management 人才，与其对大规模系统和团队管理的需求吻合
#   - Small（小型/创业公司）样本虽少（0.9%），但吸引了各个岗位类别的人才，尤其在 AI/ML Specialist 和 Research 岗位中有一定比例，反映了 AI 创业公司在核心技术研发上的投入
# - **数字经济启示**：AI 行业呈现出清晰的职业发展路径——Entry 以数据分析切入，Mid/Senior 在软件工程和数据科学领域深耕，Executive 向管理或高级技术专家分化。中型公司作为主要雇主，表明 AI 产业并非仅由少数科技巨头驱动，广大的中型企业构成了数字经济的人才蓄水池

# ### 8. 岗位薪资年度动态对比（Pyecharts Timeline 柱状图） ⬅ 动态交互
# 
# **分析目标**：按年度展示各岗位类别的平均薪资排名变化，通过年份滑块实现动态切换，直观感受薪资结构的时间演变。

# In[32]:


# 按年份和岗位类别统计平均薪资
yearly_job = df.groupby(['work_year', 'job_category'])['salary_in_usd'].mean().reset_index()
yearly_job['salary_k'] = yearly_job['salary_in_usd'] / 1000

# 计算全局 Top 9 岗位（按总平均薪资），保证每年展示相同岗位便于比较
top_cats = df.groupby('job_category')['salary_in_usd'].mean().nlargest(9).index.tolist()

# 为每个岗位分配固定颜色（深色）
colors_dark = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc']
# 对应的浅色版本
colors_light = ['#d4daf0', '#e8f5e3', '#fef4d3', '#fad4d4', '#d3ecf8', '#d8eddd', '#fee6d2', '#ebdff2', '#f9e2f0']

job_color_map = {
    job: {'dark': colors_dark[i], 'light': colors_light[i]} 
    for i, job in enumerate(top_cats)
}

# 创建 Timeline，增加高度以容纳标题和图例
tl = Timeline(init_opts=opts.InitOpts(width='1100px', height='650px', theme='light'))

years_sorted = sorted(df['work_year'].unique())

for year in years_sorted:
    year_data = yearly_job[yearly_job['work_year'] == year]
    # 筛选 Top 9 岗位并按薪资降序排列
    year_data = year_data[year_data['job_category'].isin(top_cats)]
    year_data = year_data.sort_values('salary_k', ascending=True)  # 升序排列
    year_data = year_data.dropna(subset=['salary_k'])

    cats = year_data['job_category'].tolist()
    vals = year_data['salary_k'].round(0).tolist()

    # 计算该年的最高薪资，用于动态设置X轴范围
    max_salary = year_data['salary_k'].max()
    x_max = int(max_salary * 1.2)  # 留20%余量

    # 为当前年份的岗位生成对应的渐变颜色配置
    gradient_colors = [
        [job_color_map[cat]['dark'], job_color_map[cat]['light']] 
        for cat in cats
    ]

    bar = (
        Bar(init_opts=opts.InitOpts(width='1100px', height='550px'))
        .add_xaxis(cats)
        .add_yaxis(
            f'{year} 年平均薪资',
            vals,
            label_opts=opts.LabelOpts(position='right', formatter='${c}K', font_size=11),
            itemstyle_opts=opts.ItemStyleOpts(
                # 为每个柱子创建从深色到浅色的水平渐变
                color=JsCode(
                    f"""function(params) {{
                        var gradients = {gradient_colors};
                        var colors = gradients[params.dataIndex];
                        return new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                            {{offset: 0, color: colors[0]}},
                            {{offset: 1, color: colors[1]}}
                        ]);
                    }}"""
                )
            ),
        )
        .reversal_axis()
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f'AI 岗位平均薪资位次变化 ({year} 年)',
                subtitle='岗位按薪资从高到低排列 | 同一岗位颜色固定，便于追踪位次变化',
                pos_left='center',
                pos_top='2%',
                item_gap=8,
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=18,
                    font_weight='bold'
                ),
                subtitle_textstyle_opts=opts.TextStyleOpts(
                    font_size=11,
                    color='#666'
                ),
                padding=[5, 10],
            ),
            legend_opts=opts.LegendOpts(is_show=False),
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        left="center",
                        bottom="10px",
                        z=100
                    ),
                    children=[
                        opts.GraphicText(
                            graphic_item=opts.GraphicItem(
                                left="center",
                                bottom="20px"
                            ),
                            graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                                text="数据来源: aijobs.net (2020-2025)",
                                font_size=12,
                                text_align="center",
                            )
                        )
                    ]
                )
            ],
            yaxis_opts=opts.AxisOpts(
                name='岗位类别',
                axislabel_opts=opts.LabelOpts(formatter='{value}', font_size=11),
                #is_inverse=True,  # 反转Y轴，让最高薪资显示在最上面
            ),
            xaxis_opts=opts.AxisOpts(
                name='平均薪资 (K USD)',
                max_=x_max,
                axislabel_opts=opts.LabelOpts(formatter='${value}K'),
            ),
            tooltip_opts=opts.TooltipOpts(
                formatter='{b}: ${c}K',
            ),
        )
        .set_series_opts(
            bar_width='60%',
        )
    )
    tl.add(bar, str(year))

# 添加滑块和播放控件
tl.add_schema(
    is_auto_play=True,
    play_interval=2000,
    is_loop_play=True,
    is_timeline_show=True,
    label_opts=opts.LabelOpts(font_size=12),
    pos_top='90%',
    pos_bottom='5%',
    pos_left='10%',
    pos_right='10%',
)

display_chart(tl)


# #### Timeline 动态柱状图分析
#
# - **交互功能**：拖动下方年份滑块或点击播放按钮，可切换不同年份的岗位薪资排名（2020—2025 年）。图表支持 2 秒/帧的自动轮播，同一岗位颜色固定，便于追踪其位次随时间的变化
# - **薪资排名演变**：
#   - AI/ML Specialist 自 2023 年起稳居薪资榜首（2025 年 $191K），是唯一连续三年保持前二的岗位，体现了 AI 核心算法人才的市场溢价持续领先
#   - Research（研究岗）薪资波动较大但始终处于高位：2020 年 $246K（但该年仅 75 条样本，可能受极端值影响），2023—2025 年稳定在 $173K—$191K，是 AI 基础研究持续受重视的信号
#   - Software Engineer 的排名显著上升：从 2022 年第 7 位（$118K）跃升至 2025 年第 2 位（$175K），涨幅 48.3%，反映了市场对 AI 工程化落地能力的强劲需求
#   - Management 在 2024—2025 年稳定在 $165K—$171K，较 2022 年的高位（$147K，当年排名第 1）相对位次有所下降，但绝对薪资仍在增长
#   - Data Analyst 的薪资在多年间始终处于末位（2025 年 $109K），约为 AI/ML Specialist 的 57%，验证了不同岗位间的结构性薪资分层
# - **2020 年数据谨慎说明**：2020 年仅 75 条样本，各岗位的统计值（如 Research $246K）波动极大，不宜纳入年度趋势对比。2021 年（218 条）同样存在样本量不足的问题。可靠的年度对比应从 2022 年（1,661 条）开始
# - **数字经济启示**：岗位薪资排名的演变反映了 AI 产业的需求变迁——从早期以管理层和研究员为薪资顶端，到 2023 年后 AI/ML 专岗和软件工程岗位持续领跑。这一转变与生成式 AI（如 ChatGPT 于 2023 年发布）引发的产业浪潮时间点吻合，表明技术创新直接重塑了 AI 人才市场的价格结构

# ## 五、可视化设计思路
# 
# ### 5.1 图表类型选择依据
# 
# | 图表 | 选择理由 |
# |------|----------|
# | **嵌套饼图** | 内圈展示岗位构成，外圈展示薪资区间分布，两层结构在同一视图中同时回答"谁在市场中"和"薪资怎么分布"，点击内圈可选中岗位 |
# | **世界地图 + 柱状图切换** | 薪资数据具有天然的空间属性，地图能最直观地展示全球分布格局；叠加柱状图自动切换，在同一区域同时呈现地理分布和排名对比两个视角 |
# | **双轴折线图** | 同时展示薪资（数值）和远程占比（百分比）两个不同量纲的时间序列，双 Y 轴是最经济的方案 |
# | **分面箱线图** | 箱线图能同时展示中位数、四分位距和离群值，比柱状图+误差棒更准确地反映分布形态。分面（subplot）在同一视图中对比两个维度的效应 |
# | **桑基图** | 展示“经验→岗位→公司规模”的三层流向关系，带宽直观反映流量大小，是展示分类间流动关系的最佳选择 |
# | **Timeline 柱状图** | 条形图适合排名比较，加上时间轴后能够在年份维度上动态切换，满足“动态交互”要求的同时增加展示趣味性 |
# 
# ### 5.2 配色方案
# 
# - **整体风格**：以蓝绿色系为主色调，体现”科技+数据”的理性专业感
# - **嵌套饼图**：内圈 9 个岗位类别使用蓝绿色系区分色，外圈 5 个薪资区间使用浅→深渐变（薪资越低越浅、越高越深），富文本标签对齐蓝绿主题
# - **地图**：浅色主题 (light)，VisualMap 从浅蓝（低薪资）到深红（高薪资），对比突出
# - **折线图**：薪资用实线蓝色 (#5470c6)，远程占比用虚线绿色 (#91cc75)，区分清晰
# - **箱线图**：Blues_r 和 Greens_r 渐变，色调统一
# - **Timeline 柱状图**：渐变色填充 (LinearGradient)，从蓝到绿，富有动感
# 
# ### 5.3 交互功能设计
# 
# - **饼图选中交互**：点击内圈岗位可选中并突出显示，外圈展示对应薪资分布，鼠标悬停显示详细占比
# - **地图↔柱状图自动切换**：世界地图每 5 秒自动切换为 Top 15 薪资排名柱状图，利用 universalTransition 实现平滑动画，用户可在同一视图获取地理分布和排名两个视角
# - **Timeline 滑块**：支持手动拖动和自动轮播（2 秒/帧），用户可自由选择关注特定年份
# - **地图 Tooltip**：悬停显示国家名称和具体薪资数值，减少视觉搜索成本
# - **桑基图悬停**：鼠标悬停时高亮对应流向路径，帮助追踪特定人才群体的流向
# - **工具箱**：所有 Pyecharts 图表均启用保存图片和数据视图功能，方便导出成果

# ## 六、数据分析流程说明
# 
# ### 6.1 数据清洗
# 
# 1. **缺失值检查**：全部 11 个字段无缺失值，数据完整性良好
# 2. **重复值识别**：识别出 79,532 条完全重复行（52.5%），经分析确认为不同受访者的相同履历，非数据采集错误，保留全量分析
# 3. **离群值策略**：薪资数据呈天然右偏分布，未采用 IQR 方法剔除离群值。高薪样本（如 $336K+）是 AI 行业高价值人才的重要信号，不应作为“噪声”处理
# 4. **数据规范化**：列名标准无空格，字段类型正确，无需额外转换
# 
# ### 6.2 特征提取
# 
# 1. **岗位归类**：将 422 种原始岗位按关键词优先级算法映射为 9 大类，规则透明、可复现
# 2. **薪资分箱**：基于分位数分布，将连续薪资离散化为 5 个区间（<$80K / $80-120K / $120-160K / $160-220K / >$220K）
# 3. **标签映射**：将缩写代码（EN/SE/EX 等）映射为可读的英文标签，提升图表可读性
# 
# ### 6.3 分析方法
# 
# - **描述性统计**：计算均值、中位数、分位数，概括薪资分布特征
# - **分组对比**：按经验等级、岗位类别、远程模式等维度分组，对比组间差异
# - **时间序列分析**：按年度聚合，观察薪资和远程工作的变化趋势
# - **流向分析**：通过桑基图展示多层级分类间的流量关系

# ## 七、结论与启示
# 
# ### 7.1 数据分析结果总结
# 
# 1. **市场构成**：AI/ML 人才市场由 9 大岗位类别构成，Data Scientist、Software Engineer 和 Data Engineer 是三大核心岗位。薪资呈右偏分布，大多数人才集中在 $80K—$160K 区间，>$220K 的高薪群体由资深专家和高管构成
# 2. **地理分布**：AI/ML 人才薪资呈现显著的全球不均衡分布。北美和西欧薪资最高，与这些地区的数字经济领先地位一致。亚洲主要经济体（日本、韩国、新加坡）薪资水平接近欧美，发展中国家则面临较大差距
# 3. **时间趋势**：2020—2025 年间 AI 人才薪资持续增长，中位数年均增长约 3-5%。同期远程工作占比大幅上升，数字化工具重塑了就业形态
# 4. **经验溢价**：经验是薪资最重要的决定因素之一。从入门到高管，每提升一个等级都有显著的薪资增长，验证了数字技能积累的市场价值
# 5. **岗位结构**：Data Scientist、Software Engineer 和 Data Engineer 是三大核心岗位，占数据总量的 47%。AI/ML Specialist 是薪资最高的技术岗位
# 6. **公司规模**：数据集中中型公司占绝对主导，但创业公司和小型企业同样在吸引 AI 人才，展示了 AI 创业生态的活力
# 
# ### 7.2 对国家/社会问题的启示与建议（课程思政）
# 
# **数字经济发展建议**：
# - AI 人才是数字经济的核心竞争力。从薪资数据看，全球 AI 人才供不应求。国家应加大对 AI 教育和技能培训的投入，扩大 AI 人才供给
# - 中国在全球 AI 人才市场中仍有较大发展空间。需要完善人才引进政策，优化创新创业环境
# 
# **数字鸿沟问题**：
# - 发达国家与发展中国家 AI 人才薪资差距显著，体现了技术、资本和教育资源的不均衡分配。应推动 AI 技术的全球普惠发展，让更多国家和地区共享数字经济的红利
# - 倡议国际技术合作和知识共享，帮助发展中国家培养本土 AI 人才，践行“人类命运共同体”理念
# 
# **数据伦理与就业公平**：
# - 薪资数据的透明化是促进就业公平的重要手段。本数据集以匿名方式收集和开放，既保护了个人隐私，又为公众提供了有价值的市场信息
# - 建议行业建立更多公开、匿名的薪资基准数据平台，减少求职信息不对称，促进公平薪酬实践
# - 远程工作的普及为不同地域、不同背景的人才提供了更平等的机会，企业应积极拥抱灵活的工作模式

# ## 八、学习总结
# 
# ### 8.1 课程知识应用体会
# 
# 本次大作业将课程中学到的数据清洗、特征工程、统计分析和可视化设计等知识，系统性地应用于真实的 AI 行业薪资数据分析中：
# 
# - **数据预处理**：通过缺失值检查、重复值分析、岗位归类等操作，加深了对“数据质量决定分析质量”的认识
# - **可视化工具选择**：根据分析目标和数据类型，合理选择 Pyecharts（交互式图表）和 Seaborn（统计图表），体会了不同工具的适用场景
# - **图表设计**：在配色、标注、交互等方面反复打磨，理解了“好的可视化不仅是展示数据，更是讲述故事”
# - **课程思政融入**：学会在数据分析中融入数据伦理、社会责任等思考，提升了用数据视角理解社会问题的能力
# 
# ### 8.2 技术难点与解决思路
# 
# | 难点 | 解决方案 |
# |------|----------|
# | 422 种岗位归类 | 设计关键词优先级规则，优先匹配特异性高的词（如 `machine learning`），再匹配通用词（如 `engineer`），避免误分类 |
# | 世界地图国家名称映射 | 建立 ISO alpha-2 → 英文全名的映射字典，覆盖 97 个国家/地区 |
# | 桑基图三层流向构建 | 将聚合数据转为 `(source, target, value)` 三元组，过滤流量 < 200 的次要边以保持可读性 |
# | Timeline 交互实现 | 使用 Pyecharts Timeline 组件，为每个年份创建独立的 Bar 实例，通过 `add_schema` 配置自动轮播和滑块 |
# | 双轴折线图 | 使用 `extend_axis` 添加第二 Y 轴，通过 `yaxis_index` 参数关联不同数据系列 |
# | 嵌套饼图 labelLine 控制 | pyecharts 无直接 API 设置饼图引导线，通过 `pie.options.get('series')` 底层字典操作分别控制内圈和外圈的 labelLine 显隐与长度 |
# | 地图↔柱状图自动切换 | 利用 ECharts universalTransition 特性，通过 `bar_option_override` 字典定制柱状图样式，注入 JS 定时器实现图表类型间的平滑动画过渡 |

# In[33]:


get_ipython().system('jupyter nbconvert --to html final.ipynb')

