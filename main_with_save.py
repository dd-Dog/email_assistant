"""
主程序 - 带本地保存功能
生成报告后保存到本地文件，同时尝试发送邮件
"""
import json
import logging
import sys
from datetime import datetime
from email_client import EmailClient
from email_analyzer import EmailAnalyzer
from report_generator_text import TextReportGenerator
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'email_assistant_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def load_config(config_file='config.json'):
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info("配置文件加载成功")
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        sys.exit(1)


def save_report_to_file(report_text, config):
    """保存报告到本地文件"""
    # 创建reports目录
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # 生成文件名
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(reports_dir, filename)
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    logger.info(f"✅ 报告已保存到: {filepath}")
    return filepath


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("邮件助手开始运行（V3.0 - 带本地保存）")
    logger.info("=" * 50)
    
    # 加载配置
    config = load_config()
    
    # 初始化邮件客户端
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
        # 连接到邮箱
        if not client.connect_imap():
            logger.error("无法连接到邮箱服务器，程序退出")
            return
        
        # 获取配置
        leaders = config.get('leaders', {})
        project_managers = config.get('project_managers', {})
        employees = config.get('employees', {})
        days_to_check = config.get('days_to_check', 7)
        repeat_issue_days = config.get('repeat_issue_days', 3)
        
        logger.info(f"正在读取最近 {days_to_check} 天的邮件...")
        logger.info(f"领导数量: {len(leaders)}")
        logger.info(f"项目经理数量: {len(project_managers)}")
        logger.info(f"员工数量: {len(employees)}")
        
        # 合并所有关键人，一次性获取所有邮件（避免连接超时）
        all_senders = {}
        all_senders.update(leaders)
        all_senders.update(project_managers)
        all_senders.update(employees)
        
        logger.info(f"正在获取 {len(all_senders)} 个关键人的邮件...")
        all_emails = client.fetch_emails_from_senders(all_senders, days_to_check)
        
        # 分类邮件
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
        
        logger.info(f"获取到 {len(leader_emails)} 封领导邮件")
        logger.info(f"获取到 {len(pm_emails)} 封项目经理邮件")
        logger.info(f"获取到 {len(employee_emails)} 封员工邮件")
        
        total_emails = len(all_emails)
        
        if total_emails == 0:
            logger.warning("未找到任何邮件")
            return
        
        # 分析员工邮件中的重复问题
        analyzer = EmailAnalyzer(repeat_days=repeat_issue_days)
        
        employee_repeat_issues = []
        if employee_emails:
            logger.info("正在分析员工邮件中的重复问题...")
            employee_repeat_issues = analyzer.find_repeat_issues(employee_emails)
            if employee_repeat_issues:
                logger.info(f"⚠️  发现 {len(employee_repeat_issues)} 个重复问题！")
            else:
                logger.info("✅ 未发现重复问题")
        
        # 生成摘要（V3.0）
        logger.info("正在生成邮件摘要...")
        summary = analyzer.generate_summary(leaders, project_managers, employees, 
                                            leader_emails, pm_emails, employee_emails, 
                                            employee_repeat_issues)
        
        # 生成纯文本报告（V3.0）
        logger.info("=" * 50)
        report_gen = TextReportGenerator()
        text_report = report_gen.generate_text_report(summary)
        
        # 保存报告到本地文件
        report_file = save_report_to_file(text_report, config)
        
        # 准备发送报告
        today = datetime.now().strftime('%Y-%m-%d')
        subject = f"工作邮件汇总 - {today}"
        
        if employee_repeat_issues:
            subject += f" (有{len(employee_repeat_issues)}个重复问题)"
        
        # 发送报告到多个收件人
        target_emails = config.get('target_emails', [])
        if not target_emails and 'target_email' in config:
            target_emails = [config['target_email']]
        if isinstance(target_emails, str):
            target_emails = [target_emails]
        
        logger.info(f"准备发送报告到 {len(target_emails)} 个邮箱")
        logger.info(f"报告主题: {subject}")
        
        success_count = 0
        failed_emails = []
        
        for target_email in target_emails:
            if not target_email:
                continue
            
            logger.info(f"  → 发送到: {target_email}")
            success = client.send_email_text(target_email, subject, text_report)
            
            if success:
                success_count += 1
                logger.info(f"    ✅ 发送成功")
            else:
                failed_emails.append(target_email)
                logger.error(f"    ❌ 发送失败")
        
        # 总结
        logger.info("=" * 50)
        logger.info(f"📄 本地报告: {report_file}")
        if success_count > 0:
            logger.info(f"✅ 成功发送到 {success_count}/{len(target_emails)} 个邮箱")
            if failed_emails:
                logger.warning(f"⚠️  失败邮箱: {', '.join(failed_emails)}")
        else:
            logger.warning("⚠️  邮件发送失败，但报告已保存到本地文件")
            logger.warning(f"   请查看: {report_file}")
        logger.info("=" * 50)
        
        # 断开连接
        client.disconnect_imap()
        
        logger.info("=" * 50)
        logger.info("邮件助手运行完成（V3.0）")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}", exc_info=True)
        client.disconnect_imap()
        sys.exit(1)


if __name__ == "__main__":
    main()

