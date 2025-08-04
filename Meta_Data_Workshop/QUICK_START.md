# Meta Data Workshop 快速开始指南

## 🚀 快速运行

### 方法1: 直接运行Python脚本
```bash
# 1. 进入项目目录
cd Meta_Data_Workshop

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行程序
python main.py
```

### 方法2: 构建可执行文件
```bash
# Windows用户
build.bat

# Linux/macOS用户
./build.sh
```

## 📝 快速测试

1. **运行程序**
   - 双击 `main.py` 或在命令行运行 `python main.py`

2. **加载测试文件**
   - 点击"浏览"按钮
   - 选择项目中的 `test_sample.sql` 文件
   - 点击"解析"按钮

3. **查看解析结果**
   - 在"数据概览"标签页查看统计信息
   - 在"表详情"标签页查看具体的表和字段信息

4. **测试导出功能**
   - 点击"导出元数据"按钮（功能演示）
   - 点击"字段管理"按钮（功能演示）
   - 点击"生成SQL"按钮（功能演示）

## 🎯 核心功能演示

### DDL解析
- 支持MySQL、Oracle、PostgreSQL等数据库DDL语法
- 自动识别表结构、字段类型、主键、注释等信息
- 按Schema分组显示统计信息

### 元数据导出
- Excel格式：按Schema分工作表导出
- CSV格式：表格化数据导出
- JSON格式：结构化数据导出

### 字段管理
- 类型转换：MySQL ↔ Oracle ↔ PostgreSQL等
- 系统字段：批量添加审计字段、版本控制字段等
- 变更对比：自动生成修改前后的对比报告

### SQL生成
- DROP TABLE：批量生成删除语句
- CREATE TABLE：重新生成建表语句
- INSERT...SELECT：生成数据迁移脚本

## 📋 测试文件说明

`test_sample.sql` 包含以下测试表：

1. **user_management.users** - 用户信息表
2. **product_catalog.products** - 产品信息表
3. **order_management.orders** - 订单主表
4. **order_management.order_items** - 订单明细表
5. **inventory.stock_movements** - 库存流水表

涵盖了多个Schema、不同字段类型、主键、索引、注释等常见DDL元素。

## ⚠️ 注意事项

1. **Python版本要求**: Python 3.7+
2. **依赖包**: 确保安装了pandas、openpyxl等依赖
3. **DDL格式**: 支持标准的CREATE TABLE语句
4. **文件编码**: 建议使用UTF-8编码的DDL文件

## 🔧 故障排除

### 问题1: 模块导入失败
```
解决方法: pip install -r requirements.txt
```

### 问题2: DDL解析失败
```
检查DDL语法是否符合标准CREATE TABLE格式
确保文件编码为UTF-8
```

### 问题3: 界面显示异常
```
确保系统支持tkinter (通常Python自带)
检查显示器分辨率和系统DPI设置
```

## 📞 获取帮助

- 查看 `README.md` 获取详细文档
- 查看程序内的"帮助"菜单
- 查看"操作日志"标签页的错误信息

---

**祝您使用愉快！** 🎉