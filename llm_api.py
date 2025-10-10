"""
LLM API调用模块

该模块负责与DeepSeek API进行交互，将自然语言规则转换为标准JSON格式。

作者: AI助手
创建时间: 2025-01-27
"""

import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepSeekAPI:
    """DeepSeek API调用类"""
    
    def __init__(self, api_key: str = None):
        """初始化DeepSeek API客户端
        
        Args:
            api_key: API密钥，如果为None则从环境变量读取
        """
        self.api_key = api_key or self._load_api_key()
        self.base_url = "https://api.deepseek.com/chat/completions"
        self.model = "deepseek-chat"
        
        if not self.api_key:
            raise ValueError("未找到DeepSeek API密钥，请在config.env文件中设置DEEPSEEK_API_KEY")
    
    def _load_api_key(self) -> Optional[str]:
        """从配置文件加载API密钥"""
        try:
            # 尝试从config.env文件读取
            if os.path.exists("config.env"):
                with open("config.env", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("DEEPSEEK_API_KEY="):
                            return line.split("=", 1)[1].strip()
            
            # 尝试从环境变量读取
            return os.getenv("DEEPSEEK_API_KEY")
        except Exception as e:
            logger.error(f"加载API密钥失败: {str(e)}")
            return None
    
    def call_api(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """调用DeepSeek API
        
        Args:
            messages: 消息列表
            temperature: 温度参数，控制生成文本的随机性
            
        Returns:
            Dict: API响应结果
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "temperature": temperature
            }
            
            logger.info(f"调用DeepSeek API，消息数量: {len(messages)}")
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info("DeepSeek API调用成功")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API调用失败: {str(e)}")
            return {
                "error": f"API调用失败: {str(e)}",
                "success": False
            }
        except Exception as e:
            logger.error(f"处理API响应失败: {str(e)}")
            return {
                "error": f"处理API响应失败: {str(e)}",
                "success": False
            }
    
    def parse_rule_with_llm(self, natural_language_rule: str, bank_name: str = None) -> Dict[str, Any]:
        """使用LLM解析自然语言规则
        
        Args:
            natural_language_rule: 自然语言规则描述
            bank_name: 银行名称
            
        Returns:
            Dict: 解析后的规则JSON
        """
        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt()
            
            # 构建用户提示词
            user_prompt = self._build_user_prompt(natural_language_rule, bank_name)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 调用API
            response = self.call_api(messages)
            
            if response.get("error"):
                return {
                    "success": False,
                    "error": response["error"],
                    "rule": None
                }
            
            # 解析响应
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not content:
                return {
                    "success": False,
                    "error": "API返回空内容",
                    "rule": None
                }
            
            # 尝试解析JSON
            try:
                rule_json = json.loads(content)
                
                # 验证规则格式
                if self._validate_rule_format(rule_json):
                    return {
                        "success": True,
                        "rule": rule_json,
                        "raw_response": content
                    }
                else:
                    return {
                        "success": False,
                        "error": "规则格式验证失败",
                        "rule": None,
                        "raw_response": content
                    }
                    
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"JSON解析失败: {str(e)}",
                    "rule": None,
                    "raw_response": content
                }
                
        except Exception as e:
            logger.error(f"解析规则失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "rule": None
            }
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一个专业的银行数据处理规则解析助手。你的任务是将自然语言描述的银行数据处理规则转换为标准的JSON格式。

规则类型包括：
1. field_mapping - 字段映射规则
2. date_range - 日期范围处理规则
3. balance_processing - 余额处理规则
4. income_expense - 收支分类规则
5. page_break - 分页符处理规则
6. custom - 自定义规则

请严格按照以下JSON格式返回规则：

{
    "id": "rule_unique_id",
    "type": "规则类型",
    "bank_name": "银行名称",
    "description": "规则描述",
    "status": "active",
    "created_at": "2025-01-27T10:00:00",
    "parameters": {
        "具体参数": "根据规则类型而定"
    }
}

字段映射规则参数示例：
{
    "source_field": "源字段名",
    "target_field": "目标字段名",
    "transform_type": "转换类型",
    "transform_params": {}
}

日期范围规则参数示例：
{
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "date_field": "日期字段名"
}

余额处理规则参数示例：
{
    "balance_field": "余额字段名",
    "operation": "add/subtract",
    "amount": 1000
}

收支分类规则参数示例：
{
    "amount_field": "金额字段名",
    "sign_field": "符号字段名",
    "income_condition": "收入条件",
    "expense_condition": "支出条件"
}

分页符规则参数示例：
{
    "break_condition": "分页条件",
    "break_field": "分页字段名",
    "break_value": "分页值"
}

请确保返回的JSON格式正确，参数完整，规则描述清晰。"""
    
    def _build_user_prompt(self, natural_language_rule: str, bank_name: str = None) -> str:
        """构建用户提示词"""
        prompt = f"请将以下自然语言规则转换为标准JSON格式：\n\n"
        prompt += f"规则描述：{natural_language_rule}\n\n"
        
        if bank_name:
            prompt += f"银行名称：{bank_name}\n\n"
        
        prompt += "请返回完整的JSON格式规则，不要包含其他解释文字。"
        
        return prompt
    
    def _validate_rule_format(self, rule: Dict[str, Any]) -> bool:
        """验证规则格式是否正确"""
        required_fields = ["id", "type", "description", "status", "parameters"]
        
        for field in required_fields:
            if field not in rule:
                logger.error(f"规则缺少必需字段: {field}")
                return False
        
        # 验证规则类型
        valid_types = ["field_mapping", "date_range", "balance_processing", 
                      "income_expense", "page_break", "custom"]
        
        if rule.get("type") not in valid_types:
            logger.error(f"无效的规则类型: {rule.get('type')}")
            return False
        
        # 验证状态
        if rule.get("status") not in ["active", "inactive"]:
            logger.error(f"无效的规则状态: {rule.get('status')}")
            return False
        
        return True
    
    def generate_rule_id(self, bank_name: str = None, rule_type: str = None) -> str:
        """生成规则ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bank_prefix = bank_name[:2] if bank_name else "RULE"
        type_prefix = rule_type[:2] if rule_type else "XX"
        return f"{bank_prefix}_{type_prefix}_{timestamp}"
    
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            messages = [
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "请回复'连接成功'"}
            ]
            
            response = self.call_api(messages)
            return not response.get("error")
            
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False


class RuleLLMParser:
    """规则LLM解析器"""
    
    def __init__(self, api_key: str = None):
        """初始化规则LLM解析器
        
        Args:
            api_key: API密钥
        """
        self.api = DeepSeekAPI(api_key)
    
    def parse_natural_language_rule(self, rule_description: str, bank_name: str = None) -> Dict[str, Any]:
        """解析自然语言规则
        
        Args:
            rule_description: 自然语言规则描述
            bank_name: 银行名称
            
        Returns:
            Dict: 解析结果
        """
        try:
            logger.info(f"开始解析规则: {rule_description}")
            
            # 使用LLM解析规则
            result = self.api.parse_rule_with_llm(rule_description, bank_name)
            
            if result["success"]:
                rule = result["rule"]
                
                # 确保规则ID存在
                if not rule.get("id"):
                    rule["id"] = self.api.generate_rule_id(bank_name, rule.get("type"))
                
                # 确保创建时间存在
                if not rule.get("created_at"):
                    rule["created_at"] = datetime.now().isoformat()
                
                # 确保银行名称存在
                if bank_name and not rule.get("bank_name"):
                    rule["bank_name"] = bank_name
                
                logger.info(f"规则解析成功: {rule['id']}")
                return rule
            else:
                logger.error(f"规则解析失败: {result['error']}")
                return {
                    "error": result["error"],
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"解析规则时发生错误: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
    
    def batch_parse_rules(self, rules: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """批量解析规则
        
        Args:
            rules: 规则列表，每个规则包含description和bank_name
            
        Returns:
            List[Dict]: 解析结果列表
        """
        results = []
        
        for rule_info in rules:
            description = rule_info.get("description", "")
            bank_name = rule_info.get("bank_name")
            
            result = self.parse_natural_language_rule(description, bank_name)
            results.append(result)
        
        return results


# 测试代码
if __name__ == "__main__":
    # 测试API连接
    print("测试DeepSeek API连接...")
    
    try:
        api = DeepSeekAPI()
        if api.test_connection():
            print("✓ API连接成功")
        else:
            print("✗ API连接失败")
    except Exception as e:
        print(f"✗ API初始化失败: {str(e)}")
    
    # 测试规则解析
    print("\n测试规则解析...")
    
    parser = RuleLLMParser()
    
    test_rules = [
        "北京银行日期范围从2024-01-01至2024-12-31",
        "工商银行余额增加1000元",
        "华夏银行收支分类：收入5000元",
        "长安银行分页符每1000行"
    ]
    
    for rule_desc in test_rules:
        print(f"\n解析规则: {rule_desc}")
        result = parser.parse_natural_language_rule(rule_desc)
        
        if result.get("success"):
            print(f"✓ 解析成功: {result['id']}")
            print(f"  类型: {result.get('type')}")
            print(f"  参数: {json.dumps(result.get('parameters', {}), ensure_ascii=False, indent=2)}")
        else:
            print(f"✗ 解析失败: {result.get('error')}")
    
    print("\n测试完成")


