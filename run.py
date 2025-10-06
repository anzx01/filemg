"""
Excel文档合并工具 - 启动脚本
用于启动整个应用程序
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_controller import main
    
    if __name__ == "__main__":
        print("=" * 50)
        print("Excel文档合并工具")
        print("=" * 50)
        print("正在启动应用程序...")
        
        # 启动主程序
        main()
        
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖模块都已正确安装")
    sys.exit(1)
    
except Exception as e:
    print(f"启动失败: {e}")
    sys.exit(1)
