"""
关键词管理器 - V5.1
管理通用关键词和项目关键词，识别重点内容
"""
import json
import os
import re
import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class KeywordManager:
    """关键词管理器"""
    
    def __init__(self, config_file='keyword_config.json'):
        """初始化关键词管理器
        
        Args:
            config_file: 关键词配置文件
        """
        self.config_file = config_file
        self.common_keywords = {}  # 通用关键词（产品相关）
        self.project_keywords = {}  # 项目特定关键词
        self._load_keywords()
    
    def _load_keywords(self):
        """加载关键词配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.common_keywords = data.get('common_keywords', {})
                    self.project_keywords = data.get('project_keywords', {})
                
                common_count = sum(len(v) for v in self.common_keywords.values())
                project_count = sum(len(v) for v in self.project_keywords.values())
                logger.info(f"✅ 加载了 {common_count} 个通用关键词，{project_count} 个项目关键词")
            else:
                logger.info(f"ℹ️  关键词配置文件不存在: {self.config_file}")
        except Exception as e:
            logger.error(f"加载关键词配置失败: {str(e)}")
    
    def detect_keywords_in_text(self, text, project_code=None):
        """检测文本中的关键词
        
        Args:
            text: 要检测的文本
            project_code: 项目代码（如果提供，会检测项目特定关键词）
            
        Returns:
            检测结果字典 {
                'common': {category: [keywords]},
                'project': [keywords],
                'is_important': bool
            }
        """
        result = {
            'common': {},
            'project': [],
            'is_important': False
        }
        
        text_lower = text.lower()
        
        # 检测通用关键词
        for category, keywords in self.common_keywords.items():
            found_keywords = []
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower):
                    found_keywords.append(keyword)
            
            if found_keywords:
                result['common'][category] = found_keywords
                result['is_important'] = True
        
        # 检测项目关键词
        if project_code and project_code in self.project_keywords:
            project_kws = self.project_keywords[project_code]
            for keyword in project_kws:
                if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower):
                    result['project'].append(keyword)
                    result['is_important'] = True
        
        return result
    
    def get_keyword_context(self, keyword_result):
        """获取关键词上下文说明（用于AI提示词）
        
        Args:
            keyword_result: detect_keywords_in_text的返回结果
            
        Returns:
            上下文字符串
        """
        if not keyword_result['is_important']:
            return ""
        
        parts = []
        parts.append("⚠️ 本邮件涉及重点关键词：")
        
        # 通用关键词
        for category, keywords in keyword_result['common'].items():
            category_name = self._get_category_name(category)
            parts.append(f"  【{category_name}】{', '.join(keywords)}")
        
        # 项目关键词
        if keyword_result['project']:
            parts.append(f"  【项目特定】{', '.join(keyword_result['project'])}")
        
        parts.append("请重点关注这些方面的内容！")
        parts.append("")
        
        return '\n'.join(parts)
    
    def get_keyword_tags(self, keyword_result):
        """获取关键词标签（用于报告显示）
        
        Args:
            keyword_result: detect_keywords_in_text的返回结果
            
        Returns:
            标签字符串
        """
        if not keyword_result['is_important']:
            return ""
        
        tags = []
        
        # 通用关键词标签
        for category, keywords in keyword_result['common'].items():
            tags.append(f"{category}:{','.join(keywords[:2])}")
        
        # 项目关键词标签
        if keyword_result['project']:
            tags.append(f"项目:{','.join(keyword_result['project'][:2])}")
        
        if tags:
            return " [" + " | ".join(tags) + "]"
        return ""
    
    def _get_category_name(self, category):
        """获取分类显示名称"""
        name_map = {
            'hardware': '硬件',
            'software': '软件',
            'network': '网络',
            'performance': '性能',
            'quality': '质量',
            'bug': 'Bug',
            'feature': '功能'
        }
        return name_map.get(category, category)
    
    def has_keywords(self):
        """检查是否有关键词配置"""
        return len(self.common_keywords) > 0 or len(self.project_keywords) > 0

