"""
组织关系管理器 - V5.3
管理人员之间的层级和协作关系
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class OrgRelationshipManager:
    """组织关系管理器"""
    
    def __init__(self, persons_dict):
        """初始化组织关系管理器
        
        Args:
            persons_dict: 人员信息字典 {email: person_info}
        """
        self.persons = persons_dict
        self._build_relationships()
    
    def _build_relationships(self):
        """构建组织关系索引"""
        # 按姓名索引
        self.name_to_email = {}
        for email, person in self.persons.items():
            name = person.get('name')
            if name:
                self.name_to_email[name] = email
        
        # 按部门索引
        self.department_members = {}  # {部门: [email列表]}
        self.department_leaders = {}  # {部门: leader_email}
        
        # 按直属领导索引
        self.leader_subordinates = {}  # {leader_email: [subordinate_email列表]}
        
        # PM-客户映射
        self.pm_customers = {}  # {pm_email: [customer_email列表]}
        
        # 高层-部门映射
        self.leader_departments = {}  # {leader_email: [部门列表]}
        
        # 构建索引
        for email, person in self.persons.items():
            person_type = person.get('type', '')
            
            # 部门索引
            department = person.get('department')
            if department:
                if department not in self.department_members:
                    self.department_members[department] = []
                self.department_members[department].append(email)
                
                # 部门领导
                if person_type == 'department_leader':
                    self.department_leaders[department] = email
            
            # 直属领导关系
            direct_leader_name = person.get('direct_leader')
            if direct_leader_name:
                leader_email = self.name_to_email.get(direct_leader_name)
                if leader_email:
                    if leader_email not in self.leader_subordinates:
                        self.leader_subordinates[leader_email] = []
                    self.leader_subordinates[leader_email].append(email)
            
            # PM-客户关系
            if person_type == 'pm':
                customer_names = person.get('managed_customers', '')
                if customer_names:
                    customer_list = [c.strip() for c in customer_names.split(',')]
                    self.pm_customers[email] = []
                    for customer_name in customer_list:
                        customer_email = self.name_to_email.get(customer_name)
                        if customer_email:
                            self.pm_customers[email].append(customer_email)
            
            # 高层-部门关系
            if person_type == 'top_leader':
                departments = person.get('managed_departments', '')
                if departments:
                    dept_list = [d.strip() for d in departments.split(',')]
                    self.leader_departments[email] = dept_list
    
    def get_direct_leader(self, person_email):
        """获取直属领导
        
        Args:
            person_email: 人员邮箱
            
        Returns:
            直属领导信息 {name, email, position} 或 None
        """
        person = self.persons.get(person_email)
        if not person:
            return None
        
        leader_name = person.get('direct_leader')
        if not leader_name:
            return None
        
        leader_email = self.name_to_email.get(leader_name)
        if not leader_email:
            return None
        
        leader = self.persons.get(leader_email)
        if not leader:
            return None
        
        return {
            'name': leader.get('name'),
            'email': leader_email,
            'position': leader.get('role', ''),
            'type': leader.get('type', '')
        }
    
    def get_subordinates(self, leader_email):
        """获取下属列表
        
        Args:
            leader_email: 领导邮箱
            
        Returns:
            下属信息列表
        """
        subordinate_emails = self.leader_subordinates.get(leader_email, [])
        
        result = []
        for email in subordinate_emails:
            person = self.persons.get(email)
            if person:
                result.append({
                    'name': person.get('name'),
                    'email': email,
                    'position': person.get('role', ''),
                    'department': person.get('department', '')
                })
        
        return result
    
    def get_department_members(self, department):
        """获取部门成员
        
        Args:
            department: 部门名称
            
        Returns:
            部门成员列表
        """
        member_emails = self.department_members.get(department, [])
        
        result = []
        for email in member_emails:
            person = self.persons.get(email)
            if person:
                result.append({
                    'name': person.get('name'),
                    'email': email,
                    'position': person.get('role', ''),
                    'type': person.get('type', '')
                })
        
        return result
    
    def get_department_leader(self, department):
        """获取部门领导
        
        Args:
            department: 部门名称
            
        Returns:
            部门领导信息或None
        """
        leader_email = self.department_leaders.get(department)
        if not leader_email:
            return None
        
        leader = self.persons.get(leader_email)
        if not leader:
            return None
        
        return {
            'name': leader.get('name'),
            'email': leader_email,
            'position': leader.get('role', '')
        }
    
    def get_pm_customers(self, pm_email):
        """获取PM负责的客户
        
        Args:
            pm_email: PM邮箱
            
        Returns:
            客户列表
        """
        customer_emails = self.pm_customers.get(pm_email, [])
        
        result = []
        for email in customer_emails:
            customer = self.persons.get(email)
            if customer:
                result.append({
                    'name': customer.get('name'),
                    'email': email,
                    'company': customer.get('company', ''),
                    'position': customer.get('role', '')
                })
        
        return result
    
    def get_customer_pm(self, customer_email):
        """获取客户对应的PM
        
        Args:
            customer_email: 客户邮箱
            
        Returns:
            PM信息或None
        """
        for pm_email, customer_list in self.pm_customers.items():
            if customer_email in customer_list:
                pm = self.persons.get(pm_email)
                if pm:
                    return {
                        'name': pm.get('name'),
                        'email': pm_email,
                        'position': pm.get('role', '')
                    }
        return None
    
    def get_responsibility_chain(self, person_email):
        """获取责任链（从员工到高层的完整路径）
        
        Args:
            person_email: 人员邮箱
            
        Returns:
            责任链列表 [{name, email, position, type}]
        """
        chain = []
        current_email = person_email
        visited = set()  # 防止循环引用
        
        while current_email and current_email not in visited:
            visited.add(current_email)
            
            person = self.persons.get(current_email)
            if not person:
                break
            
            chain.append({
                'name': person.get('name'),
                'email': current_email,
                'position': person.get('role', ''),
                'type': person.get('type', ''),
                'department': person.get('department', '')
            })
            
            # 查找上级
            leader_name = person.get('direct_leader')
            if not leader_name:
                break
            
            current_email = self.name_to_email.get(leader_name)
        
        return chain
    
    def find_responsible_person(self, project_name=None, department=None):
        """查找项目或部门的责任人
        
        Args:
            project_name: 项目名称
            department: 部门名称
            
        Returns:
            责任人信息列表
        """
        result = []
        
        if project_name:
            # 查找负责该项目的人员
            for email, person in self.persons.items():
                projects = person.get('projects', [])
                if isinstance(projects, list):
                    if project_name in projects:
                        result.append({
                            'name': person.get('name'),
                            'email': email,
                            'position': person.get('role', ''),
                            'type': person.get('type', ''),
                            'department': person.get('department', '')
                        })
        
        if department and not result:
            # 查找部门领导
            leader = self.get_department_leader(department)
            if leader:
                result.append(leader)
        
        return result
    
    def get_org_summary(self):
        """获取组织架构摘要
        
        Returns:
            组织架构统计信息
        """
        type_count = {}
        for person in self.persons.values():
            person_type = person.get('type', 'unknown')
            type_count[person_type] = type_count.get(person_type, 0) + 1
        
        return {
            'total_persons': len(self.persons),
            'type_distribution': type_count,
            'departments': list(self.department_members.keys()),
            'department_count': len(self.department_members)
        }

