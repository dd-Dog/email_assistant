"""
调试工具 - 查看生成的报告内容并保存到文件
"""
import json
import sys
from datetime import datetime
from email_client import EmailClient
from email_analyzer import EmailAnalyzer
from report_generator_text import TextReportGenerator

def main():
    print("=" * 70)
    print("调试工具 - 生成报告并保存到文件")
    print("=" * 70)
    
    # 加载配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ 配置文件加载成功")
    except Exception as e:
        print(f"❌ 加载配置失败: {str(e)}")
        return
    
    # 初始化客户端
    email_account = config['email_account']
    client = EmailClient(
        username=email_account['username'],
        password=email_account['password'],
        imap_server=email_account['imap_server'],
        imap_port=email_account['imap_port'],
        smtp_server=email_account['smtp_server'],
        smtp_port=email_account['smtp_port']
    )
    
    # 连接
    if not client.connect_imap():
        print("❌ 无法连接到邮箱")
        return
    
    print("✅ 连接成功")
    
    # 获取邮件
    leaders = config.get('leaders', {})
    project_managers = config.get('project_managers', {})
    employees = config.get('employees', {})
    days_to_check = config.get('days_to_check', 3)
    
    all_senders = {}
    all_senders.update(leaders)
    all_senders.update(project_managers)
    all_senders.update(employees)
    
    print(f"正在获取邮件... ({len(all_senders)} 个关键人)")
    all_emails = client.fetch_emails_from_senders(all_senders, days_to_check)
    
    # 分类
    leader_emails = []
    pm_emails = []
    employee_emails = []
    
    leader_emails_lower = {email.lower() for email in leaders.keys()}
    pm_emails_lower = {email.lower() for email in project_managers.keys()}
    
    for email_item in all_emails:
        email_lower = email_item['from_email'].lower()
        if email_lower in leader_emails_lower:
            leader_emails.append(email_item)
        elif email_lower in pm_emails_lower:
            pm_emails.append(email_item)
        else:
            employee_emails.append(email_item)
    
    print(f"✅ 获取完成: 领导 {len(leader_emails)} | 项目经理 {len(pm_emails)} | 员工 {len(employee_emails)}")
    
    # 分析
    analyzer = EmailAnalyzer(repeat_days=config.get('repeat_issue_days', 3))
    employee_repeat_issues = []
    if employee_emails:
        employee_repeat_issues = analyzer.find_repeat_issues(employee_emails)
    
    print(f"分析完成: 重复问题 {len(employee_repeat_issues)} 个")
    
    # 生成摘要
    summary = analyzer.generate_summary(leaders, project_managers, employees,
                                       leader_emails, pm_emails, employee_emails,
                                       employee_repeat_issues)
    
    # 生成报告
    report_gen = TextReportGenerator()
    text_report = report_gen.generate_text_report(summary)
    
    # 保存到文件
    output_file = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text_report)
    
    print(f"✅ 报告已保存到: {output_file}")
    print("")
    print("=" * 70)
    print("报告内容预览（前30行）：")
    print("=" * 70)
    
    # 显示前30行
    for i, line in enumerate(text_report.split('\n')[:30], 1):
        print(line)
    
    print("")
    print(f"完整报告请查看: {output_file}")
    print(f"报告大小: {len(text_report)} 字符")
    print("")
    
    # 询问是否发送
    print("=" * 70)
    print("是否现在发送这个报告？(y/n)")
    choice = input("> ").strip().lower()
    
    if choice == 'y':
        target_emails = config.get('target_emails', [])
        subject = f"邮件助手每日报告 V3.0 - {datetime.now().strftime('%Y-%m-%d')}"
        
        if employee_repeat_issues:
            subject += f" [⚠️ {len(employee_repeat_issues)} 个重复问题需要关注]"
        
        print(f"正在发送到 {len(target_emails)} 个邮箱...")
        
        for target_email in target_emails:
            if not target_email:
                continue
            
            print(f"  → 发送到: {target_email}")
            success = client.send_email_text(target_email, subject, text_report)
            
            if success:
                print(f"    ✅ 发送成功")
            else:
                print(f"    ❌ 发送失败")
    
    client.disconnect_imap()
    print("")
    print("=" * 70)
    print("调试完成")
    print("=" * 70)

if __name__ == "__main__":
    main()

