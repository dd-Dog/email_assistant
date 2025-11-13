# -*- coding: utf-8 -*-
"""
显示Excel文件内容
"""
from project_doc_loader import ProjectDocLoader

loader = ProjectDocLoader()
content = loader.get_project_content('G20', max_length=10000)

# 提取Excel相关内容
print("=" * 60)
print("Excel文件内容预览")
print("=" * 60)
print()

for line in content.split('\n'):
    if 'xlsx' in line or '工作表' in line or ('|' in line and len(line) < 100):
        print(line)

print()
print("=" * 60)

