"""
Excel文档合并工具 - 主控制器模块
负责整合所有模块，协调整个应用程序的运行
"""

import os
import sys
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

# 导入自定义模块
from ui_module import ExcelMergeUI
from file_manager import FileManager, FileInfo
from file_operations import FileOperations
from header_detection import HeaderDetector
from data_processing import DataProcessor
from special_rules import SpecialRulesManager


class ExcelMergeController:
    """Excel合并工具主控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.file_manager = FileManager()
        self.file_operations = FileOperations()
        self.header_detector = HeaderDetector()
        self.special_rules_manager = SpecialRulesManager()
        self.data_processor = DataProcessor(self.header_detector)
        self.ui = None
        self.config_dir = "config"
        self.output_dir = "output"
        
        # 确保必要目录存在
        self._ensure_directories()
        
        # 初始化配置
        self._load_configurations()
    
    def start_application(self):
        """启动应用程序"""
        try:
            # 创建用户界面
            self.ui = ExcelMergeUI()
            
            # 将控制器绑定到UI
            self.ui.controller = self
            
            # 绑定控制器方法到界面
            self._bind_ui_events()
            
            # 加载已导入的文件
            self._load_imported_files()
            
            # 启动界面
            self.ui.run()
            
        except Exception as e:
            print(f"启动应用程序失败: {e}")
            self._show_error_message(f"启动失败: {e}")
    
    def handle_file_import(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        处理文件导入
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            导入结果
        """
        try:
            print(f"开始导入文件: {file_paths}")
            
            # 使用文件管理器导入文件
            results = self.file_manager.import_excel_files(file_paths)
            
            # 更新界面显示
            if self.ui:
                self._update_ui_file_list()
            
            # 记录导入结果
            self._log_import_results(results)
            
            return results
            
        except Exception as e:
            print(f"文件导入失败: {e}")
            return {'success': [], 'failed': [{'file': f, 'error': str(e)} for f in file_paths], 'duplicates': []}
    
    def handle_file_removal(self, file_path: str) -> bool:
        """
        处理文件删除
        
        Args:
            file_path: 要删除的文件路径
            
        Returns:
            删除是否成功
        """
        try:
            success = self.file_manager.remove_file(file_path)
            
            if success and self.ui:
                self._update_ui_file_list()
            
            return success
            
        except Exception as e:
            print(f"文件删除失败: {e}")
            return False
    
    def handle_file_reimport(self, old_path: str, new_path: str) -> bool:
        """
        处理文件重新导入
        
        Args:
            old_path: 原文件路径
            new_path: 新文件路径
            
        Returns:
            重新导入是否成功
        """
        try:
            success = self.file_manager.reimport_file(old_path, new_path)
            
            if success and self.ui:
                self._update_ui_file_list()
            
            return success
            
        except Exception as e:
            print(f"文件重新导入失败: {e}")
            return False
    
    def save_field_mapping_config(self, file_name: str, mappings: List[Dict[str, Any]]) -> bool:
        """
        保存字段映射配置
        
        Args:
            file_name: 文件名
            mappings: 映射关系列表
            
        Returns:
            保存是否成功
        """
        try:
            print(f"保存字段映射配置: {file_name} -> {len(mappings)} 个映射")
            
            # 保存映射配置
            self._save_field_mapping_config(file_name, mappings)
            
            return True
            
        except Exception as e:
            print(f"字段映射配置保存失败: {e}")
            return False
    
    def load_field_mapping_config(self, file_name: str) -> List[Dict[str, Any]]:
        """
        加载字段映射配置
        
        Args:
            file_name: 文件名
            
        Returns:
            映射关系列表
        """
        try:
            if file_name in self.mapping_config:
                return self.mapping_config[file_name]
            return []
            
        except Exception as e:
            print(f"字段映射配置加载失败: {e}")
            return []
    
    def handle_special_rules(self, file_name: str, rules: List[str]) -> bool:
        """
        处理特殊规则配置
        
        Args:
            file_name: 文件名
            rules: 规则列表
            
        Returns:
            配置是否成功
        """
        try:
            # 这里将来会调用特殊规则模块
            print(f"配置特殊规则: {file_name} -> {rules}")
            
            # 保存规则配置
            self._save_rules_config(file_name, rules)
            
            return True
            
        except Exception as e:
            print(f"特殊规则配置失败: {e}")
            return False
    
    def handle_merge_operation(self) -> Dict[str, Any]:
        """
        处理合并操作
        
        Returns:
            合并结果
        """
        try:
            print("开始合并操作...")
            
            # 获取已导入的文件
            imported_files = self.file_manager.get_imported_files()
            if not imported_files:
                return {'success': False, 'error': '没有已导入的文件'}
            
            # 这里将来会调用数据处理模块进行实际合并
            # 现在只是模拟合并过程
            merged_data = self._simulate_merge_process(imported_files)
            
            # 保存合并结果
            output_path = self._save_merged_data(merged_data)
            
            return {
                'success': True,
                'output_path': output_path,
                'file_count': len(imported_files)
            }
            
        except Exception as e:
            print(f"合并操作失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_operation(self, operation_type: str, **kwargs) -> bool:
        """
        验证操作的有效性
        
        Args:
            operation_type: 操作类型
            **kwargs: 操作参数
            
        Returns:
            操作是否有效
        """
        try:
            if operation_type == 'import':
                return self._validate_import_operation(kwargs.get('file_paths', []))
            elif operation_type == 'merge':
                return self._validate_merge_operation()
            elif operation_type == 'mapping':
                return self._validate_mapping_operation(kwargs.get('file_name', ''))
            else:
                return False
                
        except Exception as e:
            print(f"操作验证失败: {e}")
            return False
    
    def _ensure_directories(self):
        """确保必要目录存在"""
        directories = [self.config_dir, self.output_dir]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"创建目录: {directory}")
    
    def _load_configurations(self):
        """加载配置"""
        try:
            # 加载字段映射配置
            field_mapping_config_path = os.path.join(self.config_dir, "field_mapping_config.json")
            self.mapping_config = self.file_operations.load_json_config(field_mapping_config_path)
            
            # 加载规则配置
            rules_config_path = os.path.join(self.config_dir, "rules_config.json")
            self.rules_config = self.file_operations.load_json_config(rules_config_path)
            
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.mapping_config = {}
            self.rules_config = {}
    
    def _bind_ui_events(self):
        """绑定界面事件"""
        if not self.ui:
            return
        
        # 这里将来会绑定具体的界面事件处理方法
        print("绑定界面事件...")
    
    def _load_imported_files(self):
        """加载已导入的文件到界面"""
        if not self.ui:
            return
        
        imported_files = self.file_manager.get_imported_files()
        for file_info in imported_files:
            # 显示文件名、路径和记录数
            file_name = file_info.file_name
            file_dir = os.path.dirname(file_info.file_path)
            record_count = file_info.record_count
            self.ui.file_treeview.insert('', 'end', values=(file_name, file_dir, f"{record_count}条"))
            self.ui.imported_files.append(file_info.file_path)
    
    def _update_ui_file_list(self):
        """更新界面文件列表"""
        if not self.ui:
            return
        
        # 清空现有列表
        for item in self.ui.file_treeview.get_children():
            self.ui.file_treeview.delete(item)
        self.ui.imported_files.clear()
        
        # 重新加载文件列表
        self._load_imported_files()
    
    def _log_import_results(self, results: Dict[str, Any]):
        """记录导入结果"""
        log_file = os.path.join(self.config_dir, "import_log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] 文件导入结果:\n")
            f.write(f"成功: {len(results['success'])}\n")
            f.write(f"失败: {len(results['failed'])}\n")
            f.write(f"重复: {len(results['duplicates'])}\n")
    
    def _save_field_mapping_config(self, file_name: str, mappings: List[Dict[str, Any]]):
        """保存字段映射配置"""
        self.mapping_config[file_name] = mappings
        
        config_path = os.path.join(self.config_dir, "field_mapping_config.json")
        self.file_operations.save_json_config(self.mapping_config, config_path)
    
    def _save_rules_config(self, file_name: str, rules: List[str]):
        """保存规则配置"""
        if file_name not in self.rules_config:
            self.rules_config[file_name] = []
        
        self.rules_config[file_name] = rules
        
        config_path = os.path.join(self.config_dir, "rules_config.json")
        self.file_operations.save_json_config(self.rules_config, config_path)
    
    def _simulate_merge_process(self, imported_files: List[FileInfo]) -> Dict[str, Any]:
        """模拟合并过程"""
        # 这里将来会实现真正的合并逻辑
        return {
            'total_rows': sum(len(self.file_operations.read_excel_file(f.file_path) or []) for f in imported_files),
            'files_processed': len(imported_files),
            'merge_time': datetime.now().isoformat()
        }
    
    def _save_merged_data(self, merged_data: Dict[str, Any]) -> str:
        """保存合并后的数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"merged_data_{timestamp}.xlsx")
        
        # 这里将来会实现真正的数据保存逻辑
        print(f"合并数据保存到: {output_path}")
        
        return output_path
    
    def _validate_import_operation(self, file_paths: List[str]) -> bool:
        """验证导入操作"""
        if not file_paths:
            return False
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                return False
        
        return True
    
    def _validate_merge_operation(self) -> bool:
        """验证合并操作"""
        imported_files = self.file_manager.get_imported_files()
        return len(imported_files) > 0
    
    def _validate_mapping_operation(self, file_name: str) -> bool:
        """验证映射操作"""
        return bool(file_name and file_name.strip())
    
    def _show_error_message(self, message: str):
        """显示错误消息"""
        print(f"错误: {message}")
        # 这里将来会显示界面错误消息
    
    def merge_files(self, file_paths: List[str], output_path: str) -> bool:
        """合并文件"""
        try:
            print(f"开始合并 {len(file_paths)} 个文件...")
            
            # 使用数据处理器合并文件
            merge_result = self.data_processor.merge_files(file_paths, output_path)
            
            if merge_result:
                print(f"合并完成: {merge_result.total_records} 条记录")
                print(f"处理时间: {merge_result.processing_time:.2f}秒")
                
                # 验证合并结果
                is_valid, issues = self.data_processor.validate_merged_data(merge_result.merged_data)
                if not is_valid:
                    print(f"数据验证警告: {issues}")
                
                # 生成汇总报告
                summary = self.data_processor.generate_summary_report(merge_result)
                print(f"汇总报告: {summary}")
                
                return True
            else:
                print("合并失败")
                return False
                
        except Exception as e:
            print(f"合并文件失败: {e}")
            return False
    
    # ==================== 特殊规则管理方法 ====================
    
    def add_special_rule(self, rule_description: str, bank_name: str = None) -> Dict[str, Any]:
        """添加特殊规则
        
        Args:
            rule_description: 规则描述（自然语言）
            bank_name: 银行名称
            
        Returns:
            Dict: 添加结果
        """
        try:
            return self.special_rules_manager.add_rule(rule_description, bank_name)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "rule": None
            }
    
    def remove_special_rule(self, rule_id: str) -> bool:
        """删除特殊规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            return self.special_rules_manager.remove_rule(rule_id)
        except Exception as e:
            print(f"删除规则失败: {e}")
            return False
    
    def update_special_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """更新特殊规则
        
        Args:
            rule_id: 规则ID
            updates: 更新内容
            
        Returns:
            bool: 更新是否成功
        """
        try:
            return self.special_rules_manager.update_rule(rule_id, updates)
        except Exception as e:
            print(f"更新规则失败: {e}")
            return False
    
    def get_special_rules(self, bank_name: str = None) -> List[Dict[str, Any]]:
        """获取特殊规则列表
        
        Args:
            bank_name: 银行名称，如果指定则只返回该银行的规则
            
        Returns:
            List[Dict]: 规则列表
        """
        try:
            return self.special_rules_manager.get_rules(bank_name)
        except Exception as e:
            print(f"获取规则失败: {e}")
            return []
    
    def get_special_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取特殊规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            Optional[Dict]: 规则对象
        """
        try:
            return self.special_rules_manager.get_rule_by_id(rule_id)
        except Exception as e:
            print(f"获取规则失败: {e}")
            return None
    
    def apply_special_rules(self, data: pd.DataFrame, bank_name: str = None, rule_ids: List[str] = None) -> pd.DataFrame:
        """应用特殊规则到数据
        
        Args:
            data: 输入数据
            bank_name: 银行名称
            rule_ids: 规则ID列表
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        try:
            return self.special_rules_manager.apply_rules(data, bank_name, rule_ids)
        except Exception as e:
            print(f"应用规则失败: {e}")
            return data
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """获取规则统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            return self.special_rules_manager.get_rule_statistics()
        except Exception as e:
            print(f"获取规则统计失败: {e}")
            return {}
    
    def validate_all_rules(self) -> Dict[str, Any]:
        """验证所有规则
        
        Returns:
            Dict: 验证结果
        """
        try:
            return self.special_rules_manager.validate_all_rules()
        except Exception as e:
            print(f"验证规则失败: {e}")
            return {}
    
    def export_rules(self, file_path: str) -> bool:
        """导出规则到文件
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            bool: 导出是否成功
        """
        try:
            return self.special_rules_manager.export_rules(file_path)
        except Exception as e:
            print(f"导出规则失败: {e}")
            return False
    
    def import_rules(self, file_path: str) -> bool:
        """从文件导入规则
        
        Args:
            file_path: 导入文件路径
            
        Returns:
            bool: 导入是否成功
        """
        try:
            return self.special_rules_manager.import_rules(file_path)
        except Exception as e:
            print(f"导入规则失败: {e}")
            return False
    
    def get_merge_result(self, file_paths: List[str], output_path: str):
        """获取合并结果对象"""
        try:
            return self.data_processor.merge_files(file_paths, output_path)
        except Exception as e:
            print(f"获取合并结果失败: {e}")
            return None


def main():
    """主函数"""
    try:
        # 创建控制器
        controller = ExcelMergeController()
        
        # 启动应用程序
        controller.start_application()
        
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
