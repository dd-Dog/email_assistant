"""
产品参数管理器 - V5.1
管理产品的硬件参数、软件配置等
"""
import json
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ProductParamsManager:
    """产品参数管理器"""
    
    def __init__(self, params_file='product_params.json'):
        """初始化参数管理器
        
        Args:
            params_file: 参数配置文件
        """
        self.params_file = params_file
        self.common_params = {}  # 通用参数定义
        self.product_params = {}  # 各产品的参数值
        self._load_params()
    
    def _load_params(self):
        """加载参数配置"""
        try:
            if os.path.exists(self.params_file):
                with open(self.params_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.common_params = data.get('common_params', {})
                    self.product_params = data.get('products', {})
                logger.info(f"✅ 加载了 {len(self.product_params)} 个产品参数")
            else:
                logger.info(f"ℹ️  参数配置文件不存在: {self.params_file}")
        except Exception as e:
            logger.error(f"加载参数配置失败: {str(e)}")
    
    def get_product_params(self, product_code):
        """获取产品参数
        
        Args:
            product_code: 产品代码
            
        Returns:
            参数字典
        """
        return self.product_params.get(product_code, {})
    
    def format_params_for_display(self, product_code, category=None):
        """格式化参数用于显示
        
        Args:
            product_code: 产品代码
            category: 参数分类（可选：hardware/software/network等）
            
        Returns:
            格式化的参数字符串
        """
        params = self.get_product_params(product_code)
        if not params:
            return ""
        
        lines = []
        
        # 按分类组织
        if category:
            category_params = params.get(category, {})
            lines.append(f"【{category}】")
            for key, value in category_params.items():
                param_name = self._get_param_name(key)
                lines.append(f"  {param_name}: {value}")
        else:
            # 显示所有分类
            for cat, cat_params in params.items():
                if isinstance(cat_params, dict):
                    lines.append(f"【{cat}】")
                    for key, value in cat_params.items():
                        param_name = self._get_param_name(key)
                        lines.append(f"  {param_name}: {value}")
                    lines.append("")
        
        return '\n'.join(lines)
    
    def format_params_for_ai(self, product_code, max_params=20):
        """格式化参数用于AI分析
        
        Args:
            product_code: 产品代码
            max_params: 最大参数数量
            
        Returns:
            简洁的参数字符串
        """
        params = self.get_product_params(product_code)
        if not params:
            return ""
        
        # 提取关键参数
        key_params = []
        param_count = 0
        
        for category, cat_params in params.items():
            if not isinstance(cat_params, dict):
                continue
            
            for key, value in cat_params.items():
                if param_count >= max_params:
                    break
                param_name = self._get_param_name(key)
                key_params.append(f"{param_name}: {value}")
                param_count += 1
            
            if param_count >= max_params:
                break
        
        result = " | ".join(key_params)
        if param_count >= max_params:
            total_count = sum(len(v) for v in params.values() if isinstance(v, dict))
            result += f" ... (共{total_count}项参数)"
        
        return result
    
    def _get_param_name(self, param_key):
        """获取参数的显示名称
        
        Args:
            param_key: 参数key
            
        Returns:
            显示名称
        """
        # 从通用参数定义中获取名称
        for category, definitions in self.common_params.items():
            if isinstance(definitions, dict) and param_key in definitions:
                return definitions[param_key].get('name', param_key)
        return param_key
    
    def search_param(self, product_code, keyword):
        """搜索包含关键词的参数
        
        Args:
            product_code: 产品代码
            keyword: 关键词
            
        Returns:
            匹配的参数列表
        """
        params = self.get_product_params(product_code)
        if not params:
            return []
        
        results = []
        keyword_lower = keyword.lower()
        
        for category, cat_params in params.items():
            if not isinstance(cat_params, dict):
                continue
            
            for key, value in cat_params.items():
                param_name = self._get_param_name(key)
                value_str = str(value)
                
                if (keyword_lower in param_name.lower() or 
                    keyword_lower in value_str.lower()):
                    results.append({
                        'category': category,
                        'name': param_name,
                        'value': value
                    })
        
        return results
    
    def has_params(self):
        """检查是否有参数配置"""
        return len(self.product_params) > 0

