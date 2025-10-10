#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复字段映射配置文件中的路径格式不一致问题
"""

import json
import os
from resource_manager import ResourceManager

def fix_field_mapping_paths():
    """修复字段映射配置文件中的路径格式"""
    print("🔧 修复字段映射配置文件中的路径格式")
    
    # 加载现有配置
    resource_manager = ResourceManager()
    config_data = resource_manager.load_json_config("config/field_mapping_config.json")
    
    if not config_data:
        print("❌ 无法加载字段映射配置")
        return
    
    print(f"📊 原始配置包含 {len(config_data)} 个文件")
    
    # 标准化所有路径
    normalized_config = {}
    path_changes = []
    
    for old_path in config_data.keys():
        # 标准化路径：统一使用正斜杠
        normalized_path = old_path.replace("\\", "/")
        
        # 如果路径发生了变化，记录变化
        if normalized_path != old_path:
            path_changes.append((old_path, normalized_path))
            print(f"🔄 路径标准化: {old_path} -> {normalized_path}")
        
        normalized_config[normalized_path] = config_data[old_path]
    
    if path_changes:
        print(f"\n✅ 共标准化了 {len(path_changes)} 个路径")
        
        # 保存标准化后的配置
        try:
            with open("config/field_mapping_config.json", 'w', encoding='utf-8') as f:
                json.dump(normalized_config, f, ensure_ascii=False, indent=2)
            print("💾 配置文件已更新")
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
            return
    else:
        print("ℹ️  所有路径格式已经一致，无需修改")
    
    # 检查并补充缺失的标准字段映射
    print("\n🔍 检查缺失的标准字段映射")
    standard_fields = ["交易时间", "收入", "支出", "余额", "摘要", "对方户名"]
    
    for file_path, mappings in normalized_config.items():
        file_name = os.path.basename(file_path)
        existing_fields = {mapping.get('standard_field') for mapping in mappings}
        missing_fields = set(standard_fields) - existing_fields
        
        if missing_fields:
            print(f"⚠️  {file_name} 缺少字段: {', '.join(missing_fields)}")
        else:
            print(f"✅ {file_name} 包含所有标准字段")

if __name__ == "__main__":
    fix_field_mapping_paths()
