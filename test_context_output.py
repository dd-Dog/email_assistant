"""
测试：查看AI实际接收到的上下文信息
"""
from context_builder import ContextBuilder

# 初始化
context_builder = ContextBuilder()

# 测试邮件
test_email = {
    'from_email': 'chenqi@flyscale.cn',
    'from_name': '陈琦',
    'subject': '回复: C52B飞图遗留问题请本周解决',
    'body': '''客户反馈测试结果，仍有12个问题待解决。请查看附件以获取详细信息。'''
}

print("=" * 70)
print("测试：AI实际接收到的上下文")
print("=" * 70)
print()

# 构建上下文
context_data = context_builder.build_context_for_email(test_email)

# 格式化为AI提示词
formatted_context = context_builder.format_context_for_prompt(context_data)

print("【AI接收到的完整上下文】")
print("-" * 70)
print(formatted_context)
print("-" * 70)
print()

# 检查关键信息
print("【上下文检查】")
checks = {
    '✓ 公司信息': '飞思卡尔' in formatted_context or '公司' in formatted_context,
    '✓ 业务领域': '业务' in formatted_context or '软件' in formatted_context,
    '✓ 部门信息': '部门' in formatted_context or '研发部' in formatted_context,
    '✓ 人员信息': '陈琦' in formatted_context,
    '✓ 项目信息': 'G20' in formatted_context or '项目' in formatted_context
}

for name, result in checks.items():
    status = "YES" if result else "NO"
    print(f"{name}: {status}")

print()
print(f"上下文总长度: {len(formatted_context)} 字符")

