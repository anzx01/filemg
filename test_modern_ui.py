"""
现代化UI测试脚本
用于测试优化后的界面功能和用户体验
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_modern_ui():
    """测试现代化UI"""
    try:
        # 导入现代化UI模块
        from ui_module_modern import ModernExcelMergeUI

        print("🚀 启动现代化Excel合并工具界面...")
        print("✨ 界面特性:")
        print("   • 现代化视觉设计，优雅配色方案")
        print("   • 直观的图标和表情符号增强")
        print("   • 改进的布局和响应式设计")
        print("   • 现代化状态栏和进度指示")
        print("   • 优化的用户体验和操作反馈")
        print("   • 新增设置和预览功能")
        print("\n🎯 测试要点:")
        print("   1. 界面布局是否合理美观")
        print("   2. 颜色搭配是否和谐现代")
        print("   3. 操作响应是否流畅")
        print("   4. 功能是否完整可用")
        print("   5. 错误处理是否完善")
        print("\n⚠️  注意: 这是一个UI测试版本，部分高级功能可能需要完善")
        print("=" * 60)

        # 创建并运行现代化界面
        app = ModernExcelMergeUI()
        app.run()

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖模块都已正确安装")
        return False

    except Exception as e:
        print(f"❌ 运行错误: {e}")
        print("请检查代码和依赖项")
        return False

    return True

def test_ui_components():
    """测试UI组件"""
    print("🔍 测试UI组件...")

    try:
        import tkinter as tk
        from tkinter import ttk

        # 创建测试窗口
        root = tk.Tk()
        root.title("UI组件测试")
        root.geometry("400x300")

        # 测试现代化样式
        from ui_module_modern import ModernStyle

        style = ttk.Style()
        style.theme_use('clam')

        # 配置测试样式
        colors = ModernStyle.COLORS
        fonts = ModernStyle.FONTS

        style.configure('TFrame', background=colors['background'])
        style.configure('TLabel', background=colors['background'],
                       foreground=colors['text_primary'], font=fonts['default'])
        style.configure('Primary.TButton',
                       background=colors['primary'],
                       foreground='white',
                       font=fonts['button'])

        # 创建测试组件
        main_frame = ttk.Frame(root, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="现代化UI组件测试",
                 font=fonts['heading']).pack(pady=(0, 20))

        ttk.Button(main_frame, text="主要按钮", style='Primary.TButton').pack(pady=5)
        ttk.Button(main_frame, text="普通按钮").pack(pady=5)

        # 测试Treeview
        columns = ('列1', '列2', '列3')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=5)
        tree.heading('列1', text='测试列1')
        tree.heading('列2', text='测试列2')
        tree.heading('列3', text='测试列3')

        tree.insert('', 'end', values=('数据1', '数据2', '数据3'))
        tree.insert('', 'end', values=('数据4', '数据5', '数据6'))

        tree.pack(pady=20, fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="如果界面显示正常，说明组件工作良好",
                 foreground=colors['text_secondary']).pack(pady=(10, 0))

        print("✅ UI组件测试窗口已打开")
        print("   检查组件样式和布局是否正常")

        root.mainloop()

    except Exception as e:
        print(f"❌ 组件测试失败: {e}")
        return False

    return True

def show_ui_comparison():
    """显示界面对比说明"""
    print("\n" + "=" * 60)
    print("📊 界面优化对比")
    print("=" * 60)

    print("\n🔸 原版界面特点:")
    print("   • 基础功能完整")
    print("   • 使用标准ttk组件")
    print("   • 布局功能性强")
    print("   • 缺乏视觉吸引力")

    print("\n🔸 现代化界面改进:")
    print("   • 🎨 优雅的配色方案和现代化设计")
    print("   • 📱 响应式布局，自适应窗口大小")
    print("   • 🎯 直观的图标和表情符号增强")
    print("   • 💫 现代化状态栏和进度指示")
    print("   • 🎪 改进的用户交互体验")
    print("   • ⚡ 优化的操作反馈机制")
    print("   • 🛠️ 新增设置和预览功能")
    print("   • 🎭 更好的错误处理和用户提示")

    print("\n🔸 技术改进:")
    print("   • 模块化的样式配置类")
    print("   • 统一的颜色和字体管理")
    print("   • 改进的组件封装")
    print("   • 更好的代码组织结构")
    print("   • 增强的异常处理")

def main():
    """主测试函数"""
    print("🎯 Excel合并工具 - 现代化UI测试")
    print("=" * 60)

    # 显示对比说明
    show_ui_comparison()

    print("\n" + "=" * 60)
    print("选择测试模式:")
    print("1. 启动完整现代化界面测试")
    print("2. 仅测试UI组件样式")
    print("3. 显示优化说明并退出")
    print("=" * 60)

    try:
        choice = input("请输入选择 (1-3): ").strip()

        if choice == '1':
            print("\n🚀 启动完整现代化界面...")
            test_modern_ui()
        elif choice == '2':
            print("\n🔍 测试UI组件样式...")
            test_ui_components()
        elif choice == '3':
            print("\n✅ 查看优化说明完成")
        else:
            print("\n❌ 无效选择，启动默认界面测试...")
            test_modern_ui()

    except KeyboardInterrupt:
        print("\n\n👋 测试已取消")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")

    print("\n🎉 测试结束！")

if __name__ == "__main__":
    main()