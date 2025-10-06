"""
Excel文档合并工具 - 文件操作模块
负责Excel文件的读写操作和JSON配置文件的处理
"""

import pandas as pd
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import openpyxl
from datetime import datetime


class FileOperations:
    """文件操作类"""
    
    def __init__(self):
        """初始化文件操作器"""
        self.supported_formats = ['.xlsx', '.xls']
        self.encoding = 'utf-8'
    
    def read_excel_file(self, file_path: str, sheet_name: Optional[str] = None, 
                       header_row: int = 0, nrows: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        读取Excel文件
        
        Args:
            file_path: 文件路径
            sheet_name: 工作表名称，None表示第一个工作表
            header_row: 表头行号（从0开始）
            nrows: 读取行数，None表示读取所有行
            
        Returns:
            DataFrame对象，失败返回None
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return None
            
            # 检查文件格式
            if not self._is_valid_excel_file(file_path):
                print(f"不支持的文件格式: {file_path}")
                return None
            
            # 读取Excel文件
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name, 
                                 header=header_row, nrows=nrows)
            else:
                df = pd.read_excel(file_path, header=header_row, nrows=nrows)
            
            # 清理数据
            df = self._clean_dataframe(df)
            
            return df
            
        except Exception as e:
            print(f"读取Excel文件失败: {file_path}, 错误: {e}")
            return None
    
    def write_excel_file(self, df: pd.DataFrame, output_path: str, 
                        sheet_name: str = 'Sheet1', index: bool = False) -> bool:
        """
        写入Excel文件
        
        Args:
            df: 要写入的DataFrame
            output_path: 输出文件路径
            sheet_name: 工作表名称
            index: 是否包含索引
            
        Returns:
            写入是否成功
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 写入Excel文件
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=index)
            
            print(f"文件写入成功: {output_path}")
            return True
            
        except Exception as e:
            print(f"写入Excel文件失败: {output_path}, 错误: {e}")
            return False
    
    def get_excel_sheets(self, file_path: str) -> List[str]:
        """
        获取Excel文件的工作表名称列表
        
        Args:
            file_path: 文件路径
            
        Returns:
            工作表名称列表
        """
        try:
            if not os.path.exists(file_path):
                return []
            
            # 使用openpyxl读取工作表名称
            workbook = openpyxl.load_workbook(file_path, read_only=True)
            sheet_names = workbook.sheetnames
            workbook.close()
            
            return sheet_names
            
        except Exception as e:
            print(f"获取工作表名称失败: {file_path}, 错误: {e}")
            return []
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取Excel文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        try:
            if not os.path.exists(file_path):
                return {}
            
            # 获取文件基本信息
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            modify_time = datetime.fromtimestamp(file_stat.st_mtime)
            
            # 获取工作表信息
            sheet_names = self.get_excel_sheets(file_path)
            
            # 读取第一个工作表的基本信息
            df = self.read_excel_file(file_path, nrows=5)
            row_count = len(df) if df is not None else 0
            column_count = len(df.columns) if df is not None else 0
            
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_size': file_size,
                'modify_time': modify_time.isoformat(),
                'sheet_names': sheet_names,
                'row_count': row_count,
                'column_count': column_count,
                'columns': df.columns.tolist() if df is not None else []
            }
            
        except Exception as e:
            print(f"获取文件信息失败: {file_path}, 错误: {e}")
            return {}
    
    def save_json_config(self, data: Dict[str, Any], config_path: str) -> bool:
        """
        保存JSON配置文件
        
        Args:
            data: 要保存的数据
            config_path: 配置文件路径
            
        Returns:
            保存是否成功
        """
        try:
            # 确保目录存在
            config_dir = os.path.dirname(config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # 保存JSON文件
            with open(config_path, 'w', encoding=self.encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"配置文件保存成功: {config_path}")
            return True
            
        except Exception as e:
            print(f"保存JSON配置失败: {config_path}, 错误: {e}")
            return False
    
    def load_json_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载JSON配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置数据字典，失败返回空字典
        """
        try:
            if not os.path.exists(config_path):
                print(f"配置文件不存在: {config_path}")
                return {}
            
            with open(config_path, 'r', encoding=self.encoding) as f:
                data = json.load(f)
            
            print(f"配置文件加载成功: {config_path}")
            return data
            
        except Exception as e:
            print(f"加载JSON配置失败: {config_path}, 错误: {e}")
            return {}
    
    def get_relative_path(self, file_path: str, base_path: str = None) -> str:
        """
        获取相对路径
        
        Args:
            file_path: 文件路径
            base_path: 基础路径，默认为当前工作目录
            
        Returns:
            相对路径
        """
        try:
            if base_path is None:
                base_path = os.getcwd()
            
            file_path = os.path.abspath(file_path)
            base_path = os.path.abspath(base_path)
            
            return os.path.relpath(file_path, base_path)
            
        except Exception:
            return file_path
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """
        创建文件备份
        
        Args:
            file_path: 要备份的文件路径
            
        Returns:
            备份文件路径，失败返回None
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name, file_ext = os.path.splitext(file_path)
            backup_path = f"{file_name}_backup_{timestamp}{file_ext}"
            
            # 复制文件
            import shutil
            shutil.copy2(file_path, backup_path)
            
            print(f"备份文件创建成功: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"创建备份失败: {file_path}, 错误: {e}")
            return None
    
    def _is_valid_excel_file(self, file_path: str) -> bool:
        """检查是否为有效的Excel文件"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            return file_ext in self.supported_formats
        except Exception:
            return False
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """清理DataFrame数据"""
        try:
            # 删除完全为空的行和列
            df = df.dropna(how='all')
            df = df.dropna(axis=1, how='all')
            
            # 重置索引
            df = df.reset_index(drop=True)
            
            # 清理列名
            df.columns = [str(col).strip() for col in df.columns]
            
            return df
            
        except Exception as e:
            print(f"清理数据失败: {e}")
            return df
    
    def validate_excel_structure(self, file_path: str) -> Dict[str, Any]:
        """
        验证Excel文件结构
        
        Args:
            file_path: 文件路径
            
        Returns:
            验证结果字典
        """
        try:
            if not os.path.exists(file_path):
                return {'valid': False, 'error': '文件不存在'}
            
            # 检查文件格式
            if not self._is_valid_excel_file(file_path):
                return {'valid': False, 'error': '不支持的文件格式'}
            
            # 尝试读取文件
            df = self.read_excel_file(file_path, nrows=10)
            if df is None:
                return {'valid': False, 'error': '无法读取文件内容'}
            
            # 检查是否有数据
            if df.empty:
                return {'valid': False, 'error': '文件为空'}
            
            # 检查列名
            if df.columns.empty:
                return {'valid': False, 'error': '没有列名'}
            
            return {
                'valid': True,
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': df.columns.tolist()
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}


if __name__ == "__main__":
    # 测试文件操作模块
    fo = FileOperations()
    
    # 测试读取Excel文件
    test_file = "test.xlsx"
    if os.path.exists(test_file):
        df = fo.read_excel_file(test_file)
        if df is not None:
            print("文件读取成功")
            print(f"行数: {len(df)}, 列数: {len(df.columns)}")
            print(f"列名: {df.columns.tolist()}")
        else:
            print("文件读取失败")
    
    # 测试JSON配置操作
    test_config = {
        'test_key': 'test_value',
        'test_list': [1, 2, 3],
        'test_dict': {'a': 1, 'b': 2}
    }
    
    config_path = "test_config.json"
    if fo.save_json_config(test_config, config_path):
        loaded_config = fo.load_json_config(config_path)
        print("JSON配置操作成功")
        print(f"加载的配置: {loaded_config}")
    
    # 清理测试文件
    if os.path.exists(config_path):
        os.remove(config_path)
