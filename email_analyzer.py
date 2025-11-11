from datetime import datetime, timedelta
from collections import defaultdict
import re
import logging

logger = logging.getLogger(__name__)


class EmailAnalyzer:
    """邮件分析器，用于分析邮件内容和检测重复问题"""
    
    def __init__(self, repeat_days=3):
        self.repeat_days = repeat_days
    
    def extract_keywords(self, text):
        """从文本中提取关键词（简单实现）"""
        # 移除常见停用词
        stopwords = {'的', '了', '和', '是', '在', '我', '有', '个', '也', '就', '不', '人', '都', 
                    '一', '上', '们', '到', '说', '时', '要', '能', '可', '去', '他', '你', '会',
                    'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with'}
        
        # 简单分词（中文按字符，英文按单词）
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', text.lower())
        keywords = [w for w in words if len(w) > 1 and w not in stopwords]
        
        return keywords
    
    def calculate_similarity(self, text1, text2):
        """计算两段文本的相似度"""
        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def group_similar_emails(self, emails, similarity_threshold=0.5):
        """将相似的邮件分组"""
        groups = []
        grouped_ids = set()
        
        for i, email1 in enumerate(emails):
            if email1['id'] in grouped_ids:
                continue
            
            group = [email1]
            grouped_ids.add(email1['id'])
            
            for j, email2 in enumerate(emails[i+1:], i+1):
                if email2['id'] in grouped_ids:
                    continue
                
                # 计算主题和正文的相似度
                subject_sim = self.calculate_similarity(email1['subject'], email2['subject'])
                body_sim = self.calculate_similarity(email1['body'][:500], email2['body'][:500])
                
                # 综合相似度
                total_sim = (subject_sim * 0.6 + body_sim * 0.4)
                
                if total_sim >= similarity_threshold:
                    group.append(email2)
                    grouped_ids.add(email2['id'])
            
            groups.append(group)
        
        return groups
    
    def find_repeat_issues(self, emails):
        """查找连续多天未解决的重复问题"""
        logger.info("开始分析重复问题...")
        
        # 将邮件按相似度分组
        groups = self.group_similar_emails(emails)
        
        repeat_issues = []
        
        for group in groups:
            if len(group) < 2:
                continue
            
            # 按日期排序
            group.sort(key=lambda x: x['date'])
            
            # 检查是否连续多天出现
            dates = [email['date'].date() for email in group]
            consecutive_days = self.count_consecutive_days(dates)
            
            if consecutive_days >= self.repeat_days:
                repeat_issues.append({
                    'emails': group,
                    'consecutive_days': consecutive_days,
                    'first_date': group[0]['date'],
                    'last_date': group[-1]['date'],
                    'count': len(group)
                })
        
        # 按连续天数排序
        repeat_issues.sort(key=lambda x: x['consecutive_days'], reverse=True)
        
        logger.info(f"发现 {len(repeat_issues)} 个重复问题")
        return repeat_issues
    
    def count_consecutive_days(self, dates):
        """计算日期列表中最长的连续天数"""
        if not dates:
            return 0
        
        unique_dates = sorted(set(dates))
        
        if len(unique_dates) == 1:
            return 1
        
        max_consecutive = 1
        current_consecutive = 1
        
        for i in range(1, len(unique_dates)):
            if (unique_dates[i] - unique_dates[i-1]).days <= 1:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1
        
        return max_consecutive
    
    def group_emails_by_sender(self, emails):
        """按发件人分组邮件"""
        grouped = {}
        for email_item in emails:
            sender_key = email_item['from_email']
            sender_name = email_item['from_name']
            
            if sender_key not in grouped:
                grouped[sender_key] = {
                    'name': sender_name,
                    'email': sender_key,
                    'emails': []
                }
            grouped[sender_key]['emails'].append(email_item)
        
        # 每组内按日期排序
        for sender_key in grouped:
            grouped[sender_key]['emails'].sort(key=lambda x: x['date'], reverse=True)
        
        return grouped
    
    def group_emails_by_sender_and_day(self, emails):
        """按发件人和日期分组邮件（V3.0）"""
        from collections import defaultdict
        
        grouped = defaultdict(lambda: defaultdict(list))
        
        for email_item in emails:
            sender = email_item['from_email']
            date_key = email_item['date'].date()
            grouped[sender][date_key].append(email_item)
        
        # 按日期排序
        for sender in grouped:
            for date_key in grouped[sender]:
                grouped[sender][date_key].sort(key=lambda x: x['date'])
        
        return dict(grouped)
    
    def generate_summary(self, leaders_config, pms_config, employees_config,
                        leader_emails, pm_emails, employee_emails, employee_repeat_issues):
        """生成邮件摘要（V3.0 - 三类人员按天汇总）
        
        Args:
            leaders_config: 领导配置字典
            pms_config: 项目经理配置字典
            employees_config: 员工配置字典
            leader_emails: 领导的邮件列表
            pm_emails: 项目经理的邮件列表
            employee_emails: 员工的邮件列表
            employee_repeat_issues: 员工邮件中的重复问题
            
        Returns:
            包含分类汇总的字典
        """
        # 按发件人分组（保持兼容）
        leaders_grouped = self.group_emails_by_sender(leader_emails)
        pms_grouped = self.group_emails_by_sender(pm_emails)
        employees_grouped = self.group_emails_by_sender(employee_emails)
        
        # 按发件人和天分组（V3.0）
        leader_emails_by_day = self.group_emails_by_sender_and_day(leader_emails)
        pm_emails_by_day = self.group_emails_by_sender_and_day(pm_emails)
        employee_emails_by_day = self.group_emails_by_sender_and_day(employee_emails)
        
        summary = {
            'total_emails': len(leader_emails) + len(pm_emails) + len(employee_emails),
            'leader_count': len(leader_emails),
            'pm_count': len(pm_emails),
            'employee_count': len(employee_emails),
            'leaders': leaders_grouped,
            'project_managers': pms_grouped,
            'employees': employees_grouped,
            'repeat_issues': employee_repeat_issues,
            # V3.0：按天分组的数据
            'leader_emails_by_day': leader_emails_by_day,
            'pm_emails_by_day': pm_emails_by_day,
            'employee_emails_by_day': employee_emails_by_day
        }
        
        return summary

