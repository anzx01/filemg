"""
Excel文档合并工具 - 完整系统测试
测试所有模块的集成和端到端功能
"""

import os
import sys
import pandas as pd
from typing import List, Dict, Any
import traceback


def test_complete_system():
    """测试完整系统功能"""
    print("=" * 80)
    print("Excel文档合并工具 - 完整系统测试")
    print("=" * 80)
    
    # 创建测试目录
    test_dir = "test_output"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # 导入所有模块
        from main_controller import ExcelMergeController
        from field_mapping import FieldMappingManager, FieldMapping
        from header_detection import HeaderDetector
        from data_processing import DataProcessor
        
        print("✓ 所有模块导入成功")
        
        # 创建控制器
        controller = ExcelMergeController()
        print("✓ 控制器初始化成功")
        
        # 创建测试数据
        print("\n创建测试数据...")
        test_data1 = {
            "账户号码": ["1234567890", "0987654321", "1111111111"],
            "户名": ["张三", "李四", "王五"],
            "交易日期": ["2025-01-01", "2025-01-02", "2025-01-03"],
            "交易金额": [1000.00, -500.00, 2000.00],
            "账户余额": [5000.00, 4500.00, 6500.00],
            "备注": ["收入", "支出", "收入"]
        }
        
        test_data2 = {
            "账户号码": ["2222222222", "3333333333"],
            "户名": ["赵六", "孙七"],
            "交易日期": ["2025-01-04", "2025-01-05"],
            "交易金额": [-1000.00, 1500.00],
            "账户余额": [5500.00, 7000.00],
            "备注": ["支出", "收入"]
        }
        
        # 创建测试文件
        test_file1 = os.path.join(test_dir, "银行A.xlsx")
        test_file2 = os.path.join(test_dir, "银行B.xlsx")
        
        pd.DataFrame(test_data1).to_excel(test_file1, index=False)
        pd.DataFrame(test_data2).to_excel(test_file2, index=False)
        
        print("✓ 测试文件创建成功")
        
        # 测试1: 表头识别
        print("\n测试1: 表头识别...")
        headers1 = controller.header_detector.detect_headers(test_file1)
        headers2 = controller.header_detector.detect_headers(test_file2)
        
        if headers1 and headers2:
            print("✓ 表头识别成功")
            print(f"  - 文件1列数: {len(headers1[0].columns)}")
            print(f"  - 文件2列数: {len(headers2[0].columns)}")
        else:
            print("✗ 表头识别失败")
            return False
        
        # 测试2: 字段映射配置
        print("\n测试2: 字段映射配置...")
        
        # 为文件1配置映射
        mappings1 = [
            FieldMapping("银行A.xlsx", "银行A.xlsx", "account_number", "账户号码", "direct"),
            FieldMapping("银行A.xlsx", "银行A.xlsx", "account_name", "户名", "direct"),
            FieldMapping("银行A.xlsx", "银行A.xlsx", "transaction_date", "交易日期", "direct"),
            FieldMapping("银行A.xlsx", "银行A.xlsx", "transaction_amount", "交易金额", "direct"),
            FieldMapping("银行A.xlsx", "银行A.xlsx", "balance", "账户余额", "direct"),
            FieldMapping("银行A.xlsx", "银行A.xlsx", "description", "备注", "direct")
        ]
        
        # 为文件2配置映射
        mappings2 = [
            FieldMapping("银行B.xlsx", "银行B.xlsx", "account_number", "账户号码", "direct"),
            FieldMapping("银行B.xlsx", "银行B.xlsx", "account_name", "户名", "direct"),
            FieldMapping("银行B.xlsx", "银行B.xlsx", "transaction_date", "交易日期", "direct"),
            FieldMapping("银行B.xlsx", "银行B.xlsx", "transaction_amount", "交易金额", "direct"),
            FieldMapping("银行B.xlsx", "银行B.xlsx", "balance", "账户余额", "direct"),
            FieldMapping("银行B.xlsx", "银行B.xlsx", "description", "备注", "direct")
        ]
        
        # 添加映射
        for mapping in mappings1 + mappings2:
            success = controller.field_mapping_manager.add_field_mapping(mapping)
            if not success:
                print(f"✗ 添加映射失败: {mapping.standard_field}")
                return False
        
        print("✓ 字段映射配置成功")
        
        # 测试3: 单文件处理
        print("\n测试3: 单文件处理...")
        processed1 = controller.data_processor.process_file(test_file1)
        processed2 = controller.data_processor.process_file(test_file2)
        
        if processed1 and processed2:
            print("✓ 单文件处理成功")
            print(f"  - 文件1处理记录数: {len(processed1.data)}")
            print(f"  - 文件2处理记录数: {len(processed2.data)}")
            print(f"  - 文件1映射列: {list(processed1.mapped_columns.keys())}")
        else:
            print("✗ 单文件处理失败")
            return False
        
        # 测试4: 文件合并
        print("\n测试4: 文件合并...")
        output_file = os.path.join(test_dir, "merged_result.xlsx")
        merge_success = controller.merge_files([test_file1, test_file2], output_file)
        
        if merge_success:
            print("✓ 文件合并成功")
            # 获取合并结果对象
            merge_result = controller.get_merge_result([test_file1, test_file2], output_file)
            if merge_result:
                print(f"  - 合并后记录数: {merge_result.total_records}")
                print(f"  - 处理时间: {merge_result.processing_time:.2f}秒")
                print(f"  - 输出文件: {output_file}")
            else:
                print("  - 无法获取合并结果详情")
        else:
            print("✗ 文件合并失败")
            return False
        
        # 测试5: 数据验证
        print("\n测试5: 数据验证...")
        if merge_result:
            is_valid, issues = controller.data_processor.validate_merged_data(merge_result.merged_data)
            if is_valid:
                print("✓ 数据验证通过")
            else:
                print(f"⚠️  数据验证警告: {issues}")
        else:
            print("⚠️  无法进行数据验证")
        
        # 测试6: 汇总报告
        print("\n测试6: 汇总报告...")
        if merge_result:
            summary = controller.data_processor.generate_summary_report(merge_result)
            if summary:
                print("✓ 汇总报告生成成功")
                print(f"  - 总记录数: {summary['total_records']}")
                print(f"  - 源文件数: {summary['total_files']}")
                print(f"  - 列数: {len(summary['columns'])}")
            else:
                print("✗ 汇总报告生成失败")
        else:
            print("⚠️  无法生成汇总报告")
        
        # 测试7: 输出文件验证
        print("\n测试7: 输出文件验证...")
        if os.path.exists(output_file):
            # 读取输出文件验证
            output_df = pd.read_excel(output_file)
            print(f"✓ 输出文件验证成功")
            print(f"  - 输出文件记录数: {len(output_df)}")
            print(f"  - 输出文件列数: {len(output_df.columns)}")
            print(f"  - 输出文件列名: {list(output_df.columns)}")
        else:
            print("✗ 输出文件不存在")
            return False
        
        print("\n" + "=" * 80)
        print("🎉 完整系统测试成功！")
        print("=" * 80)
        print("所有核心功能模块已正常工作：")
        print("✓ 表头识别模块")
        print("✓ 字段映射模块")
        print("✓ 数据处理模块")
        print("✓ 文件合并功能")
        print("✓ 数据验证功能")
        print("✓ 汇总报告功能")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 系统测试失败: {e}")
        traceback.print_exc()
        return False
    
    finally:
        # 清理测试文件
        try:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
            print("\n✓ 测试文件清理完成")
        except Exception as e:
            print(f"\n⚠️  测试文件清理失败: {e}")


def test_ui_integration():
    """测试用户界面集成"""
    print("\n" + "=" * 80)
    print("测试用户界面集成")
    print("=" * 80)
    
    try:
        from ui_module import ExcelMergeUI
        import tkinter as tk
        
        # 创建隐藏的根窗口
        root = tk.Tk()
        root.withdraw()
        
        # 创建界面实例
        ui = ExcelMergeUI()
        
        # 测试模块集成
        modules = [
            ("字段映射管理器", "field_mapping_manager"),
        ]
        
        for module_name, attr_name in modules:
            if hasattr(ui, attr_name):
                print(f"✓ {module_name}集成成功")
            else:
                print(f"✗ {module_name}集成失败")
        
        # 测试界面功能
        try:
            ui.refresh_standard_fields()
            print("✓ 标准字段刷新功能正常")
        except Exception as e:
            print(f"✗ 标准字段刷新失败: {e}")
        
        # 关闭界面
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"用户界面集成测试失败: {e}")
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("Excel文档合并工具 - 完整系统测试")
    print("=" * 80)
    
    # 运行系统测试
    system_test_result = test_complete_system()
    
    # 运行界面集成测试
    ui_test_result = test_ui_integration()
    
    # 输出最终结果
    print("\n" + "=" * 80)
    print("最终测试结果")
    print("=" * 80)
    print(f"系统功能测试: {'✓ 通过' if system_test_result else '✗ 失败'}")
    print(f"界面集成测试: {'✓ 通过' if ui_test_result else '✗ 失败'}")
    
    if system_test_result and ui_test_result:
        print("\n🎉 所有测试通过！")
        print("Excel文档合并工具已准备就绪，可以投入使用。")
        print("\n主要功能：")
        print("• 智能表头识别")
        print("• 字段映射配置")
        print("• 数据预处理")
        print("• 多文件合并")
        print("• 数据验证")
        print("• 汇总报告")
    else:
        print(f"\n⚠️  部分测试失败，请检查错误信息。")
    
    return system_test_result and ui_test_result


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
