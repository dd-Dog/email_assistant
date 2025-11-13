# -*- coding: utf-8 -*-
"""
测试人员信息加载器
"""
import logging
from person_manager import PersonManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_person_loader():
    """测试人员信息加载"""
    print("=" * 60)
    print("人员信息加载测试")
    print("=" * 60)
    print()
    
    # 创建人员管理器
    person_mgr = PersonManager(persons_root='persons')
    
    if not person_mgr.has_profiles():
        print("未找到人员信息")
        print()
        print("请确保以下位置有人员信息：")
        print("  1. persons/人员信息表.xlsx (Excel批量管理)")
        print("  2. persons/姓名.md (Markdown个人档案)")
        print()
        print("运行以下命令创建模板：")
        print("  python create_person_excel_template.py")
        return
    
    # 显示加载的人员
    all_persons = person_mgr.persons
    print(f"成功加载 {len(all_persons)} 个人员信息")
    print()
    
    # 按类型分组
    person_types = {}
    for email, person in all_persons.items():
        person_type = person.get('type', 'unknown')
        if person_type not in person_types:
            person_types[person_type] = []
        person_types[person_type].append(person)
    
    # 显示各类人员
    type_names = {
        'customer': '客户',
        'supplier': '供应商',
        'leader': '领导',
        'pm': '项目经理',
        'employee': '员工'
    }
    
    for person_type, persons_list in person_types.items():
        type_name = type_names.get(person_type, person_type)
        print(f"[{type_name}] {len(persons_list)}人")
        print()
        
        for person in persons_list:
            name = person.get('name', '未知')
            email = person.get('email', '')
            company = person.get('company', '')
            role = person.get('role', '')
            
            print(f"  - {name} ({email})")
            if company:
                print(f"    公司: {company}")
            if role:
                print(f"    职位: {role}")
            
            # 显示技能
            skills = person.get('skills', [])
            if skills:
                if isinstance(skills, list):
                    skills_str = ', '.join(skills[:5])
                else:
                    skills_str = str(skills)
                print(f"    技能: {skills_str}")
            
            # 显示项目
            projects = person.get('projects', [])
            if projects:
                if isinstance(projects, list):
                    projects_str = ', '.join(projects)
                else:
                    projects_str = str(projects)
                print(f"    项目: {projects_str}")
            
            print()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == '__main__':
    test_person_loader()

