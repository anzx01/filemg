#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def main():
    print("🔍 最终路径匹配测试")
    
    # 读取配置文件
    try:
        with open('dist/config/field_mapping_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 配置文件加载成功，包含 {len(config)} 个文件")
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return
    
    # 显示所有配置的路径
    print("\n📁 配置文件中的所有路径:")
    for i, path in enumerate(config.keys(), 1):
        print(f"  {i:2d}. {path}")
    
    # 测试路径
    test_files = [
        "D:/sjdataapp/AI比赛测试数据/华夏银行.xlsx",
        "D:/sjdataapp/AI比赛测试数据/建设银行.xlsx", 
        "D:/sjdataapp/AI比赛测试数据/招商银行.xlsx"
    ]
    
    print(f"\n🧪 测试 {len(test_files)} 个文件:")
    success_count = 0
    
    for test_file in test_files:
        print(f"\n测试: {test_file}")
        
        # 直接匹配
        if test_file in config:
            mappings = config[test_file]
            print(f"  ✅ 直接匹配成功！找到 {len(mappings)} 个字段映射")
            success_count += 1
        else:
            print(f"  ❌ 直接匹配失败")
            
            # 尝试标准化匹配
            normalized_test = os.path.normpath(test_file)
            found = False
            for config_key in config.keys():
                normalized_config = os.path.normpath(config_key)
                if normalized_config == normalized_test:
                    mappings = config[config_key]
                    print(f"  ✅ 标准化匹配成功！找到 {len(mappings)} 个字段映射")
                    success_count += 1
                    found = True
                    break
            
            if not found:
                print(f"  ❌ 所有匹配方式都失败")
    
    print(f"\n📊 最终结果: {success_count}/{len(test_files)} 个文件成功匹配")
    
    if success_count == len(test_files):
        print("🎉 所有测试文件都能成功匹配！路径修复完成！")
    else:
        print(f"⚠️ 还有 {len(test_files) - success_count} 个文件无法匹配")

if __name__ == "__main__":
    main()
