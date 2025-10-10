#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字段映射修复
"""

import os
import json
from resource_manager import ResourceManager

def test_mapping_fix():
    """测试字段映射修复"""
    print("🧪 测试字段映射修复")
    
    # 加载配置文件
    resource_manager = ResourceManager()
    config_data = resource_manager.load_json_config("config/field_mapping_config.json")
    
    if not config_data:
        print("❌ 无法加载字段映射配置")
        return
    
    print(f"✅ 成功加载字段映射配置，包含 {len(config_data)} 个文件")
    
    # 测试实际可能的文件路径
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
    success_count = 0
    
    for test_file in test_files:
        print(f"\n测试文件: {test_file}")
        
        # 模拟UI模块的匹配逻辑
        saved_mappings = None
        
        # 1. 尝试完整路径匹配
        if test_file in config_data:
            saved_mappings = config_data[test_file]
            print(f"  ✅ 完整路径匹配成功")
        
        # 2. 尝试标准化路径匹配
        if not saved_mappings:
            normalized_current = os.path.normpath(test_file)
            for config_key in config_data.keys():
                normalized_config = os.path.normpath(config_key)
                if normalized_config == normalized_current:
                    saved_mappings = config_data[config_key]
                    print(f"  ✅ 标准化路径匹配成功: {config_key}")
                    break
        
        # 3. 尝试文件名匹配
        if not saved_mappings:
            file_name = os.path.basename(test_file)
            for config_key in config_data.keys():
                if os.path.basename(config_key) == file_name:
                    saved_mappings = config_data[config_key]
                    print(f"  ✅ 文件名匹配成功: {config_key}")
                    break
        
        # 4. 尝试模糊匹配
        if not saved_mappings:
            file_name = os.path.basename(test_file)
            for config_key in config_data.keys():
                if file_name in config_key or config_key.endswith(file_name):
                    saved_mappings = config_data[config_key]
                    print(f"  ✅ 模糊匹配成功: {config_key}")
                    break
        
        if saved_mappings:
            print(f"  📊 找到 {len(saved_mappings)} 个映射")
            success_count += 1
            # 显示前3个映射作为示例
            for i, mapping in enumerate(saved_mappings[:3]):
                print(f"    {i+1}. {mapping.get('standard_field')} -> {mapping.get('imported_column')} (映射: {mapping.get('is_mapped')})")
            if len(saved_mappings) > 3:
                print(f"    ... 还有 {len(saved_mappings) - 3} 个映射")
        else:
            print(f"  ❌ 未找到匹配的映射配置")
    
    print(f"\n📈 测试结果: {success_count}/{len(test_files)} 个文件成功匹配")
    
    if success_count == len(test_files):
        print("🎉 所有文件都能成功匹配映射配置！")
    else:
        print("⚠️ 部分文件无法匹配，需要进一步检查")

if __name__ == "__main__":
    test_mapping_fix()
