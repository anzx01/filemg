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

from header_detection import HeaderDetector, HeaderInfo
from special_rules import SpecialRulesManager
from dynamic_rule_parser import DynamicRuleParser


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
    
    def __init__(self, header_detector: HeaderDetector, special_rules_manager: SpecialRulesManager = None, disable_llm: bool = False):
        """初始化数据处理器"""
        self.header_detector = header_detector
        
        # 如果禁用LLM或者special_rules_manager为None，则创建无LLM的特殊规则管理器
        if disable_llm or special_rules_manager is None:
            self.special_rules_manager = SpecialRulesManager(disable_llm=disable_llm)
        else:
            self.special_rules_manager = special_rules_manager
            
        self.rule_parser = DynamicRuleParser()
        
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
    
    def _apply_field_mapping(self, data: pd.DataFrame, file_path: str) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """应用字段映射配置"""
        try:
            import json
            import os
            from resource_manager import ResourceManager
            
            # 使用资源管理器加载字段映射配置
            resource_manager = ResourceManager()
            mapping_config = resource_manager.load_json_config("config/field_mapping_config.json")
            
            # 查找匹配的映射配置，优先使用完整路径匹配
            mappings = None
            
            # 1. 尝试完整路径匹配
            if file_path in mapping_config:
                mappings = mapping_config[file_path]
                print(f"找到完整路径匹配的映射配置: {file_path}")
            
            # 2. 尝试标准化路径匹配
            if not mappings:
                normalized_file_path = os.path.normpath(file_path)
                for config_key in mapping_config.keys():
                    normalized_config = os.path.normpath(config_key)
                    if normalized_config == normalized_file_path:
                        mappings = mapping_config[config_key]
                        print(f"找到标准化路径匹配的映射配置: {config_key}")
                        break
            
            # 3. 尝试文件名匹配（兼容旧配置）
            if not mappings:
                file_name = os.path.basename(file_path)
                for config_key in mapping_config.keys():
                    if file_name in config_key or config_key.endswith(file_name):
                        mappings = mapping_config[config_key]
                        print(f"找到文件名匹配的映射配置: {config_key}")
                        break
            
            if not mappings:
                print(f"未找到字段映射配置: {file_name}")
                return data, {}
            
            # 应用字段映射
            mapped_data = data.copy()
            mapped_columns = {}
            
            for mapping in mappings:
                if mapping.get("is_mapped", False):
                    standard_field = mapping.get("standard_field")
                    imported_column = mapping.get("imported_column")
                    
                    if standard_field and imported_column and imported_column in data.columns:
                        # 检查目标字段是否已经存在（可能由规则生成）
                        if standard_field in mapped_data.columns:
                            print(f"字段 {standard_field} 已存在，跳过映射: {imported_column} -> {standard_field}")
                        else:
                            # 将原始列映射到标准字段
                            mapped_data[standard_field] = data[imported_column]
                            mapped_columns[imported_column] = standard_field
                            print(f"字段映射: {imported_column} -> {standard_field}")
            
            return mapped_data, mapped_columns
            
        except Exception as e:
            print(f"应用字段映射失败: {e}")
            return data, {}
    
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
            
            # 读取数据 - 使用原始数据，不指定header
            df = pd.read_excel(file_path, sheet_name=header.sheet_name, header=None)
            
            # 过滤分页符行
            df = self._filter_page_breaks(df)
            
            # 重新设置表头
            if header.header_row < len(df):
                # 使用表头检测器检测到的列名
                columns = header.columns.copy()
                
                # 处理重复列名
                processed_columns = []
                column_counts = {}
                for col in columns:
                    if pd.isna(col):
                        col_name = f"Unnamed_{len(processed_columns)}"
                    else:
                        col_name = str(col)
                        if col_name in column_counts:
                            column_counts[col_name] += 1
                            col_name = f"{col_name}_{column_counts[col_name]}"
                        else:
                            column_counts[col_name] = 1
                    processed_columns.append(col_name)
                
                df.columns = processed_columns
                df = df.iloc[header.data_start_row:].reset_index(drop=True)
            
            # 清理数据
            df = self._clean_data(df)
            
            # 应用字段映射配置
            mapped_data, mapped_columns = self._apply_field_mapping(df, file_path)
            
            # 识别余额列
            balance_columns = self._identify_balance_columns(mapped_data, header.balance_columns)
            
            # 应用银行规则
            mapped_data = self.apply_bank_rules(mapped_data, file_name)
            
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
        
        # 过滤分页符行
        df = self._filter_page_breaks(df)
        
        # 过滤只有日期的行
        df = self._filter_date_only_rows(df)
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        # 清理字符串数据
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                # 不将空字符串替换为nan，保持为空字符串
                # df[col] = df[col].replace('', np.nan)
        
        # 处理日期格式，去除时间部分
        df = self._format_date_columns(df)
        
        # 过滤重复表头
        df = self._filter_duplicate_headers(df)
        
        return df
    
    def _filter_page_breaks(self, df: pd.DataFrame) -> pd.DataFrame:
        """过滤分页符行"""
        if df.empty:
            return df
        
        # 分页符关键词
        page_break_keywords = [
            "查询编号", "对公往来户明细表", "分页", "第", "页", "共",
            "明细表", "查询", "编号", "页次", "页码"
        ]
        
        # 创建过滤后的DataFrame
        filtered_rows = []
        
        for index, row in df.iterrows():
            # 将行数据转换为字符串并连接
            row_text = " ".join(str(cell) for cell in row if pd.notna(cell))
            
            # 检查是否包含分页符关键词
            is_page_break = False
            for keyword in page_break_keywords:
                if keyword in row_text:
                    is_page_break = True
                    break
            
            # 如果不是分页符行，则保留
            if not is_page_break:
                filtered_rows.append(row)
        
        if filtered_rows:
            return pd.DataFrame(filtered_rows).reset_index(drop=True)
        else:
            return df
    
    def _filter_date_only_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """过滤只有日期没有其他数据的行"""
        if df.empty:
            return df
        
        try:
            # 创建过滤后的DataFrame
            filtered_rows = []
            
            for index, row in df.iterrows():
                # 检查该行是否只有日期数据
                if self._is_date_only_row(row):
                    print(f"过滤只有日期的行 {index}: {row.to_dict()}")
                    continue  # 跳过这行
                else:
                    filtered_rows.append(row)
            
            if filtered_rows:
                return pd.DataFrame(filtered_rows).reset_index(drop=True)
            else:
                return df
                
        except Exception as e:
            print(f"过滤只有日期的行失败: {e}")
            return df
    
    def _is_date_only_row(self, row: pd.Series) -> bool:
        """判断行是否只有日期数据（只要日期列不为空，其他列为空，就不导入）"""
        try:
            # 统计非空值
            non_empty_values = []
            for value in row:
                if pd.notna(value) and str(value).strip() != '':
                    non_empty_values.append(str(value).strip())
            
            # 如果没有非空值，不是日期行
            if len(non_empty_values) == 0:
                return False
            
            # 如果只有一个非空值，检查是否为日期
            if len(non_empty_values) == 1:
                return self._is_date_value(non_empty_values[0]) or self._is_date_like_value(non_empty_values[0])
            
            # 如果有多个非空值，检查是否所有值都是日期相关格式
            date_count = 0
            for value in non_empty_values:
                if self._is_date_value(value) or self._is_date_like_value(value):
                    date_count += 1
            
            # 如果所有非空值都是日期或日期相关格式，则认为是只有日期的行
            return date_count == len(non_empty_values)
            
        except Exception as e:
            print(f"判断日期行失败: {e}")
            return False
    
    def _is_date_value(self, value: str) -> bool:
        """判断值是否为日期格式"""
        try:
            value_str = str(value).strip()
            
            # 如果值太短或太长，不太可能是日期
            if len(value_str) < 4 or len(value_str) > 20:
                return False
            
            # 常见的日期格式模式
            date_patterns = [
                r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}$',  # YYYY-MM-DD, YYYY/MM/DD
                r'^\d{1,2}[-/]\d{1,2}[-/]\d{4}$',  # MM-DD-YYYY, MM/DD/YYYY
                r'^\d{4}\d{2}\d{2}$',              # YYYYMMDD
                r'^\d{2}\d{2}\d{4}$',              # MMDDYYYY
                r'^\d{4}年\d{1,2}月\d{1,2}日$',      # 中文日期格式
                r'^\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2}$',  # 带时间的日期
                r'^\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2}$',   # 带时间的日期
            ]
            
            # 检查是否匹配日期模式
            for pattern in date_patterns:
                if re.match(pattern, value_str):
                    return True
            
            # 尝试用pandas解析日期，但要求更严格
            try:
                parsed_date = pd.to_datetime(value_str)
                # 检查解析后的日期是否合理（在1900-2100年之间）
                if 1900 <= parsed_date.year <= 2100:
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            return False
    
    def _is_date_like_value(self, value: str) -> bool:
        """判断值是否为日期相关格式（更宽松的检测）"""
        try:
            value_str = str(value).strip()
            
            # 如果值太短，不太可能是日期
            if len(value_str) < 2:
                return False
            
            # 检查是否包含日期相关的关键词
            date_keywords = ['年', '月', '日', '-', '/', '日期', '时间']
            if any(keyword in value_str for keyword in date_keywords):
                return True
            
            # 检查是否为纯数字且长度在4-8位之间（可能是日期格式）
            if value_str.isdigit() and 4 <= len(value_str) <= 8:
                return True
            
            # 检查是否包含数字和分隔符的组合
            if re.match(r'^\d+[-/]\d+[-/]?\d*$', value_str):
                return True
            
            return False
            
        except Exception as e:
            return False
    
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
    
    def _detect_balance_columns(self, df: pd.DataFrame) -> List[str]:
        """检测余额列"""
        try:
            # 使用表头检测器检测余额列
            balance_columns = []
            for col in df.columns:
                if self._is_balance_column_name(col):
                    balance_columns.append(col)
            return balance_columns
        except Exception as e:
            print(f"检测余额列失败: {e}")
            return []
    
    def _is_balance_column_name(self, column_name: str) -> bool:
        """判断列名是否为余额列"""
        balance_keywords = ["余额", "结余", "balance", "结存", "可用余额", "账户余额"]
        col_lower = str(column_name).lower()
        
        for keyword in balance_keywords:
            if keyword in col_lower:
                return True
        
        return False
    
    def _format_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """格式化日期列，统一日期格式为YYYY-MM-DD"""
        try:
            # 查找日期相关列
            date_columns = [col for col in df.columns if "日期" in col or "时间" in col or "date" in col.lower()]
            
            for col in date_columns:
                if col in df.columns:
                    # 处理日期格式，统一为YYYY-MM-DD格式
                    df[col] = df[col].apply(self._format_date_value)
            
            return df
        except Exception as e:
            print(f"格式化日期列失败: {e}")
            return df
    
    def _format_date_value(self, value):
        """格式化单个日期值，统一为YYYY-MM-DD格式"""
        try:
            if pd.isna(value) or str(value).strip() == '' or str(value).strip() == 'nan':
                return value
            
            value_str = str(value).strip()
            
            # 尝试解析并统一日期格式
            try:
                # 解析为datetime对象
                if ' ' in value_str:
                    # 包含时间的日期，只取日期部分
                    date_part = value_str.split(' ')[0]
                    dt = pd.to_datetime(date_part)
                else:
                    # 只有日期
                    dt = pd.to_datetime(value_str)
                
                # 统一格式为YYYY-MM-DD
                return dt.strftime('%Y-%m-%d')
                
            except Exception as e:
                # 如果解析失败，尝试其他常见格式
                try:
                    # 尝试常见的日期格式
                    common_formats = [
                        '%Y-%m-%d',
                        '%Y/%m/%d', 
                        '%Y.%m.%d',
                        '%m/%d/%Y',
                        '%d/%m/%Y',
                        '%Y年%m月%d日',
                        '%Y-%m-%d %H:%M:%S',
                        '%Y/%m/%d %H:%M:%S'
                    ]
                    
                    for fmt in common_formats:
                        try:
                            dt = pd.to_datetime(value_str, format=fmt)
                            return dt.strftime('%Y-%m-%d')
                        except:
                            continue
                    
                    # 如果所有格式都失败，返回原值
                    return value_str
                    
                except Exception:
                    return value_str
                
        except Exception:
            return value
    
    def _filter_duplicate_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """过滤重复表头，只保留第一个有效表头"""
        try:
            if df.empty:
                return df
            
            # 表头关键词
            header_keywords = [
                "交易日期", "交易时间", "日期", "时间", "收入", "支出", "余额", 
                "摘要", "对方户名", "交易对手", "金额", "借方", "贷方"
            ]
            
            # 查找可能的表头行
            header_rows = []
            for idx, row in df.iterrows():
                row_str = " ".join(str(cell) for cell in row if pd.notna(cell))
                # 检查是否包含表头关键词
                keyword_count = sum(1 for keyword in header_keywords if keyword in row_str)
                if keyword_count >= 3:  # 包含至少3个表头关键词
                    header_rows.append(idx)
            
            # 如果找到多个表头行，删除除第一个之外的所有表头行
            if len(header_rows) > 1:
                rows_to_remove = header_rows[1:]  # 保留第一个表头，删除其余的
                df = df.drop(rows_to_remove).reset_index(drop=True)
                print(f"删除了 {len(rows_to_remove)} 个重复表头行")
            
            return df
        except Exception as e:
            print(f"过滤重复表头失败: {e}")
            return df
    
    def merge_files(self, file_paths: List[str], output_path: str) -> Optional[MergeResult]:
        """合并多个文件"""
        try:
            start_time = datetime.now()
            
            # 处理所有文件（不应用字段映射，保持原始列名）
            processed_files = []
            for file_path in file_paths:
                processed_data = self._process_file_without_mapping(file_path)
                if processed_data:
                    processed_files.append(processed_data)
            
            if not processed_files:
                print("没有成功处理的文件")
                return None
            
            # 合并数据
            merged_data = self._merge_processed_data(processed_files)
            
            # 先应用字段映射配置，统一列名
            merged_data = self._apply_field_mapping_to_merged_data(merged_data, file_paths)
            
            # 再应用特殊规则（在字段映射之后）
            merged_data = self._apply_special_rules(merged_data, file_paths)
            
            # 最后标准化列名，确保使用标准字段
            merged_data = self._standardize_columns(merged_data)
            
            # 保存合并后的数据，使用FileOperations确保空值处理
            from file_operations import FileOperations
            file_ops = FileOperations()
            success = file_ops.write_excel_file(merged_data, output_path, '合并结果', False)
            
            if not success:
                raise Exception("保存Excel文件失败")
            
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
                    file_data[col] = ""
            
            # 合并数据
            merged_data = pd.concat([merged_data, file_data], ignore_index=True)
        
        # 处理空值，使用更强健的方法
        merged_data = self._clean_nan_values(merged_data)
        
        return merged_data
    
    def _clean_nan_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清理DataFrame中的nan值，使用更强健的方法
        
        Args:
            df: 要清理的DataFrame
            
        Returns:
            清理后的DataFrame
        """
        try:
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
    
    def _apply_special_rules(self, data: pd.DataFrame, file_paths: List[str]) -> pd.DataFrame:
        """应用特殊规则到合并后的数据"""
        try:
            print(f"开始应用特殊规则，数据形状: {data.shape}")
            print(f"文件路径: {file_paths}")
            
            if not self.special_rules_manager:
                print("特殊规则管理器未初始化")
                return data
            
            # 获取所有活跃规则
            rules = self.special_rules_manager.get_rules()
            print(f"所有规则数量: {len(rules)}")
            for rule in rules:
                print(f"规则: {rule.get('id')}, 银行: {rule.get('bank_name')}, 状态: {rule.get('status')}")
            
            active_rules = [rule for rule in rules if rule.get("status") == "active"]
            
            if not active_rules:
                print("没有活跃的特殊规则")
                return data
            
            print(f"找到 {len(active_rules)} 个活跃规则")
            
            # 按银行分组应用规则，每个银行的所有规则一起应用
            result_data = data.copy()
            
            # 按银行分组规则
            bank_rules = {}
            for rule in active_rules:
                bank_name = rule.get("bank_name")
                if bank_name:
                    if bank_name not in bank_rules:
                        bank_rules[bank_name] = []
                    bank_rules[bank_name].append(rule)
                else:
                    # 通用规则
                    if "通用" not in bank_rules:
                        bank_rules["通用"] = []
                    bank_rules["通用"].append(rule)
            
            print(f"银行规则分组: {list(bank_rules.keys())}")
            
            # 按银行应用规则
            for bank_name, rules in bank_rules.items():
                if bank_name == "通用":
                    # 应用通用规则到所有数据
                    print(f"应用通用规则: {[rule['id'] for rule in rules]}")
                    result_data = self.special_rules_manager.apply_rules(
                        result_data, None, [rule["id"] for rule in rules]
                    )
                else:
                    print(f"检查银行规则: {bank_name}")
                    print(f"文件路径列表: {file_paths}")
                    # 检查是否有该银行的文件 - 使用更灵活的匹配逻辑
                    bank_files = []
                    for fp in file_paths:
                        file_name = os.path.basename(fp)
                        # 完全匹配
                        if bank_name in file_name:
                            bank_files.append(fp)
                        # 部分匹配 - 针对浦发银行
                        elif bank_name == "浦发银行" and ("浦发" in file_name or "pufa" in file_name.lower()):
                            bank_files.append(fp)
                        # 部分匹配 - 针对其他银行
                        elif bank_name == "工商银行" and ("工商" in file_name or "icbc" in file_name.lower()):
                            bank_files.append(fp)
                        elif bank_name == "华夏银行" and ("华夏" in file_name or "hx" in file_name.lower()):
                            bank_files.append(fp)
                        elif bank_name == "长安银行" and ("长安" in file_name or "ca" in file_name.lower()):
                            bank_files.append(fp)
                        elif bank_name == "招商银行" and ("招商" in file_name or "cmb" in file_name.lower()):
                            bank_files.append(fp)
                        elif bank_name == "北京银行" and ("北京" in file_name or "boc" in file_name.lower()):
                            bank_files.append(fp)
                    print(f"匹配的文件: {bank_files}")
                    
                    if bank_files:
                        print(f"找到 {bank_name} 文件: {bank_files}")
                        print(f"应用规则: {[rule['id'] for rule in rules]}")
                        
                        # 只处理该银行的数据行
                        bank_file_names = [os.path.basename(fp) for fp in bank_files]
                        bank_mask = result_data['source_file'].isin(bank_file_names)
                        bank_data = result_data[bank_mask].copy()
                        
                        if not bank_data.empty:
                            # 应用该银行的所有规则到银行数据
                            processed_bank_data = self.special_rules_manager.apply_rules(
                                bank_data, bank_name, [rule["id"] for rule in rules]
                            )
                            
                            # 将处理后的数据更新回原数据
                            # 首先确保所有列都存在
                            for col in processed_bank_data.columns:
                                if col not in result_data.columns:
                                    result_data[col] = ""
                            
                            # 然后更新数据
                            result_data.loc[bank_mask, processed_bank_data.columns] = processed_bank_data
                            print(f"已应用 {bank_name} 规则，处理了 {len(bank_data)} 条记录")
                            print(f"规则生成的字段: {[col for col in processed_bank_data.columns if col not in bank_data.columns]}")
                        else:
                            print(f"未找到 {bank_name} 的数据行")
                    else:
                        print(f"未找到 {bank_name} 文件")
            
            return result_data
            
        except Exception as e:
            print(f"应用特殊规则失败: {e}")
            return data
    
    def apply_bank_rules(self, data: pd.DataFrame, file_name: str) -> pd.DataFrame:
        """应用银行特定规则到数据"""
        try:
            # 重新加载规则以确保获取最新配置
            self.rule_parser.reload_rules()
            
            # 获取银行规则
            bank_rule = self.rule_parser.get_bank_rule_by_file(file_name)
            
            if not bank_rule:
                return data
            
            processed_data = data.copy()
            
            # 根据规则类型应用不同的处理逻辑
            rule_type = bank_rule.get("type")
            parameters = bank_rule.get("parameters", {})
            
            if rule_type == "date_range_processing":
                processed_data = self._apply_beijing_bank_rule(processed_data, parameters)
            elif rule_type == "balance_processing":
                # 根据银行名称选择不同的处理逻辑
                if "浦发银行" in file_name or "兴业银行" in file_name:
                    processed_data = self._apply_spdb_cib_bank_rule(processed_data, parameters)
                else:
                    processed_data = self._apply_icbc_hx_bank_rule(processed_data, parameters)
            elif rule_type == "debit_credit_processing":
                # 使用动态规则解析器应用借贷标志处理规则
                processed_data = self.rule_parser.apply_rule(processed_data, bank_rule)
            elif rule_type == "income_expense_processing":
                processed_data = self._apply_ca_bank_rule(processed_data, parameters)
            elif rule_type == "sign_processing":
                processed_data = self._apply_cmb_bank_rule(processed_data, parameters)
            elif rule_type == "field_mapping":
                # 使用动态规则解析器应用字段映射规则
                processed_data = self.rule_parser.apply_rule(processed_data, bank_rule)
            
            return processed_data
            
        except Exception as e:
            print(f"应用银行规则失败: {str(e)}")
            return data
    
    def apply_icbc_rules(self, data: pd.DataFrame) -> pd.DataFrame:
        """应用工商银行特定规则到数据"""
        try:
            # 工商银行规则参数
            parameters = {
                "source_field": "借贷标志字段",
                "target_field": "收入或支出", 
                "amount_field": "发生额"
            }
            
            # 应用工商银行/华夏银行借贷标志处理规则
            processed_data = self._apply_icbc_hx_bank_rule(data, parameters)
            
            return processed_data
            
        except Exception as e:
            print(f"应用工商银行规则失败: {str(e)}")
            return data
    
    def _apply_beijing_bank_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用北京银行日期范围处理规则"""
        try:
            source_row = parameters.get("source_row", 2)
            target_field = parameters.get("target_field", "交易日期")
            
            if len(data) >= source_row:
                # 获取第二行的日期信息
                date_info = data.iloc[source_row - 1]  # 第二行（索引为1）
                
                # 查找日期相关列
                date_columns = [col for col in data.columns if "日期" in col or "date" in col.lower()]
                
                if date_columns:
                    # 将日期信息应用到所有行
                    for col in date_columns:
                        if pd.notna(date_info.get(col)):
                            data[target_field] = date_info[col]
                            break
            
            # 过滤掉日期字段不为空但其他字段为空的记录
            if len(data) > 0:
                # 获取所有列名
                all_columns = data.columns.tolist()
                
                # 找到日期相关的列（可能包含"日期"、"时间"、"date"等关键词）
                date_columns = [col for col in all_columns if any(keyword in col.lower() for keyword in ['日期', '时间', 'date', 'time'])]
                
                if date_columns:
                    # 创建过滤条件：日期字段不为空 且 其他字段都为空
                    date_not_empty = data[date_columns].notna().any(axis=1)  # 任一日期字段不为空
                    other_columns = [col for col in all_columns if col not in date_columns]
                    
                    if other_columns:
                        other_all_empty = data[other_columns].isna().all(axis=1)  # 其他字段都为空
                        # 过滤掉日期不为空但其他字段都为空的行
                        filter_condition = ~(date_not_empty & other_all_empty)
                        data = data[filter_condition]
                        filtered_count = (~filter_condition).sum()
                        if filtered_count > 0:
                            print(f"北京银行数据已过滤掉{filtered_count}行日期不为空但其他字段为空的记录")
            
            return data
        except Exception as e:
            print(f"应用北京银行规则失败: {str(e)}")
            return data
    
    def _apply_icbc_hx_bank_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用工商银行/华夏银行借贷标志处理规则"""
        try:
            source_field = parameters.get("source_field", "借贷标志字段")
            target_field = parameters.get("target_field", "收入或支出")
            amount_field = parameters.get("amount_field", "发生额")
            
            # 查找借贷标志列
            balance_columns = [col for col in data.columns if "借贷" in col or "标志" in col]
            amount_columns = [col for col in data.columns if "发生" in col or "金额" in col]
            
            if balance_columns and amount_columns:
                balance_col = balance_columns[0]
                amount_col = amount_columns[0]
                
                # 根据借贷标志处理收入支出
                def process_income(row):
                    balance_flag = str(row[balance_col]).strip()
                    amount = float(row[amount_col]) if pd.notna(row[amount_col]) else 0
                    
                    if "贷" in balance_flag:
                        return abs(amount)  # 收入为正数
                    else:
                        return 0  # 非收入为0
                
                def process_expense(row):
                    balance_flag = str(row[balance_col]).strip()
                    amount = float(row[amount_col]) if pd.notna(row[amount_col]) else 0
                    
                    if "借" in balance_flag:
                        return abs(amount)  # 支出为正数
                    else:
                        return 0  # 非支出为0
                
                # 创建收入和支出两个字段
                data["收入"] = data.apply(process_income, axis=1)
                data["支出"] = data.apply(process_expense, axis=1)
                
                # 删除原始的借贷标志和发生额列
                if balance_col in data.columns:
                    data = data.drop(columns=[balance_col])
                if amount_col in data.columns:
                    data = data.drop(columns=[amount_col])
            
            return data
        except Exception as e:
            print(f"应用工商银行/华夏银行规则失败: {str(e)}")
            return data
    
    def _apply_ca_bank_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用长安银行借/贷字段处理规则"""
        try:
            source_field = parameters.get("source_field", "借/贷字段")
            target_field = parameters.get("target_field", "收入或支出")
            amount_field = parameters.get("amount_field", "交易金额")
            
            # 查找借/贷字段列
            balance_columns = [col for col in data.columns if "借" in col and "贷" in col]
            # 查找可用的金额字段
            amount_fields = ["交易金额", "交昜金额"]
            amount_columns = []
            for field in amount_fields:
                if field in data.columns:
                    amount_columns.append(field)
            
            if balance_columns and amount_columns:
                balance_col = balance_columns[0]
                amount_col = amount_columns[0]
                
                # 先清理表头行 - 删除包含"借/贷"或"交易金额"的行
                print("应用长安银行特殊规则...")
                
                # 查找并删除表头行
                header_rows = []
                for idx, row in data.iterrows():
                    balance_flag = str(row[balance_col]).strip()
                    amount_str = str(row[amount_col]).strip()
                    
                    # 如果借/贷字段或交易金额字段包含表头文本，标记为表头行
                    if (balance_flag == "借/贷" or balance_flag == "交易金额" or 
                        amount_str == "交易金额" or amount_str == "借/贷"):
                        header_rows.append(idx)
                
                if header_rows:
                    print(f"发现表头行 {len(header_rows)} 个，删除中...")
                    data = data.drop(header_rows).reset_index(drop=True)
                
                # 根据借/贷字段处理收入支出
                def process_income(row):
                    try:
                        balance_flag = str(row[balance_col]).strip()
                        amount_str = str(row[amount_col]).strip()
                        
                        # 跳过空值和无效值
                        if (amount_str == "" or amount_str == "nan" or amount_str == "None" or
                            balance_flag == "" or balance_flag == "nan" or balance_flag == "None"):
                            return 0
                        
                        amount = float(amount_str)
                        
                        if "贷" in balance_flag:
                            return abs(amount)  # 收入为正数
                        else:
                            return 0  # 非收入为0
                    except (ValueError, TypeError) as e:
                        return 0
                
                def process_expense(row):
                    try:
                        balance_flag = str(row[balance_col]).strip()
                        amount_str = str(row[amount_col]).strip()
                        
                        # 跳过空值和无效值
                        if (amount_str == "" or amount_str == "nan" or amount_str == "None" or
                            balance_flag == "" or balance_flag == "nan" or balance_flag == "None"):
                            return 0
                        
                        amount = float(amount_str)
                        
                        if "借" in balance_flag:
                            return abs(amount)  # 支出为正数
                        else:
                            return 0  # 非支出为0
                    except (ValueError, TypeError) as e:
                        return 0
                
                # 创建收入和支出两个字段
                data["收入"] = data.apply(process_income, axis=1)
                data["支出"] = data.apply(process_expense, axis=1)
                
                # 统计收入支出记录数
                income_count = (data["收入"] > 0).sum()
                expense_count = (data["支出"] > 0).sum()
                print(f"长安银行规则应用完成，收入记录数: {income_count}, 支出记录数: {expense_count}")
            
            return data
        except Exception as e:
            print(f"应用长安银行规则失败: {str(e)}")
            return data
    
    def _apply_cmb_bank_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用招商银行正负号处理规则"""
        try:
            source_field = parameters.get("source_field", "交易金额")
            source_fields = parameters.get("source_fields", [])
            
            # 支持多个字段候选
            field_candidates = source_fields if source_fields else [source_field]
            
            # 查找金额列，优先精确匹配，然后模糊匹配
            amount_col = None
            
            # 1. 精确匹配
            for candidate in field_candidates:
                if candidate in data.columns:
                    amount_col = candidate
                    break
            
            # 2. 模糊匹配（包含关键词）
            if not amount_col:
                for candidate in field_candidates:
                    matching_cols = [col for col in data.columns if candidate in col]
                    if matching_cols:
                        amount_col = matching_cols[0]
                        break
            
            # 3. 通用匹配（包含"交易"和"金额"或"交昜"和"金额"）
            if not amount_col:
                amount_columns = [col for col in data.columns if ("交易" in col or "交昜" in col) and "金额" in col]
                if amount_columns:
                    amount_col = amount_columns[0]
            
            if amount_col:
                
                print("应用招商银行特殊规则...")
                
                # 根据正负号处理收入支出
                def process_income(row):
                    try:
                        amount_str = str(row[amount_col]).strip()
                        
                        # 跳过空值和无效值
                        if amount_str == "" or amount_str == "nan" or amount_str == "None":
                            return 0
                        
                        amount = float(amount_str)
                        
                        if amount > 0:
                            return abs(amount)  # 正数为收入
                        else:
                            return 0  # 非收入为0
                    except (ValueError, TypeError) as e:
                        return 0
                
                def process_expense(row):
                    try:
                        amount_str = str(row[amount_col]).strip()
                        
                        # 跳过空值和无效值
                        if amount_str == "" or amount_str == "nan" or amount_str == "None":
                            return 0
                        
                        amount = float(amount_str)
                        
                        if amount < 0:
                            return abs(amount)  # 负数为支出
                        else:
                            return 0  # 非支出为0
                    except (ValueError, TypeError) as e:
                        return 0
                
                # 创建收入和支出两个字段
                data["收入"] = data.apply(process_income, axis=1)
                data["支出"] = data.apply(process_expense, axis=1)
                
                # 统计收入支出记录数
                income_count = (data["收入"] > 0).sum()
                expense_count = (data["支出"] > 0).sum()
                print(f"招商银行规则应用完成，收入记录数: {income_count}, 支出记录数: {expense_count}")
            
            return data
        except Exception as e:
            print(f"应用招商银行规则失败: {str(e)}")
            return data
    
    def _apply_spdb_cib_bank_rule(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        """应用浦发银行/兴业银行借方贷方金额处理规则"""
        try:
            # 查找借方金额和贷方金额列
            debit_columns = [col for col in data.columns if "借方" in col and "金额" in col]
            credit_columns = [col for col in data.columns if "贷方" in col and "金额" in col]
            
            if debit_columns and credit_columns:
                debit_col = debit_columns[0]
                credit_col = credit_columns[0]
                
                # 处理收入列（贷方金额）
                def process_income(row):
                    credit_amount = row[credit_col]
                    if pd.notna(credit_amount) and str(credit_amount).strip() != '':
                        try:
                            return float(credit_amount)
                        except (ValueError, TypeError):
                            return None  # 保持空值，不填充nan
                    return None  # 保持空值，不填充nan
                
                # 处理支出列（借方金额）
                def process_expense(row):
                    debit_amount = row[debit_col]
                    if pd.notna(debit_amount) and str(debit_amount).strip() != '':
                        try:
                            return float(debit_amount)
                        except (ValueError, TypeError):
                            return None  # 保持空值，不填充nan
                    return None  # 保持空值，不填充nan
                
                # 创建收入和支出两个字段，保持空值不填充nan
                data["收入"] = data.apply(process_income, axis=1)
                data["支出"] = data.apply(process_expense, axis=1)
                
                # 不删除原始的借方金额和贷方金额列，保持字段映射的兼容性
            
            return data
        except Exception as e:
            print(f"应用浦发银行/兴业银行规则失败: {str(e)}")
            return data

    def _process_file_without_mapping(self, file_path: str, sheet_name: Optional[str] = None) -> Optional[ProcessedData]:
        """处理单个文件，不应用字段映射（保持原始列名）"""
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
            
            # 读取数据 - 使用原始数据，不指定header
            df = pd.read_excel(file_path, sheet_name=header.sheet_name, header=None)
            
            # 过滤分页符行
            df = self._filter_page_breaks(df)
            
            # 重新设置表头
            if header.header_row < len(df):
                # 使用表头检测器检测到的列名
                columns = header.columns.copy()
                
                # 处理重复列名
                processed_columns = []
                column_counts = {}
                for col in columns:
                    if pd.isna(col):
                        col_name = f"Unnamed_{len(processed_columns)}"
                    else:
                        col_name = str(col).strip()
                        if col_name in column_counts:
                            column_counts[col_name] += 1
                            col_name = f"{col_name}_{column_counts[col_name]}"
                        else:
                            column_counts[col_name] = 0
                    processed_columns.append(col_name)
                
                # 设置列名
                df.columns = processed_columns
                
                # 删除表头行
                df = df.iloc[header.header_row + 1:].reset_index(drop=True)
            else:
                print(f"表头行超出数据范围: {file_path}")
                return None
            
            # 清理数据
            df = self._clean_data(df)
            
            # 检测余额列
            balance_columns = self._detect_balance_columns(df)
            
            # 创建处理信息
            processing_info = {
                "header_row": header.header_row,
                "detected_columns": header.columns,
                "balance_columns": balance_columns,
                "processing_time": datetime.now().isoformat()
            }
            
            return ProcessedData(
                file_id=file_id,
                file_name=file_name,
                sheet_name=header.sheet_name,
                data=df,
                mapped_columns={},  # 不应用字段映射
                balance_columns=balance_columns,
                processing_info=processing_info
            )
            
        except Exception as e:
            print(f"处理文件失败 {file_path}: {e}")
            return None

    def _apply_field_mapping_to_merged_data(self, data: pd.DataFrame, file_paths: List[str]) -> pd.DataFrame:
        """对合并后的数据应用字段映射配置，基于文件名匹配"""
        try:
            import json
            import os
            from resource_manager import ResourceManager
            
            # 使用资源管理器加载字段映射配置
            resource_manager = ResourceManager()
            mapping_config = resource_manager.load_json_config("config/field_mapping_config.json")
            
            if not mapping_config:
                print("未找到字段映射配置")
                return data
            
            print("配置文件加载成功: config/field_mapping_config.json")
            
            # 保留现有数据，只添加缺失的标准字段
            mapped_data = data.copy()
            standard_columns = ['source_file']  # 保留源文件列
            
            # 基于文件名匹配应用字段映射配置
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                print(f"处理文件: {file_name}")
                
                # 查找匹配的映射配置
                mappings = None
                
                # 1. 尝试完整路径匹配
                if file_path in mapping_config:
                    mappings = mapping_config[file_path]
                    print(f"找到完整路径匹配的映射配置: {file_path}")
                
                # 2. 尝试标准化路径匹配
                if not mappings:
                    normalized_file_path = os.path.normpath(file_path)
                    for config_key in mapping_config.keys():
                        normalized_config = os.path.normpath(config_key)
                        if normalized_config == normalized_file_path:
                            mappings = mapping_config[config_key]
                            print(f"找到标准化路径匹配的映射配置: {config_key}")
                            break
                
                # 3. 尝试文件名匹配
                if not mappings:
                    for config_key in mapping_config.keys():
                        if file_name in config_key or config_key.endswith(file_name):
                            mappings = mapping_config[config_key]
                            print(f"找到文件名匹配的映射配置: {config_key}")
                            break
                
                if not mappings:
                    print(f"未找到字段映射配置: {file_name}")
                    continue
                
                # 应用字段映射到匹配的数据行
                file_data_mask = mapped_data['source_file'] == file_name
                if not file_data_mask.any():
                    print(f"未找到文件 {file_name} 的数据行")
                    continue
                
                print(f"应用字段映射配置到文件: {file_name}")
                
                for mapping in mappings:
                    if mapping.get("is_mapped", False):
                        standard_field = mapping.get("standard_field")
                        imported_column = mapping.get("imported_column")
                        
                        if standard_field and imported_column:
                            # 检查imported_column是否存在，如果不存在则跳过映射
                            if imported_column not in data.columns:
                                print(f"字段映射跳过: {imported_column} 不存在于数据中，跳过映射: {imported_column} -> {standard_field}")
                                continue
                            
                            # 检查目标字段是否已经存在（可能由规则生成）
                            if standard_field not in mapped_data.columns:
                                # 创建新列并映射数据
                                mapped_data[standard_field] = ""
                                mapped_data.loc[file_data_mask, standard_field] = mapped_data.loc[file_data_mask, imported_column]
                                print(f"字段映射: {imported_column} -> {standard_field}")
                            else:
                                # 字段已存在，检查是否由规则生成（非空值）
                                existing_values = mapped_data.loc[file_data_mask, standard_field]
                                if existing_values.notna().any() and (existing_values != "").any():
                                    print(f"字段 {standard_field} 已由规则生成，跳过映射: {imported_column} -> {standard_field}")
                                else:
                                    # 字段为空，可以映射
                                    mapped_data.loc[file_data_mask, standard_field] = mapped_data.loc[file_data_mask, imported_column]
                                    print(f"字段映射: {imported_column} -> {standard_field}")
                            
                            if standard_field not in standard_columns:
                                standard_columns.append(standard_field)
            
            # 确保所有标准字段都存在，缺失的用空值填充
            for col in standard_columns:
                if col not in mapped_data.columns:
                    mapped_data[col] = ""
            
            # 特别处理：如果对方户名字段在原始数据中存在但在mapped_data中不存在，
            # 说明它是由规则生成的，需要从原始数据中复制过来
            print(f"检查对方户名字段: 原始数据中有{'对方户名' in data.columns}, mapped_data中有{'对方户名' in mapped_data.columns}")
            if '对方户名' in data.columns and '对方户名' not in mapped_data.columns:
                mapped_data['对方户名'] = data['对方户名']
                print(f"从原始数据中恢复规则生成的对方户名字段")
                print(f"恢复后的mapped_data字段: {list(mapped_data.columns)}")
            
            # 特别处理规则生成的字段，确保它们被保留
            rule_generated_fields = ['收入', '支出', '对方户名']  # 规则可能生成的字段
            for field in rule_generated_fields:
                if field in mapped_data.columns and field not in standard_columns:
                    standard_columns.append(field)
            
            # 只保留标准字段，不包含原始字段
            all_columns = []
            
            # 定义标准字段列表（按照字段映射配置中的标准字段）
            standard_field_list = ['交易时间', '收入', '支出', '余额', '摘要', '对方行名', '对方户名', '借贷标志', '发生额', '对方行号']
            
            # 只添加标准字段
            for col in standard_field_list:
                if col in mapped_data.columns:
                    all_columns.append(col)
            
            # 最后添加源文件列
            all_columns.append('source_file')
            
            # 创建只包含标准字段的最终数据框
            final_data = mapped_data[all_columns].copy()
            
            print(f"字段映射完成，最终字段: {[col for col in all_columns if col != 'source_file']}")
            print(f"mapped_data中的字段: {list(mapped_data.columns)}")
            print(f"对方户名字段是否在mapped_data中: {'对方户名' in mapped_data.columns}")
            return final_data
            
        except Exception as e:
            print(f"应用字段映射失败: {e}")
            return data

    def _standardize_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """标准化列名，确保使用标准字段"""
        try:
            # 定义标准字段映射
            standard_fields = {
                '交易时间': ['交易日期', '交易时间', '日期'],
                '收入': ['收入'],
                '支出': ['支出'],
                '余额': ['余额', '账户余额', '联机余额'],
                '摘要': ['摘要', '文字摘要', '备注'],
                '对方户名': ['对方户名', '对手名称', '户名']
            }
            
            # 创建标准化后的数据框
            standardized_data = data.copy()
            
            # 为每个标准字段查找对应的列
            for standard_field, possible_columns in standard_fields.items():
                if standard_field not in standardized_data.columns:
                    # 查找可能的列名
                    for col in possible_columns:
                        if col in standardized_data.columns:
                            standardized_data[standard_field] = standardized_data[col]
                            print(f"标准化字段: {col} -> {standard_field}")
                            break
            
            # 保留source_file列
            if 'source_file' not in standardized_data.columns:
                standardized_data['source_file'] = ''
            
            # 只保留标准字段和source_file列
            final_columns = ['交易时间', '收入', '支出', '余额', '摘要', '对方户名', 'source_file']
            available_columns = [col for col in final_columns if col in standardized_data.columns]
            
            return standardized_data[available_columns]
            
        except Exception as e:
            print(f"标准化列名失败: {e}")
            return data


# 测试函数
def test_data_processing():
    """测试数据处理模块"""
    print("测试数据处理模块...")
    
    # 创建测试目录
    test_dir = "test_output"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
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
        
        # 创建数据处理器
        header_detector = HeaderDetector()
        processor = DataProcessor(header_detector)
        
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
    
if __name__ == "__main__":
    test_data_processing()
