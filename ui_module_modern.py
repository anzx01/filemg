"""
Excel文档合并工具 - 现代化用户界面模块
优化版界面，提供更好的用户体验和视觉效果
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.ttk import Combobox
from typing import List, Dict, Any
import os
import pandas as pd


class ModernStyle:
    """现代化样式配置类"""

    # 颜色方案
    COLORS = {
        'primary': '#2E86AB',       # 主色调 - 蓝色
        'primary_light': '#A23B72', # 主色调浅色
        'secondary': '#F18F01',     # 次要色 - 橙色
        'success': '#C73E1D',       # 成功色
        'background': '#F8F9FA',    # 背景色
        'surface': '#FFFFFF',       # 表面色
        'text_primary': '#212529',  # 主文本色
        'text_secondary': '#6C757D', # 次要文本色
        'border': '#DEE2E6',        # 边框色
        'hover': '#E9ECEF',         # 悬停色
        'accent': '#007BFF'         # 强调色
    }

    # 字体配置
    FONTS = {
        'default': ('Microsoft YaHei UI', 9),
        'heading': ('Microsoft YaHei UI', 12, 'bold'),
        'button': ('Microsoft YaHei UI', 9),
        'mono': ('Consolas', 9)
    }


class TreeviewWithDropdown(ttk.Treeview):
    """支持内联下拉列表的Treeview - 优化版"""

    def __init__(self, parent, columns, dropdown_column_index=1, **kwargs):
        super().__init__(parent, columns=columns, **kwargs)
        self.dropdown_column_index = dropdown_column_index
        self.dropdown_values = []
        self.current_combobox = None
        self.on_value_change_callback = None

        # 绑定事件
        self.bind('<Button-1>', self.on_click)
        self.bind('<FocusOut>', self.on_focus_out)

        # 现代化样式
        self.configure(style='Modern.Treeview')

    def set_dropdown_values(self, values):
        """设置下拉列表的值"""
        self.dropdown_values = values

    def set_value_change_callback(self, callback):
        """设置值改变时的回调函数"""
        self.on_value_change_callback = callback

    def on_click(self, event):
        """处理点击事件"""
        item = self.identify_row(event.y)
        column = self.identify_column(event.x)

        if item and column:
            # 获取列索引
            column_index = int(column.replace('#', '')) - 1

            # 如果是下拉列，显示内联下拉框
            if column_index == self.dropdown_column_index:
                self.show_inline_dropdown(item, event.x, event.y)

    def show_inline_dropdown(self, item, x, y):
        """显示内联下拉框 - 优化版"""
        # 隐藏当前下拉框
        if self.current_combobox:
            self.current_combobox.destroy()
            self.current_combobox = None

        # 检查下拉框值是否设置
        if not self.dropdown_values:
            return

        # 获取当前值
        current_values = self.item(item, 'values')
        current_value = current_values[self.dropdown_column_index] if len(current_values) > self.dropdown_column_index else ''

        # 获取列的位置和大小
        column_id = f"#{self.dropdown_column_index + 1}"
        bbox = self.bbox(item, column_id)

        if not bbox:
            width, height = 200, 25
        else:
            x, y, width, height = bbox

        try:
            # 创建现代化样式的Combobox
            combobox = Combobox(self, values=self.dropdown_values, state="readonly",
                              style='Modern.TCombobox')
            combobox.set(current_value)

            # 设置位置
            combobox.place(x=x, y=y, width=width, height=height)

            # 绑定事件
            def on_select(event):
                new_value = combobox.get()
                self.update_item_value(item, new_value)
                combobox.destroy()
                self.current_combobox = None

            def on_focus_out(event):
                combobox.destroy()
                self.current_combobox = None

            def on_escape(event):
                combobox.destroy()
                self.current_combobox = None

            combobox.bind('<<ComboboxSelected>>', on_select)
            combobox.bind('<Escape>', on_escape)

            # 保存引用
            self.current_combobox = combobox

            # 强制更新显示
            self.update()
            combobox.update()

            # 获取焦点并打开下拉列表
            combobox.focus_set()

            # 延迟打开下拉列表
            def open_dropdown():
                if self.current_combobox and self.current_combobox.winfo_exists():
                    try:
                        self.current_combobox.focus_set()
                        self.current_combobox.event_generate('<Button-1>')
                    except Exception:
                        pass

            self.after(50, open_dropdown)

        except Exception:
            if 'combobox' in locals():
                combobox.destroy()
            self.current_combobox = None

    def on_focus_out(self, event):
        """处理失去焦点事件"""
        def delayed_destroy():
            if self.current_combobox and self.current_combobox.winfo_exists():
                try:
                    self.current_combobox.destroy()
                except:
                    pass
                self.current_combobox = None

        if self.current_combobox:
            self.after(100, delayed_destroy)

    def update_item_value(self, item, new_value):
        """更新项目值"""
        current_values = list(self.item(item, 'values'))
        if len(current_values) > self.dropdown_column_index:
            current_values[self.dropdown_column_index] = new_value
            # 更新是否映射状态
            if new_value == "未映射" or not new_value or new_value.strip() == "":
                current_values[2] = "否"
            else:
                current_values[2] = "是"
            self.item(item, values=current_values)

            # 调用回调函数
            if self.on_value_change_callback:
                self.on_value_change_callback(item, new_value)


class StatusBar(ttk.Frame):
    """现代化状态栏"""

    def __init__(self, parent):
        super().__init__(parent, relief=tk.SUNKEN, style='Modern.TFrame')

        # 状态文本
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(self, textvariable=self.status_var,
                                     style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=5)

        # 进度条（隐藏状态）
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var,
                                           length=200, mode='determinate',
                                           style='Modern.Horizontal.TProgressbar')

        # 分隔符
        separator = ttk.Separator(self, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 文件计数
        self.file_count_var = tk.StringVar(value="文件: 0")
        self.file_count_label = ttk.Label(self, textvariable=self.file_count_var,
                                        style='Status.TLabel')
        self.file_count_label.pack(side=tk.RIGHT, padx=5)

    def set_status(self, text):
        """设置状态文本"""
        self.status_var.set(text)

    def set_file_count(self, count):
        """设置文件计数"""
        self.file_count_var.set(f"文件: {count}")

    def show_progress(self):
        """显示进度条"""
        self.progress_bar.pack(side=tk.RIGHT, padx=5, before=self.file_count_label)

    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.pack_forget()

    def set_progress(self, value):
        """设置进度值"""
        self.progress_var.set(value)


class ModernExcelMergeUI:
    """Excel合并工具现代化主界面类"""

    def __init__(self):
        """初始化现代化界面"""
        self.root = tk.Tk()
        self.root.title("Excel文档合并工具 v2.0 - 现代化版")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 800)

        # 设置现代化样式
        self.setup_modern_style()

        # 设置窗口图标（如果有的话）
        try:
            # 可以在这里设置应用图标
            # self.root.iconbitmap("assets/icon.ico")
            pass
        except:
            pass

        # 设置窗口居中显示
        self.center_window()

        # 界面变量
        self.imported_files = []
        self.special_rules = {}

        # 初始化特殊规则管理器
        from special_rules import SpecialRulesManager
        self.special_rules_manager = SpecialRulesManager()

        # 创建界面
        self.create_modern_main_window()

        # 创建状态栏
        self.create_status_bar()

        # 初始化数据
        self.initialize_data()

    def setup_modern_style(self):
        """设置现代化样式"""
        style = ttk.Style()
        colors = ModernStyle.COLORS
        fonts = ModernStyle.FONTS

        # 设置主题
        style.theme_use('clam')

        # 配置通用样式
        style.configure('TFrame', background=colors['background'])
        style.configure('TLabel', background=colors['background'],
                       foreground=colors['text_primary'], font=fonts['default'])
        style.configure('TButton', font=fonts['button'], padding=5)
        style.configure('TLabelframe', background=colors['background'],
                       foreground=colors['text_primary'], font=fonts['heading'])
        style.configure('TLabelframe.Label', background=colors['background'],
                       foreground=colors['primary'], font=fonts['heading'])

        # 配置现代化按钮样式
        style.configure('Primary.TButton',
                       background=colors['primary'],
                       foreground='white',
                       font=fonts['button'])
        style.map('Primary.TButton',
                 background=[('active', colors['primary_light'])])

        style.configure('Success.TButton',
                       background=colors['success'],
                       foreground='white',
                       font=fonts['button'])

        style.configure('Secondary.TButton',
                       background=colors['secondary'],
                       foreground='white',
                       font=fonts['button'])

        # 配置现代化Treeview样式
        style.configure('Modern.Treeview',
                       background=colors['surface'],
                       foreground=colors['text_primary'],
                       fieldbackground=colors['surface'],
                       bordercolor=colors['border'],
                       relief=tk.FLAT,
                       font=fonts['default'])
        style.configure('Modern.Treeview.Heading',
                       background=colors['primary'],
                       foreground='white',
                       font=fonts['heading'])
        style.map('Modern.Treeview',
                 background=[('selected', colors['accent'])],
                 foreground=[('selected', 'white')])

        # 配置现代化Combobox样式
        style.configure('Modern.TCombobox',
                       fieldbackground=colors['surface'],
                       background=colors['surface'],
                       bordercolor=colors['border'],
                       font=fonts['default'])

        # 配置现代化进度条样式
        style.configure('Modern.Horizontal.TProgressbar',
                       background=colors['primary'],
                       troughcolor=colors['border'])

        # 配置状态栏样式
        style.configure('Modern.TFrame', background=colors['border'])
        style.configure('Status.TLabel', background=colors['border'],
                       foreground=colors['text_secondary'], font=fonts['default'])

    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_modern_main_window(self):
        """创建现代化主窗口"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=3)  # 上半部分权重更大
        main_frame.rowconfigure(1, weight=1)  # 下半部分权重较小

        # 创建上半部分 - 文件管理和字段映射
        self.create_upper_section(main_frame)

        # 创建下半部分 - 特殊规则和操作区域
        self.create_lower_section(main_frame)

    def create_upper_section(self, parent):
        """创建上半部分区域"""
        upper_frame = ttk.Frame(parent, style='TFrame')
        upper_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        upper_frame.columnconfigure(0, weight=1)
        upper_frame.columnconfigure(1, weight=1)

        # 左侧 - 文件导入管理
        self.create_modern_file_section(upper_frame)

        # 右侧 - 字段映射配置
        self.create_modern_mapping_section(upper_frame)

    def create_lower_section(self, parent):
        """创建下半部分区域"""
        lower_frame = ttk.Frame(parent, style='TFrame')
        lower_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        lower_frame.columnconfigure(0, weight=1)

        # 特殊规则配置区域
        self.create_modern_rules_section(lower_frame)

        # 操作按钮区域
        self.create_modern_action_section(lower_frame)

    def create_modern_file_section(self, parent):
        """创建现代化文件导入区域"""
        # 文件导入框架
        file_frame = ttk.LabelFrame(parent, text="📁 文件导入管理",
                                  style='TLabelframe', padding="15")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(2, weight=1)

        # 文件操作按钮区域
        button_frame = ttk.Frame(file_frame, style='TFrame')
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 添加文件按钮
        add_btn = ttk.Button(button_frame, text="📂 选择Excel文件",
                            command=self.import_files, style='Primary.TButton')
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 快速操作按钮
        ttk.Button(button_frame, text="🗑️ 删除选中",
                  command=self.remove_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔄 重新导入",
                  command=self.reimport_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🧹 清空列表",
                  command=self.clear_file_list).pack(side=tk.LEFT)

        # 文件统计信息
        info_frame = ttk.Frame(file_frame, style='TFrame')
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        self.file_info_var = tk.StringVar(value="未导入文件")
        info_label = ttk.Label(info_frame, textvariable=self.file_info_var,
                              foreground=ModernStyle.COLORS['text_secondary'])
        info_label.pack(side=tk.LEFT)

        # 文件列表区域
        list_container = ttk.Frame(file_frame, style='TFrame')
        list_container.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)

        # 创建现代化Treeview
        columns = ('文件名', '路径', '记录数', '状态')
        self.file_treeview = ttk.Treeview(list_container, columns=columns,
                                         show='headings', style='Modern.Treeview')

        # 设置列标题和宽度
        self.file_treeview.heading('文件名', text='📄 文件名')
        self.file_treeview.heading('路径', text='📂 路径')
        self.file_treeview.heading('记录数', text='📊 记录数')
        self.file_treeview.heading('状态', text='✅ 状态')

        self.file_treeview.column('文件名', width=200, minwidth=150)
        self.file_treeview.column('路径', width=300, minwidth=200)
        self.file_treeview.column('记录数', width=100, minwidth=80)
        self.file_treeview.column('状态', width=100, minwidth=80)

        self.file_treeview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 滚动条
        file_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL,
                                      command=self.file_treeview.yview)
        file_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_treeview.configure(yscrollcommand=file_scrollbar.set)

        # 绑定选择事件
        self.file_treeview.bind('<<TreeviewSelect>>', self.on_file_treeview_select)

    def create_modern_mapping_section(self, parent):
        """创建现代化字段映射区域"""
        # 字段映射框架
        mapping_frame = ttk.LabelFrame(parent, text="🔗 字段映射配置",
                                     style='TLabelframe', padding="15")
        mapping_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        mapping_frame.columnconfigure(0, weight=1)
        mapping_frame.rowconfigure(2, weight=1)

        # 当前文件信息
        current_file_frame = ttk.Frame(mapping_frame, style='TFrame')
        current_file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_file_frame.columnconfigure(1, weight=1)

        ttk.Label(current_file_frame, text="当前文件:",
                 font=ModernStyle.FONTS['heading']).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.current_file_label = ttk.Label(current_file_frame, text="未选择文件",
                                          foreground=ModernStyle.COLORS['text_secondary'],
                                          font=ModernStyle.FONTS['heading'])
        self.current_file_label.grid(row=0, column=1, sticky=tk.W)

        # 标准字段管理区域
        field_mgmt_frame = ttk.LabelFrame(mapping_frame, text="📝 标准字段管理",
                                         style='TLabelframe', padding="10")
        field_mgmt_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        field_mgmt_frame.columnconfigure(1, weight=1)

        # 标准字段输入
        input_frame = ttk.Frame(field_mgmt_frame, style='TFrame')
        input_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="字段名称:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.standard_field_var = tk.StringVar()
        field_entry = ttk.Entry(input_frame, textvariable=self.standard_field_var,
                               font=ModernStyle.FONTS['default'])
        field_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        field_entry.bind('<Return>', lambda e: self.add_standard_field())

        # 字段管理按钮
        ttk.Button(input_frame, text="➕ 添加", command=self.add_standard_field,
                  style='Success.TButton').grid(row=0, column=2, padx=(0, 5))
        ttk.Button(input_frame, text="✏️ 编辑", command=self.edit_standard_field).grid(row=0, column=3, padx=(0, 5))
        ttk.Button(input_frame, text="🗑️ 删除", command=self.remove_standard_field).grid(row=0, column=4)

        # 字段映射列表
        mapping_list_frame = ttk.LabelFrame(mapping_frame, text="🎯 字段映射列表",
                                          style='TLabelframe', padding="10")
        mapping_list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        mapping_list_frame.columnconfigure(0, weight=1)
        mapping_list_frame.rowconfigure(1, weight=1)

        # 映射列表容器
        list_container = ttk.Frame(mapping_list_frame, style='TFrame')
        list_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)

        # 创建现代化映射Treeview
        mapping_columns = ('标准字段', '导入文件列名', '是否映射')
        self.mapping_treeview = TreeviewWithDropdown(list_container, columns=mapping_columns,
                                                   show='headings', style='Modern.Treeview',
                                                   dropdown_column_index=1)

        # 设置列标题和宽度
        self.mapping_treeview.heading('标准字段', text='📋 标准字段')
        self.mapping_treeview.heading('导入文件列名', text='📂 导入文件列名')
        self.mapping_treeview.heading('是否映射', text='✅ 是否映射')

        self.mapping_treeview.column('标准字段', width=150, minwidth=120)
        self.mapping_treeview.column('导入文件列名', width=180, minwidth=150)
        self.mapping_treeview.column('是否映射', width=100, minwidth=80)

        self.mapping_treeview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 设置值改变回调函数
        self.mapping_treeview.set_value_change_callback(self.on_mapping_value_change)

        # 滚动条
        mapping_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL,
                                         command=self.mapping_treeview.yview)
        mapping_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.mapping_treeview.configure(yscrollcommand=mapping_scrollbar.set)

        # 映射操作按钮
        mapping_button_frame = ttk.Frame(mapping_list_frame, style='TFrame')
        mapping_button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Button(mapping_button_frame, text="🔼 上移",
                  command=self.move_mapping_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(mapping_button_frame, text="🔽 下移",
                  command=self.move_mapping_down).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(mapping_button_frame, text="💾 保存映射",
                  command=self.save_field_mapping, style='Primary.TButton').pack(side=tk.RIGHT)

    def create_modern_rules_section(self, parent):
        """创建现代化特殊规则区域"""
        # 特殊规则框架
        rules_frame = ttk.LabelFrame(parent, text="⚙️ 特殊规则配置",
                                   style='TLabelframe', padding="15")
        rules_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        rules_frame.columnconfigure(0, weight=1)
        rules_frame.rowconfigure(1, weight=1)

        # 规则操作按钮区域
        rules_button_frame = ttk.Frame(rules_frame, style='TFrame')
        rules_button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 当前文件显示
        ttk.Label(rules_button_frame, text="当前文件:",
                 font=ModernStyle.FONTS['heading']).pack(side=tk.LEFT, padx=(0, 10))
        self.rule_file_label = ttk.Label(rules_button_frame, text="未选择文件",
                                       foreground=ModernStyle.COLORS['text_secondary'],
                                       font=ModernStyle.FONTS['heading'])
        self.rule_file_label.pack(side=tk.LEFT, padx=(0, 20))

        # 规则操作按钮
        ttk.Button(rules_button_frame, text="➕ 添加规则",
                  command=self.add_special_rule, style='Success.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rules_button_frame, text="🗑️ 删除规则",
                  command=self.remove_special_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rules_button_frame, text="💾 保存规则",
                  command=self.save_special_rules, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rules_button_frame, text="🔄 刷新列表",
                  command=self.refresh_rules_list).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rules_button_frame, text="🔄 恢复默认",
                  command=self.reset_to_default_rules).pack(side=tk.LEFT)

        # 规则列表区域
        rules_list_container = ttk.Frame(rules_frame, style='TFrame')
        rules_list_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        rules_list_container.columnconfigure(0, weight=1)
        rules_list_container.rowconfigure(0, weight=1)

        # 创建现代化规则Treeview
        rules_columns = ('文件名', '规则描述', '银行类型')
        self.rules_tree = ttk.Treeview(rules_list_container, columns=rules_columns,
                                      show='headings', style='Modern.Treeview')

        # 设置列标题
        self.rules_tree.heading('文件名', text='📄 文件名')
        self.rules_tree.heading('规则描述', text='📝 规则描述')
        self.rules_tree.heading('银行类型', text='🏦 银行类型')

        # 设置列宽
        self.rules_tree.column('文件名', width=250, minwidth=200)
        self.rules_tree.column('规则描述', width=400, minwidth=300)
        self.rules_tree.column('银行类型', width=150, minwidth=120)

        self.rules_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 滚动条
        rules_scrollbar = ttk.Scrollbar(rules_list_container, orient=tk.VERTICAL,
                                       command=self.rules_tree.yview)
        rules_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.rules_tree.configure(yscrollcommand=rules_scrollbar.set)

        # 绑定事件
        self.rules_tree.bind('<Double-1>', self.on_rule_double_click)
        self.rules_tree.bind('<Button-3>', self.on_rule_right_click)

    def create_modern_action_section(self, parent):
        """创建现代化操作按钮区域"""
        # 操作框架
        action_frame = ttk.LabelFrame(parent, text="🚀 合并操作",
                                    style='TLabelframe', padding="15")
        action_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        action_frame.columnconfigure(1, weight=1)

        # 主要操作按钮
        main_button_frame = ttk.Frame(action_frame, style='TFrame')
        main_button_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 开始合并按钮 - 突出显示
        self.merge_btn = ttk.Button(main_button_frame, text="🎯 开始合并 Excel 文件",
                                   command=self.start_merge, style='Primary.TButton',
                                   width=30)
        self.merge_btn.pack(side=tk.LEFT, padx=(0, 20))

        # 辅助操作按钮
        ttk.Button(main_button_frame, text="📊 预览结果",
                  command=self.preview_merge).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(main_button_frame, text="📁 打开输出文件夹",
                  command=self.open_output_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(main_button_frame, text="⚙️ 设置",
                  command=self.show_settings).pack(side=tk.LEFT)

        # 进度显示区域
        progress_frame = ttk.Frame(action_frame, style='TFrame')
        progress_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        progress_frame.columnconfigure(0, weight=1)

        # 进度条
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           length=400, mode='determinate',
                                           style='Modern.Horizontal.TProgressbar')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        # 进度文本
        self.progress_text_var = tk.StringVar(value="就绪")
        self.progress_text_label = ttk.Label(progress_frame, textvariable=self.progress_text_var,
                                           foreground=ModernStyle.COLORS['text_secondary'])
        self.progress_text_label.grid(row=0, column=1)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 初始状态
        self.status_bar.set_status("🎉 欢迎使用 Excel 文档合并工具 v2.0")
        self.status_bar.set_file_count(0)

    def initialize_data(self):
        """初始化数据"""
        # 初始化字段映射数据
        self.field_mappings = {}
        self.file_columns_cache = {}
        self.is_updating_mapping = False

        # 默认标准字段
        self.standard_fields = [
            "交易时间", "收入", "支出", "余额", "摘要", "对方户名"
        ]

        # 加载特殊规则
        self.load_special_rules()

        # 更新显示
        self.update_standard_fields_list()

    # 以下是继承的原有方法，保持功能不变但添加了现代化改进
    def import_files(self):
        """导入文件 - 现代化版"""
        file_paths = filedialog.askopenfilenames(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )

        if file_paths:
            # 显示进度
            self.status_bar.show_progress()
            self.status_bar.set_status(f"正在导入 {len(file_paths)} 个文件...")

            success_count = 0
            duplicate_count = 0
            failed_count = 0

            for i, file_path in enumerate(file_paths):
                try:
                    # 更新进度
                    progress = int((i / len(file_paths)) * 100)
                    self.status_bar.set_progress(progress)
                    self.root.update()

                    # 检查是否已导入
                    if file_path in self.imported_files:
                        duplicate_count += 1
                        continue

                    # 读取文件记录数
                    try:
                        record_count = len(pd.read_excel(file_path))
                        status = "✅ 已就绪"
                    except Exception as e:
                        record_count = "未知"
                        status = "⚠️ 读取失败"
                        failed_count += 1
                        continue

                    # 添加到导入列表
                    self.imported_files.append(file_path)

                    # 显示文件信息
                    file_name = os.path.basename(file_path)
                    file_dir = os.path.dirname(file_path)
                    self.file_treeview.insert('', 'end', values=(
                        file_name, file_dir, f"{record_count}条", status
                    ))

                    success_count += 1

                except Exception as e:
                    failed_count += 1
                    print(f"导入文件失败: {file_path}, 错误: {e}")

            # 更新状态
            self.status_bar.hide_progress()
            self.status_bar.set_file_count(len(self.imported_files))
            self.file_info_var.set(f"已导入 {len(self.imported_files)} 个文件")

            # 显示导入结果
            if failed_count > 0:
                self.show_message(f"导入完成：成功 {success_count} 个，跳过 {duplicate_count} 个，失败 {failed_count} 个",
                                "warning")
            elif duplicate_count > 0:
                self.show_message(f"成功导入 {success_count} 个文件，跳过 {duplicate_count} 个已导入文件")
            else:
                self.show_message(f"成功导入 {success_count} 个文件", "info")

    def on_file_treeview_select(self, event):
        """文件树选择事件 - 现代化版"""
        selection = self.file_treeview.selection()
        if selection:
            item = selection[0]
            values = self.file_treeview.item(item, 'values')
            file_name = values[0]
            file_path = values[1]
            full_path = os.path.join(file_path, file_name)

            # 更新当前文件显示
            self.current_file_label.config(text=file_name)
            self.rule_file_label.config(text=file_name)

            # 更新字段映射列表
            self.update_mapping_list()

            # 更新状态栏
            self.status_bar.set_status(f"已选择文件: {file_name}")

    def show_message(self, message, msg_type="info"):
        """显示现代化消息框"""
        if msg_type == "info":
            messagebox.showinfo("ℹ️ 信息", message)
        elif msg_type == "warning":
            messagebox.showwarning("⚠️ 警告", message)
        elif msg_type == "error":
            messagebox.showerror("❌ 错误", message)
        elif msg_type == "success":
            messagebox.showinfo("✅ 成功", message)

    def start_merge(self):
        """开始合并 - 现代化版"""
        if not self.imported_files:
            self.show_message("请先导入文件", "warning")
            return

        # 显示进度
        self.status_bar.show_progress()
        self.progress_text_var.set("正在准备合并...")

        # 禁用合并按钮，防止重复点击
        self.merge_btn.config(state='disabled')

        # 在新线程中执行合并操作
        import threading
        merge_thread = threading.Thread(target=self._perform_merge)
        merge_thread.daemon = True
        merge_thread.start()

    def _perform_merge(self):
        """执行合并操作 - 现代化版"""
        try:
            import os
            from datetime import datetime

            # 更新进度
            for i in range(0, 101, 10):
                self.progress_var.set(i)
                self.progress_text_var.set(f"正在合并文件... {i}%")
                self.root.update()
                import time
                time.sleep(0.1)

            # 创建输出目录
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 生成输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"合并结果_{timestamp}.xlsx")

            # 使用数据处理器进行合并
            from data_processing import DataProcessor
            from header_detection import HeaderDetector
            from special_rules import SpecialRulesManager

            # 创建数据处理器实例
            header_detector = HeaderDetector()
            special_rules_manager = SpecialRulesManager()
            data_processor = DataProcessor(header_detector, special_rules_manager)

            # 合并文件
            merge_result = data_processor.merge_files(self.imported_files, output_file)

            if merge_result:
                # 完成进度
                self.progress_var.set(100)
                self.progress_text_var.set(f"合并完成！共 {merge_result.total_records} 条记录")

                # 在主线程中更新UI
                self.root.after(0, lambda: self.merge_completed(output_file, merge_result.total_records))
            else:
                self.root.after(0, lambda: self.merge_failed("合并失败"))

        except Exception as e:
            self.root.after(0, lambda: self.merge_failed(f"合并过程中出错: {e}"))

    def merge_completed(self, output_file, record_count):
        """合并完成 - 现代化版"""
        self.progress_var.set(100)
        self.progress_text_var.set(f"✅ 合并完成！共 {record_count} 条记录")

        # 恢复按钮状态
        self.merge_btn.config(state='normal')

        # 更新状态栏
        self.status_bar.hide_progress()
        self.status_bar.set_status(f"✅ 合并完成！输出文件：{os.path.basename(output_file)}")

        # 显示成功消息
        self.show_message(f"🎉 文件合并完成！\n\n📁 输出文件: {output_file}\n📊 合并记录数: {record_count:,} 条\n\n是否立即打开输出文件夹？",
                        "success")

    def merge_failed(self, error_message):
        """合并失败 - 现代化版"""
        self.progress_text_var.set("❌ 合并失败")

        # 恢复按钮状态
        self.merge_btn.config(state='normal')

        # 更新状态栏
        self.status_bar.hide_progress()
        self.status_bar.set_status("❌ 合并失败")

        # 显示错误消息
        self.show_message(f"❌ 合并失败: {error_message}", "error")

    # 以下是其他必要的方法，从原始UI继承并保持功能
    def remove_selected_file(self):
        """删除选中的文件"""
        selection = self.file_treeview.selection()
        if not selection:
            self.show_message("请先选择要删除的文件", "warning")
            return

        item = selection[0]
        values = self.file_treeview.item(item, 'values')
        file_name = values[0]

        # 找到对应的文件路径
        file_path = None
        for path in self.imported_files:
            if os.path.basename(path) == file_name:
                file_path = path
                break

        if not file_path:
            self.show_message("未找到对应的文件", "error")
            return

        if messagebox.askyesno("确认删除", f"确定要删除文件 {file_name} 吗？"):
            self.imported_files.remove(file_path)
            self.file_treeview.delete(item)

            # 更新状态
            self.status_bar.set_file_count(len(self.imported_files))
            self.file_info_var.set(f"已导入 {len(self.imported_files)} 个文件")
            self.status_bar.set_status(f"已删除文件: {file_name}")

    def reimport_file(self):
        """重新导入文件"""
        selection = self.file_treeview.selection()
        if not selection:
            self.show_message("请先选择要重新导入的文件", "warning")
            return

        item = selection[0]
        values = self.file_treeview.item(item, 'values')
        file_name = values[0]

        # 找到对应的文件路径
        old_path = None
        for path in self.imported_files:
            if os.path.basename(path) == file_name:
                old_path = path
                break

        if not old_path:
            self.show_message("未找到对应的文件", "error")
            return

        new_path = filedialog.askopenfilename(
            title="重新选择文件",
            filetypes=[("Excel文件", "*.xlsx *.xls")]
        )
        if new_path:
            # 更新文件路径
            index = self.imported_files.index(old_path)
            self.imported_files[index] = new_path

            # 读取新文件的记录数
            try:
                record_count = len(pd.read_excel(new_path))
                status = "✅ 已就绪"
            except:
                record_count = "未知"
                status = "⚠️ 读取失败"

            # 更新Treeview显示
            new_file_name = os.path.basename(new_path)
            new_file_dir = os.path.dirname(new_path)
            self.file_treeview.item(item, values=(
                new_file_name, new_file_dir, f"{record_count}条", status
            ))

            self.show_message("文件重新导入成功", "success")
            self.status_bar.set_status(f"已重新导入文件: {new_file_name}")

    def clear_file_list(self):
        """清空文件列表"""
        if messagebox.askyesno("确认清空", "确定要清空所有文件吗？"):
            self.imported_files.clear()

            # 清空Treeview
            for item in self.file_treeview.get_children():
                self.file_treeview.delete(item)

            # 清空字段映射数据
            self.field_mappings.clear()
            for item in self.mapping_treeview.get_children():
                self.mapping_treeview.delete(item)

            # 更新状态
            self.status_bar.set_file_count(0)
            self.file_info_var.set("未导入文件")
            self.current_file_label.config(text="未选择文件")
            self.rule_file_label.config(text="未选择文件")
            self.status_bar.set_status("文件列表已清空")

            self.show_message("文件列表已清空", "info")

    def add_standard_field(self):
        """添加标准字段"""
        field_name = self.standard_field_var.get().strip()
        if not field_name:
            self.show_message("请输入标准字段名称", "warning")
            return

        if field_name in self.standard_fields:
            self.show_message("标准字段已存在", "warning")
            return

        self.standard_fields.append(field_name)
        self.update_standard_fields_list()
        self.standard_field_var.set("")
        self.show_message(f"标准字段 '{field_name}' 添加成功", "success")

    def remove_standard_field(self):
        """删除标准字段"""
        field_name = self.standard_field_var.get().strip()
        if not field_name:
            self.show_message("请输入要删除的标准字段名称", "warning")
            return

        if field_name not in self.standard_fields:
            self.show_message("标准字段不存在", "warning")
            return

        if messagebox.askyesno("确认删除", f"确定要删除标准字段 '{field_name}' 吗？"):
            self.standard_fields.remove(field_name)
            self.update_standard_fields_list()
            self.standard_field_var.set("")
            self.show_message(f"标准字段 '{field_name}' 删除成功", "success")

    def edit_standard_field(self):
        """修改标准字段"""
        old_field_name = self.standard_field_var.get().strip()
        if not old_field_name:
            self.show_message("请输入要修改的标准字段名称", "warning")
            return

        if old_field_name not in self.standard_fields:
            self.show_message("标准字段不存在", "warning")
            return

        # 弹出对话框获取新字段名
        new_field_name = simpledialog.askstring("修改标准字段",
                                              f"请输入新的标准字段名称:",
                                              initialvalue=old_field_name)
        if not new_field_name:
            return

        if new_field_name in self.standard_fields and new_field_name != old_field_name:
            self.show_message("标准字段已存在", "warning")
            return

        # 更新标准字段列表
        index = self.standard_fields.index(old_field_name)
        self.standard_fields[index] = new_field_name

        # 更新所有文件中的映射
        for file_name in self.field_mappings:
            for mapping in self.field_mappings[file_name]:
                if mapping['standard_field'] == old_field_name:
                    mapping['standard_field'] = new_field_name

        self.update_standard_fields_list()
        self.standard_field_var.set("")
        self.show_message(f"标准字段修改成功: '{old_field_name}' -> '{new_field_name}'", "success")

    def update_standard_fields_list(self):
        """更新标准字段列表显示"""
        self.update_mapping_list()

    def update_mapping_list(self):
        """更新字段映射列表显示"""
        # 防止重复更新
        if self.is_updating_mapping:
            return
        self.is_updating_mapping = True

        try:
            # 清空现有项目
            for item in self.mapping_treeview.get_children():
                self.mapping_treeview.delete(item)

            # 获取当前选中的文件
            current_file = self.get_current_selected_file()
            if not current_file:
                return

            # 获取该文件的列名作为下拉选项
            file_columns = self.get_file_columns(current_file)
            file_columns = [col for col in file_columns if col and str(col).strip() and str(col) != 'nan']
            dropdown_options = ['未映射'] + file_columns
            self.mapping_treeview.set_dropdown_values(dropdown_options)

            # 尝试从配置文件加载已保存的映射配置
            self.load_field_mappings_for_file(current_file)

            # 获取该文件的映射配置
            file_mappings = self.field_mappings.get(current_file, {})

            # 为每个标准字段创建映射项
            for standard_field in self.standard_fields:
                mapping_info = file_mappings.get(standard_field, {})
                imported_column = mapping_info.get('imported_column', '')
                is_mapped = mapping_info.get('is_mapped', False)

                display_column = imported_column if imported_column else "未映射"

                self.mapping_treeview.insert('', 'end', values=(
                    standard_field,
                    display_column,
                    "是" if is_mapped else "否"
                ))
        finally:
            self.is_updating_mapping = False

    def load_field_mappings_for_file(self, file_path):
        """为指定文件加载字段映射配置"""
        try:
            import json
            import os
            import sys

            # 确定配置目录位置
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(os.path.abspath(sys.executable))
                config_dir = os.path.join(exe_dir, "config")
            else:
                config_dir = "config"

            config_file = os.path.join(config_dir, "field_mapping_config.json")

            if not os.path.exists(config_file):
                return

            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 标准化文件路径，用于匹配
            file_key = os.path.normpath(file_path)
            file_name = os.path.basename(file_path)

            # 尝试多种匹配方式
            saved_mappings = None

            # 1. 完整路径匹配
            if file_key in config_data:
                saved_mappings = config_data[file_key]
                print(f"通过完整路径找到映射配置: {file_key}")

            # 2. 标准化路径匹配
            if not saved_mappings:
                for config_key in config_data.keys():
                    if os.path.normpath(config_key) == file_key:
                        saved_mappings = config_data[config_key]
                        print(f"通过标准化路径找到映射配置: {config_key}")
                        break

            # 3. 文件名匹配
            if not saved_mappings:
                for config_key in config_data.keys():
                    if os.path.basename(config_key) == file_name:
                        saved_mappings = config_data[config_key]
                        print(f"通过文件名找到映射配置: {config_key}")
                        break

            # 4. 模糊匹配
            if not saved_mappings:
                for config_key in config_data.keys():
                    if file_name in config_key or config_key.endswith(file_name):
                        saved_mappings = config_data[config_key]
                        print(f"通过模糊匹配找到映射配置: {config_key}")
                        break

            # 如果找到保存的映射，更新内存中的配置
            if saved_mappings:
                if file_path not in self.field_mappings:
                    self.field_mappings[file_path] = {}

                for mapping in saved_mappings:
                    standard_field = mapping.get('standard_field', '')
                    imported_column = mapping.get('imported_column', '')
                    is_mapped = mapping.get('is_mapped', False)

                    # 处理字段名不一致的问题：交易日期 -> 交易时间
                    if standard_field == '交易日期':
                        standard_field = '交易时间'

                    if standard_field:
                        self.field_mappings[file_path][standard_field] = {
                            'imported_column': imported_column,
                            'is_mapped': is_mapped
                        }
                        print(f"加载映射: {standard_field} -> {imported_column} (映射: {is_mapped})")

                print(f"成功加载 {len(saved_mappings)} 个字段映射配置")
            else:
                print(f"未找到文件 {file_name} 的映射配置")

        except Exception as e:
            print(f"加载字段映射配置时出错: {e}")

    def get_current_selected_file(self):
        """获取当前选中的文件"""
        selection = self.file_treeview.selection()
        if selection:
            item = selection[0]
            values = self.file_treeview.item(item, 'values')
            if values:
                file_name = values[0]
                file_path = values[1]
                full_path = os.path.join(file_path, file_name)
                return os.path.normpath(full_path)
        return None

    def get_file_columns(self, file_path):
        """获取文件的列名"""
        try:
            if file_path in self.file_columns_cache:
                return self.file_columns_cache[file_path]

            from header_detection import HeaderDetector
            detector = HeaderDetector()
            headers = detector.detect_headers(file_path)

            if headers:
                columns = headers[0].columns
            else:
                df = pd.read_excel(file_path)
                columns = df.columns.tolist()

            self.file_columns_cache[file_path] = columns
            return columns

        except Exception as e:
            self.show_message(f"获取文件列名失败: {str(e)}", "error")
        return []

    def on_mapping_value_change(self, item, new_value):
        """处理映射值改变事件"""
        current_file = self.get_current_selected_file()
        if not current_file:
            return

        current_values = self.mapping_treeview.item(item, 'values')
        standard_field = current_values[0]

        if current_file not in self.field_mappings:
            self.field_mappings[current_file] = {}

        if new_value == "未映射" or not new_value:
            self.field_mappings[current_file][standard_field] = {
                'imported_column': '',
                'is_mapped': False
            }
        else:
            self.field_mappings[current_file][standard_field] = {
                'imported_column': new_value,
                'is_mapped': True
            }

        # 自动保存字段映射配置
        self.auto_save_field_mapping(current_file)

    def auto_save_field_mapping(self, file_path):
        """自动保存字段映射配置（静默保存，不显示消息）"""
        try:
            if not file_path or file_path not in self.field_mappings:
                return

            # 获取当前映射配置
            mappings = []
            for standard_field in self.standard_fields:
                if standard_field in self.field_mappings[file_path]:
                    mapping_info = self.field_mappings[file_path][standard_field]
                    mappings.append({
                        'standard_field': standard_field,
                        'imported_column': mapping_info.get('imported_column', ''),
                        'is_mapped': mapping_info.get('is_mapped', False)
                    })

            # 保存到配置文件
            import json
            import os
            import sys

            file_key = os.path.normpath(file_path)

            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(os.path.abspath(sys.executable))
                config_dir = os.path.join(exe_dir, "config")
            else:
                config_dir = "config"

            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            config_file = os.path.join(config_dir, "field_mapping_config.json")
            config_data = {}
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

            config_data[file_key] = mappings

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            # 更新状态栏但不显示消息框
            self.status_bar.set_status(f"字段映射已自动保存: {os.path.basename(file_path)}")

        except Exception as e:
            print(f"自动保存字段映射失败: {str(e)}")

    def move_mapping_up(self):
        """上移选中的映射项"""
        selection = self.mapping_treeview.selection()
        if not selection:
            return

        item = selection[0]
        parent = self.mapping_treeview.parent(item)
        siblings = self.mapping_treeview.get_children(parent)

        if item in siblings:
            index = siblings.index(item)
            if index > 0:
                prev_item = siblings[index - 1]
                self.mapping_treeview.move(item, parent, index - 1)

    def move_mapping_down(self):
        """下移选中的映射项"""
        selection = self.mapping_treeview.selection()
        if not selection:
            return

        item = selection[0]
        parent = self.mapping_treeview.parent(item)
        siblings = self.mapping_treeview.get_children(parent)

        if item in siblings:
            index = siblings.index(item)
            if index < len(siblings) - 1:
                next_item = siblings[index + 1]
                self.mapping_treeview.move(item, parent, index + 1)

    def save_field_mapping(self):
        """保存字段映射配置"""
        current_file = self.get_current_selected_file()
        if not current_file:
            self.show_message("请先选择要保存映射的文件", "warning")
            return

        try:
            # 获取当前映射配置
            mappings = []
            for item in self.mapping_treeview.get_children():
                values = self.mapping_treeview.item(item, 'values')
                standard_field, imported_column, is_mapped = values

                mappings.append({
                    'standard_field': standard_field,
                    'imported_column': imported_column,
                    'is_mapped': is_mapped == "是"
                })

            # 保存到配置文件
            import json
            import os
            import sys

            file_key = os.path.normpath(current_file)

            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(os.path.abspath(sys.executable))
                config_dir = os.path.join(exe_dir, "config")
            else:
                config_dir = "config"

            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            config_file = os.path.join(config_dir, "field_mapping_config.json")
            config_data = {}
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

            config_data[file_key] = mappings

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            self.show_message(f"字段映射配置已保存: {os.path.basename(current_file)}", "success")
            self.status_bar.set_status(f"已保存字段映射配置")

        except Exception as e:
            self.show_message(f"保存字段映射配置失败: {str(e)}", "error")

    # 特殊规则相关方法
    def add_special_rule(self):
        """添加特殊规则"""
        file_name = self.rule_file_label.cget("text")

        if file_name == "未选择文件":
            self.show_message("请先选择文件", "warning")
            return

        # 弹出对话框输入规则描述
        rule_description = simpledialog.askstring("添加特殊规则",
                                                 "请输入规则描述:")
        if not rule_description:
            return

        # 添加到数据存储
        if file_name not in self.special_rules:
            self.special_rules[file_name] = []

        self.special_rules[file_name].append(rule_description)

        # 推断银行名称
        bank_name = self._extract_bank_name_from_filename(file_name)

        # 添加到Treeview显示
        self.rules_tree.insert('', 'end', values=(file_name, rule_description, bank_name or "未知"))

        # 添加到SpecialRulesManager
        if hasattr(self, 'special_rules_manager') and self.special_rules_manager and bank_name:
            try:
                result = self.special_rules_manager.add_rule(rule_description, bank_name)
                if result.get("success"):
                    self.show_message(f"规则已添加: {bank_name}", "success")
                else:
                    self.show_message(f"规则添加失败: {result.get('error', '未知错误')}", "error")
            except Exception as e:
                self.show_message(f"规则保存失败: {str(e)}", "error")

        self.status_bar.set_status(f"已添加特殊规则: {rule_description}")

    def remove_special_rule(self):
        """删除特殊规则"""
        selection = self.rules_tree.selection()
        if not selection:
            self.show_message("请选择要删除的规则", "warning")
            return

        item = selection[0]
        values = self.rules_tree.item(item, 'values')
        file_name = values[0]
        rule_text = values[1]

        if messagebox.askyesno("确认删除", f"确定要删除规则吗？\n\n规则: {rule_text}"):
            # 从数据存储中删除
            if file_name in self.special_rules and rule_text in self.special_rules[file_name]:
                self.special_rules[file_name].remove(rule_text)
                if not self.special_rules[file_name]:
                    del self.special_rules[file_name]

            # 从Treeview中删除
            self.rules_tree.delete(item)

            self.show_message("规则删除成功", "success")
            self.status_bar.set_status(f"已删除特殊规则")

    def save_special_rules(self):
        """保存特殊规则到文件"""
        try:
            if hasattr(self, 'special_rules_manager') and self.special_rules_manager:
                success = self.special_rules_manager.save_rules()
                if success:
                    self.show_message("特殊规则已保存", "success")
                    self.status_bar.set_status("特殊规则保存完成")
                else:
                    self.show_message("保存规则失败", "error")
            else:
                import json
                config_file = "special_rules.json"
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.special_rules, f, ensure_ascii=False, indent=2)
                self.show_message(f"特殊规则已保存到 {config_file}", "success")
        except Exception as e:
            self.show_message(f"保存规则失败: {str(e)}", "error")

    def refresh_rules_list(self):
        """刷新规则列表"""
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        self.load_special_rules()
        self.status_bar.set_status("规则列表已刷新")

    def load_special_rules(self):
        """加载特殊文件合并规则"""
        try:
            import json
            import os

            rules_config_file = "config/rules_config.json"
            if os.path.exists(rules_config_file):
                with open(rules_config_file, 'r', encoding='utf-8') as f:
                    rules_config = json.load(f)

                for rule in rules_config:
                    bank_name = rule.get('bank_name', '未知银行')
                    description = rule.get('description', '无描述')

                    file_path = self._find_matching_file(bank_name)
                    if file_path:
                        self.rules_tree.insert('', 'end', values=(file_path, description, bank_name))
                    else:
                        self.rules_tree.insert('', 'end', values=(bank_name, description, bank_name))

                if rules_config:
                    self.status_bar.set_status(f"已加载 {len(rules_config)} 个特殊规则")
        except Exception as e:
            print(f"加载规则失败: {e}")

    def _find_matching_file(self, bank_name):
        """根据银行名称查找匹配的文件路径"""
        for file_path in self.imported_files:
            file_name = os.path.basename(file_path)
            if bank_name in file_name:
                return file_path
        return None

    def _extract_bank_name_from_filename(self, file_name):
        """从文件名提取银行名称"""
        name = os.path.splitext(file_name)[0]

        bank_keywords = [
            '北京银行', '工商银行', '华夏银行', '招商银行', '长安银行',
            '建设银行', '农业银行', '中国银行', '浦发银行', '兴业银行',
            '邮储银行', '光大银行', '民生银行', '中信银行', '交通银行'
        ]

        for keyword in bank_keywords:
            if keyword in name:
                return keyword

        return None

    def on_rule_double_click(self, event):
        """双击规则行进行编辑"""
        selection = self.rules_tree.selection()
        if not selection:
            return

        item = selection[0]
        column = self.rules_tree.identify_column(event.x)

        if column == '#2':  # 规则描述列
            self.edit_rule_inline(item, 1)

    def edit_rule_inline(self, item, column):
        """内联编辑规则"""
        values = list(self.rules_tree.item(item, 'values'))
        current_value = values[column]

        # 创建编辑框
        edit_frame = ttk.Frame(self.rules_tree)
        edit_entry = ttk.Entry(edit_frame, width=50, font=ModernStyle.FONTS['default'])
        edit_entry.insert(0, current_value)
        edit_entry.pack(fill=tk.X, expand=True)

        def save_edit():
            new_value = edit_entry.get()
            values[column] = new_value
            self.rules_tree.item(item, values=values)

            # 更新数据存储
            file_name = values[0]
            rule_text = values[1]

            if file_name in self.special_rules:
                for i, rule in enumerate(self.special_rules[file_name]):
                    if rule == current_value:
                        self.special_rules[file_name][i] = new_value
                        break

            edit_frame.destroy()
            self.status_bar.set_status(f"规则已更新: {new_value}")

        def cancel_edit():
            edit_frame.destroy()

        edit_entry.bind('<Return>', lambda e: save_edit())
        edit_entry.bind('<Escape>', lambda e: cancel_edit())
        edit_entry.bind('<FocusOut>', lambda e: save_edit())

        bbox = self.rules_tree.bbox(item, column)
        if bbox:
            edit_frame.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
            edit_entry.focus_set()
            edit_entry.select_range(0, tk.END)

    def on_rule_right_click(self, event):
        """右键菜单"""
        selection = self.rules_tree.selection()
        if not selection:
            return

        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="✏️ 编辑规则", command=lambda: self.edit_rule_inline(selection[0], 1))
        context_menu.add_command(label="🗑️ 删除规则", command=self.remove_special_rule)
        context_menu.add_separator()
        context_menu.add_command(label="➕ 添加新规则", command=self.add_special_rule)

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def reset_to_default_rules(self):
        """恢复默认规则"""
        try:
            import json
            import os
            import shutil

            if not messagebox.askyesno("确认操作",
                                       "确定要恢复默认规则吗？\n这将覆盖当前的所有规则。"):
                return

            # 备份当前规则
            current_config = "config/rules_config.json"
            backup_config = "config/rules_config_backup.json"
            if os.path.exists(current_config):
                shutil.copy2(current_config, backup_config)

            # 复制默认规则
            default_config = "config/default_rules_config.json"
            if os.path.exists(default_config):
                shutil.copy2(default_config, current_config)

                # 重新加载规则
                self.rules_tree.delete(*self.rules_tree.get_children())
                self.load_special_rules()

                self.show_message("已恢复默认规则", "success")
                self.status_bar.set_status("已恢复默认规则")
            else:
                self.show_message("默认规则配置文件不存在", "error")

        except Exception as e:
            self.show_message(f"恢复默认规则失败: {str(e)}", "error")

    # 新增的现代化功能方法
    def preview_merge(self):
        """预览合并结果"""
        if not self.imported_files:
            self.show_message("请先导入文件", "warning")
            return

        # 这里可以实现预览功能
        self.show_message("预览功能正在开发中...", "info")

    def open_output_folder(self):
        """打开输出文件夹"""
        import os
        import subprocess
        import platform

        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            if platform.system() == "Windows":
                os.startfile(output_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", output_dir])
            else:  # Linux
                subprocess.run(["xdg-open", output_dir])
        except Exception as e:
            self.show_message(f"无法打开输出文件夹: {str(e)}", "error")

    def show_settings(self):
        """显示设置对话框"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ 设置")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()

        # 居中显示
        self.center_child_window(settings_window)

        # 设置内容
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="应用程序设置",
                 font=ModernStyle.FONTS['heading']).pack(pady=(0, 20))

        # 设置选项
        ttk.Label(main_frame, text="默认输出目录:").pack(anchor=tk.W, pady=(10, 5))

        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))

        output_var = tk.StringVar(value="output")
        ttk.Entry(output_frame, textvariable=output_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(output_frame, text="浏览", command=lambda: None).pack(side=tk.LEFT)

        ttk.Label(main_frame, text="自动保存字段映射:").pack(anchor=tk.W, pady=(10, 5))
        auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="启用自动保存",
                       variable=auto_save_var).pack(anchor=tk.W)

        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))

        ttk.Button(button_frame, text="保存设置",
                  command=settings_window.destroy).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消",
                  command=settings_window.destroy).pack(side=tk.LEFT)

    def center_child_window(self, window):
        """子窗口居中显示"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def run(self):
        """运行界面"""
        # 显示启动画面或欢迎信息
        self.status_bar.set_status("🎉 界面初始化完成，欢迎使用现代化Excel合并工具！")
        self.root.mainloop()


if __name__ == "__main__":
    # 启动现代化界面
    app = ModernExcelMergeUI()
    app.run()