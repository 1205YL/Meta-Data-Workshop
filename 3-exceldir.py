import re
import pandas as pd
import os
from collections import defaultdict

# 文件路径
ddl_file_path = r"C:\yelan\Medical Date Hub To CDP\3-pharma_etl_partner_prod_incro-kaiyang\sp_list-sql.txt"
output_excel_path = r"C:\yelan\Medical Date Hub To CDP\3-pharma_etl_partner_prod_incro-kaiyang\sp_list-ddlxx0731.xlsx"

# 读取DDL文件
with open(ddl_file_path, 'r', encoding='utf-8') as file:
    ddl_content = file.read()

# 分割多个DDL语句
# 使用正则表达式匹配以CREATE TABLE开头，以分号结尾的语句
ddl_statements = re.findall(r'CREATE TABLE IF NOT EXISTS.*?;', ddl_content, re.DOTALL)

# 创建一个字典来存储按schema分组的数据
schema_data = defaultdict(list)

import re

# 处理每个DDL语句
for ddl in ddl_statements:
    # 提取schema和table（修正正则表达式中的拼写错误，将a-zA-Z改为a-zA-Z）
    schema_table_match = re.search(r'CREATE TABLE IF NOT EXISTS\s+([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)', ddl)
    if not schema_table_match:
        continue
    
    schema = schema_table_match.group(1)
    table = schema_table_match.group(2)
    
    # 提取字段定义部分
    fields_section_match = re.search(r'\((.*?)\)\s*DISTSTYLE', ddl, re.DOTALL)
    if not fields_section_match:
        continue
    
    fields_section = fields_section_match.group(1)
    
    # 分割字段定义
    # 使用逗号分隔，但要注意不要分割括号内的逗号
    field_lines = []
    current_line = ""
    in_parenthesis = 0
    
    for char in fields_section:
        if char == '(':
            in_parenthesis += 1
            current_line += char
        elif char == ')':
            in_parenthesis -= 1
            current_line += char
        elif char == ',' and in_parenthesis == 0:
            field_lines.append(current_line.strip())
            current_line = ""
        else:
            current_line += char
    
    if current_line.strip():
        field_lines.append(current_line.strip())
    
    # 处理每个字段行
    for field_line in field_lines:
        # 跳过PRIMARY KEY等非字段定义行
        if field_line.strip().upper().startswith('PRIMARY KEY') or not field_line.strip():
            continue
        
        # 清理字段行
        field_line = field_line.strip()
        # 如果字段名不带引号，直接取第一个单词
        parts = field_line.split()
        if not parts:
            continue
        field_name = parts[0]
        if len(parts) > 1:
            field_type = parts[1]
        else:
            field_type = ""
        
        # 将数据添加到对应的schema
        schema_data[schema].append({
            'schema': schema,
            'table': table,
            '字段名': field_name,
            '字段类型': field_type
        })

# 创建Excel writer对象
with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
    # 为每个schema创建一个sheet
    for schema, data in schema_data.items():
        # 创建DataFrame
        df = pd.DataFrame(data)
        # 将DataFrame写入Excel
        df.to_excel(writer, sheet_name=schema, index=False)

print(f"Excel文件已创建: {output_excel_path}")