#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试路径匹配
"""

import os
import json
from resource_manager import ResourceManager

def detailed_test():
    """详细测试路径匹配"""
    print("🔍 详细测试路径匹配")
    
    # 加载配置文件
    resource_manager = ResourceManager()
    config_data = resource_manager.load_json_config("config/field_mapping_config.json")
    
    if not config_data:
        print("❌ 无法加载字段映射配置")
        return
    
    print(f"✅ 成功加载字段映射配置，包含 {len(config_data)} 个文件")
    
    # 显示配置文件中的所有路径
    print("\n📁 配置文件中的所有路径:")
    for i, path in enumerate(config_data.keys(), 1):
        print(f"  {i:2d}. {path}")
    
    # 测试几个关键路径
    test_files = [
        "D:/sjdataapp/AI比赛测试数据/华夏银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/建设银行.xlsx", 
        "D:/sjdataapp/AI比赛测试数据/招商银行.xlsx"
    ]
    
    print(f"\n🔍 详细测试路径匹配:")
    
    for test_file in test_files:
        print(f"\n{'='*60}")
        print(f"测试文件: {test_file}")
        print(f"{'='*60}")
        
        # 1. 尝试完整路径匹配
        if test_file in config_data:
            mappings = config_data[test_file]
            print(f"✅ 完整路径匹配成功！")
            print(f"   找到 {len(mappings)} 个字段映射:")
            for mapping in mappings:
                print(f"     - {mapping['standard_field']} ← {mapping['imported_column']}")
        else:
            print(f"❌ 完整路径匹配失败")
            
            # 2. 尝试标准化路径匹配
            normalized_current = os.path.normpath(test_file)
            print(f"   标准化当前路径: {normalized_current}")
            
            found = False
            for config_key in config_data.keys():
                normalized_config = os.path.normpath(config_key)
                print(f"   比较: {normalized_config}")
                if normalized_config == normalized_current:
                    mappings = config_data[config_key]
                    print(f"   ✅ 标准化路径匹配成功！")
                    print(f"   原始配置键: {config_key}")
                    print(f"   找到 {len(mappings)} 个字段映射:")
                    for mapping in mappings:
                        print(f"     - {mapping['standard_field']} ← {mapping['imported_column']}")
                    found = True
                    break
            
            if not found:
                print(f"   ❌ 标准化路径匹配也失败")
                
                # 3. 尝试部分匹配
                print(f"   🔍 尝试部分匹配...")
                filename = os.path.basename(test_file)
                print(f"   文件名: {filename}")
                
                partial_matches = []
                for config_key in config_data.keys():
                    config_filename = os.path.basename(config_key)
                    if filename == config_filename:
                        partial_matches.append(config_key)
                
                if partial_matches:
                    print(f"   ✅ 找到 {len(partial_matches)} 个文件名匹配:")
                    for match in partial_matches:
                        print(f"     - {match}")
                else:
                    print(f"   ❌ 没有找到文件名匹配")

if __name__ == "__main__":
    detailed_test()
