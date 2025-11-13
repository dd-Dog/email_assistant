"""
项目文档加载器 - V5.1
支持从文件夹加载多种格式的项目文档
"""
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ProjectDocLoader:
    """项目文档加载器"""
    
    SUPPORTED_FORMATS = ['.txt', '.md', '.markdown']
    
    def __init__(self, projects_root='projects'):
        """初始化项目文档加载器
        
        Args:
            projects_root: 项目文件夹根目录
        """
        self.projects_root = projects_root
        self.projects_data = {}
        self._load_all_projects()
    
    def _load_all_projects(self):
        """加载所有项目文档"""
        if not os.path.exists(self.projects_root):
            logger.warning(f"项目文档目录不存在: {self.projects_root}")
            return
        
        project_count = 0
        for project_name in os.listdir(self.projects_root):
            project_path = os.path.join(self.projects_root, project_name)
            if os.path.isdir(project_path):
                project_data = self._load_project_folder(project_name, project_path)
                if project_data:
                    self.projects_data[project_name] = project_data
                    project_count += 1
        
        if project_count > 0:
            logger.info(f"✅ 加载了 {project_count} 个项目的文档")
        else:
            logger.info("ℹ️  未找到项目文档")
    
    def _load_project_folder(self, project_name, project_path):
        """加载单个项目文件夹
        
        Args:
            project_name: 项目名称
            project_path: 项目文件夹路径
            
        Returns:
            项目数据字典
        """
        project_data = {
            'name': project_name,
            'path': project_path,
            'documents': {},
            'full_content': '',
            'summary': ''
        }
        
        doc_count = 0
        full_content_parts = []
        
        # 遍历文件夹中的所有文件
        for filename in os.listdir(project_path):
            file_path = os.path.join(project_path, filename)
            
            # 跳过目录
            if os.path.isdir(file_path):
                continue
            
            # 检查文件格式
            ext = os.path.splitext(filename)[1].lower()
            if ext not in self.SUPPORTED_FORMATS:
                continue
            
            # 加载文件内容
            content = self._load_file_content(file_path)
            if content:
                project_data['documents'][filename] = {
                    'path': file_path,
                    'content': content,
                    'size': len(content)
                }
                full_content_parts.append(f"\n=== {filename} ===\n")
                full_content_parts.append(content)
                doc_count += 1
        
        if doc_count > 0:
            project_data['full_content'] = '\n'.join(full_content_parts)
            project_data['summary'] = self._generate_summary(project_data)
            logger.info(f"  📁 {project_name}: {doc_count} 个文档")
            return project_data
        
        return None
    
    def _load_file_content(self, file_path):
        """加载文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容字符串
        """
        try:
            # 尝试UTF-8编码
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # 尝试GBK编码
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"读取文件失败 {file_path}: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {str(e)}")
            return None
    
    def _generate_summary(self, project_data):
        """生成项目摘要
        
        Args:
            project_data: 项目数据
            
        Returns:
            摘要字符串
        """
        parts = []
        parts.append(f"项目: {project_data['name']}")
        parts.append(f"文档数: {len(project_data['documents'])}")
        
        # 列出文档名称
        doc_names = list(project_data['documents'].keys())
        parts.append(f"文档: {', '.join(doc_names)}")
        
        return '\n'.join(parts)
    
    def get_project_info(self, project_code):
        """获取项目信息
        
        Args:
            project_code: 项目代码
            
        Returns:
            项目信息字典
        """
        return self.projects_data.get(project_code)
    
    def get_project_content(self, project_code, max_length=5000):
        """获取项目内容（用于AI分析）
        
        Args:
            project_code: 项目代码
            max_length: 最大长度
            
        Returns:
            项目内容字符串（截断）
        """
        project = self.get_project_info(project_code)
        if not project:
            return ""
        
        content = project['full_content']
        if len(content) > max_length:
            content = content[:max_length] + "\n\n... (内容过长，已截断)"
        
        return content
    
    def get_project_documents(self, project_code):
        """获取项目文档列表
        
        Args:
            project_code: 项目代码
            
        Returns:
            文档字典
        """
        project = self.get_project_info(project_code)
        if not project:
            return {}
        return project['documents']
    
    def search_in_project(self, project_code, keyword):
        """在项目文档中搜索关键词
        
        Args:
            project_code: 项目代码
            keyword: 关键词
            
        Returns:
            包含关键词的文档列表
        """
        project = self.get_project_info(project_code)
        if not project:
            return []
        
        results = []
        for doc_name, doc_data in project['documents'].items():
            if keyword.lower() in doc_data['content'].lower():
                results.append(doc_name)
        
        return results
    
    def has_projects(self):
        """检查是否有项目"""
        return len(self.projects_data) > 0
    
    def get_all_project_codes(self):
        """获取所有项目代码"""
        return list(self.projects_data.keys())

