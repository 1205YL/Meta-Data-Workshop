import re
import os

def generate_drop_statements(ddl_path, output_path):
    """
    从DDL文件中提取表名并生成对应的DROP TABLE语句
    """
    # 读取DDL文件内容
    with open(ddl_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 正则表达式匹配表名，格式为"schema"."table"
    pattern = r'CREATE TABLE IF NOT EXISTS\s+([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)'
    matches = re.findall(pattern, content)
    
    if not matches:
        print("未找到任何表定义")
        return
    
    # 生成DROP TABLE语句，去重处理
    drop_statements = set()
    for schema, table in matches:
        # 构建DROP TABLE语句，保留引号以匹配原格式
        drop_stmt = f'DROP TABLE IF EXISTS "{schema}"."{table}";'
        drop_statements.add(drop_stmt)
    
    # 将生成的语句写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        # 按字母顺序排序输出
        for stmt in sorted(drop_statements):
            f.write(stmt + '\n')
    
    print(f"成功生成 {len(drop_statements)} 条DROP TABLE语句")
    print(f"结果已保存至: {output_path}")

def main():
    # DDL文件路径
    ddl_path = r"C:\yelan\Medical Date Hub To CDP\outbound\all_ddl0729_modified.txt"
    
    # 检查文件是否存在
    if not os.path.exists(ddl_path):
        print(f"错误：文件 {ddl_path} 不存在")
        return
    
    # 输出文件路径（与DDL文件同目录）
    output_dir = os.path.dirname(ddl_path)
    output_path = os.path.join(output_dir, "table_drop.txt")
    
    # 生成DROP语句
    generate_drop_statements(ddl_path, output_path)

if __name__ == "__main__":
    main()
    