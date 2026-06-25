import nbformat
from nbconvert import PythonExporter

# 读取 notebook
with open('final.ipynb', 'r', encoding='utf-8') as f:
    notebook = nbformat.read(f, as_version=4)

# 转换为 Python 脚本
python_exporter = PythonExporter()
body, _ = python_exporter.from_notebook_node(notebook)

# 保存
with open('final.py', 'w', encoding='utf-8') as f:
    f.write(body)

print("Conversion completed successfully!")