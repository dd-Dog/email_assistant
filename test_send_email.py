"""
邮件发送测试工具 - 测试SMTP发送是否正常
"""
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_send_simple_email():
    """发送一个简单的测试邮件"""
    print("=" * 60)
    print("📧 邮件发送测试工具")
    print("=" * 60)
    
    # 读取配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ 配置文件加载成功")
    except Exception as e:
        print(f"❌ 无法读取配置文件: {str(e)}")
        return
    
    email_account = config['email_account']
    target_email = config['target_email']
    
    print(f"\n发件邮箱: {email_account['username']}")
    print(f"收件邮箱: {target_email}")
    print(f"SMTP服务器: {email_account['smtp_server']}:{email_account['smtp_port']}")
    
    # 测试1：发送纯文本邮件
    print("\n" + "-" * 60)
    print("测试1：发送纯文本邮件")
    print("-" * 60)
    
    try:
        msg = MIMEMultipart()
        msg['From'] = email_account['username']
        msg['To'] = target_email
        msg['Subject'] = f"测试邮件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = """
这是一封测试邮件。

如果您收到这封邮件，说明SMTP发送功能正常。

测试时间：{}
发件人：{}

-- 
邮件助手测试工具
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), email_account['username'])
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(email_account['smtp_server'], 
                              email_account['smtp_port'], 
                              context=context) as server:
            server.login(email_account['username'], email_account['password'])
            server.send_message(msg)
        
        print("✅ 纯文本邮件发送成功！")
        print(f"   请检查 {target_email} 的收件箱")
        print("   如果收件箱没有，请检查【垃圾邮件】、【订阅邮件】文件夹")
        
    except Exception as e:
        print(f"❌ 发送失败: {str(e)}")
        return
    
    # 测试2：发送HTML邮件（简单版）
    print("\n" + "-" * 60)
    print("测试2：发送简单HTML邮件")
    print("-" * 60)
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = email_account['username']
        msg['To'] = target_email
        msg['Subject'] = f"HTML测试邮件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #2c3e50;">📧 HTML邮件测试</h2>
    <p>这是一封HTML格式的测试邮件。</p>
    <p>如果您能看到这封邮件，说明HTML邮件可以正常发送和接收。</p>
    <ul>
        <li>测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
        <li>发件人: {email_account['username']}</li>
        <li>收件人: {target_email}</li>
    </ul>
    <hr>
    <p style="color: #7f8c8d; font-size: 12px;">邮件助手测试工具</p>
</body>
</html>
"""
        
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(html_part)
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(email_account['smtp_server'], 
                              email_account['smtp_port'], 
                              context=context) as server:
            server.login(email_account['username'], email_account['password'])
            server.send_message(msg)
        
        print("✅ HTML邮件发送成功！")
        print(f"   请检查 {target_email} 的收件箱")
        
    except Exception as e:
        print(f"❌ 发送失败: {str(e)}")
        return
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("\n请检查您的邮箱：")
    print("1. 收件箱")
    print("2. 垃圾邮件")
    print("3. 订阅邮件")
    print("4. 广告邮件")
    print("\n如果都没有收到，可能是：")
    print("- QQ邮箱的反垃圾系统拦截")
    print("- 需要设置白名单")
    print("- 邮箱地址输入错误")
    print("=" * 60)

if __name__ == "__main__":
    test_send_simple_email()

