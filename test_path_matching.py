#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试路径匹配问题
"""

import os
import json
from resource_manager import ResourceManager

def test_path_matching():
    """测试路径匹配问题"""
    print("🔍 测试路径匹配问题")
    
    # 使用资源管理器加载配置
    resource_manager = ResourceManager()
    config_data = resource_manager.load_json_config("config/field_mapping_config.json")
    
    if not config_data:
        print("❌ 无法加载字段映射配置")
        return
    
    print(f"✅ 成功加载字段映射配置，包含 {len(config_data)} 个文件")
    
    # 测试问题银行文件
    test_files = [
        "D:/sjdataapp/AI比赛测试数据/建设银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/浦发银行.xlsx", 
        "D:/sjdataapp/AI比赛测试数据/兴业银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/邮储银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/长安银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/中国银行.xlsx"
    ]
    
    print(f"\n🧪 测试 {len(test_files)} 个问题银行文件:")
    
    for test_file in test_files:
        print(f"\n{'='*60}")
        print(f"测试文件: {test_file}")
        print(f"{'='*60}")
        
        # 1. 直接匹配
        if test_file in config_data:
            mappings = config_data[test_file]
            print(f"✅ 直接匹配成功！找到 {len(mappings)} 个映射")
            print_mappings(mappings)
            continue
        else:
            print(f"❌ 直接匹配失败")
        
        # 2. 标准化路径匹配
        normalized_test = os.path.normpath(test_file)
        found = False
        for config_key in config_data.keys():
            normalized_config = os.path.normpath(config_key)
            if normalized_config == normalized_test:
                mappings = config_data[config_key]
                print(f"✅ 标准化路径匹配成功！找到 {len(mappings)} 个映射")
                print(f"   配置键: {config_key}")
                print(f"   标准化后: {normalized_config}")
                print_mappings(mappings)
                found = True
                break
        
        if not found:
            print(f"❌ 标准化路径匹配失败")
            print(f"   测试文件标准化后: {normalized_test}")
            
            # 3. 文件名匹配
            file_name = os.path.basename(test_file)
            for config_key in config_data.keys():
                if os.path.basename(config_key) == file_name:
                    mappings = config_data[config_key]
                    print(f"✅ 文件名匹配成功！找到 {len(mappings)} 个映射")
                    print(f"   配置键: {config_key}")
                    print_mappings(mappings)
                    found = True
                    break
            
            if not found:
                print(f"❌ 文件名匹配失败")
                
                # 4. 路径替换匹配
                for config_key in config_data.keys():
                    normalized_config_key = config_key.replace('\\', '/')
                    if normalized_config_key == test_file:
                        mappings = config_data[config_key]
                        print(f"✅ 路径替换匹配成功！找到 {len(mappings)} 个映射")
                        print(f"   配置键: {config_key}")
                        print(f"   替换后: {normalized_config_key}")
                        print_mappings(mappings)
                        found = True
                        break
                
                if not found:
                    print(f"❌ 所有匹配方式都失败")
                    print(f"   测试文件: {test_file}")
                    print(f"   可用配置键示例:")
                    for i, key in enumerate(list(config_data.keys())[:3]):
                        print(f"     {i+1}. {key}")

def print_mappings(mappings):
    """打印映射详情"""
    print(f"   📋 映射详情:")
    for i, mapping in enumerate(mappings, 1):
        standard_field = mapping.get('standard_field', '')
        imported_column = mapping.get('imported_column', '')
        is_mapped = mapping.get('is_mapped', False)
        print(f"      {i}. {standard_field} -> {imported_column} (映射: {is_mapped})")

if __name__ == "__main__":
    test_path_matching()