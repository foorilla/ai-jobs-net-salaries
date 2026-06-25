# CLAUDE.md

## 项目说明

- `final.ipynb` — Jupyter notebook，对 salaries 数据集进行 pyecharts 和 seaborn 可视化分析
- `final.py` — `final.ipynb` 的纯代码版本（由 nbconvert 转换），内容与 notebook 同步

## 修改流程

- **修改代码时只编辑 `final.py`**，不要直接改 `.ipynb`
- 全部修改完成并确认无误后，运行 `python3 sync_to_ipynb.py` 将 `.py` 同步到 `.ipynb`
- `convert.py` — 反向转换（`.ipynb` → `.py`），由 nbconvert 驱动
- `sync_to_ipynb.py` — 正向同步（`.py` → `.ipynb`），解析 `# In[XX]:` 标记和 `# ##` 标题还原 cell 结构
