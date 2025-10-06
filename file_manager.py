"""
Excel文档合并工具 - 文件管理模块
负责文件导入、删除、重新导入等操作
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class FileInfo:
    """文件信息类"""
    
    def __init__(self, file_path: str, file_name: str, columns: List[str], 
                 header_row: int = 0, import_time: datetime = None):
        self.file_path = file_path
        self.file_name = file_name
        self.columns = columns
        self.header_row = header_row
        self.import_time = import_time or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'file_path': self.file_path,
            'file_name': self.file_name,
            'columns': self.columns,
            'header_row': self.header_row,
            'import_time': self.import_time.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileInfo':
        """从字典创建"""
        return cls(
            file_path=data['file_path'],
            file_name=data['file_name'],
            columns=data['columns'],
            header_row=data['header_row'],
            import_time=datetime.fromisoformat(data['import_time'])
        )


class FileManager:
    """文件管理类"""
    
    def __init__(self):
        """初始化文件管理器"""
        self.imported_files: List[FileInfo] = []
        self.config_file = "imported_files.json"
        self.load_imported_files()
    
    def import_excel_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        导入Excel文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            导入结果字典
        """
        results = {
            'success': [],
            'failed': [],
            'duplicates': []
        }
        
        for file_path in file_paths:
            try:
                # 检查文件是否已存在
                if self.is_file_imported(file_path):
                    results['duplicates'].append(file_path)
                    continue
                
                # 验证文件
                if not self.validate_file(file_path):
                    results['failed'].append({'file': file_path, 'error': '文件格式无效'})
                    continue
                
                # 读取文件信息
                file_info = self._read_file_info(file_path)
                if file_info:
                    self.imported_files.append(file_info)
                    results['success'].append(file_info.file_name)
                else:
                    results['failed'].append({'file': file_path, 'error': '无法读取文件信息'})
                    
            except Exception as e:
                results['failed'].append({'file': file_path, 'error': str(e)})
        
        # 保存导入的文件信息
        self.save_imported_files()
        return results
    
    def remove_file(self, file_path: str) -> bool:
        """
        删除已导入文件
        
        Args:
            file_path: 要删除的文件路径
            
        Returns:
            删除是否成功
        """
        for i, file_info in enumerate(self.imported_files):
            if file_info.file_path == file_path:
                self.imported_files.pop(i)
                self.save_imported_files()
                return True
        return False
    
    def reimport_file(self, old_path: str, new_path: str) -> bool:
        """
        重新导入文件
        
        Args:
            old_path: 原文件路径
            new_path: 新文件路径
            
        Returns:
            重新导入是否成功
        """
        try:
            # 验证新文件
            if not self.validate_file(new_path):
                return False
            
            # 读取新文件信息
            new_file_info = self._read_file_info(new_path)
            if not new_file_info:
                return False
            
            # 替换文件信息
            for i, file_info in enumerate(self.imported_files):
                if file_info.file_path == old_path:
                    self.imported_files[i] = new_file_info
                    self.save_imported_files()
                    return True
            
            return False
            
        except Exception:
            return False
    
    def get_imported_files(self) -> List[FileInfo]:
        """获取已导入文件列表"""
        return self.imported_files.copy()
    
    def get_file_by_name(self, file_name: str) -> Optional[FileInfo]:
        """根据文件名获取文件信息"""
        for file_info in self.imported_files:
            if file_info.file_name == file_name:
                return file_info
        return None
    
    def validate_file(self, file_path: str) -> bool:
        """
        验证文件格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件是否有效
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False
            
            # 检查文件扩展名
            if not file_path.lower().endswith(('.xlsx', '.xls')):
                return False
            
            # 尝试读取文件
            df = pd.read_excel(file_path, nrows=1)
            return True
            
        except Exception:
            return False
    
    def get_file_columns(self, file_path: str) -> List[str]:
        """
        获取文件列名
        
        Args:
            file_path: 文件路径
            
        Returns:
            列名列表
        """
        try:
            df = pd.read_excel(file_path, nrows=0)
            return df.columns.tolist()
        except Exception:
            return []
    
    def is_file_imported(self, file_path: str) -> bool:
        """检查文件是否已导入"""
        for file_info in self.imported_files:
            if file_info.file_path == file_path:
                return True
        return False
    
    def clear_all_files(self):
        """清空所有导入的文件"""
        self.imported_files.clear()
        self.save_imported_files()
    
    def _read_file_info(self, file_path: str) -> Optional[FileInfo]:
        """
        读取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息对象
        """
        try:
            # 获取列名
            columns = self.get_file_columns(file_path)
            if not columns:
                return None
            
            # 创建文件信息对象
            file_name = os.path.basename(file_path)
            file_info = FileInfo(
                file_path=file_path,
                file_name=file_name,
                columns=columns,
                header_row=0,  # 默认第一行为表头
                import_time=datetime.now()
            )
            
            return file_info
            
        except Exception:
            return None
    
    def save_imported_files(self):
        """保存导入的文件信息"""
        try:
            data = [file_info.to_dict() for file_info in self.imported_files]
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存文件信息失败: {e}")
    
    def load_imported_files(self):
        """加载导入的文件信息"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.imported_files = []
                for item in data:
                    # 检查文件是否仍然存在
                    if os.path.exists(item['file_path']):
                        file_info = FileInfo.from_dict(item)
                        self.imported_files.append(file_info)
                    else:
                        print(f"文件不存在，跳过: {item['file_path']}")
                        
        except Exception as e:
            print(f"加载文件信息失败: {e}")
            self.imported_files = []
    
    def get_file_summary(self) -> Dict[str, Any]:
        """获取文件导入摘要"""
        return {
            'total_files': len(self.imported_files),
            'files': [
                {
                    'name': f.file_name,
                    'path': f.file_path,
                    'columns': len(f.columns),
                    'import_time': f.import_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                for f in self.imported_files
            ]
        }


if __name__ == "__main__":
    # 测试文件管理模块
    fm = FileManager()
    
    # 测试导入文件
    test_files = ["test1.xlsx", "test2.xlsx"]
    results = fm.import_excel_files(test_files)
    print("导入结果:", results)
    
    # 测试获取文件列表
    files = fm.get_imported_files()
    print("已导入文件:", [f.file_name for f in files])
    
    # 测试文件摘要
    summary = fm.get_file_summary()
    print("文件摘要:", summary)
