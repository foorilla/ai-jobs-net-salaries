#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 调用方向：Renderer → Manager → Helper

import html
import json
from typing import Dict, Optional, List
from IPython.display import display, HTML

from pyecharts.globals import CurrentConfig
from pyecharts.charts.base import Base
from pyecharts.charts.chart import Chart
from pyecharts.datasets import FILENAMES

CurrentConfig.NOTEBOOK_TYPE = ""

# ========== 国内加速 CDN 配置 ==========
CDN_CONFIGS = {
    "pyecharts_official": "https://assets.pyecharts.org/assets/v6/",
    "jsdelivr_fastly": "https://fastly.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/v6/",
}
DEFAULT_CDN = "pyecharts_official"


# ========== 主题助手 (辅助类) ==========
class ThemeHelper:
    """仅作为工具类，判断主题是否需要额外 JS 资源"""
    
    BUILTIN_THEMES = ["light", "dark", "white"]
    EXTENSION_THEMES = [
        "chalk", "essos", "infographic", "macarons", "purple-passion",
        "roma", "romantic", "shine", "vintage", "walden", "westeros", 
        "wonderland", "halloween"
    ]

    @classmethod
    def is_extension(cls, theme: str) -> bool:
        return theme in cls.EXTENSION_THEMES

    @classmethod
    def get_js_url(cls, theme: str, cdn_base: str) -> Optional[str]:
        if cls.is_extension(theme):
            return f"{cdn_base}{theme}.js"
        return None


# ========== JS 依赖管理器 ==========
class JSDependencyManager:
    """自动分析图表实例的依赖及主题 JS"""
    
    def __init__(self, cdn_provider: str = DEFAULT_CDN, custom_cdn_base: str = None):
        if custom_cdn_base:
            self.cdn_base = custom_cdn_base
        else:
            self.cdn_base = CDN_CONFIGS.get(cdn_provider, CDN_CONFIGS[DEFAULT_CDN])

    def get_url(self, dep: str) -> str:
        if dep in FILENAMES:
            filename, ext = FILENAMES[dep]
            return f"{self.cdn_base}{filename}.{ext}"
        return f"{self.cdn_base}{dep}.js"

    def get_dependencies(self, chart: Base) -> Dict:
        deps = list(dict.fromkeys(chart.js_dependencies.items))
        urls = [self.get_url(dep) for dep in deps]
        
        current_theme = getattr(chart, "theme", "white")
        theme_js_url = ThemeHelper.get_js_url(current_theme, self.cdn_base)
        if theme_js_url:
            urls.append(theme_js_url)
            deps.append(f"theme-{current_theme}")
        
        html_tags = "\n".join([f'<script src="{url}"></script>' for url in urls])
        
        return {
            "dependencies": deps,
            "cdn_urls": urls,
            "html_tags": html_tags,
            "theme_detected": current_theme
        }


# ========== iframe 渲染器 (增强版) ==========
class EChartsRenderer:
    def __init__(self, cdn_provider: str = DEFAULT_CDN, custom_cdn_base: str = None):
        self.dep_manager = JSDependencyManager(cdn_provider, custom_cdn_base)
        self._custom_scripts: List[str] = []  # 存储额外要注入的 JS

    def add_script(self, js_code: str):
        """添加自定义 JS 代码（会在图表渲染后执行）"""
        self._custom_scripts.append(js_code)
        return self  # 链式调用

    def _get_injected_scripts(self) -> str:
        """生成注入脚本的 HTML"""
        if not self._custom_scripts:
            return ""
        
        scripts_html = ""
        for code in self._custom_scripts:
            scripts_html += f"""
<script>
(function() {{
    // 等待 iframe 内的 DOM 和图表完全加载
    var checkExist = setInterval(function() {{
        // 查找所有 echarts 实例
        var charts = document.querySelectorAll('[id]');
        var foundChart = null;
        
        charts.forEach(function(el) {{
            if (el.getAttribute('_echarts_instance_') || 
                typeof echarts !== 'undefined' && echarts.getInstanceByDom(el)) {{
                foundChart = el;
            }}
        }});
        
        if (foundChart || document.readyState === 'complete') {{
            clearInterval(checkExist);
            {code}
        }}
    }}, 100);
}})();
</script>"""
        return scripts_html

    def render(self, chart: Base, width: str = None, height: str = None,
               scrolling: str = "no", 
               sandbox: str = "allow-scripts allow-same-origin allow-downloads") -> HTML:
        
        dep_info = self.dep_manager.get_dependencies(chart)
        chart_html = chart.render_embed()
        injected_scripts = self._get_injected_scripts()
        
        full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    {dep_info['html_tags']}
</head>
<body style="margin:0; padding:0;">
    {chart_html}
    {injected_scripts}
</body>
</html>
"""
        
        escaped_html = html.escape(full_html)
        iframe_width = width or getattr(chart, 'width', '100%')
        iframe_height = height or getattr(chart, 'height', '500px')

        iframe_html = f"""
<iframe srcdoc="{escaped_html}" 
        width="{iframe_width}" height="{iframe_height}" 
        frameborder="0" scrolling="{scrolling}" sandbox="{sandbox}">
</iframe>
"""
        return HTML(iframe_html)


# ========== 快速调用入口 ==========
def display_chart(chart: Base, cdn_provider: str = DEFAULT_CDN, **kwargs):
    renderer = EChartsRenderer(cdn_provider)
    display(renderer.render(chart, **kwargs))


def get_chart_urls(chart: Base, cdn_provider: str = DEFAULT_CDN, custom_cdn_base: str = None) -> Dict:
    dep_manager = JSDependencyManager(cdn_provider, custom_cdn_base)
    return dep_manager.get_dependencies(chart)


# ========== 新增：带切换效果的 display 函数 ==========
def display_transition_chart(
    map_chart: Base,
    bar_chart: Base,
    map_data: list,         # [(name, value), ...] 格式的原始数据
    chart_id: str = "myChart",
    interval: int = 3000,
    cdn_provider: str = DEFAULT_CDN
):
    """
    在 Jupyter Notebook 中渲染一个地图和柱状图自动切换的图表。
    
    参数:
        map_chart: Pyecharts Map 实例
        bar_chart: Pyecharts Bar 实例 (仅用于提取配置，不直接渲染)
        map_data: 原始数据 [(name, value), ...]
        chart_id: 图表 DOM 元素的 ID
        interval: 切换间隔（毫秒）
    """
    renderer = EChartsRenderer(cdn_provider)
    
    # 构建切换的 JS 代码
    data_json = json.dumps(map_data)
    values = [item[1] for item in map_data]
    
    transition_js = f"""
    var data = {data_json};
    var names = data.map(function(item) {{ return item[0]; }});
    var values = data.map(function(item) {{ return item[1]; }});

    // 查找 echarts 实例
    var chartDom = document.getElementById('{chart_id}');
    if (!chartDom) {{
        // 如果没找到指定 ID，尝试找第一个 echarts 实例
        var allDoms = document.querySelectorAll('[id]');
        for (var i = 0; i < allDoms.length; i++) {{
            if (echarts.getInstanceByDom(allDoms[i])) {{
                chartDom = allDoms[i];
                break;
            }}
        }}
    }}
    
    if (!chartDom) return;
    var chart = echarts.getInstanceByDom(chartDom);
    if (!chart) return;

    // 给当前地图 series 添加 universalTransition 所需的属性
    var mapOption = chart.getOption();
    mapOption.series[0].id = 'salary';
    mapOption.series[0].universalTransition = true;
    chart.setOption(mapOption, true);

    // 构建柱状图 option
    var barOption = {{
        title: {{ text: '全球薪资中位数排名', left: 'center' }},
        tooltip: {{
            trigger: 'axis',
            axisPointer: {{ type: 'shadow' }},
            formatter: function(params) {{
                return params[0].name + ': $' + params[0].value.toLocaleString();
            }}
        }},
        grid: {{ left: '15%', right: '10%', bottom: '10%' }},
        xAxis: {{
            type: 'value',
            name: '薪资中位数 (USD)',
            axisLabel: {{
                formatter: function(val) {{
                    return '$' + Math.round(val / 1000) + 'k';
                }}
            }}
        }},
        yAxis: {{
            type: 'category',
            axisLabel: {{ rotate: 30 }},
            data: names
        }},
        animationDurationUpdate: 1000,
        series: [{{
            type: 'bar',
            id: 'salary',
            data: values,
            universalTransition: true
        }}]
    }};

    // 定时切换
    var currentOption = mapOption;
    setInterval(function() {{
        currentOption = currentOption === mapOption ? barOption : mapOption;
        chart.setOption(currentOption, true);
    }}, {interval});
    """
    
    renderer.add_script(transition_js)
    display(renderer.render(map_chart))