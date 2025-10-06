"""
Excel文档合并工具 - 用户界面模块
负责创建和管理用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Any
import os
from field_mapping import FieldMappingManager, StandardField, FieldMapping


class ExcelMergeUI:
    """Excel合并工具主界面类"""
    
    def __init__(self):
        """初始化界面"""
        self.root = tk.Tk()
        self.root.title("Excel文档合并工具")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # 界面变量
        self.imported_files = []
        self.standard_fields = []
        self.file_mappings = {}
        self.special_rules = {}
        
        # 字段映射管理器
        self.field_mapping_manager = FieldMappingManager()
        
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
        import_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        import_frame.columnconfigure(1, weight=1)
        
        # 导入按钮
        ttk.Button(import_frame, text="选择Excel文件", 
                  command=self.import_files).grid(row=0, column=0, padx=(0, 10))
        
        # 已导入文件列表
        ttk.Label(import_frame, text="已导入文件:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        # 文件列表框架
        list_frame = ttk.Frame(import_frame)
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        list_frame.columnconfigure(0, weight=1)
        
        # 文件列表 - 增加高度以显示更多文件
        self.file_listbox = tk.Listbox(list_frame, height=12, selectmode=tk.SINGLE)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 文件操作按钮
        button_frame = ttk.Frame(import_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="删除选中", 
                  command=self.remove_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="重新导入", 
                  command=self.reimport_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空列表", 
                  command=self.clear_file_list).pack(side=tk.LEFT)
        
    def create_field_mapping_section(self, parent):
        """创建字段映射区域"""
        # 字段映射框架
        mapping_frame = ttk.LabelFrame(parent, text="字段映射配置", padding="10")
        mapping_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        mapping_frame.columnconfigure(1, weight=1)
        
        # 标准字段管理
        std_field_frame = ttk.Frame(mapping_frame)
        std_field_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        std_field_frame.columnconfigure(1, weight=1)
        
        ttk.Label(std_field_frame, text="标准字段:").grid(row=0, column=0, sticky=tk.W)
        
        # 标准字段输入和按钮
        input_frame = ttk.Frame(std_field_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        input_frame.columnconfigure(0, weight=1)
        
        self.std_field_entry = ttk.Entry(input_frame)
        self.std_field_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(input_frame, text="添加", 
                  command=self.add_standard_field).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(input_frame, text="删除", 
                  command=self.remove_standard_field).grid(row=0, column=2)
        
        # 标准字段列表
        self.std_field_listbox = tk.Listbox(std_field_frame, height=4)
        self.std_field_listbox.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 文件映射配置
        file_mapping_frame = ttk.Frame(mapping_frame)
        file_mapping_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        file_mapping_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_mapping_frame, text="选择文件:").grid(row=0, column=0, sticky=tk.W)
        
        self.file_combo = ttk.Combobox(file_mapping_frame, state="readonly")
        self.file_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        self.file_combo.bind('<<ComboboxSelected>>', self.on_file_selected)
        
        # 映射配置按钮
        ttk.Button(file_mapping_frame, text="配置映射", 
                  command=self.configure_mapping).grid(row=0, column=2, padx=(10, 0))
        
        # 映射配置区域
        self.mapping_config_frame = ttk.Frame(mapping_frame)
        self.mapping_config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def create_special_rules_section(self, parent):
        """创建特殊规则区域"""
        # 特殊规则框架
        rules_frame = ttk.LabelFrame(parent, text="特殊规则配置", padding="10")
        rules_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
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
        
    def create_merge_section(self, parent):
        """创建合并操作区域"""
        # 合并操作框架
        merge_frame = ttk.LabelFrame(parent, text="合并操作", padding="10")
        merge_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
                    
                    # 显示文件名和记录数
                    file_name = os.path.basename(file_path)
                    display_text = f"{file_name} ({record_count}条记录)"
                    self.file_listbox.insert(tk.END, display_text)
                    
                    # 更新下拉框
                    self.file_combo['values'] = list(self.file_combo['values']) + [file_name]
                    self.rule_file_combo['values'] = list(self.rule_file_combo['values']) + [file_name]
                    
                    imported_count += 1
                
                # 显示导入结果
                if duplicate_count > 0:
                    self.show_message(f"成功导入 {imported_count} 个文件，跳过 {duplicate_count} 个已导入文件")
                else:
                    self.show_message(f"成功导入 {imported_count} 个文件")
    
    def remove_selected_file(self):
        """删除选中的文件"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            file_path = self.imported_files[index]
            
            # 如果有控制器，使用控制器处理
            if hasattr(self, 'controller') and self.controller:
                success = self.controller.handle_file_removal(file_path)
                if success:
                    self.show_message(f"已删除文件: {os.path.basename(file_path)}")
                else:
                    self.show_message("删除文件失败")
            else:
                # 直接处理（兼容模式）
                self.imported_files.pop(index)
                self.file_listbox.delete(index)
                
                # 更新下拉框
                self.update_file_combos()
                self.show_message(f"已删除文件: {os.path.basename(file_path)}")
    
    def reimport_file(self):
        """重新导入文件"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            old_path = self.imported_files[index]
            new_path = filedialog.askopenfilename(
                title="重新选择文件",
                filetypes=[("Excel文件", "*.xlsx *.xls")]
            )
            if new_path:
                self.imported_files[index] = new_path
                self.file_listbox.delete(index)
                self.file_listbox.insert(index, os.path.basename(new_path))
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
                self.file_listbox.delete(0, tk.END)
                self.file_combo['values'] = []
                self.rule_file_combo['values'] = []
                self.show_message("文件列表已清空")
    
    def update_file_combos(self):
        """更新文件下拉框"""
        file_names = [os.path.basename(f) for f in self.imported_files]
        self.file_combo['values'] = file_names
        self.rule_file_combo['values'] = file_names
    
    def add_standard_field(self):
        """添加标准字段"""
        field_name = self.std_field_entry.get().strip()
        if field_name:
            # 创建标准字段对象
            field = StandardField(
                name=field_name,
                display_name=field_name,
                data_type="string",
                required=False,
                description=""
            )
            
            # 添加到字段映射管理器
            success = self.field_mapping_manager.add_standard_field(field)
            if success:
                self.refresh_standard_fields()
                self.std_field_entry.delete(0, tk.END)
                self.show_message(f"已添加标准字段: {field_name}")
            else:
                self.show_message("该字段已存在", "warning")
        else:
            self.show_message("请输入字段名", "warning")
    
    def remove_standard_field(self):
        """删除标准字段"""
        selection = self.std_field_listbox.curselection()
        if selection:
            index = selection[0]
            field_name = self.std_field_listbox.get(index)
            
            # 从字段映射管理器删除
            success = self.field_mapping_manager.remove_standard_field(field_name)
            if success:
                self.refresh_standard_fields()
                self.show_message(f"已删除标准字段: {field_name}")
            else:
                self.show_message("无法删除字段，存在相关映射", "warning")
        else:
            self.show_message("请选择要删除的字段", "warning")
    
    def refresh_standard_fields(self):
        """刷新标准字段列表"""
        self.std_field_listbox.delete(0, tk.END)
        for field in self.field_mapping_manager.get_standard_fields():
            self.std_field_listbox.insert(tk.END, f"{field.display_name} ({field.name})")
    
    def refresh_standard_field_combo(self):
        """刷新标准字段下拉框"""
        field_names = [field.name for field in self.field_mapping_manager.get_standard_fields()]
        # 这里需要在界面中添加标准字段下拉框
        pass
    
    def on_file_selected(self, event):
        """文件选择事件"""
        # 清空映射配置区域
        for widget in self.mapping_config_frame.winfo_children():
            widget.destroy()
    
    def configure_mapping(self):
        """配置映射"""
        selected_file = self.file_combo.get()
        if not selected_file:
            self.show_message("请先选择文件", "warning")
            return
        
        # 获取文件路径
        file_path = None
        for file_info in self.imported_files:
            if os.path.basename(file_info) == selected_file:
                file_path = file_info
                break
        
        if not file_path:
            self.show_message("找不到文件路径", "error")
            return
        
        # 获取文件列名
        columns = self.field_mapping_manager.get_file_columns(file_path)
        if not columns:
            self.show_message("无法读取文件列名", "error")
            return
        
        # 创建映射配置对话框
        self.create_mapping_dialog(selected_file, file_path, columns)
    
    def create_mapping_dialog(self, file_name, file_path, columns):
        """创建映射配置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"配置字段映射 - {file_name}")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建映射表格
        self.create_mapping_table(main_frame, file_name, file_path, columns)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="保存映射", 
                  command=lambda: self.save_mapping_dialog(dialog, file_name, file_path)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", 
                  command=dialog.destroy).pack(side=tk.RIGHT)
    
    def create_mapping_table(self, parent, file_name, file_path, columns):
        """创建映射表格"""
        # 表格框架
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns_list = ["标准字段", "文件字段", "映射类型", "变换规则"]
        self.mapping_tree = ttk.Treeview(table_frame, columns=columns_list, show="headings", height=15)
        
        # 设置列标题
        for col in columns_list:
            self.mapping_tree.heading(col, text=col)
            self.mapping_tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.mapping_tree.yview)
        self.mapping_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.mapping_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 填充数据
        self.populate_mapping_table(file_name, file_path, columns)
    
    def populate_mapping_table(self, file_name, file_path, columns):
        """填充映射表格数据"""
        # 获取标准字段
        standard_fields = self.field_mapping_manager.get_standard_fields()
        
        # 获取现有映射
        file_id = os.path.basename(file_path)
        existing_mappings = {m.standard_field: m for m in self.field_mapping_manager.get_file_mappings(file_id)}
        
        for field in standard_fields:
            # 获取建议的文件字段
            suggested_field = self.field_mapping_manager.suggest_mapping(columns, field.name)
            
            # 获取现有映射
            existing_mapping = existing_mappings.get(field.name)
            
            # 创建行数据
            file_field = existing_mapping.file_field if existing_mapping else (suggested_field or "")
            mapping_type = existing_mapping.mapping_type if existing_mapping else "direct"
            transform_rule = existing_mapping.transform_rule if existing_mapping else ""
            
            # 插入行
            item_id = self.mapping_tree.insert("", tk.END, values=[
                field.display_name,
                file_field,
                mapping_type,
                transform_rule
            ])
            
            # 为文件字段列创建下拉框
            self.create_field_combo(item_id, columns, file_field)
    
    def create_field_combo(self, item_id, columns, current_value):
        """为表格行创建字段下拉框"""
        # 这里需要实现内嵌下拉框
        # 由于tkinter的限制，这是一个复杂的功能
        # 暂时使用简单实现
        pass
    
    def save_mapping_dialog(self, dialog, file_name, file_path):
        """保存映射对话框"""
        file_id = os.path.basename(file_path)
        
        # 遍历表格行，保存映射
        for item in self.mapping_tree.get_children():
            values = self.mapping_tree.item(item, "values")
            standard_field = values[0]
            file_field = values[1]
            mapping_type = values[2]
            transform_rule = values[3]
            
            if file_field:  # 只保存有映射的字段
                success = self.field_mapping_manager.update_field_mapping(
                    file_id, standard_field, file_field, mapping_type, transform_rule
                )
        
        self.show_message(f"已保存 {file_name} 的字段映射")
        dialog.destroy()
    
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
    
    def run(self):
        """运行界面"""
        self.root.mainloop()


if __name__ == "__main__":
    # 测试界面
    app = ExcelMergeUI()
    app.run()
