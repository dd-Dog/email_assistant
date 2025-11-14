"""
上下文构建器 - V6.0
为AI分析构建完整的上下文信息（集成公司知识图谱）
"""
import logging
from person_manager import PersonManager
from project_manager import ProjectManager
from keyword_manager import KeywordManager
from company_manager import CompanyManager  # V6.0：公司管理器

logger = logging.getLogger(__name__)


class ContextBuilder:
    """上下文构建器"""
    
    def __init__(self, profiles_file='profiles.json', projects_root='projects', company_root='config/公司'):
        """初始化上下文构建器（V6.0：集成公司知识图谱）"""
        self.person_mgr = PersonManager(profiles_file)
        self.project_mgr = ProjectManager(profiles_file, projects_root)
        self.keyword_mgr = KeywordManager()  # V5.1：关键词管理器
        self.company_mgr = CompanyManager(company_root)  # V6.0：公司管理器
        
        self.context_enabled = (self.person_mgr.has_profiles() or 
                               self.project_mgr.has_projects() or
                               self.keyword_mgr.has_keywords() or
                               self.company_mgr.has_company_info())
        
        if self.context_enabled:
            features = []
            if self.person_mgr.has_profiles():
                features.append("人员")
            if self.project_mgr.has_projects():
                features.append("项目")
            if self.keyword_mgr.has_keywords():
                features.append("关键词")
            if self.company_mgr.has_company_info():
                features.append("公司")  # V6.0新增
            
            logger.info(f"✅ 上下文功能已启用（{'/'.join(features)}）")
        else:
            logger.info("ℹ️  未配置上下文信息，使用基础分析模式")
    
    def build_context_for_email(self, email_item):
        """为邮件构建完整上下文
        
        Args:
            email_item: 邮件数据字典
            
        Returns:
            上下文字典 {person_context, project_contexts, detected_projects}
        """
        if not self.context_enabled:
            return None
        
        sender_email = email_item.get('from_email', '')
        subject = email_item.get('subject', '')
        body = email_item.get('body', '')
        
        # 获取发件人信息
        person_context = self.person_mgr.get_person_context(sender_email)
        
        # 检测邮件中提到的项目
        text_to_search = f"{subject} {body}"
        detected_projects = self.project_mgr.detect_project_in_text(text_to_search)
        
        # V5.1：检测关键词
        keyword_result = None
        if detected_projects:
            # 如果检测到项目，使用项目代码检测项目特定关键词
            keyword_result = self.keyword_mgr.detect_keywords_in_text(
                text_to_search, 
                detected_projects[0] if detected_projects else None
            )
        else:
            # 否则只检测通用关键词
            keyword_result = self.keyword_mgr.detect_keywords_in_text(text_to_search)
        
        # 获取项目详细信息
        project_contexts = []
        for project_code in detected_projects:
            project_context = self.project_mgr.get_project_context(project_code)
            if project_context:
                project_contexts.append({
                    'code': project_code,
                    'context': project_context
                })
        
        return {
            'person_context': person_context,
            'project_contexts': project_contexts,
            'detected_projects': detected_projects,
            'keyword_result': keyword_result  # V5.1：关键词检测结果
        }
    
    def format_context_for_prompt(self, context_data):
        """将上下文格式化为AI提示词
        
        Args:
            context_data: build_context_for_email返回的数据
            
        Returns:
            格式化的上下文字符串
        """
        if not context_data:
            # V6.0：即使没有邮件上下文，也提供公司背景
            if self.company_mgr.has_company_info():
                return self.company_mgr.get_company_context_for_ai()
            return ""
        
        parts = []
        
        # V6.0：公司背景信息（放在最前面，提供宏观视角）
        if self.company_mgr.has_company_info():
            company_context = self.company_mgr.get_company_context_for_ai()
            if company_context:
                parts.append(company_context)
        
        # 人员信息
        if context_data.get('person_context'):
            parts.append("=" * 40)
            parts.append("背景信息：")
            parts.append(context_data['person_context'])
        
        # 项目信息
        if context_data.get('project_contexts'):
            parts.append("")
            parts.append("涉及项目：")
            for proj in context_data['project_contexts']:
                parts.append(proj['context'])
                parts.append("")
        
        # V5.1：关键词上下文
        if context_data.get('keyword_result'):
            keyword_context = self.keyword_mgr.get_keyword_context(
                context_data['keyword_result']
            )
            if keyword_context:
                parts.append(keyword_context)
        
        if parts:
            parts.append("=" * 40)
            parts.append("")
            return '\n'.join(parts)
        
        return ""
    
    def get_project_brief_for_display(self, project_code):
        """获取项目简要信息用于报告显示
        
        Args:
            project_code: 项目代码
            
        Returns:
            简要信息字符串
        """
        return self.project_mgr.get_project_brief(project_code)

