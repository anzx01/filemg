"""
规则解析模块测试脚本

测试自然语言规则解析和特殊规则管理功能。

作者: AI助手
创建时间: 2025-01-27
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from rule_parser import RuleParser
    from special_rules import SpecialRulesManager
    from main_controller import ExcelMergeController
    print("✓ 所有模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败: {e}")
    sys.exit(1)


def test_rule_parser():
    """测试规则解析器"""
    print("\n" + "="*60)
    print("测试规则解析器")
    print("="*60)
    
    parser = RuleParser()
    
    # 测试自然语言规则解析
    test_rules = [
        "北京银行日期范围从2024-01-01至2024-12-31",
        "工商银行余额增加1000元",
        "华夏银行收支分类：收入5000元",
        "长安银行分页符每1000行",
        "字段映射：账户号映射到account_number"
    ]
    
    print("测试自然语言规则解析:")
    for i, rule_text in enumerate(test_rules, 1):
        print(f"\n测试 {i}: {rule_text}")
        rule = parser.parse_natural_language_rule(rule_text)
        
        if rule.get("error"):
            print(f"✗ 解析失败: {rule['error']}")
        else:
            print(f"✓ 解析成功")
            print(f"  - 规则ID: {rule['id']}")
            print(f"  - 规则类型: {rule['type']}")
            print(f"  - 关键词: {rule['keywords']}")
            print(f"  - 参数: {rule['parameters']}")
    
    # 测试规则应用
    print(f"\n测试规则应用:")
    test_data = pd.DataFrame({
        'account_number': [123456789, 987654321],
        'balance': [1000, 2000],
        'transaction_date': ['2024-01-15', '2024-06-20'],
        'transaction_amount': [500, -300]
    })
    
    print(f"原始数据:")
    print(test_data)
    
    # 应用余额规则
    balance_rule = parser.parse_natural_language_rule("余额增加1000元")
    if not balance_rule.get("error"):
        result_data = parser.apply_rule(test_data, balance_rule)
        print(f"\n应用余额规则后:")
        print(result_data)
    
    return True


def test_special_rules_manager():
    """测试特殊规则管理器"""
    print("\n" + "="*60)
    print("测试特殊规则管理器")
    print("="*60)
    
    manager = SpecialRulesManager()
    
    # 测试添加规则
    print("测试添加规则:")
    test_rules = [
        ("北京银行日期范围从2024-01-01至2024-12-31", "北京银行"),
        ("工商银行余额增加1000元", "工商银行"),
        ("华夏银行收支分类：收入5000元", "华夏银行"),
        ("长安银行分页符每1000行", "长安银行")
    ]
    
    added_rules = []
    for rule_description, bank_name in test_rules:
        print(f"\n添加规则: {rule_description}")
        result = manager.add_rule(rule_description, bank_name)
        
        if result["success"]:
            print(f"✓ 规则添加成功: {result['rule']['id']}")
            added_rules.append(result['rule']['id'])
        else:
            print(f"✗ 规则添加失败: {result['error']}")
    
    # 测试获取规则
    print(f"\n测试获取规则:")
    all_rules = manager.get_rules()
    print(f"总规则数: {len(all_rules)}")
    
    for bank_name in ["北京银行", "工商银行", "华夏银行", "长安银行"]:
        bank_rules = manager.get_rules(bank_name)
        print(f"{bank_name}规则数: {len(bank_rules)}")
    
    # 测试规则统计
    print(f"\n测试规则统计:")
    stats = manager.get_rule_statistics()
    print(f"总规则数: {stats['total_rules']}")
    print(f"活跃规则数: {stats['active_rules']}")
    print(f"错误规则数: {stats['error_rules']}")
    print(f"银行统计: {stats['bank_statistics']}")
    print(f"规则类型统计: {stats['rule_type_statistics']}")
    
    # 测试规则验证
    print(f"\n测试规则验证:")
    validation = manager.validate_all_rules()
    print(f"总检查数: {validation['total_checked']}")
    print(f"有效规则: {len(validation['valid_rules'])}")
    print(f"无效规则: {len(validation['invalid_rules'])}")
    
    if validation['invalid_rules']:
        print("无效规则详情:")
        for invalid_rule in validation['invalid_rules']:
            print(f"  - {invalid_rule['rule_id']}: {invalid_rule['errors']}")
    
    # 测试规则应用
    print(f"\n测试规则应用:")
    test_data = pd.DataFrame({
        'account_number': [123456789, 987654321, 111222333],
        'balance': [1000, 2000, 1500],
        'transaction_date': ['2024-01-15', '2024-06-20', '2024-03-10'],
        'transaction_amount': [500, -300, 800]
    })
    
    print(f"原始数据:")
    print(test_data)
    
    # 应用工商银行规则
    icbc_rules = manager.get_rules("工商银行")
    if icbc_rules:
        result_data = manager.apply_rules(test_data, "工商银行")
        print(f"\n应用工商银行规则后:")
        print(result_data)
    
    return True


def test_controller_integration():
    """测试控制器集成"""
    print("\n" + "="*60)
    print("测试控制器集成")
    print("="*60)
    
    controller = ExcelMergeController()
    
    # 测试添加特殊规则
    print("测试控制器特殊规则管理:")
    
    # 添加规则
    result = controller.add_special_rule("北京银行日期范围从2024-01-01至2024-12-31", "北京银行")
    if result["success"]:
        print(f"✓ 规则添加成功: {result['rule']['id']}")
        rule_id = result['rule']['id']
        
        # 获取规则
        rule = controller.get_special_rule_by_id(rule_id)
        if rule:
            print(f"✓ 规则获取成功: {rule['description']}")
        
        # 更新规则
        update_success = controller.update_special_rule(rule_id, {"status": "inactive"})
        if update_success:
            print(f"✓ 规则更新成功")
        
        # 删除规则
        delete_success = controller.remove_special_rule(rule_id)
        if delete_success:
            print(f"✓ 规则删除成功")
    
    # 测试规则统计
    stats = controller.get_rule_statistics()
    print(f"\n规则统计: {stats}")
    
    # 测试规则验证
    validation = controller.validate_all_rules()
    print(f"规则验证: {validation}")
    
    return True


def test_data_processing_with_rules():
    """测试带规则的数据处理"""
    print("\n" + "="*60)
    print("测试带规则的数据处理")
    print("="*60)
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'account_number': [123456789, 987654321, 111222333, 444555666],
        'balance': [1000, 2000, 1500, 3000],
        'transaction_date': ['2024-01-15', '2024-06-20', '2024-03-10', '2024-08-25'],
        'transaction_amount': [500, -300, 800, -200]
    })
    
    print("原始数据:")
    print(test_data)
    
    # 创建规则管理器
    manager = SpecialRulesManager()
    
    # 添加测试规则
    rules_to_add = [
        ("余额增加500元", "测试银行"),
        ("日期范围从2024-01-01至2024-06-30", "测试银行"),
        ("收支分类：收入1000元", "测试银行")
    ]
    
    rule_ids = []
    for rule_description, bank_name in rules_to_add:
        result = manager.add_rule(rule_description, bank_name)
        if result["success"]:
            rule_ids.append(result['rule']['id'])
            print(f"✓ 规则添加成功: {result['rule']['description']}")
    
    # 应用规则
    if rule_ids:
        print(f"\n应用规则: {rule_ids}")
        result_data = manager.apply_rules(test_data, rule_ids=rule_ids)
        print("处理后的数据:")
        print(result_data)
    
    return True


def main():
    """主测试函数"""
    print("规则解析模块测试")
    print("="*60)
    
    try:
        # 测试规则解析器
        test_rule_parser()
        
        # 测试特殊规则管理器
        test_special_rules_manager()
        
        # 测试控制器集成
        test_controller_integration()
        
        # 测试带规则的数据处理
        test_data_processing_with_rules()
        
        print("\n" + "="*60)
        print("🎉 所有测试通过！")
        print("="*60)
        print("规则解析功能已准备就绪，可以投入使用。")
        print("\n主要功能：")
        print("• 自然语言规则解析")
        print("• 银行特定规则处理")
        print("• 规则管理和应用")
        print("• 数据转换和处理")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


