"""
资源管理器 - 处理内嵌资源文件
用于在打包后的exe中访问内嵌的配置文件和其他资源
"""

import os
import sys
import json
import tempfile
from typing import Dict, Any, Optional


class ResourceManager:
    """资源管理器类"""
    
    def __init__(self):
        """初始化资源管理器"""
        self.temp_dir = None
        self.is_packaged = getattr(sys, 'frozen', False)
        self._setup_temp_directory()
    
    def _setup_temp_directory(self):
        """设置临时目录"""
        if self.is_packaged:
            # 在打包环境中，使用临时目录
            self.temp_dir = tempfile.mkdtemp(prefix='excel_merge_')
            print(f"创建临时目录: {self.temp_dir}")
        else:
            # 在开发环境中，使用当前目录
            self.temp_dir = os.getcwd()
    
    def get_resource_path(self, resource_name: str) -> str:
        """
        获取资源文件路径
        
        Args:
            resource_name: 资源文件名
            
        Returns:
            资源文件的实际路径
        """
        if self.is_packaged:
            # 在打包环境中，从内嵌资源获取
            return self._get_packaged_resource(resource_name)
        else:
            # 在开发环境中，直接返回文件路径
            return resource_name
    
    def _get_packaged_resource(self, resource_name: str) -> str:
        """
        从打包的资源中获取文件
        
        Args:
            resource_name: 资源文件名
            
        Returns:
            临时文件路径
        """
        try:
            # 首先尝试从exe同目录的config文件夹加载
            exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            config_path = os.path.join(exe_dir, resource_name)
            
            if os.path.exists(config_path):
                print(f"从exe同目录加载: {config_path}")
                return config_path
            
            # 尝试从当前工作目录加载
            if os.path.exists(resource_name):
                print(f"从当前目录加载: {resource_name}")
                return resource_name
            
            # 尝试从内嵌资源加载
            import pkgutil
            resource_data = pkgutil.get_data(__name__, resource_name)
            if resource_data:
                # 创建临时文件
                temp_file_path = os.path.join(self.temp_dir, os.path.basename(resource_name))
                with open(temp_file_path, 'wb') as f:
                    f.write(resource_data)
                print(f"从内嵌资源加载: {resource_name} -> {temp_file_path}")
                return temp_file_path
                
            # 创建默认配置文件
            print(f"创建默认配置: {resource_name}")
            return self._create_default_config(resource_name)
            
        except Exception as e:
            print(f"加载资源失败: {resource_name}, 错误: {e}")
            return self._create_default_config(resource_name)
    
    def _create_default_config(self, config_name: str) -> str:
        """
        创建默认配置文件
        
        Args:
            config_name: 配置文件名
            
        Returns:
            配置文件路径
        """
        config_path = os.path.join(self.temp_dir, os.path.basename(config_name))
        
        if 'field_mapping_config.json' in config_name:
            default_config = {}
        elif 'rules_config.json' in config_name:
            default_config = {
                "rules": [],
                "version": "1.0"
            }
        elif 'bank_rules_config.json' in config_name:
            default_config = {
                "bank_rules": [],
                "version": "1.0"
            }
        elif 'special_rules.json' in config_name:
            default_config = {
                "special_rules": [],
                "version": "1.0"
            }
        elif 'imported_files.json' in config_name:
            default_config = {
                "imported_files": [],
                "version": "1.0"
            }
        else:
            default_config = {}
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"创建默认配置文件: {config_path}")
        except Exception as e:
            print(f"创建默认配置文件失败: {config_path}, 错误: {e}")
        
        return config_path
    
    def load_json_config(self, config_name: str) -> Dict[str, Any]:
        """
        加载JSON配置文件
        
        Args:
            config_name: 配置文件名
            
        Returns:
            配置数据字典
        """
        try:
            # 首先尝试从exe文件所在目录加载保存的配置
            if self.is_packaged:
                exe_dir = os.path.dirname(sys.executable)
                saved_config_path = os.path.join(exe_dir, os.path.basename(config_name))
                if os.path.exists(saved_config_path):
                    with open(saved_config_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"从保存的配置文件加载: {saved_config_path}")
                    return data
            
            # 如果保存的配置不存在，尝试从内嵌资源加载
            config_path = self.get_resource_path(config_name)
            
            if not os.path.exists(config_path):
                print(f"配置文件不存在: {config_path}")
                return {}
            
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"配置文件加载成功: {config_path}")
            return data
            
        except Exception as e:
            print(f"加载JSON配置失败: {config_name}, 错误: {e}")
            return {}
    
    def save_json_config(self, data: Dict[str, Any], config_name: str) -> bool:
        """
        保存JSON配置文件
        
        Args:
            data: 要保存的数据
            config_name: 配置文件名
            
        Returns:
            保存是否成功
        """
        try:
            if self.is_packaged:
                # 在打包环境中，保存到exe文件所在目录
                exe_dir = os.path.dirname(sys.executable)
                config_path = os.path.join(exe_dir, os.path.basename(config_name))
            else:
                # 在开发环境中，保存到当前目录
                config_path = os.path.basename(config_name)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # 保存JSON文件
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"配置文件保存成功: {config_path}")
            return True
            
        except Exception as e:
            print(f"保存JSON配置失败: {config_name}, 错误: {e}")
            return False
    
    def get_output_directory(self) -> str:
        """
        获取输出目录
        
        Returns:
            输出目录路径
        """
        if self.is_packaged:
            # 在打包环境中，使用exe文件所在目录
            exe_dir = os.path.dirname(sys.executable)
            output_dir = os.path.join(exe_dir, 'output')
        else:
            # 在开发环境中，使用当前目录下的output
            output_dir = os.path.join(os.getcwd(), 'output')
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def cleanup(self):
        """清理临时文件"""
        if self.temp_dir and self.is_packaged:
            try:
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                print(f"清理临时目录: {self.temp_dir}")
            except Exception as e:
                print(f"清理临时目录失败: {e}")
    
    def __del__(self):
        """析构函数，自动清理"""
        self.cleanup()
