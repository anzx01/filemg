"""
Excel文档合并工具 - 用户界面模块
负责创建和管理用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.ttk import Combobox
from typing import List, Dict, Any
import os
import pandas as pd


class TreeviewWithDropdown(ttk.Treeview):
    """支持内联下拉列表的Treeview"""
    
    def __init__(self, parent, columns, dropdown_column_index=1, **kwargs):
        super().__init__(parent, columns=columns, **kwargs)
        self.dropdown_column_index = dropdown_column_index
        self.dropdown_values = []
        self.current_combobox = None
        self.on_value_change_callback = None
        
        # 绑定事件
        self.bind('<Button-1>', self.on_click)
        # 移除双击事件绑定，只保留单击事件
        # self.bind('<Double-1>', self.on_double_click)
        self.bind('<FocusOut>', self.on_focus_out)
        
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
    
    def on_double_click(self, event):
        """处理双击事件"""
        item = self.identify_row(event.y)
        column = self.identify_column(event.x)
        
        if item and column:
            # 获取列索引
            column_index = int(column.replace('#', '')) - 1
            
            # 只有在下拉列才处理双击事件，其他列（如标准字段列）不处理
            if column_index == self.dropdown_column_index:
                self.show_inline_dropdown(item, event.x, event.y)
            # 对于标准字段列（第0列），不处理双击事件，避免改变列表大小
                
    def show_inline_dropdown(self, item, x, y):
        """显示内联下拉框"""
        print(f"show_inline_dropdown 被调用: item={item}")
        
        # 隐藏当前下拉框
        if self.current_combobox:
            self.current_combobox.destroy()
            self.current_combobox = None
        
        # 检查下拉框值是否设置
        if not self.dropdown_values:
            print("下拉框值未设置")
            return
        
        # 获取当前值
        current_values = self.item(item, 'values')
        current_value = current_values[self.dropdown_column_index] if len(current_values) > self.dropdown_column_index else ''
        print(f"当前值: {current_value}")
        
        # 获取列的位置和大小
        column_id = f"#{self.dropdown_column_index + 1}"
        bbox = self.bbox(item, column_id)
        
        if not bbox:
            print(f"无法获取列位置: item={item}, column_id={column_id}")
            # 尝试使用传入的坐标
            print(f"使用传入坐标: x={x}, y={y}")
            # 创建一个固定大小的下拉框
            width, height = 200, 25
        else:
            x, y, width, height = bbox
            print(f"获取到列位置: x={x}, y={y}, width={width}, height={height}")
        
        try:
            # 创建Combobox - 直接在当前Treeview上创建
            combobox = Combobox(self, values=self.dropdown_values, state="readonly")
            combobox.set(current_value)
            
            # 设置位置 - 使用place方法精确定位
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
            # 移除FocusOut绑定，避免下拉框被立即销毁
            # combobox.bind('<FocusOut>', on_focus_out)
            combobox.bind('<Escape>', on_escape)
            
            # 保存引用
            self.current_combobox = combobox
            
            # 强制更新显示
            self.update()
            combobox.update()
            
            # 获取焦点并打开下拉列表
            combobox.focus_set()
            combobox.focus()
            
            # 延迟打开下拉列表
            def open_dropdown():
                if self.current_combobox and self.current_combobox.winfo_exists():
                    try:
                        self.current_combobox.focus_set()
                        # 使用最简单的方法打开下拉框
                        self.current_combobox.event_generate('<Button-1>')
                    except Exception as e:
                        print(f"打开下拉框失败: {e}")
            
            # 减少延迟时间，提高响应速度
            self.after(50, open_dropdown)
            
            print(f"下拉框已创建: x={x}, y={y}, width={width}, height={height}")
            
        except Exception as e:
            print(f"创建下拉框时出错: {e}")
            import traceback
            traceback.print_exc()
            if 'combobox' in locals():
                combobox.destroy()
            self.current_combobox = None
    
    def on_focus_out(self, event):
        """处理失去焦点事件"""
        # 延迟销毁，给下拉框一些时间
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
            # 如果选择了"未映射"或空值，则设为未映射
            if new_value == "未映射" or not new_value or new_value.strip() == "":
                current_values[2] = "否"  # 是否映射列
            else:
                current_values[2] = "是"  # 是否映射列
            self.item(item, values=current_values)
            
            # 调用回调函数
            if self.on_value_change_callback:
                self.on_value_change_callback(item, new_value)


class ExcelMergeUI:
    """Excel合并工具主界面类"""
    
    def __init__(self):
        """初始化界面"""
        self.root = tk.Tk()
        self.root.title("Excel文档合并工具")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        self.root.resizable(True, True)  # 允许调整大小，但保持初始大小
        
        # 设置窗口居中显示
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # 界面变量
        self.imported_files = []
        self.special_rules = {}
        
        # 初始化特殊规则管理器
        from special_rules import SpecialRulesManager
        self.special_rules_manager = SpecialRulesManager()
        
        
        
        # 创建界面
        self.create_main_window()
    
        
    def create_main_window(self):
        """创建主窗口"""
        # 设置窗口样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # 左侧文件导入区域
        main_frame.columnconfigure(1, weight=1)  # 右侧字段映射区域
        
        # 创建各个功能区域
        self.create_file_import_section(main_frame)
        self.create_field_mapping_section(main_frame)
        self.create_special_rules_section(main_frame)
        self.create_merge_section(main_frame)
        
        
    def create_file_import_section(self, parent):
        """创建文件导入区域"""
        # 文件导入框架
        import_frame = ttk.LabelFrame(parent, text="文件导入管理", padding="5")
        import_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        import_frame.columnconfigure(0, weight=1)
        import_frame.rowconfigure(2, weight=1)
        
        # 导入按钮
        ttk.Button(import_frame, text="选择Excel文件", 
                  command=self.import_files).grid(row=0, column=0, pady=(0, 5))
        
        # 已导入文件列表
        ttk.Label(import_frame, text="已导入文件:").grid(row=1, column=0, sticky=tk.W, pady=(0, 3))
        
        # 文件列表框架
        list_frame = ttk.Frame(import_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 使用Treeview替代Listbox，显示文件名、路径、记录数
        columns = ('文件名', '路径', '记录数')
        self.file_treeview = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        
        # 设置列标题和宽度
        self.file_treeview.heading('文件名', text='文件名')
        self.file_treeview.heading('路径', text='路径')
        self.file_treeview.heading('记录数', text='记录数')
        
        self.file_treeview.column('文件名', width=150, minwidth=100)
        self.file_treeview.column('路径', width=300, minwidth=200)
        self.file_treeview.column('记录数', width=80, minwidth=60)
        
        # 使用固定高度，避免界面大小变化
        self.file_treeview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.file_treeview.configure(height=6)  # 明确设置固定高度
        
        # 防止Treeview自动调整大小
        self.file_treeview.grid_propagate(False)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_treeview.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_treeview.configure(yscrollcommand=scrollbar.set)
        
        # 绑定选择事件
        self.file_treeview.bind('<<TreeviewSelect>>', self.on_file_treeview_select)
        
        # 文件操作按钮
        button_frame = ttk.Frame(import_frame)
        button_frame.grid(row=3, column=0, pady=(5, 0))
        
        ttk.Button(button_frame, text="删除选中", 
                  command=self.remove_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="重新导入", 
                  command=self.reimport_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空列表", 
                  command=self.clear_file_list).pack(side=tk.LEFT)
        
    def create_field_mapping_section(self, parent):
        """创建字段映射配置区域"""
        # 字段映射框架
        mapping_frame = ttk.LabelFrame(parent, text="字段映射配置", padding="5")
        mapping_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        mapping_frame.columnconfigure(0, weight=1)
        mapping_frame.rowconfigure(2, weight=1)
        
        # 当前文件显示区域
        current_file_frame = ttk.Frame(mapping_frame)
        current_file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        current_file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(current_file_frame, text="当前文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.current_file_label = ttk.Label(current_file_frame, text="未选择文件", foreground="gray")
        self.current_file_label.grid(row=0, column=1, sticky=tk.W)
        
        # 字段映射列表区域（合并了标准字段管理和映射配置）
        mapping_list_frame = ttk.LabelFrame(mapping_frame, text="字段映射列表", padding="3")
        mapping_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        mapping_list_frame.columnconfigure(0, weight=1)
        mapping_list_frame.rowconfigure(1, weight=1)
        
        # 字段映射列表框架
        list_container_frame = ttk.Frame(mapping_list_frame)
        list_container_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_container_frame.columnconfigure(0, weight=1)
        list_container_frame.rowconfigure(0, weight=1)
        
        # 使用支持下拉列表的Treeview显示字段映射（合并了标准字段和映射信息）
        mapping_columns = ('标准字段', '导入文件列名', '是否映射')
        self.mapping_treeview = TreeviewWithDropdown(list_container_frame, columns=mapping_columns, show='headings', height=6, dropdown_column_index=1)
        
        # 设置列标题和宽度
        self.mapping_treeview.heading('标准字段', text='标准字段')
        self.mapping_treeview.heading('导入文件列名', text='导入文件列名')
        self.mapping_treeview.heading('是否映射', text='是否映射')
        
        self.mapping_treeview.column('标准字段', width=120, minwidth=100)
        self.mapping_treeview.column('导入文件列名', width=150, minwidth=120)
        self.mapping_treeview.column('是否映射', width=80, minwidth=60)
        
        # 使用固定高度，避免界面大小变化
        self.mapping_treeview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.mapping_treeview.configure(height=6)  # 明确设置固定高度
        
        # 防止Treeview自动调整大小
        self.mapping_treeview.grid_propagate(False)
        
        # 设置值改变回调函数
        self.mapping_treeview.set_value_change_callback(self.on_mapping_value_change)
        
        # 滚动条
        mapping_scrollbar = ttk.Scrollbar(list_container_frame, orient=tk.VERTICAL, command=self.mapping_treeview.yview)
        mapping_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.mapping_treeview.configure(yscrollcommand=mapping_scrollbar.set)
        
        # 绑定选择事件用于编辑
        self.mapping_treeview.bind('<<TreeviewSelect>>', self.on_mapping_select)
        # 移除双击事件绑定，让TreeviewWithDropdown自己处理
        # self.mapping_treeview.bind('<Double-1>', self.on_mapping_double_click)
        
        # 添加右键菜单
        
        # 标准字段管理按钮区域
        field_management_frame = ttk.Frame(mapping_list_frame)
        field_management_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 3))
        field_management_frame.columnconfigure(1, weight=1)
        
        # 标准字段输入框
        ttk.Label(field_management_frame, text="标准字段:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.standard_field_var = tk.StringVar()
        standard_field_entry = ttk.Entry(field_management_frame, textvariable=self.standard_field_var, width=20)
        standard_field_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 标准字段管理按钮
        field_buttons_frame = ttk.Frame(field_management_frame)
        field_buttons_frame.grid(row=0, column=2, sticky=tk.W)
        
        ttk.Button(field_buttons_frame, text="添加", command=self.add_standard_field, width=8).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(field_buttons_frame, text="删除", command=self.remove_standard_field, width=8).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(field_buttons_frame, text="编辑", command=self.edit_standard_field, width=8).pack(side=tk.LEFT, padx=(0, 2))
        
        # 映射顺序调整按钮
        move_buttons_frame = ttk.Frame(field_management_frame)
        move_buttons_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(3, 0))
        
        ttk.Button(move_buttons_frame, text="上移", command=self.move_mapping_up, width=8).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(move_buttons_frame, text="下移", command=self.move_mapping_down, width=8).pack(side=tk.LEFT, padx=(0, 2))
        
        # 保存映射配置按钮
        save_buttons_frame = ttk.Frame(field_management_frame)
        save_buttons_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(3, 0))
        
        ttk.Button(save_buttons_frame, text="保存映射配置", command=self.save_field_mapping, width=12).pack(side=tk.LEFT, padx=(0, 5))
        
        # 初始化字段映射数据
        self.field_mappings = {}  # 存储每个文件的字段映射配置
        self.file_columns_cache = {}  # 缓存文件列名，避免重复检测
        self.is_updating_mapping = False  # 防止重复更新标志
        self.standard_fields = [  # 默认标准字段
            "交易时间", "收入", "支出", "余额", "摘要", "对方户名"
        ]
        self.update_standard_fields_list()
        
    def create_special_rules_section(self, parent):
        """创建特殊规则区域"""
        # 特殊规则框架
        rules_frame = ttk.LabelFrame(parent, text="特殊规则配置", padding="5")
        rules_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 5))
        rules_frame.columnconfigure(1, weight=1)
        
        # 规则输入区域
        input_frame = ttk.Frame(rules_frame)
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        input_frame.columnconfigure(1, weight=1)
        
        # 当前文件名显示
        ttk.Label(input_frame, text="当前文件名:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.rule_file_label = ttk.Label(input_frame, text="未选择文件", foreground="gray")
        self.rule_file_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # 规则描述输入（移除，功能整合到已配置规则中）
        
        # 操作按钮
        button_frame = ttk.Frame(rules_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(button_frame, text="添加", command=self.add_special_rule, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除", command=self.remove_special_rule, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="保存", command=self.save_special_rules, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空", command=self.clear_rule_input, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="刷新", command=self.refresh_rules_list, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # 规则列表
        list_frame = ttk.Frame(rules_frame)
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        list_frame.columnconfigure(0, weight=1)
        
        ttk.Label(list_frame, text="特殊文件合并规则:").grid(row=0, column=0, sticky=tk.W)
        
        # 创建Treeview来显示规则
        columns = ('文件名', '规则描述')
        self.rules_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        
        # 设置列标题
        self.rules_tree.heading('文件名', text='文件名')
        self.rules_tree.heading('规则描述', text='规则描述')
        
        # 设置列宽
        self.rules_tree.column('文件名', width=200)
        self.rules_tree.column('规则描述', width=350)
        
        self.rules_tree.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(3, 0))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.rules_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.rules_tree.configure(yscrollcommand=scrollbar.set)
        
        # 绑定双击编辑事件
        self.rules_tree.bind('<Double-1>', self.on_rule_double_click)
        self.rules_tree.bind('<Button-3>', self.on_rule_right_click)  # 右键菜单
        
        # 添加恢复默认规则按钮
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(button_frame, text="恢复默认规则", 
                  command=self.reset_to_default_rules,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="清空所有规则", 
                  command=self.clear_all_rules).pack(side=tk.LEFT)
        
        # 初始化特殊规则数据
        self.special_rules = {}  # 存储特殊规则数据
        self.load_special_rules()  # 加载已保存的规则
        
    def create_merge_section(self, parent):
        """创建合并操作区域"""
        # 合并操作框架
        merge_frame = ttk.LabelFrame(parent, text="合并操作", padding="5")
        merge_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 合并按钮
        ttk.Button(merge_frame, text="开始合并", 
                  command=self.start_merge, 
                  style="Accent.TButton").pack(pady=5)
        
        # 进度条
        self.progress = ttk.Progressbar(merge_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # 状态标签
        self.status_label = ttk.Label(merge_frame, text="就绪")
        self.status_label.pack()
        
    def import_files(self):
        """导入文件"""
        file_paths = filedialog.askopenfilenames(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        
        if file_paths:
            # 如果有控制器，使用控制器处理
            if hasattr(self, 'controller') and self.controller:
                results = self.controller.handle_file_import(file_paths)
                
                # 显示导入结果
                success_count = len(results['success'])
                duplicate_count = len(results['duplicates'])
                failed_count = len(results['failed'])
                
                if duplicate_count > 0:
                    self.show_message(f"成功导入 {success_count} 个文件，跳过 {duplicate_count} 个已导入文件")
                else:
                    self.show_message(f"成功导入 {success_count} 个文件")
                
                if failed_count > 0:
                    self.show_message(f"导入失败 {failed_count} 个文件")
            else:
                # 直接处理（兼容模式）
                imported_count = 0
                duplicate_count = 0
                
                for file_path in file_paths:
                    # 检查是否已导入
                    if file_path in self.imported_files:
                        duplicate_count += 1
                        continue
                    
                    # 读取文件记录数
                    try:
                        record_count = len(pd.read_excel(file_path))
                    except:
                        record_count = "未知"
                    
                    # 添加到导入列表
                    self.imported_files.append(file_path)
                    
                    # 显示文件名、路径和记录数
                    file_name = os.path.basename(file_path)
                    file_dir = os.path.dirname(file_path)
                    self.file_treeview.insert('', 'end', values=(file_name, file_dir, f"{record_count}条"))
                    
                    # 文件已添加到树形视图，无需更新下拉框
                    
                    imported_count += 1
                
                # 显示导入结果
                if duplicate_count > 0:
                    self.show_message(f"成功导入 {imported_count} 个文件，跳过 {duplicate_count} 个已导入文件")
                else:
                    self.show_message(f"成功导入 {imported_count} 个文件")
    
    def remove_selected_file(self):
        """删除选中的文件"""
        selection = self.file_treeview.selection()
        if not selection:
            self.show_message("请先选择要删除的文件", "warning")
            return
        
        item = selection[0]
        # 获取选中项的值
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
        
        if messagebox.askyesno("确认", f"确定要删除文件 {file_name} 吗？"):
            # 如果有控制器，使用控制器处理
            if hasattr(self, 'controller') and self.controller:
                success = self.controller.handle_file_removal(file_path)
                if success:
                    self.file_treeview.delete(item)
                    self.show_message(f"已删除文件: {file_name}")
                else:
                    self.show_message("删除文件失败")
            else:
                # 直接处理（兼容模式）
                self.imported_files.remove(file_path)
                self.file_treeview.delete(item)
                self.update_file_combos()
                self.show_message(f"已删除文件: {file_name}")
    
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
            except:
                record_count = "未知"
            
            # 更新Treeview显示
            new_file_name = os.path.basename(new_path)
            new_file_dir = os.path.dirname(new_path)
            self.file_treeview.item(item, values=(new_file_name, new_file_dir, f"{record_count}条"))
            
            self.update_file_combos()
            self.show_message("文件重新导入成功")
    
    def clear_file_list(self):
        """清空文件列表"""
        if messagebox.askyesno("确认", "确定要清空所有文件吗？"):
            # 如果有控制器，使用控制器处理
            if hasattr(self, 'controller') and self.controller:
                # 逐个删除所有文件
                for file_path in self.imported_files.copy():
                    self.controller.handle_file_removal(file_path)
                self.show_message("文件列表已清空")
            else:
                # 直接处理（兼容模式）
                self.imported_files.clear()
                # 清空Treeview
                for item in self.file_treeview.get_children():
                    self.file_treeview.delete(item)
                # 清空文件选择标签
                self.rule_file_label.config(text="未选择文件", foreground="gray")
                # 清空字段映射数据
                self.field_mappings.clear()
                # 清空字段映射列表
                for item in self.mapping_treeview.get_children():
                    self.mapping_treeview.delete(item)
                self.show_message("文件列表已清空")
    
    def update_file_combos(self):
        """更新文件下拉框（已废弃，使用树形视图）"""
        # 此方法已废弃，文件选择通过树形视图进行
        pass
    
    
    
    
    
    
    
    
    
    def on_file_treeview_select(self, event):
        """文件树选择事件"""
        selection = self.file_treeview.selection()
        if selection:
            item = selection[0]
            values = self.file_treeview.item(item, 'values')
            file_name = values[0]
            file_path = values[1]
            full_path = os.path.join(file_path, file_name)
            
            # 更新当前文件显示
            self.current_file_label.config(text=file_name, foreground="black")
            
            # 更新当前文件名显示
            self.rule_file_label.config(text=file_name, foreground="black")
            
            # 更新字段映射列表
            self.update_mapping_list()
    
    
    
    
    
    
    
    
    def add_special_rule(self):
        """添加特殊规则"""
        # 从当前文件名标签获取文件名
        file_name = self.rule_file_label.cget("text")
        
        if file_name == "未选择文件":
            self.show_message("请先选择文件", "warning")
            return
        
        # 直接在列表中添加新行，用户可以双击编辑
        new_rule_text = "点击编辑规则描述..."
        
        # 添加到数据存储
        if file_name not in self.special_rules:
            self.special_rules[file_name] = []
        
        self.special_rules[file_name].append(new_rule_text)
        
        # 注意：只有在用户实际编辑规则描述后才会添加到SpecialRulesManager
        # 这里只添加到UI显示和self.special_rules中
        
        # 添加到Treeview显示
        item_id = self.rules_tree.insert('', 'end', values=(file_name, new_rule_text))
        
        # 自动选中新添加的行，方便用户编辑
        self.rules_tree.selection_set(item_id)
        self.rules_tree.see(item_id)
        
        self.show_message("新规则已添加，双击可编辑")
    
    def on_rule_double_click(self, event):
        """双击规则行进行编辑"""
        selection = self.rules_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        column = self.rules_tree.identify_column(event.x)
        
        # 只允许编辑规则描述列
        if column == '#2':  # 规则描述列
            self.edit_rule_inline(item, 1)  # 编辑第二列（规则描述）
    
    def edit_rule_inline(self, item, column):
        """内联编辑规则"""
        # 获取当前值
        values = list(self.rules_tree.item(item, 'values'))
        current_value = values[column]
        
        # 创建编辑框
        edit_frame = ttk.Frame(self.rules_tree)
        edit_entry = ttk.Entry(edit_frame, width=50)
        edit_entry.insert(0, current_value)
        edit_entry.pack(fill=tk.X, expand=True)
        
        def save_edit():
            new_value = edit_entry.get()
            values[column] = new_value
            self.rules_tree.item(item, values=values)
            
            # 更新数据存储
            file_name = values[0]
            rule_text = values[1]
            
            # 找到对应的规则并更新
            if file_name in self.special_rules:
                # 找到对应的规则索引
                for i, rule in enumerate(self.special_rules[file_name]):
                    if rule == current_value:
                        self.special_rules[file_name][i] = new_value
                        break
            
            # 如果编辑的是规则描述列（column=1），且不是默认的占位符文本
            if column == 1 and new_value != "点击编辑规则描述...":
                # 添加到SpecialRulesManager中
                if hasattr(self, 'special_rules_manager') and self.special_rules_manager:
                    try:
                        # 从文件名推断银行名称
                        bank_name = self._extract_bank_name_from_filename(file_name)
                        
                        if bank_name:
                            # 添加规则到SpecialRulesManager
                            result = self.special_rules_manager.add_rule(new_value, bank_name)
                            if result.get("success"):
                                self.show_message(f"规则已成功保存到系统: {bank_name}")
                                print(f"已添加规则到SpecialRulesManager: {bank_name}")
                            else:
                                error_msg = result.get('error', '未知错误')
                                self.show_message(f"规则保存失败: {error_msg}", "error")
                                print(f"添加规则到SpecialRulesManager失败: {error_msg}")
                        else:
                            # 如果无法自动识别银行名称，让用户手动选择
                            bank_name = self._ask_user_to_select_bank()
                            if bank_name:
                                result = self.special_rules_manager.add_rule(new_value, bank_name)
                                if result.get("success"):
                                    self.show_message(f"规则已成功保存到系统: {bank_name}")
                                else:
                                    error_msg = result.get('error', '未知错误')
                                    self.show_message(f"规则保存失败: {error_msg}", "error")
                            else:
                                self.show_message("未选择银行类型，规则未保存", "warning")
                    except Exception as e:
                        error_msg = str(e)
                        self.show_message(f"规则保存失败: {error_msg}", "error")
                        print(f"添加规则到SpecialRulesManager失败: {e}")
            
            edit_frame.destroy()
        
        def cancel_edit():
            edit_frame.destroy()
        
        # 绑定事件
        edit_entry.bind('<Return>', lambda e: save_edit())
        edit_entry.bind('<Escape>', lambda e: cancel_edit())
        edit_entry.bind('<FocusOut>', lambda e: save_edit())
        
        # 获取编辑位置
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
        
        # 创建右键菜单
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="编辑规则", command=lambda: self.edit_rule_inline(selection[0], 1))
        context_menu.add_command(label="删除规则", command=self.remove_special_rule)
        context_menu.add_separator()
        context_menu.add_command(label="添加新规则", command=self.add_special_rule)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def remove_special_rule(self):
        """删除特殊规则"""
        selection = self.rules_tree.selection()
        if not selection:
            self.show_message("请选择要删除的规则", "warning")
            return
        
        # 获取选中的项目
        item = selection[0]
        values = self.rules_tree.item(item, 'values')
        file_name = values[0]
        rule_text = values[1]
        
        # 从数据存储中删除
        if file_name in self.special_rules and rule_text in self.special_rules[file_name]:
            self.special_rules[file_name].remove(rule_text)
            if not self.special_rules[file_name]:  # 如果该文件没有规则了，删除文件键
                del self.special_rules[file_name]
        
        # 同时从SpecialRulesManager中删除规则
        if hasattr(self, 'special_rules_manager') and self.special_rules_manager:
            try:
                # 从文件名推断银行名称
                bank_name = self._extract_bank_name_from_filename(file_name)
                
                if bank_name:
                    # 查找并删除匹配的规则
                    rules_to_remove = []
                    for rule in self.special_rules_manager.rules:
                        if (rule.get("bank_name") == bank_name and 
                            rule.get("description") == rule_text):
                            rules_to_remove.append(rule)
                    
                    for rule in rules_to_remove:
                        self.special_rules_manager.rules.remove(rule)
                        print(f"已从SpecialRulesManager删除规则: {rule.get('id', 'unknown')}")
                    
                    if rules_to_remove:
                        # 保存更新后的规则
                        self.special_rules_manager.save_rules()
                        self.show_message(f"已从系统中删除 {len(rules_to_remove)} 个规则")
                    else:
                        self.show_message("未找到匹配的规则", "warning")
            except Exception as e:
                error_msg = str(e)
                self.show_message(f"删除规则失败: {error_msg}", "error")
                print(f"从SpecialRulesManager删除规则失败: {e}")
        
        # 从Treeview中删除
        self.rules_tree.delete(item)
        self.show_message("规则删除成功")
    
    def save_special_rules(self):
        """保存特殊规则到文件"""
        try:
            # 使用SpecialRulesManager保存规则到config/rules_config.json
            if hasattr(self, 'special_rules_manager') and self.special_rules_manager:
                success = self.special_rules_manager.save_rules()
                if success:
                    self.show_message("特殊规则已保存到 config/rules_config.json")
                else:
                    self.show_message("保存规则失败", "error")
            else:
                # 备用方案：直接保存到special_rules.json
                import json
                import os
                
                config_file = "special_rules.json"
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.special_rules, f, ensure_ascii=False, indent=2)
                
                self.show_message(f"特殊规则已保存到 {config_file}")
        except Exception as e:
            self.show_message(f"保存规则失败: {str(e)}", "error")
    
    def clear_rule_input(self):
        """清空规则输入"""
        # 由于移除了规则描述文本框，只需要清空文件名显示
        self.rule_file_label.config(text="未选择文件", foreground="gray")
    
    def _find_matching_file(self, bank_name):
        """根据银行名称查找匹配的文件路径"""
        import os
        for file_path in self.imported_files:
            file_name = os.path.basename(file_path)
            if bank_name in file_name:
                return file_path
        return None
    
    def load_special_rules(self):
        """加载特殊文件合并规则"""
        try:
            import json
            import os
            
            # 加载特殊文件合并规则配置
            rules_config_file = "config/rules_config.json"
            if os.path.exists(rules_config_file):
                with open(rules_config_file, 'r', encoding='utf-8') as f:
                    rules_config = json.load(f)
                
                # 将规则显示到Treeview中
                for rule in rules_config:
                    bank_name = rule.get('bank_name', '未知银行')
                    description = rule.get('description', '无描述')
                    
                    # 查找匹配的文件路径
                    file_path = self._find_matching_file(bank_name)
                    if file_path:
                        # 显示文件名（包含路径）
                        self.rules_tree.insert('', 'end', values=(file_path, description))
                    else:
                        # 如果没有找到匹配的文件，显示银行名称
                        self.rules_tree.insert('', 'end', values=(bank_name, description))
                
                if rules_config:
                    self.show_message(f"已加载 {len(rules_config)} 个特殊文件合并规则")
                    return
            
            # 如果规则配置不存在，则尝试加载旧的特殊规则
            config_file = "special_rules.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.special_rules = json.load(f)
                
                # 将规则显示到Treeview中
                for file_name, rules in self.special_rules.items():
                    for rule in rules:
                        # 查找匹配的文件路径
                        file_path = self._find_matching_file(file_name)
                        if file_path:
                            self.rules_tree.insert('', 'end', values=(file_path, rule))
                        else:
                            # 如果没有找到匹配的文件，显示文件名
                            self.rules_tree.insert('', 'end', values=(file_name, rule))
                
                if self.special_rules:
                    self.show_message(f"已加载 {len(self.special_rules)} 个文件的特殊规则")
        except Exception as e:
            self.show_message(f"加载规则失败: {str(e)}", "error")
    
    def refresh_rules_list(self):
        """刷新规则列表"""
        # 清空现有规则
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        
        # 重新加载规则
        self.load_special_rules()
    
    def start_merge(self):
        """开始合并"""
        if not self.imported_files:
            self.show_message("请先导入文件", "warning")
            return
        
        # 检查是否有字段映射配置
        if not self.field_mappings:
            self.show_message("请先配置字段映射", "warning")
            return
        
        # 检查是否有标准字段
        if not self.standard_fields:
            self.show_message("请先添加标准字段", "warning")
            return
        
        self.progress.start()
        self.status_label.config(text="正在合并...")
        self.show_message("开始合并文件")
        
        # 在新线程中执行合并操作
        import threading
        merge_thread = threading.Thread(target=self._perform_merge)
        merge_thread.daemon = True
        merge_thread.start()
    
    def _perform_merge(self):
        """执行合并操作"""
        try:
            import os
            from datetime import datetime
            
            # 创建输出目录
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 生成输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"合并结果_{timestamp}.xlsx")
            
            print(f"开始合并，共 {len(self.imported_files)} 个文件")
            print(f"标准字段: {self.standard_fields}")
            
            # 使用数据处理器进行合并，确保规则正确应用
            from data_processing import DataProcessor
            from header_detection import HeaderDetector
            from special_rules import SpecialRulesManager
            
            # 创建数据处理器实例
            header_detector = HeaderDetector()
            special_rules_manager = SpecialRulesManager()
            data_processor = DataProcessor(header_detector, special_rules_manager)
            
            # 使用数据处理器合并文件
            merge_result = data_processor.merge_files(self.imported_files, output_file)
            
            if merge_result:
                print(f"合并完成: {merge_result.total_records} 条记录")
                print(f"处理时间: {merge_result.processing_time:.2f}秒")
                
                # 验证合并结果
                is_valid, issues = data_processor.validate_merged_data(merge_result.merged_data)
                if not is_valid:
                    print(f"数据验证警告: {issues}")
                
                # 生成汇总报告
                summary = data_processor.generate_summary_report(merge_result)
                print(f"汇总报告: {summary}")
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.merge_completed(output_file, merge_result.total_records))
            else:
                print("合并失败")
                self.root.after(0, lambda: self.merge_failed("合并失败"))
                
        except Exception as e:
            print(f"合并操作失败: {e}")
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: self.merge_failed(f"合并过程中出错: {e}"))
    
    def merge_completed(self, output_file, record_count):
        """合并完成"""
        self.progress.stop()
        self.status_label.config(text="合并完成")
        self.show_message(f"文件合并完成！\n输出文件: {output_file}\n合并记录数: {record_count}")
    
    def _clean_nan_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清理DataFrame中的nan值，使用更强健的方法
        
        Args:
            df: 要清理的DataFrame
            
        Returns:
            清理后的DataFrame
        """
        try:
            import numpy as np
            
            # 方法1: 使用fillna("")
            df_cleaned = df.fillna("")
            
            # 方法2: 对每个列进行额外的nan值检查和处理
            for col in df_cleaned.columns:
                # 检查是否还有nan值
                if df_cleaned[col].isnull().any():
                    # 使用apply方法确保所有nan值都被替换
                    df_cleaned[col] = df_cleaned[col].apply(
                        lambda x: "" if pd.isna(x) or x is None else x
                    )
            
            # 方法3: 使用replace方法处理可能遗漏的nan值
            df_cleaned = df_cleaned.replace([np.nan, None, 'nan', 'NaN'], "")
            
            # 最终检查
            if df_cleaned.isnull().any().any():
                print("警告: 仍然存在nan值，使用强制替换")
                df_cleaned = df_cleaned.fillna("")
                # 对每个单元格进行最终检查
                for col in df_cleaned.columns:
                    df_cleaned[col] = df_cleaned[col].apply(
                        lambda x: "" if pd.isna(x) else str(x) if x != "nan" else ""
                    )
            
            return df_cleaned
            
        except Exception as e:
            print(f"清理nan值失败: {e}")
            # 如果清理失败，至少使用基本的fillna方法
            return df.fillna("")
    
    def merge_failed(self, error_message):
        """合并失败"""
        self.progress.stop()
        self.status_label.config(text="合并失败")
        self.show_message(f"合并失败: {error_message}", "error")
    
    def _get_file_mappings(self, file_path):
        """获取文件的字段映射配置"""
        try:
            # 首先尝试直接匹配完整路径
            if file_path in self.field_mappings:
                return self.field_mappings[file_path]
            
            # 尝试标准化路径匹配（处理正斜杠和反斜杠的差异）
            normalized_path = os.path.normpath(file_path)
            for config_key in self.field_mappings.keys():
                normalized_config_key = os.path.normpath(config_key)
                if normalized_config_key == normalized_path:
                    return self.field_mappings[config_key]
            
            # 尝试文件名匹配
            file_name = os.path.basename(file_path)
            for config_key in self.field_mappings.keys():
                if os.path.basename(config_key) == file_name:
                    return self.field_mappings[config_key]
            
            # 尝试路径替换匹配（处理正斜杠和反斜杠的差异）
            for config_key in self.field_mappings.keys():
                # 将配置中的反斜杠替换为正斜杠进行比较
                normalized_config_key = config_key.replace('\\', '/')
                if normalized_config_key == file_path:
                    return self.field_mappings[config_key]
            
            return {}
            
        except Exception as e:
            print(f"获取文件映射配置时出错: {e}")
            return {}

    def _apply_special_rules(self, df, file_path):
        """应用特殊规则处理数据"""
        try:
            import os
            
            # 获取文件名（不包含路径）
            file_name = os.path.basename(file_path)
            
            # 使用新的SpecialRulesManager应用规则
            if hasattr(self, 'special_rules_manager') and self.special_rules_manager:
                # 根据文件名识别银行类型
                bank_name = None
                if "北京银行" in file_name:
                    bank_name = "北京银行"
                elif "工商银行" in file_name or self._is_icbc_data(df):
                    bank_name = "工商银行"
                elif "华夏银行" in file_name:
                    bank_name = "华夏银行"
                elif "长安银行" in file_name:
                    bank_name = "长安银行"
                elif "招商银行" in file_name:
                    bank_name = "招商银行"
                elif "邮储银行" in file_name:
                    bank_name = "邮储银行"
                
                if bank_name:
                    print(f"应用 {bank_name} 的特殊规则...")
                    # 获取该银行的规则
                    bank_rules = self.special_rules_manager.get_rules(bank_name)
                    if bank_rules:
                        print(f"找到 {len(bank_rules)} 个 {bank_name} 规则")
                        # 应用该银行的所有规则
                        df = self.special_rules_manager.apply_rules(df, bank_name)
                        print(f"已应用 {bank_name} 规则")
                    else:
                        print(f"未找到 {bank_name} 的规则")
                else:
                    print("未识别到银行类型，跳过特殊规则处理")
            else:
                print("特殊规则管理器未初始化，跳过特殊规则处理")
            
            return df
            
        except Exception as e:
            print(f"应用特殊规则时出错: {e}")
            return df
    
    def _apply_beijing_bank_rules(self, df):
        """应用北京银行特殊规则"""
        try:
            # 北京银行流水.xlsx文件，从第二行获取日期范围，与月日数据合并
            if len(df) >= 2:
                # 获取第二行的日期信息
                second_row = df.iloc[1]
                # 这里可以根据实际需求处理日期范围
                pass
            
            # 过滤掉日期字段不为空但其他字段为空的记录
            if len(df) > 0:
                # 获取所有列名
                all_columns = df.columns.tolist()
                
                # 找到日期相关的列（可能包含"日期"、"时间"、"date"等关键词）
                date_columns = [col for col in all_columns if any(keyword in col.lower() for keyword in ['日期', '时间', 'date', 'time'])]
                
                if date_columns:
                    # 创建过滤条件：日期字段不为空 且 其他字段都为空
                    date_not_empty = df[date_columns].notna().any(axis=1)  # 任一日期字段不为空
                    other_columns = [col for col in all_columns if col not in date_columns]
                    
                    if other_columns:
                        other_all_empty = df[other_columns].isna().all(axis=1)  # 其他字段都为空
                        # 过滤掉日期不为空但其他字段都为空的行
                        filter_condition = ~(date_not_empty & other_all_empty)
                        df = df[filter_condition]
                        filtered_count = (~filter_condition).sum()
                        if filtered_count > 0:
                            print(f"北京银行数据已过滤掉{filtered_count}行日期不为空但其他字段为空的记录")
            
            return df
        except Exception as e:
            print(f"应用北京银行规则时出错: {e}")
            return df
    
    def _is_icbc_data(self, df):
        """根据数据内容判断是否为工商银行数据"""
        try:
            if df.empty:
                return False
            
            # 检查是否包含工商银行特有的列名
            icbc_indicators = ['借贷标志', '发生额', '对方户名', '对方账号']
            column_matches = sum(1 for col in df.columns if any(indicator in str(col) for indicator in icbc_indicators))
            
            # 如果匹配的列数大于等于2，认为是工商银行数据
            if column_matches >= 2:
                print(f"根据数据内容识别为工商银行数据，匹配列数: {column_matches}")
                return True
            
            # 检查数据内容中是否包含工商银行特有标识
            for col in df.columns:
                if df[col].dtype == 'object':  # 只检查文本列
                    sample_values = df[col].dropna().astype(str).head(10)
                    if any('工商银行' in str(val) or 'ICBC' in str(val) for val in sample_values):
                        print("根据数据内容识别为工商银行数据")
                        return True
            
            return False
        except Exception as e:
            print(f"判断工商银行数据时出错: {e}")
            return False

    def _apply_icbc_rules(self, df):
        """应用工商银行特殊规则"""
        try:
            print("应用工商银行特殊规则...")
            
            # 1. 过滤包含分页符的行（查询编号或对公往来户明细表）
            df = self._filter_icbc_page_breaks(df)
            
            # 2. 处理多个表头，只保留第一个有效表头
            df = self._filter_duplicate_headers(df)
            
            # 3. 根据借贷标志字段处理收支，直接修改标准字段
            if '借贷标志' in df.columns:
                print("发现借贷标志列，开始处理收支...")
                
                # 确保发生额列存在且为数值类型
                if '发生额' in df.columns:
                    # 转换发生额为数值类型，处理可能的字符串
                    df['发生额'] = pd.to_numeric(df['发生额'], errors='coerce').fillna(0)
                
                # 创建收入支出列，使用标准字段名
                # 借贷标志是"贷"：收入（正数）
                # 借贷标志是"借"：支出（正数）
                df['收入'] = df.apply(lambda row: abs(float(row.get('发生额', 0))) if str(row.get('借贷标志', '')).strip() == '贷' else 0, axis=1)
                df['支出'] = df.apply(lambda row: abs(float(row.get('发生额', 0))) if str(row.get('借贷标志', '')).strip() == '借' else 0, axis=1)
                
                # 统计处理结果
                income_count = (df['收入'] != 0).sum()
                expense_count = (df['支出'] != 0).sum()
                print(f"收入记录数: {income_count}, 支出记录数: {expense_count}")
                
                # 删除原始的借贷标志和发生额列，避免字段映射冲突
                if '借贷标志' in df.columns:
                    df = df.drop('借贷标志', axis=1)
                if '发生额' in df.columns:
                    df = df.drop('发生额', axis=1)
            else:
                print("未发现借贷标志列，跳过收支处理")
            
            print(f"工商银行规则应用完成，剩余数据行数: {len(df)}")
            return df
        except Exception as e:
            print(f"应用工商银行规则时出错: {e}")
            return df
    
    def _filter_icbc_page_breaks(self, df):
        """过滤工商银行分页符行（包含查询编号或对公往来户明细表的行）"""
        try:
            
            if df.empty:
                return df
            
            # 查找包含分页符的行
            page_break_rows = []
            for idx, row in df.iterrows():
                # 检查整行是否包含分页符标识
                row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                if '查询编号' in row_str or '对公往来户明细表' in row_str:
                    page_break_rows.append(idx)
                    print(f"发现分页符行 {idx}: {row_str[:50]}...")
            
            # 删除分页符行
            if page_break_rows:
                print(f"删除 {len(page_break_rows)} 个分页符行")
                df = df.drop(page_break_rows).reset_index(drop=True)
            
            return df
        except Exception as e:
            print(f"过滤工商银行分页符失败: {e}")
            return df
    
    def _filter_duplicate_headers(self, df):
        """过滤重复表头，只保留第一个有效表头"""
        try:
            
            if df.empty:
                return df
            
            # 银行表头关键词
            header_keywords = ['帐号', '账号', '入帐日期', '入账日期', '交易时间', '发生额', '余额', '借贷标志']
            
            # 查找所有可能的表头行
            header_rows = []
            for idx, row in df.iterrows():
                row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                # 检查是否包含银行表头关键词
                keyword_count = sum(1 for keyword in header_keywords if keyword in row_str)
                if keyword_count >= 3:  # 至少包含3个银行关键词
                    header_rows.append(idx)
                    print(f"发现表头行 {idx}: {row_str[:50]}...")
            
            # 如果有多个表头，删除除第一个之外的所有表头
            if len(header_rows) > 1:
                rows_to_remove = header_rows[1:]  # 保留第一个表头，删除其他
                print(f"删除 {len(rows_to_remove)} 个重复表头行")
                df = df.drop(rows_to_remove).reset_index(drop=True)
            
            # 再次检查是否还有表头行（更严格的检查）
            remaining_headers = []
            for idx, row in df.iterrows():
                row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                # 更严格的表头检查：包含多个银行关键词且看起来像表头
                keyword_count = sum(1 for keyword in header_keywords if keyword in row_str)
                if keyword_count >= 2 and any(keyword in row_str for keyword in ['帐号', '账号']):
                    remaining_headers.append(idx)
                    print(f"发现剩余表头行 {idx}: {row_str[:50]}...")
            
            # 删除所有剩余的表头行（除了第一个）
            if remaining_headers:
                rows_to_remove = remaining_headers[1:] if len(remaining_headers) > 1 else remaining_headers
                if rows_to_remove:
                    print(f"删除 {len(rows_to_remove)} 个剩余表头行")
                    df = df.drop(rows_to_remove).reset_index(drop=True)
            
            return df
        except Exception as e:
            print(f"过滤重复表头失败: {e}")
            return df

    def _apply_hua_xia_bank_rules(self, df):
        """应用华夏银行特殊规则"""
        try:
            # 华夏银行明细.xlsx文件，根据借贷标志字段处理收支
            if '借贷标志' in df.columns:
                df['收入'] = df.apply(lambda row: row.get('发生额', 0) if row.get('借贷标志') == '贷' else 0, axis=1)
                df['支出'] = df.apply(lambda row: abs(row.get('发生额', 0)) if row.get('借贷标志') == '借' else 0, axis=1)
            return df
        except Exception as e:
            print(f"应用华夏银行规则时出错: {e}")
            return df
    
    def _apply_chang_an_bank_rules(self, df):
        """应用长安银行特殊规则"""
        try:
            # 长安银行交易记录.xlsx文件，根据借/贷字段处理收支
            if '借/贷' in df.columns:
                # 查找可用的金额字段
                amount_fields = ['交易金额', '交昜金额']
                available_amount_field = None
                for field in amount_fields:
                    if field in df.columns:
                        available_amount_field = field
                        break
                
                if available_amount_field:
                    def process_income(row):
                        balance_flag = str(row.get('借/贷', '')).strip()
                        amount = float(row.get(available_amount_field, 0)) if pd.notna(row.get(available_amount_field, 0)) else 0
                        if "贷" in balance_flag:
                            return abs(amount)  # 收入为正数
                        else:
                            return 0  # 非收入为0
                    
                    def process_expense(row):
                        balance_flag = str(row.get('借/贷', '')).strip()
                        amount = float(row.get(available_amount_field, 0)) if pd.notna(row.get(available_amount_field, 0)) else 0
                        if "借" in balance_flag:
                            return abs(amount)  # 支出为正数
                        else:
                            return 0  # 非支出为0
                    
                    df['收入'] = df.apply(process_income, axis=1)
                    df['支出'] = df.apply(process_expense, axis=1)
            return df
        except Exception as e:
            print(f"应用长安银行规则时出错: {e}")
            return df
    
    def _format_date_value(self, value):
        """格式化日期值，去除时间部分"""
        try:
            if pd.isna(value) or str(value).strip() == '' or str(value).strip() == 'nan':
                return value
            
            value_str = str(value).strip()
            
            # 如果包含时间，只取日期部分
            if ' ' in value_str:
                date_part = value_str.split(' ')[0]
                # 验证日期格式
                try:
                    pd.to_datetime(date_part)
                    return date_part
                except:
                    return value_str
            else:
                return value_str
                
        except Exception:
            return value

    def _apply_cmb_rules(self, df):
        """应用招商银行特殊规则"""
        try:
            print("应用招商银行特殊规则...")
            
            # 1. 清理招商银行文件中的无用表头列
            df = self._clean_cmb_headers(df)
            
            # 2. 招商银行流水明细.xlsx文件，根据交易金额的正负号处理收支
            # 查找交易金额列（可能是"交易金额"或"交昜金额"）
            amount_col = None
            for col in df.columns:
                if ("交易" in col and "金额" in col) or ("交昜" in col and "金额" in col):
                    amount_col = col
                    break
            
            if amount_col:
                # 确保交易金额列为数值类型
                df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce').fillna(0)
                
                # 严格按照规则：根据交易金额的正负号处理收支
                # 正数为收入，负数为支出
                df['收入'] = df.apply(lambda row: row[amount_col] if row[amount_col] > 0 else 0, axis=1)
                df['支出'] = df.apply(lambda row: abs(row[amount_col]) if row[amount_col] < 0 else 0, axis=1)
                
                # 统计收入支出记录数
                income_count = (df['收入'] > 0).sum()
                expense_count = (df['支出'] > 0).sum()
                print(f"招商银行规则应用完成，收入记录数: {income_count}, 支出记录数: {expense_count}")
            else:
                print("未找到招商银行交易金额列")
            return df
        except Exception as e:
            print(f"应用招商银行规则时出错: {e}")
            return df
    
    def _clean_cmb_headers(self, df):
        """清理招商银行文件中的无用表头列"""
        try:
            # 查找并删除包含分页符、表头等无用信息的行
            # 通常这些行包含"查询编号"、"对公往来户明细表"等关键词
            if not df.empty:
                # 删除包含分页符的行
                df = df[~df.astype(str).apply(lambda x: x.str.contains('查询编号|对公往来户明细表|分页符', na=False)).any(axis=1)]
                
                # 删除完全为空的行
                df = df.dropna(how='all')
                
                # 删除列名包含无用信息的列
                useful_cols = []
                for col in df.columns:
                    col_str = str(col).strip()
                    # 保留有用的列，排除明显的表头信息
                    if not any(keyword in col_str for keyword in ['查询编号', '对公往来户明细表', '分页符', '表头']):
                        useful_cols.append(col)
                
                if useful_cols:
                    df = df[useful_cols]
                
                print(f"招商银行表头清理完成，保留列数: {len(df.columns)}")
            
            return df
        except Exception as e:
            print(f"清理招商银行表头时出错: {e}")
            return df
    
    def show_message(self, message, msg_type="info"):
        """显示消息"""
        if msg_type == "info":
            messagebox.showinfo("信息", message)
        elif msg_type == "warning":
            messagebox.showwarning("警告", message)
        elif msg_type == "error":
            messagebox.showerror("错误", message)
    
    
    def on_mapping_select(self, event):
        """字段映射选择事件"""
        selection = self.mapping_treeview.selection()
        if selection:
            item = selection[0]
            values = self.mapping_treeview.item(item, 'values')
            standard_field, imported_column, is_mapped = values
            
            # 只更新标准字段输入框，不触发界面重新布局
            try:
                # 使用StringVar来更新，避免直接操作Entry导致界面变化
                if hasattr(self, 'standard_field_var'):
                    # 临时禁用事件处理，避免触发界面变化
                    self.standard_field_var.set(standard_field)
            except Exception:
                # 如果更新失败，静默处理，不影响界面
                pass
    
    def on_mapping_double_click(self, event):
        """字段映射双击编辑事件"""
        selection = self.mapping_treeview.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.mapping_treeview.item(item, 'values')
        standard_field, imported_column, is_mapped = values
        
        # 直接在当前界面编辑，不弹出对话框
        self.edit_mapping_inline(item, standard_field, imported_column, is_mapped)
    
    def create_mapping_edit_dialog(self, item, standard_field, imported_column, is_mapped):
        """创建字段映射编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑字段映射")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标准字段
        ttk.Label(main_frame, text="标准字段:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        standard_field_var = tk.StringVar(value=standard_field)
        standard_field_entry = ttk.Entry(main_frame, textvariable=standard_field_var, width=30)
        standard_field_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 导入文件列名
        ttk.Label(main_frame, text="导入文件列名:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        imported_column_var = tk.StringVar(value=imported_column)
        imported_column_entry = ttk.Entry(main_frame, textvariable=imported_column_var, width=30)
        imported_column_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 是否映射
        ttk.Label(main_frame, text="是否映射:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        is_mapped_var = tk.StringVar(value="是" if is_mapped == "是" else "否")
        is_mapped_combo = ttk.Combobox(main_frame, textvariable=is_mapped_var, 
                                      values=["是", "否"], state="readonly", width=27)
        is_mapped_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        def save_mapping():
            new_standard = standard_field_var.get().strip()
            new_imported = imported_column_var.get().strip()
            new_mapped = is_mapped_var.get()
            
            if not new_standard and not new_imported:
                self.show_message("标准字段和导入文件列名不能同时为空", "warning")
                return
            
            # 更新Treeview
            self.mapping_treeview.item(item, values=(new_standard, new_imported, new_mapped))
            
            # 保存到字段映射数据
            current_file = self.get_current_selected_file()
            if current_file:
                if current_file not in self.field_mappings:
                    self.field_mappings[current_file] = []
                
                # 查找并更新现有映射
                updated = False
                for mapping in self.field_mappings[current_file]:
                    if (mapping['standard_field'] == standard_field and 
                        mapping['imported_column'] == imported_column):
                        mapping['standard_field'] = new_standard
                        mapping['imported_column'] = new_imported
                        mapping['is_mapped'] = new_mapped == "是"
                        updated = True
                        break
                
                # 如果没有找到现有映射，添加新映射
                if not updated and new_standard and new_imported:
                    self.field_mappings[current_file].append({
                        'standard_field': new_standard,
                        'imported_column': new_imported,
                        'is_mapped': new_mapped == "是"
                    })
            
            dialog.destroy()
            self.show_message("字段映射已更新")
        
        ttk.Button(button_frame, text="保存", command=save_mapping).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT)
    
    
    
    # 标准字段管理方法
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
        self.show_message(f"标准字段 '{field_name}' 添加成功")
    
    def remove_standard_field(self):
        """删除标准字段"""
        # 通过输入框获取要删除的字段名
        field_name = self.standard_field_var.get().strip()
        if not field_name:
            self.show_message("请输入要删除的标准字段名称", "warning")
            return
        
        if field_name not in self.standard_fields:
            self.show_message("标准字段不存在", "warning")
            return
        
        if messagebox.askyesno("确认", f"确定要删除标准字段 '{field_name}' 吗？"):
            self.standard_fields.remove(field_name)
            self.update_standard_fields_list()
            self.standard_field_var.set("")
            self.show_message(f"标准字段 '{field_name}' 删除成功")
    
    def edit_standard_field(self):
        """修改标准字段"""
        # 通过输入框获取要修改的字段名
        old_field_name = self.standard_field_var.get().strip()
        if not old_field_name:
            self.show_message("请输入要修改的标准字段名称", "warning")
            return
        
        if old_field_name not in self.standard_fields:
            self.show_message("标准字段不存在", "warning")
            return
        
        # 弹出对话框获取新字段名
        new_field_name = tk.simpledialog.askstring("修改标准字段", 
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
        self.show_message(f"标准字段修改成功: '{old_field_name}' -> '{new_field_name}'")
    
    
    def update_standard_fields_list(self):
        """更新标准字段列表显示"""
        # 更新映射列表中的标准字段
        self.update_mapping_list()
    
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
                # 交换位置
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
                # 交换位置
                next_item = siblings[index + 1]
                self.mapping_treeview.move(item, parent, index + 1)
    
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
            
            # 获取该文件的列名作为下拉选项（使用缓存）
            file_columns = self.get_file_columns(current_file)
            # 过滤掉空值和NaN值
            file_columns = [col for col in file_columns if col and str(col).strip() and str(col) != 'nan']
            # 添加"未映射"选项，不添加空选项
            dropdown_options = ['未映射'] + file_columns
            self.mapping_treeview.set_dropdown_values(dropdown_options)
            
            # 首先尝试从配置文件加载已保存的映射配置
            try:
                # 提取文件名（不包含路径）
                file_name = os.path.basename(current_file)
                # 使用资源管理器加载配置文件
                from resource_manager import ResourceManager
                resource_manager = ResourceManager()
                config_data = resource_manager.load_json_config("config/field_mapping_config.json")
                
                # 尝试多种匹配方式
                saved_mappings = None
                
                # 1. 尝试完整路径匹配
                if current_file in config_data:
                    saved_mappings = config_data[current_file]
                    print(f"找到完整路径匹配的映射配置: {current_file}")
                
                # 2. 尝试标准化路径匹配（处理路径分隔符差异）
                if not saved_mappings:
                    normalized_current = os.path.normpath(current_file)
                    for config_key in config_data.keys():
                        normalized_config = os.path.normpath(config_key)
                        if normalized_config == normalized_current:
                            saved_mappings = config_data[config_key]
                            print(f"找到标准化路径匹配的映射配置: {config_key}")
                            break
                
                # 3. 尝试文件名匹配
                if not saved_mappings:
                    for config_key in config_data.keys():
                        if os.path.basename(config_key) == file_name:
                            saved_mappings = config_data[config_key]
                            print(f"找到文件名匹配的映射配置: {config_key}")
                            break
                
                # 4. 尝试模糊匹配（包含文件名）
                if not saved_mappings:
                    for config_key in config_data.keys():
                        if file_name in config_key or config_key.endswith(file_name):
                            saved_mappings = config_data[config_key]
                            print(f"找到模糊匹配的映射配置: {config_key}")
                            break
                
                if saved_mappings:
                    print(f"找到已保存的映射配置: {len(saved_mappings)} 个映射")
                    # 将保存的映射配置转换为内部格式
                    for mapping in saved_mappings:
                        standard_field = mapping.get('standard_field', '')
                        imported_column = mapping.get('imported_column', '')
                        is_mapped = mapping.get('is_mapped', False)
                        
                        # 处理字段名不一致的问题：交易日期 -> 交易时间
                        if standard_field == '交易日期':
                            standard_field = '交易时间'
                        
                        if standard_field:
                            if current_file not in self.field_mappings:
                                self.field_mappings[current_file] = {}
                            self.field_mappings[current_file][standard_field] = {
                                'imported_column': imported_column,
                                'is_mapped': is_mapped
                            }
                            print(f"加载映射: {standard_field} -> {imported_column} (映射: {is_mapped})")
                else:
                    print(f"文件 {file_name} 没有已保存的映射配置")
            except Exception as e:
                print(f"加载映射配置时出错: {e}")
                import traceback
                traceback.print_exc()
            
            # 获取该文件的映射配置
            file_mappings = self.field_mappings.get(current_file, {})
            
            # 为每个标准字段创建映射项
            for standard_field in self.standard_fields:
                mapping_info = file_mappings.get(standard_field, {})
                imported_column = mapping_info.get('imported_column', '')
                is_mapped = mapping_info.get('is_mapped', False)
                
                # 如果没有映射，显示"未映射"
                display_column = imported_column if imported_column else "未映射"
                
                # 插入到映射列表
                item_id = self.mapping_treeview.insert('', 'end', values=(
                    standard_field, 
                    display_column, 
                    "是" if is_mapped else "否"
                ))
                
                # 内联下拉框由TreeviewWithDropdown类自动处理
        finally:
            self.is_updating_mapping = False
    
    def on_mapping_value_change(self, item, new_value):
        """处理映射值改变事件"""
        current_file = self.get_current_selected_file()
        if not current_file:
            return
            
        # 获取标准字段名
        current_values = self.mapping_treeview.item(item, 'values')
        standard_field = current_values[0]
        
        # 更新映射配置
        if current_file not in self.field_mappings:
            self.field_mappings[current_file] = {}
        
        # 如果选择"未映射"或空值，则设置为未映射
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
    
    def get_current_selected_file(self):
        """获取当前选中的文件"""
        # 从文件树视图获取当前选中的文件
        selection = self.file_treeview.selection()
        if selection:
            item = selection[0]
            values = self.file_treeview.item(item, 'values')
            if values:
                file_name = values[0]
                file_path = values[1]
                # 组合完整路径并标准化
                full_path = os.path.join(file_path, file_name)
                # 标准化路径，确保路径分隔符一致
                normalized_path = os.path.normpath(full_path)
                return normalized_path
        return None
    
    # 字段映射管理方法
    def edit_mapping_inline(self, item, standard_field, imported_column, is_mapped):
        """在当前界面内编辑字段映射"""
        # 获取当前选中文件的列名
        current_file = self.get_current_selected_file()
        if not current_file:
            self.show_message("请先选择文件", "warning")
            return
        
        # 获取文件列名
        file_columns = self.get_file_columns(current_file)
        if not file_columns:
            self.show_message("无法获取文件列名", "error")
            return
        
        # 创建编辑框架（在映射列表下方）
        if hasattr(self, 'edit_frame'):
            self.edit_frame.destroy()
        
        self.edit_frame = ttk.Frame(self.mapping_treeview.master)
        self.edit_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        self.edit_frame.columnconfigure(1, weight=1)
        
        # 标准字段选择
        ttk.Label(self.edit_frame, text="标准字段:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.edit_standard_combo = ttk.Combobox(self.edit_frame, values=self.standard_fields, width=15)
        self.edit_standard_combo.set(standard_field)
        self.edit_standard_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 导入文件列名选择
        ttk.Label(self.edit_frame, text="导入文件列名:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.edit_imported_combo = ttk.Combobox(self.edit_frame, values=file_columns, width=15)
        self.edit_imported_combo.set(imported_column)
        self.edit_imported_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 是否映射选择
        ttk.Label(self.edit_frame, text="是否映射:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.edit_mapped_combo = ttk.Combobox(self.edit_frame, values=["是", "否"], state="readonly", width=8)
        self.edit_mapped_combo.set(is_mapped)
        self.edit_mapped_combo.grid(row=0, column=5, padx=(0, 10))
        
        # 保存和取消按钮
        ttk.Button(self.edit_frame, text="保存", command=lambda: self.save_mapping_edit(item)).grid(row=0, column=6, padx=(0, 5))
        ttk.Button(self.edit_frame, text="取消", command=self.cancel_mapping_edit).grid(row=0, column=7)
    
    def save_mapping_edit(self, item):
        """保存映射编辑"""
        standard_field = self.edit_standard_combo.get()
        imported_column = self.edit_imported_combo.get()
        is_mapped = self.edit_mapped_combo.get()
        
        if not standard_field and not imported_column:
            self.show_message("标准字段和导入文件列名不能同时为空", "warning")
            return
        
        # 通过标准字段名查找要更新的项目
        target_item = None
        for child in self.mapping_treeview.get_children():
            values = self.mapping_treeview.item(child, 'values')
            if len(values) > 0 and values[0] == standard_field:
                target_item = child
                break
        
        if target_item:
            # 更新Treeview
            self.mapping_treeview.item(target_item, values=(standard_field, imported_column, is_mapped))
        else:
            # 如果没有找到现有项目，添加新项目
            self.mapping_treeview.insert('', 'end', values=(standard_field, imported_column, is_mapped))
        
        # 保存到字段映射数据
        current_file = self.get_current_selected_file()
        if current_file:
            if current_file not in self.field_mappings:
                self.field_mappings[current_file] = {}
            
            # 更新映射配置
            if imported_column == "未映射" or not imported_column or imported_column.strip() == "":
                self.field_mappings[current_file][standard_field] = {
                    'imported_column': '',
                    'is_mapped': False
                }
            else:
                self.field_mappings[current_file][standard_field] = {
                    'imported_column': imported_column,
                    'is_mapped': True
                }
        
        self.cancel_mapping_edit()
        self.show_message("字段映射已更新")
    
    def cancel_mapping_edit(self):
        """取消映射编辑"""
        if hasattr(self, 'edit_frame'):
            self.edit_frame.destroy()
    
    def get_file_columns(self, file_path):
        """获取文件的列名 - 使用智能表头识别，带缓存机制"""
        try:
            # 检查缓存
            if file_path in self.file_columns_cache:
                return self.file_columns_cache[file_path]
            
            from header_detection import HeaderDetector
            
            # 创建表头识别器
            detector = HeaderDetector()
            
            # 检测表头
            headers = detector.detect_headers(file_path)
            if headers:
                # 返回第一个检测到的表头的列名
                columns = headers[0].columns
            else:
                # 如果检测失败，使用传统方法
                df = pd.read_excel(file_path)
                columns = df.columns.tolist()
            
            # 缓存结果
            self.file_columns_cache[file_path] = columns
            return columns
            
        except Exception as e:
            self.show_message(f"获取文件列名失败: {str(e)}", "error")
        return []
    
    def _read_file_with_header_detection(self, file_path):
        """使用DataProcessor处理文件"""
        try:
            # 使用DataProcessor处理数据
            if hasattr(self, 'controller') and hasattr(self.controller, 'data_processor'):
                # 从文件名推断银行名称
                file_name = os.path.basename(file_path)
                bank_name = self._extract_bank_name(file_name)
                
                # 使用DataProcessor处理数据
                result = self.controller.data_processor.process_file(file_path)
                
                if result and hasattr(result, 'data') and result.data is not None:
                    return result.data
                else:
                    print(f"DataProcessor处理失败: {file_path}")
                    return None
            else:
                # 如果没有DataProcessor，创建临时的DataProcessor
                print(f"没有controller，创建临时DataProcessor: {file_path}")
                return self._read_file_with_temporary_processor(file_path)
            
        except Exception as e:
            print(f"使用DataProcessor读取文件失败: {file_path}, 错误: {e}")
            # 如果DataProcessor失败，回退到传统方法
            try:
                return self._read_file_traditional(file_path)
            except Exception as e2:
                print(f"传统方法读取文件也失败: {file_path}, 错误: {e2}")
                return None
    
    def _read_file_with_temporary_processor(self, file_path):
        """使用临时DataProcessor处理文件"""
        try:
            # 导入必要的模块
            from header_detection import HeaderDetector
            from special_rules import SpecialRulesManager
            from data_processing import DataProcessor
            
            # 创建临时的DataProcessor
            header_detector = HeaderDetector()
            special_rules_manager = SpecialRulesManager()
            data_processor = DataProcessor(header_detector, special_rules_manager)
            
            # 从文件名推断银行名称
            file_name = os.path.basename(file_path)
            bank_name = self._extract_bank_name(file_name)
            
            # 使用DataProcessor处理数据
            result = data_processor.process_file(file_path)
            
            if result and hasattr(result, 'data') and result.data is not None:
                return result.data
            else:
                print(f"临时DataProcessor处理失败: {file_path}")
                return None
                
        except Exception as e:
            print(f"临时DataProcessor处理失败: {file_path}, 错误: {e}")
            return None
    
    def _extract_bank_name(self, file_name):
        """从文件名提取银行名称"""
        # 移除文件扩展名
        name = os.path.splitext(file_name)[0]
        
        # 常见的银行名称关键词
        bank_keywords = [
            '浦发银行', '兴业银行', '长安银行', '中国银行', '工商银行', 
            '建设银行', '农业银行', '招商银行', '北京银行', '华夏银行',
            '邮储银行', '光大银行', '民生银行', '中信银行', '交通银行'
        ]
        
        for keyword in bank_keywords:
            if keyword in name:
                return keyword
        
        return name
    
    def _extract_bank_name_from_filename(self, file_name):
        """从文件名提取银行名称（用于规则管理）"""
        # 移除文件扩展名
        name = os.path.splitext(file_name)[0]
        
        # 常见的银行名称关键词
        bank_keywords = [
            '北京银行', '工商银行', '华夏银行', '招商银行', '长安银行',
            '建设银行', '农业银行', '中国银行', '浦发银行', '兴业银行',
            '邮储银行', '光大银行', '民生银行', '中信银行', '交通银行'
        ]
        
        for keyword in bank_keywords:
            if keyword in name:
                return keyword
        
        # 如果无法识别，返回None
        return None
    
    def _ask_user_to_select_bank(self):
        """让用户手动选择银行名称"""
        try:
            from tkinter import simpledialog
            
            # 银行选项
            bank_options = [
                "北京银行", "工商银行", "华夏银行", "招商银行", "长安银行",
                "建设银行", "农业银行", "中国银行", "浦发银行", "兴业银行",
                "邮储银行", "光大银行", "民生银行", "中信银行", "交通银行"
            ]
            
            # 创建选择对话框
            bank_name = simpledialog.askstring(
                "选择银行",
                "无法自动识别银行类型，请手动选择：",
                initialvalue="工商银行"
            )
            
            if bank_name and bank_name in bank_options:
                return bank_name
            else:
                return None
                
        except Exception as e:
            print(f"用户选择银行失败: {e}")
            return None
    
    def _read_file_traditional(self, file_path):
        """传统方法读取文件"""
        try:
            
            # 读取原始数据
            df = pd.read_excel(file_path, header=None)
            
            if df.empty:
                return None
            
            # 过滤分页符行
            df = self._filter_page_breaks(df)
            
            # 使用修复后的表头检测逻辑
            header_row = self._find_header_row_fixed(df)
            
            if header_row is not None:
                # 重新设置表头
                if header_row < len(df):
                    df.columns = df.iloc[header_row]
                    df = df.iloc[header_row + 1:].reset_index(drop=True)
            else:
                # 如果检测失败，使用传统方法
                print(f"无法检测到表头，使用传统方法: {file_path}")
                return pd.read_excel(file_path)
            
            # 清理数据
            df = self._clean_data(df)
            
            return df
            
        except Exception as e:
            print(f"传统方法读取文件失败: {file_path}, 错误: {e}")
            return None
    
    def _filter_page_breaks(self, df):
        """过滤分页符行"""
        try:
            
            # 查找包含分页符的行
            page_break_rows = []
            for idx, row in df.iterrows():
                # 检查是否包含分页符标识
                row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                if '分页符' in row_str or '第' in row_str and '页' in row_str:
                    page_break_rows.append(idx)
            
            # 删除分页符行
            if page_break_rows:
                df = df.drop(page_break_rows).reset_index(drop=True)
            
            return df
        except Exception as e:
            print(f"过滤分页符失败: {e}")
            return df
    
    def _clean_data(self, df):
        """清理数据"""
        try:
            # 删除完全为空的行
            df = df.dropna(how='all')
            
            # 删除完全为空的列
            df = df.dropna(axis=1, how='all')
            
            # 重置索引
            df = df.reset_index(drop=True)
            
            return df
        except Exception as e:
            print(f"清理数据失败: {e}")
            return df
    
    def _find_header_row_fixed(self, df):
        """修复后的表头检测逻辑"""
        
        # 银行常见字段关键词
        bank_keywords = ['账号', '账户名称', '交易时间', '交易金额', '余额', '对方账号', '对方户名', '摘要', '业务类型', '序号', '过账日期', '借方发生额', '贷方发生额', '币种', '凭证号', '入帐', '入账', '日期', '时间', '代码', '柜员', '附言', '用途', '摘要']
        
        best_row = None
        best_score = 0
        
        # 检查前15行
        for i in range(min(15, len(df))):
            row = df.iloc[i]
            row_text = " ".join(str(cell) for cell in row if pd.notna(cell))
            
            # 跳过分页符行和标题行
            if self._is_page_break_row(row_text) or self._is_title_row(row_text):
                continue
            
            # 计算关键词匹配分数
            keyword_count = 0
            for keyword in bank_keywords:
                if keyword in row_text:
                    keyword_count += 1
            
            # 如果包含多个关键词，认为是有效表头
            if keyword_count >= 2:
                if keyword_count > best_score:
                    best_score = keyword_count
                    best_row = i
        
        return best_row
    
    def _is_page_break_row(self, row_text):
        """检查是否是分页符行"""
        return '分页符' in row_text or ('第' in row_text and '页' in row_text)
    
    def _is_title_row(self, row_text):
        """检查是否是标题行"""
        title_indicators = ['明细表', '流水', '账单', '对账单', '交易明细', '账户明细']
        return any(indicator in row_text for indicator in title_indicators)
    
    

    # 已移除重复的排序功能方法，避免与标准字段管理功能重复


    # 已移除不再使用的_update_field_mappings_data方法

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
            
            # 直接保存到配置文件
            try:
                import json
                import os
                import sys
                
                # 使用标准化路径作为配置键，避免重复配置
                file_key = os.path.normpath(current_file)
                
                # 确定配置目录位置（优先使用exe同目录）
                if getattr(sys, 'frozen', False):
                    # 打包环境：保存到exe同目录
                    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
                    config_dir = os.path.join(exe_dir, "config")
                else:
                    # 开发环境：保存到当前目录
                    config_dir = "config"
                
                # 确保配置目录存在
                if not os.path.exists(config_dir):
                    os.makedirs(config_dir)
                
                # 加载现有配置
                config_file = os.path.join(config_dir, "field_mapping_config.json")
                config_data = {}
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                
                # 清理重复配置：移除相同文件的不同路径形式
                config_data = self._clean_duplicate_configs(config_data, file_key)
                
                # 更新配置
                config_data[file_key] = mappings
                
                # 保存配置
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                
                self.show_message(f"字段映射配置已保存: {os.path.basename(current_file)}")
                print(f"配置保存到: {config_file}")
                
            except Exception as e:
                self.show_message(f"保存字段映射配置失败: {str(e)}", "error")
                
        except Exception as e:
            self.show_message(f"保存字段映射配置失败: {str(e)}", "error")
    
    def _clean_duplicate_configs(self, config_data: dict, current_file_key: str) -> dict:
        """清理重复的字段映射配置"""
        if not config_data:
            return config_data
        
        # 获取当前文件的文件名（用于匹配）
        current_file_name = os.path.basename(current_file_key)
        current_normalized = os.path.normpath(current_file_key)
        
        # 需要删除的键
        keys_to_remove = []
        
        for config_key in list(config_data.keys()):
            # 跳过当前要保存的键
            if config_key == current_file_key:
                continue
                
            config_normalized = os.path.normpath(config_key)
            config_file_name = os.path.basename(config_key)
            
            # 检查是否为同一个文件的不同路径形式
            # 优先保留完整路径的配置，删除短路径的配置
            if config_file_name == current_file_name:
                # 如果当前键是完整路径，删除短路径的配置
                if len(current_file_key) > len(config_key):
                    keys_to_remove.append(config_key)
                # 如果当前键是短路径，删除完整路径的配置
                elif len(current_file_key) < len(config_key):
                    keys_to_remove.append(config_key)
                # 如果长度相同但路径不同，保留当前键，删除其他
                elif config_normalized != current_normalized:
                    keys_to_remove.append(config_key)
        
        # 删除重复的配置
        for key in keys_to_remove:
            del config_data[key]
        
        return config_data
    
    def reset_to_default_rules(self):
        """恢复默认规则"""
        try:
            import json
            import os
            import shutil
            
            # 确认对话框
            from tkinter import messagebox
            result = messagebox.askyesno("确认操作", 
                                       "确定要恢复默认规则吗？\n这将覆盖当前的所有规则。")
            if not result:
                return
            
            # 备份当前规则
            current_config = "config/rules_config.json"
            backup_config = "config/rules_config_backup.json"
            if os.path.exists(current_config):
                shutil.copy2(current_config, backup_config)
                self.show_message("已备份当前规则到 rules_config_backup.json")
            
            # 复制默认规则到当前规则配置
            default_config = "config/default_rules_config.json"
            if os.path.exists(default_config):
                shutil.copy2(default_config, current_config)
                
                # 重新加载规则
                self.rules_tree.delete(*self.rules_tree.get_children())  # 清空当前显示
                self.load_special_rules()  # 重新加载
                
                self.show_message("已恢复默认规则", "success")
            else:
                self.show_message("默认规则配置文件不存在", "error")
                
        except Exception as e:
            self.show_message(f"恢复默认规则失败: {str(e)}", "error")
    
    def _apply_field_mapping_to_dataframe(self, df: pd.DataFrame, file_mappings: Dict[str, Any]) -> pd.DataFrame:
        """将字段映射应用到DataFrame，创建标准化的列名"""
        try:
            if not file_mappings:
                return df
            
            # 创建新的DataFrame，包含标准化的列名
            mapped_df = pd.DataFrame()
            
            for standard_field, mapping in file_mappings.items():
                imported_column = mapping.get('imported_column', '')
                is_mapped = mapping.get('is_mapped', False)
                
                if is_mapped and imported_column and imported_column != '未映射':
                    # 如果映射了列，使用映射的列
                    if imported_column in df.columns:
                        mapped_df[standard_field] = df[imported_column]
                    else:
                        mapped_df[standard_field] = ""
                else:
                    # 如果没有映射，尝试自动匹配列名
                    matched_column = None
                    for col in df.columns:
                        if col and str(col).strip():
                            col_str = str(col).lower()
                            field_str = standard_field.lower()
                            
                            # 直接匹配
                            if field_str in col_str or col_str in field_str:
                                matched_column = col
                                break
                            
                            # 关键词匹配
                            if '日期' in standard_field and any(kw in col_str for kw in ['日期', 'date', '时间', '入帐日期']):
                                matched_column = col
                                break
                            elif '时间' in standard_field and any(kw in col_str for kw in ['时间', 'time', '入帐时间']):
                                matched_column = col
                                break
                            elif '金额' in standard_field and any(kw in col_str for kw in ['金额', 'amount', 'money', '交易金额', '发生额']):
                                matched_column = col
                                break
                            elif '收入' in standard_field and any(kw in col_str for kw in ['收入', 'income', 'in']):
                                matched_column = col
                                break
                            elif '支出' in standard_field and any(kw in col_str for kw in ['支出', 'expense', 'out']):
                                matched_column = col
                                break
                            elif '余额' in standard_field and any(kw in col_str for kw in ['余额', 'balance', '结余', '账户余额']):
                                matched_column = col
                                break
                            elif '对手' in standard_field and any(kw in col_str for kw in ['对手', 'counterpart', '对方', '对方户名', '对方行名']):
                                matched_column = col
                                break
                            elif '摘要' in standard_field and any(kw in col_str for kw in ['摘要', 'summary', '备注', 'remark', '用途', '附言']):
                                matched_column = col
                                break
                    
                    if matched_column:
                        mapped_df[standard_field] = df[matched_column]
                    else:
                        mapped_df[standard_field] = ""
            
            # 保留原始列名，以便特殊规则能够找到正确的字段
            for col in df.columns:
                if col not in mapped_df.columns:
                    mapped_df[col] = df[col]
            
            print(f"字段映射完成，新DataFrame形状: {mapped_df.shape}")
            print(f"新DataFrame列名: {list(mapped_df.columns)}")
            
            return mapped_df
            
        except Exception as e:
            print(f"字段映射失败: {e}")
            import traceback
            traceback.print_exc()
            return df

    def clear_all_rules(self):
        """清空所有规则"""
        try:
            from tkinter import messagebox
            result = messagebox.askyesno("确认操作", 
                                       "确定要清空所有规则吗？\n此操作不可撤销。")
            if not result:
                return
            
            # 清空规则配置文件
            rules_config_file = "config/rules_config.json"
            if os.path.exists(rules_config_file):
                with open(rules_config_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            
            # 清空显示
            self.rules_tree.delete(*self.rules_tree.get_children())
            self.special_rules = {}
            
            self.show_message("已清空所有规则", "success")
            
        except Exception as e:
            self.show_message(f"清空规则失败: {str(e)}", "error")

    def run(self):
        """运行界面"""
        self.root.mainloop()


if __name__ == "__main__":
    # 测试界面
    app = ExcelMergeUI()
    app.run()
