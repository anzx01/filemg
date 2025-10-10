"""
LLM规则功能演示脚本

该脚本演示如何使用基于DeepSeek API的自然语言规则解析功能。

作者: AI助手
创建时间: 2025-01-27
"""

import os
import sys
import json
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_llm_parsing():
    """演示LLM规则解析功能"""
    print("🤖 LLM规则解析功能演示")
    print("=" * 50)
    
    try:
        from llm_api import RuleLLMParser
        
        # 创建解析器
        parser = RuleLLMParser()
        
        # 演示规则
        demo_rules = [
            {
                "description": "北京银行日期范围从2024-01-01至2024-12-31",
                "bank_name": "北京银行"
            },
            {
                "description": "工商银行将'交易日期'字段映射到'日期'字段",
                "bank_name": "工商银行"
            },
            {
                "description": "华夏银行余额增加1000元",
                "bank_name": "华夏银行"
            },
            {
                "description": "招商银行根据交易金额正负号分类收支",
                "bank_name": "招商银行"
            }
        ]
        
        print("开始解析演示规则...\n")
        
        for i, rule_info in enumerate(demo_rules, 1):
            print(f"规则 {i}: {rule_info['description']}")
            print("-" * 40)
            
            try:
                result = parser.parse_natural_language_rule(
                    rule_info['description'], 
                    rule_info['bank_name']
                )
                
                if result.get("success"):
                    print("✅ 解析成功")
                    print(f"   规则ID: {result.get('id')}")
                    print(f"   规则类型: {result.get('type')}")
                    print(f"   银行名称: {result.get('bank_name')}")
                    print(f"   描述: {result.get('description')}")
                    print(f"   状态: {result.get('status')}")
                    print(f"   创建时间: {result.get('created_at')}")
                    print(f"   参数: {json.dumps(result.get('parameters', {}), ensure_ascii=False, indent=2)}")
                else:
                    print(f"❌ 解析失败: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ 解析异常: {str(e)}")
            
            print()
        
        print("演示完成！")
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {str(e)}")
        print("请确保已安装所需依赖：pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")


def demo_ui_launch():
    """演示UI启动"""
    print("\n🖥️ 启动图形界面演示")
    print("=" * 50)
    
    try:
        from special_rules_ui import SpecialRulesUI
        
        print("正在启动特殊规则配置界面...")
        print("界面功能包括：")
        print("- 🤖 LLM智能解析规则")
        print("- 📝 手动编辑规则")
        print("- 🏦 银行特定规则管理")
        print("- 💾 规则导入导出")
        print("- 🔍 规则搜索和筛选")
        print("\n请在弹出的界面中体验LLM规则功能！")
        
        # 启动UI
        app = SpecialRulesUI()
        app.run()
        
    except ImportError as e:
        print(f"❌ 导入UI模块失败: {str(e)}")
        print("请确保已安装tkinter：pip install tkinter")
    except Exception as e:
        print(f"❌ 启动UI失败: {str(e)}")


def check_config():
    """检查配置"""
    print("🔧 检查配置")
    print("=" * 50)
    
    # 检查配置文件
    if os.path.exists("config.env"):
        print("✅ 找到配置文件: config.env")
        
        # 读取配置
        with open("config.env", "r", encoding="utf-8") as f:
            content = f.read()
            if "your_deepseek_api_key_here" in content:
                print("⚠️  请设置正确的DEEPSEEK_API_KEY")
                return False
            else:
                print("✅ API密钥已配置")
                return True
    else:
        print("❌ 未找到配置文件: config.env")
        print("请创建config.env文件并设置DEEPSEEK_API_KEY")
        return False


def main():
    """主函数"""
    print("🚀 LLM规则功能演示程序")
    print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查配置
    if not check_config():
        print("\n请先配置API密钥后再运行演示")
        return
    
    print()
    
    # 选择演示模式
    print("请选择演示模式：")
    print("1. 命令行解析演示")
    print("2. 图形界面演示")
    print("3. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-3): ").strip()
            
            if choice == "1":
                demo_llm_parsing()
                break
            elif choice == "2":
                demo_ui_launch()
                break
            elif choice == "3":
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入1-3")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    main()


