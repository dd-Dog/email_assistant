"""
人员信息管理模块 - V5.2
管理和查询人员的详细信息（支持文件加载）
"""
import json
import os
import logging
from person_file_loader import PersonFileLoader

logger = logging.getLogger(__name__)


class PersonManager:
    """人员信息管理器"""
    
    def __init__(self, profiles_file='profiles.json', persons_root='persons'):
        """初始化人员管理器（V5.2：支持文件加载）
        
        Args:
            profiles_file: 人员信息配置文件（JSON）
            persons_root: 人员信息文件夹
        """
        self.profiles_file = profiles_file
        self.persons_root = persons_root
        self.persons = {}
        
        # V5.2：从文件加载人员信息
        self.file_loader = PersonFileLoader(persons_root)
        
        self._load_profiles()
    
    def _load_profiles(self):
        """加载人员信息（V5.2：优先从文件加载）"""
        # 优先从文件加载
        file_persons = self.file_loader.get_all_persons()
        if file_persons:
            self.persons.update(file_persons)
            logger.info(f"✅ 从文件加载了 {len(file_persons)} 个人员信息")
        
        # 再从JSON加载（兼容旧版本）
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    json_persons = data.get('persons', {})
                    
                    # 合并（文件优先级更高）
                    for email, person in json_persons.items():
                        if email not in self.persons:
                            self.persons[email] = person
                    
                    if json_persons:
                        logger.info(f"✅ 从JSON加载了 {len(json_persons)} 个人员信息")
        except Exception as e:
            logger.error(f"从JSON加载人员信息失败: {str(e)}")
        
        if not self.persons:
            logger.info("ℹ️  未找到人员信息")
    
    def get_person_info(self, email):
        """获取人员信息
        
        Args:
            email: 邮箱地址
            
        Returns:
            人员信息字典，如果不存在返回None
        """
        return self.persons.get(email)
    
    def get_person_context(self, email):
        """获取人员上下文信息（用于AI提示词）
        
        Args:
            email: 邮箱地址
            
        Returns:
            格式化的上下文字符串
        """
        person = self.get_person_info(email)
        if not person:
            return ""
        
        context_parts = []
        
        # 基本信息
        name = person.get('name', '')
        company = person.get('company', '')
        role = person.get('role', '')
        
        context_parts.append(f"发件人背景：{name}")
        if company:
            context_parts.append(f"- 公司：{company}")
        if role:
            context_parts.append(f"- 职位：{role}")
        
        # 技能和经验
        skills = person.get('skills', [])
        if skills:
            context_parts.append(f"- 技能：{', '.join(skills[:5])}")
        
        experience_years = person.get('experience_years')
        if experience_years:
            context_parts.append(f"- 工作经验：{experience_years}年")
        
        education = person.get('education')
        if education:
            context_parts.append(f"- 学历：{education}")
        
        # 技术水平（客户专用）
        technical_level = person.get('technical_level')
        if technical_level:
            level_map = {
                'expert': '技术专家，可以深入讨论技术细节',
                'intermediate': '有一定技术背景，理解技术概念',
                'basic': '技术背景较弱，需要简化说明'
            }
            context_parts.append(f"- 技术水平：{level_map.get(technical_level, technical_level)}")
        
        # 负责项目
        projects = person.get('projects', [])
        if projects:
            context_parts.append(f"- 负责项目：{', '.join(projects)}")
        
        # 职责
        responsibilities = person.get('responsibilities')
        if responsibilities:
            context_parts.append(f"- 职责：{responsibilities}")
        
        # 沟通风格（客户专用）
        communication_style = person.get('communication_style')
        if communication_style:
            context_parts.append(f"- 沟通风格：{communication_style}")
        
        # 关注点（客户专用）
        priorities = person.get('priorities', [])
        if priorities:
            context_parts.append(f"- 关注点：{', '.join(priorities)}")
        
        # 备注
        notes = person.get('notes')
        if notes:
            context_parts.append(f"- 备注：{notes}")
        
        return '\n'.join(context_parts)
    
    def get_all_persons_by_type(self, person_type):
        """获取某类人员的所有信息
        
        Args:
            person_type: 人员类型 (customer/supplier/leader/pm/employee)
            
        Returns:
            该类型的人员字典
        """
        result = {}
        for email, person in self.persons.items():
            if person.get('type') == person_type:
                result[email] = person
        return result
    
    def has_profiles(self):
        """检查是否有人员信息"""
        return len(self.persons) > 0

