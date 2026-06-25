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


# ========== 修复后的深度合并函数 ==========
def _deep_update(base: dict, override: dict):
    """
    递归合并字典，override 覆盖 base 中的同名 key。
    支持数组内对象的合并（按索引位置）。
    """
    for key, value in override.items():
        if key in base:
            # 如果两者都是列表，按索引递归合并列表中的元素
            if isinstance(base[key], list) and isinstance(value, list):
                for i in range(min(len(base[key]), len(value))):
                    if isinstance(base[key][i], dict) and isinstance(value[i], dict):
                        _deep_update(base[key][i], value[i])
                    else:
                        base[key][i] = value[i]
                # 如果 override 的列表更长，追加多余元素
                if len(value) > len(base[key]):
                    base[key].extend(value[len(base[key]):])
            # 如果两者都是字典，递归合并
            elif isinstance(base[key], dict) and isinstance(value, dict):
                _deep_update(base[key], value)
            # 否则直接覆盖
            else:
                base[key] = value
        else:
            # base 中没有这个 key，直接添加
            base[key] = value


# ========== 修改后的：带切换效果的 display 函数 ==========
def display_transition_chart(
    map_chart: Base,
    bar_chart: Base,
    map_data: list,
    chart_id: str = "myChart",
    interval: int = 3000,
    bar_option_override: dict = None,
    cdn_provider: str = DEFAULT_CDN
):
    renderer = EChartsRenderer(cdn_provider)
    
    data_json = json.dumps(map_data)
    
    # ========== 最简默认配置（只包含必要的框架） ==========
    default_bar_option = {
        "title": {
            "text": "数据排名",
            "left": "center"
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"}
        },
        "grid": {
            "left": "15%",
            "right": "10%",
            "bottom": "10%",
            "top": "15%"
        },
        "xAxis": {
            "type": "value"
        },
        "yAxis": {
            "type": "category",
            "data": []  # 占位，JS 中会被替换
        },
        "animationDurationUpdate": 1000,
        "series": [{
            "type": "bar",
            "id": "salary",
            "data": [],  # 占位，JS 中会被替换
            "universalTransition": True
        }]
    }
    
    # 合并用户自定义配置
    if bar_option_override:
        _deep_update(default_bar_option, bar_option_override)
    
    bar_option_json = json.dumps(default_bar_option)
    
    transition_js = f"""
    var data = {data_json};
    var names = data.map(function(item) {{ return item[0]; }});
    var values = data.map(function(item) {{ return item[1]; }});

    // 从 JSON 加载柱状图配置
    var barOption = {bar_option_json};

    // 🔧 强制注入数据（确保数据一定存在）
    barOption.yAxis.data = names;
    barOption.series[0].data = values;
    barOption.series[0].id = 'salary';
    barOption.series[0].universalTransition = true;

    // 🔧 注入 formatter 函数（JSON 无法序列化函数）
    if (barOption.tooltip && !barOption.tooltip.formatter) {{
        barOption.tooltip.formatter = function(params) {{
            if (params && params.length > 0) {{
                return params[0].name + ': $' + params[0].value.toLocaleString();
            }}
            return '';
        }};
    }}

    if (barOption.xAxis && barOption.xAxis.axisLabel && !barOption.xAxis.axisLabel.formatter) {{
        barOption.xAxis.axisLabel.formatter = function(val) {{
            return '$' + Math.round(val / 1000) + 'k';
        }};
    }}

    // 🔧 注入 series label 的 formatter
    if (barOption.series && barOption.series[0] && barOption.series[0].label) {{
        if (barOption.series[0].label.show && !barOption.series[0].label.formatter) {{
            barOption.series[0].label.formatter = function(params) {{
                return '$' + (params.value / 1000).toFixed(1) + 'k';
            }};
        }}
    }}

    // 🔧 查找 echarts 实例
    var chartDom = document.getElementById('{chart_id}');
    if (!chartDom) {{
        var allDoms = document.querySelectorAll('[_echarts_instance_]');
        if (allDoms.length > 0) {{
            chartDom = allDoms[0];
        }}
    }}
    
    if (!chartDom) {{
        console.log('未找到 ECharts 实例');
        return;
    }}
    
    var chart = echarts.getInstanceByDom(chartDom);
    if (!chart) {{
        console.log('无法获取 ECharts 实例');
        return;
    }}

    // 🔧 给当前地图 series 添加 universalTransition 所需的属性
    var mapOption = chart.getOption();
    if (mapOption.series && mapOption.series.length > 0) {{
        mapOption.series[0].id = 'salary';
        mapOption.series[0].universalTransition = true;
        chart.setOption(mapOption, true);
    }}

    // 🔧 定时切换（增加错误处理）
    var currentOption = mapOption;
    setInterval(function() {{
        try {{
            currentOption = currentOption === mapOption ? barOption : mapOption;
            chart.setOption(currentOption, true);
        }} catch(e) {{
            console.log('切换出错:', e);
        }}
    }}, {interval});
    """
    
    renderer.add_script(transition_js)
    display(renderer.render(map_chart))