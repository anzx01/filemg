#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试路径匹配
"""

import json
import os

def simple_test():
    """简单测试路径匹配"""
    print("🧪 简单测试路径匹配")
    
    # 直接读取配置文件
    config_path = "dist/config/field_mapping_config.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        print(f"✅ 成功加载配置文件，包含 {len(config_data)} 个文件")
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return
    
    # 测试文件列表
    test_files = [
        "D:/sjdataapp/AI比赛测试数据/华夏银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/建设银行.xlsx", 
        "D:/sjdataapp/AI比赛测试数据/招商银行.xlsx"
    ]
    
    print(f"\n🔍 测试路径匹配:")
    success_count = 0
    
    for test_file in test_files:
        print(f"\n测试: {test_file}")
        
        # 直接匹配
        if test_file in config_data:
            mappings = config_data[test_file]
            print(f"  ✅ 直接匹配成功，找到 {len(mappings)} 个映射")
            success_count += 1
        else:
            print(f"  ❌ 直接匹配失败")
            
            # 标准化匹配
            normalized_test = os.path.normpath(test_file)
            found = False
            for config_key in config_data.keys():
                normalized_config = os.path.normpath(config_key)
                if normalized_config == normalized_test:
                    mappings = config_data[config_key]
                    print(f"  ✅ 标准化匹配成功，找到 {len(mappings)} 个映射")
                    success_count += 1
                    found = True
                    break
            
            if not found:
                print(f"  ❌ 标准化匹配也失败")
    
    print(f"\n📊 测试结果: {success_count}/{len(test_files)} 个文件成功匹配")
    
    if success_count == len(test_files):
        print("🎉 所有测试文件都能成功匹配！")
        return True
    else:
        print("⚠️ 部分文件无法匹配")
        return False

if __name__ == "__main__":
    simple_test()
