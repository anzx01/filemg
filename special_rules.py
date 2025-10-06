"""
特殊规则模块 - 规则管理和应用功能

该模块负责管理银行特定的业务规则，包括规则的添加、删除、更新和应用。
支持自然语言规则描述和自动规则解析。

作者: AI助手
创建时间: 2025-01-27
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from rule_parser import RuleParser

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpecialRulesManager:
    """特殊规则管理器类
    
    负责管理银行特定的业务规则，包括规则的CRUD操作和规则应用。
    """
    
    def __init__(self, config_file: str = "config/rules_config.json"):
        """初始化特殊规则管理器
        
        Args:
            config_file: 规则配置文件路径
        """
        self.config_file = config_file
        self.rules = []
        self.rule_parser = RuleParser()
        self.bank_rules = {}
        
        # 加载现有规则
        self.load_rules()
    
    def add_rule(self, rule_description: str, bank_name: str = None, rule_type: str = None) -> Dict[str, Any]:
        """添加新规则
        
        Args:
            rule_description: 规则描述（自然语言）
            bank_name: 银行名称
            rule_type: 规则类型
            
        Returns:
            Dict: 添加的规则对象
        """
        try:
            logger.info(f"添加新规则: {rule_description}")
            
            # 使用规则解析器解析自然语言规则
            parsed_rule = self.rule_parser.parse_natural_language_rule(rule_description, bank_name)
            
            if parsed_rule.get("error"):
                logger.error(f"规则解析失败: {parsed_rule['error']}")
                return {
                    "success": False,
                    "error": parsed_rule["error"],
                    "rule": None
                }
            
            # 验证规则
            is_valid, errors = self.rule_parser.validate_rule(parsed_rule)
            if not is_valid:
                logger.error(f"规则验证失败: {errors}")
                return {
                    "success": False,
                    "error": f"规则验证失败: {', '.join(errors)}",
                    "rule": None
                }
            
            # 添加到规则列表
            self.rules.append(parsed_rule)
            
            # 按银行分组
            if bank_name:
                if bank_name not in self.bank_rules:
                    self.bank_rules[bank_name] = []
                self.bank_rules[bank_name].append(parsed_rule)
            
            # 保存规则
            self.save_rules()
            
            logger.info(f"规则添加成功: {parsed_rule['id']}")
            return {
                "success": True,
                "rule": parsed_rule
            }
            
        except Exception as e:
            logger.error(f"添加规则失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "rule": None
            }
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            logger.info(f"删除规则: {rule_id}")
            
            # 从规则列表中删除
            success = self.rule_parser.remove_rule(rule_id)
            
            if success:
                # 从银行规则中删除
                for bank_name, bank_rule_list in self.bank_rules.items():
                    self.bank_rules[bank_name] = [
                        rule for rule in bank_rule_list if rule["id"] != rule_id
                    ]
                
                # 保存规则
                self.save_rules()
                logger.info(f"规则删除成功: {rule_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除规则失败: {str(e)}")
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
            
            # 更新规则
            success = self.rule_parser.update_rule(rule_id, updates)
            
            if success:
                # 更新银行规则
                for bank_name, bank_rule_list in self.bank_rules.items():
                    for rule in bank_rule_list:
                        if rule["id"] == rule_id:
                            rule.update(updates)
                            break
                
                # 保存规则
                self.save_rules()
                logger.info(f"规则更新成功: {rule_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"更新规则失败: {str(e)}")
            return False
    
    def get_rules(self, bank_name: str = None) -> List[Dict[str, Any]]:
        """获取规则列表
        
        Args:
            bank_name: 银行名称，如果指定则只返回该银行的规则
            
        Returns:
            List[Dict]: 规则列表
        """
        if bank_name:
            return self.bank_rules.get(bank_name, [])
        else:
            return self.rules
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            Optional[Dict]: 规则对象，如果不存在则返回None
        """
        return self.rule_parser.get_rule_by_id(rule_id)
    
    def apply_rules(self, data: pd.DataFrame, bank_name: str = None, rule_ids: List[str] = None) -> pd.DataFrame:
        """应用规则到数据
        
        Args:
            data: 输入数据
            bank_name: 银行名称，如果指定则只应用该银行的规则
            rule_ids: 规则ID列表，如果指定则只应用这些规则
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        try:
            logger.info(f"开始应用规则，银行: {bank_name}, 规则数量: {len(rule_ids) if rule_ids else 'all'}")
            
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
                "field_mapping": 1,
                "date_range": 2,
                "balance_processing": 3,
                "income_expense": 4,
                "page_break": 5,
                "custom": 6
            }
            
            rules_to_apply.sort(key=lambda x: rule_priority.get(x.get("type", "custom"), 6))
            
            # 应用规则
            for rule in rules_to_apply:
                if rule.get("status") == "active":
                    try:
                        result_data = self.rule_parser.apply_rule(result_data, rule)
                        applied_rules.append(rule["id"])
                        logger.info(f"规则应用成功: {rule['id']}")
                    except Exception as e:
                        logger.error(f"规则应用失败: {rule['id']}, 错误: {str(e)}")
            
            logger.info(f"规则应用完成，应用了 {len(applied_rules)} 个规则")
            return result_data
            
        except Exception as e:
            logger.error(f"应用规则失败: {str(e)}")
            return data
    
    def save_rules(self) -> bool:
        """保存规则到文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保配置目录存在
            import os
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # 保存规则
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, ensure_ascii=False, indent=2)
            
            logger.info(f"规则保存成功: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存规则失败: {str(e)}")
            return False
    
    def load_rules(self) -> bool:
        """从文件加载规则
        
        Returns:
            bool: 加载是否成功
        """
        try:
            import os
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.rules = json.load(f)
                
                # 重建银行规则索引
                self.bank_rules = {}
                for rule in self.rules:
                    bank_name = rule.get("bank_name")
                    if bank_name:
                        if bank_name not in self.bank_rules:
                            self.bank_rules[bank_name] = []
                        self.bank_rules[bank_name].append(rule)
                
                logger.info(f"规则加载成功: {len(self.rules)} 个规则")
                return True
            else:
                logger.info("规则文件不存在，使用默认规则")
                return True
                
        except Exception as e:
            logger.error(f"加载规则失败: {str(e)}")
            return False
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """获取规则统计信息
        
        Returns:
            Dict: 统计信息
        """
        total_rules = len(self.rules)
        active_rules = len([rule for rule in self.rules if rule.get("status") == "active"])
        error_rules = len([rule for rule in self.rules if rule.get("status") == "error"])
        
        bank_stats = {}
        for bank_name, bank_rule_list in self.bank_rules.items():
            bank_stats[bank_name] = len(bank_rule_list)
        
        rule_type_stats = {}
        for rule in self.rules:
            rule_type = rule.get("type", "unknown")
            rule_type_stats[rule_type] = rule_type_stats.get(rule_type, 0) + 1
        
        return {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "error_rules": error_rules,
            "bank_statistics": bank_stats,
            "rule_type_statistics": rule_type_stats
        }
    
    def validate_all_rules(self) -> Dict[str, Any]:
        """验证所有规则
        
        Returns:
            Dict: 验证结果
        """
        validation_results = {
            "valid_rules": [],
            "invalid_rules": [],
            "total_checked": 0
        }
        
        for rule in self.rules:
            is_valid, errors = self.rule_parser.validate_rule(rule)
            validation_results["total_checked"] += 1
            
            if is_valid:
                validation_results["valid_rules"].append(rule["id"])
            else:
                validation_results["invalid_rules"].append({
                    "rule_id": rule["id"],
                    "errors": errors
                })
        
        return validation_results
    
    def export_rules(self, file_path: str) -> bool:
        """导出规则到文件
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            bool: 导出是否成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, ensure_ascii=False, indent=2)
            
            logger.info(f"规则导出成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出规则失败: {str(e)}")
            return False
    
    def import_rules(self, file_path: str) -> bool:
        """从文件导入规则
        
        Args:
            file_path: 导入文件路径
            
        Returns:
            bool: 导入是否成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_rules = json.load(f)
            
            # 验证导入的规则
            valid_rules = []
            for rule in imported_rules:
                is_valid, errors = self.rule_parser.validate_rule(rule)
                if is_valid:
                    valid_rules.append(rule)
                else:
                    logger.warning(f"跳过无效规则: {rule.get('id', 'unknown')}, 错误: {errors}")
            
            # 添加有效规则
            self.rules.extend(valid_rules)
            
            # 重建银行规则索引
            self.bank_rules = {}
            for rule in self.rules:
                bank_name = rule.get("bank_name")
                if bank_name:
                    if bank_name not in self.bank_rules:
                        self.bank_rules[bank_name] = []
                    self.bank_rules[bank_name].append(rule)
            
            # 保存规则
            self.save_rules()
            
            logger.info(f"规则导入成功: {len(valid_rules)} 个有效规则")
            return True
            
        except Exception as e:
            logger.error(f"导入规则失败: {str(e)}")
            return False


# 测试代码
if __name__ == "__main__":
    # 创建特殊规则管理器实例
    rules_manager = SpecialRulesManager()
    
    # 测试添加规则
    print("特殊规则管理器测试:")
    print("=" * 50)
    
    # 添加测试规则
    test_rules = [
        ("北京银行日期范围从2024-01-01至2024-12-31", "北京银行"),
        ("工商银行余额增加1000元", "工商银行"),
        ("华夏银行收支分类：收入5000元", "华夏银行"),
        ("长安银行分页符每1000行", "长安银行")
    ]
    
    for rule_description, bank_name in test_rules:
        print(f"\n添加规则: {rule_description}")
        result = rules_manager.add_rule(rule_description, bank_name)
        if result["success"]:
            print(f"✓ 规则添加成功: {result['rule']['id']}")
        else:
            print(f"✗ 规则添加失败: {result['error']}")
    
    # 显示规则统计
    print(f"\n规则统计:")
    stats = rules_manager.get_rule_statistics()
    print(f"总规则数: {stats['total_rules']}")
    print(f"活跃规则数: {stats['active_rules']}")
    print(f"错误规则数: {stats['error_rules']}")
    print(f"银行统计: {stats['bank_statistics']}")
    
    # 验证所有规则
    print(f"\n规则验证:")
    validation = rules_manager.validate_all_rules()
    print(f"总检查数: {validation['total_checked']}")
    print(f"有效规则: {len(validation['valid_rules'])}")
    print(f"无效规则: {len(validation['invalid_rules'])}")
    
    print("\n" + "=" * 50)
    print("特殊规则管理器测试完成")


