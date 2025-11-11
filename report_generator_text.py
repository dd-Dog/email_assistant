"""
纯文本报告生成器 - V3.0 紧凑版
简洁、清晰、易读的纯文本格式，减少空行
"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TextReportGenerator:
    """纯文本报告生成器（紧凑版）"""
    
    def __init__(self):
        pass
    
    def format_date_only(self, date):
        """只格式化日期（不含时间）"""
        return date.strftime("%Y-%m-%d")
    
    def format_time_only(self, date):
        """只格式化时间"""
        return date.strftime("%H:%M")
    
    def generate_text_report(self, summary):
        """生成纯文本格式的报告（紧凑版）"""
        logger.info("正在生成紧凑版纯文本报告...")
        
        lines = []
        lines.append("=" * 70)
        lines.append("📧 邮件助手每日报告 V3.0")
        lines.append("=" * 70)
        
        # 概览统计 - 紧凑显示
        # 添加精确到秒的时间戳，确保每次报告都不同
        now = datetime.now()
        lines.append(f"生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')} (ID:{now.strftime('%Y%m%d%H%M%S')})")
        lines.append(f"邮件总数: {summary['total_emails']} 封 | " +
                    f"领导: {summary['leader_count']} | " +
                    f"项目经理: {summary['pm_count']} | " +
                    f"员工: {summary['employee_count']}")
        if summary['repeat_issues']:
            lines.append(f"⚠️  重复问题: {len(summary['repeat_issues'])} 个")
        lines.append("")
        
        # 重复问题（最优先）
        if summary['repeat_issues']:
            lines.append("=" * 70)
            lines.append("🚨 连续3天未解决的问题（重点关注）")
            lines.append("=" * 70)
            
            for idx, issue in enumerate(summary['repeat_issues'], 1):
                first_email = issue['emails'][0]
                sender_display = f"{first_email['from_name']}({first_email['from_email']})"
                
                lines.append(f"[问题{idx}] {first_email['subject']}")
                lines.append(f"  发件人: {sender_display} | 连续{issue['consecutive_days']}天 | 共{issue['count']}封")
                lines.append(f"  时间: {self.format_date_only(issue['first_date'])} ~ {self.format_date_only(issue['last_date'])}")
                
                # 显示最近邮件内容
                for i, email_item in enumerate(issue['emails'][:2], 1):  # 只显示2封
                    content = email_item['body'].strip()[:200]  # 限制200字符
                    if content:
                        lines.append(f"  [{self.format_date_only(email_item['date'])}] {content}")
                
                if idx < len(summary['repeat_issues']):  # 不是最后一个才加分隔线
                    lines.append("  " + "-" * 66)
            lines.append("")
        
        # 辅助函数：生成人员邮件部分
        def add_person_emails(person_data, config_data, title, emoji):
            """添加某类人员的邮件"""
            if not person_data:
                return
            
            lines.append("=" * 70)
            lines.append(f"{emoji} {title}")
            lines.append("=" * 70)
            
            person_count = 0
            for sender_email, days_data in person_data.items():
                sender_name = config_data.get(sender_email, {}).get('name', sender_email)
                total_count = sum(len(emails) for emails in days_data.values())
                
                if total_count == 0:
                    continue
                
                person_count += 1
                lines.append(f"[{sender_name}]({sender_email}) {total_count}封")
                
                # 按日期排序
                sorted_dates = sorted(days_data.keys(), reverse=True)
                for date_key in sorted_dates:
                    day_emails = days_data[date_key]
                    lines.append(f"  {self.format_date_only(date_key)}:")
                    
                    for email_item in day_emails:
                        time_str = self.format_time_only(email_item['date'])
                        subject = email_item['subject'][:40]  # 限制主题长度
                        lines.append(f"    {time_str} {subject}")
                        
                        # 内容紧凑显示
                        content = email_item['body'].strip()
                        if content:
                            # 只显示前150字符，分行显示
                            content_lines = []
                            for line in content.split('\n')[:3]:  # 最多3行
                                if line.strip():
                                    content_lines.append(line.strip()[:60])
                            if content_lines:
                                lines.append(f"      {' | '.join(content_lines)}")
            
            # 如果这部分有内容才加空行
            if person_count > 0:
                lines.append("")
        
        # 领导邮件
        if summary.get('leader_emails_by_day'):
            add_person_emails(summary['leader_emails_by_day'], 
                            summary.get('leaders', {}),
                            f"领导邮件汇总 ({summary['leader_count']}封)", 
                            "👔")
        
        # 项目经理邮件
        if summary.get('pm_emails_by_day'):
            # 过滤掉重复问题
            repeat_email_ids = set()
            for issue in summary['repeat_issues']:
                for email_item in issue['emails']:
                    repeat_email_ids.add(email_item['id'])
            
            filtered_pm_data = {}
            for sender_email, days_data in summary['pm_emails_by_day'].items():
                filtered_days = {}
                for date_key, emails in days_data.items():
                    filtered_emails = [e for e in emails if e['id'] not in repeat_email_ids]
                    if filtered_emails:
                        filtered_days[date_key] = filtered_emails
                if filtered_days:
                    filtered_pm_data[sender_email] = filtered_days
            
            if filtered_pm_data:
                # 计算过滤后的数量
                pm_count_filtered = sum(len(e) for days in filtered_pm_data.values() 
                                       for e in days.values())
                add_person_emails(filtered_pm_data,
                                summary.get('project_managers', {}),
                                f"项目经理邮件汇总 ({pm_count_filtered}封)",
                                "📋")
        
        # 员工邮件（排除重复问题）
        if summary.get('employee_emails_by_day'):
            # 过滤重复问题
            repeat_email_ids = set()
            for issue in summary['repeat_issues']:
                for email_item in issue['emails']:
                    repeat_email_ids.add(email_item['id'])
            
            filtered_emp_data = {}
            for sender_email, days_data in summary['employee_emails_by_day'].items():
                filtered_days = {}
                for date_key, emails in days_data.items():
                    filtered_emails = [e for e in emails if e['id'] not in repeat_email_ids]
                    if filtered_emails:
                        filtered_days[date_key] = filtered_emails
                if filtered_days:
                    filtered_emp_data[sender_email] = filtered_days
            
            if filtered_emp_data:
                emp_count_filtered = sum(len(e) for days in filtered_emp_data.values() 
                                        for e in days.values())
                add_person_emails(filtered_emp_data,
                                summary.get('employees', {}),
                                f"员工邮件汇总 ({emp_count_filtered}封)",
                                "👥")
        
        # 页脚（添加唯一标识）
        lines.append("=" * 70)
        report_id = datetime.now().strftime('%Y%m%d%H%M%S')
        lines.append(f"本报告由邮件助手自动生成 - V3.0 | 报告编号: {report_id}")
        lines.append("=" * 70)
        
        report = '\n'.join(lines)
        logger.info("紧凑版纯文本报告生成完成")
        return report
