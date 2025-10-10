#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试路径匹配修复
"""

import os
import json
from resource_manager import ResourceManager

def quick_test():
    """快速测试路径匹配"""
    print("🧪 快速测试路径匹配修复")
    
    # 加载配置文件
    resource_manager = ResourceManager()
    config_data = resource_manager.load_json_config("config/field_mapping_config.json")
    
    if not config_data:
        print("❌ 无法加载字段映射配置")
        return
    
    print(f"✅ 成功加载字段映射配置，包含 {len(config_data)} 个文件")
    
    # 显示配置文件中的所有路径
    print("\n📁 配置文件中的路径:")
    for i, path in enumerate(config_data.keys(), 1):
        print(f"  {i}. {path}")
    
    # 测试几个关键路径
    test_files = [
        "D:/sjdataapp/AI比赛测试数据/华夏银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/建设银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/招商银行.xlsx"
    ]
    
    print(f"\n🔍 测试路径匹配:")
    success_count = 0
    
    for test_file in test_files:
        print(f"\n测试文件: {test_file}")
        
        # 1. 尝试完整路径匹配
        if test_file in config_data:
            mappings = config_data[test_file]
            print(f"  ✅ 完整路径匹配成功，找到 {len(mappings)} 个映射")
            success_count += 1
        else:
            print(f"  ❌ 完整路径匹配失败")
            
            # 2. 尝试标准化路径匹配
            normalized_current = os.path.normpath(test_file)
            found = False
            for config_key in config_data.keys():
                normalized_config = os.path.normpath(config_key)
                if normalized_config == normalized_current:
                    mappings = config_data[config_key]
                    print(f"  ✅ 标准化路径匹配成功: {config_key}，找到 {len(mappings)} 个映射")
                    success_count += 1
                    found = True
                    break
            
            if not found:
                print(f"  ❌ 标准化路径匹配也失败")
    
    print(f"\n📈 测试结果: {success_count}/{len(test_files)} 个文件成功匹配")
    
    if success_count == len(test_files):
        print("🎉 所有测试文件都能成功匹配映射配置！")
    else:
        print("⚠️ 部分文件无法匹配，需要进一步检查")

if __name__ == "__main__":
    quick_test()
