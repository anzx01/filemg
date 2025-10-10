#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试招商银行规则对"交易金额"和"交昜金额"两种字段名的兼容性
"""

import pandas as pd
import tempfile
import os
from rule_parser import RuleParser

def test_cmb_dual_fields():
    """测试招商银行规则对两种字段名的支持"""
    print("🧪 测试招商银行规则对'交易金额'和'交昜金额'字段的兼容性")
    
    # 创建测试数据 - 使用"交易金额"
    data1 = pd.DataFrame({
        '交易时间': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
        '交易金额': [1000.0, -500.0, 2000.0, -300.0],
        '对方户名': ['张三', '李四', '王五', '赵六']
    })
    
    # 创建测试数据 - 使用"交昜金额"
    data2 = pd.DataFrame({
        '交易时间': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
        '交昜金额': [1500.0, -600.0, 2500.0, -400.0],
        '对方户名': ['张三', '李四', '王五', '赵六']
    })
    
    # 创建规则解析器
    rule_parser = RuleParser()
    
    # 招商银行规则参数
    cmb_rule_params = {
        "processing_type": "sign",
        "description": "根据正负号处理",
        "source_fields": ["交易金额", "交昜金额"],
        "target_field": "收入或支出",
        "mapping": {
            "positive": "收入",
            "negative": "支出"
        }
    }
    
    print("\n📊 测试数据1 - 使用'交易金额'字段:")
    print(data1)
    
    # 应用规则到数据1
    result1 = rule_parser._apply_sign_processing_rule(data1.copy(), cmb_rule_params)
    print("\n✅ 处理结果1:")
    print(result1[['交易时间', '交易金额', '收入', '支出']])
    
    # 验证结果1
    expected_income1 = [1000.0, 0.0, 2000.0, 0.0]
    expected_expense1 = [0.0, 500.0, 0.0, 300.0]
    
    if (result1['收入'].tolist() == expected_income1 and 
        result1['支出'].tolist() == expected_expense1):
        print("✅ 数据1处理正确")
    else:
        print("❌ 数据1处理错误")
        print(f"期望收入: {expected_income1}")
        print(f"实际收入: {result1['收入'].tolist()}")
        print(f"期望支出: {expected_expense1}")
        print(f"实际支出: {result1['支出'].tolist()}")
    
    print("\n📊 测试数据2 - 使用'交昜金额'字段:")
    print(data2)
    
    # 应用规则到数据2
    result2 = rule_parser._apply_sign_processing_rule(data2.copy(), cmb_rule_params)
    print("\n✅ 处理结果2:")
    print(result2[['交易时间', '交昜金额', '收入', '支出']])
    
    # 验证结果2
    expected_income2 = [1500.0, 0.0, 2500.0, 0.0]
    expected_expense2 = [0.0, 600.0, 0.0, 400.0]
    
    if (result2['收入'].tolist() == expected_income2 and 
        result2['支出'].tolist() == expected_expense2):
        print("✅ 数据2处理正确")
    else:
        print("❌ 数据2处理错误")
        print(f"期望收入: {expected_income2}")
        print(f"实际收入: {result2['收入'].tolist()}")
        print(f"期望支出: {expected_expense2}")
        print(f"实际支出: {result2['支出'].tolist()}")
    
    # 测试混合数据（同时包含两个字段）
    data3 = pd.DataFrame({
        '交易时间': ['2024-01-01', '2024-01-02'],
        '交易金额': [1000.0, -500.0],
        '交昜金额': [1500.0, -600.0],
        '对方户名': ['张三', '李四']
    })
    
    print("\n📊 测试数据3 - 同时包含'交易金额'和'交昜金额'字段:")
    print(data3)
    
    result3 = rule_parser._apply_sign_processing_rule(data3.copy(), cmb_rule_params)
    print("\n✅ 处理结果3:")
    print(result3[['交易时间', '交易金额', '交昜金额', '收入', '支出']])
    
    # 验证结果3 - 应该优先使用第一个匹配的字段（交易金额）
    expected_income3 = [1000.0, 0.0]
    expected_expense3 = [0.0, 500.0]
    
    if (result3['收入'].tolist() == expected_income3 and 
        result3['支出'].tolist() == expected_expense3):
        print("✅ 数据3处理正确（优先使用'交易金额'）")
    else:
        print("❌ 数据3处理错误")
        print(f"期望收入: {expected_income3}")
        print(f"实际收入: {result3['收入'].tolist()}")
        print(f"期望支出: {expected_expense3}")
        print(f"实际支出: {result3['支出'].tolist()}")
    
    print("\n🎉 招商银行双字段兼容性测试完成！")

if __name__ == "__main__":
    test_cmb_dual_fields()
