#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单路径匹配测试
"""

import os
import json

def test_path_matching():
    """测试路径匹配问题"""
    print("🔍 测试路径匹配问题")
    
    # 加载配置文件
    with open('dist/config/field_mapping_config.json', 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    print(f"✅ 成功加载字段映射配置，包含 {len(config_data)} 个文件")
    
    # 测试路径
    test_path = "D:/sjdataapp/AI比赛测试数据/建设银行.xlsx"
    
    print(f"\n测试路径: {test_path}")
    print(f"路径分隔符: {repr(os.sep)}")
    
    # 检查配置中的键
    config_keys = list(config_data.keys())
    print(f"\n配置中的键 (前3个):")
    for i, key in enumerate(config_keys[:3]):
        print(f"  {i+1}. {repr(key)}")
    
    # 直接匹配
    if test_path in config_data:
        print(f"✅ 直接匹配成功")
    else:
        print(f"❌ 直接匹配失败")
    
    # 标准化路径匹配
    normalized_test = os.path.normpath(test_path)
    print(f"\n标准化后的测试路径: {repr(normalized_test)}")
    
    found = False
    for config_key in config_keys:
        normalized_config = os.path.normpath(config_key)
        if normalized_config == normalized_test:
            print(f"✅ 标准化路径匹配成功")
            print(f"   配置键: {repr(config_key)}")
            print(f"   标准化后: {repr(normalized_config)}")
            found = True
            break
    
    if not found:
        print(f"❌ 标准化路径匹配失败")
        
        # 检查是否有相似的键
        print(f"\n查找相似的键:")
        for key in config_keys:
            if "建设银行" in key:
                print(f"  找到包含'建设银行'的键: {repr(key)}")
                print(f"  标准化后: {repr(os.path.normpath(key))}")

if __name__ == "__main__":
    test_path_matching()
