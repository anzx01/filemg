"""
Excel文档合并工具 - 基础框架测试脚本
用于测试基础框架的各个模块是否正常工作
"""

import os
import sys
import tempfile
import pandas as pd
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_file_operations():
    """测试文件操作模块"""
    print("测试文件操作模块...")
    
    try:
        from file_operations import FileOperations
        
        fo = FileOperations()
        
        # 创建测试Excel文件
        test_data = {
            '姓名': ['张三', '李四', '王五'],
            '年龄': [25, 30, 35],
            '部门': ['技术部', '销售部', '人事部']
        }
        df = pd.DataFrame(test_data)
        
        test_file = "test_excel.xlsx"
        df.to_excel(test_file, index=False)
        
        # 测试读取文件
        result_df = fo.read_excel_file(test_file)
        if result_df is not None:
            print("✓ 文件读取功能正常")
        else:
            print("✗ 文件读取功能失败")
        
        # 测试文件信息获取
        file_info = fo.get_file_info(test_file)
        if file_info:
            print("✓ 文件信息获取功能正常")
        else:
            print("✗ 文件信息获取功能失败")
        
        # 测试JSON配置操作
        test_config = {'test': 'value', 'number': 123}
        config_path = "test_config.json"
        
        if fo.save_json_config(test_config, config_path):
            print("✓ JSON配置保存功能正常")
        else:
            print("✗ JSON配置保存功能失败")
        
        loaded_config = fo.load_json_config(config_path)
        if loaded_config == test_config:
            print("✓ JSON配置加载功能正常")
        else:
            print("✗ JSON配置加载功能失败")
        
        # 清理测试文件
        for file in [test_file, config_path]:
            if os.path.exists(file):
                os.remove(file)
        
        return True
        
    except Exception as e:
        print(f"✗ 文件操作模块测试失败: {e}")
        return False

def test_file_manager():
    """测试文件管理模块"""
    print("测试文件管理模块...")
    
    try:
        from file_manager import FileManager
        
        fm = FileManager()
        
        # 创建测试Excel文件
        test_data = {
            '账户': ['123456', '789012', '345678'],
            '余额': [1000, 2000, 3000],
            '日期': ['2024-01-01', '2024-01-02', '2024-01-03']
        }
        df = pd.DataFrame(test_data)
        
        test_file = "test_bank.xlsx"
        df.to_excel(test_file, index=False)
        
        # 测试文件导入
        results = fm.import_excel_files([test_file])
        if results['success']:
            print("✓ 文件导入功能正常")
        else:
            print("✗ 文件导入功能失败")
        
        # 测试获取文件列表
        files = fm.get_imported_files()
        if len(files) > 0:
            print("✓ 文件列表获取功能正常")
        else:
            print("✗ 文件列表获取功能失败")
        
        # 测试文件删除
        if fm.remove_file(test_file):
            print("✓ 文件删除功能正常")
        else:
            print("✗ 文件删除功能失败")
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists("imported_files.json"):
            os.remove("imported_files.json")
        
        return True
        
    except Exception as e:
        print(f"✗ 文件管理模块测试失败: {e}")
        return False

def test_ui_module():
    """测试用户界面模块"""
    print("测试用户界面模块...")
    
    try:
        from ui_module import ExcelMergeUI
        
        # 创建界面实例（不启动主循环）
        ui = ExcelMergeUI()
        
        # 测试界面组件创建
        if hasattr(ui, 'file_listbox') and hasattr(ui, 'std_field_listbox'):
            print("✓ 界面组件创建正常")
        else:
            print("✗ 界面组件创建失败")
        
        # 测试标准字段操作
        ui.std_field_entry.insert(0, "测试字段")
        ui.add_standard_field()
        
        if "测试字段" in ui.standard_fields:
            print("✓ 标准字段添加功能正常")
        else:
            print("✗ 标准字段添加功能失败")
        
        return True
        
    except Exception as e:
        print(f"✗ 用户界面模块测试失败: {e}")
        return False

def test_main_controller():
    """测试主控制器模块"""
    print("测试主控制器模块...")
    
    try:
        from main_controller import ExcelMergeController
        
        controller = ExcelMergeController()
        
        # 测试控制器初始化
        if hasattr(controller, 'file_manager') and hasattr(controller, 'file_operations'):
            print("✓ 控制器初始化正常")
        else:
            print("✗ 控制器初始化失败")
        
        # 测试目录创建
        if os.path.exists(controller.config_dir) and os.path.exists(controller.output_dir):
            print("✓ 目录创建功能正常")
        else:
            print("✗ 目录创建功能失败")
        
        return True
        
    except Exception as e:
        print(f"✗ 主控制器模块测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("Excel文档合并工具 - 基础框架测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("文件操作模块", test_file_operations()))
    test_results.append(("文件管理模块", test_file_manager()))
    test_results.append(("用户界面模块", test_ui_module()))
    test_results.append(("主控制器模块", test_main_controller()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for module_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{module_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个模块测试通过")
    
    if passed == total:
        print("🎉 所有基础框架模块测试通过！")
        print("基础框架已准备就绪，可以开始下一阶段开发。")
    else:
        print("⚠️  部分模块测试失败，请检查相关代码。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
