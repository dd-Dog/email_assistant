"""
邮箱连接测试工具 - 用于诊断IMAP/SMTP连接问题
"""
import imaplib
import smtplib
import json
import ssl
import sys

def test_imap_connection(username, password, server, port):
    """测试IMAP连接"""
    print("\n" + "="*60)
    print("🔍 测试 IMAP 连接...")
    print("="*60)
    print(f"服务器: {server}:{port}")
    print(f"用户名: {username}")
    print(f"密码: {'*' * len(password)}")
    print()
    
    try:
        print("正在连接...")
        imap = imaplib.IMAP4_SSL(server, port)
        print("✅ SSL连接成功")
        
        print("正在登录...")
        imap.login(username, password)
        print("✅ IMAP登录成功！")
        
        # 尝试列出文件夹
        status, folders = imap.list()
        if status == 'OK':
            print(f"✅ 找到 {len(folders)} 个邮件文件夹")
        
        # 选择收件箱
        status, messages = imap.select("INBOX")
        if status == 'OK':
            print(f"✅ 收件箱中有 {messages[0].decode()} 封邮件")
        
        imap.logout()
        print("\n✅ IMAP 测试完全成功！\n")
        return True
        
    except imaplib.IMAP4.error as e:
        print(f"\n❌ IMAP错误: {str(e)}")
        print("\n可能的原因：")
        print("  1. 用户名或密码错误")
        print("  2. IMAP服务未开启")
        print("  3. 需要使用授权码而不是密码")
        print("  4. 账户被锁定或有安全限制")
        return False
        
    except Exception as e:
        print(f"\n❌ 连接错误: {str(e)}")
        print("\n可能的原因：")
        print("  1. 网络连接问题")
        print("  2. 服务器地址或端口错误")
        print("  3. 防火墙阻止连接")
        return False


def test_smtp_connection(username, password, server, port):
    """测试SMTP连接"""
    print("\n" + "="*60)
    print("🔍 测试 SMTP 连接...")
    print("="*60)
    print(f"服务器: {server}:{port}")
    print(f"用户名: {username}")
    print(f"密码: {'*' * len(password)}")
    print()
    
    try:
        print("正在连接...")
        context = ssl.create_default_context()
        smtp = smtplib.SMTP_SSL(server, port, context=context)
        print("✅ SSL连接成功")
        
        print("正在登录...")
        smtp.login(username, password)
        print("✅ SMTP登录成功！")
        
        smtp.quit()
        print("\n✅ SMTP 测试完全成功！\n")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ SMTP认证错误: {str(e)}")
        print("\n可能的原因：")
        print("  1. 用户名或密码错误")
        print("  2. SMTP服务未开启")
        print("  3. 需要使用授权码而不是密码")
        return False
        
    except Exception as e:
        print(f"\n❌ 连接错误: {str(e)}")
        print("\n可能的原因：")
        print("  1. 网络连接问题")
        print("  2. 服务器地址或端口错误")
        print("  3. 防火墙阻止连接")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("📧 邮箱连接测试工具")
    print("="*60)
    
    # 读取配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ 配置文件加载成功")
    except Exception as e:
        print(f"❌ 无法读取配置文件: {str(e)}")
        sys.exit(1)
    
    email_account = config['email_account']
    
    # 显示配置信息
    print("\n当前配置：")
    print(f"  邮箱账号: {email_account['username']}")
    print(f"  IMAP服务器: {email_account['imap_server']}:{email_account['imap_port']}")
    print(f"  SMTP服务器: {email_account['smtp_server']}:{email_account['smtp_port']}")
    
    # 测试IMAP
    imap_success = test_imap_connection(
        email_account['username'],
        email_account['password'],
        email_account['imap_server'],
        email_account['imap_port']
    )
    
    # 测试SMTP
    smtp_success = test_smtp_connection(
        email_account['username'],
        email_account['password'],
        email_account['smtp_server'],
        email_account['smtp_port']
    )
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    print(f"IMAP测试: {'✅ 成功' if imap_success else '❌ 失败'}")
    print(f"SMTP测试: {'✅ 成功' if smtp_success else '❌ 失败'}")
    
    if imap_success and smtp_success:
        print("\n🎉 所有测试通过！您可以正常使用邮件助手了。")
        print("   运行 'python main.py' 开始使用。")
    else:
        print("\n⚠️  请根据上面的错误信息排查问题。")
        print("\n常见解决方案：")
        print("1. 登录阿里企业邮箱网页版，开启IMAP/SMTP服务")
        print("2. 生成客户端授权码，替换config.json中的密码")
        print("3. 确认用户名和密码输入正确")
        print("4. 联系企业邮箱管理员确认权限")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

