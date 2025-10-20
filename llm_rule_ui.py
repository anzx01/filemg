#!/usr/bin/env python3
"""
LLM自然语言规则输入界面

提供简单的命令行界面，让用户输入自然语言规则并查看解析结果。
"""

import json
import sys
from dynamic_rule_parser import DynamicRuleParser

class LLMRuleUI:
    """LLM规则输入界面"""
    
    def __init__(self):
        """初始化界面"""
        self.parser = DynamicRuleParser()
        self.running = True
    
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "=" * 60)
        print("LLM自然语言规则解析工具")
        print("=" * 60)
        print("1. 输入自然语言规则")
        print("2. 查看已解析的规则")
        print("3. 测试规则解析")
        print("4. 配置LLM设置")
        print("5. 批量导入规则")
        print("0. 退出")
        print("-" * 60)
    
    def input_natural_language_rule(self):
        """输入自然语言规则"""
        print("\n" + "-" * 40)
        print("输入自然语言规则")
        print("-" * 40)
        
        rule_text = input("请输入规则描述: ").strip()
        if not rule_text:
            print("规则描述不能为空")
            return
        
        bank_name = input("请输入银行名称（可选）: ").strip()
        if not bank_name:
            bank_name = None
        
        print(f"\n正在解析规则: {rule_text}")
        print("解析中...")
        
        try:
            # 解析规则
            parsed_rule = self.parser.add_rule_from_natural_language(rule_text, bank_name)
            
            print("\n解析成功！")
            print("=" * 40)
            print("规则ID:", parsed_rule['id'])
            print("规则类型:", parsed_rule['type'])
            print("银行名称:", parsed_rule['bank_name'])
            print("关键词:", ", ".join(parsed_rule['keywords']))
            print("参数配置:")
            print(json.dumps(parsed_rule['parameters'], ensure_ascii=False, indent=2))
            
        except Exception as e:
            print(f"解析失败: {e}")
    
    def view_parsed_rules(self):
        """查看已解析的规则"""
        print("\n" + "-" * 40)
        print("已解析的规则")
        print("-" * 40)
        
        if not self.parser.rules:
            print("暂无已解析的规则")
            return
        
        for i, rule in enumerate(self.parser.rules, 1):
            print(f"\n规则 {i}:")
            print(f"  ID: {rule['id']}")
            print(f"  描述: {rule['description']}")
            print(f"  类型: {rule['type']}")
            print(f"  银行: {rule['bank_name']}")
            print(f"  状态: {rule['status']}")
    
    def test_rule_parsing(self):
        """测试规则解析"""
        print("\n" + "-" * 40)
        print("规则解析测试")
        print("-" * 40)
        
        test_rules = [
            "将对方行名字段映射到对方户名字段",
            "处理日期格式转换",
            "计算账户余额",
            "自动分类交易类型"
        ]
        
        print("测试规则列表:")
        for i, rule in enumerate(test_rules, 1):
            print(f"{i}. {rule}")
        
        choice = input("\n选择要测试的规则编号 (1-4): ").strip()
        
        try:
            rule_index = int(choice) - 1
            if 0 <= rule_index < len(test_rules):
                rule_text = test_rules[rule_index]
                print(f"\n测试规则: {rule_text}")
                
                # 解析规则
                parsed_rule = self.parser.parse_natural_language_with_llm(rule_text, "测试银行")
                
                print("\n解析结果:")
                print(json.dumps(parsed_rule, ensure_ascii=False, indent=2))
            else:
                print("无效的选择")
        except ValueError:
            print("请输入有效的数字")
        except Exception as e:
            print(f"测试失败: {e}")
    
    def configure_llm_settings(self):
        """配置LLM设置"""
        print("\n" + "-" * 40)
        print("LLM配置")
        print("-" * 40)
        
        print(f"当前LLM状态: {'启用' if self.parser.use_llm else '禁用'}")
        print(f"当前配置: {json.dumps(self.parser.llm_config, ensure_ascii=False, indent=2)}")
        
        print("\n配置选项:")
        print("1. 启用/禁用LLM功能")
        print("2. 设置OpenAI API密钥")
        print("3. 修改模型参数")
        print("0. 返回主菜单")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            enable = input("是否启用LLM功能? (y/n): ").strip().lower() == 'y'
            self.parser.update_llm_config({"enable_llm_parsing": enable})
            print(f"LLM功能已{'启用' if enable else '禁用'}")
            
        elif choice == "2":
            api_key = input("请输入OpenAI API密钥: ").strip()
            if api_key:
                self.parser.update_llm_config({
                    "openai": {"api_key": api_key}
                })
                print("API密钥已设置")
            else:
                print("API密钥不能为空")
                
        elif choice == "3":
            model = input("请输入模型名称 (默认: gpt-3.5-turbo): ").strip()
            temperature = input("请输入温度值 (默认: 0.1): ").strip()
            
            config_updates = {}
            if model:
                config_updates["openai"] = {"model": model}
            if temperature:
                try:
                    config_updates["openai"]["temperature"] = float(temperature)
                except ValueError:
                    print("温度值必须是数字")
                    return
            
            if config_updates:
                self.parser.update_llm_config(config_updates)
                print("模型参数已更新")
    
    def batch_import_rules(self):
        """批量导入规则"""
        print("\n" + "-" * 40)
        print("批量导入规则")
        print("-" * 40)
        
        print("请输入规则描述，每行一条，输入空行结束:")
        rules = []
        while True:
            rule = input().strip()
            if not rule:
                break
            rules.append(rule)
        
        if not rules:
            print("没有输入任何规则")
            return
        
        bank_name = input("请输入银行名称（可选）: ").strip()
        if not bank_name:
            bank_name = None
        
        print(f"\n正在批量解析 {len(rules)} 条规则...")
        
        try:
            parsed_rules = self.parser.batch_parse_natural_language_rules(rules, bank_name)
            print(f"成功解析 {len(parsed_rules)} 条规则")
            
            # 显示解析结果摘要
            for i, rule in enumerate(parsed_rules, 1):
                print(f"{i}. {rule['type']} - {rule['description'][:50]}...")
                
        except Exception as e:
            print(f"批量解析失败: {e}")
    
    def run(self):
        """运行界面"""
        print("欢迎使用LLM自然语言规则解析工具！")
        
        while self.running:
            try:
                self.show_menu()
                choice = input("\n请选择操作 (0-5): ").strip()
                
                if choice == "0":
                    print("感谢使用，再见！")
                    self.running = False
                elif choice == "1":
                    self.input_natural_language_rule()
                elif choice == "2":
                    self.view_parsed_rules()
                elif choice == "3":
                    self.test_rule_parsing()
                elif choice == "4":
                    self.configure_llm_settings()
                elif choice == "5":
                    self.batch_import_rules()
                else:
                    print("无效的选择，请重新输入")
                
                if self.running:
                    input("\n按回车键继续...")
                    
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                self.running = False
            except Exception as e:
                print(f"\n发生错误: {e}")
                input("按回车键继续...")

if __name__ == "__main__":
    try:
        ui = LLMRuleUI()
        ui.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)

