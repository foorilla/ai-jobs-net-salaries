# `pyecharts_exporter` 模块使用文档

## 1. 模块简介
`pyecharts_exporter` 是一个专为 Jupyter Notebook (及 JupyterLab/VSCode Jupyter) 环境设计的 Pyecharts 渲染辅助包。
它通过构建完全自治的 **Iframe 沙箱 (`srcdoc`)**，彻底解决了 Pyecharts 原生渲染时常见的 `require.js` 冲突、白屏报错以及导出 HTML 后脱机失效的问题。同时，它内置了国内高速 CDN 切换功能，并支持自动嗅探图表主题并按需加载扩展 JS 资源。

---

## 2. 目录结构与引用规范

为了在你的 Jupyter Notebook 中能直接使用相对路径（同级目录寻找包）进行无缝调用，请确保你的项目目录结构如下：

```text
你的项目主目录/
│
├── pyecharts_exporter/          <-- 本地核心包文件夹
│   ├── __init__.py              <-- 接口暴露声明
│   └── core.py                  <-- 核心源码
│
└── 你的分析报告.ipynb             <-- 在同级目录下运行的 Notebook
```

只要保证 Notebook 文件与 `pyecharts_exporter` 文件夹处于**同一层级**，Python 就能自动将其识别为一个本地包。

---

## 3. 快速上手

在遵循上述目录结构的前提下，你可以像使用官方标准库一样，极其清爽地导入该包暴露的核心函数。

```python
from pyecharts.charts import Bar
from pyecharts import options as opts

# 导入该模块
from pyecharts_exporter import display_chart

# 1. 正常构建你的图表
bar = Bar().add_xaxis(["A", "B", "C"]).add_yaxis("数据", [1, 2, 3])

# 2. 替代原生的 bar.render_notebook()
display_chart(bar)
```

---

## 4. 核心函数 API

### `display_chart(chart: Base, **kwargs)`
在 Jupyter 单元格中直接渲染并展示图表。
* **作用**：底层调用 `EChartsRenderer`，生成隔离的 HTML 并通过 `IPython.display` 输出。
* **返回值**：无（直接在输出区显示图像）。

### `get_chart_urls(chart: Base, cdn_provider: str = "jsdelivr_fastly", custom_cdn_base: str = None) -> Dict`
获取图表渲染所需的依赖文件信息（通常用于调试或自定义网页构建）。
* **返回值**：返回一个字典，包含 `dependencies` (依赖列表), `cdn_urls` (完整链接列表), `html_tags` (生成的 script 标签文本) 和 `theme_detected` (探测到的主题)。

---

## 5. `display_chart` 参数详解

可通过 `**kwargs` 向 `display_chart` 传递多种控制参数：

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `chart` | `Base` | **必填** | Pyecharts 的图表实例（如 `Bar()`, `Line()`, `Page()` 等）。 |
| `width` | `str` | 图表自带宽度 / `"100%"` | Iframe 的宽度。例如 `"800px"` 或 `"100%"`。若不填，默认读取 `chart.width`。 |
| `height` | `str` | 图表自带高度 / `"500px"` | Iframe 的高度。例如 `"600px"`。若不填，默认读取 `chart.height`。 |
| `cdn_provider` | `str` | `"jsdelivr_fastly"` | 选择内置的 CDN 提供商。可选：`"pyecharts_official"` (官方国内加速) 或 `"jsdelivr_fastly"` (jsDelivr 镜像)。 |
| `custom_cdn_base` | `str` | `None` | 自定义基础 CDN 路径。如果提供，将覆盖 `cdn_provider` 的设置。需以 `/` 结尾。 |
| `scrolling` | `str` | `"no"` | 是否允许 Iframe 内部出现滚动条。可选 `"yes"`, `"no"`, `"auto"`。 |
| `sandbox` | `str` | `"allow-scripts allow-same-origin allow-downloads"` | Iframe 的沙箱权限。默认已开启脚本执行和文件下载（为了支持 Pyecharts 工具栏的保存图片功能）。 |

---

## 6. 进阶使用示例

### 示例 A：修改画布尺寸与切换 CDN
```python
from pyecharts.charts import Pie
from pyecharts_exporter import display_chart

pie = Pie().add("", [("苹果", 10), ("香蕉", 20)])

display_chart(
    pie, 
    width="600px", 
    height="400px", 
    cdn_provider="pyecharts_official" # 切换至 pyecharts 官方资源库
)
```

### 示例 B：使用扩展主题 (自动依赖注入)
模块会自动检测你在 `InitOpts` 中设置的主题，并自动从 CDN 拉取对应的 `{theme}.js` 文件注入到沙箱中，无需手动干预。

```python
from pyecharts.charts import Line
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts_exporter import display_chart

# 使用 macarons 扩展主题
line = (
    Line(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
    .add_xaxis(["周一", "周二", "周三"])
    .add_yaxis("气温", [15, 20, 18])
)

# 模块会自动发现主题为 macarons，并自动加载 macarons.js
display_chart(line)
```
------


## 7. 模块核心架构与类字典

### 1. `ThemeHelper` (主题辅助类)
**职责**：纯静态工具类，充当主题配置的“字典”。负责维护内置主题和扩展主题的清单，并提供查询 URL 的服务。它不保存任何实例状态。

* **类属性 (Class Attributes)**：
    * `BUILTIN_THEMES` *(List[str])*：内置主题列表（如 `["light", "dark", "white"]`），这些主题已内置于 ECharts 核心库，无需额外加载 JS。
    * `EXTENSION_THEMES` *(List[str])*：扩展主题列表（如 `["macarons", "chalk", "wonderland", ...]`），这些主题需要从外部拉取独立的 JS 文件。
* **核心方法 (Class Methods)**：
    * `is_extension(cls, theme: str) -> bool`
        * **说明**：判断传入的主题字符串是否属于扩展主题。
    * `get_js_url(cls, theme: str, cdn_base: str) -> Optional[str]`
        * **说明**：如果主题是扩展主题，则将其名称与 `cdn_base` 拼接，返回完整的 CDN 文件路径（如 `https://.../macarons.js`）；若是内置主题则返回 `None`。

---

### 2. `JSDependencyManager` (资源调度类)
**职责**：中间层业务逻辑。负责解析传入的 Pyecharts 图表实例，动态嗅探其配置，并统筹计算出渲染该图表需要加载的所有外部 JavaScript 资源链接。

* **实例属性 (Instance Attributes)**：
    * `cdn_base` *(str)*：当前实例所使用的基础 CDN 链接前缀（例如 `https://assets.pyecharts.org/assets/v6/`）。
* **核心方法 (Instance Methods)**：
    * `__init__(self, cdn_provider: str, custom_cdn_base: str = None)`
        * **说明**：初始化调度器，根据传入的提供商名称或自定义 URL 设定 `cdn_base`。
    * `get_url(self, dep: str) -> str`
        * **说明**：将单个依赖名称（如 `echarts` 或 `echarts-gl`）映射并拼接为绝对 CDN 路径。内部会查阅 `pyecharts.datasets.FILENAMES` 以匹配正确的文件扩展名。
    * `get_dependencies(self, chart: Base) -> Dict`
        * **说明**：**核心业务函数**。
        * 1. 提取 `chart.js_dependencies` 获取基础依赖。
        * 2. 通过 `getattr(chart, "theme", "white")` 动态嗅探图表实例的主题。
        * 3. 调用 `ThemeHelper` 获取扩展主题资源并合并。
        * 4. 返回包含 `dependencies`、`cdn_urls`、`html_tags` 和 `theme_detected` 的组装结果字典。

---

### 3. `EChartsRenderer` (沙箱渲染类)
**职责**：顶层视图层。负责将图表的底层 HTML 代码与调度器生成的 JS 依赖包进行最终合并，并将其封装入一个安全的 HTML5 `iframe` 沙箱中。

* **实例属性 (Instance Attributes)**：
    * `dep_manager` *(JSDependencyManager)*：在初始化时绑定的资源调度器实例，用于为当前渲染器提供依赖分析服务。
* **核心方法 (Instance Methods)**：
    * `__init__(self, cdn_provider: str, custom_cdn_base: str = None)`
        * **说明**：初始化渲染器，并同时实例化底层的 `JSDependencyManager`。每次调用都会生成全新实例，彻底解决状态污染问题。
    * `render(self, chart: Base, width: str = None, height: str = None, scrolling: str = "no", sandbox: str = "...") -> IPython.display.HTML`
        * **说明**：**核心渲染函数**。
        * 1. 调用 `self.dep_manager.get_dependencies()` 拿到所需注入的 `<script>` 标签文本。
        * 2. 调用 `chart.render_embed()` 生成 Pyecharts 原生的图表 div 容器与实例化代码。
        * 3. 将上述两者拼接为一个完整的 HTML 骨架字符串。
        * 4. 对 HTML 字符串进行转义 (`html.escape`)，塞入 `iframe` 的 `srcdoc` 属性中，最终打包为 Jupyter 可识别的 `HTML` 对象。