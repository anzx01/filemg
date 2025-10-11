# DeepSeek API 配置指南

## 概述
本项目已成功配置支持DeepSeek API，可以从`.env`文件读取API密钥和配置信息。

## 配置步骤

### 1. 环境变量配置
在项目根目录创建或修改`.env`文件，添加以下配置：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# 其他配置
DEBUG=True
```

### 2. 代码修改
已对`rule_parser.py`进行以下修改：

1. **导入更新**：
   - 添加了`from dotenv import load_dotenv`
   - 更新为`from openai import OpenAI`（支持新版本OpenAI API）

2. **环境变量加载**：
   - 在初始化时加载多个`.env`文件位置
   - 支持从环境变量读取DeepSeek配置

3. **API客户端初始化**：
   - 使用新的OpenAI客户端初始化方式
   - 支持自定义base_url（DeepSeek API地址）

4. **LLM调用更新**：
   - 使用`self.openai_client.chat.completions.create()`
   - 支持markdown代码块响应解析

### 3. 配置优先级
API配置按以下优先级加载：
1. 构造函数参数
2. 配置文件中的设置
3. 环境变量（DEEPSEEK_API_KEY等）
4. 默认配置

### 4. 测试验证
运行测试脚本验证配置：

```bash
python test_env_config.py
```

## 功能特性

### 支持的API提供商
- ✅ DeepSeek API
- ✅ OpenAI API
- ✅ 其他兼容OpenAI格式的API

### 自动配置
- 自动从`.env`文件读取API密钥
- 自动设置正确的API端点
- 自动选择适当的模型

### 错误处理
- API调用失败时自动回退到传统规则解析
- 详细的错误日志记录
- 优雅的降级处理

## 使用示例

```python
from rule_parser import RuleParser

# 自动从.env文件读取配置
parser = RuleParser()

# 使用LLM解析规则
rule = "从第二行获取日期范围，与月日数据合并，存入合并文件标准字段交易日期"
result = parser.parse_natural_language_with_llm(rule, "北京银行")
print(result)
```

## 注意事项

1. 确保`.env`文件中的API密钥格式正确
2. 检查网络连接和API配额
3. 如果API调用失败，系统会自动回退到传统解析方法
4. 建议在生产环境中使用环境变量而不是硬编码API密钥

## 故障排除

### 常见问题
1. **401 Unauthorized**: 检查API密钥是否正确
2. **JSON解析错误**: 已修复markdown代码块解析问题
3. **环境变量未加载**: 确保`.env`文件在正确位置

### 调试方法
1. 运行`test_env_config.py`检查配置
2. 查看日志输出了解详细错误信息
3. 检查网络连接和API服务状态

