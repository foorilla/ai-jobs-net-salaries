#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 调用方向：Renderer → Manager → Helper

import html
from typing import Dict, Optional
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
    
    # 内置主题（无需额外 JS）
    BUILTIN_THEMES = ["light", "dark", "white"]
    # 扩展主题（需要从 CDN 加载对应的 {theme}.js）
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
        """
        核心逻辑：
        1. 获取图表自身依赖 (如 echarts.min.js)
        2. 探测图表实例的主题 (chart.theme)
        3. 如果是扩展主题，自动加入主题 JS 链接
        """
        # 1. 基础组件依赖
        deps = list(dict.fromkeys(chart.js_dependencies.items))
        urls = [self.get_url(dep) for dep in deps]
        
        # 2. 探测图表实例的主题
        # pyecharts 实例通常会将主题名存在 .theme 属性中
        current_theme = getattr(chart, "theme", "white")
        
        # 3. 如果是扩展主题，追加 JS
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

# ========== iframe 渲染器 ==========
class EChartsRenderer:
    def __init__(self, cdn_provider: str = DEFAULT_CDN, custom_cdn_base: str = None):
        self.dep_manager = JSDependencyManager(cdn_provider, custom_cdn_base)

    def render(self, chart: Base, width: str = None, height: str = None,
               scrolling: str = "no", 
               sandbox: str = "allow-scripts allow-same-origin allow-downloads") -> HTML:
        
        # 获取包含主题 JS 的依赖信息
        dep_info = self.dep_manager.get_dependencies(chart)
        
        # 生成图表本体 HTML
        chart_html = chart.render_embed()
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            {dep_info['html_tags']}
        </head>
        <body style="margin:0; padding:0;">
            {chart_html}
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