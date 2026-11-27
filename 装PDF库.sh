#!/bin/bash
# 检查/安装 PDF 文本提取库
/opt/qa-venv/bin/python -c "import pypdf; print('pypdf', pypdf.__version__)" 2>/dev/null && exit 0
/opt/qa-venv/bin/python -c "import fitz; print('pymupdf ok')" 2>/dev/null && exit 0
echo "未安装，尝试安装 pypdf"
/opt/qa-venv/bin/pip install -q -i https://mirrors.aliyun.com/pypi/simple/ pypdf 2>&1 | tail -2
/opt/qa-venv/bin/python -c "import pypdf; print('pypdf', pypdf.__version__)"
