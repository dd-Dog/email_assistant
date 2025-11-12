"""
AI分析器模块 - V4.0
集成OpenAI和Gemini，提供智能邮件分析
"""
import logging
import json
import time
from typing import Dict, List, Optional
from ai_cache import AICache

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI邮件分析器（带缓存）"""
    
    def __init__(self, config):
        """初始化AI分析器
        
        Args:
            config: AI配置字典
        """
        self.enabled = config.get('enabled', False)
        self.provider = config.get('provider', 'openai')
        self.api_key = config.get('api_key', '')
        self.model = config.get('model', 'gpt-4o-mini')
        self.enable_summary = config.get('enable_summary', True)
        self.enable_priority = config.get('enable_priority', True)
        self.enable_action_items = config.get('enable_action_items', True)
        self.max_tokens = config.get('max_tokens', 500)
        self.temperature = config.get('temperature', 0.3)
        
        self.client = None
        self.cache = AICache()  # 初始化缓存
        self.api_calls = 0  # API调用计数
        self.cache_hits = 0  # 缓存命中计数
        
        if self.enabled and self.api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """初始化AI客户端"""
        try:
            if self.provider == 'openai':
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info(f"✅ OpenAI客户端初始化成功 (模型: {self.model})")
            elif self.provider == 'gemini':
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model)
                logger.info(f"✅ Gemini客户端初始化成功 (模型: {self.model})")
            else:
                logger.error(f"不支持的AI提供商: {self.provider}")
                self.enabled = False
        except Exception as e:
            logger.error(f"AI客户端初始化失败: {str(e)}")
            self.enabled = False
    
    def is_available(self):
        """检查AI功能是否可用"""
        return self.enabled and self.client is not None
    
    def analyze_email(self, email_item, sender_type='normal'):
        """分析单封邮件（带缓存和类型识别）
        
        Args:
            email_item: 邮件数据字典
            sender_type: 发件人类型 (normal/customer/supplier)
            
        Returns:
            包含AI分析结果的字典
        """
        if not self.is_available():
            return None
        
        try:
            email_id = email_item.get('id', '')
            subject = email_item.get('subject', '')
            body = email_item.get('body', '')
            sender_name = email_item.get('from_name', '')
            
            # 先查缓存
            cached_analysis = self.cache.get(email_id, subject, body)
            if cached_analysis:
                self.cache_hits += 1
                logger.info(f"        → 使用缓存 ✓")
                return cached_analysis
            
            # 缓存未命中，调用AI
            self.api_calls += 1
            
            # 根据发件人类型显示不同的提示
            if sender_type == 'customer':
                logger.info(f"        → 调用AI API (客户需求分析)...")
            elif sender_type == 'supplier':
                logger.info(f"        → 调用AI API (供应商邮件分析)...")
            else:
                logger.info(f"        → 调用AI API...")
            
            # 构建提示词（传入类型）
            prompt = self._build_prompt(sender_name, subject, body, sender_type)
            
            # 调用AI
            if self.provider == 'openai':
                result = self._call_openai(prompt)
            elif self.provider == 'gemini':
                result = self._call_gemini(prompt)
            else:
                return None
            
            # 解析结果
            logger.info(f"        → AI响应成功 ✓")
            analysis = self._parse_result(result)
            
            # 保存到缓存
            self.cache.set(email_id, subject, body, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            return None
    
    def _build_prompt(self, sender_name, subject, body, sender_type='normal'):
        """构建AI分析提示词
        
        Args:
            sender_name: 发件人姓名
            subject: 邮件主题
            body: 邮件内容
            sender_type: 发件人类型 (normal/customer/supplier)
        """
        
        # 客户邮件特殊分析
        if sender_type == 'customer':
            prompt = f"""你是一个专业的技术需求分析师，请分析客户的需求邮件。

客户: {sender_name}
主题: {subject}
内容:
{body[:1000]}

请按照以下JSON格式返回分析结果：
{{
  "summary": "需求简述（1-2句话）",
  "priority": "high/medium/low",
  "urgency": "urgent/normal/low",
  "feasibility": "技术可行性评估（简短）",
  "implementation": "实现方法建议（关键点，2-3条）",
  "suggestions": "简洁建议（1-2句话）",
  "action_items": ["需要执行的行动"],
  "deadline": "截止时间（如果有）",
  "tags": ["需求类型", "涉及模块"]
}}

注意：
1. 重点分析技术可行性和实现方法
2. 建议要简洁，只说关键点
3. 识别是新功能、bug修复还是改进
4. 只返回JSON，不要其他内容
"""
        # 供应商邮件特殊分析  
        elif sender_type == 'supplier':
            prompt = f"""你是一个专业的供应链管理助手，请分析供应商邮件。

供应商: {sender_name}
主题: {subject}
内容:
{body[:1000]}

请按照以下JSON格式返回分析结果：
{{
  "summary": "简述（1-2句话）",
  "priority": "high/medium/low",
  "urgency": "urgent/normal/low",
  "response_needed": "是否需要回复（是/否）",
  "action_items": ["需要执行的行动"],
  "key_info": "关键信息（简短）",
  "deadline": "截止时间（如果有）",
  "tags": ["邮件类型"]
}}

注意：
1. 识别是技术支持、交付信息还是商务沟通
2. 提取关键时间节点
3. 判断是否需要及时回复
4. 只返回JSON，不要其他内容
"""
        # 普通邮件分析
        else:
            prompt = f"""你是一个专业的邮件助手，请分析以下邮件并提供结构化的分析结果。

发件人: {sender_name}
主题: {subject}
内容:
{body[:1000]}

请按照以下JSON格式返回分析结果：
{{
  "summary": "3-5句话的简洁摘要",
  "priority": "high/medium/low",
  "urgency": "urgent/normal/low",
  "action_items": ["需要执行的行动1", "行动2"],
  "key_points": ["要点1", "要点2"],
  "deadline": "截止时间（如果有）",
  "tags": ["标签1", "标签2"]
}}

注意：
1. summary要简洁清晰，突出重点
2. priority基于重要性判断
3. urgency基于时间紧迫性判断
4. action_items提取需要做的事情
5. 只返回JSON，不要其他内容
"""
        return prompt
    
    def _call_openai(self, prompt):
        """调用OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的邮件分析助手，擅长提取关键信息和生成摘要。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}")
            raise
    
    def _call_gemini(self, prompt):
        """调用Gemini API"""
        try:
            response = self.client.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': self.max_tokens,
                    'temperature': self.temperature,
                }
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API调用失败: {str(e)}")
            raise
    
    def _parse_result(self, result_text):
        """解析AI返回结果"""
        try:
            # 尝试解析JSON
            result = json.loads(result_text)
            return result
        except json.JSONDecodeError:
            # 如果不是标准JSON，尝试提取
            logger.warning("AI返回结果不是标准JSON，使用默认值")
            return {
                'summary': result_text[:200],
                'priority': 'medium',
                'urgency': 'normal',
                'action_items': [],
                'key_points': [],
                'deadline': None,
                'tags': []
            }
    
    def analyze_emails_batch(self, emails, sender_type_map=None):
        """批量分析邮件（支持不同类型）
        
        Args:
            emails: 邮件列表
            sender_type_map: 发件人类型映射 {email: type}
            
        Returns:
            带有AI分析的邮件列表
        """
        if not self.is_available():
            logger.warning("AI功能未启用，跳过AI分析")
            return emails
        
        logger.info(f"开始AI分析 {len(emails)} 封邮件...")
        logger.info(f"提示：AI分析需要一些时间，请耐心等待...")
        
        analyzed_emails = []
        success_count = 0
        
        for i, email_item in enumerate(emails, 1):
            try:
                # 更详细的进度显示
                subject = email_item.get('subject', 'unknown')[:30]
                logger.info(f"  [{i}/{len(emails)}] 正在分析: {subject}")
                
                # 确定发件人类型
                sender_email = email_item.get('from_email', '')
                sender_type = 'normal'
                if sender_type_map:
                    sender_type = sender_type_map.get(sender_email, 'normal')
                
                # 调用AI分析（传入类型）
                analysis = self.analyze_email(email_item, sender_type)
                
                if analysis:
                    email_item['ai_analysis'] = analysis
                    success_count += 1
                else:
                    email_item['ai_analysis'] = None
                
                analyzed_emails.append(email_item)
                
                # 添加延迟，避免API限流
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"分析第{i}封邮件失败: {str(e)}")
                email_item['ai_analysis'] = None
                analyzed_emails.append(email_item)
                continue
        
        logger.info(f"✅ AI分析完成: {success_count}/{len(emails)} 封成功")
        logger.info(f"   API调用: {self.api_calls} 次 | 缓存命中: {self.cache_hits} 次")
        
        # 显示成本
        if self.api_calls > 0:
            actual_cost = self.get_cost_estimate(self.api_calls)
            logger.info(f"   预估成本: ${actual_cost:.4f}")
        
        return analyzed_emails
    
    def get_cost_estimate(self, email_count, avg_tokens=800):
        """估算成本
        
        Args:
            email_count: 邮件数量
            avg_tokens: 平均每封邮件的token数
            
        Returns:
            预估成本（美元）
        """
        if self.provider == 'openai':
            if 'gpt-4' in self.model.lower():
                # GPT-4: 输入$0.03/1K, 输出$0.06/1K
                input_cost = (email_count * avg_tokens / 1000) * 0.03
                output_cost = (email_count * self.max_tokens / 1000) * 0.06
                return input_cost + output_cost
            else:
                # GPT-3.5或gpt-4o-mini: 便宜很多
                return (email_count * (avg_tokens + self.max_tokens) / 1000) * 0.001
        elif self.provider == 'gemini':
            # Gemini Pro: 更便宜
            return (email_count * (avg_tokens + self.max_tokens) / 1000) * 0.0005
        
        return 0.0

