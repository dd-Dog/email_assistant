import json
import logging
import sys
from datetime import datetime
from email_client import EmailClient
from email_analyzer import EmailAnalyzer
from report_generator import ReportGenerator

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


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("邮件助手开始运行")
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
        employees = config.get('employees', {})
        days_to_check = config.get('days_to_check', 7)
        repeat_issue_days = config.get('repeat_issue_days', 3)
        
        logger.info(f"正在读取最近 {days_to_check} 天的邮件...")
        logger.info(f"领导数量: {len(leaders)}")
        logger.info(f"员工数量: {len(employees)}")
        
        # 合并所有关键人，一次性获取所有邮件（避免连接超时）
        all_senders = {}
        all_senders.update(leaders)
        all_senders.update(employees)
        
        logger.info(f"正在获取 {len(all_senders)} 个关键人的邮件...")
        all_emails = client.fetch_emails_from_senders(all_senders, days_to_check)
        
        # 分类邮件
        leader_emails = []
        employee_emails = []
        
        leader_emails_lower = {email.lower() for email in leaders.keys()}
        
        for email_item in all_emails:
            if email_item['from_email'].lower() in leader_emails_lower:
                leader_emails.append(email_item)
            else:
                employee_emails.append(email_item)
        
        logger.info(f"获取到 {len(leader_emails)} 封领导邮件")
        logger.info(f"获取到 {len(employee_emails)} 封员工邮件")
        
        total_emails = len(all_emails)
        
        if total_emails == 0:
            logger.warning("未找到任何邮件")
            # 仍然发送一封空报告
            report_gen = ReportGenerator()
            summary = {
                'total_emails': 0,
                'leader_count': 0,
                'employee_count': 0,
                'leaders': {},
                'employees': {},
                'repeat_issues': []
            }
            html_report = report_gen.generate_html_report(summary)
            
            # 发送报告
            target_email = config['target_email']
            subject = f"邮件助手每日报告 V2.0 - {datetime.now().strftime('%Y-%m-%d')}"
            client.send_email(target_email, subject, html_report)
            
            client.disconnect_imap()
            return
        
        # 分析员工邮件中的重复问题
        analyzer = EmailAnalyzer(repeat_days=repeat_issue_days)
        
        employee_repeat_issues = []
        if employee_emails:
            logger.info("正在分析员工邮件中的重复问题...")
            employee_repeat_issues = analyzer.find_repeat_issues(employee_emails)
        
        # 生成摘要（V2.0）
        logger.info("正在生成邮件摘要...")
        summary = analyzer.generate_summary(leader_emails, employee_emails, employee_repeat_issues)
        
        # 生成HTML报告
        report_gen = ReportGenerator()
        html_report = report_gen.generate_html_report(summary)
        
        # 发送报告到目标邮箱
        target_email = config['target_email']
        subject = f"邮件助手每日报告 V2.0 - {datetime.now().strftime('%Y-%m-%d')}"
        
        if employee_repeat_issues:
            subject += f" [⚠️ {len(employee_repeat_issues)} 个重复问题需要关注]"
        
        success = client.send_email(target_email, subject, html_report)
        
        if success:
            logger.info(f"报告已成功发送到: {target_email}")
        else:
            logger.error("报告发送失败")
        
        # 断开连接
        client.disconnect_imap()
        
        logger.info("=" * 50)
        logger.info("邮件助手运行完成（V2.0）")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}", exc_info=True)
        client.disconnect_imap()
        sys.exit(1)


if __name__ == "__main__":
    main()

