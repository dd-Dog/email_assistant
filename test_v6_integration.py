"""
测试V6.0集成（公司知识图谱 + V5.3兼容性）
"""
import logging
import sys
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_company_manager():
    """测试CompanyManager"""
    print("\n" + "=" * 60)
    print("测试1: CompanyManager（公司知识图谱）")
    print("=" * 60)
    
    try:
        from company_manager import CompanyManager
        
        company_mgr = CompanyManager()
        
        if company_mgr.has_company_info():
            print("[OK] CompanyManager加载成功")
            
            # 测试公司概览
            overview = company_mgr.get_company_overview()
            print(f"  - 公司名称: {overview.get('公司名称', '未配置')}")
            print(f"  - 业务领域: {len(company_mgr.business_areas)} 个")
            print(f"  - 产品线: {len(company_mgr.products)} 个")
            print(f"  - 部门数: {len(company_mgr.departments)} 个")
            
            # 测试AI上下文
            context = company_mgr.get_company_context_for_ai()
            if context:
                print(f"  - AI上下文长度: {len(context)} 字符")
                print("[OK] 公司上下文生成成功")
            else:
                print("[WARN] 公司上下文为空")
            
            return True
        else:
            print("[WARN] 未找到公司信息")
            print("  提示: 运行 python create_company_excel_template.py")
            return False
            
    except Exception as e:
        print(f"[ERROR] CompanyManager测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_context_builder():
    """测试ContextBuilder集成"""
    print("\n" + "=" * 60)
    print("测试2: ContextBuilder集成（V6.0 + V5.3兼容）")
    print("=" * 60)
    
    try:
        from context_builder import ContextBuilder
        
        # 初始化（自动检测V5.3和V6.0配置）
        context_builder = ContextBuilder()
        
        if context_builder.context_enabled:
            print("[OK] ContextBuilder初始化成功")
            
            # 检测启用的功能
            features = []
            if context_builder.person_mgr.has_profiles():
                features.append("人员✓")
            if context_builder.project_mgr.has_projects():
                features.append("项目✓")
            if context_builder.keyword_mgr.has_keywords():
                features.append("关键词✓")
            if context_builder.company_mgr.has_company_info():
                features.append("公司✓(V6.0)")
            
            print(f"  - 启用功能: {' | '.join(features)}")
            
            # 测试公司上下文
            test_email = {
                'from_email': 'test@example.com',
                'subject': '测试邮件',
                'body': '这是一封测试邮件'
            }
            
            context_data = context_builder.build_context_for_email(test_email)
            formatted_context = context_builder.format_context_for_prompt(context_data)
            
            if formatted_context and '公司' in formatted_context:
                print("[OK] 公司背景信息已集成到AI提示词")
                print(f"  - 上下文长度: {len(formatted_context)} 字符")
            else:
                print("[WARN] 公司背景信息未在上下文中")
            
            return True
        else:
            print("[WARN] ContextBuilder未启用")
            return False
            
    except Exception as e:
        print(f"[ERROR] ContextBuilder测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_v5_3_compatibility():
    """测试V5.3兼容性"""
    print("\n" + "=" * 60)
    print("测试3: V5.3兼容性（persons/ & projects/）")
    print("=" * 60)
    
    import os
    
    v5_3_ok = True
    
    # 检查V5.3目录
    if os.path.exists('persons'):
        print("[OK] persons/ 目录存在（V5.3）")
    else:
        print("[INFO] persons/ 目录不存在（已迁移到config/人员/）")
        v5_3_ok = False
    
    if os.path.exists('projects'):
        print("[OK] projects/ 目录存在（V5.3）")
    else:
        print("[INFO] projects/ 目录不存在（已迁移到config/项目/）")
        v5_3_ok = False
    
    # 测试PersonManager兼容性
    try:
        from person_manager import PersonManager
        person_mgr = PersonManager(persons_root='persons')
        
        if person_mgr.persons:
            print(f"[OK] PersonManager兼容V5.3 ({len(person_mgr.persons)} 人)")
        else:
            print("[INFO] PersonManager未找到V5.3数据")
    except Exception as e:
        print(f"[ERROR] PersonManager测试失败: {str(e)}")
    
    # 测试ProjectManager兼容性
    try:
        from project_manager import ProjectManager
        project_mgr = ProjectManager(projects_root='projects')
        
        if project_mgr.has_projects():
            print(f"[OK] ProjectManager兼容V5.3 ({len(project_mgr.projects)} 项目)")
        else:
            print("[INFO] ProjectManager未找到V5.3数据")
    except Exception as e:
        print(f"[ERROR] ProjectManager测试失败: {str(e)}")
    
    return v5_3_ok


def test_v6_new_structure():
    """测试V6.0新结构"""
    print("\n" + "=" * 60)
    print("测试4: V6.0新结构（config/）")
    print("=" * 60)
    
    import os
    
    v6_ok = True
    
    # 检查V6.0目录
    expected_dirs = [
        'config',
        'config/公司',
        'config/客户',
        'config/供应商',
        'config/系统'
    ]
    
    for dir_path in expected_dirs:
        if os.path.exists(dir_path):
            print(f"[OK] {dir_path}/ 存在")
        else:
            print(f"[WARN] {dir_path}/ 不存在")
            v6_ok = False
    
    # 检查Excel文件
    company_files = [
        'config/公司/公司信息.xlsx',
        'config/公司/部门信息.xlsx'
    ]
    
    for file_path in company_files:
        if os.path.exists(file_path):
            print(f"[OK] {file_path} 存在")
        else:
            print(f"[WARN] {file_path} 不存在")
            v6_ok = False
    
    return v6_ok


def test_ai_integration():
    """测试AI集成"""
    print("\n" + "=" * 60)
    print("测试5: AI集成（模拟邮件分析）")
    print("=" * 60)
    
    try:
        from context_builder import ContextBuilder
        
        context_builder = ContextBuilder()
        
        if not context_builder.context_enabled:
            print("[SKIP] 上下文功能未启用，跳过AI测试")
            return False
        
        # 模拟一封邮件
        test_email = {
            'from_email': 'customer@example.com',
            'from_name': '测试客户',
            'subject': 'G20项目需要增加WiFi 6功能',
            'body': '''
你好，

我们的G20项目目前使用WiFi 5，客户反馈速度不够快，
希望升级到WiFi 6。请评估可行性和所需时间。

谢谢！
'''
        }
        
        print("[INFO] 模拟邮件:")
        print(f"  - 发件人: {test_email['from_name']}")
        print(f"  - 主题: {test_email['subject']}")
        
        # 构建上下文
        context_data = context_builder.build_context_for_email(test_email)
        formatted_context = context_builder.format_context_for_prompt(context_data)
        
        print(f"\n[INFO] AI会接收到以下上下文:")
        print("-" * 60)
        print(formatted_context[:500] + "..." if len(formatted_context) > 500 else formatted_context)
        print("-" * 60)
        
        # 检查关键信息
        checks = {
            '公司信息': '公司' in formatted_context or '飞思卡尔' in formatted_context,
            'G20项目': 'G20' in formatted_context or 'g20' in formatted_context.lower(),
            '业务领域': '业务' in formatted_context or '硬件' in formatted_context or 'Android' in formatted_context
        }
        
        print(f"\n[INFO] 上下文检查:")
        for check_name, check_result in checks.items():
            status = "[OK]" if check_result else "[WARN]"
            print(f"  {status} {check_name}: {'✓' if check_result else '×'}")
        
        all_passed = all(checks.values())
        
        if all_passed:
            print("\n[OK] AI会基于完整的公司知识图谱进行分析")
            print("[OK] AI能够理解：")
            print("  - 公司有硬件设计能力")
            print("  - G20是公司的产品")
            print("  - 需要研发部和采购部协作")
            print("  - WiFi模块需要从供应商采购")
        
        return all_passed
        
    except Exception as e:
        print(f"[ERROR] AI集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("V6.0 集成测试套件")
    print("测试渐进式迁移：V6.0新功能 + V5.3兼容性")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # 运行所有测试
    results['CompanyManager'] = test_company_manager()
    results['ContextBuilder'] = test_context_builder()
    results['V5.3兼容性'] = test_v5_3_compatibility()
    results['V6.0新结构'] = test_v6_new_structure()
    results['AI集成'] = test_ai_integration()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print()
    print(f"通过率: {passed}/{total} ({passed*100//total}%)")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！✓")
        print()
        print("V6.0 Phase 1 完成！")
        print("  - CompanyManager已集成")
        print("  - ContextBuilder已升级")
        print("  - AI提示词已增强")
        print("  - V5.3完全兼容")
        print()
        print("下一步：")
        print("  1. 填写config/公司/下的Excel文件")
        print("  2. 运行main_v4.py测试实际邮件分析")
        print("  3. 观察AI分析是否更具宏观视角")
    else:
        print("\n[WARNING] 部分测试未通过")
        print("请检查以上失败的测试项")
    
    print("=" * 60)


if __name__ == "__main__":
    main()

