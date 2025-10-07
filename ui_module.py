"""
Excel文档合并工具 - 用户界面模块
负责创建和管理用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.ttk import Combobox
from typing import List, Dict, Any
import os


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
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
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
        
        
        
        # 创建界面
        self.create_main_window()
    
        
    def create_main_window(self):
        """创建主窗口"""
        # 设置窗口样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
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
        import_frame = ttk.LabelFrame(parent, text="文件导入管理", padding="10")
        import_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        import_frame.columnconfigure(0, weight=1)
        import_frame.rowconfigure(2, weight=1)
        
        # 导入按钮
        ttk.Button(import_frame, text="选择Excel文件", 
                  command=self.import_files).grid(row=0, column=0, pady=(0, 10))
        
        # 已导入文件列表
        ttk.Label(import_frame, text="已导入文件:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # 文件列表框架
        list_frame = ttk.Frame(import_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 使用Treeview替代Listbox，显示文件名、路径、记录数
        columns = ('文件名', '路径', '记录数')
        self.file_treeview = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # 设置列标题和宽度
        self.file_treeview.heading('文件名', text='文件名')
        self.file_treeview.heading('路径', text='路径')
        self.file_treeview.heading('记录数', text='记录数')
        
        self.file_treeview.column('文件名', width=150, minwidth=100)
        self.file_treeview.column('路径', width=300, minwidth=200)
        self.file_treeview.column('记录数', width=80, minwidth=60)
        
        # 使用固定高度，避免界面大小变化
        self.file_treeview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.file_treeview.configure(height=12)  # 明确设置固定高度
        
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
        button_frame.grid(row=3, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="删除选中", 
                  command=self.remove_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="重新导入", 
                  command=self.reimport_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空列表", 
                  command=self.clear_file_list).pack(side=tk.LEFT)
        
    def create_field_mapping_section(self, parent):
        """创建字段映射配置区域"""
        # 字段映射框架
        mapping_frame = ttk.LabelFrame(parent, text="字段映射配置", padding="10")
        mapping_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        mapping_frame.columnconfigure(0, weight=1)
        mapping_frame.rowconfigure(2, weight=1)
        
        # 当前文件显示区域
        current_file_frame = ttk.Frame(mapping_frame)
        current_file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(current_file_frame, text="当前文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.current_file_label = ttk.Label(current_file_frame, text="未选择文件", foreground="gray")
        self.current_file_label.grid(row=0, column=1, sticky=tk.W)
        
        # 字段映射列表区域（合并了标准字段管理和映射配置）
        mapping_list_frame = ttk.LabelFrame(mapping_frame, text="字段映射列表", padding="5")
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
        self.mapping_treeview = TreeviewWithDropdown(list_container_frame, columns=mapping_columns, show='headings', height=12, dropdown_column_index=1)
        
        # 设置列标题和宽度
        self.mapping_treeview.heading('标准字段', text='标准字段')
        self.mapping_treeview.heading('导入文件列名', text='导入文件列名')
        self.mapping_treeview.heading('是否映射', text='是否映射')
        
        self.mapping_treeview.column('标准字段', width=120, minwidth=100)
        self.mapping_treeview.column('导入文件列名', width=150, minwidth=120)
        self.mapping_treeview.column('是否映射', width=80, minwidth=60)
        
        # 使用固定高度，避免界面大小变化
        self.mapping_treeview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.mapping_treeview.configure(height=12)  # 明确设置固定高度
        
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
        field_management_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
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
        move_buttons_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(move_buttons_frame, text="上移", command=self.move_mapping_up, width=8).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(move_buttons_frame, text="下移", command=self.move_mapping_down, width=8).pack(side=tk.LEFT, padx=(0, 2))
        
        # 保存映射配置按钮
        save_buttons_frame = ttk.Frame(field_management_frame)
        save_buttons_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
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
        rules_frame = ttk.LabelFrame(parent, text="特殊规则配置", padding="10")
        rules_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        rules_frame.columnconfigure(1, weight=1)
        
        # 规则输入
        ttk.Label(rules_frame, text="选择文件:").grid(row=0, column=0, sticky=tk.W)
        
        self.rule_file_combo = ttk.Combobox(rules_frame, state="readonly")
        self.rule_file_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Label(rules_frame, text="规则描述:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        # 规则输入文本框
        self.rule_text = tk.Text(rules_frame, height=4, wrap=tk.WORD)
        self.rule_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 规则操作按钮
        rule_button_frame = ttk.Frame(rules_frame)
        rule_button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(rule_button_frame, text="添加规则", 
                  command=self.add_special_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rule_button_frame, text="删除规则", 
                  command=self.remove_special_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rule_button_frame, text="保存规则", 
                  command=self.save_special_rules).pack(side=tk.LEFT)
        
        # 规则列表
        ttk.Label(rules_frame, text="已配置规则:").grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        
        self.rules_listbox = tk.Listbox(rules_frame, height=4)
        self.rules_listbox.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 防止Listbox自动调整大小
        self.rules_listbox.grid_propagate(False)
        
    def create_merge_section(self, parent):
        """创建合并操作区域"""
        # 合并操作框架
        merge_frame = ttk.LabelFrame(parent, text="合并操作", padding="10")
        merge_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 合并按钮
        ttk.Button(merge_frame, text="开始合并", 
                  command=self.start_merge, 
                  style="Accent.TButton").pack(pady=10)
        
        # 进度条
        self.progress = ttk.Progressbar(merge_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
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
                        import pandas as pd
                        record_count = len(pd.read_excel(file_path))
                    except:
                        record_count = "未知"
                    
                    # 添加到导入列表
                    self.imported_files.append(file_path)
                    
                    # 显示文件名、路径和记录数
                    file_name = os.path.basename(file_path)
                    file_dir = os.path.dirname(file_path)
                    self.file_treeview.insert('', 'end', values=(file_name, file_dir, f"{record_count}条"))
                    
                    # 更新下拉框
                    self.rule_file_combo['values'] = list(self.rule_file_combo['values']) + [file_name]
                    
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
                import pandas as pd
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
                self.rule_file_combo['values'] = []
                # 清空字段映射数据
                self.field_mappings.clear()
                # 清空字段映射列表
                for item in self.mapping_treeview.get_children():
                    self.mapping_treeview.delete(item)
                self.show_message("文件列表已清空")
    
    def update_file_combos(self):
        """更新文件下拉框"""
        file_names = [os.path.basename(f) for f in self.imported_files]
        self.rule_file_combo['values'] = file_names
    
    
    
    
    
    
    
    
    
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
            
            # 更新规则文件下拉框选择
            self.rule_file_combo.set(file_name)
            
            # 更新字段映射列表
            self.update_mapping_list()
    
    
    
    
    
    
    
    
    def add_special_rule(self):
        """添加特殊规则"""
        file_name = self.rule_file_combo.get()
        rule_text = self.rule_text.get("1.0", tk.END).strip()
        
        if not file_name or not rule_text:
            self.show_message("请选择文件并输入规则描述", "warning")
            return
        
        if file_name not in self.special_rules:
            self.special_rules[file_name] = []
        
        self.special_rules[file_name].append(rule_text)
        self.rules_listbox.insert(tk.END, f"{file_name}: {rule_text[:30]}...")
        self.rule_text.delete("1.0", tk.END)
        self.show_message("规则添加成功")
    
    def remove_special_rule(self):
        """删除特殊规则"""
        selection = self.rules_listbox.curselection()
        if selection:
            index = selection[0]
            self.rules_listbox.delete(index)
            self.show_message("规则删除成功")
    
    def save_special_rules(self):
        """保存特殊规则"""
        self.show_message("特殊规则保存成功")
    
    def start_merge(self):
        """开始合并"""
        if not self.imported_files:
            self.show_message("请先导入文件", "warning")
            return
        
        self.progress.start()
        self.status_label.config(text="正在合并...")
        self.show_message("开始合并文件")
        
        # 这里需要调用数据处理模块
        # 暂时模拟合并过程
        self.root.after(2000, self.merge_completed)
    
    def merge_completed(self):
        """合并完成"""
        self.progress.stop()
        self.status_label.config(text="合并完成")
        self.show_message("文件合并完成！")
    
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
            
            # 首先尝试从控制器加载已保存的映射配置
            if self.controller:
                saved_mappings = self.controller.load_field_mapping_config(current_file)
                if saved_mappings:
                    # 将保存的映射配置转换为内部格式
                    for mapping in saved_mappings:
                        standard_field = mapping.get('standard_field', '')
                        imported_column = mapping.get('imported_column', '')
                        is_mapped = mapping.get('is_mapped', False)
                        
                        if standard_field:
                            if current_file not in self.field_mappings:
                                self.field_mappings[current_file] = {}
                            self.field_mappings[current_file][standard_field] = {
                                'imported_column': imported_column,
                                'is_mapped': is_mapped
                            }
            
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
                # 组合完整路径
                full_path = os.path.join(file_path, file_name)
                return full_path
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
                import pandas as pd
                df = pd.read_excel(file_path)
                columns = df.columns.tolist()
            
            # 缓存结果
            self.file_columns_cache[file_path] = columns
            return columns
            
        except Exception as e:
            self.show_message(f"获取文件列名失败: {str(e)}", "error")
        return []
    
    

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
            
            # 调用控制器保存映射配置
            if self.controller:
                success = self.controller.save_field_mapping_config(current_file, mappings)
                if success:
                    # 提取文件名（不包含路径）
                    file_name = os.path.basename(current_file)
                    self.show_message(f"字段映射配置已保存: {file_name}")
                else:
                    self.show_message("保存字段映射配置失败", "error")
            else:
                self.show_message("控制器未初始化", "error")
                
        except Exception as e:
            self.show_message(f"保存字段映射配置失败: {str(e)}", "error")
    

    def run(self):
        """运行界面"""
        self.root.mainloop()


if __name__ == "__main__":
    # 测试界面
    app = ExcelMergeUI()
    app.run()
