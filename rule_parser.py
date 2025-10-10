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
        self.bank_rules_config = self._load_bank_rules_config()
        
    def _initialize_bank_rules(self) -> Dict[str, Dict]:
        """初始化银行特定规则模板"""
        return {
            "北京银行": {
                "date_range_processing": {
                    "keywords": ["从第二行获取日期范围", "与月日数据合并", "交易日期"],
                    "pattern": r"从第二行获取日期范围.*?存入合并文件标准字段交易日期",
                    "description": "处理北京银行的日期范围规则：从第二行获取日期范围，与月日数据合并"
                },
                "date_merge": {
                    "keywords": ["日期合并", "月日数据"],
                    "pattern": r"与月日数据合并",
                    "description": "处理日期与月日数据合并"
                }
            },
            "工商银行": {
                "balance_processing": {
                    "keywords": ["借贷标志字段", "发生额", "收入或支出", "贷为收入", "借为支出"],
                    "pattern": r"根据借贷标志字段.*?存入合并文件标准字段收入或支出.*?贷为收入.*?借为支出",
                    "description": "处理工商银行借贷标志字段规则"
                },
                "page_break_processing": {
                    "keywords": ["查询编号", "对公往来户明细表", "分页符"],
                    "pattern": r"包含查询编号或对公往来户明细表字符的行为分页符",
                    "description": "处理工商银行分页符规则"
                },
                "header_processing": {
                    "keywords": ["有效表头", "列名", "分页符"],
                    "pattern": r"只有开始一个包含列名的有效表头.*?其他表头不在导出文档体现",
                    "description": "处理工商银行表头规则"
                }
            },
            "华夏银行": {
                "income_expense_processing": {
                    "keywords": ["借贷标志字段", "发生额", "收入或支出", "贷为收入", "借为支出"],
                    "pattern": r"根据借贷标志字段.*?存入合并文件标准字段收入或支出.*?贷为收入.*?借为支出",
                    "description": "处理华夏银行借贷标志字段规则"
                }
            },
            "长安银行": {
                "income_expense_processing": {
                    "keywords": ["借/贷字段", "交易金额", "收入或支出", "贷为收入", "借为支出"],
                    "pattern": r"根据借/贷字段.*?存入合并文件标准字段收入或支出.*?贷为收入.*?借为支出",
                    "description": "处理长安银行借/贷字段规则"
                }
            },
            "招商银行": {
                "sign_processing": {
                    "keywords": ["交易金额", "正负号", "正数为收入", "负数为支出"],
                    "pattern": r"根据.*?交易金额.*?字段的正负号.*?正数为收入.*?负数为支出",
                    "description": "处理招商银行交易金额正负号规则"
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
    
    def _load_bank_rules_config(self) -> List[Dict[str, Any]]:
        """加载银行规则配置"""
        try:
            import os
            config_path = os.path.join("config", "bank_rules_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return config_data.get("bank_rules", [])
            return []
        except Exception as e:
            logger.error(f"加载银行规则配置失败: {str(e)}")
            return []
    
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
        if any("日期范围" in kw for kw in keywords) or "从第二行获取日期范围" in text:
            return "date_range_processing"
        elif any("借贷标志" in kw for kw in keywords) or "借贷标志字段" in text:
            return "balance_processing"
        elif any("借/贷" in kw for kw in keywords) or "借/贷字段" in text:
            return "income_expense_processing"
        elif any("正负号" in kw for kw in keywords) or "交易金额" in text:
            return "sign_processing"
        elif any("分页符" in kw for kw in keywords) or "查询编号" in text:
            return "page_break_processing"
        elif any("表头" in kw for kw in keywords) or "有效表头" in text:
            return "header_processing"
        elif any("日期" in kw for kw in keywords):
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
        
        if rule_type == "date_range_processing":
            parameters = self._parse_date_range_processing_rule(text)
        elif rule_type == "balance_processing":
            parameters = self._parse_balance_processing_rule(text)
        elif rule_type == "income_expense_processing":
            parameters = self._parse_income_expense_processing_rule(text)
        elif rule_type == "sign_processing":
            parameters = self._parse_sign_processing_rule(text)
        elif rule_type == "page_break_processing":
            parameters = self._parse_page_break_processing_rule(text)
        elif rule_type == "header_processing":
            parameters = self._parse_header_processing_rule(text)
        elif rule_type == "date_range":
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
            
            if rule_type == "date_range_processing":
                logger.info(f"应用日期范围处理规则: {rule['id']}")
                return self._apply_date_range_processing_rule(data, parameters)
            elif rule_type == "balance_processing":
                logger.info(f"应用余额处理规则: {rule['id']}")
                return self._apply_balance_processing_rule(data, parameters)
            elif rule_type == "income_expense_processing":
                logger.info(f"应用收支处理规则: {rule['id']}")
                return self._apply_income_expense_processing_rule(data, parameters)
            elif rule_type == "sign_processing":
                logger.info(f"应用正负号处理规则: {rule['id']}")
                return self._apply_sign_processing_rule(data, parameters)
            elif rule_type == "debit_credit_processing":
                logger.info(f"应用借贷标志处理规则: {rule['id']}")
                return self._apply_debit_credit_processing_rule(data, parameters)
            elif rule_type == "debit_credit_field_processing":
                logger.info(f"应用借/贷字段处理规则: {rule['id']}")
                return self._apply_debit_credit_field_processing_rule(data, parameters)
            elif rule_type == "page_break_processing":
                logger.info(f"应用分页符处理规则: {rule['id']}")
                return self._apply_page_break_processing_rule(data, parameters)
            elif rule_type == "header_processing":
                logger.info(f"应用表头处理规则: {rule['id']}")
                return self._apply_header_processing_rule(data, parameters)
            elif rule_type == "filter_processing":
                logger.info(f"应用过滤处理规则: {rule['id']}")
                return self._apply_filter_processing_rule(data, parameters)
            elif rule_type == "date_range":
                logger.info(f"应用日期范围规则: {rule['id']}")
                return self._apply_date_range_rule(data, parameters)
            elif rule_type == "income_expense":
                logger.info(f"应用收支规则: {rule['id']}")
                return self._apply_income_expense_rule(data, parameters)
            elif rule_type == "page_break":
                logger.info(f"应用分页规则: {rule['id']}")
                return self._apply_page_break_rule(data, parameters)
            elif rule_type == "field_mapping":
                logger.info(f"应用字段映射规则: {rule['id']}")
                return self._apply_field_mapping_rule(data, parameters)
            else:
                logger.warning(f"未知规则类型: {rule_type}, 规则ID: {rule['id']}")
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
    
    def get_bank_rules(self) -> List[Dict[str, Any]]:
        """获取银行规则配置"""
        return self.bank_rules_config
    
    def get_bank_rule_by_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """根据文件名获取银行规则"""
        for rule in self.bank_rules_config:
            if rule.get("file_pattern") in filename:
                return rule
        return None
    
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
    
    def _parse_date_range_processing_rule(self, text: str) -> Dict[str, Any]:
        """解析北京银行日期范围处理规则"""
        return {
            "source_row": 2,  # 从第二行获取
            "target_field": "交易日期",
            "merge_with_date": True,
            "description": "从第二行获取日期范围，与月日数据合并"
        }
    
    def _parse_balance_processing_rule(self, text: str) -> Dict[str, Any]:
        """解析工商银行/华夏银行借贷标志处理规则"""
        return {
            "source_field": "借贷标志字段",
            "target_field": "收入或支出",
            "debit_mapping": "借为支出",
            "credit_mapping": "贷为收入",
            "amount_field": "发生额"
        }
    
    def _parse_income_expense_processing_rule(self, text: str) -> Dict[str, Any]:
        """解析长安银行借/贷字段处理规则"""
        return {
            "source_field": "借/贷字段",
            "target_field": "收入或支出",
            "debit_mapping": "借为支出",
            "credit_mapping": "贷为收入",
            "amount_field": "交易金额"
        }
    
    def _parse_sign_processing_rule(self, text: str) -> Dict[str, Any]:
        """解析招商银行正负号处理规则"""
        return {
            "source_field": "交易金额",
            "target_field": "收入或支出",
            "positive_mapping": "正数为收入",
            "negative_mapping": "负数为支出"
        }
    
    def _parse_page_break_processing_rule(self, text: str) -> Dict[str, Any]:
        """解析工商银行分页符处理规则"""
        return {
            "break_keywords": ["查询编号", "对公往来户明细表"],
            "exclude_break_rows": True,
            "description": "包含查询编号或对公往来户明细表字符的行为分页符"
        }
    
    def _parse_header_processing_rule(self, text: str) -> Dict[str, Any]:
        """解析工商银行表头处理规则"""
        return {
            "valid_header_row": 1,  # 只有开始一个包含列名的有效表头
            "exclude_other_headers": True,
            "description": "只有开始一个包含列名的有效表头，其他表头不在导出文档体现"
        }
    
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
    
    def _apply_date_range_processing_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用北京银行日期范围处理规则"""
        try:
            # 从第二行获取日期范围
            source_row = parameters.get("source_row", 2)
            target_field = parameters.get("target_field", "交易日期")
            
            if len(data) >= source_row:
                # 获取第二行的日期信息
                date_info = data.iloc[source_row - 1]  # 第二行（索引为1）
                
                # 查找日期相关列
                date_columns = [col for col in data.columns if "日期" in col or "date" in col.lower()]
                
                if date_columns:
                    # 将日期信息应用到所有行
                    for col in date_columns:
                        if pd.notna(date_info.get(col)):
                            data[target_field] = date_info[col]
                            break
            
            return data
        except Exception as e:
            logger.error(f"应用日期范围处理规则失败: {str(e)}")
            return data
    
    def _apply_balance_processing_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用工商银行/华夏银行借贷标志处理规则"""
        try:
            source_field = parameters.get("source_field", "借贷标志字段")
            target_field = parameters.get("target_field", "收入或支出")
            amount_field = parameters.get("amount_field", "发生额")
            
            # 查找借贷标志列
            balance_columns = [col for col in data.columns if "借贷" in col or "标志" in col]
            amount_columns = [col for col in data.columns if "发生" in col or "金额" in col]
            
            if balance_columns and amount_columns:
                balance_col = balance_columns[0]
                amount_col = amount_columns[0]
                
                # 根据借贷标志处理收入支出
                def process_income(row):
                    balance_flag = str(row[balance_col]).strip()
                    amount = float(row[amount_col]) if pd.notna(row[amount_col]) else 0
                    
                    if "贷" in balance_flag:
                        return abs(amount)  # 收入为正数
                    else:
                        return 0  # 非收入为0
                
                def process_expense(row):
                    balance_flag = str(row[balance_col]).strip()
                    amount = float(row[amount_col]) if pd.notna(row[amount_col]) else 0
                    
                    if "借" in balance_flag:
                        return abs(amount)  # 支出为正数
                    else:
                        return 0  # 非支出为0
                
                # 创建收入和支出两个字段
                data["收入"] = data.apply(process_income, axis=1)
                data["支出"] = data.apply(process_expense, axis=1)
                
                # 删除原始的借贷标志和发生额列
                if balance_col in data.columns:
                    data = data.drop(columns=[balance_col])
                if amount_col in data.columns:
                    data = data.drop(columns=[amount_col])
            
            return data
        except Exception as e:
            logger.error(f"应用借贷标志处理规则失败: {str(e)}")
            return data
    
    def _apply_income_expense_processing_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用长安银行借/贷字段处理规则"""
        try:
            # 获取新的参数格式
            balance_field = parameters.get("balance_field", "借/贷")
            amount_field = parameters.get("amount_field", "交易金额")
            income_field = parameters.get("income_field", "收入")
            expense_field = parameters.get("expense_field", "支出")
            debit_value = parameters.get("debit_value", "借")
            credit_value = parameters.get("credit_value", "贷")
            
            # 查找借/贷字段列
            balance_columns = [col for col in data.columns if "借" in col and "贷" in col]
            # 更灵活地匹配金额字段，支持繁体字和简体字
            amount_columns = [col for col in data.columns if ("交易" in col or "交昜" in col) and "金额" in col]
            
            if balance_columns and amount_columns:
                balance_col = balance_columns[0]
                amount_col = amount_columns[0]
                
                # 根据借/贷字段处理收入支出
                def process_income(row):
                    balance_flag = str(row[balance_col]).strip()
                    amount = float(row[amount_col]) if pd.notna(row[amount_col]) else 0
                    
                    if credit_value in balance_flag:
                        return abs(amount)  # 贷为收入
                    else:
                        return 0  # 非收入为0
                
                def process_expense(row):
                    balance_flag = str(row[balance_col]).strip()
                    amount = float(row[amount_col]) if pd.notna(row[amount_col]) else 0
                    
                    if debit_value in balance_flag:
                        return abs(amount)  # 借为支出
                    else:
                        return 0  # 非支出为0
                
                # 创建收入和支出两个字段
                data[income_field] = data.apply(process_income, axis=1)
                data[expense_field] = data.apply(process_expense, axis=1)
                
                logger.info(f"成功创建字段: {income_field} 和 {expense_field}")
            
            return data
        except Exception as e:
            logger.error(f"应用借/贷字段处理规则失败: {str(e)}")
            return data
    
    def _apply_sign_processing_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用招商银行正负号处理规则"""
        try:
            # 支持单个字段或多个字段
            source_fields = parameters.get("source_fields", [])
            source_field = parameters.get("source_field", "交易金额")
            
            # 如果source_fields存在，使用它；否则使用source_field
            if source_fields:
                field_candidates = source_fields
            else:
                field_candidates = [source_field]
            
            # 查找匹配的金额列
            amount_col = None
            for candidate in field_candidates:
                if candidate in data.columns:
                    amount_col = candidate
                    break
            
            # 如果直接匹配失败，尝试模糊匹配
            if not amount_col:
                for candidate in field_candidates:
                    # 查找包含关键词的列
                    matching_cols = [col for col in data.columns if candidate in col]
                    if matching_cols:
                        amount_col = matching_cols[0]
                        break
            
            # 如果还是没找到，使用原来的逻辑
            if not amount_col:
                amount_columns = [col for col in data.columns if "交易" in col and "金额" in col]
                if amount_columns:
                    amount_col = amount_columns[0]
            
            if amount_col:
                logger.info(f"使用字段 '{amount_col}' 进行正负号处理")
                
                # 根据正负号处理收入支出
                def process_income(row):
                    amount = float(row[amount_col]) if pd.notna(row[amount_col]) else 0
                    if amount > 0:
                        return abs(amount)  # 正数为收入
                    else:
                        return 0  # 非收入为0
                
                def process_expense(row):
                    amount = float(row[amount_col]) if pd.notna(row[amount_col]) else 0
                    if amount < 0:
                        return abs(amount)  # 负数为支出
                    else:
                        return 0  # 非支出为0
                
                # 创建收入和支出两个字段
                data["收入"] = data.apply(process_income, axis=1)
                data["支出"] = data.apply(process_expense, axis=1)
            else:
                logger.warning("未找到匹配的金额字段进行正负号处理")
            
            return data
        except Exception as e:
            logger.error(f"应用正负号处理规则失败: {str(e)}")
            return data
    
    def _apply_page_break_processing_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用工商银行分页符处理规则"""
        try:
            break_keywords = parameters.get("break_keywords", ["查询编号", "对公往来户明细表"])
            exclude_break_rows = parameters.get("exclude_break_rows", True)
            
            if exclude_break_rows:
                # 查找包含分页符关键词的行
                mask = pd.Series([True] * len(data))
                
                for col in data.columns:
                    for keyword in break_keywords:
                        mask &= ~data[col].astype(str).str.contains(keyword, na=False)
                
                return data[mask]
            
            return data
        except Exception as e:
            logger.error(f"应用分页符处理规则失败: {str(e)}")
            return data
    
    def _apply_header_processing_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用工商银行表头处理规则"""
        try:
            valid_header_row = parameters.get("valid_header_row", 1)
            exclude_other_headers = parameters.get("exclude_other_headers", True)
            
            if exclude_other_headers:
                # 只保留第一个有效表头，移除其他表头行
                # 这里假设数据已经正确加载，只处理数据内容
                pass
            
            return data
        except Exception as e:
            logger.error(f"应用表头处理规则失败: {str(e)}")
            return data
    
    def _apply_filter_processing_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用过滤处理规则（工商银行分页符和表头过滤）"""
        try:
            logger.info("应用过滤处理规则")
            
            # 获取过滤参数
            filters = parameters.get("filters", {})
            exclude_keywords = filters.get("exclude_keywords", [])
            header_only_first = filters.get("header_only_first", False)
            remove_pagination = filters.get("remove_pagination", False)
            
            result_data = data.copy()
            
            # 过滤包含排除关键词的行
            if exclude_keywords:
                for keyword in exclude_keywords:
                    # 检查所有列是否包含关键词
                    mask = result_data.astype(str).apply(
                        lambda x: x.str.contains(keyword, na=False)
                    ).any(axis=1)
                    result_data = result_data[~mask]
                    logger.info(f"过滤包含关键词 '{keyword}' 的行，剩余 {len(result_data)} 行")
            
            # 过滤分页符
            if remove_pagination:
                # 查找可能的分页符行（通常包含页码、分页信息等）
                pagination_patterns = [
                    r'第\s*\d+\s*页',
                    r'共\s*\d+\s*页',
                    r'页码',
                    r'分页',
                    r'Page\s*\d+',
                    r'Total\s*\d+'
                ]
                
                for pattern in pagination_patterns:
                    mask = result_data.astype(str).apply(
                        lambda x: x.str.contains(pattern, na=False, regex=True)
                    ).any(axis=1)
                    result_data = result_data[~mask]
                    logger.info(f"过滤分页符模式 '{pattern}'，剩余 {len(result_data)} 行")
            
            # 只保留第一个表头
            if header_only_first and len(result_data) > 1:
                # 假设第一行是表头，查找重复的表头行
                header_row = result_data.iloc[0]
                duplicate_headers = []
                
                for idx in range(1, len(result_data)):
                    if result_data.iloc[idx].equals(header_row):
                        duplicate_headers.append(idx)
                
                if duplicate_headers:
                    result_data = result_data.drop(duplicate_headers)
                    logger.info(f"移除重复表头行 {duplicate_headers}，剩余 {len(result_data)} 行")
            
            logger.info(f"过滤处理完成，处理了 {len(result_data)} 条记录")
            return result_data
            
        except Exception as e:
            logger.error(f"应用过滤处理规则失败: {str(e)}")
            return data
    
    def _apply_debit_credit_processing_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用借贷标志处理规则（工商银行、华夏银行）"""
        try:
            logger.info("应用借贷标志处理规则")
            
            # 获取参数
            source_field = parameters.get("source_field", "借贷标志")
            target_field = parameters.get("target_field", "收入或支出")
            amount_fields = parameters.get("amount_fields", ["发生额"])
            mapping = parameters.get("mapping", {"贷": "收入", "借": "支出"})
            
            # 如果amount_fields是单个字段，转换为数组
            if isinstance(amount_fields, str):
                amount_fields = [amount_fields]
            
            # 查找可用的金额字段
            available_amount_field = None
            for field in amount_fields:
                if field in data.columns:
                    available_amount_field = field
                    break
            
            # 如果没找到指定的金额字段，尝试模糊匹配
            if not available_amount_field:
                for col in data.columns:
                    if any(keyword in col for keyword in ["发生", "金额", "交易"]):
                        available_amount_field = col
                        break
            
            # 查找借贷标志字段
            available_source_field = None
            if source_field in data.columns:
                available_source_field = source_field
            else:
                # 尝试模糊匹配
                for col in data.columns:
                    if any(keyword in col for keyword in ["借贷", "标志", "借/贷"]):
                        available_source_field = col
                        break
            
            # 检查必要字段是否存在
            if not available_source_field:
                logger.warning(f"未找到借贷标志字段，尝试的字段: {source_field}")
                logger.warning(f"可用字段: {list(data.columns)}")
                return data
            
            if not available_amount_field:
                logger.warning(f"未找到金额字段，尝试的字段: {amount_fields}")
                logger.warning(f"可用字段: {list(data.columns)}")
                return data
            
            logger.info(f"使用字段 - 借贷标志: {available_source_field}, 金额: {available_amount_field}")
            
            # 创建收入支出列
            result_data = data.copy()
            result_data["收入"] = 0.0
            result_data["支出"] = 0.0
            
            # 处理借贷标志
            for idx, row in result_data.iterrows():
                debit_credit = str(row[available_source_field]).strip()
                
                # 安全地转换金额
                try:
                    amount_value = row[available_amount_field]
                    if pd.notna(amount_value) and str(amount_value).strip() != '':
                        amount = float(amount_value)
                    else:
                        amount = 0.0
                except (ValueError, TypeError):
                    amount = 0.0
                
                if debit_credit in mapping:
                    if mapping[debit_credit] == "收入":
                        result_data.at[idx, "收入"] = amount
                    elif mapping[debit_credit] == "支出":
                        result_data.at[idx, "支出"] = amount
            
            logger.info(f"借贷标志处理完成，处理了 {len(result_data)} 条记录")
            return result_data
            
        except Exception as e:
            logger.error(f"应用借贷标志处理规则失败: {str(e)}")
            return data
    
    def _apply_debit_credit_field_processing_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用借/贷字段处理规则（长安银行）"""
        try:
            logger.info("应用借/贷字段处理规则")
            
            # 获取参数
            source_field = parameters.get("source_field", "借/贷")
            amount_fields = parameters.get("amount_fields", ["交易金额"])
            target_field = parameters.get("target_field", "收入或支出")
            mapping = parameters.get("mapping", {"贷": "收入", "借": "支出"})
            
            # 如果amount_fields是单个字段，转换为数组
            if isinstance(amount_fields, str):
                amount_fields = [amount_fields]
            
            # 查找可用的金额字段
            available_amount_field = None
            for field in amount_fields:
                if field in data.columns:
                    available_amount_field = field
                    break
            
            # 如果没找到指定的金额字段，尝试模糊匹配
            if not available_amount_field:
                for col in data.columns:
                    if any(keyword in col for keyword in ["交易", "金额", "发生"]):
                        available_amount_field = col
                        break
            
            # 查找借/贷字段
            available_source_field = None
            if source_field in data.columns:
                available_source_field = source_field
            else:
                # 尝试模糊匹配
                for col in data.columns:
                    if any(keyword in col for keyword in ["借/贷", "借贷", "标志"]):
                        available_source_field = col
                        break
            
            # 检查必要字段是否存在
            if not available_source_field:
                logger.warning(f"未找到借/贷字段，尝试的字段: {source_field}")
                logger.warning(f"可用字段: {list(data.columns)}")
                return data
            
            if not available_amount_field:
                logger.warning(f"未找到金额字段，尝试的字段: {amount_fields}")
                logger.warning(f"可用字段: {list(data.columns)}")
                return data
            
            logger.info(f"使用字段 - 借/贷: {available_source_field}, 金额: {available_amount_field}")
            
            # 创建收入支出列
            result_data = data.copy()
            result_data["收入"] = 0.0
            result_data["支出"] = 0.0
            
            # 处理借/贷字段
            for idx, row in result_data.iterrows():
                debit_credit = str(row[available_source_field]).strip()
                
                # 安全地转换金额
                try:
                    amount_value = row[available_amount_field]
                    if pd.notna(amount_value) and str(amount_value).strip() != '':
                        amount = float(amount_value)
                    else:
                        amount = 0.0
                except (ValueError, TypeError):
                    amount = 0.0
                
                if debit_credit in mapping:
                    if mapping[debit_credit] == "收入":
                        result_data.at[idx, "收入"] = amount
                    elif mapping[debit_credit] == "支出":
                        result_data.at[idx, "支出"] = amount
            
            logger.info(f"借/贷字段处理完成，处理了 {len(result_data)} 条记录")
            return result_data
            
        except Exception as e:
            logger.error(f"应用借/贷字段处理规则失败: {str(e)}")
            return data

    def apply_icbc_rules(self, data: pd.DataFrame) -> pd.DataFrame:
        """应用工商银行特定规则到数据"""
        try:
            # 工商银行规则参数
            parameters = {
                "source_field": "借贷标志字段",
                "target_field": "收入或支出", 
                "amount_field": "发生额"
            }
            
            # 应用工商银行/华夏银行借贷标志处理规则
            processed_data = self._apply_balance_processing_rule(data, parameters)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"应用工商银行规则失败: {str(e)}")
            return data


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


