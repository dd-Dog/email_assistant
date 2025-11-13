# -*- coding: utf-8 -*-
"""
测试组织关系功能 - V5.3
"""
import logging
from person_manager import PersonManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_org_relationships():
    """测试组织关系功能"""
    print("=" * 70)
    print("组织关系测试 - V5.3")
    print("=" * 70)
    print()
    
    # 创建人员管理器
    person_mgr = PersonManager(persons_root='persons')
    
    if not person_mgr.has_profiles():
        print("未找到人员信息")
        print("请先创建 persons/人员信息表_V5.3.xlsx")
        return
    
    if not person_mgr.org_manager:
        print("组织关系管理器未初始化")
        return
    
    print(f"成功加载 {len(person_mgr.persons)} 个人员")
    print()
    
    # 测试1：组织架构摘要
    print("=" * 70)
    print("[测试1] 组织架构摘要")
    print("=" * 70)
    summary = person_mgr.get_org_summary()
    print(f"总人数: {summary.get('total_persons', 0)}")
    print()
    print("人员类型分布:")
    for person_type, count in summary.get('type_distribution', {}).items():
        type_names = {
            'top_leader': '高层领导',
            'department_leader': '部门领导',
            'pm': '项目经理',
            'employee': '员工',
            'customer': '客户',
            'supplier': '供应商',
            'leader': '领导（旧类型）'
        }
        type_name = type_names.get(person_type, person_type)
        print(f"  {type_name}: {count}人")
    print()
    print(f"部门数量: {summary.get('department_count', 0)}")
    print(f"部门列表: {', '.join(summary.get('departments', []))}")
    print()
    
    # 测试2：查找直属领导
    print("=" * 70)
    print("[测试2] 查找直属领导")
    print("=" * 70)
    test_employees = [
        'xingpp@flyscale.cn',
        'liyz@flyscale.cn',
        'sunxx@flyscale.cn'
    ]
    
    for email in test_employees:
        person = person_mgr.get_person_info(email)
        if person:
            name = person.get('name', '未知')
            leader = person_mgr.get_direct_leader(email)
            
            if leader:
                print(f"{name} → 直属领导: {leader['name']} ({leader['position']})")
            else:
                print(f"{name} → 无直属领导记录")
    print()
    
    # 测试3：查找下属
    print("=" * 70)
    print("[测试3] 查找下属列表")
    print("=" * 70)
    test_leaders = [
        ('chenqi@flyscale.cn', '陈琦'),
        ('xuzh@flyscale.cn', '徐智慧')
    ]
    
    for email, name in test_leaders:
        subordinates = person_mgr.get_subordinates(email)
        if subordinates:
            print(f"{name} 的下属 ({len(subordinates)}人):")
            for sub in subordinates:
                print(f"  - {sub['name']} ({sub['position']}) [{sub.get('department', '')}]")
        else:
            print(f"{name} 暂无下属记录")
        print()
    
    # 测试4：责任链
    print("=" * 70)
    print("[测试4] 责任链查询")
    print("=" * 70)
    test_email = 'xingpp@flyscale.cn'
    chain = person_mgr.get_responsibility_chain(test_email)
    
    if chain:
        print(f"邢鹏鹏的责任链:")
        for idx, person in enumerate(chain):
            indent = "  " * idx
            type_names = {
                'employee': '员工',
                'department_leader': '部门领导',
                'top_leader': '高层领导'
            }
            type_name = type_names.get(person['type'], person['type'])
            print(f"{indent}└─ {person['name']} ({person['position']}) [{type_name}]")
    else:
        print("未找到责任链")
    print()
    
    # 测试5：PM-客户关系
    print("=" * 70)
    print("[测试5] PM-客户关系")
    print("=" * 70)
    
    # 查找所有PM
    pms = person_mgr.get_persons_by_type('pm')
    for pm_email, pm_name in pms.items():
        customers = person_mgr.org_manager.get_pm_customers(pm_email)
        if customers:
            print(f"项目经理 {pm_name}:")
            for customer in customers:
                print(f"  → 负责客户: {customer['name']} ({customer['company']})")
        else:
            print(f"项目经理 {pm_name}: 暂无客户对接记录")
        print()
    
    # 测试6：项目责任人查找
    print("=" * 70)
    print("[测试6] 项目责任人查找")
    print("=" * 70)
    test_projects = ['G20项目', '889项目']
    
    for project in test_projects:
        responsible = person_mgr.find_responsible_person(project_name=project)
        if responsible:
            print(f"{project} 的责任人:")
            for person in responsible:
                type_names = {
                    'pm': '项目经理',
                    'employee': '员工',
                    'department_leader': '部门领导',
                    'customer': '客户'
                }
                type_name = type_names.get(person['type'], person['type'])
                dept = f" [{person.get('department', '')}]" if person.get('department') else ""
                print(f"  - {person['name']} ({person['position']}) [{type_name}]{dept}")
        else:
            print(f"{project}: 未找到责任人")
        print()
    
    print("=" * 70)
    print("测试完成")
    print("=" * 70)


if __name__ == '__main__':
    test_org_relationships()

