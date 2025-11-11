# V4.0 AI智能分析 - 快速上手

## 🤖 新功能

### AI能力
- 📝 **智能摘要** - AI自动总结邮件重点
- 🎯 **优先级识别** - 高/中/低优先级自动判断
- ⏰ **紧急度检测** - 紧急/普通/不急
- ✅ **行动项提取** - 自动提取需要做的事情
- 🏷️ **智能标签** - 自动分类标记

### 报告增强
- 🔴 高优先级邮件优先显示
- 💡 AI摘要替代原始内容
- ✓ 行动项清单
- 📅 截止时间提醒

## 🚀 快速开始

### 1. 安装AI依赖

```bash
pip install openai google-generativeai tiktoken
```

或运行：
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `config.json`，添加AI配置：

```json
{
  "ai_config": {
    "enabled": true,                    // 启用AI
    "provider": "openai",               // 或 "gemini"
    "api_key": "sk-xxx",                // 您的API密钥
    "model": "gpt-4o-mini",             // 推荐：性价比高
    "enable_summary": true,             // 启用摘要
    "enable_priority": true,            // 启用优先级
    "enable_action_items": true,        // 启用行动项
    "max_tokens": 500,
    "temperature": 0.3
  }
}
```

### 3. 运行AI版本

```bash
python main_v4.py
```

或双击 `run_v4.bat`

## 🔑 获取API密钥

### OpenAI（推荐）
1. 访问：https://platform.openai.com/
2. 注册并登录
3. API Keys → Create new secret key
4. 复制密钥到配置文件

**推荐模型：**
- `gpt-4o-mini` - 性价比最高，约$0.15/1M tokens
- `gpt-4o` - 质量最好，约$2.5/1M tokens

### Google Gemini（备选）
1. 访问：https://ai.google.dev/
2. Get API Key
3. 配置：`"provider": "gemini"`
4. 模型：`gemini-pro`

## 💰 成本说明

### 每天运行成本估算

**假设场景：**
- 每天20封邮件
- 每封约800 tokens（输入）+ 500 tokens（输出）

**成本对比：**

| 模型 | 单次成本 | 月成本(30天) |
|------|---------|-------------|
| gpt-4o-mini | $0.003 | **$0.09** ⭐ |
| gpt-4o | $0.033 | $0.99 |
| gemini-pro | $0.001 | **$0.03** ⭐⭐ |

**推荐：gpt-4o-mini 或 gemini-pro**

## 📊 报告格式对比

### V3.0（基础版）
```
[陈琦](chenqi@flyscale.cn) 3封
  2025-11-11:
    09:51 889  8088 遗留的两个问题
      王怡轩在现场反馈现在遗留2个问题： | 1. 889 录音声音小。
```

### V4.0（AI版）
```
[陈琦](chenqi@flyscale.cn) 3封
  2025-11-11:
    09:51 889  8088 遗留的两个问题 🔴
      💡 项目存在2个遗留bug需要解决：录音音量问题和通话质量问题
      ✓ 1. 检查889设备的录音音量设置
      ✓ 2. 联系王怡轩确认详细情况
      ✓ 3. 今天内给出解决方案
```

## ⚙️ AI功能开关

### 完全启用
```json
{
  "ai_config": {
    "enabled": true,
    "enable_summary": true,
    "enable_priority": true,
    "enable_action_items": true
  }
}
```

### 部分启用（省钱）
```json
{
  "ai_config": {
    "enabled": true,
    "enable_summary": true,        // 只要摘要
    "enable_priority": false,      // 不要优先级
    "enable_action_items": false   // 不要行动项
  }
}
```

### 完全关闭（回到V3.0）
```json
{
  "ai_config": {
    "enabled": false               // 关闭AI，使用V3.0模式
  }
}
```

或直接运行：
```bash
python main.py  # V3.0版本
```

## 🎯 使用建议

### 初期
1. 先用 `gpt-4o-mini` 测试几天
2. 观察效果和成本
3. 根据需要调整

### 日常使用
- 设置定时任务自动运行
- AI分析自动完成
- 查看reports/文件夹的报告

### 成本控制
- 只对重要邮件启用AI（领导和项目经理）
- 员工邮件可以关闭AI
- 使用便宜的模型

## 🔧 故障排除

### API密钥错误
```
ERROR: OpenAI API调用失败: Incorrect API key
```
→ 检查API密钥是否正确

### 网络问题
```
ERROR: AI客户端初始化失败
```
→ 检查网络连接，可能需要代理

### 成本过高
→ 调低 `max_tokens`
→ 关闭部分功能
→ 换用更便宜的模型

## 💡 最佳实践

1. **首次运行** - 用少量邮件测试
2. **监控成本** - 观察API使用情况
3. **调整配置** - 根据效果优化
4. **备用方案** - 可以随时关闭AI，回到V3.0

---

**准备好体验AI的强大能力了吗？** 🚀

