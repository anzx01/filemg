"""
Excel文档合并工具 - 字段映射模块测试脚本
测试字段映射功能的完整性和正确性
"""

import os
import sys
import pandas as pd
from field_mapping import FieldMappingManager, StandardField, FieldMapping


def test_field_mapping_module():
    """测试字段映射模块"""
    print("=" * 60)
    print("Excel文档合并工具 - 字段映射模块测试")
    print("=" * 60)
    
    # 创建测试目录
    test_dir = "test_output"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # 测试1: 字段映射管理器初始化
        print("测试字段映射管理器初始化...")
        manager = FieldMappingManager(config_dir=test_dir)
        print("✓ 字段映射管理器初始化成功")
        
        # 测试2: 标准字段管理
        print("\n测试标准字段管理...")
        
        # 获取预定义字段
        standard_fields = manager.get_standard_fields()
        print(f"✓ 预定义标准字段数量: {len(standard_fields)}")
        
        # 添加自定义字段
        custom_field = StandardField(
            name="custom_field",
            display_name="自定义字段",
            data_type="string",
            required=False,
            description="测试自定义字段"
        )
        
        success = manager.add_standard_field(custom_field)
        if success:
            print("✓ 添加自定义字段成功")
        else:
            print("✗ 添加自定义字段失败")
        
        # 测试3: 字段映射管理
        print("\n测试字段映射管理...")
        
        # 创建测试映射
        test_mapping = FieldMapping(
            file_id="test_file_1",
            file_name="test_file_1.xlsx",
            standard_field="account_number",
            file_field="账户号码",
            mapping_type="direct",
            is_active=True
        )
        
        success = manager.add_field_mapping(test_mapping)
        if success:
            print("✓ 添加字段映射成功")
        else:
            print("✗ 添加字段映射失败")
        
        # 查询映射
        retrieved_mapping = manager.get_field_mapping("test_file_1", "account_number")
        if retrieved_mapping:
            print("✓ 查询字段映射成功")
        else:
            print("✗ 查询字段映射失败")
        
        # 测试4: 智能映射建议
        print("\n测试智能映射建议...")
        
        test_columns = ["账户号码", "户名", "交易日期", "金额", "余额", "交易类型", "备注"]
        
        # 测试不同标准字段的映射建议
        test_fields = ["account_number", "account_name", "transaction_date", "transaction_amount", "balance"]
        
        for field in test_fields:
            suggestion = manager.suggest_mapping(test_columns, field)
            if suggestion:
                print(f"✓ {field} 映射建议: {suggestion}")
            else:
                print(f"✗ {field} 映射建议失败")
        
        # 测试5: 映射验证
        print("\n测试映射验证...")
        
        # 有效映射
        valid_mapping = FieldMapping(
            file_id="test_file_2",
            file_name="test_file_2.xlsx",
            standard_field="account_number",
            file_field="账户号码",
            mapping_type="direct"
        )
        
        is_valid, message = manager.validate_mapping(valid_mapping)
        if is_valid:
            print("✓ 有效映射验证通过")
        else:
            print(f"✗ 有效映射验证失败: {message}")
        
        # 无效映射（不存在的标准字段）
        invalid_mapping = FieldMapping(
            file_id="test_file_3",
            file_name="test_file_3.xlsx",
            standard_field="non_existent_field",
            file_field="某字段",
            mapping_type="direct"
        )
        
        is_valid, message = manager.validate_mapping(invalid_mapping)
        if not is_valid:
            print("✓ 无效映射验证正确")
        else:
            print("✗ 无效映射验证失败")
        
        # 测试6: 配置文件操作
        print("\n测试配置文件操作...")
        
        # 导出映射模板
        template_path = os.path.join(test_dir, "mapping_template.json")
        success = manager.export_mapping_template(template_path)
        if success and os.path.exists(template_path):
            print("✓ 导出映射模板成功")
        else:
            print("✗ 导出映射模板失败")
        
        # 测试7: 文件列名获取
        print("\n测试文件列名获取...")
        
        # 创建测试Excel文件
        test_excel_path = os.path.join(test_dir, "test_file.xlsx")
        test_data = {
            "账户号码": ["1234567890", "0987654321"],
            "户名": ["张三", "李四"],
            "交易日期": ["2025-01-01", "2025-01-02"],
            "金额": [1000.00, -500.00],
            "余额": [5000.00, 4500.00]
        }
        
        df = pd.DataFrame(test_data)
        df.to_excel(test_excel_path, index=False)
        
        columns = manager.get_file_columns(test_excel_path)
        if columns:
            print(f"✓ 获取文件列名成功: {columns}")
        else:
            print("✗ 获取文件列名失败")
        
        # 测试8: 批量映射操作
        print("\n测试批量映射操作...")
        
        # 添加多个映射
        mappings = [
            FieldMapping("test_file_1", "test_file_1.xlsx", "account_name", "户名", "direct"),
            FieldMapping("test_file_1", "test_file_1.xlsx", "transaction_date", "交易日期", "direct"),
            FieldMapping("test_file_1", "test_file_1.xlsx", "transaction_amount", "金额", "direct"),
            FieldMapping("test_file_1", "test_file_1.xlsx", "balance", "余额", "direct")
        ]
        
        success_count = 0
        for mapping in mappings:
            if manager.add_field_mapping(mapping):
                success_count += 1
        
        if success_count == len(mappings):
            print(f"✓ 批量添加映射成功: {success_count}/{len(mappings)}")
        else:
            print(f"✗ 批量添加映射失败: {success_count}/{len(mappings)}")
        
        # 获取文件的所有映射
        file_mappings = manager.get_file_mappings("test_file_1")
        print(f"✓ 获取文件映射数量: {len(file_mappings)}")
        
        # 测试9: 映射更新
        print("\n测试映射更新...")
        
        success = manager.update_field_mapping(
            "test_file_1", "account_number", "新账户号码", "transform", "upper()"
        )
        if success:
            print("✓ 更新字段映射成功")
        else:
            print("✗ 更新字段映射失败")
        
        # 验证更新
        updated_mapping = manager.get_field_mapping("test_file_1", "account_number")
        if updated_mapping and updated_mapping.file_field == "新账户号码":
            print("✓ 映射更新验证成功")
        else:
            print("✗ 映射更新验证失败")
        
        # 测试10: 映射删除
        print("\n测试映射删除...")
        
        success = manager.remove_field_mapping("test_file_1", "account_name")
        if success:
            print("✓ 删除字段映射成功")
        else:
            print("✗ 删除字段映射失败")
        
        # 验证删除
        deleted_mapping = manager.get_field_mapping("test_file_1", "account_name")
        if not deleted_mapping:
            print("✓ 映射删除验证成功")
        else:
            print("✗ 映射删除验证失败")
        
        print("\n" + "=" * 60)
        print("字段映射模块测试完成")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理测试文件
        try:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
            print("✓ 测试文件清理完成")
        except Exception as e:
            print(f"清理测试文件失败: {e}")


def test_integration():
    """测试集成功能"""
    print("\n" + "=" * 60)
    print("集成测试 - 字段映射与界面模块")
    print("=" * 60)
    
    try:
        # 测试界面模块导入字段映射管理器
        from ui_module import ExcelMergeUI
        
        # 创建界面实例（不显示）
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        ui = ExcelMergeUI()
        
        # 测试字段映射管理器是否正常初始化
        if hasattr(ui, 'field_mapping_manager'):
            print("✓ 界面模块成功集成字段映射管理器")
        else:
            print("✗ 界面模块未集成字段映射管理器")
        
        # 测试标准字段刷新
        ui.refresh_standard_fields()
        print("✓ 标准字段刷新功能正常")
        
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("开始字段映射模块测试...")
    
    # 运行基础测试
    basic_test_result = test_field_mapping_module()
    
    # 运行集成测试
    integration_test_result = test_integration()
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"基础功能测试: {'✓ 通过' if basic_test_result else '✗ 失败'}")
    print(f"集成功能测试: {'✓ 通过' if integration_test_result else '✗ 失败'}")
    
    if basic_test_result and integration_test_result:
        print("\n🎉 所有字段映射功能测试通过！")
        print("字段映射模块已准备就绪，可以开始下一阶段开发。")
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")


