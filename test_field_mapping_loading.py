#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字段映射配置加载问题
"""

import os
import json
from resource_manager import ResourceManager

def test_field_mapping_loading():
    """测试字段映射配置加载"""
    print("🧪 测试字段映射配置加载")
    
    # 使用资源管理器加载配置
    resource_manager = ResourceManager()
    config_data = resource_manager.load_json_config("config/field_mapping_config.json")
    
    if not config_data:
        print("❌ 无法加载字段映射配置")
        return
    
    print(f"✅ 成功加载字段映射配置，包含 {len(config_data)} 个文件")
    
    # 显示所有配置的键
    print("\n📋 配置文件中的所有键:")
    for i, key in enumerate(config_data.keys(), 1):
        print(f"{i}. {key}")
    
    # 测试路径匹配逻辑
    test_files = [
        "D:/sjdataapp/AI比赛测试数据/华夏银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/招商银行.xlsx", 
        "D:/sjdataapp/AI比赛测试数据/北京银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/工商银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/建设银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/浦发银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/兴业银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/邮储银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/长安银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/中国银行.xlsx"
    ]
    
    print("\n🔍 测试路径匹配:")
    for test_file in test_files:
        print(f"\n测试文件: {test_file}")
        
        # 1. 尝试完整路径匹配
        if test_file in config_data:
            print(f"  ✅ 完整路径匹配成功")
            mappings = config_data[test_file]
            print(f"  📊 找到 {len(mappings)} 个映射")
            for mapping in mappings:
                print(f"    - {mapping.get('standard_field')} -> {mapping.get('imported_column')} (映射: {mapping.get('is_mapped')})")
            continue
        
        # 2. 尝试标准化路径匹配
        normalized_test = os.path.normpath(test_file)
        found = False
        for config_key in config_data.keys():
            if os.path.normpath(config_key) == normalized_test:
                print(f"  ✅ 标准化路径匹配成功: {config_key}")
                mappings = config_data[config_key]
                print(f"  📊 找到 {len(mappings)} 个映射")
                for mapping in mappings:
                    print(f"    - {mapping.get('standard_field')} -> {mapping.get('imported_column')} (映射: {mapping.get('is_mapped')})")
                found = True
                break
        
        if found:
            continue
            
        # 3. 尝试文件名匹配
        file_name = os.path.basename(test_file)
        for config_key in config_data.keys():
            if os.path.basename(config_key) == file_name:
                print(f"  ✅ 文件名匹配成功: {config_key}")
                mappings = config_data[config_key]
                print(f"  📊 找到 {len(mappings)} 个映射")
                for mapping in mappings:
                    print(f"    - {mapping.get('standard_field')} -> {mapping.get('imported_column')} (映射: {mapping.get('is_mapped')})")
                found = True
                break
        
        if not found:
            print(f"  ❌ 未找到匹配的映射配置")
    
    # 检查路径格式问题
    print("\n🔧 检查路径格式问题:")
    for config_key in config_data.keys():
        if "\\" in config_key and "/" in config_key:
            print(f"  ⚠️  混合路径分隔符: {config_key}")
        elif "\\" in config_key:
            print(f"  📁 使用反斜杠: {config_key}")
        elif "/" in config_key:
            print(f"  📁 使用正斜杠: {config_key}")

if __name__ == "__main__":
    test_field_mapping_loading()
