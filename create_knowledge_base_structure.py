"""
创建完整的企业知识库目录结构
"""
import os
from pathlib import Path


def create_directory_structure():
    """创建目录结构"""
    
    directories = [
        # 技术知识库
        "knowledge",
        "knowledge/suppliers",
        "knowledge/suppliers/展锐(Unisoc)",
        "knowledge/suppliers/展锐(Unisoc)/chips",
        "knowledge/suppliers/展锐(Unisoc)/chips/T310",
        "knowledge/suppliers/展锐(Unisoc)/chips/T610",
        "knowledge/suppliers/展锐(Unisoc)/chips/T760",
        "knowledge/suppliers/展锐(Unisoc)/sdk",
        "knowledge/suppliers/展锐(Unisoc)/support",
        "knowledge/suppliers/其他供应商",
        
        # 项目知识库（扩展现有projects/）
        # 为现有项目创建子目录
        "projects/G20/project_definition",
        "projects/G20/project_plan",
        "projects/G20/test_reports",
        "projects/889/project_definition",
        "projects/889/project_plan",
        "projects/889/test_reports",
        
        # 组织与资源
        "config/组织",
        "config/客户",
        "config/供应商",
        "config/市场",
        
        # 流程与协作
        "config/流程",
    ]
    
    print("=" * 70)
    print("创建企业知识库目录结构")
    print("=" * 70)
    print()
    
    created = 0
    existed = 0
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            if not Path(directory).exists():
                print(f"[创建] {directory}")
                created += 1
            else:
                print(f"[存在] {directory}")
                existed += 1
        except Exception as e:
            print(f"[失败] {directory}: {str(e)}")
    
    print()
    print("=" * 70)
    print(f"目录创建完成: 新建 {created} 个，已存在 {existed} 个")
    print("=" * 70)
    print()
    
    print("目录结构：")
    print()
    print("knowledge/              <- 技术知识库")
    print("├── suppliers/")
    print("│   └── 展锐(Unisoc)/")
    print("│       ├── chips/")
    print("│       │   ├── T310/   <- 芯片规格书、技术文档")
    print("│       │   ├── T610/")
    print("│       │   └── T760/")
    print("│       ├── sdk/        <- SDK文档")
    print("│       └── support/    <- 技术支持文档")
    print()
    print("projects/               <- 项目知识库（扩展）")
    print("├── G20/")
    print("│   ├── project_definition/  <- 项目定义书")
    print("│   ├── project_plan/        <- 项目计划表")
    print("│   ├── test_reports/        <- 测试报告")
    print("│   └── docs/                <- 其他文档")
    print("└── 889/")
    print()
    print("config/                 <- 配置管理")
    print("├── 公司/               <- V6.0已创建")
    print("├── 组织/               <- 部门生产力配置")
    print("├── 客户/               <- 客户信息")
    print("├── 供应商/             <- 供应商信息")
    print("├── 市场/               <- 市场反馈")
    print("└── 流程/               <- 工作流程")
    print()


def create_readme_files():
    """创建README说明文件"""
    
    readmes = {
        "knowledge/README.md": """# 技术知识库

## 目录说明

### suppliers/ - 供应商技术文档
存放芯片供应商提供的各类技术文档

#### 展锐(Unisoc)/
- **chips/** - 芯片型号文档
  - T310/ - T310芯片相关文档
    - datasheet.pdf - 芯片规格书
    - technical_guide.pdf - 技术指导文档
    - customization.md - 定制化指南
    - errata.txt - 已知问题列表
  - T610/ - T610芯片文档
  - T760/ - T760芯片文档

- **sdk/** - SDK开发文档
  - android_sdk.md - Android SDK指南
  - driver_guide.pdf - 驱动开发指南

- **support/** - 技术支持文档
  - faq.md - 常见问题
  - troubleshooting.md - 问题排查指南

## 数据用途

AI会从这些文档中：
1. 查询芯片规格和能力
2. 搜索技术解决方案
3. 评估技术可行性
4. 提供技术参考

## 添加新文档

1. 在对应目录下添加文件
2. 支持格式：PDF/Word/Markdown/TXT
3. 程序会自动索引和解析
""",

        "projects/G20/project_definition/README.md": """# G20 项目定义书

## 文件说明

### 产品参数要求.xlsx
定义G20产品的所有参数要求
- 硬件参数（CPU、内存、WiFi、蓝牙等）
- 软件功能（Android版本、预装应用等）
- 性能指标（续航、性能跑分等）
- 质量标准（可靠性、环境适应性等）

### 软件需求规格说明.md
详细的软件功能需求
- 功能需求列表
- 性能需求
- 接口需求
- 安全需求

## AI如何使用

当收到需求变更邮件时，AI会：
1. 对比当前需求规格
2. 评估变更影响范围
3. 估算开发工作量
4. 预测进度影响
""",

        "projects/G20/project_plan/README.md": """# G20 项目计划

## 文件说明

### 项目计划表.xlsx
包含：
- 里程碑时间表
- 任务分解（WBS）
- 资源分配
- 关键路径
- 依赖关系

## AI如何使用

当收到新任务或问题时，AI会：
1. 查询当前项目进度
2. 评估对里程碑的影响
3. 计算是否会导致延期
4. 建议调整计划
""",

        "projects/G20/test_reports/README.md": """# G20 测试报告

## 文件命名规范

- alpha测试报告_YYYYMMDD.xlsx
- beta测试报告_YYYYMMDD.xlsx
- 性能测试报告_YYYYMMDD.pdf
- 稳定性测试报告_YYYYMMDD.xlsx

## 包含内容

- 测试结果统计
- Bug列表和统计
- 质量评估
- 遗留问题

## AI如何使用

当收到Bug报告邮件时，AI会：
1. 查询历史测试报告
2. 分析Bug趋势
3. 评估质量风险
4. 预测解决时间
""",

        "config/组织/README.md": """# 组织与资源配置

## 文件说明

### 部门生产力配置.xlsx

**软件部配置**
- 服务器配置（编译服务器、测试服务器）
- 开发工具（IDE、调试工具）
- 开发能力评估（人员配置、开发产能）

**生产部配置**
- 生产线配置（SMT、组装、测试）
- 日产能计算
- 质量控制能力
- 瓶颈分析

**其他部门**
- 测试部：测试设备、测试能力
- 采购部：采购能力、供应商资源

## AI如何使用

当收到产能相关问题时，AI会：
1. 查询生产能力
2. 计算交付时间
3. 识别瓶颈
4. 建议资源优化
""",

        "config/供应商/README.md": """# 供应商信息管理

## 文件说明

### 供应商信息.xlsx

**芯片供应商**
- 供应商名称（展锐、MTK等）
- 芯片型号列表
- 供货周期（下单到交货）
- MOQ（最小起订量）
- 价格信息
- 技术支持能力

**器件供应商**
- 供应商名称
- 主要器件类型
- 供货周期
- 库存水平
- 价格稳定性

## AI如何使用

当收到采购相关问题时，AI会：
1. 查询供货周期
2. 评估采购风险
3. 计算到货时间
4. 建议采购策略
""",

        "config/流程/README.md": """# 工作流程定义

## 文件说明

### 研发工作流程.xlsx

包含所有研发相关流程：
- 需求评审流程
- 开发流程
- 测试流程
- 发布流程

每个流程包括：
- 步骤编号
- 步骤名称
- 责任人
- 审批人
- 时限要求
- 输入/输出
- 协作人员

### 生产工作流程.xlsx

包含生产相关流程：
- 物料采购流程
- 生产排程流程
- 质量检验流程
- 成品入库流程

## AI如何使用

当收到任何工作邮件时，AI会：
1. 识别所属流程
2. 定位当前环节
3. 告知下一步操作
4. 推荐责任人
5. 预警超时风险
"""
    }
    
    print("=" * 70)
    print("创建README说明文件")
    print("=" * 70)
    print()
    
    for file_path, content in readmes.items():
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] {file_path}")
        except Exception as e:
            print(f"[FAIL] {file_path}: {str(e)}")
    
    print()
    print("=" * 70)
    print("README文件创建完成")
    print("=" * 70)


if __name__ == "__main__":
    create_directory_structure()
    print()
    create_readme_files()
    
    print()
    print("=" * 70)
    print("知识库结构创建完成！")
    print("=" * 70)
    print()
    print("下一步：")
    print("  1. 将您的文档复制到对应目录")
    print("  2. 运行 python data_inventory.py 检查完整度")
    print("  3. 运行 python auto_extract_from_emails.py 自动提取数据")
    print()

