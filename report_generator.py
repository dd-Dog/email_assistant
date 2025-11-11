from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器，生成HTML格式的邮件摘要"""
    
    def __init__(self):
        pass
    
    def truncate_text(self, text, max_length=200):
        """截断文本到指定长度"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def format_date(self, date):
        """格式化日期"""
        return date.strftime("%Y-%m-%d %H:%M")
    
    def generate_html_report(self, summary):
        """生成HTML格式的报告（V2.0）"""
        logger.info("正在生成HTML报告...")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            max-width: 1200px;
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
        h3 {{
            color: #2980b9;
            margin-top: 20px;
            margin-bottom: 10px;
            padding-left: 5px;
            border-left: 3px solid #95a5a6;
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
        .sender-group {{
            background-color: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border: 2px solid #dee2e6;
        }}
        .sender-header {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }}
        .leader-group {{
            border-color: #e74c3c;
        }}
        .leader-header {{
            color: #c0392b;
        }}
        .email-item {{
            background-color: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 3px solid #95a5a6;
        }}
        .email-subject {{
            font-weight: bold;
            color: #2980b9;
            font-size: 16px;
            margin-bottom: 5px;
        }}
        .email-meta {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        .email-body {{
            color: #34495e;
            line-height: 1.6;
            margin-top: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 3px;
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
        .badge-success {{
            background-color: #27ae60;
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
        <h1>📧 邮件助手每日报告 V2.0</h1>
        <div class="summary-box">
            <p><strong>生成时间：</strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>邮件总数：</strong>{summary['total_emails']} 封 
               （领导 {summary['leader_count']} 封 + 员工 {summary['employee_count']} 封）</p>
            <p><strong>重复问题数：</strong>{len(summary['repeat_issues'])} 个</p>
        </div>
"""
        
        # 重复问题（重点，放在最前面）
        if summary['repeat_issues']:
            html += """
        <h2>🚨 重复问题警报（重点关注）</h2>
        <p style="color: #e74c3c; font-weight: bold;">以下问题连续多天出现，需要重点关注！</p>
"""
            for idx, issue in enumerate(summary['repeat_issues'], 1):
                first_email = issue['emails'][0]
                sender_display = f"{first_email['from_name']}({first_email['from_email']})"
                html += f"""
        <div class="alert">
            <div class="alert-title">
                问题 #{idx}: {first_email['subject']}
                <span class="badge badge-danger">连续 {issue['consecutive_days']} 天</span>
                <span class="badge badge-info">共 {issue['count']} 封邮件</span>
            </div>
            <p><strong>发件人：</strong>{sender_display}</p>
            <p><strong>首次出现：</strong>{self.format_date(issue['first_date'])}</p>
            <p><strong>最后出现：</strong>{self.format_date(issue['last_date'])}</p>
            <p><strong>相关邮件：</strong></p>
"""
                for email_item in issue['emails'][:5]:  # 最多显示5封
                    html += f"""
            <div class="email-item">
                <div class="email-meta">
                    <strong>日期：</strong>{self.format_date(email_item['date'])}
                </div>
                <div class="email-body">
                    {self.truncate_text(email_item['body'], 300)}
                </div>
            </div>
"""
                if len(issue['emails']) > 5:
                    html += f"            <p style='color: #7f8c8d;'>...还有 {len(issue['emails']) - 5} 封相关邮件</p>\n"
                
                html += """
        </div>
"""
        else:
            html += """
        <h2>✅ 重复问题</h2>
        <p style="color: #27ae60;">暂无发现连续多天的重复问题。</p>
"""
        
        # 领导邮件（按人分类）
        if summary['leaders']:
            html += f"""
        <h2>👔 领导邮件（共 {summary['leader_count']} 封）</h2>
        <p style="color: #7f8c8d;">以下是来自领导的所有邮件，已按发件人分类</p>
"""
            for sender_email, sender_info in summary['leaders'].items():
                sender_display = f"{sender_info['name']}({sender_email})"
                email_count = len(sender_info['emails'])
                html += f"""
        <div class="sender-group leader-group">
            <div class="sender-header leader-header">
                {sender_display} <span class="badge badge-danger">{email_count} 封</span>
            </div>
"""
                for email_item in sender_info['emails']:
                    html += f"""
            <div class="email-item">
                <div class="email-subject">{email_item['subject']}</div>
                <div class="email-meta">
                    <strong>日期：</strong>{self.format_date(email_item['date'])}
                </div>
                <div class="email-body">
                    {self.truncate_text(email_item['body'], 300)}
                </div>
            </div>
"""
                html += """
        </div>
"""
        
        # 员工邮件（按人分类，排除已在重复问题中显示的）
        if summary['employees']:
            # 获取重复问题中的邮件ID
            repeat_email_ids = set()
            for issue in summary['repeat_issues']:
                for email_item in issue['emails']:
                    repeat_email_ids.add(email_item['id'])
            
            # 统计非重复问题的员工邮件数量
            non_repeat_count = 0
            for sender_info in summary['employees'].values():
                for email_item in sender_info['emails']:
                    if email_item['id'] not in repeat_email_ids:
                        non_repeat_count += 1
            
            html += f"""
        <h2>👥 员工邮件（共 {summary['employee_count']} 封）</h2>
        <p style="color: #7f8c8d;">以下是来自部门员工的邮件，已按发件人分类。重复问题已在上方单独显示。</p>
"""
            for sender_email, sender_info in summary['employees'].items():
                sender_display = f"{sender_info['name']}({sender_email})"
                
                # 过滤掉重复问题中的邮件
                normal_emails = [e for e in sender_info['emails'] if e['id'] not in repeat_email_ids]
                
                if normal_emails:
                    email_count = len(normal_emails)
                    html += f"""
        <div class="sender-group">
            <div class="sender-header">
                {sender_display} <span class="badge badge-info">{email_count} 封</span>
            </div>
"""
                    for email_item in normal_emails:
                        html += f"""
            <div class="email-item">
                <div class="email-subject">{email_item['subject']}</div>
                <div class="email-meta">
                    <strong>日期：</strong>{self.format_date(email_item['date'])}
                </div>
                <div class="email-body">
                    {self.truncate_text(email_item['body'], 300)}
                </div>
            </div>
"""
                    html += """
        </div>
"""
        
        html += """
        <div class="footer">
            <p>本报告由邮件助手自动生成 - V2.0</p>
        </div>
    </div>
</body>
</html>
"""
        
        logger.info("HTML报告生成完成")
        return html

