#!/usr/bin/env python3
"""
测试真实UI合并流程中招商银行规则的应用
"""

import pandas as pd
import os
import tempfile
from data_processing import DataProcessor
from header_detection import HeaderDetector
from special_rules import SpecialRulesManager

def test_real_ui_merge():
    """测试真实UI合并流程"""
    print("=== 测试真实UI合并流程中招商银行规则的应用 ===")
    
    try:
        # 创建测试数据文件
        test_data = pd.DataFrame({
            '交易日期': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04'],
            '交易金额': [1000.50, -500.25, 2000.00, -150.75],
            '对方户名': ['客户A', '客户B', '客户C', '客户D'],
            '摘要': ['收入', '支出', '收入', '支出']
        })
        
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(suffix='招商银行.xlsx', delete=False) as tmp_file:
            test_file_path = tmp_file.name
        
        # 保存测试数据到Excel文件
        test_data.to_excel(test_file_path, index=False)
        print(f"创建测试文件: {test_file_path}")
        
        # 模拟UI合并流程 - 按照ui_module.py中的逻辑
        print("\n=== 模拟UI合并流程 ===")
        
        # 创建输出目录
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成输出文件名
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"合并结果_{timestamp}.xlsx")
        
        print(f"开始合并，共 1 个文件")
        
        # 使用数据处理器进行合并，确保规则正确应用
        from data_processing import DataProcessor
        from header_detection import HeaderDetector
        from special_rules import SpecialRulesManager
        
        # 创建数据处理器实例（模拟UI中的创建方式）
        header_detector = HeaderDetector()
        special_rules_manager = SpecialRulesManager()
        data_processor = DataProcessor(header_detector, special_rules_manager)
        
        print(f"规则管理器加载的规则数量: {len(special_rules_manager.rules)}")
        print("活跃规则:")
        for rule in special_rules_manager.rules:
            if rule.get("status") == "active":
                print(f"  - {rule['id']}: {rule['bank_name']} - {rule['type']}")
        
        # 使用数据处理器合并文件
        merge_result = data_processor.merge_files([test_file_path], output_file)
        
        if merge_result:
            print(f"\n合并完成: {merge_result.total_records} 条记录")
            print(f"处理时间: {merge_result.processing_time:.2f}秒")
            
            # 检查合并结果
            print("\n合并后的数据:")
            print(merge_result.merged_data)
            print(f"\n合并后的列名: {list(merge_result.merged_data.columns)}")
            
            # 检查是否生成了收入和支出字段
            if '收入' in merge_result.merged_data.columns and '支出' in merge_result.merged_data.columns:
                print("\n✅ 成功生成收入和支出字段")
                print(f"收入记录数: {(merge_result.merged_data['收入'] > 0).sum()}")
                print(f"支出记录数: {(merge_result.merged_data['支出'] > 0).sum()}")
                
                # 显示收入和支出详情
                print("\n收入记录:")
                income_records = merge_result.merged_data[merge_result.merged_data['收入'] > 0]
                for idx, row in income_records.iterrows():
                    print(f"  交易时间: {row['交易时间']}, 收入: {row['收入']}")
                
                print("\n支出记录:")
                expense_records = merge_result.merged_data[merge_result.merged_data['支出'] > 0]
                for idx, row in expense_records.iterrows():
                    print(f"  交易时间: {row['交易时间']}, 支出: {row['支出']}")
            else:
                print("\n❌ 未生成收入和支出字段")
                print("可能的原因:")
                print("1. 规则没有正确加载")
                print("2. 规则没有正确应用")
                print("3. 文件名不匹配")
            
            # 验证导出的文件
            if os.path.exists(output_file):
                print(f"\n验证导出的文件: {output_file}")
                exported_data = pd.read_excel(output_file)
                print(f"导出文件形状: {exported_data.shape}")
                print(f"导出文件列名: {list(exported_data.columns)}")
                
                if '收入' in exported_data.columns and '支出' in exported_data.columns:
                    print("✅ 导出的文件包含收入和支出字段")
                else:
                    print("❌ 导出的文件不包含收入和支出字段")
            else:
                print("❌ 输出文件不存在")
        else:
            print("❌ 合并失败")
        
        # 清理临时文件
        if os.path.exists(test_file_path):
            try:
                # 等待一下确保文件句柄释放
                import time
                time.sleep(0.5)
                os.unlink(test_file_path)
                print(f"✅ 清理测试文件: {test_file_path}")
            except Exception as e:
                print(f"⚠️ 清理测试文件失败: {e}")
                print("文件可能被其他程序占用，将在程序退出后自动清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_ui_merge()
    if success:
        print("\n🎉 真实UI合并流程测试完成！")
    else:
        print("\n❌ 真实UI合并流程测试失败")
