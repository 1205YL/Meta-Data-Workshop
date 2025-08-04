import re
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class FieldInfo:
    """字段信息数据类"""
    name: str
    type: str
    nullable: bool = True
    default_value: Optional[str] = None
    comment: Optional[str] = None

@dataclass 
class TableInfo:
    """表信息数据类"""
    database: str
    schema: str
    table: str
    fields: List[FieldInfo]
    primary_keys: List[str]
    comment: Optional[str] = None

class DDLParser:
    """DDL语句解析器"""
    
    def __init__(self):
        self.tables = []
        self.parsed_data = defaultdict(list)
        
    def parse_file(self, file_path: str, encoding: str = 'utf-8') -> List[TableInfo]:
        """
        解析DDL文件
        
        Args:
            file_path: DDL文件路径
            encoding: 文件编码
            
        Returns:
            解析后的表信息列表
        """
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                ddl_content = file.read()
            return self.parse_content(ddl_content)
        except Exception as e:
            raise Exception(f"读取文件失败: {str(e)}")
    
    def parse_content(self, ddl_content: str) -> List[TableInfo]:
        """
        解析DDL内容
        
        Args:
            ddl_content: DDL语句内容
            
        Returns:
            解析后的表信息列表
        """
        self.tables.clear()
        self.parsed_data.clear()
        
        # 支持多种CREATE TABLE语法
        patterns = [
            r'CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+.*?;',
            r'CREATE\s+TABLE\s+.*?;',
            r'CREATE\s+OR\s+REPLACE\s+TABLE\s+.*?;'
        ]
        
        ddl_statements = []
        for pattern in patterns:
            statements = re.findall(pattern, ddl_content, re.DOTALL | re.IGNORECASE)
            ddl_statements.extend(statements)
        
        for ddl in ddl_statements:
            table_info = self._parse_single_table(ddl)
            if table_info:
                self.tables.append(table_info)
                self.parsed_data[table_info.schema].append(table_info)
        
        return self.tables
    
    def _parse_single_table(self, ddl: str) -> Optional[TableInfo]:
        """
        解析单个表的DDL语句
        
        Args:
            ddl: 单个表的DDL语句
            
        Returns:
            表信息对象
        """
        try:
            # 提取表名（支持多种格式）
            table_patterns = [
                r'CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([`"]?[\w]+[`"]?)\.([`"]?[\w]+[`"]?)\.([`"]?[\w]+[`"]?)',
                r'CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([`"]?[\w]+[`"]?)\.([`"]?[\w]+[`"]?)',
                r'CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([`"]?[\w]+[`"]?)'
            ]
            
            database, schema, table = "", "default", ""
            
            for pattern in table_patterns:
                match = re.search(pattern, ddl, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    if len(groups) == 3:
                        database, schema, table = groups
                    elif len(groups) == 2:
                        schema, table = groups
                        database = "default"
                    else:
                        table = groups[0]
                        schema = "default"
                        database = "default"
                    break
            
            if not table:
                return None
            
            # 清理引号
            database = database.strip('`"')
            schema = schema.strip('`"')
            table = table.strip('`"')
            
            # 提取字段定义部分
            fields_match = re.search(r'\((.*?)\)(?:\s*(?:ENGINE|DISTSTYLE|COMMENT|WITH|PARTITION)|\s*$)', ddl, re.DOTALL | re.IGNORECASE)
            if not fields_match:
                return None
            
            fields_section = fields_match.group(1)
            
            # 解析字段
            fields = self._parse_fields(fields_section)
            primary_keys = self._extract_primary_keys(fields_section)
            
            # 提取表注释
            comment_match = re.search(r'COMMENT\s*=?\s*[\'"]([^\'"]*)[\'"]', ddl, re.IGNORECASE)
            table_comment = comment_match.group(1) if comment_match else None
            
            return TableInfo(
                database=database,
                schema=schema,
                table=table,
                fields=fields,
                primary_keys=primary_keys,
                comment=table_comment
            )
            
        except Exception as e:
            print(f"解析表DDL失败: {str(e)}")
            return None
    
    def _parse_fields(self, fields_section: str) -> List[FieldInfo]:
        """解析字段定义"""
        fields = []
        field_lines = self._split_field_lines(fields_section)
        
        for line in field_lines:
            line = line.strip()
            if not line or line.upper().startswith(('PRIMARY KEY', 'UNIQUE', 'INDEX', 'KEY', 'CONSTRAINT')):
                continue
            
            field_info = self._parse_single_field(line)
            if field_info:
                fields.append(field_info)
        
        return fields
    
    def _split_field_lines(self, fields_section: str) -> List[str]:
        """智能分割字段行，处理括号内的逗号"""
        lines = []
        current_line = ""
        paren_count = 0
        in_quotes = False
        quote_char = None
        
        for char in fields_section:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif not in_quotes:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == ',' and paren_count == 0:
                    lines.append(current_line.strip())
                    current_line = ""
                    continue
            
            current_line += char
        
        if current_line.strip():
            lines.append(current_line.strip())
        
        return lines
    
    def _parse_single_field(self, field_line: str) -> Optional[FieldInfo]:
        """解析单个字段定义"""
        try:
            # 基本字段解析正则
            field_pattern = r'^([`"]?[\w]+[`"]?)\s+([\w()]+(?:\(\d+(?:,\s*\d+)?\))?)'
            match = re.match(field_pattern, field_line, re.IGNORECASE)
            
            if not match:
                return None
            
            field_name = match.group(1).strip('`"')
            field_type = match.group(2)
            
            # 检查NULL约束
            nullable = not bool(re.search(r'\bNOT\s+NULL\b', field_line, re.IGNORECASE))
            
            # 提取默认值
            default_match = re.search(r'DEFAULT\s+([^,\s]+)', field_line, re.IGNORECASE)
            default_value = default_match.group(1) if default_match else None
            
            # 提取注释
            comment_match = re.search(r'COMMENT\s*[\'"]([^\'"]*)[\'"]', field_line, re.IGNORECASE)
            comment = comment_match.group(1) if comment_match else None
            
            return FieldInfo(
                name=field_name,
                type=field_type,
                nullable=nullable,
                default_value=default_value,
                comment=comment
            )
            
        except Exception as e:
            print(f"解析字段失败: {field_line}, 错误: {str(e)}")
            return None
    
    def _extract_primary_keys(self, fields_section: str) -> List[str]:
        """提取主键字段"""
        primary_keys = []
        
        # 查找PRIMARY KEY定义
        pk_patterns = [
            r'PRIMARY\s+KEY\s*\(\s*([^)]+)\s*\)',
            r'PRIMARY\s+KEY\s+([`"]?[\w]+[`"]?)'
        ]
        
        for pattern in pk_patterns:
            matches = re.findall(pattern, fields_section, re.IGNORECASE)
            for match in matches:
                # 分割多个主键字段
                keys = [key.strip().strip('`"') for key in match.split(',')]
                primary_keys.extend(keys)
        
        return list(set(primary_keys))  # 去重
    
    def get_tables_by_schema(self) -> Dict[str, List[TableInfo]]:
        """按Schema分组获取表信息"""
        return dict(self.parsed_data)
    
    def get_all_schemas(self) -> List[str]:
        """获取所有Schema列表"""
        return list(self.parsed_data.keys())
    
    def get_table_count(self) -> int:
        """获取表总数"""
        return len(self.tables)
    
    def get_field_count(self) -> int:
        """获取字段总数"""
        return sum(len(table.fields) for table in self.tables)