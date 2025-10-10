#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试字段映射显示问题
"""

import os
import json
from resource_manager import ResourceManager

def debug_mapping_issue():
    """调试字段映射显示问题"""
    print("🔍 调试字段映射显示问题")
    
    # 使用资源管理器加载配置
    resource_manager = ResourceManager()
    config_data = resource_manager.load_json_config("config/field_mapping_config.json")
    
    if not config_data:
        print("❌ 无法加载字段映射配置")
        return
    
    print(f"✅ 成功加载字段映射配置，包含 {len(config_data)} 个文件")
    
    # 测试问题银行文件
    problem_banks = [
        "D:/sjdataapp/AI比赛测试数据/建设银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/浦发银行.xlsx", 
        "D:/sjdataapp/AI比赛测试数据/兴业银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/邮储银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/长安银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/中国银行.xlsx"
    ]
    
    print(f"\n🧪 测试 {len(problem_banks)} 个问题银行文件:")
    
    for bank_file in problem_banks:
        print(f"\n{'='*60}")
        print(f"测试文件: {bank_file}")
        print(f"{'='*60}")
        
        # 1. 检查配置文件中的键
        print(f"1. 配置文件中的键:")
        found_keys = []
        bank_name = os.path.basename(bank_file).replace('.xlsx', '')
        for key in config_data.keys():
            if bank_name in key:
                found_keys.append(key)
                print(f"   ✅ 找到: {key}")
        
        if not found_keys:
            print(f"   ❌ 未找到包含 '{bank_name}' 的键")
            continue
        
        # 2. 尝试各种匹配方式
        print(f"\n2. 尝试匹配方式:")
        
        # 直接匹配
        if bank_file in config_data:
            mappings = config_data[bank_file]
            print(f"   ✅ 直接匹配成功！找到 {len(mappings)} 个映射")
            print_mappings(mappings)
        else:
            print(f"   ❌ 直接匹配失败")
            
            # 标准化路径匹配
            normalized_bank = os.path.normpath(bank_file)
            found = False
            for config_key in config_data.keys():
                normalized_config = os.path.normpath(config_key)
                if normalized_config == normalized_bank:
                    mappings = config_data[config_key]
                    print(f"   ✅ 标准化路径匹配成功！找到 {len(mappings)} 个映射")
                    print_mappings(mappings)
                    found = True
                    break
            
            if not found:
                print(f"   ❌ 标准化路径匹配失败")
                
                # 文件名匹配
                file_name = os.path.basename(bank_file)
                for config_key in config_data.keys():
                    if os.path.basename(config_key) == file_name:
                        mappings = config_data[config_key]
                        print(f"   ✅ 文件名匹配成功！找到 {len(mappings)} 个映射")
                        print_mappings(mappings)
                        found = True
                        break
                
                if not found:
                    print(f"   ❌ 文件名匹配失败")
                    
                    # 模糊匹配
                    for config_key in config_data.keys():
                        if file_name in config_key or config_key.endswith(file_name):
                            mappings = config_data[config_key]
                            print(f"   ✅ 模糊匹配成功！找到 {len(mappings)} 个映射")
                            print_mappings(mappings)
                            found = True
                            break
                    
                    if not found:
                        print(f"   ❌ 所有匹配方式都失败")

def print_mappings(mappings):
    """打印映射详情"""
    print(f"   📋 映射详情:")
    for i, mapping in enumerate(mappings, 1):
        standard_field = mapping.get('standard_field', '')
        imported_column = mapping.get('imported_column', '')
        is_mapped = mapping.get('is_mapped', False)
        print(f"      {i}. {standard_field} -> {imported_column} (映射: {is_mapped})")

if __name__ == "__main__":
    debug_mapping_issue()
