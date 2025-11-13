"""
AI增强的报告生成器 - V5.0
在原有报告基础上，添加AI分析结果和项目关联
"""
from datetime import datetime
import logging
from context_builder import ContextBuilder

logger = logging.getLogger(__name__)


class AIReportGenerator:
    """AI增强的报告生成器（V5.0：支持项目关联）"""
    
    def __init__(self):
        self.context_builder = ContextBuilder()  # V5.0：上下文构建器
    
    def format_date_only(self, date):
        """只格式化日期（不含时间）"""
        return date.strftime("%Y-%m-%d")
    
    def format_time_only(self, date):
        """只格式化时间"""
        return date.strftime("%H:%M")
    
    def get_priority_emoji(self, priority):
        """获取优先级emoji"""
        priority_map = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        return priority_map.get(priority, '⚪')
    
    def get_urgency_text(self, urgency):
        """获取紧急程度文本"""
        urgency_map = {
            'urgent': '紧急',
            'normal': '普通',
            'low': '不急'
        }
        return urgency_map.get(urgency, '普通')
    
    def generate_text_report(self, summary, ai_enabled=False):
        """生成AI增强的纯文本报告
        
        Args:
            summary: 邮件摘要数据
            ai_enabled: 是否启用了AI分析
        """
        logger.info("正在生成AI增强的报告...")
        
        lines = []
        lines.append("=" * 70)
        title = "📧 AI邮件助手每日报告 V5.0" if ai_enabled else "📧 邮件助手每日报告 V3.0"
        lines.append(title)
        lines.append("=" * 70)
        
        # 概览统计
        now = datetime.now()
        lines.append(f"生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')} (ID:{now.strftime('%Y%m%d%H%M%S')})")
        lines.append(f"邮件总数: {summary['total_emails']} 封 | " +
                    f"领导: {summary['leader_count']} | " +
                    f"项目经理: {summary['pm_count']} | " +
                    f"员工: {summary['employee_count']} | " +
                    f"客户: {summary['customer_count']} | " +
                    f"供应商: {summary['supplier_count']}")
        if summary['repeat_issues']:
            lines.append(f"⚠️  重复问题: {len(summary['repeat_issues'])} 个")
        if ai_enabled:
            lines.append("🤖 AI分析已启用")
        lines.append("")
        
        # AI识别的高优先级邮件（V4.0新增）
        high_priority_email_ids = set()  # 记录高优先级邮件ID，避免重复显示
        
        if ai_enabled:
            high_priority_emails = []
            for email_list in [summary.get('leader_emails_by_day', {}).values(),
                             summary.get('pm_emails_by_day', {}).values(),
                             summary.get('employee_emails_by_day', {}).values()]:
                for days_data in email_list:
                    for emails in days_data.values():
                        for email_item in emails:
                            ai_analysis = email_item.get('ai_analysis')
                            if ai_analysis and ai_analysis.get('priority') == 'high':
                                high_priority_emails.append(email_item)
                                high_priority_email_ids.add(email_item['id'])
            
            if high_priority_emails:
                lines.append("")
                lines.append("█ 🔴 高优先级邮件（需立即处理）")
                lines.append("")
                
                for email_item in high_priority_emails[:5]:  # 最多显示5封
                    ai = email_item['ai_analysis']
                    sender_display = f"{email_item['from_name']}({email_item['from_email']})"
                    
                    # 紧凑格式：一行显示多个信息
                    time_info = f"{self.format_date_only(email_item['date'])} {self.format_time_only(email_item['date'])}"
                    priority_info = f"{self.get_priority_emoji(ai.get('priority'))}高优先"
                    urgency_info = f"⏰{self.get_urgency_text(ai.get('urgency'))}"
                    
                    lines.append(f"▸ [{sender_display}] {email_item['subject']}")
                    lines.append(f"  {time_info} | {priority_info} | {urgency_info}")
                    
                    if ai.get('summary'):
                        lines.append(f"  💡 {ai['summary']}")
                    
                    if ai.get('action_items'):
                        for action in ai['action_items'][:3]:
                            lines.append(f"  ✓ {action}")
                    
                    if ai.get('deadline'):
                        lines.append(f"  📅 {ai['deadline']}")
                lines.append("")
        
        # 重复问题（保持原有逻辑）
        if summary['repeat_issues']:
            lines.append("")
            lines.append("█ 🚨 连续3天未解决的问题")
            lines.append("")
            
            for idx, issue in enumerate(summary['repeat_issues'], 1):
                first_email = issue['emails'][0]
                sender_display = f"{first_email['from_name']}({first_email['from_email']})"
                
                lines.append(f"[问题{idx}] {first_email['subject']}")
                lines.append(f"  发件人: {sender_display} | 连续{issue['consecutive_days']}天 | 共{issue['count']}封")
                lines.append(f"  时间: {self.format_date_only(issue['first_date'])} ~ {self.format_date_only(issue['last_date'])}")
                
                # 如果有AI分析，显示AI建议
                if ai_enabled and first_email.get('ai_analysis'):
                    ai = first_email['ai_analysis']
                    if ai.get('summary'):
                        lines.append(f"  AI分析: {ai['summary']}")
                
                # 显示最近邮件内容
                for email_item in issue['emails'][:2]:
                    content = email_item['body'].strip()[:200]
                    if content:
                        lines.append(f"  [{self.format_date_only(email_item['date'])}] {content}")
                
                if idx < len(summary['repeat_issues']):
                    lines.append("  " + "-" * 66)
            lines.append("")
        
        # 辅助函数：生成人员邮件部分（带AI分析，排除高优先级）
        def add_person_emails_with_ai(person_data, config_data, title, emoji):
            """添加某类人员的邮件（带AI分析，排除高优先级重复显示）"""
            if not person_data:
                return
            
            lines.append("")
            lines.append(f"█ {emoji} {title}")  # 醒目标题，无分隔线
            lines.append("")
            
            for sender_email, days_data in person_data.items():
                sender_name = config_data.get(sender_email, {}).get('name', sender_email)
                total_count = sum(len(emails) for emails in days_data.values())
                
                if total_count == 0:
                    continue
                
                lines.append(f"▸ 【{sender_name}】({sender_email}) - {total_count}封")
                
                # 按日期排序，日期和邮件内容紧凑显示
                sorted_dates = sorted(days_data.keys(), reverse=True)
                for date_key in sorted_dates:
                    day_emails = days_data[date_key]
                    date_str = self.format_date_only(date_key)
                    
                    for email_item in day_emails:
                        # 如果是高优先级邮件且已在前面显示，则跳过
                        if ai_enabled and email_item['id'] in high_priority_email_ids:
                            continue
                        
                        time_str = self.format_time_only(email_item['date'])
                        subject = email_item['subject'][:45]
                        
                        # 超紧凑格式：日期+时间+主题+标签一行显示
                        if ai_enabled and email_item.get('ai_analysis'):
                            ai = email_item['ai_analysis']
                            priority_emoji = self.get_priority_emoji(ai.get('priority'))
                            urgency = self.get_urgency_text(ai.get('urgency'))
                            lines.append(f"  {date_str} {time_str} {subject} [{priority_emoji}{urgency}]")
                            
                            # AI摘要（紧凑）
                            if ai.get('summary'):
                                summary_text = ai['summary'][:100]
                                lines.append(f"    💡 {summary_text}")
                            
                            # 行动项（一行显示，用|分隔）
                            if ai.get('action_items'):
                                actions = " | ".join(ai['action_items'][:2])
                                if actions:
                                    lines.append(f"    ✓ {actions[:80]}")
                        else:
                            lines.append(f"  {date_str} {time_str} {subject}")
                            # 原始内容（紧凑显示）
                            content = email_item['body'].strip()
                            if content:
                                content_lines = []
                                for line in content.split('\n')[:2]:
                                    if line.strip():
                                        content_lines.append(line.strip()[:60])
                                if content_lines:
                                    lines.append(f"    {' | '.join(content_lines)}")
            
            lines.append("")
        
        # 客户需求邮件（优先显示，V4.0新增）
        if summary.get('customer_emails_by_day'):
            filtered_customer_data = {}
            for sender_email, days_data in summary['customer_emails_by_day'].items():
                filtered_days = {}
                for date_key, emails in days_data.items():
                    filtered_emails = [e for e in emails if e['id'] not in high_priority_email_ids]
                    if filtered_emails:
                        filtered_days[date_key] = filtered_emails
                if filtered_days:
                    filtered_customer_data[sender_email] = filtered_days
            
            if filtered_customer_data:
                customer_count_filtered = sum(len(e) for days in filtered_customer_data.values() for e in days.values())
                
                lines.append("")
                lines.append(f"█ 🏢 客户需求邮件 ({customer_count_filtered}封) - AI需求分析")
                lines.append("")
                
                for sender_email, days_data in filtered_customer_data.items():
                    sender_name = summary.get('customers', {}).get(sender_email, {}).get('name', sender_email)
                    total_count = sum(len(emails) for emails in days_data.values())
                    lines.append(f"▸ 【{sender_name}】({sender_email}) - {total_count}封")
                    
                    sorted_dates = sorted(days_data.keys(), reverse=True)
                    for date_key in sorted_dates:
                        day_emails = days_data[date_key]
                        date_str = self.format_date_only(date_key)
                        
                        for email_item in day_emails:
                            if email_item['id'] in high_priority_email_ids:
                                continue
                            
                            time_str = self.format_time_only(email_item['date'])
                            subject = email_item['subject'][:45]
                            
                            if ai_enabled and email_item.get('ai_analysis'):
                                ai = email_item['ai_analysis']
                                priority_emoji = self.get_priority_emoji(ai.get('priority'))
                                urgency = self.get_urgency_text(ai.get('urgency'))
                                
                                # V5.0：显示项目标签
                                project_tag = ""
                                if ai.get('detected_projects'):
                                    projects_str = ','.join(ai['detected_projects'])
                                    project_tag = f" [项目:{projects_str}]"
                                
                                lines.append(f"  {date_str} {time_str} {subject} [{priority_emoji}{urgency}]{project_tag}")
                                
                                # V5.0：显示项目信息
                                if ai.get('detected_projects'):
                                    for proj_code in ai['detected_projects']:
                                        proj_brief = self.context_builder.get_project_brief_for_display(proj_code)
                                        lines.append(f"    📋 {proj_brief}")
                                
                                # 客户邮件特殊显示：需求分析
                                if ai.get('summary'):
                                    lines.append(f"    📝 需求: {ai['summary']}")
                                
                                if ai.get('feasibility'):
                                    lines.append(f"    ⚙️  可行性: {ai['feasibility']}")
                                
                                if ai.get('implementation'):
                                    impl = ai['implementation']
                                    if isinstance(impl, list):
                                        impl_text = " | ".join(impl[:3])
                                    else:
                                        impl_text = impl[:100]
                                    lines.append(f"    🔧 实现: {impl_text}")
                                
                                if ai.get('suggestions'):
                                    lines.append(f"    💡 建议: {ai['suggestions']}")
                                
                                if ai.get('action_items'):
                                    actions = " | ".join(ai['action_items'][:2])
                                    if actions:
                                        lines.append(f"    ✓ {actions[:80]}")
                            else:
                                lines.append(f"  {date_str} {time_str} {subject}")
                                content = email_item['body'].strip()
                                if content:
                                    content_lines = [line.strip()[:60] for line in content.split('\n')[:2] if line.strip()]
                                    if content_lines:
                                        lines.append(f"    {' | '.join(content_lines)}")
                
                lines.append("")
        
        # 供应商邮件（V4.0新增）
        if summary.get('supplier_emails_by_day'):
            filtered_supplier_data = {}
            for sender_email, days_data in summary['supplier_emails_by_day'].items():
                filtered_days = {}
                for date_key, emails in days_data.items():
                    filtered_emails = [e for e in emails if e['id'] not in high_priority_email_ids]
                    if filtered_emails:
                        filtered_days[date_key] = filtered_emails
                if filtered_days:
                    filtered_supplier_data[sender_email] = filtered_days
            
            if filtered_supplier_data:
                supplier_count_filtered = sum(len(e) for days in filtered_supplier_data.values() for e in days.values())
                add_person_emails_with_ai(filtered_supplier_data,
                                        summary.get('suppliers', {}),
                                        f"供应商邮件汇总 ({supplier_count_filtered}封)",
                                        "🔌")
        
        # 领导邮件（排除已在高优先级显示的）
        if summary.get('leader_emails_by_day'):
            # 过滤掉高优先级邮件
            filtered_leader_data = {}
            for sender_email, days_data in summary['leader_emails_by_day'].items():
                filtered_days = {}
                for date_key, emails in days_data.items():
                    filtered_emails = [e for e in emails if e['id'] not in high_priority_email_ids]
                    if filtered_emails:
                        filtered_days[date_key] = filtered_emails
                if filtered_days:
                    filtered_leader_data[sender_email] = filtered_days
            
            if filtered_leader_data:
                leader_count_filtered = sum(len(e) for days in filtered_leader_data.values() for e in days.values())
                add_person_emails_with_ai(filtered_leader_data,
                                        summary.get('leaders', {}),
                                        f"领导邮件汇总 ({leader_count_filtered}封)",
                                        "👔")
        
        # 项目经理邮件（排除重复问题和高优先级）
        if summary.get('pm_emails_by_day'):
            repeat_email_ids = set()
            for issue in summary['repeat_issues']:
                for email_item in issue['emails']:
                    repeat_email_ids.add(email_item['id'])
            
            # 合并高优先级和重复问题的ID
            excluded_ids = repeat_email_ids | high_priority_email_ids
            
            filtered_pm_data = {}
            for sender_email, days_data in summary['pm_emails_by_day'].items():
                filtered_days = {}
                for date_key, emails in days_data.items():
                    filtered_emails = [e for e in emails if e['id'] not in excluded_ids]
                    if filtered_emails:
                        filtered_days[date_key] = filtered_emails
                if filtered_days:
                    filtered_pm_data[sender_email] = filtered_days
            
            if filtered_pm_data:
                pm_count = sum(len(e) for days in filtered_pm_data.values() for e in days.values())
                add_person_emails_with_ai(filtered_pm_data,
                                        summary.get('project_managers', {}),
                                        f"项目经理邮件汇总 ({pm_count}封)",
                                        "📋")
        
        # 员工邮件（排除重复问题和高优先级）
        if summary.get('employee_emails_by_day'):
            repeat_email_ids = set()
            for issue in summary['repeat_issues']:
                for email_item in issue['emails']:
                    repeat_email_ids.add(email_item['id'])
            
            # 合并高优先级和重复问题的ID
            excluded_ids = repeat_email_ids | high_priority_email_ids
            
            filtered_emp_data = {}
            for sender_email, days_data in summary['employee_emails_by_day'].items():
                filtered_days = {}
                for date_key, emails in days_data.items():
                    filtered_emails = [e for e in emails if e['id'] not in excluded_ids]
                    if filtered_emails:
                        filtered_days[date_key] = filtered_emails
                if filtered_days:
                    filtered_emp_data[sender_email] = filtered_days
            
            if filtered_emp_data:
                emp_count = sum(len(e) for days in filtered_emp_data.values() for e in days.values())
                add_person_emails_with_ai(filtered_emp_data,
                                        summary.get('employees', {}),
                                        f"员工邮件汇总 ({emp_count}封)",
                                        "👥")
        
        # 页脚
        lines.append("=" * 70)
        report_id = datetime.now().strftime('%Y%m%d%H%M%S')
        footer_text = "本报告由AI邮件助手自动生成 - V5.0（上下文感知）" if ai_enabled else "本报告由邮件助手自动生成 - V3.0"
        lines.append(f"{footer_text} | 报告编号: {report_id}")
        lines.append("=" * 70)
        
        report = '\n'.join(lines)
        logger.info("报告生成完成")
        return report

