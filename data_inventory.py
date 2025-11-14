"""
企业数据盘点工具
帮助用户了解当前拥有的数据和缺失的数据
"""
import os
import json
from pathlib import Path
from datetime import datetime


class DataInventory:
    """数据盘点器"""
    
    def __init__(self):
        self.results = {
            '现有数据': {},
            '缺失数据': {},
            '数据质量': {},
            '建议': []
        }
    
    def check_technical_knowledge(self):
        """检查技术知识库"""
        print("\n" + "=" * 70)
        print("1. 技术知识库盘点")
        print("=" * 70)
        
        # 检查芯片供应商文档
        supplier_docs = Path("knowledge/suppliers") if Path("knowledge/suppliers").exists() else None
        
        if supplier_docs and supplier_docs.is_dir():
            suppliers = [d.name for d in supplier_docs.iterdir() if d.is_dir()]
            print(f"✓ 芯片供应商文档: {len(suppliers)} 个供应商")
            for supplier in suppliers:
                chip_dir = supplier_docs / supplier / "chips"
                if chip_dir.exists():
                    chips = [d.name for d in chip_dir.iterdir() if d.is_dir()]
                    print(f"  - {supplier}: {len(chips)} 个芯片型号")
            self.results['现有数据']['芯片供应商文档'] = len(suppliers)
        else:
            print("✗ 芯片供应商文档: 未配置")
            self.results['缺失数据']['芯片供应商文档'] = True
            self.results['建议'].append({
                'type': '高优先级',
                'item': '芯片供应商技术文档',
                'reason': '影响技术方案准确性',
                'action': '创建 knowledge/suppliers/ 目录，添加芯片规格书、技术指导等'
            })
    
    def check_project_knowledge(self):
        """检查项目知识库"""
        print("\n" + "=" * 70)
        print("2. 项目知识库盘点")
        print("=" * 70)
        
        projects_dir = Path("projects")
        
        if projects_dir.exists():
            projects = [d.name for d in projects_dir.iterdir() if d.is_dir()]
            print(f"✓ 项目数量: {len(projects)} 个")
            
            for project in projects:
                project_path = projects_dir / project
                print(f"\n  【{project}】")
                
                # 检查项目定义书
                definition_dir = project_path / "project_definition"
                if definition_dir.exists():
                    files = list(definition_dir.glob("*"))
                    print(f"    ✓ 项目定义书: {len(files)} 个文件")
                else:
                    print(f"    ✗ 项目定义书: 缺失")
                
                # 检查项目计划
                plan_dir = project_path / "project_plan"
                if plan_dir.exists():
                    files = list(plan_dir.glob("*"))
                    print(f"    ✓ 项目计划: {len(files)} 个文件")
                else:
                    print(f"    ✗ 项目计划: 缺失")
                
                # 检查测试报告
                test_dir = project_path / "test_reports"
                if test_dir.exists():
                    files = list(test_dir.glob("*"))
                    print(f"    ✓ 测试报告: {len(files)} 个文件")
                else:
                    print(f"    ✗ 测试报告: 缺失")
                
                # 检查项目元数据
                metadata_file = project_path / "metadata.json"
                if metadata_file.exists():
                    print(f"    ✓ 项目元数据: 存在")
                else:
                    print(f"    ✗ 项目元数据: 缺失")
            
            self.results['现有数据']['项目'] = len(projects)
        else:
            print("✗ 项目目录不存在")
            self.results['缺失数据']['项目'] = True
        
        self.results['建议'].append({
            'type': '高优先级',
            'item': '项目完整信息',
            'reason': '影响延期评估和资源分配准确性',
            'action': '为每个项目添加：project_definition/, project_plan/, test_reports/, metadata.json'
        })
    
    def check_organization_resources(self):
        """检查组织与资源数据"""
        print("\n" + "=" * 70)
        print("3. 组织与资源盘点")
        print("=" * 70)
        
        # 人员信息
        persons_file = Path("persons/人员信息表_V5.3.xlsx")
        if persons_file.exists():
            print(f"✓ 人员信息: 存在（Excel格式）")
            self.results['现有数据']['人员信息'] = True
        else:
            print(f"✗ 人员信息: 缺失")
            self.results['缺失数据']['人员信息'] = True
        
        # 部门生产力配置
        dept_capacity = Path("config/组织/部门生产力配置.xlsx")
        if dept_capacity.exists():
            print(f"✓ 部门生产力配置: 存在")
            self.results['现有数据']['部门配置'] = True
        else:
            print(f"✗ 部门生产力配置: 缺失")
            self.results['缺失数据']['部门配置'] = True
            self.results['建议'].append({
                'type': '高优先级',
                'item': '部门生产力配置',
                'reason': '影响资源评估和产能计算',
                'action': '创建 config/组织/部门生产力配置.xlsx，包含：\n' +
                         '  - 软件部：服务器配置、开发工具、开发能力\n' +
                         '  - 生产部：生产线配置、日产能、质量控制能力'
            })
        
        # 客户信息
        customer_file = Path("config/客户/客户信息.xlsx")
        if customer_file.exists():
            print(f"✓ 客户信息: 存在")
            self.results['现有数据']['客户信息'] = True
        else:
            print(f"✗ 客户信息: 缺失")
            self.results['缺失数据']['客户信息'] = True
        
        # 供应商信息
        supplier_file = Path("config/供应商/供应商信息.xlsx")
        if supplier_file.exists():
            print(f"✓ 供应商信息: 存在")
            self.results['现有数据']['供应商信息'] = True
        else:
            print(f"✗ 供应商信息: 缺失")
            self.results['缺失数据']['供应商信息'] = True
            self.results['建议'].append({
                'type': '高优先级',
                'item': '供应商详细信息',
                'reason': '影响采购周期和成本评估',
                'action': '创建供应商信息表，包含：\n' +
                         '  - 芯片供应商（展锐等）：供货周期、MOQ、价格\n' +
                         '  - 器件供应商：供货周期、库存水平'
            })
        
        # 市场反馈
        market_file = Path("config/市场/市场反馈.xlsx")
        if market_file.exists():
            print(f"✓ 市场反馈: 存在")
            self.results['现有数据']['市场反馈'] = True
        else:
            print(f"✗ 市场反馈: 缺失")
            self.results['缺失数据']['市场反馈'] = True
    
    def check_process_workflows(self):
        """检查流程与协作"""
        print("\n" + "=" * 70)
        print("4. 流程与协作盘点")
        print("=" * 70)
        
        # 工作流程
        workflow_file = Path("config/流程/研发工作流程.xlsx")
        if workflow_file.exists():
            print(f"✓ 研发工作流程: 存在")
            self.results['现有数据']['工作流程'] = True
        else:
            print(f"✗ 研发工作流程: 缺失")
            self.results['缺失数据']['工作流程'] = True
            self.results['建议'].append({
                'type': '高优先级',
                'item': '详细工作流程',
                'reason': '影响流程建议和责任人识别',
                'action': '创建 config/流程/研发工作流程.xlsx，细化到：\n' +
                         '  - 每个环节的责任人\n' +
                         '  - 每个环节的时限\n' +
                         '  - 人员间的协作关系\n' +
                         '  - 决策审批链'
            })
        
        # 协作关系
        collab_file = Path("config/流程/协作关系网络.xlsx")
        if collab_file.exists():
            print(f"✓ 协作关系网络: 存在")
            self.results['现有数据']['协作关系'] = True
        else:
            print(f"✗ 协作关系网络: 缺失")
            self.results['缺失数据']['协作关系'] = True
    
    def check_historical_emails(self):
        """检查历史邮件"""
        print("\n" + "=" * 70)
        print("5. 历史数据盘点")
        print("=" * 70)
        
        # 检查AI缓存（间接反映历史邮件数量）
        cache_file = Path("ai_cache/analysis_cache.json")
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    print(f"✓ 历史邮件分析缓存: {len(cache_data)} 封")
                    self.results['现有数据']['历史邮件'] = len(cache_data)
            except:
                print(f"✗ 无法读取缓存")
        else:
            print(f"ℹ️  历史邮件分析缓存: 无")
    
    def generate_summary(self):
        """生成总结报告"""
        print("\n" + "=" * 70)
        print("数据盘点总结")
        print("=" * 70)
        
        existing_count = len(self.results['现有数据'])
        missing_count = len(self.results['缺失数据'])
        
        print(f"\n【现有数据】: {existing_count} 项")
        for key, value in self.results['现有数据'].items():
            print(f"  ✓ {key}: {value if not isinstance(value, bool) else '已配置'}")
        
        print(f"\n【缺失数据】: {missing_count} 项")
        for key in self.results['缺失数据'].keys():
            print(f"  ✗ {key}")
        
        print(f"\n【数据完整度】: {existing_count / (existing_count + missing_count) * 100:.1f}%")
        
        if existing_count < 5:
            print("  ⚠️  数据严重不足，AI分析能力受限")
        elif existing_count < 10:
            print("  ⚡ 数据基本满足，但还有提升空间")
        else:
            print("  ✓ 数据较为完整，AI能力充分发挥")
        
        print(f"\n【优先级建议】: {len(self.results['建议'])} 项")
        for idx, suggestion in enumerate(self.results['建议'], 1):
            print(f"\n  {idx}. [{suggestion['type']}] {suggestion['item']}")
            print(f"     原因: {suggestion['reason']}")
            print(f"     行动: {suggestion['action']}")
    
    def run_inventory(self):
        """运行完整盘点"""
        print("=" * 70)
        print("企业数据盘点工具")
        print("=" * 70)
        print(f"盘点时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.check_technical_knowledge()
        self.check_project_knowledge()
        self.check_organization_resources()
        self.check_process_workflows()
        self.check_historical_emails()
        self.generate_summary()
        
        # 生成下一步建议
        print("\n" + "=" * 70)
        print("下一步建议")
        print("=" * 70)
        
        print("\n【立即可做】")
        print("  1. 创建基础目录结构")
        print("     python create_knowledge_base_structure.py")
        print()
        print("  2. 从历史邮件自动提取基础数据")
        print("     python auto_extract_from_emails.py")
        print()
        print("  3. 逐步补充关键数据（迭代方式）")
        print("     - 第1周: 补充芯片文档和项目计划")
        print("     - 第2周: 补充部门配置和工作流程")
        print("     - 第3周: 补充供应商信息和市场反馈")
        
        print("\n【数据采集工具】")
        print("  方式A: 自动提取（推荐）")
        print("    - 从邮件自动提取：python auto_extract_from_emails.py")
        print("    - 从文档自动解析：python auto_parse_documents.py")
        print()
        print("  方式B: 交互式录入")
        print("    - 对话式采集：python interactive_data_entry.py")
        print("    - Web界面录入：(未来开发)")
        print()
        print("  方式C: 导入现有文件")
        print("    - 直接复制文档到指定目录")
        print("    - AI自动索引和结构化")
        
        print("\n" + "=" * 70)
        print("盘点完成！")
        print("=" * 70)


if __name__ == "__main__":
    inventory = DataInventory()
    inventory.run_inventory()

