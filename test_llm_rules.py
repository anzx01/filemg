"""
LLM规则功能测试脚本

该脚本用于测试基于DeepSeek API的自然语言规则解析功能。

作者: AI助手
创建时间: 2025-01-27
"""

import os
import sys
import json
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_api import DeepSeekAPI, RuleLLMParser
from special_rules import SpecialRulesManager
from special_rules_ui import SpecialRulesUI


def test_api_connection():
    """测试API连接"""
    print("=" * 50)
    print("测试DeepSeek API连接")
    print("=" * 50)
    
    try:
        api = DeepSeekAPI()
        if api.test_connection():
            print("✅ API连接成功")
            return True
        else:
            print("❌ API连接失败")
            return False
    except Exception as e:
        print(f"❌ API初始化失败: {str(e)}")
        return False


def test_rule_parsing():
    """测试规则解析"""
    print("\n" + "=" * 50)
    print("测试规则解析功能")
    print("=" * 50)
    
    parser = RuleLLMParser()
    
    test_rules = [
        {
            "description": "北京银行日期范围从2024-01-01至2024-12-31",
            "bank_name": "北京银行"
        },
        {
            "description": "工商银行余额增加1000元",
            "bank_name": "工商银行"
        },
        {
            "description": "华夏银行收支分类：收入5000元",
            "bank_name": "华夏银行"
        },
        {
            "description": "长安银行分页符每1000行",
            "bank_name": "长安银行"
        },
        {
            "description": "招商银行根据交易金额正负号分类收支",
            "bank_name": "招商银行"
        }
    ]
    
    success_count = 0
    
    for i, rule_info in enumerate(test_rules, 1):
        print(f"\n测试规则 {i}: {rule_info['description']}")
        print("-" * 30)
        
        try:
            result = parser.parse_natural_language_rule(
                rule_info['description'], 
                rule_info['bank_name']
            )
            
            if result.get("success"):
                print(f"✅ 解析成功")
                print(f"   规则ID: {result.get('id')}")
                print(f"   规则类型: {result.get('type')}")
                print(f"   银行名称: {result.get('bank_name')}")
                print(f"   参数: {json.dumps(result.get('parameters', {}), ensure_ascii=False, indent=2)}")
                success_count += 1
            else:
                print(f"❌ 解析失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 解析异常: {str(e)}")
    
    print(f"\n解析结果: {success_count}/{len(test_rules)} 成功")
    return success_count == len(test_rules)


def test_rules_manager():
    """测试规则管理器"""
    print("\n" + "=" * 50)
    print("测试规则管理器功能")
    print("=" * 50)
    
    try:
        manager = SpecialRulesManager()
        
        # 测试添加LLM规则
        print("测试添加LLM规则...")
        result = manager.add_llm_rule(
            "建设银行字段映射：将'交易日期'映射到'日期'字段",
            "建设银行"
        )
        
        if result["success"]:
            print("✅ LLM规则添加成功")
            print(f"   规则ID: {result['rule']['id']}")
            print(f"   规则类型: {result['rule']['type']}")
        else:
            print(f"❌ LLM规则添加失败: {result['error']}")
        
        # 测试获取规则
        print("\n测试获取规则...")
        rules = manager.get_rules()
        print(f"✅ 当前规则数量: {len(rules)}")
        
        # 测试规则统计
        print("\n测试规则统计...")
        stats = manager.get_rule_statistics()
        print(f"✅ 总规则数: {stats['total_rules']}")
        print(f"✅ 活跃规则数: {stats['active_rules']}")
        print(f"✅ 银行统计: {stats['bank_statistics']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 规则管理器测试失败: {str(e)}")
        return False


def test_ui_components():
    """测试UI组件"""
    print("\n" + "=" * 50)
    print("测试UI组件")
    print("=" * 50)
    
    try:
        # 测试UI初始化
        print("测试UI初始化...")
        ui = SpecialRulesUI()
        print("✅ UI初始化成功")
        
        # 测试模板加载
        print("\n测试模板加载...")
        ui.load_template("beijing_date")
        template_content = ui.desc_text.get(1.0, tk.END).strip()
        if template_content:
            print("✅ 模板加载成功")
            print(f"   模板内容: {template_content[:50]}...")
        else:
            print("❌ 模板加载失败")
        
        # 测试表单清空
        print("\n测试表单清空...")
        ui.clear_form()
        print("✅ 表单清空成功")
        
        return True
        
    except Exception as e:
        print(f"❌ UI组件测试失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("🤖 LLM规则功能测试开始")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查配置文件
    if not os.path.exists("config.env"):
        print("❌ 未找到config.env文件，请先配置API密钥")
        return False
    
    # 读取API密钥
    with open("config.env", "r", encoding="utf-8") as f:
        content = f.read()
        if "your_deepseek_api_key_here" in content:
            print("⚠️  请在config.env文件中设置正确的DEEPSEEK_API_KEY")
            return False
    
    test_results = []
    
    # 测试API连接
    test_results.append(("API连接", test_api_connection()))
    
    # 测试规则解析
    test_results.append(("规则解析", test_rule_parsing()))
    
    # 测试规则管理器
    test_results.append(("规则管理器", test_rules_manager()))
    
    # 测试UI组件
    test_results.append(("UI组件", test_ui_components()))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{len(test_results)} 通过")
    
    if passed == len(test_results):
        print("🎉 所有测试通过！LLM规则功能正常工作")
    else:
        print("⚠️  部分测试失败，请检查配置和代码")
    
    return passed == len(test_results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


