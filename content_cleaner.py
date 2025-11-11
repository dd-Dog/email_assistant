"""
邮件内容清理模块 - 去除签名等无关信息
"""
import re
import logging

logger = logging.getLogger(__name__)


class ContentCleaner:
    """邮件内容清理器"""
    
    def __init__(self):
        # 常见的签名分隔符
        self.signature_patterns = [
            r'--+\s*$',  # -- 分隔符
            r'_{5,}',     # _____ 下划线
            r'={5,}',     # ===== 等号
            r'\*{5,}',    # ***** 星号
            r'-{3,}',     # --- 短横线
        ]
        
        # 签名常见关键词
        self.signature_keywords = [
            'E-mail', 'Email', 'e-mail', 'email', 'E-Mail',
            'Tel', 'Phone', 'Mobile', '电话', '手机', '座机', '移动电话',
            '公司', 'Company', '有限公司', 'Co.,Ltd', 'Ltd', '股份',
            '地址', 'Address', 'Addr', 'ADD',
            '邮编', '邮政编码', 'Zip', 'Post', 'Postal',
            'QQ', '微信', 'WeChat', 'Skype', 'Wechat',
            '传真', 'Fax', 'FAX',
            '网址', 'Website', 'Web', 'Http', 'www.', 'http://', 'https://',
        ]
        
        # 回复/转发标记
        self.reply_markers = [
            r'^-+\s*原始邮件\s*-+',
            r'^-+\s*Original Message\s*-+',
            r'^-+\s*转发邮件\s*-+',
            r'^-+\s*Forwarded Message\s*-+',
            r'^在.*写道[:：]',
            r'^On.*wrote[:：]',
            r'^发件人[:：]',
            r'^From[:：]',
            r'^发送时间[:：]',
            r'^Sent[:：]',
            r'^收件人[:：]',
            r'^To[:：]',
            r'^主题[:：]',
            r'^Subject[:：]',
            r'^抄送[:：]',
            r'^Cc[:：]',
            r'^>\s*',  # 引用符号
        ]
        
        # HTML标签
        self.html_pattern = re.compile(r'<[^>]+>')
    
    def clean_email_body(self, body):
        """清理邮件正文，去除签名等无关信息（V3.0增强版）
        
        Args:
            body: 原始邮件正文
            
        Returns:
            清理后的正文
        """
        if not body:
            return ""
        
        # 1. 去除HTML标签
        body = self.html_pattern.sub('', body)
        
        # 2. 检测并移除历史对话（最重要）
        body = self.remove_conversation_history(body)
        
        # 3. 按行处理，移除签名
        lines = body.split('\n')
        cleaned_lines = []
        found_signature = False
        
        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()
            
            # 如果已经找到签名，后续内容全部忽略
            if found_signature:
                break
            
            # 跳过空行（但记录）
            if not line:
                if cleaned_lines:  # 不在开头的空行保留
                    cleaned_lines.append('')
                continue
            
            # 检测签名分隔符
            for pattern in self.signature_patterns:
                if re.search(pattern, line):
                    found_signature = True
                    break
            
            if found_signature:
                break
            
            # 检测回复/转发标记
            is_reply_marker = False
            for pattern in self.reply_markers:
                if re.search(pattern, line, re.IGNORECASE):
                    found_signature = True
                    is_reply_marker = True
                    break
            
            if is_reply_marker:
                break
            
            # 检测签名关键词（如果一行中包含2个以上签名关键词，可能是签名）
            keyword_count = sum(1 for keyword in self.signature_keywords if keyword in line)
            if keyword_count >= 2:
                # 检查是否包含联系方式模式
                if self.contains_contact_info(line):
                    found_signature = True
                    break
            
            # 单独的邮箱地址或电话号码也可能是签名
            if self.is_contact_line(line):
                found_signature = True
                break
            
            cleaned_lines.append(line)
        
        # 4. 去除多余的空白
        result = '\n'.join(cleaned_lines)
        result = self.clean_whitespace(result)
        
        return result
    
    def remove_conversation_history(self, text):
        """移除邮件对话历史
        
        当检测到回复/转发标记时，截断后续内容
        """
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # 检测历史对话开始标记
            is_history_start = False
            
            # 中文标记
            if re.search(r'^-+\s*(原始邮件|转发邮件|回复|答复)\s*-+', line_stripped, re.IGNORECASE):
                is_history_start = True
            
            # 英文标记
            if re.search(r'^-+\s*(Original Message|Forwarded Message|Reply|From)\s*-+', line_stripped, re.IGNORECASE):
                is_history_start = True
            
            # "在...写道:" 或 "On...wrote:"
            if re.search(r'^(在.{1,50}写道|On.{1,50}wrote)[：:]', line_stripped):
                is_history_start = True
            
            # 邮件头部字段（连续出现表示是历史记录）
            if re.search(r'^(发件人|From|发送时间|Sent|收件人|To|主题|Subject)[：:]', line_stripped):
                is_history_start = True
            
            if is_history_start:
                # 找到历史记录开始，后续内容全部丢弃
                break
            
            clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    def is_contact_line(self, text):
        """判断是否是单独的联系方式行"""
        # 单独的电话号码
        if re.match(r'^(Tel|电话|手机|Mobile)[：:：\s]*[\d\s\-\+]+$', text, re.IGNORECASE):
            return True
        
        # 单独的邮箱
        if re.match(r'^(E-?mail)[：:：\s]*[\w\.-]+@[\w\.-]+$', text, re.IGNORECASE):
            return True
        
        # 纯数字（可能是电话或邮编）
        if re.match(r'^[\d\s\-\+\(\)]{10,}$', text):
            return True
        
        return False
    
    def contains_contact_info(self, text):
        """检查文本是否包含联系方式信息"""
        # 电话号码模式
        phone_patterns = [
            r'\d{3,4}[-\s]?\d{7,8}',  # 固定电话
            r'1[3-9]\d{9}',            # 手机号
            r'\+86[-\s]?\d+',          # 国际号码
            r'\d{11}',                 # 11位数字（手机号）
        ]
        
        for pattern in phone_patterns:
            if re.search(pattern, text):
                return True
        
        # 邮箱地址（在签名上下文中）
        if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
            # 如果包含E-mail/Email关键词，肯定是签名
            if re.search(r'E-?mail', text, re.IGNORECASE):
                return True
            # 如果一行中有多个@，也可能是签名
            if text.count('@') >= 2:
                return True
        
        # 邮编
        if re.search(r'(邮编|邮政编码|Zip|Post)[：:：\s]*\d{6}', text, re.IGNORECASE):
            return True
        
        # 公司地址（通常很长）
        if re.search(r'(地址|Address)[：:：]', text, re.IGNORECASE) and len(text) > 20:
            return True
        
        return False
    
    def remove_reply_headers(self, text):
        """去除回复/转发标记（已被 remove_conversation_history 替代，保留作为补充）"""
        lines = text.split('\n')
        cleaned = []
        skip_next = 0
        
        for i, line in enumerate(lines):
            if skip_next > 0:
                skip_next -= 1
                continue
            
            line_stripped = line.strip()
            is_header = False
            
            # 检测邮件头部字段
            for pattern in self.reply_markers:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    is_header = True
                    # 如果是"发件人:"这类，后续几行可能也是头部
                    if re.match(r'^(发件人|From|发送时间|Sent)[:：]', line_stripped, re.IGNORECASE):
                        skip_next = 3  # 跳过后续3行（通常是发件人、时间、收件人、主题）
                    break
            
            if not is_header:
                cleaned.append(line)
        
        return '\n'.join(cleaned)
    
    def clean_whitespace(self, text):
        """清理多余的空白字符"""
        # 去除每行首尾空白
        lines = [line.strip() for line in text.split('\n')]
        
        # 去除连续的空行（保留最多1个）
        result = []
        prev_empty = False
        
        for line in lines:
            if not line:
                if not prev_empty:
                    result.append('')
                prev_empty = True
            else:
                result.append(line)
                prev_empty = False
        
        # 去除首尾空行
        while result and not result[0]:
            result.pop(0)
        while result and not result[-1]:
            result.pop()
        
        return '\n'.join(result)
    
    def extract_main_content(self, body):
        """提取邮件的主要内容（更激进的清理）
        
        这个方法会更激进地清理内容，只保留看起来像正文的部分
        """
        cleaned = self.clean_email_body(body)
        
        # 按段落分割
        paragraphs = [p.strip() for p in cleaned.split('\n\n') if p.strip()]
        
        # 过滤掉过短的段落（可能是签名片段）
        main_paragraphs = [p for p in paragraphs if len(p) > 20]
        
        return '\n\n'.join(main_paragraphs)

