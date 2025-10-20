#!/usr/bin/env python3
"""
Excel合并工具 - 现代化版快速启动脚本
"""

import sys
import os

def check_requirements():
    """检查运行要求"""
    print("🔍 检查运行环境...")

    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        return False

    print(f"✅ Python版本: {sys.version.split()[0]}")

    # 检查必要模块
    required_modules = ['tkinter', 'pandas', 'openpyxl']
    missing_modules = []

    for module in required_modules:
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'pandas':
                import pandas
            elif module == 'openpyxl':
                import openpyxl
            print(f"✅ {module}: 已安装")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module}: 未安装")

    if missing_modules:
        print(f"\n⚠️  缺少以下模块: {', '.join(missing_modules)}")
        print("请使用以下命令安装:")
        print(f"pip install {' '.join(missing_modules)}")
        return False

    return True

def setup_directories():
    """设置必要的目录"""
    directories = ['config', 'output', 'test_data']

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 创建目录: {directory}")
        else:
            print(f"📁 目录已存在: {directory}")

def launch_modern_ui():
    """启动现代化UI"""
    try:
        print("\n🚀 启动现代化Excel合并工具...")
        print("✨ 新版本特性:")
        print("   • 现代化视觉设计")
        print("   • 优雅的配色方案")
        print("   • 直观的图标和表情符号")
        print("   • 改进的用户体验")
        print("   • 响应式布局设计")
        print("   • 现代化状态栏")
        print("   • 新增设置功能")
        print("-" * 50)

        # 导入并启动现代化UI
        from ui_module_modern import ModernExcelMergeUI

        app = ModernExcelMergeUI()
        app.run()

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保ui_module_modern.py文件存在且可访问")
        return False
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

    return True

def main():
    """主函数"""
    print("🎯 Excel文档合并工具 - 现代化版 v2.0")
    print("=" * 50)

    # 检查运行要求
    if not check_requirements():
        input("\n按回车键退出...")
        return False

    # 设置目录
    setup_directories()

    print("\n📋 使用说明:")
    print("1. 点击'选择Excel文件'导入要合并的文件")
    print("2. 选择文件后配置字段映射")
    print("3. 如需要，配置特殊处理规则")
    print("4. 点击'开始合并'完成操作")
    print("5. 在output文件夹中查看合并结果")

    try:
        input("\n按回车键启动现代化界面...")
    except KeyboardInterrupt:
        print("\n👋 已取消启动")
        return False

    # 启动现代化UI
    success = launch_modern_ui()

    if not success:
        print("\n💡 提示: 如果遇到问题，可以尝试:")
        print("   1. 检查Python环境和依赖模块")
        print("   2. 确保所有文件都在正确位置")
        print("   3. 运行 test_modern_ui.py 进行组件测试")
        input("\n按回车键退出...")
        return False

    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序异常退出: {e}")
        input("\n按回车键退出...")
        sys.exit(1)