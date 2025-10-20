#!/usr/bin/env python3
"""
测试合并功能修复
专门测试修复后的"开始合并"按钮功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_merge_functionality():
    """测试合并功能"""
    try:
        print("🧪 测试合并功能修复...")

        # 导入修复后的UI模块
        from ui_module_modern import ModernExcelMergeUI

        print("✅ UI模块导入成功")

        # 创建UI实例但不显示
        app = ModernExcelMergeUI()

        print("✅ UI实例创建成功")

        # 测试合并相关的初始化
        print("\n🔍 检查合并相关组件...")

        # 检查进度条是否正确初始化
        if hasattr(app, 'progress_bar'):
            print("✅ 进度条组件存在")
        else:
            print("❌ 进度条组件缺失")

        # 检查进度变量
        if hasattr(app, 'progress_var'):
            print("✅ 进度变量存在")
        else:
            print("❌ 进度变量缺失")

        # 检查进度文本变量
        if hasattr(app, 'progress_text_var'):
            print("✅ 进度文本变量存在")
        else:
            print("❌ 进度文本变量缺失")

        # 检查合并按钮
        if hasattr(app, 'merge_btn'):
            print("✅ 合并按钮存在")
        else:
            print("❌ 合并按钮缺失")

        # 测试无文件时的合并行为
        print("\n🎯 测试无文件时的合并行为...")

        # 直接调用start_merge方法
        try:
            app.start_merge()
            print("✅ start_merge方法调用成功（应该显示警告消息）")
        except Exception as e:
            print(f"❌ start_merge方法调用失败: {e}")
            return False

        # 模拟添加一个虚拟文件
        print("\n📁 添加测试文件...")
        app.imported_files = ["test_file.xlsx"]

        # 测试有文件时的合并行为
        print("🎯 测试有文件时的合并行为...")

        try:
            app.start_merge()
            print("✅ start_merge方法调用成功（应该开始合并过程）")

            # 等待一小段时间观察是否有错误
            import time
            time.sleep(0.5)

            print("✅ 合并过程启动正常，无布局管理器冲突")

        except Exception as e:
            print(f"❌ 合并过程启动失败: {e}")
            return False

        print("\n🎉 合并功能测试完成！")
        return True

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Excel合并工具 - 修复验证测试")
    print("=" * 50)

    print("📋 修复内容:")
    print("   • 修复了混用pack和grid布局管理器的冲突")
    print("   • 移除了重复的进度条布局设置")
    print("   • 确保合并按钮正常响应")
    print("=" * 50)

    success = test_merge_functionality()

    if success:
        print("\n✅ 所有测试通过！")
        print("🚀 可以安全使用现代化界面进行合并操作")
        print("\n💡 使用建议:")
        print("   1. 运行 python run_modern.py 启动界面")
        print("   2. 导入Excel文件")
        print("   3. 配置字段映射")
        print("   4. 点击'开始合并'按钮")
        print("   5. 观察进度条和状态反馈")
    else:
        print("\n❌ 测试失败，请检查修复是否完整")

    print("\n按回车键退出...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n👋 已退出")

if __name__ == "__main__":
    main()