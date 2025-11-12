"""
测试V4.0 - 不启用AI版本
先测试基础功能是否正常
"""
import json
from datetime import datetime
from email_client import EmailClient
from email_analyzer import EmailAnalyzer
from report_generator_ai import AIReportGenerator

print("=" * 70)
print("测试 V4.0 基础功能（不启用AI）")
print("=" * 70)

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 临时禁用AI
config['ai_config']['enabled'] = False

email_account = config['email_account']
client = EmailClient(
    username=email_account['username'],
    password=email_account['password'],
    imap_server=email_account['imap_server'],
    imap_port=email_account['imap_port'],
    smtp_server=email_account['smtp_server'],
    smtp_port=email_account['smtp_port']
)

try:
    print("\n1. 连接邮箱...")
    if not client.connect_imap():
        print("❌ 连接失败")
        exit(1)
    print("✅ 连接成功")
    
    print("\n2. 获取邮件...")
    leaders = config.get('leaders', {})
    project_managers = config.get('project_managers', {})
    employees = config.get('employees', {})
    
    all_senders = {}
    all_senders.update(leaders)
    all_senders.update(project_managers)
    all_senders.update(employees)
    
    all_emails = client.fetch_emails_from_senders(all_senders, 4)
    print(f"✅ 获取到 {len(all_emails)} 封邮件")
    
    print("\n3. 分类邮件...")
    leader_emails_lower = {email.lower() for email in leaders.keys()}
    pm_emails_lower = {email.lower() for email in project_managers.keys()}
    
    leader_emails = []
    pm_emails = []
    employee_emails = []
    
    for email_item in all_emails:
        email_lower = email_item['from_email'].lower()
        if email_lower in leader_emails_lower:
            leader_emails.append(email_item)
        elif email_lower in pm_emails_lower:
            pm_emails.append(email_item)
        else:
            employee_emails.append(email_item)
    
    print(f"✅ 分类完成: 领导 {len(leader_emails)} | 项目经理 {len(pm_emails)} | 员工 {len(employee_emails)}")
    
    print("\n4. 分析重复问题...")
    analyzer = EmailAnalyzer(repeat_days=3)
    employee_repeat_issues = analyzer.find_repeat_issues(employee_emails) if employee_emails else []
    print(f"✅ 发现 {len(employee_repeat_issues)} 个重复问题")
    
    print("\n5. 生成摘要...")
    summary = analyzer.generate_summary(leaders, project_managers, employees,
                                       leader_emails, pm_emails, employee_emails,
                                       employee_repeat_issues)
    print(f"✅ 摘要生成完成")
    
    print("\n6. 生成报告（不含AI）...")
    report_gen = AIReportGenerator()
    text_report = report_gen.generate_text_report(summary, ai_enabled=False)
    
    # 保存到文件
    filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text_report)
    
    print(f"✅ 报告已保存: {filename}")
    print(f"   报告大小: {len(text_report)} 字符")
    
    print("\n" + "=" * 70)
    print("✅ 所有测试通过！基础功能正常")
    print("=" * 70)
    print("\n下一步：")
    print("1. 安装AI依赖: pip install openai")
    print("2. 配置API密钥")
    print("3. 运行: python main_v4.py")
    
    client.disconnect_imap()
    
except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    client.disconnect_imap()

