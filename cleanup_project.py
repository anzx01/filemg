#!/usr/bin/env python3
"""
项目清理脚本
安全删除项目中的无用文件，保持项目整洁
"""

import os
import shutil
import glob
from datetime import datetime, timedelta

class ProjectCleaner:
    def __init__(self, project_root):
        self.project_root = project_root
        self.cleaned_files = []
        self.cleaned_dirs = []
        self.total_size_freed = 0

    def clean_python_cache(self):
        """清理Python缓存文件"""
        print("🧹 清理Python缓存文件...")

        # 清理__pycache__目录
        for root, dirs, files in os.walk(self.project_root):
            if '__pycache__' in dirs:
                pycache_path = os.path.join(root, '__pycache__')
                size = self.get_directory_size(pycache_path)
                if self.safe_remove_directory(pycache_path):
                    self.cleaned_dirs.append(pycache_path)
                    self.total_size_freed += size
                    print(f"   ✅ 删除缓存目录: {pycache_path}")

        # 清理.pyc文件
        pyc_files = glob.glob(os.path.join(self.project_root, '**/*.pyc'), recursive=True)
        for pyc_file in pyc_files:
            size = os.path.getsize(pyc_file)
            if self.safe_remove_file(pyc_file):
                self.cleaned_files.append(pyc_file)
                self.total_size_freed += size
                print(f"   ✅ 删除pyc文件: {pyc_file}")

    def clean_temp_excel_files(self):
        """清理临时Excel文件"""
        print("🧹 清理临时Excel文件...")

        output_dir = os.path.join(self.project_root, 'output')
        if not os.path.exists(output_dir):
            return

        # 删除Excel临时文件（以~$开头的文件）
        temp_files = glob.glob(os.path.join(output_dir, '~$*.xlsx'))
        for temp_file in temp_files:
            size = os.path.getsize(temp_file)
            if self.safe_remove_file(temp_file):
                self.cleaned_files.append(temp_file)
                self.total_size_freed += size
                print(f"   ✅ 删除临时Excel文件: {os.path.basename(temp_file)}")

        # 询问是否清理旧的合并结果文件
        old_files = self.get_old_output_files(days=7)
        if old_files:
            print(f"\n📅 发现 {len(old_files)} 个超过7天的合并结果文件:")
            for file_path in old_files:
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                file_size = os.path.getsize(file_path)
                print(f"   📄 {os.path.basename(file_path)} ({file_time.strftime('%Y-%m-%d')}, {file_size:,} bytes)")

            response = input("\n🗑️  是否删除这些旧文件? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                for file_path in old_files:
                    size = os.path.getsize(file_path)
                    if self.safe_remove_file(file_path):
                        self.cleaned_files.append(file_path)
                        self.total_size_freed += size
                        print(f"   ✅ 删除旧文件: {os.path.basename(file_path)}")

    def clean_log_files(self):
        """清理日志文件"""
        print("🧹 清理日志文件...")

        log_files = glob.glob(os.path.join(self.project_root, '**/*.log'), recursive=True)
        for log_file in log_files:
            size = os.path.getsize(log_file)
            if self.safe_remove_file(log_file):
                self.cleaned_files.append(log_file)
                self.total_size_freed += size
                print(f"   ✅ 删除日志文件: {os.path.basename(log_file)}")

    def clean_backup_files(self):
        """清理备份文件"""
        print("🧹 清理备份文件...")

        # 清理.bak文件
        bak_files = glob.glob(os.path.join(self.project_root, '**/*.bak'), recursive=True)
        for bak_file in bak_files:
            size = os.path.getsize(bak_file)
            if self.safe_remove_file(bak_file):
                self.cleaned_files.append(bak_file)
                self.total_size_freed += size
                print(f"   ✅ 删除备份文件: {os.path.basename(bak_file)}")

    def clean_test_files(self):
        """清理测试生成的临时文件"""
        print("🧹 清理测试临时文件...")

        # 查找测试相关的临时文件
        test_temp_patterns = [
            'test_*_temp.xlsx',
            'temp_*.json',
            'test_*.csv',
            'debug_*.log'
        ]

        for pattern in test_temp_patterns:
            temp_files = glob.glob(os.path.join(self.project_root, pattern))
            for temp_file in temp_files:
                size = os.path.getsize(temp_file)
                if self.safe_remove_file(temp_file):
                    self.cleaned_files.append(temp_file)
                    self.total_size_freed += size
                    print(f"   ✅ 删除测试临时文件: {os.path.basename(temp_file)}")

    def get_old_output_files(self, days=7):
        """获取超过指定天数的输出文件"""
        output_dir = os.path.join(self.project_root, 'output')
        if not os.path.exists(output_dir):
            return []

        old_files = []
        cutoff_time = datetime.now() - timedelta(days=days)

        for file_name in os.listdir(output_dir):
            if file_name.startswith('合并结果_') and file_name.endswith('.xlsx'):
                file_path = os.path.join(output_dir, file_name)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_time:
                    old_files.append(file_path)

        return old_files

    def safe_remove_file(self, file_path):
        """安全删除文件"""
        try:
            if os.path.exists(file_path) and not os.path.isdir(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"   ❌ 删除文件失败: {file_path} - {e}")
        return False

    def safe_remove_directory(self, dir_path):
        """安全删除目录"""
        try:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
                return True
        except Exception as e:
            print(f"   ❌ 删除目录失败: {dir_path} - {e}")
        return False

    def get_directory_size(self, dir_path):
        """获取目录大小"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except:
            pass
        return total_size

    def format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def clean_all(self, clean_old_outputs=False):
        """执行所有清理操作"""
        print("🧹 开始清理项目...")
        print("=" * 50)

        start_time = datetime.now()

        # 执行各种清理操作
        self.clean_python_cache()
        self.clean_temp_excel_files()
        self.clean_log_files()
        self.clean_backup_files()
        self.clean_test_files()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 显示清理结果
        print("\n" + "=" * 50)
        print("📊 清理结果:")
        print(f"   📁 删除目录: {len(self.cleaned_dirs)} 个")
        print(f"   📄 删除文件: {len(self.cleaned_files)} 个")
        print(f"   💾 释放空间: {self.format_size(self.total_size_freed)}")
        print(f"   ⏱️  清理时间: {duration:.2f} 秒")

        if self.cleaned_files or self.cleaned_dirs:
            print("\n🗑️  已删除的文件:")
            for item in self.cleaned_files + self.cleaned_dirs:
                print(f"   📄 {item}")
        else:
            print("\n✨ 项目已经很整洁，没有需要清理的文件")

def main():
    """主函数"""
    print("🧹 Excel合并工具 - 项目清理脚本")
    print("=" * 50)

    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))

    print(f"📂 项目目录: {project_root}")

    # 显示清理选项
    print("\n🔧 清理选项:")
    print("   1. 清理Python缓存文件")
    print("   2. 清理临时Excel文件")
    print("   3. 清理日志文件")
    print("   4. 清理备份文件")
    print("   5. 清理测试临时文件")
    print("   6. 全部清理（推荐）")
    print("   0. 退出")

    try:
        choice = input("\n请选择清理选项 (0-6): ").strip()

        if choice == '0':
            print("👋 已取消清理")
            return
        elif choice not in ['1', '2', '3', '4', '5', '6']:
            print("❌ 无效选择，执行全部清理...")
            choice = '6'

        # 创建清理器
        cleaner = ProjectCleaner(project_root)

        # 执行清理
        if choice == '6':
            cleaner.clean_all()
        elif choice == '1':
            cleaner.clean_python_cache()
        elif choice == '2':
            cleaner.clean_temp_excel_files()
        elif choice == '3':
            cleaner.clean_log_files()
        elif choice == '4':
            cleaner.clean_backup_files()
        elif choice == '5':
            cleaner.clean_test_files()

        print("\n🎉 清理完成！")

    except KeyboardInterrupt:
        print("\n\n👋 清理已取消")
    except Exception as e:
        print(f"\n❌ 清理过程中出现错误: {e}")

if __name__ == "__main__":
    main()