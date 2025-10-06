# Excel文档合并工具

一个用于合并多个Excel文档的Python工具，支持字段映射、特殊规则处理和数据合并功能。

## 项目结构

```
Excel文档合并工具/
├── requirements.txt              # 项目依赖
├── run.py                       # 主启动脚本
├── test_basic_framework.py      # 基础框架测试脚本
├── README.md                    # 项目说明文档
├── 软件设计文档.md               # 详细软件设计文档
├── 功能进度表.md                 # 开发进度跟踪表
├── ui_module.py                 # 用户界面模块
├── file_manager.py              # 文件管理模块
├── file_operations.py           # 文件操作模块
├── main_controller.py           # 主控制器模块
├── config/                      # 配置文件目录
└── output/                      # 输出文件目录
```

## 功能特性

### 已完成功能（基础框架）

1. **用户界面模块** ✅
   - 基于tkinter的现代化界面
   - 文件导入管理区域
   - 字段映射配置区域
   - 特殊规则配置区域
   - 合并操作区域

2. **文件管理模块** ✅
   - 多文件导入功能
   - 文件删除和重新导入
   - 重复导入检查
   - 文件信息持久化

3. **文件操作模块** ✅
   - Excel文件读写操作
   - JSON配置文件处理
   - 文件备份功能
   - 文件结构验证

4. **主控制器模块** ✅
   - 模块整合和协调
   - 业务流程控制
   - 配置管理
   - 错误处理

### 待开发功能

1. **字段映射模块** 🔄
   - 标准字段管理
   - 文件字段映射配置
   - 映射规则保存和加载

2. **特殊规则模块** 🔄
   - 自然语言规则解析
   - 银行特定规则处理
   - 规则应用和执行

3. **表头识别模块** 🔄
   - 智能表头识别
   - 余额列自动识别
   - 多表头处理

4. **数据处理模块** 🔄
   - 数据预处理
   - 字段映射应用
   - 特殊规则应用
   - 数据合并

## 安装和运行

### 环境要求

- Python 3.7+
- 依赖包见 `requirements.txt`

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python run.py
```

### 运行测试

```bash
python test_basic_framework.py
```

## 使用说明

### 基础操作流程

1. **启动程序**
   ```bash
   python run.py
   ```

2. **导入Excel文件**
   - 点击"选择Excel文件"按钮
   - 选择要合并的Excel文件
   - 文件将显示在已导入文件列表中

3. **配置字段映射**（待开发）
   - 添加标准字段
   - 为每个文件配置字段映射关系

4. **设置特殊规则**（待开发）
   - 为特定银行文件设置处理规则
   - 使用自然语言描述规则

5. **执行合并操作**（待开发）
   - 点击"开始合并"按钮
   - 等待合并完成
   - 查看输出结果

### 配置文件

程序会自动创建以下配置文件：

- `config/mapping_config.json` - 字段映射配置
- `config/rules_config.json` - 特殊规则配置
- `config/imported_files.json` - 已导入文件信息
- `output/` - 合并后的输出文件

## 开发进度

### 里程碑1: 基础框架 ✅ (已完成)

- [x] 主窗口和基础界面
- [x] 文件管理基础功能
- [x] 基础文件操作
- [x] 主控制器整合

### 里程碑2: 核心功能 🔄 (进行中)

- [ ] 字段映射功能
- [ ] 表头识别功能
- [ ] 基础数据处理

### 里程碑3: 高级功能 🔄 (待开始)

- [ ] 自然语言规则解析
- [ ] 特殊规则处理
- [ ] 数据合并功能

### 里程碑4: 完善优化 🔄 (待开始)

- [ ] 所有功能集成
- [ ] 错误处理完善
- [ ] 性能优化

## 技术架构

### 模块设计

```
Excel合并工具
├── 用户界面层 (UI Layer)
│   └── ExcelMergeUI
├── 业务逻辑层 (Business Logic Layer)
│   ├── FileManager
│   ├── FieldMappingManager
│   ├── SpecialRulesManager
│   └── DataProcessor
├── 数据处理层 (Data Processing Layer)
│   ├── HeaderDetector
│   ├── RuleParser
│   └── FileOperations
└── 控制层 (Control Layer)
    └── ExcelMergeController
```

### 核心类和方法

- `ExcelMergeUI`: 用户界面管理
- `FileManager`: 文件导入和管理
- `FileOperations`: 文件读写操作
- `ExcelMergeController`: 主控制器

## 贡献指南

1. 查看 `功能进度表.md` 了解当前开发状态
2. 按照 `软件设计文档.md` 的设计进行开发
3. 运行测试确保功能正常
4. 更新进度表记录开发状态

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请通过项目仓库提交Issue。
