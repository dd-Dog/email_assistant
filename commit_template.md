# Git提交信息模板

## 推荐格式（英文）

### 功能类
```bash
feat: add AI analysis feature
feat: optimize report format
feat: support multiple recipients
```

### 修复类
```bash
fix: resolve IMAP connection timeout
fix: fix email encoding issue
fix: correct priority detection
```

### 文档类
```bash
docs: update README
docs: add API usage guide
docs: improve installation steps
```

### 配置类
```bash
config: update email settings
config: enable AI features
config: adjust time ranges
```

### 优化类
```bash
perf: improve email fetching speed
perf: reduce memory usage
perf: optimize AI cache
```

## 常用提交信息

### 日常更新
```bash
git commit -m "update: daily improvements"
```

### 测试
```bash
git commit -m "test: verify AI functionality"
```

### 重构
```bash
git commit -m "refactor: restructure email analyzer"
```

## 💡 提交规范

### 格式
```
类型: 简短描述（不超过50字符）

详细说明（可选）
- 改动点1
- 改动点2
```

### 类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | feat: add AI analysis |
| fix | 修复bug | fix: resolve timeout |
| docs | 文档 | docs: update guide |
| style | 格式 | style: format code |
| refactor | 重构 | refactor: optimize logic |
| perf | 性能 | perf: improve speed |
| test | 测试 | test: add unit tests |
| chore | 杂项 | chore: update deps |

## 🎯 使用建议

1. **推荐用英文** - 避免乱码，更通用
2. **描述要清晰** - 让未来的自己看懂
3. **遵循规范** - 便于查找和管理

## 📝 在Cursor中提交

1. 打开 Source Control (`Ctrl+Shift+G`)
2. 在Message框输入英文信息
3. 点击 ✓ 提交
4. 点击同步按钮推送

这样就不会有乱码问题！

