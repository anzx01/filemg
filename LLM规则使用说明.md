# LLM规则功能使用说明

## 概述

本系统新增了基于DeepSeek API的自然语言规则解析功能，允许用户使用自然语言描述银行数据处理规则，系统会自动将其转换为标准的JSON格式规则。

## 功能特性

- 🤖 **智能解析**: 使用DeepSeek LLM将自然语言转换为标准JSON规则
- 📝 **自然语言输入**: 支持中文自然语言描述规则
- 🏦 **银行特定规则**: 支持不同银行的特定业务规则
- 💾 **自动保存**: 解析后的规则自动保存为JSON文件
- 🔄 **实时验证**: 解析过程中实时验证规则格式
- 🎯 **多种规则类型**: 支持字段映射、日期范围、余额处理、收支分类等

## 安装配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

在项目根目录创建 `config.env` 文件：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your_actual_api_key_here

# 其他配置
DEBUG=True
```

**注意**: 请将 `your_actual_api_key_here` 替换为您的实际DeepSeek API密钥。

## 使用方法

### 1. 启动特殊规则配置界面

```python
from special_rules_ui import SpecialRulesUI

# 创建并运行界面
app = SpecialRulesUI()
app.run()
```

### 2. 使用LLM解析规则

1. **选择银行**: 在"银行"下拉框中选择目标银行
2. **输入规则**: 在"自然语言描述"文本框中输入规则描述
3. **LLM解析**: 点击"🤖 LLM智能解析"按钮
4. **查看结果**: 系统会显示解析后的规则参数
5. **保存规则**: 点击"保存规则"按钮保存到系统

### 3. 规则描述示例

#### 日期范围规则
```
北京银行日期范围从2024-01-01至2024-12-31
```

#### 字段映射规则
```
工商银行将'交易日期'字段映射到'日期'字段
```

#### 余额处理规则
```
华夏银行余额增加1000元
```

#### 收支分类规则
```
招商银行根据交易金额正负号分类收支（正数为收入，负数为支出）
```

#### 分页符规则
```
长安银行分页符每1000行
```

## 支持的规则类型

| 规则类型 | 描述 | 示例 |
|---------|------|------|
| `field_mapping` | 字段映射 | 将源字段映射到目标字段 |
| `date_range` | 日期范围 | 指定日期范围过滤 |
| `balance_processing` | 余额处理 | 对余额进行加减操作 |
| `income_expense` | 收支分类 | 根据条件分类收入支出 |
| `page_break` | 分页符处理 | 设置分页条件 |
| `custom` | 自定义规则 | 其他自定义处理逻辑 |

## API调用示例

### 直接使用LLM解析器

```python
from llm_api import RuleLLMParser

# 创建解析器
parser = RuleLLMParser()

# 解析规则
result = parser.parse_natural_language_rule(
    "北京银行日期范围从2024-01-01至2024-12-31",
    "北京银行"
)

if result.get("success"):
    print(f"规则ID: {result['id']}")
    print(f"规则类型: {result['type']}")
    print(f"参数: {result['parameters']}")
else:
    print(f"解析失败: {result['error']}")
```

### 使用规则管理器

```python
from special_rules import SpecialRulesManager

# 创建管理器
manager = SpecialRulesManager()

# 添加LLM规则
result = manager.add_llm_rule(
    "工商银行余额增加1000元",
    "工商银行"
)

if result["success"]:
    print("规则添加成功")
else:
    print(f"规则添加失败: {result['error']}")
```

## 测试功能

运行测试脚本验证功能：

```bash
python test_llm_rules.py
```

测试包括：
- API连接测试
- 规则解析测试
- 规则管理器测试
- UI组件测试

## 故障排除

### 1. API连接失败

**问题**: 提示"API连接测试失败"

**解决方案**:
- 检查 `config.env` 文件是否存在
- 确认API密钥是否正确设置
- 检查网络连接是否正常
- 验证API密钥是否有效

### 2. 规则解析失败

**问题**: LLM解析返回错误

**解决方案**:
- 检查规则描述是否清晰明确
- 确认银行名称是否正确
- 查看错误日志获取详细信息
- 尝试简化规则描述

### 3. 规则验证失败

**问题**: 解析成功但验证失败

**解决方案**:
- 检查规则参数是否完整
- 确认规则类型是否支持
- 查看验证错误信息
- 手动调整规则参数

## 注意事项

1. **API密钥安全**: 请妥善保管您的DeepSeek API密钥，不要将其提交到版本控制系统
2. **网络要求**: 需要稳定的网络连接才能正常使用LLM功能
3. **规则描述**: 建议使用清晰、具体的自然语言描述规则
4. **银行名称**: 确保银行名称与系统中预定义的银行列表一致
5. **规则验证**: 系统会自动验证解析后的规则格式，确保规则正确性

## 更新日志

### v1.0.0 (2025-01-27)
- 初始版本发布
- 支持DeepSeek API集成
- 实现自然语言规则解析
- 添加规则验证和保存功能
- 提供图形化用户界面

## 技术支持

如有问题或建议，请联系开发团队或查看项目文档。


