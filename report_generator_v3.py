from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ReportGeneratorV3:
    """报告生成器V3.0 - 按天汇总"""
    
    def __init__(self):
        pass
    
    def format_date_only(self, date):
        """只格式化日期（不含时间）"""
        return date.strftime("%Y-%m-%d")
    
    def format_time_only(self, date):
        """只格式化时间"""
        return date.strftime("%H:%M")
    
    def group_emails_by_sender_and_day(self, emails):
        """将邮件按发件人和日期分组
        
        Returns:
            {sender_email: {date: [emails]}}
        """
        grouped = defaultdict(lambda: defaultdict(list))
        
        for email_item in emails:
            sender = email_item['from_email']
            date_key = email_item['date'].date()
            grouped[sender][date_key].append(email_item)
        
        # 按日期排序每个发件人的邮件
        for sender in grouped:
            for date_key in grouped[sender]:
                grouped[sender][date_key].sort(key=lambda x: x['date'])
        
        return dict(grouped)
    
    def generate_html_report(self, summary):
        """生成HTML格式的报告（V3.0）"""
        logger.info("正在生成HTML报告 V3.0...")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }}
        .summary-box {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .alert {{
            background-color: #ffe6e6;
            border-left: 5px solid #e74c3c;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .alert-title {{
            font-weight: bold;
            color: #c0392b;
            font-size: 18px;
            margin-bottom: 10px;
        }}
        .person-group {{
            background-color: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border: 2px solid #dee2e6;
        }}
        .person-header {{
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }}
        .leader-group {{
            border-color: #e74c3c;
        }}
        .leader-header {{
            border-bottom-color: #e74c3c;
        }}
        .day-section {{
            background-color: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #95a5a6;
        }}
        .day-header {{
            font-size: 16px;
            font-weight: bold;
            color: #2980b9;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid #ecf0f1;
        }}
        .email-content {{
            padding: 10px;
            margin: 8px 0;
            background-color: #f8f9fa;
            border-radius: 3px;
            border-left: 2px solid #bdc3c7;
        }}
        .email-time {{
            color: #7f8c8d;
            font-size: 13px;
            margin-bottom: 5px;
        }}
        .email-subject {{
            font-weight: bold;
            color: #34495e;
            margin-bottom: 5px;
        }}
        .email-body {{
            color: #2c3e50;
            line-height: 1.6;
            white-space: pre-wrap;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .badge-danger {{
            background-color: #e74c3c;
            color: white;
        }}
        .badge-info {{
            background-color: #3498db;
            color: white;
        }}
        .badge-warning {{
            background-color: #f39c12;
            color: white;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📧 邮件助手每日报告 V3.0</h1>
        <div class="summary-box">
            <p><strong>生成时间：</strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>邮件总数：</strong>{summary['total_emails']} 封 
               （领导 {summary['leader_count']} 封 + 员工 {summary['employee_count']} 封）</p>
            <p><strong>重复问题数：</strong>{len(summary['repeat_issues'])} 个</p>
        </div>
"""
        
        # 重复问题（重点）
        if summary['repeat_issues']:
            html += """
        <h2>🚨 连续3天未解决的问题（重点关注）</h2>
        <p style="color: #e74c3c; font-weight: bold;">以下问题连续3天出现，需要重点关注！</p>
"""
            for idx, issue in enumerate(summary['repeat_issues'], 1):
                first_email = issue['emails'][0]
                sender_display = f"{first_email['from_name']}({first_email['from_email']})"
                html += f"""
        <div class="alert">
            <div class="alert-title">
                问题 #{idx}: {first_email['subject']}
                <span class="badge badge-danger">连续 {issue['consecutive_days']} 天</span>
                <span class="badge badge-info">{issue['count']} 封邮件</span>
            </div>
            <p><strong>发件人：</strong>{sender_display}</p>
            <p><strong>时间范围：</strong>{self.format_date_only(issue['first_date'])} 至 {self.format_date_only(issue['last_date'])}</p>
            <div style="margin-top: 10px;">
"""
                for email_item in issue['emails'][:3]:  # 显示最近3封
                    html += f"""
                <div class="email-content">
                    <div class="email-time">{self.format_date_only(email_item['date'])} {self.format_time_only(email_item['date'])}</div>
                    <div class="email-body">{email_item['body'][:400]}</div>
                </div>
"""
                html += """
            </div>
        </div>
"""
        else:
            html += """
        <h2>✅ 重复问题</h2>
        <p style="color: #27ae60;">暂无发现连续3天的重复问题。</p>
"""
        
        # 领导邮件（按人和天汇总）
        if summary.get('leader_emails_by_day'):
            html += f"""
        <h2>👔 领导邮件汇总（共 {summary['leader_count']} 封）</h2>
        <p style="color: #7f8c8d;">按人员和日期汇总最近3天的邮件内容</p>
"""
            for sender_email, days_data in summary['leader_emails_by_day'].items():
                sender_name = summary['leaders'][sender_email]['name']
                sender_display = f"{sender_name}({sender_email})"
                total_count = sum(len(emails) for emails in days_data.values())
                
                html += f"""
        <div class="person-group leader-group">
            <div class="person-header leader-header">
                {sender_display} <span class="badge badge-danger">{total_count} 封</span>
            </div>
"""
                # 按日期排序
                sorted_dates = sorted(days_data.keys(), reverse=True)
                for date_key in sorted_dates:
                    day_emails = days_data[date_key]
                    html += f"""
            <div class="day-section">
                <div class="day-header">📅 {self.format_date_only(date_key)} <span class="badge badge-info">{len(day_emails)} 封</span></div>
"""
                    for email_item in day_emails:
                        html += f"""
                <div class="email-content">
                    <div class="email-time">{self.format_time_only(email_item['date'])}</div>
                    <div class="email-subject">主题: {email_item['subject']}</div>
                    <div class="email-body">{email_item['body']}</div>
                </div>
"""
                    html += """
            </div>
"""
                html += """
        </div>
"""
        
        # 员工邮件（按人和天汇总，排除重复问题）
        if summary.get('employee_emails_by_day'):
            # 获取重复问题中的邮件ID
            repeat_email_ids = set()
            for issue in summary['repeat_issues']:
                for email_item in issue['emails']:
                    repeat_email_ids.add(email_item['id'])
            
            html += f"""
        <h2>👥 员工邮件汇总（共 {summary['employee_count']} 封）</h2>
        <p style="color: #7f8c8d;">按人员和日期汇总最近3天的邮件内容（重复问题已在上方单独显示）</p>
"""
            for sender_email, days_data in summary['employee_emails_by_day'].items():
                sender_name = summary['employees'][sender_email]['name']
                sender_display = f"{sender_name}({sender_email})"
                
                # 过滤重复问题邮件
                filtered_days = {}
                for date_key, emails in days_data.items():
                    filtered_emails = [e for e in emails if e['id'] not in repeat_email_ids]
                    if filtered_emails:
                        filtered_days[date_key] = filtered_emails
                
                if not filtered_days:
                    continue
                
                total_count = sum(len(emails) for emails in filtered_days.values())
                
                html += f"""
        <div class="person-group">
            <div class="person-header">
                {sender_display} <span class="badge badge-info">{total_count} 封</span>
            </div>
"""
                # 按日期排序
                sorted_dates = sorted(filtered_days.keys(), reverse=True)
                for date_key in sorted_dates:
                    day_emails = filtered_days[date_key]
                    html += f"""
            <div class="day-section">
                <div class="day-header">📅 {self.format_date_only(date_key)} <span class="badge badge-info">{len(day_emails)} 封</span></div>
"""
                    for email_item in day_emails:
                        html += f"""
                <div class="email-content">
                    <div class="email-time">{self.format_time_only(email_item['date'])}</div>
                    <div class="email-subject">主题: {email_item['subject']}</div>
                    <div class="email-body">{email_item['body']}</div>
                </div>
"""
                    html += """
            </div>
"""
                html += """
        </div>
"""
        
        html += """
        <div class="footer">
            <p>本报告由邮件助手自动生成 - V3.0（按天汇总）</p>
        </div>
    </div>
</body>
</html>
"""
        
        logger.info("HTML报告生成完成")
        return html

