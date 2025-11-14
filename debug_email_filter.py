# -*- coding: utf-8 -*-
"""
调试邮件过滤 - 查看哪些邮件被过滤了
"""
import json
import logging
from datetime import datetime
from email_client import EmailClient
from person_manager import PersonManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def debug_email_filter():
    """调试邮件过滤"""
    print("=" * 70)
    print("邮件过滤调试工具")
    print("=" * 70)
    print()
    
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 加载人员
    person_mgr = PersonManager(persons_root='persons')
    
    if person_mgr.has_profiles():
        leaders = person_mgr.get_persons_by_type('leader')
        project_managers = person_mgr.get_persons_by_type('pm')
        employees = person_mgr.get_persons_by_type('employee')
        customers = person_mgr.get_persons_by_type('customer')
        suppliers = person_mgr.get_persons_by_type('supplier')
        all_senders = person_mgr.get_all_key_senders()
    else:
        print("未找到人员信息")
        return
    
    print(f"配置的关键人员:")
    print(f"  领导: {len(leaders)}")
    print(f"  项目经理: {len(project_managers)}")
    print(f"  员工: {len(employees)}")
    print(f"  客户: {len(customers)}")
    print(f"  供应商: {len(suppliers)}")
    print(f"  总计: {len(all_senders)}")
    print()
    
    # 显示员工列表
    print("员工列表:")
    for email, name in employees.items():
        print(f"  - {name} ({email})")
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
    print(f"正在获取最近 {days_to_check} 天的邮件...")
    all_emails = client.fetch_emails_from_senders(all_senders, days_to_check)
    
    print(f"总共获取: {len(all_emails)} 封邮件")
    print()
    
    # 按发件人分组统计
    sender_count = {}
    for email_item in all_emails:
        sender = email_item['from_email']
        sender_name = all_senders.get(sender, sender)
        key = f"{sender_name} ({sender})"
        sender_count[key] = sender_count.get(key, 0) + 1
    
    print("各发件人邮件数量:")
    for sender, count in sorted(sender_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {sender}: {count}封")
    print()
    
    # 检查姜新宇的邮件
    print("=" * 70)
    print("姜新宇的邮件详情:")
    print("=" * 70)
    
    jiangxy_email = 'jiangxy@flyscale.cn'
    jiangxy_emails = [e for e in all_emails if e['from_email'].lower() == jiangxy_email.lower()]
    
    if jiangxy_emails:
        print(f"找到 {len(jiangxy_emails)} 封姜新宇的邮件:")
        print()
        for idx, email in enumerate(jiangxy_emails, 1):
            print(f"  [{idx}] 日期: {email['date'].strftime('%Y-%m-%d %H:%M')}")
            print(f"      主题: {email['subject']}")
            print(f"      内容: {email['body'][:100]}...")
            print()
    else:
        print("未找到姜新宇的邮件")
        print()
        print(f"配置中的姜新宇邮箱: {jiangxy_email}")
        print(f"是否在员工列表中: {jiangxy_email in employees}")
    
    client.disconnect_imap()
    
    print("=" * 70)
    print("调试完成")
    print("=" * 70)


if __name__ == '__main__':
    debug_email_filter()

