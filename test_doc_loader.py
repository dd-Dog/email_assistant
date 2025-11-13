"""
测试文档加载器 - 检查是否能正确读取各种格式的文档
"""
import os
import logging
from project_doc_loader import ProjectDocLoader

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_doc_loader():
    """测试文档加载器"""
    print("=" * 60)
    print("文档加载器测试")
    print("=" * 60)
    print()
    
    # 检查依赖
    try:
        from docx import Document
        print("[OK] Word支持（python-docx）已安装")
    except ImportError:
        print("[X] Word支持（python-docx）未安装")
        print("  运行: pip install python-docx")
    
    try:
        from openpyxl import load_workbook
        print("[OK] Excel支持（openpyxl）已安装")
    except ImportError:
        print("[X] Excel支持（openpyxl）未安装")
        print("  运行: pip install openpyxl")
    
    print()
    print("-" * 60)
    print("开始加载项目文档...")
    print("-" * 60)
    print()
    
    # 创建加载器
    loader = ProjectDocLoader(projects_root='projects')
    
    if not loader.has_projects():
        print("未找到项目文档")
        print()
        print("请确保 projects/ 目录下有项目文件夹，例如：")
        print("  projects/G20/产品规格书.md")
        print("  projects/G20/测试报告.docx")
        print("  projects/G20/参数表.xlsx")
        return
    
    # 显示加载的项目
    print(f"成功加载 {len(loader.projects_data)} 个项目")
    print()
    
    for project_code, project_data in loader.projects_data.items():
        print(f"[项目] {project_code}")
        print(f"   文档数: {len(project_data['documents'])}")
        print()
        
        for doc_name, doc_data in project_data['documents'].items():
            print(f"   [文件] {doc_name}")
            print(f"      大小: {doc_data['size']} 字符")
            
            # 显示前100个字符
            preview = doc_data['content'][:100].replace('\n', ' ')
            print(f"      预览: {preview}...")
            print()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == '__main__':
    test_doc_loader()

