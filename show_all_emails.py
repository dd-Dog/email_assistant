# -*- coding: utf-8 -*-
"""
显示所有获取到的邮件 - 完整列表
"""
import json
import logging
from datetime import datetime
from email_client import EmailClient
from person_manager import PersonManager

# 配置日志
logging.basicConfig(
    level=logging.WARNING  # 只显示警告和错误
)

logger = logging.getLogger(__name__)


def show_all_emails():
    """显示所有获取到的邮件"""
    print("=" * 80)
    print("邮件获取详情")
    print("=" * 80)
    print()
    
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 加载人员
    person_mgr = PersonManager(persons_root='persons')
    
    if person_mgr.has_profiles():
        all_senders = person_mgr.get_all_key_senders()
    else:
        print("未找到人员信息")
        return
    
    print(f"监控 {len(all_senders)} 个关键人员")
    print()
    
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
    print(f"获取最近 {days_to_check} 天的邮件...")
    all_emails = client.fetch_emails_from_senders(all_senders, days_to_check)
    
    print(f"总共: {len(all_emails)} 封")
    print()
    print("=" * 80)
    
    # 按时间排序
    all_emails.sort(key=lambda x: x['date'], reverse=True)
    
    # 显示所有邮件
    for idx, email in enumerate(all_emails, 1):
        sender_name = all_senders.get(email['from_email'], '未知')
        date_str = email['date'].strftime('%Y-%m-%d %H:%M')
        
        print(f"[{idx:2d}] {date_str} | {sender_name:8s} | {email['subject']}")
    
    print()
    print("=" * 80)
    
    # 按发件人分组
    print("按发件人分组:")
    print("=" * 80)
    
    sender_emails = {}
    for email in all_emails:
        sender = email['from_email']
        if sender not in sender_emails:
            sender_emails[sender] = []
        sender_emails[sender].append(email)
    
    for sender in sorted(sender_emails.keys()):
        sender_name = all_senders.get(sender, sender)
        emails = sender_emails[sender]
        print(f"\n{sender_name} ({sender}) - {len(emails)}封:")
        for email in emails:
            date_str = email['date'].strftime('%m-%d %H:%M')
            print(f"  [{date_str}] {email['subject'][:50]}")
    
    client.disconnect_imap()
    
    print()
    print("=" * 80)


if __name__ == '__main__':
    show_all_emails()

