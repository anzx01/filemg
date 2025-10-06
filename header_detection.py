"""
Excel文档合并工具 - 表头识别模块
负责智能识别Excel文件的表头结构和余额列
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re
import os


@dataclass
class HeaderInfo:
    """表头信息数据类"""
    file_path: str
    sheet_name: str
    header_row: int
    data_start_row: int
    columns: List[str]
    balance_columns: List[str]
    confidence: float
    detection_method: str


@dataclass
class ColumnInfo:
    """列信息数据类"""
    name: str
    index: int
    data_type: str
    sample_values: List[str]
    is_balance: bool
    confidence: float


class HeaderDetector:
    """表头识别器"""
    
    def __init__(self):
        """初始化表头识别器"""
        # 余额列关键词
        self.balance_keywords = [
            "余额", "结余", "balance", "结存", "可用余额", "账户余额",
            "当前余额", "余额金额", "账户结余", "资金余额"
        ]
        
        # 日期列关键词
        self.date_keywords = [
            "日期", "时间", "date", "time", "交易日期", "发生日期",
            "记账日期", "业务日期", "处理日期"
        ]
        
        # 金额列关键词
        self.amount_keywords = [
            "金额", "金额", "amount", "交易金额", "发生额", "收支金额",
            "借方金额", "贷方金额", "收入金额", "支出金额"
        ]
        
        # 账户列关键词
        self.account_keywords = [
            "账户", "账号", "account", "卡号", "户名", "账户名称",
            "客户名称", "户主姓名"
        ]
        
        # 表头识别模式
        self.header_patterns = [
            r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}",  # 日期格式
            r"^\d+\.?\d*$",  # 纯数字
            r"^[+-]?\d+\.?\d*$",  # 带符号的数字
        ]
    
    def detect_headers(self, file_path: str, sheet_name: Optional[str] = None) -> List[HeaderInfo]:
        """检测文件中的所有表头"""
        try:
            # 读取Excel文件
            excel_file = pd.ExcelFile(file_path)
            sheet_names = [sheet_name] if sheet_name else excel_file.sheet_names
            
            headers = []
            
            for sheet in sheet_names:
                header_info = self._detect_sheet_header(file_path, sheet)
                if header_info:
                    headers.append(header_info)
            
            return headers
            
        except Exception as e:
            print(f"检测表头失败: {e}")
            return []
    
    def _detect_sheet_header(self, file_path: str, sheet_name: str) -> Optional[HeaderInfo]:
        """检测单个工作表的表头"""
        try:
            # 读取工作表数据
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            
            if df.empty:
                return None
            
            # 寻找表头行
            header_row = self._find_header_row(df)
            if header_row is None:
                return None
            
            # 获取列名
            columns = df.iloc[header_row].astype(str).tolist()
            
            # 识别余额列
            balance_columns = self._identify_balance_columns(columns)
            
            # 计算置信度
            confidence = self._calculate_confidence(df, header_row, columns, balance_columns)
            
            # 确定数据开始行
            data_start_row = header_row + 1
            
            return HeaderInfo(
                file_path=file_path,
                sheet_name=sheet_name,
                header_row=header_row,
                data_start_row=data_start_row,
                columns=columns,
                balance_columns=balance_columns,
                confidence=confidence,
                detection_method="auto"
            )
            
        except Exception as e:
            print(f"检测工作表表头失败: {e}")
            return None
    
    def _find_header_row(self, df: pd.DataFrame) -> Optional[int]:
        """寻找表头行"""
        # 方法1: 寻找包含最多文本的行
        text_scores = []
        for i in range(min(10, len(df))):  # 只检查前10行
            row = df.iloc[i]
            text_count = sum(1 for cell in row if isinstance(cell, str) and cell.strip())
            text_scores.append(text_count)
        
        if text_scores:
            max_text_row = np.argmax(text_scores)
            if text_scores[max_text_row] > 0:
                return max_text_row
        
        # 方法2: 寻找包含关键词的行
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            row_text = " ".join(str(cell) for cell in row if pd.notna(cell))
            
            # 检查是否包含表头关键词
            keyword_count = 0
            for keyword in self.balance_keywords + self.date_keywords + self.amount_keywords + self.account_keywords:
                if keyword in row_text:
                    keyword_count += 1
            
            if keyword_count >= 2:  # 至少包含2个关键词
                return i
        
        # 方法3: 默认使用第一行
        return 0
    
    def _identify_balance_columns(self, columns: List[str]) -> List[str]:
        """识别余额列"""
        balance_columns = []
        
        for col in columns:
            col_lower = str(col).lower()
            
            # 直接匹配关键词
            for keyword in self.balance_keywords:
                if keyword in col_lower:
                    balance_columns.append(col)
                    break
            
            # 模式匹配
            if self._is_balance_pattern(col):
                balance_columns.append(col)
        
        return balance_columns
    
    def _is_balance_pattern(self, column_name: str) -> bool:
        """检查列名是否符合余额模式"""
        col_lower = str(column_name).lower()
        
        # 包含"余额"相关词汇
        balance_indicators = ["余额", "结余", "balance", "结存"]
        for indicator in balance_indicators:
            if indicator in col_lower:
                return True
        
        # 包含"当前"、"可用"等修饰词
        modifiers = ["当前", "可用", "实际", "有效"]
        for modifier in modifiers:
            if modifier in col_lower and any(word in col_lower for word in ["余额", "金额", "资金"]):
                return True
        
        return False
    
    def _calculate_confidence(self, df: pd.DataFrame, header_row: int, 
                            columns: List[str], balance_columns: List[str]) -> float:
        """计算表头识别的置信度"""
        confidence = 0.0
        
        # 基础置信度
        confidence += 0.3
        
        # 列名质量评分
        valid_columns = sum(1 for col in columns if col and str(col).strip())
        if valid_columns > 0:
            confidence += 0.2 * (valid_columns / len(columns))
        
        # 余额列识别评分
        if balance_columns:
            confidence += 0.2
        
        # 数据类型一致性评分
        if header_row + 1 < len(df):
            data_row = df.iloc[header_row + 1]
            numeric_count = sum(1 for cell in data_row if pd.api.types.is_numeric_dtype(type(cell)) or str(cell).replace('.', '').replace('-', '').isdigit())
            if numeric_count > 0:
                confidence += 0.1 * (numeric_count / len(data_row))
        
        # 关键词匹配评分
        all_text = " ".join(str(col) for col in columns)
        keyword_matches = 0
        for keyword in self.balance_keywords + self.date_keywords + self.amount_keywords + self.account_keywords:
            if keyword in all_text:
                keyword_matches += 1
        
        if keyword_matches > 0:
            confidence += 0.2 * min(keyword_matches / 5, 1.0)
        
        return min(confidence, 1.0)
    
    def analyze_column(self, df: pd.DataFrame, column_name: str, start_row: int = 0) -> ColumnInfo:
        """分析单个列的信息"""
        try:
            # 获取列数据
            column_data = df.iloc[start_row:, df.columns.get_loc(column_name)]
            
            # 确定数据类型
            data_type = self._determine_data_type(column_data)
            
            # 获取样本值
            sample_values = column_data.dropna().head(5).astype(str).tolist()
            
            # 判断是否为余额列
            is_balance = self._is_balance_column(column_name, sample_values)
            
            # 计算置信度
            confidence = self._calculate_column_confidence(column_name, sample_values, data_type)
            
            return ColumnInfo(
                name=column_name,
                index=df.columns.get_loc(column_name),
                data_type=data_type,
                sample_values=sample_values,
                is_balance=is_balance,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"分析列信息失败: {e}")
            return ColumnInfo(
                name=column_name,
                index=0,
                data_type="unknown",
                sample_values=[],
                is_balance=False,
                confidence=0.0
            )
    
    def _determine_data_type(self, column_data: pd.Series) -> str:
        """确定列的数据类型"""
        # 检查数值类型
        numeric_count = 0
        for value in column_data.dropna().head(10):
            if pd.api.types.is_numeric_dtype(type(value)):
                numeric_count += 1
            elif str(value).replace('.', '').replace('-', '').replace(',', '').isdigit():
                numeric_count += 1
        
        if numeric_count > len(column_data.dropna().head(10)) * 0.8:
            return "numeric"
        
        # 检查日期类型
        date_count = 0
        for value in column_data.dropna().head(10):
            if pd.api.types.is_datetime64_any_dtype(type(value)):
                date_count += 1
            elif self._is_date_string(str(value)):
                date_count += 1
        
        if date_count > len(column_data.dropna().head(10)) * 0.8:
            return "date"
        
        return "text"
    
    def _is_date_string(self, value: str) -> bool:
        """检查字符串是否为日期格式"""
        date_patterns = [
            r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$",
            r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}$",
            r"^\d{4}\d{2}\d{2}$"
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, value):
                return True
        
        return False
    
    def _is_balance_column(self, column_name: str, sample_values: List[str]) -> bool:
        """判断列是否为余额列"""
        col_lower = str(column_name).lower()
        
        # 检查列名
        for keyword in self.balance_keywords:
            if keyword in col_lower:
                return True
        
        # 检查样本值模式
        if sample_values:
            # 检查是否包含货币符号
            currency_symbols = ["¥", "$", "€", "£", "元"]
            for value in sample_values[:3]:
                if any(symbol in str(value) for symbol in currency_symbols):
                    return True
            
            # 检查数值模式
            numeric_pattern = r"^[+-]?\d+\.?\d*$"
            numeric_count = sum(1 for value in sample_values[:5] if re.match(numeric_pattern, str(value)))
            if numeric_count >= 3:  # 至少3个数值
                return True
        
        return False
    
    def _calculate_column_confidence(self, column_name: str, sample_values: List[str], data_type: str) -> float:
        """计算列识别的置信度"""
        confidence = 0.0
        
        # 列名匹配评分
        col_lower = str(column_name).lower()
        for keyword in self.balance_keywords:
            if keyword in col_lower:
                confidence += 0.4
                break
        
        # 数据类型评分
        if data_type == "numeric":
            confidence += 0.3
        
        # 样本值评分
        if sample_values:
            # 检查数值格式
            numeric_count = 0
            for value in sample_values:
                if re.match(r"^[+-]?\d+\.?\d*$", str(value)):
                    numeric_count += 1
            
            if numeric_count > 0:
                confidence += 0.3 * (numeric_count / len(sample_values))
        
        return min(confidence, 1.0)
    
    def get_balance_columns(self, file_path: str, sheet_name: Optional[str] = None) -> List[str]:
        """获取文件的余额列"""
        headers = self.detect_headers(file_path, sheet_name)
        
        balance_columns = []
        for header in headers:
            balance_columns.extend(header.balance_columns)
        
        return list(set(balance_columns))  # 去重
    
    def validate_header_detection(self, file_path: str, expected_headers: List[str]) -> Tuple[bool, str]:
        """验证表头识别结果"""
        try:
            headers = self.detect_headers(file_path)
            
            if not headers:
                return False, "未检测到表头"
            
            # 检查是否包含期望的表头
            detected_columns = []
            for header in headers:
                detected_columns.extend(header.columns)
            
            missing_headers = [h for h in expected_headers if h not in detected_columns]
            
            if missing_headers:
                return False, f"缺少表头: {missing_headers}"
            
            return True, "表头识别正确"
            
        except Exception as e:
            return False, f"验证失败: {e}"


# 测试函数
def test_header_detection():
    """测试表头识别模块"""
    print("测试表头识别模块...")
    
    # 创建测试目录
    test_dir = "test_output"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # 创建测试Excel文件
        test_data = {
            "账户号码": ["1234567890", "0987654321"],
            "户名": ["张三", "李四"],
            "交易日期": ["2025-01-01", "2025-01-02"],
            "交易金额": [1000.00, -500.00],
            "账户余额": [5000.00, 4500.00],
            "备注": ["收入", "支出"]
        }
        
        test_file = os.path.join(test_dir, "test_header.xlsx")
        df = pd.DataFrame(test_data)
        df.to_excel(test_file, index=False)
        
        # 创建表头识别器
        detector = HeaderDetector()
        
        # 测试表头检测
        headers = detector.detect_headers(test_file)
        if headers:
            print("✓ 表头检测功能正常")
            header = headers[0]
            print(f"  - 检测到表头行: {header.header_row}")
            print(f"  - 列名: {header.columns}")
            print(f"  - 余额列: {header.balance_columns}")
            print(f"  - 置信度: {header.confidence:.2f}")
        else:
            print("✗ 表头检测失败")
        
        # 测试余额列识别
        balance_columns = detector.get_balance_columns(test_file)
        if balance_columns:
            print(f"✓ 余额列识别功能正常: {balance_columns}")
        else:
            print("✗ 余额列识别失败")
        
        # 测试列分析
        if headers:
            column_info = detector.analyze_column(df, "账户余额", header.data_start_row)
            print(f"✓ 列分析功能正常")
            print(f"  - 列名: {column_info.name}")
            print(f"  - 数据类型: {column_info.data_type}")
            print(f"  - 是否余额列: {column_info.is_balance}")
            print(f"  - 置信度: {column_info.confidence:.2f}")
        
        # 测试验证功能
        expected_headers = ["账户号码", "户名", "交易日期", "交易金额", "账户余额"]
        is_valid, message = detector.validate_header_detection(test_file, expected_headers)
        if is_valid:
            print(f"✓ 表头验证功能正常: {message}")
        else:
            print(f"✗ 表头验证失败: {message}")
        
        print("表头识别模块测试完成")
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
    test_header_detection()


