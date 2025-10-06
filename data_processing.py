"""
Excel文档合并工具 - 数据处理模块
负责数据预处理、字段映射应用和数据合并功能
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import os
from datetime import datetime
import re

from field_mapping import FieldMappingManager, FieldMapping
from header_detection import HeaderDetector, HeaderInfo


@dataclass
class ProcessedData:
    """处理后的数据类"""
    file_id: str
    file_name: str
    sheet_name: str
    data: pd.DataFrame
    mapped_columns: Dict[str, str]
    balance_columns: List[str]
    processing_info: Dict[str, Any]


@dataclass
class MergeResult:
    """合并结果数据类"""
    merged_data: pd.DataFrame
    source_files: List[str]
    total_records: int
    processing_time: float
    merge_info: Dict[str, Any]


class DataProcessor:
    """数据处理器"""
    
    def __init__(self, field_mapping_manager: FieldMappingManager, header_detector: HeaderDetector):
        """初始化数据处理器"""
        self.field_mapping_manager = field_mapping_manager
        self.header_detector = header_detector
        
        # 数据类型转换规则
        self.data_type_converters = {
            "string": self._convert_to_string,
            "number": self._convert_to_number,
            "date": self._convert_to_date,
            "boolean": self._convert_to_boolean
        }
    
    def _convert_to_string(self, data: pd.Series) -> pd.Series:
        """转换为字符串类型"""
        return data.astype(str)
    
    def _convert_to_number(self, data: pd.Series) -> pd.Series:
        """转换为数值类型"""
        return pd.to_numeric(data, errors='coerce')
    
    def _convert_to_date(self, data: pd.Series) -> pd.Series:
        """转换为日期类型"""
        return pd.to_datetime(data, errors='coerce')
    
    def _convert_to_boolean(self, data: pd.Series) -> pd.Series:
        """转换为布尔类型"""
        return data.astype(bool)
    
    def process_file(self, file_path: str, sheet_name: Optional[str] = None) -> Optional[ProcessedData]:
        """处理单个文件"""
        try:
            # 获取文件信息
            file_id = os.path.basename(file_path)
            file_name = os.path.basename(file_path)
            
            # 检测表头
            headers = self.header_detector.detect_headers(file_path, sheet_name)
            if not headers:
                print(f"无法检测到表头: {file_path}")
                return None
            
            header = headers[0] if not sheet_name else next((h for h in headers if h.sheet_name == sheet_name), headers[0])
            
            # 读取数据
            df = pd.read_excel(file_path, sheet_name=header.sheet_name, header=header.header_row)
            
            # 清理数据
            df = self._clean_data(df)
            
            # 应用字段映射
            mapped_data, mapped_columns = self._apply_field_mapping(df, file_id, header.columns)
            
            # 识别余额列
            balance_columns = self._identify_balance_columns(mapped_data, header.balance_columns)
            
            # 创建处理信息
            processing_info = {
                "original_columns": header.columns,
                "mapped_columns": mapped_columns,
                "balance_columns": balance_columns,
                "data_shape": mapped_data.shape,
                "processing_time": datetime.now().isoformat()
            }
            
            return ProcessedData(
                file_id=file_id,
                file_name=file_name,
                sheet_name=header.sheet_name,
                data=mapped_data,
                mapped_columns=mapped_columns,
                balance_columns=balance_columns,
                processing_info=processing_info
            )
            
        except Exception as e:
            print(f"处理文件失败 {file_path}: {e}")
            return None
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清理数据"""
        # 删除完全为空的行
        df = df.dropna(how='all')
        
        # 删除完全为空的列
        df = df.dropna(axis=1, how='all')
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        # 清理字符串数据
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('', np.nan)
        
        return df
    
    def _apply_field_mapping(self, df: pd.DataFrame, file_id: str, original_columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """应用字段映射"""
        # 获取文件的所有映射
        mappings = self.field_mapping_manager.get_file_mappings(file_id)
        
        if not mappings:
            # 如果没有映射，返回原始数据
            return df, {}
        
        # 创建映射字典
        mapping_dict = {m.standard_field: m for m in mappings}
        
        # 创建新的数据框
        mapped_data = pd.DataFrame()
        mapped_columns = {}
        
        for mapping in mappings:
            if mapping.file_field in df.columns:
                # 获取原始列数据
                original_data = df[mapping.file_field].copy()
                
                # 应用数据转换
                if mapping.mapping_type == "transform" and mapping.transform_rule:
                    original_data = self._apply_transform(original_data, mapping.transform_rule)
                elif mapping.mapping_type == "custom":
                    original_data = self._apply_custom_rule(original_data, mapping.transform_rule)
                
                # 添加到映射后的数据框
                mapped_data[mapping.standard_field] = original_data
                mapped_columns[mapping.standard_field] = mapping.file_field
        
        return mapped_data, mapped_columns
    
    def _apply_transform(self, data: pd.Series, transform_rule: str) -> pd.Series:
        """应用数据转换规则"""
        try:
            # 简单的转换规则处理
            if transform_rule == "upper()":
                return data.astype(str).str.upper()
            elif transform_rule == "lower()":
                return data.astype(str).str.lower()
            elif transform_rule == "strip()":
                return data.astype(str).str.strip()
            elif transform_rule == "abs()":
                return pd.to_numeric(data, errors='coerce').abs()
            else:
                # 默认返回原始数据
                return data
        except Exception as e:
            print(f"应用转换规则失败: {e}")
            return data
    
    def _apply_custom_rule(self, data: pd.Series, custom_rule: str) -> pd.Series:
        """应用自定义规则"""
        try:
            # 这里可以实现更复杂的自定义规则
            # 暂时返回原始数据
            return data
        except Exception as e:
            print(f"应用自定义规则失败: {e}")
            return data
    
    def _identify_balance_columns(self, df: pd.DataFrame, detected_balance_columns: List[str]) -> List[str]:
        """识别余额列"""
        balance_columns = []
        
        # 使用检测到的余额列
        for col in detected_balance_columns:
            if col in df.columns:
                balance_columns.append(col)
        
        # 如果没有检测到余额列，尝试从列名推断
        if not balance_columns:
            for col in df.columns:
                if self._is_balance_column_name(col):
                    balance_columns.append(col)
        
        return balance_columns
    
    def _is_balance_column_name(self, column_name: str) -> bool:
        """判断列名是否为余额列"""
        balance_keywords = ["余额", "结余", "balance", "结存", "可用余额", "账户余额"]
        col_lower = str(column_name).lower()
        
        for keyword in balance_keywords:
            if keyword in col_lower:
                return True
        
        return False
    
    def merge_files(self, file_paths: List[str], output_path: str) -> Optional[MergeResult]:
        """合并多个文件"""
        try:
            start_time = datetime.now()
            
            # 处理所有文件
            processed_files = []
            for file_path in file_paths:
                processed_data = self.process_file(file_path)
                if processed_data:
                    processed_files.append(processed_data)
            
            if not processed_files:
                print("没有成功处理的文件")
                return None
            
            # 合并数据
            merged_data = self._merge_processed_data(processed_files)
            
            # 保存合并后的数据
            merged_data.to_excel(output_path, index=False)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 创建合并信息
            merge_info = {
                "source_files": [pf.file_name for pf in processed_files],
                "total_records": len(merged_data),
                "columns": list(merged_data.columns),
                "processing_time": processing_time,
                "output_file": output_path
            }
            
            return MergeResult(
                merged_data=merged_data,
                source_files=[pf.file_name for pf in processed_files],
                total_records=len(merged_data),
                processing_time=processing_time,
                merge_info=merge_info
            )
            
        except Exception as e:
            print(f"合并文件失败: {e}")
            return None
    
    def _merge_processed_data(self, processed_files: List[ProcessedData]) -> pd.DataFrame:
        """合并处理后的数据"""
        if not processed_files:
            return pd.DataFrame()
        
        # 获取所有列名
        all_columns = set()
        for pf in processed_files:
            all_columns.update(pf.data.columns)
        
        # 创建统一的数据框
        merged_data = pd.DataFrame()
        
        for pf in processed_files:
            # 为每个文件添加源文件标识
            file_data = pf.data.copy()
            file_data['source_file'] = pf.file_name
            
            # 确保所有列都存在
            for col in all_columns:
                if col not in file_data.columns:
                    file_data[col] = np.nan
            
            # 合并数据
            merged_data = pd.concat([merged_data, file_data], ignore_index=True)
        
        return merged_data
    
    def validate_merged_data(self, merged_data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """验证合并后的数据"""
        issues = []
        
        # 检查数据完整性
        if merged_data.empty:
            issues.append("合并后的数据为空")
        
        # 检查必要列
        required_columns = ["account_number", "account_name", "transaction_date", "transaction_amount"]
        missing_columns = [col for col in required_columns if col not in merged_data.columns]
        if missing_columns:
            issues.append(f"缺少必要列: {missing_columns}")
        
        # 检查数据类型
        if "transaction_amount" in merged_data.columns:
            try:
                pd.to_numeric(merged_data["transaction_amount"], errors='coerce')
            except:
                issues.append("交易金额列包含非数值数据")
        
        # 检查重复记录
        if merged_data.duplicated().any():
            issues.append("存在重复记录")
        
        return len(issues) == 0, issues
    
    def generate_summary_report(self, merge_result: MergeResult) -> Dict[str, Any]:
        """生成汇总报告"""
        try:
            data = merge_result.merged_data
            
            # 基本统计信息
            summary = {
                "total_records": len(data),
                "total_files": len(merge_result.source_files),
                "processing_time": merge_result.processing_time,
                "columns": list(data.columns),
                "data_types": data.dtypes.to_dict(),
                "missing_values": data.isnull().sum().to_dict(),
                "duplicate_records": data.duplicated().sum()
            }
            
            # 数值列统计
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                summary["numeric_summary"] = data[numeric_columns].describe().to_dict()
            
            # 日期列统计
            date_columns = data.select_dtypes(include=['datetime64']).columns
            if len(date_columns) > 0:
                summary["date_summary"] = {}
                for col in date_columns:
                    summary["date_summary"][col] = {
                        "min": data[col].min(),
                        "max": data[col].max(),
                        "unique_dates": data[col].nunique()
                    }
            
            return summary
            
        except Exception as e:
            print(f"生成汇总报告失败: {e}")
            return {}
    
    def export_processing_log(self, merge_result: MergeResult, log_path: str) -> bool:
        """导出处理日志"""
        try:
            import json
            
            log_data = {
                "processing_time": merge_result.processing_time,
                "source_files": merge_result.source_files,
                "total_records": merge_result.total_records,
                "output_file": merge_result.merge_info.get("output_file", ""),
                "columns": list(merge_result.merged_data.columns),
                "processing_info": merge_result.merge_info
            }
            
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"导出处理日志失败: {e}")
            return False


# 测试函数
def test_data_processing():
    """测试数据处理模块"""
    print("测试数据处理模块...")
    
    # 创建测试目录
    test_dir = "test_output"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        from field_mapping import FieldMappingManager
        from header_detection import HeaderDetector
        
        # 创建测试数据
        test_data1 = {
            "账户号码": ["1234567890", "0987654321"],
            "户名": ["张三", "李四"],
            "交易日期": ["2025-01-01", "2025-01-02"],
            "交易金额": [1000.00, -500.00],
            "账户余额": [5000.00, 4500.00]
        }
        
        test_data2 = {
            "账户号码": ["1111111111", "2222222222"],
            "户名": ["王五", "赵六"],
            "交易日期": ["2025-01-03", "2025-01-04"],
            "交易金额": [2000.00, -1000.00],
            "账户余额": [7000.00, 6000.00]
        }
        
        # 创建测试文件
        test_file1 = os.path.join(test_dir, "test1.xlsx")
        test_file2 = os.path.join(test_dir, "test2.xlsx")
        
        pd.DataFrame(test_data1).to_excel(test_file1, index=False)
        pd.DataFrame(test_data2).to_excel(test_file2, index=False)
        
        # 创建字段映射
        field_manager = FieldMappingManager(config_dir=test_dir)
        header_detector = HeaderDetector()
        
        # 添加字段映射
        mappings = [
            FieldMapping("test1.xlsx", "test1.xlsx", "account_number", "账户号码", "direct"),
            FieldMapping("test1.xlsx", "test1.xlsx", "account_name", "户名", "direct"),
            FieldMapping("test1.xlsx", "test1.xlsx", "transaction_date", "交易日期", "direct"),
            FieldMapping("test1.xlsx", "test1.xlsx", "transaction_amount", "交易金额", "direct"),
            FieldMapping("test1.xlsx", "test1.xlsx", "balance", "账户余额", "direct"),
            FieldMapping("test2.xlsx", "test2.xlsx", "account_number", "账户号码", "direct"),
            FieldMapping("test2.xlsx", "test2.xlsx", "account_name", "户名", "direct"),
            FieldMapping("test2.xlsx", "test2.xlsx", "transaction_date", "交易日期", "direct"),
            FieldMapping("test2.xlsx", "test2.xlsx", "transaction_amount", "交易金额", "direct"),
            FieldMapping("test2.xlsx", "test2.xlsx", "balance", "账户余额", "direct")
        ]
        
        for mapping in mappings:
            field_manager.add_field_mapping(mapping)
        
        # 创建数据处理器
        processor = DataProcessor(field_manager, header_detector)
        
        # 测试单文件处理
        print("测试单文件处理...")
        processed_data = processor.process_file(test_file1)
        if processed_data:
            print("✓ 单文件处理成功")
            print(f"  - 处理后的列: {list(processed_data.data.columns)}")
            print(f"  - 数据行数: {len(processed_data.data)}")
        else:
            print("✗ 单文件处理失败")
            return False
        
        # 测试文件合并
        print("测试文件合并...")
        output_file = os.path.join(test_dir, "merged_output.xlsx")
        merge_result = processor.merge_files([test_file1, test_file2], output_file)
        
        if merge_result:
            print("✓ 文件合并成功")
            print(f"  - 合并后记录数: {merge_result.total_records}")
            print(f"  - 处理时间: {merge_result.processing_time:.2f}秒")
        else:
            print("✗ 文件合并失败")
            return False
        
        # 测试数据验证
        print("测试数据验证...")
        is_valid, issues = processor.validate_merged_data(merge_result.merged_data)
        if is_valid:
            print("✓ 数据验证通过")
        else:
            print(f"✗ 数据验证失败: {issues}")
        
        # 测试汇总报告
        print("测试汇总报告...")
        summary = processor.generate_summary_report(merge_result)
        if summary:
            print("✓ 汇总报告生成成功")
            print(f"  - 总记录数: {summary['total_records']}")
            print(f"  - 列数: {len(summary['columns'])}")
        else:
            print("✗ 汇总报告生成失败")
        
        print("数据处理模块测试完成")
        return True
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理测试文件
        try:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
        except Exception as e:
            print(f"清理测试文件失败: {e}")


if __name__ == "__main__":
    test_data_processing()
