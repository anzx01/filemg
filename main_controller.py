"""
Excel文档合并工具 - 主控制器模块
负责整合所有模块，协调整个应用程序的运行
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# 导入自定义模块
from ui_module import ExcelMergeUI
from file_manager import FileManager, FileInfo
from file_operations import FileOperations


class ExcelMergeController:
    """Excel合并工具主控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.file_manager = FileManager()
        self.file_operations = FileOperations()
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
            print("启动Excel文档合并工具...")
            
            # 创建用户界面
            self.ui = ExcelMergeUI()
            
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
    
    def handle_field_mapping(self, file_name: str, mappings: Dict[str, str]) -> bool:
        """
        处理字段映射配置
        
        Args:
            file_name: 文件名
            mappings: 映射关系字典
            
        Returns:
            配置是否成功
        """
        try:
            # 这里将来会调用字段映射模块
            print(f"配置字段映射: {file_name} -> {mappings}")
            
            # 保存映射配置
            self._save_mapping_config(file_name, mappings)
            
            return True
            
        except Exception as e:
            print(f"字段映射配置失败: {e}")
            return False
    
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
            # 加载映射配置
            mapping_config_path = os.path.join(self.config_dir, "mapping_config.json")
            self.mapping_config = self.file_operations.load_json_config(mapping_config_path)
            
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
            self.ui.file_listbox.insert('end', file_info.file_name)
            self.ui.imported_files.append(file_info.file_path)
    
    def _update_ui_file_list(self):
        """更新界面文件列表"""
        if not self.ui:
            return
        
        # 清空现有列表
        self.ui.file_listbox.delete(0, 'end')
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
    
    def _save_mapping_config(self, file_name: str, mappings: Dict[str, str]):
        """保存映射配置"""
        if file_name not in self.mapping_config:
            self.mapping_config[file_name] = {}
        
        self.mapping_config[file_name].update(mappings)
        
        config_path = os.path.join(self.config_dir, "mapping_config.json")
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
