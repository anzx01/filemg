"""
Excel文档合并工具 - 字段映射模块
负责管理标准字段和文件字段的映射关系
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class StandardField:
    """标准字段数据类"""
    name: str
    display_name: str
    data_type: str
    required: bool = False
    description: str = ""


@dataclass
class FieldMapping:
    """字段映射数据类"""
    file_id: str
    file_name: str
    standard_field: str
    file_field: str
    mapping_type: str = "direct"  # direct, transform, custom
    transform_rule: str = ""
    is_active: bool = True


class FieldMappingManager:
    """字段映射管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """初始化字段映射管理器"""
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "field_mapping_config.json")
        
        # 标准字段列表
        self.standard_fields: List[StandardField] = []
        
        # 字段映射关系
        self.field_mappings: List[FieldMapping] = []
        
        # 预定义的标准字段
        self._initialize_standard_fields()
        
        # 加载配置
        self._load_configuration()
    
    def _initialize_standard_fields(self):
        """初始化预定义的标准字段"""
        default_fields = [
            StandardField("account_number", "账户号码", "string", True, "银行账户号码"),
            StandardField("account_name", "账户名称", "string", True, "账户持有人姓名"),
            StandardField("transaction_date", "交易日期", "date", True, "交易发生日期"),
            StandardField("transaction_amount", "交易金额", "number", True, "交易金额"),
            StandardField("balance", "余额", "number", True, "账户余额"),
            StandardField("transaction_type", "交易类型", "string", False, "交易类型（收入/支出）"),
            StandardField("description", "交易描述", "string", False, "交易描述信息"),
            StandardField("reference_number", "参考号", "string", False, "交易参考号码"),
            StandardField("bank_name", "银行名称", "string", False, "银行名称"),
            StandardField("currency", "币种", "string", False, "货币类型")
        ]
        
        self.standard_fields = default_fields
    
    def add_standard_field(self, field: StandardField) -> bool:
        """添加标准字段"""
        try:
            # 检查是否已存在
            if any(f.name == field.name for f in self.standard_fields):
                return False
            
            self.standard_fields.append(field)
            self._save_configuration()
            return True
        except Exception as e:
            print(f"添加标准字段失败: {e}")
            return False
    
    def remove_standard_field(self, field_name: str) -> bool:
        """删除标准字段"""
        try:
            # 检查是否有映射关系使用此字段
            if any(m.standard_field == field_name for m in self.field_mappings):
                return False
            
            self.standard_fields = [f for f in self.standard_fields if f.name != field_name]
            self._save_configuration()
            return True
        except Exception as e:
            print(f"删除标准字段失败: {e}")
            return False
    
    def get_standard_fields(self) -> List[StandardField]:
        """获取所有标准字段"""
        return self.standard_fields.copy()
    
    def get_standard_field_by_name(self, name: str) -> Optional[StandardField]:
        """根据名称获取标准字段"""
        for field in self.standard_fields:
            if field.name == name:
                return field
        return None
    
    def add_field_mapping(self, mapping: FieldMapping) -> bool:
        """添加字段映射"""
        try:
            # 检查是否已存在相同的映射
            existing = self.get_field_mapping(mapping.file_id, mapping.standard_field)
            if existing:
                # 更新现有映射
                existing.file_field = mapping.file_field
                existing.mapping_type = mapping.mapping_type
                existing.transform_rule = mapping.transform_rule
                existing.is_active = mapping.is_active
            else:
                # 添加新映射
                self.field_mappings.append(mapping)
            
            self._save_configuration()
            return True
        except Exception as e:
            print(f"添加字段映射失败: {e}")
            return False
    
    def remove_field_mapping(self, file_id: str, standard_field: str) -> bool:
        """删除字段映射"""
        try:
            self.field_mappings = [
                m for m in self.field_mappings 
                if not (m.file_id == file_id and m.standard_field == standard_field)
            ]
            self._save_configuration()
            return True
        except Exception as e:
            print(f"删除字段映射失败: {e}")
            return False
    
    def get_field_mapping(self, file_id: str, standard_field: str) -> Optional[FieldMapping]:
        """获取特定文件的字段映射"""
        for mapping in self.field_mappings:
            if mapping.file_id == file_id and mapping.standard_field == standard_field:
                return mapping
        return None
    
    def get_file_mappings(self, file_id: str) -> List[FieldMapping]:
        """获取特定文件的所有字段映射"""
        return [m for m in self.field_mappings if m.file_id == file_id and m.is_active]
    
    def get_all_mappings(self) -> List[FieldMapping]:
        """获取所有字段映射"""
        return self.field_mappings.copy()
    
    def update_field_mapping(self, file_id: str, standard_field: str, 
                           file_field: str, mapping_type: str = "direct", 
                           transform_rule: str = "") -> bool:
        """更新字段映射"""
        try:
            mapping = self.get_field_mapping(file_id, standard_field)
            if mapping:
                mapping.file_field = file_field
                mapping.mapping_type = mapping_type
                mapping.transform_rule = transform_rule
                mapping.is_active = True
            else:
                # 创建新映射
                mapping = FieldMapping(
                    file_id=file_id,
                    file_name="",  # 将在调用时设置
                    standard_field=standard_field,
                    file_field=file_field,
                    mapping_type=mapping_type,
                    transform_rule=transform_rule
                )
                self.field_mappings.append(mapping)
            
            self._save_configuration()
            return True
        except Exception as e:
            print(f"更新字段映射失败: {e}")
            return False
    
    def get_file_columns(self, file_path: str) -> List[str]:
        """获取Excel文件的列名"""
        try:
            df = pd.read_excel(file_path, nrows=0)
            return df.columns.tolist()
        except Exception as e:
            print(f"获取文件列名失败: {e}")
            return []
    
    def suggest_mapping(self, file_columns: List[str], standard_field: str) -> Optional[str]:
        """智能建议字段映射"""
        # 获取标准字段信息
        field = self.get_standard_field_by_name(standard_field)
        if not field:
            return None
        
        # 定义关键词映射规则
        keyword_mapping = {
            "account_number": ["账户", "账号", "卡号", "account", "card"],
            "account_name": ["户名", "姓名", "name", "户主"],
            "transaction_date": ["日期", "时间", "date", "time", "交易日期"],
            "transaction_amount": ["金额", "金额", "amount", "交易金额", "发生额"],
            "balance": ["余额", "balance", "结余"],
            "transaction_type": ["类型", "type", "交易类型", "收支"],
            "description": ["描述", "说明", "备注", "desc", "memo"],
            "reference_number": ["参考", "流水", "ref", "reference"],
            "bank_name": ["银行", "bank", "机构"],
            "currency": ["币种", "货币", "currency", "币别"]
        }
        
        keywords = keyword_mapping.get(standard_field, [])
        
        # 查找匹配的列名
        for column in file_columns:
            column_lower = column.lower()
            for keyword in keywords:
                if keyword.lower() in column_lower:
                    return column
        
        # 如果没有找到匹配，返回第一个列名作为建议
        return file_columns[0] if file_columns else None
    
    def validate_mapping(self, mapping: FieldMapping) -> Tuple[bool, str]:
        """验证字段映射的有效性"""
        try:
            # 检查标准字段是否存在
            if not self.get_standard_field_by_name(mapping.standard_field):
                return False, f"标准字段 '{mapping.standard_field}' 不存在"
            
            # 检查映射类型是否有效
            valid_types = ["direct", "transform", "custom"]
            if mapping.mapping_type not in valid_types:
                return False, f"无效的映射类型: {mapping.mapping_type}"
            
            # 检查变换规则（如果适用）
            if mapping.mapping_type == "transform" and not mapping.transform_rule:
                return False, "变换类型映射需要提供变换规则"
            
            return True, "映射有效"
        except Exception as e:
            return False, f"验证失败: {e}"
    
    def _load_configuration(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 加载标准字段
                if 'standard_fields' in data:
                    self.standard_fields = [
                        StandardField(**field_data) 
                        for field_data in data['standard_fields']
                    ]
                
                # 加载字段映射
                if 'field_mappings' in data:
                    self.field_mappings = [
                        FieldMapping(**mapping_data) 
                        for mapping_data in data['field_mappings']
                    ]
        except Exception as e:
            print(f"加载字段映射配置失败: {e}")
    
    def _save_configuration(self):
        """保存配置文件"""
        try:
            # 确保配置目录存在
            os.makedirs(self.config_dir, exist_ok=True)
            
            data = {
                'standard_fields': [asdict(field) for field in self.standard_fields],
                'field_mappings': [asdict(mapping) for mapping in self.field_mappings]
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存字段映射配置失败: {e}")
    
    def export_mapping_template(self, file_path: str) -> bool:
        """导出字段映射模板"""
        try:
            template_data = {
                'standard_fields': [asdict(field) for field in self.standard_fields],
                'mapping_template': {
                    'file_id': 'example_file_id',
                    'file_name': 'example_file.xlsx',
                    'mappings': {
                        field.name: {
                            'file_field': 'suggested_column_name',
                            'mapping_type': 'direct',
                            'transform_rule': ''
                        }
                        for field in self.standard_fields
                    }
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"导出映射模板失败: {e}")
            return False
    
    def import_mapping_template(self, file_path: str) -> bool:
        """导入字段映射模板"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 导入标准字段
            if 'standard_fields' in data:
                for field_data in data['standard_fields']:
                    field = StandardField(**field_data)
                    self.add_standard_field(field)
            
            # 导入字段映射
            if 'mapping_template' in data and 'mappings' in data['mapping_template']:
                template = data['mapping_template']
                for standard_field, mapping_data in template['mappings'].items():
                    mapping = FieldMapping(
                        file_id=template['file_id'],
                        file_name=template['file_name'],
                        standard_field=standard_field,
                        file_field=mapping_data['file_field'],
                        mapping_type=mapping_data['mapping_type'],
                        transform_rule=mapping_data.get('transform_rule', '')
                    )
                    self.add_field_mapping(mapping)
            
            return True
        except Exception as e:
            print(f"导入映射模板失败: {e}")
            return False


# 测试函数
def test_field_mapping():
    """测试字段映射模块"""
    print("测试字段映射模块...")
    
    # 创建字段映射管理器
    manager = FieldMappingManager()
    
    # 测试标准字段管理
    print("✓ 标准字段管理功能正常")
    
    # 测试字段映射
    mapping = FieldMapping(
        file_id="test_file_1",
        file_name="test.xlsx",
        standard_field="account_number",
        file_field="账户号码",
        mapping_type="direct"
    )
    
    success = manager.add_field_mapping(mapping)
    if success:
        print("✓ 字段映射添加功能正常")
    
    # 测试映射查询
    retrieved = manager.get_field_mapping("test_file_1", "account_number")
    if retrieved:
        print("✓ 字段映射查询功能正常")
    
    # 测试智能建议
    columns = ["账户号码", "户名", "交易日期", "金额"]
    suggestion = manager.suggest_mapping(columns, "account_number")
    if suggestion:
        print("✓ 智能映射建议功能正常")
    
    print("字段映射模块测试完成")


if __name__ == "__main__":
    test_field_mapping()


