"""
动态规则解析器 - 完全基于 rules_config.json 的规则处理系统
"""
import json
import logging
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class DynamicRuleParser:
    """动态规则解析器 - 基于配置文件的规则处理系统"""
    
    def __init__(self, config_path: str = "config/rules_config.json"):
        """初始化动态规则解析器
        
        Args:
            config_path: 规则配置文件路径
        """
        self.config_path = config_path
        self.rules = []
        self.load_rules()
    
    def load_rules(self) -> bool:
        """从配置文件加载规则"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)
            logger.info(f"成功加载 {len(self.rules)} 个规则")
            return True
        except Exception as e:
            logger.error(f"加载规则失败: {e}")
            return False
    
    def reload_rules(self) -> bool:
        """重新加载规则（用于规则更新后）"""
        try:
            logger.info("重新加载规则...")
            success = self.load_rules()
            if success:
                # 验证规则完整性并报告问题
                issues = self.validate_and_report_issues()
                total_issues = sum(len(issue_list) for issue_list in issues.values())
                if total_issues > 0:
                    logger.warning(f"规则配置存在 {total_issues} 个问题，请检查配置文件")
                    self._print_validation_issues(issues)
                else:
                    logger.info("规则配置验证通过")
            return success
        except Exception as e:
            logger.error(f"重新加载规则失败: {e}")
            return False
    
    def validate_rules(self) -> bool:
        """验证规则配置的完整性"""
        try:
            issues = self.validate_and_report_issues()
            total_issues = sum(len(issue_list) for issue_list in issues.values())
            return total_issues == 0
                
        except Exception as e:
            logger.error(f"验证规则配置失败: {e}")
            return False
    
    def validate_and_report_issues(self) -> Dict[str, List[str]]:
        """验证规则配置并报告问题，不进行自动修复"""
        issues = {
            "missing_parameters": [],
            "invalid_rules": [],
            "incomplete_configs": []
        }
        
        try:
            logger.info("开始验证规则配置...")
            
            for rule in self.rules:
                rule_id = rule.get("id", "未知")
                rule_type = rule.get("type", "未知")
                bank_name = rule.get("bank_name", "未知银行")
                parameters = rule.get("parameters", {})
                
                # 检查字段映射规则
                if rule_type == "field_mapping":
                    if "field_mappings" not in parameters or not parameters["field_mappings"]:
                        issues["missing_parameters"].append(
                            f"规则 {rule_id} ({bank_name}): 字段映射规则缺少 'field_mappings' 参数"
                        )
                
                # 检查日期处理规则
                elif rule_type == "date_range_processing":
                    if "date_columns" not in parameters or not parameters["date_columns"]:
                        issues["missing_parameters"].append(
                            f"规则 {rule_id} ({bank_name}): 日期处理规则缺少 'date_columns' 参数"
                        )
                
                # 检查余额处理规则
                elif rule_type == "balance_processing":
                    if "balance_columns" not in parameters or not parameters["balance_columns"]:
                        issues["missing_parameters"].append(
                            f"规则 {rule_id} ({bank_name}): 余额处理规则缺少 'balance_columns' 参数"
                        )
                
                # 检查借贷处理规则
                elif rule_type == "debit_credit_processing":
                    missing_params = []
                    if "debit_columns" not in parameters or not parameters["debit_columns"]:
                        missing_params.append("debit_columns")
                    if "credit_columns" not in parameters or not parameters["credit_columns"]:
                        missing_params.append("credit_columns")
                    if missing_params:
                        issues["missing_parameters"].append(
                            f"规则 {rule_id} ({bank_name}): 借贷处理规则缺少参数: {', '.join(missing_params)}"
                        )
                
                # 检查规则基本结构
                if not rule_id or rule_id == "未知":
                    issues["invalid_rules"].append(f"发现缺少ID的规则: {rule.get('description', '无描述')}")
                
                if not rule_type or rule_type == "未知":
                    issues["invalid_rules"].append(f"规则 {rule_id} 缺少类型信息")
                
                if not bank_name or bank_name == "未知银行":
                    issues["invalid_rules"].append(f"规则 {rule_id} 缺少银行名称")
            
            # 统计问题数量
            total_issues = sum(len(issue_list) for issue_list in issues.values())
            if total_issues > 0:
                logger.warning(f"发现 {total_issues} 个配置问题")
            else:
                logger.info("规则配置验证通过")
                
            return issues
            
        except Exception as e:
            logger.error(f"验证规则配置时发生错误: {e}")
            issues["invalid_rules"].append(f"验证过程发生错误: {str(e)}")
            return issues
    
    def _print_validation_issues(self, issues: Dict[str, List[str]]) -> None:
        """打印验证问题详情"""
        print("\n" + "="*60)
        print("规则配置问题报告")
        print("="*60)
        
        if issues["missing_parameters"]:
            print("\n[错误] 缺少必要参数:")
            for issue in issues["missing_parameters"]:
                print(f"  - {issue}")
        
        if issues["invalid_rules"]:
            print("\n[错误] 无效规则:")
            for issue in issues["invalid_rules"]:
                print(f"  - {issue}")
        
        if issues["incomplete_configs"]:
            print("\n[错误] 不完整配置:")
            for issue in issues["incomplete_configs"]:
                print(f"  - {issue}")
        
        print("\n" + "="*60)
        print("请检查并修复 config/rules_config.json 文件中的问题")
        print("="*60)
    
    def check_configuration_issues(self) -> bool:
        """检查配置问题并显示给用户
        
        Returns:
            bool: True表示配置正常，False表示存在问题
        """
        issues = self.validate_and_report_issues()
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        
        if total_issues > 0:
            self._print_validation_issues(issues)
            return False
        else:
            print("规则配置验证通过，没有发现问题")
            return True
    
    def save_rules(self) -> bool:
        """保存规则到配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, ensure_ascii=False, indent=2)
            logger.info(f"规则配置已保存到 {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"保存规则配置失败: {e}")
            return False
    
    def get_rules(self, bank_name: str = None) -> List[Dict[str, Any]]:
        """获取规则列表
        
        Args:
            bank_name: 银行名称，如果指定则只返回该银行的规则
            
        Returns:
            List[Dict]: 规则列表
        """
        if bank_name:
            return [rule for rule in self.rules if rule.get("bank_name") == bank_name and rule.get("status") == "active"]
        return [rule for rule in self.rules if rule.get("status") == "active"]
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            Optional[Dict]: 规则对象
        """
        for rule in self.rules:
            if rule.get("id") == rule_id:
                return rule
        return None
    
    def get_bank_rule_by_file(self, file_name: str) -> Optional[Dict[str, Any]]:
        """根据文件名获取银行规则
        
        Args:
            file_name: 文件名
            
        Returns:
            Optional[Dict]: 银行规则对象，如果不存在则返回None
        """
        try:
            # 从文件名中提取银行名称
            bank_name = None
            if "浦发银行" in file_name:
                bank_name = "浦发银行"
            elif "工商银行" in file_name:
                bank_name = "工商银行"
            elif "华夏银行" in file_name:
                bank_name = "华夏银行"
            elif "长安银行" in file_name:
                bank_name = "长安银行"
            elif "招商银行" in file_name:
                bank_name = "招商银行"
            elif "北京银行" in file_name:
                bank_name = "北京银行"
            elif "兴业银行" in file_name:
                bank_name = "兴业银行"
            
            if bank_name:
                # 获取该银行的所有活跃规则
                bank_rules = self.get_rules(bank_name)
                if bank_rules:
                    # 优先选择非默认规则（用户自定义规则）
                    for rule in bank_rules:
                        if not rule.get("id", "").startswith("default_rule_"):
                            return rule
                    
                    # 如果没有用户自定义规则，返回第一个规则
                    return bank_rules[0]
            
            return None
        except Exception as e:
            self.logger.error(f"获取银行规则时发生错误: {e}, 文件名: {file_name}")
            return None
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            logger.info(f"删除规则: {rule_id}")
            
            # 查找要删除的规则
            rule_to_remove = None
            for rule in self.rules:
                if rule.get("id") == rule_id:
                    rule_to_remove = rule
                    break
            
            if not rule_to_remove:
                logger.warning(f"规则不存在: {rule_id}")
                return False
            
            # 从规则列表中删除
            self.rules = [rule for rule in self.rules if rule.get("id") != rule_id]
            
            # 保存到文件
            self.save_rules()
            
            logger.info(f"规则删除成功: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除规则失败: {e}")
            return False
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """更新规则
        
        Args:
            rule_id: 规则ID
            updates: 更新内容
            
        Returns:
            bool: 更新是否成功
        """
        try:
            logger.info(f"更新规则: {rule_id}")
            
            # 查找要更新的规则
            rule_to_update = None
            for i, rule in enumerate(self.rules):
                if rule.get("id") == rule_id:
                    rule_to_update = i
                    break
            
            if rule_to_update is None:
                logger.warning(f"规则不存在: {rule_id}")
                return False
            
            # 更新规则
            self.rules[rule_to_update].update(updates)
            
            # 保存到文件
            self.save_rules()
            
            logger.info(f"规则更新成功: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新规则失败: {e}")
            return False
    
    def validate_rule(self, rule: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证规则
        
        Args:
            rule: 规则对象
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误列表)
        """
        errors = []
        
        # 检查必需字段
        required_fields = ["id", "description", "type", "bank_name"]
        for field in required_fields:
            if field not in rule or not rule[field]:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查规则类型
        valid_types = [
            "filter_processing",
            "date_range_processing", 
            "debit_credit_processing",
            "debit_credit_field_processing",
            "sign_processing",
            "balance_processing",
            "field_mapping",
            "custom"
        ]
        
        if rule.get("type") not in valid_types:
            errors.append(f"无效的规则类型: {rule.get('type')}")
        
        # 检查参数
        if "parameters" not in rule:
            errors.append("缺少参数配置")
        
        return len(errors) == 0, errors
    
    def save_rules(self) -> bool:
        """保存规则到文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, ensure_ascii=False, indent=2)
            logger.info(f"规则保存成功: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"保存规则失败: {e}")
            return False
    
    def parse_natural_language_rule(self, rule_description: str, bank_name: str = None) -> Dict[str, Any]:
        """解析自然语言规则描述
        
        Args:
            rule_description: 自然语言规则描述
            bank_name: 银行名称
            
        Returns:
            Dict: 解析后的规则对象
        """
        try:
            # 生成规则ID
            rule_id = f"{bank_name.lower() if bank_name else 'custom'}_{int(datetime.now().timestamp())}"
            
            # 根据描述推断规则类型
            rule_type = "custom"
            if "借方金额" in rule_description and "贷方金额" in rule_description:
                rule_type = "balance_processing"
            elif "过滤" in rule_description or "分页" in rule_description:
                rule_type = "filter_processing"
            elif "日期" in rule_description or "范围" in rule_description:
                rule_type = "date_range_processing"
            elif "借贷" in rule_description or "借/贷" in rule_description:
                rule_type = "debit_credit_processing"
            elif "正负" in rule_description or "符号" in rule_description:
                rule_type = "sign_processing"
            elif "映射" in rule_description or "字段" in rule_description:
                rule_type = "field_mapping"
            
            # 创建规则对象
            rule = {
                "id": rule_id,
                "description": rule_description,
                "type": rule_type,
                "bank_name": bank_name or "未知银行",
                "keywords": [f"银行:{bank_name}", f"描述:{rule_description}"],
                "parameters": {
                    "processing_type": rule_type.replace("_processing", ""),
                    "description": rule_description
                },
                "created_time": datetime.now().isoformat(),
                "status": "active"
            }
            
            # 为特定规则类型添加详细参数
            if rule_type == "balance_processing":
                rule["parameters"].update({
                    "debit_columns": ["借方金额"],
                    "credit_columns": ["贷方金额"],
                    "target_income_field": "收入",
                    "target_expense_field": "支出"
                })
                rule["keywords"].extend([
                    "处理:借方贷方金额",
                    "字段:借方金额",
                    "字段:贷方金额",
                    "规则:余额处理"
                ])
            elif rule_type == "field_mapping":
                # 从规则描述中提取字段映射信息
                field_mappings = self._extract_field_mappings_from_description(rule_description)
                rule["parameters"].update({
                    "field_mappings": field_mappings
                })
                
                # 根据提取的字段名生成关键词
                keywords = ["处理:字段映射", "规则:字段映射"]
                for source_field, target_field in field_mappings.items():
                    keywords.extend([
                        f"字段:{source_field}",
                        f"字段:{target_field}"
                    ])
                rule["keywords"].extend(keywords)
            
            return rule
            
        except Exception as e:
            logger.error(f"解析自然语言规则失败: {e}")
            return {
                "error": f"解析失败: {str(e)}",
                "success": False
            }
    
    def _extract_field_mappings_from_description(self, description: str) -> Dict[str, str]:
        """从规则描述中提取字段映射信息"""
        import re
        
        # 常见的字段映射模式
        patterns = [
            # 模式1: "将导入文件的X字段映射到导出文件的Y字段上"
            r"将导入文件的(.+?)字段映射到导出文件的(.+?)字段上",
            # 模式2: "将X字段映射到Y字段"
            r"将(.+?)字段映射到(.+?)字段",
            # 模式3: "X字段 -> Y字段"
            r"(.+?)字段\s*->\s*(.+?)字段",
            # 模式4: "X -> Y"
            r"(\S+)\s*->\s*(\S+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                source_field = match.group(1).strip()
                target_field = match.group(2).strip()
                return {source_field: target_field}
        
        # 如果没有匹配到，返回空映射
        logger.warning(f"无法从描述中提取字段映射: {description}")
        return {}
    
    def apply_rules(self, data: pd.DataFrame, bank_name: str = None, rule_ids: List[str] = None) -> pd.DataFrame:
        """应用规则到数据
        
        Args:
            data: 输入数据
            bank_name: 银行名称
            rule_ids: 规则ID列表
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        try:
            logger.info(f"开始应用动态规则，银行: {bank_name}, 规则数量: {len(rule_ids) if rule_ids else 'all'}")
            
            result_data = data.copy()
            applied_rules = []
            
            # 获取要应用的规则
            rules_to_apply = []
            
            if rule_ids:
                # 应用指定的规则
                for rule_id in rule_ids:
                    rule = self.get_rule_by_id(rule_id)
                    if rule:
                        rules_to_apply.append(rule)
            elif bank_name:
                # 应用指定银行的规则
                rules_to_apply = self.get_rules(bank_name)
            else:
                # 应用所有规则
                rules_to_apply = self.get_rules()
            
            # 按规则类型排序，确保处理顺序
            rule_priority = {
                "filter_processing": 1,
                "date_range_processing": 2,
                "debit_credit_processing": 3,
                "debit_credit_field_processing": 4,
                "balance_processing": 5,
                "sign_processing": 6,
                "field_mapping": 7,
                "custom": 8
            }
            
            rules_to_apply.sort(key=lambda x: rule_priority.get(x.get("type", "custom"), 7))
            
            # 应用规则
            for rule in rules_to_apply:
                try:
                    logger.info(f"应用规则: {rule['id']} - {rule['description']}")
                    result_data = self.apply_rule(result_data, rule)
                    applied_rules.append(rule['id'])
                except Exception as e:
                    logger.error(f"应用规则 {rule['id']} 失败: {e}")
                    continue
            
            logger.info(f"规则应用完成，应用了 {len(applied_rules)} 个规则")
            return result_data
            
        except Exception as e:
            logger.error(f"应用规则失败: {e}")
            return data
    
    def apply_rule(self, data: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """应用单个规则到数据
        
        Args:
            data: 输入数据
            rule: 规则对象
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        try:
            # 验证输入参数
            if data is None or data.empty:
                logger.warning("输入数据为空，跳过规则应用")
                return data
                
            if not rule or not isinstance(rule, dict):
                logger.error("规则对象无效")
                return data
                
            rule_type = rule.get("type")
            parameters = rule.get("parameters", {})
            rule_id = rule.get("id", "未知")
            
            logger.info(f"应用规则类型: {rule_type}, 规则ID: {rule_id}")
            
            # 验证规则类型
            if not rule_type:
                logger.error(f"规则 {rule_id} 缺少类型信息")
                return data
            
            # 根据规则类型动态调用对应的处理方法
            if rule_type == "filter_processing":
                return self._apply_filter_rule(data, parameters)
            elif rule_type == "date_range_processing":
                return self._apply_date_range_rule(data, parameters)
            elif rule_type == "debit_credit_processing":
                return self._apply_debit_credit_rule(data, parameters)
            elif rule_type == "debit_credit_field_processing":
                return self._apply_debit_credit_field_rule(data, parameters)
            elif rule_type == "balance_processing":
                return self._apply_balance_processing_rule(data, parameters)
            elif rule_type == "sign_processing":
                return self._apply_sign_rule(data, parameters)
            elif rule_type == "field_mapping":
                return self._apply_field_mapping_rule(data, parameters)
            else:
                logger.warning(f"未知规则类型: {rule_type}, 规则ID: {rule_id}")
                return data
                
        except Exception as e:
            logger.error(f"应用规则失败: {e}, 规则ID: {rule.get('id', '未知') if rule else '无'}")
            return data
    
    def _apply_filter_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用过滤规则"""
        try:
            filters = parameters.get("filters", {})
            exclude_keywords = filters.get("exclude_keywords", [])
            remove_pagination = filters.get("remove_pagination", True)
            
            if not exclude_keywords or not remove_pagination:
                return data
            
            # 创建过滤掩码
            mask = pd.Series([True] * len(data))
            
            for col in data.columns:
                for keyword in exclude_keywords:
                    mask &= ~data[col].astype(str).str.contains(keyword, na=False)
            
            filtered_data = data[mask]
            logger.info(f"过滤规则应用完成，过滤前: {len(data)} 行，过滤后: {len(filtered_data)} 行")
            return filtered_data
            
        except Exception as e:
            logger.error(f"应用过滤规则失败: {e}")
            return data
    
    def _apply_date_range_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用日期范围规则"""
        try:
            import re
            import pandas as pd
            from datetime import datetime
            
            # 日期范围处理规则通常用于北京银行
            logger.info("应用日期范围规则")
            
            # 获取参数
            source_row = parameters.get("source_row", 2)
            target_field = parameters.get("target_field", "交易日期")
            merge_type = parameters.get("merge_type", "date_range_with_month_day")
            date_columns = parameters.get("date_columns", ["交易日期", "日期"])
            
            # 查找包含日期范围信息的列
            date_range_text = None
            
            # 首先尝试从当前数据中查找
            for row_idx in range(min(5, len(data))):  # 检查前5行
                for col in data.columns:
                    cell_value = data.iloc[row_idx][col]
                    if pd.notna(cell_value):
                        cell_value_str = str(cell_value)
                        if "起止日期" in cell_value_str:
                            date_range_text = cell_value_str
                            logger.info(f"从第{row_idx+1}行找到日期范围信息: {date_range_text}")
                            break
                if date_range_text:
                    break
            
            # 如果当前数据中没有找到，尝试从原始文件读取
            if not date_range_text:
                try:
                    # 尝试从原始文件读取前几行来获取日期范围信息
                    import pandas as pd
                    # 这里需要知道原始文件路径，暂时跳过
                    logger.warning("未找到日期范围信息，跳过日期范围处理")
                    return data
                except Exception as e:
                    logger.warning(f"无法读取原始文件获取日期范围信息: {e}")
                    return data
            
            if not date_range_text:
                logger.warning("未找到日期范围信息")
                return data
            
            # 提取日期范围
            # 匹配格式：2022年01月01日-2022年12月31日
            date_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日-(\d{4})年(\d{1,2})月(\d{1,2})日'
            match = re.search(date_pattern, date_range_text)
            
            if not match:
                logger.warning(f"无法解析日期范围: {date_range_text}")
                return data
            
            # 提取开始和结束日期
            start_year, start_month, start_day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            end_year, end_month, end_day = int(match.group(4)), int(match.group(5)), int(match.group(6))
            
            logger.info(f"提取到日期范围: {start_year}年{start_month}月{start_day}日 - {end_year}年{end_month}月{end_day}日")
            
            # 查找日期列
            date_col = None
            for col in date_columns:
                if col in data.columns:
                    date_col = col
                    break
            
            if not date_col:
                # 如果没有找到标准日期列，查找包含"日期"的列
                for col in data.columns:
                    if "日期" in str(col):
                        date_col = col
                        break
            
            if not date_col:
                logger.warning("未找到日期列")
                return data
            
            # 处理日期数据
            def process_date(date_value):
                if pd.isna(date_value):
                    return None
                
                date_str = str(date_value).strip()
                
                # 如果已经是完整日期格式，直接返回
                if len(date_str) >= 8 and "年" in date_str and "月" in date_str and "日" in date_str:
                    return date_str
                
                # 如果是数字格式的日期（如"20220111"），转换为标准格式
                if date_str.isdigit() and len(date_str) == 8:
                    try:
                        year = int(date_str[:4])
                        month = int(date_str[4:6])
                        day = int(date_str[6:8])
                        return f"{year}年{month:02d}月{day:02d}日"
                    except ValueError:
                        pass
                
                # 如果是月日格式（如"01月01日"），需要与年份合并
                month_day_pattern = r'(\d{1,2})月(\d{1,2})日'
                month_day_match = re.search(month_day_pattern, date_str)
                
                if month_day_match:
                    month = int(month_day_match.group(1))
                    day = int(month_day_match.group(2))
                    
                    # 根据月份判断年份
                    # 如果月份在开始月份之前，使用结束年份
                    if month < start_month:
                        year = end_year
                    else:
                        year = start_year
                    
                    return f"{year}年{month:02d}月{day:02d}日"
                
                return date_str
            
            # 应用日期处理
            if date_col in data.columns:
                data[date_col] = data[date_col].apply(process_date)
                logger.info(f"已处理日期列: {date_col}")
            
            # 如果目标字段与源字段不同，创建目标字段
            if target_field != date_col and target_field not in data.columns:
                data[target_field] = data[date_col]
                logger.info(f"已创建目标日期字段: {target_field}")
            
            return data
            
        except Exception as e:
            logger.error(f"应用日期范围规则失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return data
    
    def _apply_debit_credit_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用借贷标志规则（工商银行、华夏银行）"""
        try:
            source_field = parameters.get("source_field", "借贷标志")
            target_field = parameters.get("target_field", "收入或支出")
            amount_fields = parameters.get("amount_fields", ["发生额", "交易金额", "交昜金额"])
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
                # 按优先级查找金额字段
                priority_keywords = [["发生", "金额"], ["借方", "金额"], ["支出", "金额"], ["交易", "金额"]]
                for keywords in priority_keywords:
                    for col in data.columns:
                        if all(keyword in col for keyword in keywords) and "时间" not in col and "日期" not in col:
                            available_amount_field = col
                            break
                    if available_amount_field:
                        break
                
                # 如果还是没找到，尝试更宽泛的匹配
                if not available_amount_field:
                    for col in data.columns:
                        if any(keyword in col for keyword in ["发生", "金额"]) and "时间" not in col and "日期" not in col:
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
                logger.warning(f"未找到借贷标志字段: {source_field}")
                return data
            
            if not available_amount_field:
                logger.warning(f"未找到金额字段: {amount_fields}")
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
            logger.error(f"应用借贷标志规则失败: {e}")
            return data
    
    def _apply_debit_credit_field_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用借/贷字段规则（长安银行）"""
        try:
            source_field = parameters.get("source_field", "借/贷")
            amount_fields = parameters.get("amount_fields", ["交易金额", "交昜金额"])
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
                    if any(keyword in col for keyword in ["交易", "金额"]):
                        available_amount_field = col
                        break
            
            # 查找借/贷字段
            available_source_field = None
            if source_field in data.columns:
                available_source_field = source_field
            else:
                # 尝试模糊匹配
                for col in data.columns:
                    if any(keyword in col for keyword in ["借/贷", "借贷"]):
                        available_source_field = col
                        break
            
            # 检查必要字段是否存在
            if not available_source_field:
                logger.warning(f"未找到借/贷字段: {source_field}")
                return data
            
            if not available_amount_field:
                logger.warning(f"未找到金额字段: {amount_fields}")
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
            logger.error(f"应用借/贷字段规则失败: {e}")
            return data
    
    def _apply_sign_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用正负号规则（招商银行）"""
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
            logger.error(f"应用正负号规则失败: {e}")
            return data
    
    def _apply_field_mapping_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用字段映射规则"""
        try:
            mappings = parameters.get("field_mappings", {})
            
            if not mappings:
                logger.warning("字段映射规则缺少 field_mappings 参数，跳过处理")
                return data
            
            for source, target in mappings.items():
                if source in data.columns:
                    data[target] = data[source]
                    logger.info(f"字段映射: {source} -> {target}")
                else:
                    logger.warning(f"源字段 '{source}' 不存在于数据中，跳过映射")
            
            return data
            
        except Exception as e:
            logger.error(f"应用字段映射规则失败: {e}")
            return data
    
    def _apply_balance_processing_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用余额处理规则"""
        try:
            # 获取参数
            debit_columns = parameters.get("debit_columns", [])
            credit_columns = parameters.get("credit_columns", [])
            target_income_field = parameters.get("target_income_field", "收入")
            target_expense_field = parameters.get("target_expense_field", "支出")
            
            # 查找借方金额和贷方金额列
            found_debit_cols = []
            found_credit_cols = []
            
            for col in data.columns:
                for debit_col in debit_columns:
                    if debit_col in col:
                        found_debit_cols.append(col)
                        break
                for credit_col in credit_columns:
                    if credit_col in col:
                        found_credit_cols.append(col)
                        break
            
            if found_debit_cols and found_credit_cols:
                debit_col = found_debit_cols[0]
                credit_col = found_credit_cols[0]
                
                logger.info(f"找到借方列: {debit_col}, 贷方列: {credit_col}")
                
                # 处理收入列（贷方金额）
                def process_income(row):
                    credit_amount = row[credit_col]
                    if pd.notna(credit_amount) and str(credit_amount).strip() != '':
                        try:
                            return float(credit_amount)
                        except (ValueError, TypeError):
                            return None
                    return None
                
                # 处理支出列（借方金额）
                def process_expense(row):
                    debit_amount = row[debit_col]
                    if pd.notna(debit_amount) and str(debit_amount).strip() != '':
                        try:
                            return float(debit_amount)
                        except (ValueError, TypeError):
                            return None
                    return None
                
                # 创建收入和支出字段
                data[target_income_field] = data.apply(process_income, axis=1)
                data[target_expense_field] = data.apply(process_expense, axis=1)
                
                logger.info(f"余额处理规则应用成功，创建字段: {target_income_field}, {target_expense_field}")
            else:
                logger.warning(f"未找到指定的借方或贷方列，借方列: {debit_columns}, 贷方列: {credit_columns}")
            
            return data
            
        except Exception as e:
            logger.error(f"应用余额处理规则失败: {e}")
            return data


# 测试代码
if __name__ == "__main__":
    # 创建动态规则解析器实例
    parser = DynamicRuleParser()
    
    # 测试获取规则
    print("所有规则:")
    for rule in parser.get_rules():
        print(f"  - {rule['id']}: {rule['description']}")
    
    print("\n工商银行规则:")
    for rule in parser.get_rules("工商银行"):
        print(f"  - {rule['id']}: {rule['description']}")
    
    print("\n动态规则解析器测试完成")
