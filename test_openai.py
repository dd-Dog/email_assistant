"""
测试OpenAI连接
"""
import json

print("=" * 70)
print("OpenAI连接测试")
print("=" * 70)

# 读取配置
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    ai_config = config['ai_config']
    print(f"✅ 配置加载成功")
    print(f"   Provider: {ai_config['provider']}")
    print(f"   Model: {ai_config['model']}")
    print(f"   API Key: {ai_config['api_key'][:20]}...{ai_config['api_key'][-10:]}")
except Exception as e:
    print(f"❌ 配置加载失败: {str(e)}")
    exit(1)

# 测试导入
print("\n测试1: 导入openai模块...")
try:
    import openai
    print("✅ openai模块导入成功")
    print(f"   版本: {openai.__version__}")
except ImportError as e:
    print("❌ openai模块未安装")
    print("   请运行: pip install openai")
    exit(1)

# 测试连接
print("\n测试2: 测试API连接...")
try:
    client = openai.OpenAI(api_key=ai_config['api_key'])
    print("✅ OpenAI客户端创建成功")
except Exception as e:
    print(f"❌ 客户端创建失败: {str(e)}")
    exit(1)

# 测试简单调用
print("\n测试3: 测试API调用...")
print("提示：这可能需要几秒钟，请稍候...")
try:
    response = client.chat.completions.create(
        model=ai_config['model'],
        messages=[
            {"role": "user", "content": "你好，请回复：测试成功"}
        ],
        max_tokens=50
    )
    
    result = response.choices[0].message.content
    print(f"✅ API调用成功！")
    print(f"   AI回复: {result}")
    print(f"   使用tokens: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"❌ API调用失败: {str(e)}")
    print("\n可能的原因：")
    print("1. API密钥无效")
    print("2. 网络无法访问OpenAI（需要代理）")
    print("3. 账户余额不足")
    exit(1)

print("\n" + "=" * 70)
print("✅ 所有测试通过！可以使用AI功能")
print("=" * 70)

