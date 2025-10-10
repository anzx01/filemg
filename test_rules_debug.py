#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试规则应用问题
"""

import sys
import os
import pandas as pd
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_rules_debug():
    """调试规则应用问题"""
    print("🔍 调试规则应用问题")
    print("=" * 50)
    
    try:
        # 导入相关模块
        from special_rules import SpecialRulesManager
        from rule_parser import RuleParser
        
        # 创建规则管理器
        rules_manager = SpecialRulesManager()
        
        # 获取所有规则
        all_rules = rules_manager.get_rules()
        print(f"📋 总规则数量: {len(all_rules)}")
        
        # 按银行分组
        bank_rules = {}
        for rule in all_rules:
            bank_name = rule.get("bank_name", "未知银行")
            if bank_name not in bank_rules:
                bank_rules[bank_name] = []
            bank_rules[bank_name].append(rule)
        
        print("\n📊 按银行分组的规则:")
        for bank_name, rules in bank_rules.items():
            print(f"  {bank_name} ({len(rules)} 个规则):")
            for rule in rules:
                print(f"    - {rule['id']}: {rule['type']} - {rule['description'][:50]}...")
        
        # 测试工商银行规则
        print(f"\n🏦 测试工商银行规则:")
        icbc_rules = rules_manager.get_rules("工商银行")
        print(f"  工商银行规则数量: {len(icbc_rules)}")
        
        for rule in icbc_rules:
            print(f"    规则ID: {rule['id']}")
            print(f"    规则类型: {rule['type']}")
            print(f"    参数: {rule.get('parameters', {})}")
        
        # 创建测试数据
        test_data = pd.DataFrame({
            '交易日期': ['2025-01-01', '2025-01-02', '2025-01-03'],
            '借贷标志': ['贷', '借', '贷'],
            '发生额': [1000.0, 500.0, 2000.0],
            '对方户名': ['测试户名1', '测试户名2', '测试户名3']
        })
        
        print(f"\n🧪 测试数据:")
        print(f"  数据形状: {test_data.shape}")
        print(f"  数据列: {list(test_data.columns)}")
        print(f"  前3行数据:")
        print(test_data.head(3))
        
        # 测试规则应用
        print(f"\n🔄 应用工商银行规则:")
        result_data = rules_manager.apply_rules(test_data, "工商银行")
        
        print(f"  处理结果形状: {result_data.shape}")
        print(f"  处理结果列: {list(result_data.columns)}")
        print(f"  前3行结果:")
        print(result_data.head(3))
        
        # 检查是否有收入/支出列
        if '收入' in result_data.columns and '支出' in result_data.columns:
            print(f"\n✅ 成功创建收入/支出列:")
            print(f"  收入列统计: {result_data['收入'].sum()}")
            print(f"  支出列统计: {result_data['支出'].sum()}")
        else:
            print(f"\n❌ 未创建收入/支出列")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rules_debug()


