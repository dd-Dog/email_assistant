"""
项目信息管理模块 - V5.0
管理和查询项目的详细信息
"""
import json
import os
import logging
import re

logger = logging.getLogger(__name__)


class ProjectManager:
    """项目信息管理器"""
    
    def __init__(self, profiles_file='profiles.json'):
        """初始化项目管理器
        
        Args:
            profiles_file: 项目信息配置文件
        """
        self.profiles_file = profiles_file
        self.projects = {}
        self.project_keywords = {}
        self._load_profiles()
    
    def _load_profiles(self):
        """加载项目信息"""
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.projects = data.get('projects', {})
                    self.project_keywords = data.get('project_keywords', {})
                logger.info(f"✅ 加载了 {len(self.projects)} 个项目信息")
            else:
                logger.warning(f"项目信息文件不存在: {self.profiles_file}")
                self.projects = {}
                self.project_keywords = {}
        except Exception as e:
            logger.error(f"加载项目信息失败: {str(e)}")
            self.projects = {}
            self.project_keywords = {}
    
    def get_project_info(self, project_code):
        """获取项目信息
        
        Args:
            project_code: 项目代码
            
        Returns:
            项目信息字典，如果不存在返回None
        """
        return self.projects.get(project_code)
    
    def detect_project_in_text(self, text):
        """从文本中检测项目关键词
        
        Args:
            text: 邮件主题或内容
            
        Returns:
            检测到的项目代码列表
        """
        detected_projects = []
        
        for project_code, keywords in self.project_keywords.items():
            for keyword in keywords:
                # 不区分大小写的搜索
                if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                    if project_code not in detected_projects:
                        detected_projects.append(project_code)
                    break
        
        return detected_projects
    
    def get_project_context(self, project_code):
        """获取项目上下文信息（用于AI提示词）
        
        Args:
            project_code: 项目代码
            
        Returns:
            格式化的上下文字符串
        """
        project = self.get_project_info(project_code)
        if not project:
            return ""
        
        context_parts = []
        
        # 基本信息
        full_name = project.get('full_name', project.get('name', project_code))
        context_parts.append(f"相关项目：{full_name} ({project_code})")
        
        status = project.get('status')
        if status:
            status_map = {
                'planning': '规划阶段',
                'development': '开发阶段',
                'testing': '测试阶段',
                'completed': '已完成',
                'in_progress': '进行中',
                'bug_fix': 'Bug修复'
            }
            context_parts.append(f"- 状态：{status_map.get(status, status)}")
        
        # 当前阶段
        current_phase = project.get('current_phase')
        if current_phase:
            context_parts.append(f"- 当前阶段：{current_phase}")
        
        # 进度
        progress = project.get('progress')
        if progress:
            context_parts.append(f"- 进度：{progress}")
        
        # 客户
        customer = project.get('customer')
        if customer:
            context_parts.append(f"- 客户：{customer}")
        
        # 技术栈
        tech_stack = project.get('tech_stack')
        if tech_stack:
            if isinstance(tech_stack, dict):
                tech_items = []
                for key, value in tech_stack.items():
                    tech_items.append(f"{value}")
                context_parts.append(f"- 技术：{', '.join(tech_items)}")
            elif isinstance(tech_stack, list):
                context_parts.append(f"- 技术栈：{', '.join(tech_stack)}")
        
        # 关键功能
        key_features = project.get('key_features', [])
        if key_features:
            context_parts.append(f"- 关键功能：{', '.join(key_features[:3])}")
        
        # 当前问题/挑战
        current_issues = project.get('current_issues', [])
        if current_issues:
            context_parts.append(f"- 当前挑战：{', '.join(current_issues[:3])}")
        
        # 截止时间
        deadline = project.get('deadline')
        if deadline:
            context_parts.append(f"- 截止时间：{deadline}")
        
        # 备注
        notes = project.get('notes')
        if notes:
            context_parts.append(f"- 备注：{notes}")
        
        return '\n'.join(context_parts)
    
    def get_project_brief(self, project_code):
        """获取项目简要信息（用于报告显示）
        
        Args:
            project_code: 项目代码
            
        Returns:
            简要信息字符串
        """
        project = self.get_project_info(project_code)
        if not project:
            return project_code
        
        name = project.get('name', project_code)
        status = project.get('status', '')
        progress = project.get('progress', '')
        
        brief_parts = [name]
        if status:
            brief_parts.append(status)
        if progress:
            brief_parts.append(progress)
        
        return ' | '.join(brief_parts)
    
    def has_projects(self):
        """检查是否有项目信息"""
        return len(self.projects) > 0

