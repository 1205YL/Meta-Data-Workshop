# Meta Data Workshop 项目汇总

## 🎯 项目概述

**Meta Data Workshop** 是一款专业的数据库元数据处理工具，旨在解决数据库DDL语句处理中的重复劳动问题，提升开发和运维效率。

### 核心价值
- **自动化**: 减少手工处理DDL文件的重复劳动
- **标准化**: 统一的元数据处理流程和输出格式
- **高效率**: 批量处理大量表结构，快速生成所需文档和脚本
- **易使用**: 图形化界面，操作简单直观

## 📁 项目结构

```
Meta_Data_Workshop/
├── main.py                     # 程序入口文件
├── requirements.txt            # Python依赖列表
├── setup.py                   # Python包安装配置
├── README.md                  # 项目详细说明
├── QUICK_START.md             # 快速开始指南
├── PROJECT_SUMMARY.md         # 项目汇总（本文件）
├── test_sample.sql            # 测试用DDL样例
├── build_executable.py        # 可执行文件打包脚本
├── build.bat                  # Windows构建脚本
├── build.sh                   # Linux/macOS构建脚本
└── src/                       # 源代码目录
    ├── __init__.py
    ├── core/                  # 核心功能模块
    │   ├── __init__.py
    │   ├── ddl_parser.py      # DDL解析器
    │   ├── metadata_exporter.py  # 元数据导出器
    │   ├── field_manager.py   # 字段管理器
    │   └── sql_generator.py   # SQL生成器
    ├── gui/                   # 图形界面模块
    │   ├── __init__.py
    │   └── main_window.py     # 主窗口界面
    ├── utils/                 # 工具模块
    │   └── __init__.py
    └── config/                # 配置模块
        └── __init__.py
```

## 🔧 核心组件

### 1. DDL解析器 (ddl_parser.py)
- **功能**: 解析CREATE TABLE语句，提取表结构信息
- **支持**: MySQL, Oracle, PostgreSQL, SQL Server DDL语法
- **特性**: 
  - 智能识别数据库、Schema、表名
  - 解析字段类型、约束、默认值、注释
  - 提取主键、索引信息
  - 容错处理，跳过无效语句

### 2. 元数据导出器 (metadata_exporter.py)
- **功能**: 将解析后的元数据导出为多种格式
- **格式**: Excel (.xlsx), CSV (.csv), JSON (.json)
- **模式**: 
  - 全量合并导出
  - 按Schema分层导出
  - 按表单独导出
  - Excel多工作表导出

### 3. 字段管理器 (field_manager.py)
- **类型转换**: 内置主流数据库间字段类型转换规则
- **系统字段**: 预定义审计字段、版本控制字段等模板
- **自定义规则**: 支持用户定义转换规则和字段模板
- **变更对比**: 生成详细的字段变更对比报告

### 4. SQL生成器 (sql_generator.py)
- **DROP TABLE**: 批量生成表删除语句
- **CREATE TABLE**: 根据元数据重新生成建表语句
- **INSERT...SELECT**: 智能生成数据迁移脚本
- **方言支持**: 针对不同数据库生成对应语法的SQL

### 5. 图形界面 (main_window.py)
- **现代化设计**: 基于Tkinter的用户友好界面
- **多标签页**: 数据概览、表详情、操作日志分离显示
- **实时反馈**: 进度条、状态提示、错误日志
- **快捷操作**: 菜单栏、工具栏、快捷键支持

## 🚀 主要功能

### 元数据提取与导出
- [x] DDL文件解析 (支持.sql, .txt, .ddl格式)
- [x] 多级元数据提取 (Database → Schema → Table → Field)
- [x] 多格式导出 (Excel, CSV, JSON)
- [x] 灵活导出选项 (全量/分层/单表)

### 字段管理
- [x] 字段类型批量转换
- [x] 内置数据库转换规则 (MySQL↔Oracle↔PostgreSQL)
- [x] 自定义转换规则
- [x] 系统字段模板 (审计字段、版本控制、租户字段)
- [x] 字段变更对比报告

### SQL脚本生成
- [x] DROP TABLE语句生成
- [x] CREATE TABLE语句生成  
- [x] INSERT...SELECT语句生成
- [x] CASE WHEN条件处理
- [x] 多数据库方言支持

### 界面与交互
- [x] 图形化操作界面
- [x] 文件拖拽支持
- [x] 实时进度显示
- [x] 详细操作日志
- [x] 错误处理与提示

## 📊 测试验证

项目包含完整的测试样例 (`test_sample.sql`)，包含：
- 5个表，分布在4个不同Schema中
- 覆盖常见字段类型 (INT, VARCHAR, TEXT, DECIMAL, DATETIME等)
- 包含主键、外键、索引、注释等完整信息
- 测试验证解析器能正确识别所有元素

**测试结果**: ✅ 成功解析10个DDL对象

## 🔧 部署方式

### 开发模式
```bash
pip install -r requirements.txt
python main.py
```

### 可执行文件
```bash
# Windows
build.bat

# Linux/macOS  
./build.sh
```

### Python包安装
```bash
pip install -e .
```

## 🎯 应用场景

### 数据库迁移
- **场景**: MySQL到Oracle数据库迁移
- **解决**: 自动转换字段类型，生成目标数据库DDL
- **价值**: 减少人工转换错误，提升迁移效率

### 元数据文档生成
- **场景**: 为现有数据库生成数据字典
- **解决**: 批量导出表结构到Excel文档
- **价值**: 标准化文档格式，便于团队协作

### 开发规范统一
- **场景**: 为所有表添加审计字段
- **解决**: 批量添加created_at, updated_at等系统字段
- **价值**: 统一开发规范，提升代码质量

### SQL脚本自动化
- **场景**: 生成环境清理和重建脚本
- **解决**: 批量生成DROP/CREATE语句
- **价值**: 减少手工编写SQL的工作量

## 📈 技术特点

### 健壮性
- 容错处理：跳过无效DDL语句
- 编码支持：自动处理UTF-8编码
- 异常处理：详细错误信息和日志

### 扩展性
- 模块化设计：核心功能独立封装
- 插件架构：支持自定义转换规则
- 配置化：支持用户自定义模板

### 性能
- 异步处理：大文件解析不阻塞界面
- 内存优化：流式处理大量数据
- 缓存机制：避免重复解析

## 🔮 未来规划

### v1.1 计划
- [ ] 完善GUI对话框功能
- [ ] 增加更多数据库支持 (SQLite, DB2等)
- [ ] 批处理命令行模式
- [ ] 配置文件持久化

### v1.2 计划  
- [ ] DDL语法智能提示
- [ ] 元数据版本管理
- [ ] 数据字典自动生成
- [ ] Web界面版本

### v2.0 愿景
- [ ] AI驱动的智能转换
- [ ] 云端协作功能
- [ ] 企业级权限管理
- [ ] 集成主流开发工具

## 📞 支持与贡献

### 获取帮助
- 📖 查看 `README.md` 详细文档
- 🚀 参考 `QUICK_START.md` 快速入门
- 💬 查看程序内置帮助信息

### 贡献代码
- 🍴 Fork项目并创建功能分支
- 🧪 确保代码质量和测试覆盖
- 📝 更新相关文档
- 🔃 提交Pull Request

### 反馈问题
- 🐛 通过GitHub Issues报告bug
- 💡 提出功能改进建议
- 📧 发送邮件到 metadata.workshop@example.com

---

**Meta Data Workshop** - 专业的数据库元数据处理解决方案 🎉