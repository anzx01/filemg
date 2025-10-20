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
from dynamic_rule_parser import DynamicRuleParser
from llm_api import RuleLLMParser

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpecialRulesManager:
    """特殊规则管理器类
    
    负责管理银行特定的业务规则，包括规则的CRUD操作和规则应用。
    """
    
    def __init__(self, config_file: str = "config/rules_config.json", disable_llm: bool = False):
        """初始化特殊规则管理器
        
        Args:
            config_file: 规则配置文件路径
            disable_llm: 是否禁用LLM功能
        """
        self.config_file = config_file
        self.rules = []
        self.rule_parser = DynamicRuleParser(config_file)
        self.disable_llm = disable_llm
        
        # 只有在不禁用LLM时才初始化LLM解析器
        if not disable_llm:
            try:
                self.llm_parser = RuleLLMParser()
            except Exception as e:
                print(f"警告: LLM解析器初始化失败，将使用传统解析: {e}")
                self.llm_parser = None
                self.disable_llm = True
        else:
            self.llm_parser = None
            
        self.bank_rules = {}
        
        # 加载现有规则
        self.load_rules()
    
    def _is_duplicate_rule(self, new_rule: Dict[str, Any]) -> bool:
        """检查是否存在重复规则
        
        Args:
            new_rule: 新规则对象
            
        Returns:
            bool: 是否存在重复规则
        """
        return self._find_duplicate_rule(new_rule) is not None
    
    def _clean_rule_description(self, description: str, bank_name: str) -> str:
        """清理规则描述，用于比较
        
        Args:
            description: 原始描述
            bank_name: 银行名称
            
        Returns:
            str: 清理后的描述
        """
        if not description:
            return ""
            
        # 去除银行名称前缀
        desc = description.strip()
        if desc.startswith(f"{bank_name} - "):
            desc = desc[len(f"{bank_name} - "):].strip()
        elif desc.startswith(f"{bank_name} -"):
            desc = desc[len(f"{bank_name} -"):].strip()
        elif desc.startswith(f"{bank_name} "):
            desc = desc[len(f"{bank_name} "):].strip()
            
        # 去除多余的空格和标点
        desc = desc.replace("  ", " ").strip()
        desc = desc.replace("，", "，").strip()
        
        return desc
    
    def _find_duplicate_rule(self, new_rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """查找重复规则
        
        Args:
            new_rule: 新规则对象
            
        Returns:
            Optional[Dict]: 重复的规则对象，如果没有找到则返回None
        """
        new_bank = new_rule.get('bank_name', '')
        new_desc = new_rule.get('description', '').strip()
        new_type = new_rule.get('type', '')
        
        for existing_rule in self.rules:
            existing_bank = existing_rule.get('bank_name', '')
            existing_desc = existing_rule.get('description', '').strip()
            existing_type = existing_rule.get('type', '')
            
            # 银行名称必须相同
            if new_bank != existing_bank:
                continue
                
            # 规则类型必须相同
            if new_type != existing_type:
                continue
            
            # 检查描述是否相似（去除银行名称前缀和多余空格）
            new_desc_clean = self._clean_rule_description(new_desc, new_bank)
            existing_desc_clean = self._clean_rule_description(existing_desc, existing_bank)
            
            # 如果清理后的描述相同，则认为是重复规则
            if new_desc_clean == existing_desc_clean:
                return existing_rule
                
        return None
    
    def _update_existing_rule(self, rule_id: str, new_rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新现有规则
        
        Args:
            rule_id: 要更新的规则ID
            new_rule_data: 新的规则数据
            
        Returns:
            Dict: 更新结果
        """
        try:
            # 找到要更新的规则
            rule_index = None
            for i, rule in enumerate(self.rules):
                if rule["id"] == rule_id:
                    rule_index = i
                    break
            
            if rule_index is None:
                return {
                    "success": False,
                    "error": f"规则不存在: {rule_id}",
                    "rule": None
                }
            
            # 保留原有的ID和创建时间
            original_id = self.rules[rule_index]["id"]
            original_created_time = self.rules[rule_index].get("created_time")
            
            # 更新规则数据
            self.rules[rule_index].update(new_rule_data)
            self.rules[rule_index]["id"] = original_id
            if original_created_time:
                self.rules[rule_index]["created_time"] = original_created_time
            self.rules[rule_index]["updated_time"] = datetime.now().isoformat()
            
            # 更新银行规则
            bank_name = new_rule_data.get('bank_name', '')
            if bank_name in self.bank_rules:
                for rule in self.bank_rules[bank_name]:
                    if rule["id"] == rule_id:
                        rule.update(new_rule_data)
                        rule["id"] = original_id
                        if original_created_time:
                            rule["created_time"] = original_created_time
                        rule["updated_time"] = datetime.now().isoformat()
                        break
            
            # 同步到rule_parser
            self.rule_parser.rules = self.rules.copy()
            
            # 保存规则
            self.save_rules()
            
            logger.info(f"规则更新成功: {rule_id}")
            return {
                "success": True,
                "rule": self.rules[rule_index],
                "message": "规则已更新"
            }
            
        except Exception as e:
            logger.error(f"更新规则失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "rule": None
            }

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
            
            # 检查是否存在重复规则
            duplicate_rule = self._find_duplicate_rule(parsed_rule)
            if duplicate_rule:
                logger.warning(f"发现重复规则，将更新现有规则: {duplicate_rule['id']}")
                # 更新现有规则
                return self._update_existing_rule(duplicate_rule['id'], parsed_rule)
            
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
            
            # 同步到rule_parser并保存
            self.rule_parser.rules = self.rules.copy()
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
    
    def add_llm_rule(self, rule_description: str, bank_name: str = None) -> Dict[str, Any]:
        """使用LLM添加新规则
        
        Args:
            rule_description: 规则描述（自然语言）
            bank_name: 银行名称
            
        Returns:
            Dict: 添加的规则对象
        """
        try:
            logger.info(f"使用LLM添加新规则: {rule_description}")
            
            # 检查LLM解析器是否可用
            if not self.llm_parser or self.disable_llm:
                logger.warning("LLM解析器不可用，回退到传统解析")
                return self.add_rule(rule_description, bank_name)
            
            # 使用LLM解析规则
            result = self.llm_parser.parse_natural_language_rule(rule_description, bank_name)
            
            if not result.get("success"):
                logger.error(f"LLM规则解析失败: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error"),
                    "rule": None
                }
            
            rule = result
            
            # 验证规则
            is_valid, errors = self.rule_parser.validate_rule(rule)
            if not is_valid:
                logger.error(f"LLM规则验证失败: {errors}")
                return {
                    "success": False,
                    "error": f"规则验证失败: {', '.join(errors)}",
                    "rule": None
                }
            
            # 添加到规则列表
            self.rules.append(rule)
            
            # 按银行分组
            if bank_name:
                if bank_name not in self.bank_rules:
                    self.bank_rules[bank_name] = []
                self.bank_rules[bank_name].append(rule)
            
            # 保存规则
            self.save_rules()
            
            logger.info(f"LLM规则添加成功: {rule['id']}")
            return {
                "success": True,
                "rule": rule
            }
            
        except Exception as e:
            logger.error(f"添加LLM规则失败: {str(e)}")
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
            
            # 检查规则是否存在
            rule_to_remove = self.get_rule_by_id(rule_id)
            if not rule_to_remove:
                logger.warning(f"规则不存在: {rule_id}")
                return False
            
            # 从SpecialRulesManager的规则列表中删除
            original_count = len(self.rules)
            self.rules = [rule for rule in self.rules if rule["id"] != rule_id]
            
            if len(self.rules) == original_count:
                logger.warning(f"规则不存在: {rule_id}")
                return False
            
            # 从银行规则中删除
            for bank_name, bank_rule_list in self.bank_rules.items():
                self.bank_rules[bank_name] = [
                    rule for rule in bank_rule_list if rule["id"] != rule_id
                ]
            
            # 同步到rule_parser并保存
            self.rule_parser.rules = self.rules.copy()
            self.save_rules()
            logger.info(f"规则删除成功: {rule_id}")
            return True
            
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
            
            # 检查规则是否存在
            rule_to_update = None
            for i, rule in enumerate(self.rules):
                if rule["id"] == rule_id:
                    rule_to_update = i
                    break
            
            if rule_to_update is None:
                logger.warning(f"规则不存在: {rule_id}")
                return False
            
            # 更新规则
            self.rules[rule_to_update].update(updates)
            
            # 更新银行规则
            for bank_name, bank_rule_list in self.bank_rules.items():
                for rule in bank_rule_list:
                    if rule["id"] == rule_id:
                        rule.update(updates)
                        break
            
            # 同步到rule_parser并保存
            self.rule_parser.rules = self.rules.copy()
            self.save_rules()
            logger.info(f"规则更新成功: {rule_id}")
            return True
            
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
        return self.rule_parser.get_rules(bank_name)
    
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
            logger.info(f"开始应用动态规则，银行: {bank_name}, 规则数量: {len(rule_ids) if rule_ids else 'all'}")
            
            # 使用动态规则解析器应用规则
            return self.rule_parser.apply_rules(data, bank_name, rule_ids)
            
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
            
            # 同步规则到rule_parser
            self.rule_parser.rules = self.rules.copy()
            
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
                
                # 同步规则到RuleParser
                self.rule_parser.rules = self.rules.copy()
                
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


