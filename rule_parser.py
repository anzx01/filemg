"""
规则解析模块 - 自然语言规则解析和银行特定规则处理

该模块负责解析用户输入的自然语言规则，并将其转换为可执行的数据处理规则。
支持多种银行特定的业务规则，如日期范围处理、余额计算、收支分类等。

作者: AI助手
创建时间: 2025-01-27
"""

import re
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleParser:
    """规则解析器类
    
    负责解析自然语言规则，支持多种银行特定的业务规则处理。
    """
    
    def __init__(self):
        """初始化规则解析器"""
        self.rules = []
        self.bank_specific_rules = self._initialize_bank_rules()
        self.keyword_patterns = self._initialize_keyword_patterns()
        
    def _initialize_bank_rules(self) -> Dict[str, Dict]:
        """初始化银行特定规则模板"""
        return {
            "北京银行": {
                "date_range": {
                    "keywords": ["日期范围", "时间范围", "起止日期"],
                    "pattern": r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*至\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
                    "description": "处理北京银行的日期范围规则"
                },
                "balance_calculation": {
                    "keywords": ["余额计算", "余额统计"],
                    "pattern": r"余额\s*([+-]?)\s*(\d+(?:\.\d+)?)",
                    "description": "处理余额计算规则"
                }
            },
            "工商银行": {
                "balance_processing": {
                    "keywords": ["余额处理", "余额转换"],
                    "pattern": r"余额\s*([+-]?)\s*(\d+(?:\.\d+)?)",
                    "description": "处理工商银行余额规则"
                },
                "page_break": {
                    "keywords": ["分页符", "分页处理"],
                    "pattern": r"分页符\s*(\d+)",
                    "description": "处理分页符规则"
                }
            },
            "华夏银行": {
                "income_expense": {
                    "keywords": ["收支分类", "收入支出"],
                    "pattern": r"(收入|支出)\s*(\d+(?:\.\d+)?)",
                    "description": "处理收支分类规则"
                }
            },
            "长安银行": {
                "income_expense": {
                    "keywords": ["收支分类", "收入支出"],
                    "pattern": r"(收入|支出)\s*(\d+(?:\.\d+)?)",
                    "description": "处理收支分类规则"
                }
            }
        }
    
    def _initialize_keyword_patterns(self) -> Dict[str, str]:
        """初始化关键词模式"""
        return {
            "日期": r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
            "金额": r"(\d+(?:\.\d+)?)",
            "银行": r"(北京银行|工商银行|华夏银行|长安银行|建设银行|招商银行|浦发银行|邮储银行|兴业银行|中国银行)",
            "操作": r"(增加|减少|计算|统计|处理|转换|分类)",
            "字段": r"(账户|余额|金额|日期|时间|描述|备注)"
        }
    
    def parse_natural_language_rule(self, rule_text: str, bank_name: str = None) -> Dict[str, Any]:
        """解析自然语言规则
        
        Args:
            rule_text: 自然语言规则描述
            bank_name: 银行名称，用于选择特定的规则模板
            
        Returns:
            Dict: 解析后的规则对象
        """
        try:
            logger.info(f"开始解析规则: {rule_text}")
            
            # 提取关键词
            keywords = self.extract_keywords(rule_text)
            
            # 识别规则类型
            rule_type = self._identify_rule_type(rule_text, keywords)
            
            # 解析规则参数
            parameters = self._parse_rule_parameters(rule_text, rule_type, bank_name)
            
            # 构建规则对象
            rule = {
                "id": f"rule_{len(self.rules) + 1}",
                "description": rule_text,
                "type": rule_type,
                "bank_name": bank_name,
                "keywords": keywords,
                "parameters": parameters,
                "created_time": datetime.now().isoformat(),
                "status": "active"
            }
            
            self.rules.append(rule)
            logger.info(f"规则解析成功: {rule['id']}")
            return rule
            
        except Exception as e:
            logger.error(f"规则解析失败: {str(e)}")
            return {
                "id": None,
                "description": rule_text,
                "type": "unknown",
                "error": str(e),
                "status": "error"
            }
    
    def extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 提取的关键词列表
        """
        keywords = []
        
        # 匹配预定义的关键词模式
        for category, pattern in self.keyword_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                keywords.extend([f"{category}:{match}" for match in matches])
        
        # 匹配银行特定关键词
        for bank, rules in self.bank_specific_rules.items():
            if bank in text:
                keywords.append(f"银行:{bank}")
                for rule_name, rule_info in rules.items():
                    for keyword in rule_info["keywords"]:
                        if keyword in text:
                            keywords.append(f"规则:{keyword}")
        
        return keywords
    
    def _identify_rule_type(self, text: str, keywords: List[str]) -> str:
        """识别规则类型
        
        Args:
            text: 规则文本
            keywords: 提取的关键词
            
        Returns:
            str: 规则类型
        """
        # 基于关键词识别规则类型
        if any("日期" in kw for kw in keywords):
            return "date_range"
        elif any("余额" in kw for kw in keywords):
            return "balance_processing"
        elif any("收支" in kw for kw in keywords):
            return "income_expense"
        elif any("分页" in kw for kw in keywords):
            return "page_break"
        elif any("字段" in kw for kw in keywords):
            return "field_mapping"
        else:
            return "custom"
    
    def _parse_rule_parameters(self, text: str, rule_type: str, bank_name: str = None) -> Dict[str, Any]:
        """解析规则参数
        
        Args:
            text: 规则文本
            rule_type: 规则类型
            bank_name: 银行名称
            
        Returns:
            Dict: 解析后的参数
        """
        parameters = {}
        
        if rule_type == "date_range":
            parameters = self._parse_date_range_rule(text)
        elif rule_type == "balance_processing":
            parameters = self._parse_balance_rule(text)
        elif rule_type == "income_expense":
            parameters = self._parse_income_expense_rule(text)
        elif rule_type == "page_break":
            parameters = self._parse_page_break_rule(text)
        elif rule_type == "field_mapping":
            parameters = self._parse_header_rule(text)
        else:
            parameters = self._parse_custom_rule(text)
        
        return parameters
    
    def _parse_date_range_rule(self, text: str) -> Dict[str, Any]:
        """解析日期范围规则
        
        Args:
            text: 规则文本
            
        Returns:
            Dict: 日期范围参数
        """
        # 匹配日期范围模式
        pattern = r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*至\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})"
        match = re.search(pattern, text)
        
        if match:
            start_date = match.group(1)
            end_date = match.group(2)
            return {
                "start_date": start_date,
                "end_date": end_date,
                "date_format": "%Y-%m-%d"
            }
        else:
            # 尝试其他日期格式
            dates = re.findall(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})", text)
            if len(dates) >= 2:
                return {
                    "start_date": dates[0],
                    "end_date": dates[1],
                    "date_format": "%Y-%m-%d"
                }
        
        return {"error": "无法解析日期范围"}
    
    def _parse_balance_rule(self, text: str) -> Dict[str, Any]:
        """解析余额规则
        
        Args:
            text: 规则文本
            
        Returns:
            Dict: 余额处理参数
        """
        # 匹配余额计算模式
        pattern = r"余额\s*([+-]?)\s*(\d+(?:\.\d+)?)"
        match = re.search(pattern, text)
        
        if match:
            operation = match.group(1) if match.group(1) else "+"
            amount = float(match.group(2))
            return {
                "operation": operation,
                "amount": amount,
                "field": "balance"
            }
        
        return {"error": "无法解析余额规则"}
    
    def _parse_income_expense_rule(self, text: str) -> Dict[str, Any]:
        """解析收支规则
        
        Args:
            text: 规则文本
            
        Returns:
            Dict: 收支处理参数
        """
        # 匹配收支分类模式
        pattern = r"(收入|支出)\s*(\d+(?:\.\d+)?)"
        match = re.search(pattern, text)
        
        if match:
            category = match.group(1)
            amount = float(match.group(2))
            return {
                "category": category,
                "amount": amount,
                "field": "transaction_amount"
            }
        
        return {"error": "无法解析收支规则"}
    
    def _parse_page_break_rule(self, text: str) -> Dict[str, Any]:
        """解析分页符规则
        
        Args:
            text: 规则文本
            
        Returns:
            Dict: 分页符处理参数
        """
        # 匹配分页符模式
        pattern = r"分页符\s*(\d+)"
        match = re.search(pattern, text)
        
        if match:
            page_size = int(match.group(1))
            return {
                "page_size": page_size,
                "break_condition": "row_count"
            }
        
        return {"error": "无法解析分页符规则"}
    
    def _parse_header_rule(self, text: str) -> Dict[str, Any]:
        """解析表头规则
        
        Args:
            text: 规则文本
            
        Returns:
            Dict: 表头处理参数
        """
        # 匹配字段映射模式
        pattern = r"(\w+)\s*映射到\s*(\w+)"
        matches = re.findall(pattern, text)
        
        if matches:
            mappings = {source: target for source, target in matches}
            return {
                "field_mappings": mappings,
                "rule_type": "field_mapping"
            }
        
        return {"error": "无法解析表头规则"}
    
    def _parse_custom_rule(self, text: str) -> Dict[str, Any]:
        """解析自定义规则
        
        Args:
            text: 规则文本
            
        Returns:
            Dict: 自定义规则参数
        """
        return {
            "description": text,
            "rule_type": "custom",
            "parameters": {}
        }
    
    def apply_rule(self, data: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """应用规则到数据
        
        Args:
            data: 输入数据
            rule: 规则对象
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        try:
            logger.info(f"开始应用规则: {rule['id']}")
            
            rule_type = rule.get("type")
            parameters = rule.get("parameters", {})
            
            if rule_type == "date_range":
                return self._apply_date_range_rule(data, parameters)
            elif rule_type == "balance_processing":
                return self._apply_balance_rule(data, parameters)
            elif rule_type == "income_expense":
                return self._apply_income_expense_rule(data, parameters)
            elif rule_type == "page_break":
                return self._apply_page_break_rule(data, parameters)
            elif rule_type == "field_mapping":
                return self._apply_field_mapping_rule(data, parameters)
            else:
                return data
                
        except Exception as e:
            logger.error(f"规则应用失败: {str(e)}")
            return data
    
    def _apply_date_range_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用日期范围规则"""
        if "error" in parameters:
            return data
        
        start_date = pd.to_datetime(parameters["start_date"])
        end_date = pd.to_datetime(parameters["end_date"])
        
        # 假设数据中有日期列
        date_columns = [col for col in data.columns if "日期" in col or "date" in col.lower()]
        
        if date_columns:
            date_col = date_columns[0]
            mask = (pd.to_datetime(data[date_col]) >= start_date) & (pd.to_datetime(data[date_col]) <= end_date)
            return data[mask]
        
        return data
    
    def _apply_balance_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用余额规则"""
        if "error" in parameters:
            return data
        
        operation = parameters.get("operation", "+")
        amount = parameters.get("amount", 0)
        field = parameters.get("field", "balance")
        
        if field in data.columns:
            if operation == "+":
                data[field] = data[field] + amount
            elif operation == "-":
                data[field] = data[field] - amount
        
        return data
    
    def _apply_income_expense_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用收支规则"""
        if "error" in parameters:
            return data
        
        category = parameters.get("category")
        amount = parameters.get("amount", 0)
        field = parameters.get("field", "transaction_amount")
        
        if field in data.columns and category:
            # 根据收支类型调整金额符号
            if category == "支出" and amount > 0:
                data[field] = data[field].apply(lambda x: -abs(x) if x > 0 else x)
            elif category == "收入" and amount > 0:
                data[field] = data[field].apply(lambda x: abs(x) if x < 0 else x)
        
        return data
    
    def _apply_page_break_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用分页符规则"""
        if "error" in parameters:
            return data
        
        page_size = parameters.get("page_size", 1000)
        
        # 添加分页标识
        data["page_number"] = (data.index // page_size) + 1
        
        return data
    
    def _apply_field_mapping_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用字段映射规则"""
        if "error" in parameters:
            return data
        
        mappings = parameters.get("field_mappings", {})
        
        for source, target in mappings.items():
            if source in data.columns:
                data[target] = data[source]
        
        return data
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """获取所有规则"""
        return self.rules
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取规则"""
        for rule in self.rules:
            if rule["id"] == rule_id:
                return rule
        return None
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除规则"""
        for i, rule in enumerate(self.rules):
            if rule["id"] == rule_id:
                del self.rules[i]
                return True
        return False
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """更新规则"""
        for rule in self.rules:
            if rule["id"] == rule_id:
                rule.update(updates)
                return True
        return False
    
    def save_rules(self, file_path: str) -> bool:
        """保存规则到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存规则失败: {str(e)}")
            return False
    
    def load_rules(self, file_path: str) -> bool:
        """从文件加载规则"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)
            return True
        except Exception as e:
            logger.error(f"加载规则失败: {str(e)}")
            return False
    
    def validate_rule(self, rule: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证规则有效性"""
        errors = []
        
        if not rule.get("description"):
            errors.append("规则描述不能为空")
        
        if not rule.get("type"):
            errors.append("规则类型不能为空")
        
        if rule.get("type") == "date_range":
            params = rule.get("parameters", {})
            if "start_date" not in params or "end_date" not in params:
                errors.append("日期范围规则缺少开始或结束日期")
        
        return len(errors) == 0, errors


# 测试代码
if __name__ == "__main__":
    # 创建规则解析器实例
    parser = RuleParser()
    
    # 测试自然语言规则解析
    test_rules = [
        "北京银行日期范围从2024-01-01至2024-12-31",
        "工商银行余额增加1000元",
        "华夏银行收支分类：收入5000元",
        "长安银行分页符每1000行"
    ]
    
    print("规则解析测试:")
    print("=" * 50)
    
    for rule_text in test_rules:
        print(f"\n解析规则: {rule_text}")
        rule = parser.parse_natural_language_rule(rule_text)
        print(f"解析结果: {json.dumps(rule, ensure_ascii=False, indent=2)}")
    
    print("\n" + "=" * 50)
    print("规则解析模块测试完成")


