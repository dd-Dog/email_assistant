# -*- coding: utf-8 -*-
"""
调试遗漏邮件 - 查找哪些邮件没有显示在报告中
"""
import json
import logging
from datetime import datetime
from email_client import EmailClient
from person_manager import PersonManager
from ai_analyzer import AIAnalyzer
from email_analyzer import EmailAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.WARNING
)

logger = logging.getLogger(__name__)


def debug_missing_emails():
    """调试遗漏的邮件"""
    print("=" * 80)
    print("遗漏邮件调试")
    print("=" * 80)
    print()
    
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 加载人员
    person_mgr = PersonManager(persons_root='persons')
    all_senders = person_mgr.get_all_key_senders()
    leaders = person_mgr.get_persons_by_type('leader')
    pms = person_mgr.get_persons_by_type('pm')
    employees = person_mgr.get_persons_by_type('employee')
    customers = person_mgr.get_persons_by_type('customer')
    suppliers = person_mgr.get_persons_by_type('supplier')
    
    # 连接邮箱
    email_account = config['email_account']
    client = EmailClient(
        username=email_account['username'],
        password=email_account['password'],
        imap_server=email_account['imap_server'],
        imap_port=email_account['imap_port'],
        smtp_server=email_account['smtp_server'],
        smtp_port=email_account['smtp_port']
    )
    
    if not client.connect_imap():
        print("无法连接到邮箱")
        return
    
    # 获取邮件
    days_to_check = config.get('days_to_check', 1)
    all_emails = client.fetch_emails_from_senders(all_senders, days_to_check)
    
    print(f"获取到 {len(all_emails)} 封邮件")
    print()
    
    # 分类邮件
    leader_emails_lower = {email.lower() for email in leaders.keys()}
    pm_emails_lower = {email.lower() for email in pms.keys()}
    customer_emails_lower = {email.lower() for email in customers.keys()}
    supplier_emails_lower = {email.lower() for email in suppliers.keys()}
    
    employee_emails = []
    for email_item in all_emails:
        email_lower = email_item['from_email'].lower()
        if email_lower not in leader_emails_lower and \
           email_lower not in pm_emails_lower and \
           email_lower not in customer_emails_lower and \
           email_lower not in supplier_emails_lower:
            employee_emails.append(email_item)
    
    print(f"员工邮件: {len(employee_emails)} 封")
    print()
    
    # AI分析
    ai_config = config.get('ai_config', {})
    ai_analyzer = AIAnalyzer(ai_config)
    
    if ai_analyzer.is_available():
        print("开始AI分析...")
        sender_type_map = {}
        for email in employees.keys():
            sender_type_map[email] = 'normal'
        
        ai_analyzer.analyze_emails_batch(all_emails, sender_type_map)
        print()
    
    # 检查高优先级
    high_priority_emails = []
    for email in employee_emails:
        ai_analysis = email.get('ai_analysis')
        if ai_analysis and ai_analysis.get('priority') == 'high':
            high_priority_emails.append(email)
    
    print(f"员工邮件中的高优先级: {len(high_priority_emails)} 封")
    print()
    
    if high_priority_emails:
        print("高优先级员工邮件:")
        for email in high_priority_emails:
            sender_name = all_senders.get(email['from_email'], '未知')
            date_str = email['date'].strftime('%m-%d %H:%M')
            print(f"  [{date_str}] {sender_name:8s} | {email['subject']}")
        print()
    
    # 非高优先级的员工邮件
    normal_priority_emails = [e for e in employee_emails if e['id'] not in {e['id'] for e in high_priority_emails}]
    
    print(f"普通优先级员工邮件: {len(normal_priority_emails)} 封")
    print()
    
    if normal_priority_emails:
        print("普通优先级员工邮件（应该在'员工邮件汇总'中显示）:")
        for email in normal_priority_emails:
            sender_name = all_senders.get(email['from_email'], '未知')
            date_str = email['date'].strftime('%m-%d %H:%M')
            priority = email.get('ai_analysis', {}).get('priority', '无')
            print(f"  [{date_str}] {sender_name:8s} | {email['subject'][:30]} | 优先级:{priority}")
    
    client.disconnect_imap()
    
    print()
    print("=" * 80)
    print("分析完成")
    print("=" * 80)


if __name__ == '__main__':
    debug_missing_emails()

