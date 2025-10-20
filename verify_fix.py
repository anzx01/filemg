#!/usr/bin/env python3
"""
快速验证修复脚本
用于验证现代化界面合并功能是否正常工作
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_fix():
    """验证修复是否成功"""
    print("🔍 验证现代化界面修复...")

    try:
        # 尝试导入修复后的模块
        from ui_module_modern import ModernExcelMergeUI
        print("✅ 现代化UI模块导入成功")

        # 创建一个最小的测试窗口
        test_window = tk.Tk()
        test_window.title("修复验证")
        test_window.geometry("400x200")

        # 创建UI实例（但不显示主窗口）
        app = ModernExcelMergeUI()

        # 检查关键组件
        components = [
            ('progress_bar', '进度条'),
            ('progress_var', '进度变量'),
            ('progress_text_var', '进度文本'),
            ('merge_btn', '合并按钮'),
            ('status_bar', '状态栏')
        ]

        print("\n🧪 检查关键组件:")
        all_good = True

        for attr, name in components:
            if hasattr(app, attr):
                print(f"   ✅ {name}: 存在")
            else:
                print(f"   ❌ {name}: 缺失")
                all_good = False

        if not all_good:
            print("\n❌ 关键组件缺失，修复可能不完整")
            return False

        # 测试合并方法的调用
        print("\n🎯 测试合并方法调用...")
        try:
            # 这应该会显示"请先导入文件"的警告
            app.start_merge()
            print("   ✅ 合并方法调用成功")
        except Exception as e:
            print(f"   ❌ 合并方法调用失败: {e}")
            print("   🔧 这可能是布局管理器冲突的迹象")
            return False

        # 关闭测试窗口
        test_window.destroy()
        print("\n✅ 验证完成！修复似乎成功")
        return True

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("   请确保ui_module_modern.py文件存在")
        return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        print("   可能仍有其他问题需要解决")
        return False

def show_fix_details():
    """显示修复详情"""
    print("\n" + "="*60)
    print("🔧 修复详情")
    print("="*60)

    print("\n🐛 问题描述:")
    print("   • 点击'开始合并'按钮时出现TclError")
    print("   • 错误信息: 'cannot use geometry manager pack inside... which already has slaves managed by grid'")
    print("   • 原因: 混用了pack和grid布局管理器")

    print("\n🛠️ 修复方案:")
    print("   1. 移除start_merge()方法中重复的进度条布局设置")
    print("   2. 确保进度条在创建时已经正确布局")
    print("   3. 保持布局管理器的一致性")

    print("\n📝 修改的代码:")
    print("   文件: ui_module_modern.py")
    print("   方法: start_merge()")
    print("   移除: self.progress_bar.pack() 调用")
    print("   保留: 原有的grid布局设置")

def main():
    """主函数"""
    print("🚀 Excel合并工具 - 修复验证")
    print("="*50)

    # 显示修复详情
    show_fix_details()

    print("\n🧪 开始验证...")

    success = verify_fix()

    print("\n" + "="*50)
    if success:
        print("🎉 验证成功！")
        print("💡 现在可以正常使用'开始合并'功能")
        print("\n🚀 启动命令:")
        print("   python run_modern.py")
        print("   或")
        print("   python ui_module_modern.py")
    else:
        print("❌ 验证失败")
        print("🔧 可能需要进一步修复")
        print("\n📞 建议:")
        print("   1. 检查所有布局管理器是否一致")
        print("   2. 确认所有组件正确初始化")
        print("   3. 运行详细测试: python test_merge_fix.py")

    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 验证已取消")
    except Exception as e:
        print(f"\n❌ 验证过程中出现错误: {e}")