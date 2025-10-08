"""
特殊规则配置界面模块

该模块提供特殊规则配置的用户界面，支持自然语言规则输入和银行特定规则管理。

作者: AI助手
创建时间: 2025-01-27
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from typing import Dict, List, Any, Optional
from special_rules import SpecialRulesManager
from rule_parser import RuleParser


class SpecialRulesUI:
    """特殊规则配置界面类"""
    
    def __init__(self, parent=None):
        """初始化特殊规则配置界面
        
        Args:
            parent: 父窗口，如果为None则创建独立窗口
        """
        self.parent = parent
        self.rules_manager = SpecialRulesManager()
        self.rule_parser = RuleParser()
        
        # 银行列表
        self.bank_list = [
            "北京银行", "工商银行", "华夏银行", "长安银行", 
            "建设银行", "招商银行", "浦发银行", "邮储银行", 
            "兴业银行", "中国银行"
        ]
        
        # 规则类型列表
        self.rule_types = [
            "日期范围处理", "余额计算", "收支分类", "分页符处理", 
            "表头处理", "字段映射", "自定义规则"
        ]
        
        # 创建界面
        self.create_ui()
        
        # 加载现有规则
        self.load_rules_to_tree()
    
    def create_ui(self):
        """创建用户界面"""
        if self.parent:
            self.window = tk.Toplevel(self.parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("特殊规则配置")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧规则列表区域
        self.create_rules_list_area(main_frame)
        
        # 创建右侧规则编辑区域
        self.create_rule_edit_area(main_frame)
        
        # 创建底部按钮区域
        self.create_button_area(main_frame)
    
    def create_rules_list_area(self, parent):
        """创建规则列表区域"""
        # 左侧框架
        left_frame = ttk.LabelFrame(parent, text="规则列表", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 搜索框
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 银行筛选
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="银行筛选:").pack(side=tk.LEFT)
        self.bank_filter_var = tk.StringVar()
        self.bank_filter_var.set("全部")
        self.bank_filter_var.trace('w', self.on_filter_change)
        bank_combo = ttk.Combobox(filter_frame, textvariable=self.bank_filter_var, 
                                 values=["全部"] + self.bank_list, state="readonly")
        bank_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 规则树形视图
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图
        columns = ("ID", "银行", "类型", "描述", "状态")
        self.rules_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        self.rules_tree.heading("ID", text="规则ID")
        self.rules_tree.heading("银行", text="银行")
        self.rules_tree.heading("类型", text="类型")
        self.rules_tree.heading("描述", text="描述")
        self.rules_tree.heading("状态", text="状态")
        
        # 设置列宽
        self.rules_tree.column("ID", width=80)
        self.rules_tree.column("银行", width=100)
        self.rules_tree.column("类型", width=120)
        self.rules_tree.column("描述", width=200)
        self.rules_tree.column("状态", width=80)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=tree_scroll.set)
        
        # 布局
        self.rules_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.rules_tree.bind("<<TreeviewSelect>>", self.on_rule_select)
        
        # 规则操作按钮
        rule_buttons_frame = ttk.Frame(left_frame)
        rule_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(rule_buttons_frame, text="新增规则", command=self.add_new_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rule_buttons_frame, text="编辑规则", command=self.edit_selected_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rule_buttons_frame, text="删除规则", command=self.delete_selected_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rule_buttons_frame, text="复制规则", command=self.copy_selected_rule).pack(side=tk.LEFT)
    
    def create_rule_edit_area(self, parent):
        """创建规则编辑区域"""
        # 右侧框架
        right_frame = ttk.LabelFrame(parent, text="规则编辑", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 基本信息
        basic_frame = ttk.LabelFrame(right_frame, text="基本信息", padding=10)
        basic_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 银行选择
        bank_frame = ttk.Frame(basic_frame)
        bank_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(bank_frame, text="银行:").pack(side=tk.LEFT)
        self.bank_var = tk.StringVar()
        bank_combo = ttk.Combobox(bank_frame, textvariable=self.bank_var, 
                                 values=self.bank_list, state="readonly")
        bank_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 规则类型
        type_frame = ttk.Frame(basic_frame)
        type_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(type_frame, text="类型:").pack(side=tk.LEFT)
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(type_frame, textvariable=self.type_var, 
                                 values=self.rule_types, state="readonly")
        type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 规则状态
        status_frame = ttk.Frame(basic_frame)
        status_frame.pack(fill=tk.X)
        ttk.Label(status_frame, text="状态:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar()
        self.status_var.set("active")
        status_combo = ttk.Combobox(status_frame, textvariable=self.status_var, 
                                   values=["active", "inactive"], state="readonly")
        status_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 规则描述
        desc_frame = ttk.LabelFrame(right_frame, text="规则描述", padding=10)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(desc_frame, text="自然语言描述:").pack(anchor=tk.W)
        self.desc_text = scrolledtext.ScrolledText(desc_frame, height=6, wrap=tk.WORD)
        self.desc_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 预设规则模板
        template_frame = ttk.LabelFrame(right_frame, text="预设规则模板", padding=10)
        template_frame.pack(fill=tk.X)
        
        template_buttons_frame = ttk.Frame(template_frame)
        template_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(template_buttons_frame, text="北京银行日期规则", 
                  command=lambda: self.load_template("beijing_date")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(template_buttons_frame, text="工商银行收支规则", 
                  command=lambda: self.load_template("icbc_balance")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(template_buttons_frame, text="华夏银行收支规则", 
                  command=lambda: self.load_template("hx_balance")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(template_buttons_frame, text="招商银行正负规则", 
                  command=lambda: self.load_template("cmb_sign")).pack(side=tk.LEFT)
        
        # 规则参数
        params_frame = ttk.LabelFrame(right_frame, text="规则参数", padding=10)
        params_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(params_frame, text="解析后的参数:").pack(anchor=tk.W)
        self.params_text = scrolledtext.ScrolledText(params_frame, height=4, wrap=tk.WORD)
        self.params_text.pack(fill=tk.X, pady=(5, 0))
    
    def create_button_area(self, parent):
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="保存规则", command=self.save_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="测试规则", command=self.test_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="导入规则", command=self.import_rules).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="导出规则", command=self.export_rules).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空表单", command=self.clear_form).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="关闭", command=self.window.destroy).pack(side=tk.RIGHT)
    
    def load_rules_to_tree(self):
        """加载规则到树形视图"""
        # 清空现有项目
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        
        # 获取所有规则
        rules = self.rules_manager.get_rules()
        
        # 添加到树形视图
        for rule in rules:
            self.rules_tree.insert("", tk.END, values=(
                rule.get("id", ""),
                rule.get("bank_name", ""),
                rule.get("type", ""),
                rule.get("description", "")[:50] + "..." if len(rule.get("description", "")) > 50 else rule.get("description", ""),
                rule.get("status", "")
            ))
    
    def on_search_change(self, *args):
        """搜索框变化事件"""
        search_text = self.search_var.get().lower()
        bank_filter = self.bank_filter_var.get()
        
        # 清空现有项目
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        
        # 获取所有规则
        rules = self.rules_manager.get_rules()
        
        # 筛选规则
        filtered_rules = []
        for rule in rules:
            # 银行筛选
            if bank_filter != "全部" and rule.get("bank_name") != bank_filter:
                continue
            
            # 文本搜索
            if search_text:
                searchable_text = (rule.get("description", "") + " " + 
                                 rule.get("bank_name", "") + " " + 
                                 rule.get("type", "")).lower()
                if search_text not in searchable_text:
                    continue
            
            filtered_rules.append(rule)
        
        # 添加到树形视图
        for rule in filtered_rules:
            self.rules_tree.insert("", tk.END, values=(
                rule.get("id", ""),
                rule.get("bank_name", ""),
                rule.get("type", ""),
                rule.get("description", "")[:50] + "..." if len(rule.get("description", "")) > 50 else rule.get("description", ""),
                rule.get("status", "")
            ))
    
    def on_filter_change(self, *args):
        """筛选变化事件"""
        self.on_search_change()
    
    def on_rule_select(self, event):
        """规则选择事件"""
        selection = self.rules_tree.selection()
        if selection:
            item = self.rules_tree.item(selection[0])
            rule_id = item['values'][0]
            
            # 获取规则详情
            rule = self.rules_manager.get_rule_by_id(rule_id)
            if rule:
                self.load_rule_to_form(rule)
    
    def load_rule_to_form(self, rule):
        """加载规则到表单"""
        self.bank_var.set(rule.get("bank_name", ""))
        self.type_var.set(rule.get("type", ""))
        self.status_var.set(rule.get("status", "active"))
        
        # 清空并设置描述
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, rule.get("description", ""))
        
        # 设置参数
        self.params_text.delete(1.0, tk.END)
        params = rule.get("parameters", {})
        self.params_text.insert(1.0, json.dumps(params, ensure_ascii=False, indent=2))
    
    def add_new_rule(self):
        """添加新规则"""
        self.clear_form()
        self.desc_text.focus()
    
    def edit_selected_rule(self):
        """编辑选中的规则"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个规则")
            return
        
        # 规则已在选择事件中加载到表单
        pass
    
    def delete_selected_rule(self):
        """删除选中的规则"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个规则")
            return
        
        item = self.rules_tree.item(selection[0])
        rule_id = item['values'][0]
        
        if messagebox.askyesno("确认删除", f"确定要删除规则 {rule_id} 吗？"):
            if self.rules_manager.remove_rule(rule_id):
                messagebox.showinfo("成功", "规则删除成功")
                self.load_rules_to_tree()
                self.clear_form()
            else:
                messagebox.showerror("错误", "规则删除失败")
    
    def copy_selected_rule(self):
        """复制选中的规则"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个规则")
            return
        
        item = self.rules_tree.item(selection[0])
        rule_id = item['values'][0]
        
        # 获取规则详情
        rule = self.rules_manager.get_rule_by_id(rule_id)
        if rule:
            # 清空ID，创建新规则
            rule_copy = rule.copy()
            rule_copy["id"] = f"rule_{len(self.rules_manager.get_rules()) + 1}"
            rule_copy["description"] = rule_copy["description"] + " (副本)"
            
            # 添加到规则管理器
            self.rules_manager.rules.append(rule_copy)
            self.rules_manager.save_rules()
            
            messagebox.showinfo("成功", "规则复制成功")
            self.load_rules_to_tree()
    
    def save_rule(self):
        """保存规则"""
        # 获取表单数据
        bank_name = self.bank_var.get()
        rule_type = self.type_var.get()
        status = self.status_var.get()
        description = self.desc_text.get(1.0, tk.END).strip()
        
        if not description:
            messagebox.showwarning("警告", "请输入规则描述")
            return
        
        if not bank_name:
            messagebox.showwarning("警告", "请选择银行")
            return
        
        # 解析规则
        try:
            result = self.rules_manager.add_rule(description, bank_name, rule_type)
            if result["success"]:
                messagebox.showinfo("成功", "规则保存成功")
                self.load_rules_to_tree()
                
                # 更新参数显示
                rule = result["rule"]
                self.params_text.delete(1.0, tk.END)
                self.params_text.insert(1.0, json.dumps(rule.get("parameters", {}), 
                                                       ensure_ascii=False, indent=2))
            else:
                messagebox.showerror("错误", f"规则保存失败: {result['error']}")
        except Exception as e:
            messagebox.showerror("错误", f"保存规则时发生错误: {str(e)}")
    
    def test_rule(self):
        """测试规则"""
        description = self.desc_text.get(1.0, tk.END).strip()
        if not description:
            messagebox.showwarning("警告", "请输入规则描述")
            return
        
        try:
            # 解析规则
            parsed_rule = self.rule_parser.parse_natural_language_rule(description)
            
            if parsed_rule.get("error"):
                messagebox.showerror("错误", f"规则解析失败: {parsed_rule['error']}")
            else:
                # 显示解析结果
                self.params_text.delete(1.0, tk.END)
                self.params_text.insert(1.0, json.dumps(parsed_rule, ensure_ascii=False, indent=2))
                
                messagebox.showinfo("成功", "规则解析成功，请查看参数区域")
        except Exception as e:
            messagebox.showerror("错误", f"测试规则时发生错误: {str(e)}")
    
    def load_template(self, template_name):
        """加载预设模板"""
        templates = {
            "beijing_date": "北京银行.excel文件，从第二行获取日期范围，与月日数据合并，在合并文件时将对应记录存入合并文件标准字段交易日期。",
            "icbc_balance": "工商银行.excel文件，根据借贷标志字段，在合并文件时将发生额存入合并文件标准字段收入或支出（贷为收入，借为支出）；导入文件中包含查询编号或对公往来户明细表字符的行为分页符，其所在行不在导出文件里出现；导入文件只有开始一个包含列名的有效表头，其他表头不在导出文档体现。",
            "hx_balance": "华夏银行.excel文件：根据借贷标志字段，在合并文件时将发生额存入合并文件标准字段收入或支出（贷为收入，借为支出）。",
            "cmb_sign": "招商银行.excel文件：根据交易金额（或交易金额）字段的正负号，将其对应记录数据存入收入或支出（正数为收入，负数为支出）。"
        }
        
        if template_name in templates:
            self.desc_text.delete(1.0, tk.END)
            self.desc_text.insert(1.0, templates[template_name])
    
    def import_rules(self):
        """导入规则"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="选择规则文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            if self.rules_manager.import_rules(file_path):
                messagebox.showinfo("成功", "规则导入成功")
                self.load_rules_to_tree()
            else:
                messagebox.showerror("错误", "规则导入失败")
    
    def export_rules(self):
        """导出规则"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="保存规则文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            if self.rules_manager.export_rules(file_path):
                messagebox.showinfo("成功", "规则导出成功")
            else:
                messagebox.showerror("错误", "规则导出失败")
    
    def clear_form(self):
        """清空表单"""
        self.bank_var.set("")
        self.type_var.set("")
        self.status_var.set("active")
        self.desc_text.delete(1.0, tk.END)
        self.params_text.delete(1.0, tk.END)
    
    def run(self):
        """运行界面"""
        self.window.mainloop()


# 测试代码
if __name__ == "__main__":
    # 创建特殊规则配置界面
    app = SpecialRulesUI()
    app.run()
