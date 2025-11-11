"""
AI分析缓存模块 - 节省成本
缓存已分析的邮件，避免重复调用API
"""
import json
import os
import hashlib
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AICache:
    """AI分析结果缓存"""
    
    def __init__(self, cache_dir='ai_cache', cache_days=7):
        """初始化缓存
        
        Args:
            cache_dir: 缓存目录
            cache_days: 缓存保留天数
        """
        self.cache_dir = cache_dir
        self.cache_days = cache_days
        self.cache_file = os.path.join(cache_dir, 'analysis_cache.json')
        self.cache_data = {}
        
        # 创建缓存目录
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            logger.info(f"创建缓存目录: {cache_dir}")
        
        # 加载缓存
        self._load_cache()
        
        # 清理过期缓存
        self._clean_expired()
    
    def _generate_key(self, email_id, subject, body):
        """生成邮件的缓存key
        
        使用邮件ID + 内容hash确保唯一性
        """
        content = f"{email_id}_{subject}_{body[:200]}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _load_cache(self):
        """加载缓存数据"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache_data = json.load(f)
                logger.info(f"缓存加载成功: {len(self.cache_data)} 条")
            else:
                self.cache_data = {}
                logger.info("缓存文件不存在，创建新缓存")
        except Exception as e:
            logger.error(f"加载缓存失败: {str(e)}")
            self.cache_data = {}
    
    def _save_cache(self):
        """保存缓存数据"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
            logger.debug("缓存已保存")
        except Exception as e:
            logger.error(f"保存缓存失败: {str(e)}")
    
    def _clean_expired(self):
        """清理过期的缓存"""
        try:
            now = datetime.now()
            expired_keys = []
            
            for key, value in self.cache_data.items():
                cached_time = datetime.fromisoformat(value.get('cached_at', '2000-01-01'))
                if (now - cached_time).days > self.cache_days:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache_data[key]
            
            if expired_keys:
                logger.info(f"清理了 {len(expired_keys)} 条过期缓存")
                self._save_cache()
                
        except Exception as e:
            logger.error(f"清理缓存失败: {str(e)}")
    
    def get(self, email_id, subject, body):
        """获取缓存的分析结果
        
        Returns:
            缓存的分析结果，如果不存在返回None
        """
        key = self._generate_key(email_id, subject, body)
        
        if key in self.cache_data:
            logger.debug(f"缓存命中: {email_id}")
            return self.cache_data[key].get('analysis')
        
        return None
    
    def set(self, email_id, subject, body, analysis):
        """保存分析结果到缓存"""
        key = self._generate_key(email_id, subject, body)
        
        self.cache_data[key] = {
            'email_id': email_id,
            'subject': subject[:100],
            'analysis': analysis,
            'cached_at': datetime.now().isoformat()
        }
        
        self._save_cache()
        logger.debug(f"缓存已保存: {email_id}")
    
    def get_stats(self):
        """获取缓存统计信息"""
        return {
            'total': len(self.cache_data),
            'cache_file': self.cache_file
        }

