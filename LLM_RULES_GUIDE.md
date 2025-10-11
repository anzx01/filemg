# LLM自然语言规则解析功能使用指南

## 概述

本系统现在支持使用自然语言输入规则，通过LLM（大语言模型）自动解析为系统可执行的规则配置。这使得规则配置更加人性化和直观。

## 功能特性

### 1. 自然语言输入
- 支持用自然语言描述规则需求
- 自动识别规则类型和参数
- 智能提取关键词和字段映射关系

### 2. 多种规则类型支持
- **字段映射规则**: 将源字段映射到目标字段
- **日期处理规则**: 处理日期格式转换和合并
- **金额处理规则**: 处理金额格式和计算
- **余额计算规则**: 计算账户余额变化
- **收支分类规则**: 自动分类收入和支出
- **自定义规则**: 支持复杂的业务逻辑

### 3. 银行特定规则
- 支持不同银行的特定业务规则
- 自动识别银行名称和规则类型
- 提供银行特定的参数配置

## 使用方法

### 1. 基本使用

```python
from rule_parser import RuleParser

# 创建规则解析器
parser = RuleParser()

# 输入自然语言规则
rule_text = "将对方行名字段映射到对方户名字段"
parsed_rule = parser.parse_natural_language_rule(rule_text)

print(f"规则类型: {parsed_rule['type']}")
print(f"规则描述: {parsed_rule['description']}")
```

### 2. 使用LLM解析（需要配置API密钥）

```python
# 配置OpenAI API密钥
parser = RuleParser(openai_api_key="your-api-key")

# 或者通过配置文件设置
# 编辑 config/llm_config.json 文件
{
    "openai": {
        "api_key": "your-api-key",
        "model": "gpt-3.5-turbo",
        "temperature": 0.1,
        "max_tokens": 1000
    },
    "enable_llm_parsing": true
}

# 使用LLM解析
rule_text = "将对方行名字段映射到对方户名字段，并处理特殊字符"
parsed_rule = parser.parse_natural_language_with_llm(rule_text, "邮储银行")
```

### 3. 批量解析规则

```python
# 批量解析多个规则
rules = [
    "将对方行名字段映射到对方户名字段",
    "处理日期格式，从MM/DD/YYYY转换为YYYY-MM-DD",
    "计算账户余额，每笔交易后更新余额"
]

parsed_rules = parser.batch_parse_natural_language_rules(rules, "测试银行")
```

### 4. 添加规则到系统

```python
# 直接添加规则到系统
rule = parser.add_rule_from_natural_language(
    "将交易金额字段保留两位小数", 
    "工商银行"
)
```

## 规则示例

### 字段映射规则
```
"将对方行名字段映射到对方户名字段"
"将交易金额字段映射到标准金额字段"
"将交易时间字段映射到交易日期字段"
```

### 日期处理规则
```
"将日期格式从MM/DD/YYYY转换为YYYY-MM-DD"
"从第二行获取日期范围，与月日数据合并"
"将交易时间格式从YYYY-MM-DD转换为YYYY年MM月DD日"
```

### 金额处理规则
```
"将交易金额字段保留两位小数"
"处理金额格式，添加千分位分隔符"
"将金额从元转换为分"
```

### 余额计算规则
```
"计算每笔交易后的账户余额"
"根据借贷标志计算余额变化"
"累计计算账户余额"
```

### 收支分类规则
```
"根据交易类型自动分类为收入或支出"
"根据交易描述自动分类交易类型"
"根据金额正负号分类收支"
```

### 银行特定规则
```
"邮储银行 - 将导入文件中对方行名的记录记入导出文件的对方户名记录"
"北京银行 - 从第二行获取日期范围，与月日数据合并"
"工商银行 - 将交易金额字段映射到标准金额字段，并保留两位小数"
```

## 配置说明

### LLM配置文件 (config/llm_config.json)

```json
{
    "openai": {
        "api_key": "your-openai-api-key",
        "model": "gpt-3.5-turbo",
        "temperature": 0.1,
        "max_tokens": 1000
    },
    "fallback_to_traditional": true,
    "enable_llm_parsing": true
}
```

### 配置参数说明

- `api_key`: OpenAI API密钥（必需）
- `model`: 使用的模型名称（默认: gpt-3.5-turbo）
- `temperature`: 生成文本的随机性（0-1，默认: 0.1）
- `max_tokens`: 最大生成token数（默认: 1000）
- `fallback_to_traditional`: LLM失败时是否回退到传统解析（默认: true）
- `enable_llm_parsing`: 是否启用LLM解析功能（默认: true）

## 运行演示

### 1. 基本功能测试
```bash
python test_llm_rule_parser.py
```

### 2. 完整功能演示
```bash
python demo_llm_rules.py
```

### 3. 交互式界面
```bash
python llm_rule_ui.py
```

## 注意事项

1. **API密钥**: 使用LLM功能需要配置OpenAI API密钥
2. **网络连接**: LLM解析需要网络连接
3. **费用**: 使用OpenAI API会产生费用
4. **回退机制**: 如果LLM解析失败，系统会自动回退到传统解析方法
5. **规则验证**: 建议在添加规则后验证其正确性

## 故障排除

### 1. LLM功能未启用
```
WARNING: 未提供OpenAI API密钥或LLM功能被禁用，将使用传统规则解析方法
```
**解决方案**: 配置OpenAI API密钥或检查配置文件

### 2. API调用失败
```
ERROR: LLM解析失败: API调用失败
```
**解决方案**: 检查网络连接和API密钥有效性

### 3. JSON解析错误
```
ERROR: LLM响应JSON解析失败
```
**解决方案**: 系统会自动回退到传统解析方法

## 扩展功能

### 1. 自定义规则类型
可以在 `rule_parser.py` 中添加新的规则类型解析逻辑

### 2. 自定义提示词
可以修改 `_build_llm_prompt` 方法来自定义LLM提示词

### 3. 规则验证
可以添加规则验证逻辑来确保解析结果的正确性

## 技术支持

如有问题或建议，请联系开发团队或查看相关文档。

