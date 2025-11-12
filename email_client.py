import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import ssl
import logging
from content_cleaner import ContentCleaner

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
        self.content_cleaner = ContentCleaner()  # 内容清理器
    
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
            
            logger.info(f"正在获取最近 {days} 天的邮件（将在本地过滤发件人）...")
            
            # 尝试使用SINCE日期搜索（更精确）
            since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
            logger.info(f"尝试使用日期搜索：SINCE {since_date}")
            
            try:
                # 尝试1：标准SINCE格式
                status, messages = self.imap_conn.search(None, f'SINCE {since_date}')
                
                if status == "OK":
                    email_ids = messages[0].split()
                    logger.info(f"✅ 日期搜索成功！找到 {len(email_ids)} 封邮件")
                    recent_email_ids = email_ids
                else:
                    raise Exception("日期搜索不支持，使用备用方案")
                    
            except Exception as e:
                logger.warning(f"日期搜索失败: {str(e)}，使用备用方案（检查最近邮件）")
                
                # 备用方案：获取所有邮件ID，取最近的
                try:
                    status, messages = self.imap_conn.search(None, 'ALL')
                    if status != "OK":
                        logger.error("搜索邮件失败")
                        return []
                    
                    email_ids = messages[0].split()
                    total_emails = len(email_ids)
                    logger.info(f"收件箱中共有 {total_emails} 封邮件，正在筛选...")
                    
                    # 只处理最近的N封邮件（避免处理过多）
                    # 根据检查天数动态调整：3天大约100-150封邮件已经足够
                    max_check = min(150, total_emails)  # V3.0优化：最多检查最近150封
                    recent_email_ids = email_ids[-max_check:] if total_emails > max_check else email_ids
                    
                    logger.info(f"将检查最近 {len(recent_email_ids)} 封邮件（约占收件箱的 {len(recent_email_ids)*100//total_emails}%）")
                except Exception as inner_e:
                    logger.error(f"备用方案也失败: {str(inner_e)}")
                    return []
                
            # 处理邮件
            logger.info(f"开始处理邮件，总共 {len(recent_email_ids)} 封")
            processed = 0
            
            for email_id in recent_email_ids:
                try:
                    processed += 1
                    
                    # 更频繁的进度显示
                    if processed == 1 or processed % 10 == 0 or processed == len(recent_email_ids):
                        logger.info(f"处理进度: {processed}/{len(recent_email_ids)} 封...")
                    
                    # 获取邮件（可能耗时）
                    logger.debug(f"正在获取邮件 #{processed}")
                    status, msg_data = self.imap_conn.fetch(email_id, "(RFC822)")
                    if status != "OK":
                        logger.warning(f"邮件 #{processed} 获取失败")
                        continue
                    
                    logger.debug(f"正在解析邮件 #{processed}")
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # 提取邮件信息
                    subject = self.decode_mime_words(msg.get("Subject", ""))
                    from_addr = self.decode_mime_words(msg.get("From", ""))
                    date_str = msg.get("Date", "")
                    
                    logger.debug(f"邮件 #{processed}: {subject[:30]}")
                    
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
                    
                    # 获取邮件正文（限制大小，避免过大邮件）
                    body = self.get_email_body(msg)
                    
                    # 限制邮件内容大小（避免处理超大邮件）
                    if len(body) > 10000:
                        body = body[:10000] + "\n...(内容过长，已截断)"
                        logger.debug(f"邮件内容过长，已截断: {subject[:30]}")
                    
                    # 清理邮件内容（V3.0新增）
                    body = self.content_cleaner.clean_email_body(body)
                    
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
                    logger.error(f"解析邮件 #{processed} 失败: {str(e)}")
                    continue
            
            logger.info(f"邮件获取循环完成，共处理 {processed} 封")
            
            # 按日期排序
            logger.info(f"正在排序邮件...")
            emails_data.sort(key=lambda x: x['date'], reverse=True)
            logger.info(f"✅ 总共筛选出 {len(emails_data)} 封符合条件的邮件")
            
            return emails_data
            
        except Exception as e:
            logger.error(f"获取邮件失败: {str(e)}")
            return []
    
    def send_email(self, to_email, subject, body_html):
        """发送邮件（V3.0优化版 - 提高送达率）"""
        try:
            logger.info(f"正在发送邮件到: {to_email}")
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加更多邮件头信息，提高送达率
            msg['X-Mailer'] = 'Email Assistant V3.0'
            msg['X-Priority'] = '3'  # 正常优先级
            msg['Importance'] = 'Normal'
            
            # 添加纯文本版本（重要！很多邮箱要求有纯文本备份）
            text_body = f"""
邮件助手每日报告

本邮件为HTML格式，请使用支持HTML的邮件客户端查看。

如果看不到内容，请：
1. 检查是否在垃圾邮件文件夹
2. 将 {self.username} 添加到白名单
3. 使用支持HTML的邮件客户端

报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
邮件助手自动发送
"""
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # 添加HTML内容
            html_part = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 使用SSL连接SMTP服务器
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info("邮件发送成功")
            logger.info(f"提示：如果未收到，请检查垃圾邮件、订阅邮件文件夹")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False
    
    def send_email_text(self, to_email, subject, body_text):
        """发送纯文本邮件（V3.0 - 伪装成普通邮件，避免拦截）"""
        try:
            logger.info(f"正在发送纯文本邮件到: {to_email}")
            
            msg = MIMEText(body_text, 'plain', 'utf-8')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            # 去掉X-Mailer标识，伪装成普通邮件
            # msg['X-Mailer'] = 'Email Assistant V3.0'
            
            # 使用SSL连接SMTP服务器
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info("✅ 纯文本邮件发送成功")
            
            # 添加延迟，避免频繁发送被限制
            import time
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 邮件发送失败: {str(e)}")
            return False

