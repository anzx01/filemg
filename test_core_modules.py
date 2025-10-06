"""
Excel文档合并工具 - 核心模块综合测试
测试字段映射、表头识别等核心功能模块
"""

import os
import sys
import pandas as pd
from typing import List, Dict, Any
import traceback


def test_field_mapping_integration():
    """测试字段映射模块集成"""
    print("=" * 60)
    print("测试字段映射模块集成")
    print("=" * 60)
    
    try:
        from field_mapping import FieldMappingManager, StandardField, FieldMapping
        
        # 创建测试目录
        test_dir = "test_output"
        os.makedirs(test_dir, exist_ok=True)
        
        # 初始化字段映射管理器
        manager = FieldMappingManager(config_dir=test_dir)
        
        # 测试标准字段管理
        print("测试标准字段管理...")
        standard_fields = manager.get_standard_fields()
        print(f"✓ 预定义标准字段数量: {len(standard_fields)}")
        
        # 测试字段映射
        print("测试字段映射功能...")
        test_mapping = FieldMapping(
            file_id="test_file",
            file_name="test.xlsx",
            standard_field="account_number",
            file_field="账户号码",
            mapping_type="direct"
        )
        
        success = manager.add_field_mapping(test_mapping)
        if success:
            print("✓ 字段映射添加成功")
        else:
            print("✗ 字段映射添加失败")
        
        # 测试智能建议
        print("测试智能映射建议...")
        columns = ["账户号码", "户名", "交易日期", "金额", "余额"]
        suggestion = manager.suggest_mapping(columns, "account_number")
        if suggestion:
            print(f"✓ 智能建议功能正常: {suggestion}")
        else:
            print("✗ 智能建议功能失败")
        
        return True
        
    except Exception as e:
        print(f"字段映射模块测试失败: {e}")
        traceback.print_exc()
        return False


def test_header_detection_integration():
    """测试表头识别模块集成"""
    print("\n" + "=" * 60)
    print("测试表头识别模块集成")
    print("=" * 60)
    
    try:
        from header_detection import HeaderDetector
        
        # 创建测试目录
        test_dir = "test_output"
        os.makedirs(test_dir, exist_ok=True)
        
        # 创建测试Excel文件
        test_data = {
            "账户号码": ["1234567890", "0987654321"],
            "户名": ["张三", "李四"],
            "交易日期": ["2025-01-01", "2025-01-02"],
            "交易金额": [1000.00, -500.00],
            "账户余额": [5000.00, 4500.00]
        }
        
        test_file = os.path.join(test_dir, "test_header.xlsx")
        df = pd.DataFrame(test_data)
        df.to_excel(test_file, index=False)
        
        # 创建表头识别器
        detector = HeaderDetector()
        
        # 测试表头检测
        print("测试表头检测...")
        headers = detector.detect_headers(test_file)
        if headers:
            print("✓ 表头检测成功")
            header = headers[0]
            print(f"  - 检测到列: {header.columns}")
            print(f"  - 余额列: {header.balance_columns}")
            print(f"  - 置信度: {header.confidence:.2f}")
        else:
            print("✗ 表头检测失败")
        
        # 测试余额列识别
        print("测试余额列识别...")
        balance_columns = detector.get_balance_columns(test_file)
        if balance_columns:
            print(f"✓ 余额列识别成功: {balance_columns}")
        else:
            print("✗ 余额列识别失败")
        
        return True
        
    except Exception as e:
        print(f"表头识别模块测试失败: {e}")
        traceback.print_exc()
        return False


def test_ui_integration():
    """测试用户界面集成"""
    print("\n" + "=" * 60)
    print("测试用户界面集成")
    print("=" * 60)
    
    try:
        from ui_module import ExcelMergeUI
        import tkinter as tk
        
        # 创建隐藏的根窗口
        root = tk.Tk()
        root.withdraw()
        
        # 创建界面实例
        ui = ExcelMergeUI()
        
        # 测试字段映射管理器集成
        if hasattr(ui, 'field_mapping_manager'):
            print("✓ 界面成功集成字段映射管理器")
        else:
            print("✗ 界面未集成字段映射管理器")
        
        # 测试标准字段刷新
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


def test_controller_integration():
    """测试主控制器集成"""
    print("\n" + "=" * 60)
    print("测试主控制器集成")
    print("=" * 60)
    
    try:
        from main_controller import ExcelMergeController
        
        # 创建控制器实例
        controller = ExcelMergeController()
        
        # 测试模块集成
        modules = [
            ("文件管理器", "file_manager"),
            ("文件操作", "file_operations"),
            ("字段映射管理器", "field_mapping_manager"),
            ("表头识别器", "header_detector")
        ]
        
        for module_name, attr_name in modules:
            if hasattr(controller, attr_name):
                print(f"✓ {module_name}集成成功")
            else:
                print(f"✗ {module_name}集成失败")
        
        # 测试目录创建
        if os.path.exists(controller.config_dir) and os.path.exists(controller.output_dir):
            print("✓ 目录创建功能正常")
        else:
            print("✗ 目录创建功能失败")
        
        return True
        
    except Exception as e:
        print(f"主控制器集成测试失败: {e}")
        traceback.print_exc()
        return False


def test_end_to_end_workflow():
    """测试端到端工作流程"""
    print("\n" + "=" * 60)
    print("测试端到端工作流程")
    print("=" * 60)
    
    try:
        from field_mapping import FieldMappingManager, FieldMapping
        from header_detection import HeaderDetector
        import pandas as pd
        
        # 创建测试目录
        test_dir = "test_output"
        os.makedirs(test_dir, exist_ok=True)
        
        # 创建测试Excel文件
        test_data = {
            "账户号码": ["1234567890", "0987654321"],
            "户名": ["张三", "李四"],
            "交易日期": ["2025-01-01", "2025-01-02"],
            "交易金额": [1000.00, -500.00],
            "账户余额": [5000.00, 4500.00]
        }
        
        test_file = os.path.join(test_dir, "test_workflow.xlsx")
        df = pd.DataFrame(test_data)
        df.to_excel(test_file, index=False)
        
        # 步骤1: 表头识别
        print("步骤1: 表头识别...")
        detector = HeaderDetector()
        headers = detector.detect_headers(test_file)
        
        if headers:
            print("✓ 表头识别成功")
            header = headers[0]
            print(f"  - 检测到列: {header.columns}")
        else:
            print("✗ 表头识别失败")
            return False
        
        # 步骤2: 字段映射
        print("步骤2: 字段映射...")
        manager = FieldMappingManager(config_dir=test_dir)
        
        # 创建字段映射
        mappings = [
            FieldMapping("test_workflow.xlsx", "test_workflow.xlsx", "account_number", "账户号码", "direct"),
            FieldMapping("test_workflow.xlsx", "test_workflow.xlsx", "account_name", "户名", "direct"),
            FieldMapping("test_workflow.xlsx", "test_workflow.xlsx", "transaction_date", "交易日期", "direct"),
            FieldMapping("test_workflow.xlsx", "test_workflow.xlsx", "transaction_amount", "交易金额", "direct"),
            FieldMapping("test_workflow.xlsx", "test_workflow.xlsx", "balance", "账户余额", "direct")
        ]
        
        success_count = 0
        for mapping in mappings:
            if manager.add_field_mapping(mapping):
                success_count += 1
        
        if success_count == len(mappings):
            print(f"✓ 字段映射创建成功: {success_count}/{len(mappings)}")
        else:
            print(f"✗ 字段映射创建失败: {success_count}/{len(mappings)}")
            return False
        
        # 步骤3: 验证映射
        print("步骤3: 验证映射...")
        file_mappings = manager.get_file_mappings("test_workflow.xlsx")
        if len(file_mappings) == len(mappings):
            print(f"✓ 映射验证成功: {len(file_mappings)} 个映射")
        else:
            print(f"✗ 映射验证失败: 期望 {len(mappings)}, 实际 {len(file_mappings)}")
            return False
        
        # 步骤4: 余额列识别
        print("步骤4: 余额列识别...")
        balance_columns = detector.get_balance_columns(test_file)
        if balance_columns:
            print(f"✓ 余额列识别成功: {balance_columns}")
        else:
            print("✗ 余额列识别失败")
            return False
        
        print("✓ 端到端工作流程测试成功")
        return True
        
    except Exception as e:
        print(f"端到端工作流程测试失败: {e}")
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("Excel文档合并工具 - 核心模块综合测试")
    print("=" * 80)
    
    # 运行各项测试
    tests = [
        ("字段映射模块集成", test_field_mapping_integration),
        ("表头识别模块集成", test_header_detection_integration),
        ("用户界面集成", test_ui_integration),
        ("主控制器集成", test_controller_integration),
        ("端到端工作流程", test_end_to_end_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果汇总
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有核心模块测试通过！")
        print("核心功能模块已准备就绪，可以开始数据处理模块开发。")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查错误信息。")
    
    # 清理测试文件
    try:
        import shutil
        if os.path.exists("test_output"):
            shutil.rmtree("test_output")
        print("\n✓ 测试文件清理完成")
    except Exception as e:
        print(f"\n⚠️  测试文件清理失败: {e}")


if __name__ == "__main__":
    main()


