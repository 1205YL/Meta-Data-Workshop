# Meta Data Workshop

数据库元数据处理工具 - 高效处理DDL语句，自动化生成SQL脚本

## 功能特点

### 🔍 元数据提取与导出
- **智能DDL解析**: 支持MySQL、Oracle、PostgreSQL、SQL Server等主流数据库DDL语法
- **多格式导出**: Excel、CSV、JSON格式，满足不同使用场景
- **灵活分层导出**: 支持按数据库、Schema、表三级维度分别导出

### 🛠️ 字段管理功能
- **批量类型转换**: 内置主流数据库间的字段类型转换规则，支持自定义转换规则
- **系统字段添加**: 预置审计字段、版本控制字段等模板，支持批量添加
- **字段变更对比**: 自动生成字段变更对比报告

### 📋 SQL脚本生成
- **DROP TABLE语句**: 批量生成删除表语句，支持IF EXISTS条件
- **CREATE TABLE语句**: 根据解析的元数据重新生成建表语句
- **INSERT...SELECT语句**: 智能生成数据迁移脚本，支持CASE WHEN条件处理

### 🖥️ 现代化界面
- **直观操作**: 基于Tkinter的现代化图形界面
- **实时反馈**: 操作进度显示和详细日志记录
- **多标签页**: 数据概览、表详情、操作日志分离显示

## 安装说明

### 环境要求
- Python 3.7+
- 操作系统: Windows, macOS, Linux

### 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd Meta_Data_Workshop
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   python main.py
   ```

## 使用指南

### 1. DDL文件解析
1. 点击"浏览"按钮选择DDL文件（支持.sql、.txt、.ddl格式）
2. 点击"解析"按钮开始解析
3. 查看"数据概览"标签页中的统计信息

### 2. 元数据导出
1. 确保已解析DDL文件
2. 点击"导出元数据"按钮
3. 选择导出格式和导出方式（全量/按Schema/按表）
4. 指定输出路径，完成导出

### 3. 字段类型转换
1. 进入"字段管理"功能
2. 选择转换规则（如mysql_to_oracle）
3. 选择要转换的表
4. 执行批量转换

### 4. 系统字段添加
1. 进入"字段管理"功能
2. 选择字段模板（如audit_fields审计字段）
3. 设置添加位置（表首/表尾）
4. 选择目标表执行添加

### 5. SQL脚本生成
1. 进入"生成SQL"功能
2. 选择要生成的SQL类型
3. 配置生成选项
4. 保存生成的SQL脚本

## 支持的数据库

- **MySQL** (5.7+, 8.0+)
- **Oracle** (11g+, 12c+, 19c+)
- **PostgreSQL** (10+, 11+, 12+, 13+, 14+)
- **SQL Server** (2012+, 2016+, 2019+)

## 文件结构

```
Meta_Data_Workshop/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖列表
├── README.md              # 说明文档
├── src/                   # 源代码目录
│   ├── core/             # 核心功能模块
│   │   ├── ddl_parser.py        # DDL解析器
│   │   ├── metadata_exporter.py # 元数据导出器
│   │   ├── field_manager.py     # 字段管理器
│   │   └── sql_generator.py     # SQL生成器
│   ├── gui/              # 图形界面模块
│   │   └── main_window.py       # 主窗口
│   ├── utils/            # 工具模块
│   └── config/           # 配置模块
├── tests/                # 测试文件
├── docs/                 # 文档目录
├── assets/               # 资源文件
└── build/                # 构建输出目录
```

## 开发计划

### 当前版本 (v1.0)
- ✅ DDL解析功能
- ✅ 元数据导出
- ✅ 字段类型转换
- ✅ 系统字段管理
- ✅ SQL脚本生成
- ✅ 基础GUI界面

### 后续版本规划
- 🔄 更多数据库支持
- 🔄 DDL语法智能提示
- 🔄 批处理脚本功能
- 🔄 元数据版本管理
- 🔄 数据字典生成

## 技术架构

### 核心组件
- **DDLParser**: 基于正则表达式的DDL语句解析器
- **MetadataExporter**: 支持多格式的元数据导出器
- **FieldManager**: 字段类型转换和系统字段管理器
- **SQLGenerator**: 智能SQL脚本生成器

### 技术栈
- **后端**: Python 3.7+
- **GUI**: Tkinter (内置)
- **数据处理**: pandas, openpyxl
- **文件格式**: Excel, CSV, JSON

## 常见问题

### Q: 支持哪些DDL语句格式？
A: 支持标准的CREATE TABLE语句，包括IF NOT EXISTS、OR REPLACE等变体。

### Q: 如何添加自定义字段类型转换规则？
A: 在字段管理功能中，可以通过界面添加自定义转换规则。

### Q: 生成的SQL脚本是否可以直接执行？
A: 是的，生成的SQL脚本经过语法检查，可以直接在对应数据库中执行。

### Q: 如何处理大型DDL文件？
A: 工具支持后台处理，大文件解析时会显示进度条，不会阻塞界面。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 报告问题
- 使用Issue模板描述问题
- 提供DDL文件样例（如果涉及解析问题）
- 说明操作系统和Python版本

### 提交代码
- Fork项目并创建feature分支
- 确保代码符合PEP 8规范
- 添加必要的测试用例
- 更新相关文档

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 邮箱联系: metadata.workshop@example.com

---

**Meta Data Workshop** - 让数据库元数据处理更简单高效！