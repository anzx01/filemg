"""
规则验证工具
用于检测和修复规则配置中的问题
"""

import json
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
import os

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RuleValidator:
    """规则验证器"""
    
    def __init__(self, config_path: str = "config/rules_config.json"):
        self.config_path = config_path
        self.rules = []
        self.errors = []
        self.warnings = []
    
    def load_rules(self) -> bool:
        """加载规则配置"""
        try:
            if not os.path.exists(self.config_path):
                self.errors.append(f"规则配置文件不存在: {self.config_path}")
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)
            
            logger.info(f"成功加载 {len(self.rules)} 个规则")
            return True
            
        except Exception as e:
            self.errors.append(f"加载规则配置失败: {e}")
            return False
    
    def validate_rules(self) -> Tuple[bool, List[str], List[str]]:
        """验证所有规则"""
        self.errors = []
        self.warnings = []
        
        if not self.rules:
            self.errors.append("没有规则需要验证")
            return False, self.errors, self.warnings
        
        # 检查规则ID唯一性
        rule_ids = []
        for i, rule in enumerate(self.rules):
            rule_id = rule.get("id")
            if not rule_id:
                self.errors.append(f"规则 {i+1} 缺少ID")
            elif rule_id in rule_ids:
                self.errors.append(f"规则ID重复: {rule_id}")
            else:
                rule_ids.append(rule_id)
        
        # 验证每个规则
        for i, rule in enumerate(self.rules):
            self._validate_single_rule(rule, i+1)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_single_rule(self, rule: Dict[str, Any], rule_index: int):
        """验证单个规则"""
        rule_id = rule.get("id", f"规则{rule_index}")
        
        # 检查必需字段
        required_fields = ["id", "description", "type", "bank_name", "parameters"]
        for field in required_fields:
            if field not in rule:
                self.errors.append(f"规则 {rule_id} 缺少必需字段: {field}")
        
        # 检查规则类型
        rule_type = rule.get("type")
        valid_types = [
            "filter_processing", "date_range_processing", "debit_credit_processing",
            "debit_credit_field_processing", "sign_processing", "field_mapping",
            "balance_processing", "custom"
        ]
        if rule_type and rule_type not in valid_types:
            self.warnings.append(f"规则 {rule_id} 使用了未知类型: {rule_type}")
        
        # 检查参数结构
        parameters = rule.get("parameters", {})
        if not isinstance(parameters, dict):
            self.errors.append(f"规则 {rule_id} 的parameters字段必须是字典")
        
        # 根据规则类型检查特定参数
        if rule_type == "field_mapping":
            field_mappings = parameters.get("field_mappings", {})
            if not field_mappings:
                self.warnings.append(f"规则 {rule_id} 的字段映射为空")
            elif not isinstance(field_mappings, dict):
                self.errors.append(f"规则 {rule_id} 的field_mappings必须是字典")
        
        # 检查银行名称
        bank_name = rule.get("bank_name")
        if not bank_name or bank_name == "未知银行":
            self.warnings.append(f"规则 {rule_id} 的银行名称未设置或为未知")
    
    def auto_fix_rules(self) -> bool:
        """自动修复规则问题"""
        fixed_count = 0
        
        for rule in self.rules:
            # 修复缺少的ID
            if not rule.get("id"):
                rule["id"] = f"auto_generated_{int(datetime.now().timestamp())}"
                fixed_count += 1
            
            # 修复缺少的银行名称
            if not rule.get("bank_name") or rule.get("bank_name") == "未知银行":
                # 尝试从描述中提取银行名称
                description = rule.get("description", "")
                if "浦发银行" in description:
                    rule["bank_name"] = "浦发银行"
                elif "工商银行" in description:
                    rule["bank_name"] = "工商银行"
                elif "华夏银行" in description:
                    rule["bank_name"] = "华夏银行"
                elif "长安银行" in description:
                    rule["bank_name"] = "长安银行"
                elif "招商银行" in description:
                    rule["bank_name"] = "招商银行"
                elif "北京银行" in description:
                    rule["bank_name"] = "北京银行"
                elif "兴业银行" in description:
                    rule["bank_name"] = "兴业银行"
                else:
                    rule["bank_name"] = "未知银行"
                fixed_count += 1
            
            # 确保parameters是字典
            if not isinstance(rule.get("parameters"), dict):
                rule["parameters"] = {}
                fixed_count += 1
        
        if fixed_count > 0:
            logger.info(f"自动修复了 {fixed_count} 个问题")
            return True
        
        return False
    
    def save_rules(self) -> bool:
        """保存修复后的规则"""
        try:
            # 创建备份
            backup_path = f"{self.config_path}.backup_{int(datetime.now().timestamp())}"
            if os.path.exists(self.config_path):
                import shutil
                shutil.copy2(self.config_path, backup_path)
                logger.info(f"已创建备份文件: {backup_path}")
            
            # 保存修复后的规则
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, ensure_ascii=False, indent=2)
            
            logger.info(f"规则已保存到: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存规则失败: {e}")
            return False
    
    def generate_rule_report(self) -> str:
        """生成规则报告"""
        report = []
        report.append("=" * 50)
        report.append("规则验证报告")
        report.append("=" * 50)
        report.append(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"规则总数: {len(self.rules)}")
        report.append(f"错误数量: {len(self.errors)}")
        report.append(f"警告数量: {len(self.warnings)}")
        report.append("")
        
        if self.errors:
            report.append("错误列表:")
            for i, error in enumerate(self.errors, 1):
                report.append(f"  {i}. {error}")
            report.append("")
        
        if self.warnings:
            report.append("警告列表:")
            for i, warning in enumerate(self.warnings, 1):
                report.append(f"  {i}. {warning}")
            report.append("")
        
        # 按银行分组统计规则
        bank_stats = {}
        for rule in self.rules:
            bank_name = rule.get("bank_name", "未知银行")
            bank_stats[bank_name] = bank_stats.get(bank_name, 0) + 1
        
        report.append("银行规则统计:")
        for bank_name, count in sorted(bank_stats.items()):
            report.append(f"  {bank_name}: {count} 个规则")
        
        return "\n".join(report)


def main():
    """主函数"""
    print("规则验证工具")
    print("=" * 30)
    
    # 创建验证器
    validator = RuleValidator()
    
    # 加载规则
    if not validator.load_rules():
        print("[失败] 规则加载失败")
        return
    
    # 验证规则
    is_valid, errors, warnings = validator.validate_rules()
    
    # 显示结果
    print(f"\n验证结果: {'[通过]' if is_valid else '[失败]'}")
    print(f"错误: {len(errors)} 个")
    print(f"警告: {len(warnings)} 个")
    
    if errors:
        print("\n错误详情:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    
    if warnings:
        print("\n警告详情:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    
    # 自动修复
    if errors or warnings:
        print("\n尝试自动修复...")
        if validator.auto_fix_rules():
            print("[成功] 自动修复完成")
            
            # 重新验证
            is_valid_after, errors_after, warnings_after = validator.validate_rules()
            print(f"\n修复后验证结果: {'[通过]' if is_valid_after else '[仍有问题]'}")
            print(f"剩余错误: {len(errors_after)} 个")
            print(f"剩余警告: {len(warnings_after)} 个")
            
            # 保存修复后的规则
            if validator.save_rules():
                print("[成功] 修复后的规则已保存")
            else:
                print("[失败] 保存规则失败")
        else:
            print("[警告] 无法自动修复所有问题")
    
    # 生成报告
    report = validator.generate_rule_report()
    print(f"\n{report}")


if __name__ == "__main__":
    main()
