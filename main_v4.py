"""
主程序 V4.0 - AI增强版
集成AI分析能力，提供智能邮件摘要和建议
"""
import json
import logging
import sys
import os
from datetime import datetime
from email_client import EmailClient
from email_analyzer import EmailAnalyzer
from report_generator_ai import AIReportGenerator
from ai_analyzer import AIAnalyzer

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
    """主函数 V4.0"""
    logger.info("=" * 50)
    logger.info("AI邮件助手开始运行（V5.0 - 上下文感知版）")
    logger.info("=" * 50)
    
    # 加载配置
    config = load_config()
    
    # 初始化AI分析器
    ai_config = config.get('ai_config', {})
    ai_analyzer = AIAnalyzer(ai_config)
    
    if ai_analyzer.is_available():
        logger.info("🤖 AI功能已启用")
        # 显示成本估算
        cost = ai_analyzer.get_cost_estimate(20)  # 假设20封邮件
        logger.info(f"   预估成本: ${cost:.3f} (约20封邮件)")
    else:
        logger.info("ℹ️  AI功能未启用，使用基础模式")
    
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
        
        # 获取配置（5类人员）
        leaders = config.get('leaders', {})
        project_managers = config.get('project_managers', {})
        employees = config.get('employees', {})
        customers = config.get('customers', {})
        suppliers = config.get('suppliers', {})
        days_to_check = config.get('days_to_check', 3)
        repeat_issue_days = config.get('repeat_issue_days', 3)
        
        logger.info(f"正在读取最近 {days_to_check} 天的邮件...")
        logger.info(f"领导: {len(leaders)} | 项目经理: {len(project_managers)} | 员工: {len(employees)}")
        logger.info(f"客户: {len(customers)} | 供应商: {len(suppliers)}")
        
        # 合并所有关键人，一次性获取所有邮件
        all_senders = {}
        all_senders.update(leaders)
        all_senders.update(project_managers)
        all_senders.update(employees)
        all_senders.update(customers)
        all_senders.update(suppliers)
        
        logger.info(f"正在获取 {len(all_senders)} 个关键人的邮件...")
        all_emails = client.fetch_emails_from_senders(all_senders, days_to_check)
        
        # 分类邮件（5类）
        leader_emails = []
        pm_emails = []
        employee_emails = []
        customer_emails = []
        supplier_emails = []
        
        leader_emails_lower = {email.lower() for email in leaders.keys()}
        pm_emails_lower = {email.lower() for email in project_managers.keys()}
        customer_emails_lower = {email.lower() for email in customers.keys()}
        supplier_emails_lower = {email.lower() for email in suppliers.keys()}
        
        for email_item in all_emails:
            email_lower = email_item['from_email'].lower()
            if email_lower in leader_emails_lower:
                leader_emails.append(email_item)
            elif email_lower in pm_emails_lower:
                pm_emails.append(email_item)
            elif email_lower in customer_emails_lower:
                customer_emails.append(email_item)
            elif email_lower in supplier_emails_lower:
                supplier_emails.append(email_item)
            else:
                employee_emails.append(email_item)
        
        logger.info(f"领导: {len(leader_emails)} | 项目经理: {len(pm_emails)} | 员工: {len(employee_emails)}")
        logger.info(f"客户: {len(customer_emails)} | 供应商: {len(supplier_emails)}")
        
        total_emails = len(all_emails)
        
        if total_emails == 0:
            logger.warning("未找到任何邮件")
            client.disconnect_imap()
            return
        
        # V4.0新增：AI分析邮件（根据类型定制分析）
        if ai_analyzer.is_available():
            logger.info("=" * 50)
            logger.info("🤖 开始AI智能分析...")
            logger.info("=" * 50)
            
            # 创建发件人类型映射
            sender_type_map = {}
            for email in customers.keys():
                sender_type_map[email] = 'customer'
            for email in suppliers.keys():
                sender_type_map[email] = 'supplier'
            
            # 对所有邮件进行AI分析（传入类型映射）
            all_emails = ai_analyzer.analyze_emails_batch(all_emails, sender_type_map)
            
            # 重新分类（因为邮件对象已更新）
            leader_emails = [e for e in all_emails if e['from_email'].lower() in leader_emails_lower]
            pm_emails = [e for e in all_emails if e['from_email'].lower() in pm_emails_lower]
            customer_emails = [e for e in all_emails if e['from_email'].lower() in customer_emails_lower]
            supplier_emails = [e for e in all_emails if e['from_email'].lower() in supplier_emails_lower]
            employee_emails = [e for e in all_emails if e['from_email'].lower() not in leader_emails_lower 
                              and e['from_email'].lower() not in pm_emails_lower
                              and e['from_email'].lower() not in customer_emails_lower
                              and e['from_email'].lower() not in supplier_emails_lower]
        
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
        
        # 生成摘要（5类人员）
        logger.info("正在生成邮件摘要...")
        summary = analyzer.generate_summary(leaders, project_managers, employees, customers, suppliers,
                                            leader_emails, pm_emails, employee_emails, 
                                            customer_emails, supplier_emails,
                                            employee_repeat_issues)
        
        # 生成AI增强报告
        logger.info("=" * 50)
        report_gen = AIReportGenerator()
        text_report = report_gen.generate_text_report(summary, ai_analyzer.is_available())
        
        # 保存报告到本地
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        report_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_filepath = os.path.join(reports_dir, report_filename)
        
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        logger.info(f"✅ 报告已保存到本地: {report_filepath}")
        
        # 准备发送报告
        today = datetime.now().strftime('%m月%d日')
        subject = f"{today}工作汇总"
        
        if ai_analyzer.is_available():
            subject += " [AI分析]"
        
        if employee_repeat_issues:
            subject += f"(需关注)"
        
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
        logger.info(f"📄 本地报告: {report_filepath}")
        if success_count > 0:
            logger.info(f"✅ 成功发送到 {success_count}/{len(target_emails)} 个邮箱")
            if failed_emails:
                logger.warning(f"⚠️  失败邮箱: {', '.join(failed_emails)}")
        else:
            logger.warning("⚠️  邮件发送失败，但报告已保存到本地")
            logger.warning(f"   请直接查看: {report_filepath}")
        logger.info("=" * 50)
        
        # 断开连接
        client.disconnect_imap()
        
        logger.info("=" * 50)
        logger.info("AI邮件助手运行完成（V5.0）")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}", exc_info=True)
        client.disconnect_imap()
        sys.exit(1)


if __name__ == "__main__":
    main()

