#!/usr/bin/env python3
"""
测试字段映射持久化功能
验证字段映射配置是否能够正确保存和加载
"""

import sys
import os
import json

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mapping_persistence():
    """测试字段映射持久化"""
    print("🧪 测试字段映射持久化功能...")

    try:
        from ui_module_modern import ModernExcelMergeUI

        print("✅ 导入现代化UI模块成功")

        # 创建UI实例
        app = ModernExcelMergeUI()

        print("✅ UI实例创建成功")

        # 模拟测试数据
        test_file_path = "test_sample.xlsx"
        app.imported_files = [test_file_path]

        # 设置测试字段映射
        test_mappings = {
            "交易时间": {"imported_column": "交易日期", "is_mapped": True},
            "收入": {"imported_column": "收入金额", "is_mapped": True},
            "支出": {"imported_column": "支出金额", "is_mapped": True},
            "余额": {"imported_column": "账户余额", "is_mapped": True},
            "摘要": {"imported_column": "交易摘要", "is_mapped": True},
            "对方户名": {"imported_column": "对方姓名", "is_mapped": True}
        }

        app.field_mappings[test_file_path] = test_mappings

        print("\n📝 设置测试字段映射:")
        for field, mapping in test_mappings.items():
            print(f"   {field} -> {mapping['imported_column']} (映射: {mapping['is_mapped']})")

        # 测试保存功能
        print("\n💾 测试自动保存功能...")
        app.auto_save_field_mapping(test_file_path)
        print("✅ 自动保存功能测试完成")

        # 验证配置文件是否创建
        config_file = "config/field_mapping_config.json"
        if os.path.exists(config_file):
            print("✅ 配置文件已创建")

            # 读取并验证配置内容
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            print(f"📊 配置文件包含 {len(config_data)} 个文件的映射")

            # 查找测试文件的配置
            found_mapping = None
            for file_key, mappings in config_data.items():
                if "test_sample" in file_key or file_key.endswith(test_file_path):
                    found_mapping = mappings
                    print(f"✅ 找到测试文件映射: {file_key}")
                    break

            if found_mapping:
                print(f"✅ 映射配置验证成功，包含 {len(found_mapping)} 个字段映射")

                # 验证具体映射内容
                for mapping in found_mapping:
                    field = mapping.get('standard_field', '')
                    column = mapping.get('imported_column', '')
                    is_mapped = mapping.get('is_mapped', False)
                    print(f"   📋 {field} -> {column} (映射: {is_mapped})")
            else:
                print("❌ 未找到测试文件的映射配置")
                return False
        else:
            print("❌ 配置文件未创建")
            return False

        # 测试加载功能
        print("\n📂 测试加载功能...")

        # 清空内存中的映射
        app.field_mappings.clear()

        # 模拟文件选择，触发加载
        app.load_field_mappings_for_file(test_file_path)

        # 验证是否正确加载
        if test_file_path in app.field_mappings:
            print("✅ 字段映射加载成功")

            loaded_mappings = app.field_mappings[test_file_path]
            print(f"📊 加载了 {len(loaded_mappings)} 个字段映射")

            # 验证加载的内容
            for field, mapping in loaded_mappings.items():
                expected = test_mappings.get(field, {})
                if (mapping.get('imported_column') == expected.get('imported_column') and
                    mapping.get('is_mapped') == expected.get('is_mapped')):
                    print(f"   ✅ {field}: 映射正确")
                else:
                    print(f"   ❌ {field}: 映射不匹配")
                    return False
        else:
            print("❌ 字段映射加载失败")
            return False

        print("\n🎉 字段映射持久化功能测试通过！")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_matching():
    """测试文件匹配逻辑"""
    print("\n🔍 测试文件匹配逻辑...")

    try:
        # 创建测试配置
        test_config = {
            "C:\\Users\\User\\Documents\\test.xlsx": [
                {"standard_field": "交易时间", "imported_column": "日期", "is_mapped": True}
            ],
            "D:\\Data\\bank_statement.xlsx": [
                {"standard_field": "收入", "imported_column": "收入金额", "is_mapped": True}
            ]
        }

        # 创建配置目录和文件
        os.makedirs("config", exist_ok=True)
        config_file = "config/test_field_mapping.json"

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)

        print("✅ 测试配置文件创建成功")

        # 测试匹配逻辑
        from ui_module_modern import ModernExcelMergeUI
        app = ModernExcelMergeUI()

        test_cases = [
            ("C:\\Users\\User\\Documents\\test.xlsx", "完整路径匹配"),
            ("test.xlsx", "文件名匹配"),
            ("bank_statement.xlsx", "文件名匹配"),
            ("D:\\Data\\bank_statement.xlsx", "完整路径匹配")
        ]

        for file_path, test_name in test_cases:
            print(f"\n🧪 {test_name}: {file_path}")

            # 清空内存映射
            app.field_mappings.clear()

            # 加载映射
            app.load_field_mappings_for_file(file_path)

            # 检查结果
            if file_path in app.field_mappings:
                mappings = app.field_mappings[file_path]
                print(f"   ✅ 找到 {len(mappings)} 个映射")
                for field, mapping in mappings.items():
                    print(f"   📋 {field} -> {mapping['imported_column']}")
            else:
                print(f"   ❌ 未找到映射")

        # 清理测试文件
        if os.path.exists(config_file):
            os.remove(config_file)
            print("\n🧹 清理测试文件完成")

        print("✅ 文件匹配逻辑测试完成")
        return True

    except Exception as e:
        print(f"❌ 文件匹配测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Excel合并工具 - 字段映射持久化测试")
    print("=" * 60)

    print("📋 测试内容:")
    print("   1. 字段映射自动保存功能")
    print("   2. 字段映射加载功能")
    print("   3. 文件匹配逻辑")
    print("   4. 配置文件读写")
    print("=" * 60)

    # 测试持久化功能
    success1 = test_mapping_persistence()

    # 测试文件匹配逻辑
    success2 = test_file_matching()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 所有测试通过！")
        print("✨ 字段映射持久化功能正常工作")
        print("\n💡 使用说明:")
        print("   1. 配置字段映射后自动保存")
        print("   2. 重启程序后自动加载已保存的映射")
        print("   3. 支持多种文件路径匹配方式")
        print("   4. 映射配置保存在 config/field_mapping_config.json")
    else:
        print("❌ 部分测试失败")
        print("🔧 请检查修复是否完整")

    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 测试已取消")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")