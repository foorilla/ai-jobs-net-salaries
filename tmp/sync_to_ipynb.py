#!/usr/bin/env python3
"""将 final.py（nbconvert --to script 格式）同步为 final.ipynb。

用法: python3 sync_to_ipynb.py

原理：
- # In[XX]: 标记分隔各个代码 cell
- 代码 cell 内若包含 # ## / # ### / # #### 标题行，则标题之后的内容为 markdown cell
- 文件首段（第一个 In[] 之前）为前置 markdown
- markdown 中的 # 前缀会被剥离
"""

import nbformat as nbf
import re


def strip_md_prefix(block: str) -> str:
    """剥离 markdown 块中的 '# ' 前缀。"""
    lines = []
    for line in block.split('\n'):
        if line.startswith('# '):
            lines.append(line[2:])
        elif line.startswith('#'):
            lines.append(line[1:].lstrip())
        else:
            lines.append(line)
    return '\n'.join(lines).strip()


def convert(py_path: str = 'final.py', ipynb_path: str = 'final.ipynb') -> None:
    with open(py_path, 'r') as f:
        text = f.read()

    # 移除 shebang 和 coding 行
    text = re.sub(r'^#!/usr/bin/env python\n# coding: utf-8\n', '', text)

    # 以 In[XX]: 为分隔符拆分
    parts = re.split(r'\n# In\[\d+\]:\n', text)

    cells = []

    for i, part in enumerate(parts):
        stripped = part.strip()
        if not stripped:
            continue

        if i == 0:
            # 第一个 In[] 之前的内容全部为 markdown
            md = strip_md_prefix(stripped)
            if md:
                cells.append(nbf.v4.new_markdown_cell(md))
            continue

        # 在代码块内查找 markdown 标题（# ## / # ### / # ####）
        md_start = re.search(r'\n\n# [#]{2,4} ', '\n' + stripped)

        if md_start:
            split_pos = md_start.start()
            code_part = stripped[:split_pos].strip()
            md_part = stripped[split_pos:].strip()

            if code_part:
                cells.append(nbf.v4.new_code_cell(code_part))
            if md_part:
                cells.append(nbf.v4.new_markdown_cell(strip_md_prefix(md_part)))
        else:
            # 纯代码 cell
            cells.append(nbf.v4.new_code_cell(stripped))

    nb = nbf.v4.new_notebook(cells=cells)
    nbf.write(nb, ipynb_path)

    md_count = sum(1 for c in cells if c.cell_type == 'markdown')
    code_count = sum(1 for c in cells if c.cell_type == 'code')
    print(f'{py_path} → {ipynb_path}: {len(cells)} cells ({md_count} markdown + {code_count} code)')


if __name__ == '__main__':
    convert()
