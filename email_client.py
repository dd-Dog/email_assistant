import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import ssl
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmailClient:
    """邮箱客户端类，处理邮件的接收和发送"""
    
    def __init__(self, username, password, imap_server, imap_port, smtp_server, smtp_port):
        self.username = username
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_conn = None
    
    def connect_imap(self):
        """连接到IMAP服务器"""
        try:
            logger.info(f"正在连接到 IMAP 服务器: {self.imap_server}:{self.imap_port}")
            self.imap_conn = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.imap_conn.login(self.username, self.password)
            logger.info("IMAP 登录成功")
            return True
        except Exception as e:
            logger.error(f"IMAP 连接失败: {str(e)}")
            return False
    
    def disconnect_imap(self):
        """断开IMAP连接"""
        if self.imap_conn:
            try:
                self.imap_conn.close()
                self.imap_conn.logout()
                logger.info("IMAP 连接已关闭")
            except:
                pass
    
    def decode_mime_words(self, s):
        """解码邮件头部信息"""
        if s is None:
            return ""
        decoded_parts = decode_header(s)
        result = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    try:
                        result.append(part.decode(encoding))
                    except:
                        result.append(part.decode('utf-8', errors='ignore'))
                else:
                    result.append(part.decode('utf-8', errors='ignore'))
            else:
                result.append(str(part))
        return ''.join(result)
    
    def get_email_body(self, msg):
        """提取邮件正文"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        try:
                            charset = part.get_content_charset() or 'utf-8'
                            body = part.get_payload(decode=True).decode(charset, errors='ignore')
                            if body:
                                break
                        except:
                            pass
                    elif content_type == "text/html" and not body:
                        try:
                            charset = part.get_content_charset() or 'utf-8'
                            body = part.get_payload(decode=True).decode(charset, errors='ignore')
                        except:
                            pass
        else:
            try:
                charset = msg.get_content_charset() or 'utf-8'
                body = msg.get_payload(decode=True).decode(charset, errors='ignore')
            except:
                pass
        
        return body.strip()
    
    def fetch_emails_from_senders(self, senders_dict, days=7):
        """从指定发件人获取最近几天的邮件
        
        Args:
            senders_dict: 字典格式 {email: name}
            days: 获取最近几天的邮件
            
        Returns:
            邮件数据列表，每封邮件包含发件人姓名信息
        """
        if not self.imap_conn:
            logger.error("未连接到 IMAP 服务器")
            return []
        
        try:
            self.imap_conn.select("INBOX")
            
            # 计算日期范围（用于本地过滤）
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 创建发件人邮箱地址集合（小写，用于匹配）
            sender_emails_lower = {email.lower(): (email, name) for email, name in senders_dict.items()}
            
            emails_data = []
            
            logger.info(f"正在获取最近的邮件（将在本地过滤发件人）...")
            
            # 获取所有邮件ID - 使用最简单的搜索命令
            try:
                status, messages = self.imap_conn.search(None, 'ALL')
                if status != "OK":
                    logger.error("搜索邮件失败")
                    return []
                
                email_ids = messages[0].split()
                total_emails = len(email_ids)
                logger.info(f"收件箱中共有 {total_emails} 封邮件，正在筛选...")
                
                # 只处理最近的N封邮件（避免处理过多）
                max_check = min(500, total_emails)  # 最多检查最近500封（提升速度）
                recent_email_ids = email_ids[-max_check:] if total_emails > max_check else email_ids
                
                logger.info(f"将检查最近 {len(recent_email_ids)} 封邮件")
                
                processed = 0
                for email_id in recent_email_ids:
                    try:
                        processed += 1
                        if processed % 50 == 0:
                            logger.info(f"已处理 {processed}/{len(recent_email_ids)} 封邮件...")
                        
                        status, msg_data = self.imap_conn.fetch(email_id, "(RFC822)")
                        if status != "OK":
                            continue
                        
                        msg = email.message_from_bytes(msg_data[0][1])
                        
                        # 提取邮件信息
                        subject = self.decode_mime_words(msg.get("Subject", ""))
                        from_addr = self.decode_mime_words(msg.get("From", ""))
                        date_str = msg.get("Date", "")
                        
                        # 解析日期
                        try:
                            date_tuple = email.utils.parsedate_tz(date_str)
                            if date_tuple:
                                local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                            else:
                                local_date = datetime.now()
                        except:
                            local_date = datetime.now()
                        
                        # 过滤日期：只保留指定天数内的邮件
                        if local_date < cutoff_date:
                            continue
                        
                        # 从发件人地址中提取邮箱
                        # 格式可能是："Name <email@example.com>" 或 "email@example.com"
                        import re
                        email_match = re.search(r'[\w\.-]+@[\w\.-]+', from_addr)
                        if not email_match:
                            continue
                        
                        sender_email = email_match.group(0).lower()
                        
                        # 检查是否是目标发件人
                        if sender_email not in sender_emails_lower:
                            continue
                        
                        # 获取发件人姓名
                        original_email, sender_name = sender_emails_lower[sender_email]
                        
                        # 获取邮件正文
                        body = self.get_email_body(msg)
                        
                        emails_data.append({
                            'id': email_id.decode(),
                            'from': from_addr,
                            'from_email': original_email,
                            'from_name': sender_name,
                            'subject': subject,
                            'date': local_date,
                            'body': body
                        })
                        
                    except Exception as e:
                        logger.error(f"解析邮件失败: {str(e)}")
                        continue
                
            except Exception as e:
                logger.error(f"搜索邮件时出错: {str(e)}")
                return []
            
            # 按日期排序
            emails_data.sort(key=lambda x: x['date'], reverse=True)
            logger.info(f"总共筛选出 {len(emails_data)} 封符合条件的邮件")
            
            return emails_data
            
        except Exception as e:
            logger.error(f"获取邮件失败: {str(e)}")
            return []
    
    def send_email(self, to_email, subject, body_html):
        """发送邮件"""
        try:
            logger.info(f"正在发送邮件到: {to_email}")
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加HTML内容
            html_part = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 使用SSL连接SMTP服务器
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info("邮件发送成功")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False

