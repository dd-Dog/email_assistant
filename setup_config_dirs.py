"""
创建V6.0统一配置目录结构
"""
import os

def create_config_structure():
    """创建config/目录结构"""
    
    # 定义目录结构
    directories = [
        "config",
        "config/公司",
        "config/客户",
        "config/供应商",
        "config/系统"
    ]
    
    print("=" * 60)
    print("创建 V6.0 统一配置目录结构")
    print("=" * 60)
    print()
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ 创建目录: {directory}")
        except Exception as e:
            print(f"✗ 创建目录失败 {directory}: {str(e)}")
    
    print()
    print("=" * 60)
    print("✓ 目录结构创建完成")
    print("=" * 60)
    print()
    print("当前结构：")
    print("config/")
    print("├── 公司/      ← 公司知识图谱")
    print("├── 客户/      ← 客户信息管理")
    print("├── 供应商/    ← 供应商信息管理")
    print("└── 系统/      ← 系统配置")
    print()
    print("V5.3目录保持不变：")
    print("├── persons/   ← 人员信息（V5.3继续使用）")
    print("└── projects/  ← 项目文档（V5.3继续使用）")
    print()

if __name__ == "__main__":
    create_config_structure()

