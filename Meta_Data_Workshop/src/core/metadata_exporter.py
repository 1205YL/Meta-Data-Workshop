import pandas as pd
import json
import os
from typing import List, Dict, Any, Optional
from .ddl_parser import TableInfo, FieldInfo

class MetadataExporter:
    """元数据导出器"""
    
    def __init__(self):
        self.supported_formats = ['excel', 'csv', 'json']
    
    def export_all_merged(self, tables: List[TableInfo], output_path: str, format_type: str = 'excel') -> bool:
        """
        全量合并导出：将所有表的元数据合并到一个文件
        
        Args:
            tables: 表信息列表
            output_path: 输出文件路径
            format_type: 导出格式 (excel/csv/json)
            
        Returns:
            导出是否成功
        """
        try:
            if format_type not in self.supported_formats:
                raise ValueError(f"不支持的导出格式: {format_type}")
            
            # 准备数据
            all_data = []
            for table in tables:
                for field in table.fields:
                    all_data.append({
                        '数据库': table.database,
                        '模式': table.schema,
                        '表名': table.table,
                        '字段名': field.name,
                        '字段类型': field.type,
                        '是否可空': '是' if field.nullable else '否',
                        '默认值': field.default_value or '',
                        '是否主键': '是' if field.name in table.primary_keys else '否',
                        '字段注释': field.comment or '',
                        '表注释': table.comment or ''
                    })
            
            if format_type == 'excel':
                return self._export_to_excel_single(all_data, output_path)
            elif format_type == 'csv':
                return self._export_to_csv(all_data, output_path)
            elif format_type == 'json':
                return self._export_to_json_merged(tables, output_path)
                
        except Exception as e:
            print(f"导出失败: {str(e)}")
            return False
    
    def export_by_schema(self, tables: List[TableInfo], output_dir: str, format_type: str = 'excel') -> bool:
        """
        按Schema分层导出
        
        Args:
            tables: 表信息列表
            output_dir: 输出目录
            format_type: 导出格式
            
        Returns:
            导出是否成功
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # 按schema分组
            schema_groups = {}
            for table in tables:
                if table.schema not in schema_groups:
                    schema_groups[table.schema] = []
                schema_groups[table.schema].append(table)
            
            success_count = 0
            for schema, schema_tables in schema_groups.items():
                file_name = f"schema_{schema}.{self._get_file_extension(format_type)}"
                file_path = os.path.join(output_dir, file_name)
                
                if format_type == 'excel':
                    if self._export_schema_to_excel(schema_tables, file_path):
                        success_count += 1
                elif format_type == 'csv':
                    schema_data = self._prepare_schema_data(schema_tables)
                    if self._export_to_csv(schema_data, file_path):
                        success_count += 1
                elif format_type == 'json':
                    if self._export_to_json_merged(schema_tables, file_path):
                        success_count += 1
            
            return success_count == len(schema_groups)
            
        except Exception as e:
            print(f"按Schema导出失败: {str(e)}")
            return False
    
    def export_by_table(self, tables: List[TableInfo], output_dir: str, format_type: str = 'excel') -> bool:
        """
        按表分层导出
        
        Args:
            tables: 表信息列表
            output_dir: 输出目录
            format_type: 导出格式
            
        Returns:
            导出是否成功
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            success_count = 0
            for table in tables:
                file_name = f"table_{table.schema}_{table.table}.{self._get_file_extension(format_type)}"
                file_path = os.path.join(output_dir, file_name)
                
                table_data = []
                for field in table.fields:
                    table_data.append({
                        '字段名': field.name,
                        '字段类型': field.type,
                        '是否可空': '是' if field.nullable else '否',
                        '默认值': field.default_value or '',
                        '是否主键': '是' if field.name in table.primary_keys else '否',
                        '字段注释': field.comment or ''
                    })
                
                if format_type == 'excel':
                    if self._export_to_excel_single(table_data, file_path):
                        success_count += 1
                elif format_type == 'csv':
                    if self._export_to_csv(table_data, file_path):
                        success_count += 1
                elif format_type == 'json':
                    if self._export_to_json_merged([table], file_path):
                        success_count += 1
            
            return success_count == len(tables)
            
        except Exception as e:
            print(f"按表导出失败: {str(e)}")
            return False
    
    def export_to_excel_multi_sheet(self, tables: List[TableInfo], output_path: str) -> bool:
        """
        导出到Excel多工作表（每个Schema一个工作表）
        
        Args:
            tables: 表信息列表
            output_path: 输出文件路径
            
        Returns:
            导出是否成功
        """
        try:
            # 按schema分组
            schema_groups = {}
            for table in tables:
                if table.schema not in schema_groups:
                    schema_groups[table.schema] = []
                schema_groups[table.schema].append(table)
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for schema, schema_tables in schema_groups.items():
                    schema_data = self._prepare_schema_data(schema_tables)
                    df = pd.DataFrame(schema_data)
                    
                    # 确保sheet名称符合Excel规范
                    sheet_name = self._clean_sheet_name(schema)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return True
            
        except Exception as e:
            print(f"导出到Excel多工作表失败: {str(e)}")
            return False
    
    def _export_to_excel_single(self, data: List[Dict], output_path: str) -> bool:
        """导出到单个Excel文件"""
        try:
            df = pd.DataFrame(data)
            df.to_excel(output_path, index=False)
            return True
        except Exception as e:
            print(f"导出Excel失败: {str(e)}")
            return False
    
    def _export_schema_to_excel(self, schema_tables: List[TableInfo], output_path: str) -> bool:
        """导出单个Schema到Excel"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for table in schema_tables:
                    table_data = []
                    for field in table.fields:
                        table_data.append({
                            '字段名': field.name,
                            '字段类型': field.type,
                            '是否可空': '是' if field.nullable else '否',
                            '默认值': field.default_value or '',
                            '是否主键': '是' if field.name in table.primary_keys else '否',
                            '字段注释': field.comment or ''
                        })
                    
                    df = pd.DataFrame(table_data)
                    sheet_name = self._clean_sheet_name(table.table)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return True
        except Exception as e:
            print(f"导出Schema到Excel失败: {str(e)}")
            return False
    
    def _export_to_csv(self, data: List[Dict], output_path: str) -> bool:
        """导出到CSV文件"""
        try:
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"导出CSV失败: {str(e)}")
            return False
    
    def _export_to_json_merged(self, tables: List[TableInfo], output_path: str) -> bool:
        """导出到JSON文件"""
        try:
            json_data = {
                'metadata': {
                    'total_tables': len(tables),
                    'total_fields': sum(len(table.fields) for table in tables)
                },
                'tables': []
            }
            
            for table in tables:
                table_data = {
                    'database': table.database,
                    'schema': table.schema,
                    'table': table.table,
                    'comment': table.comment,
                    'primary_keys': table.primary_keys,
                    'fields': [
                        {
                            'name': field.name,
                            'type': field.type,
                            'nullable': field.nullable,
                            'default_value': field.default_value,
                            'comment': field.comment
                        }
                        for field in table.fields
                    ]
                }
                json_data['tables'].append(table_data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"导出JSON失败: {str(e)}")
            return False
    
    def _prepare_schema_data(self, schema_tables: List[TableInfo]) -> List[Dict]:
        """准备Schema数据"""
        data = []
        for table in schema_tables:
            for field in table.fields:
                data.append({
                    '表名': table.table,
                    '字段名': field.name,
                    '字段类型': field.type,
                    '是否可空': '是' if field.nullable else '否',
                    '默认值': field.default_value or '',
                    '是否主键': '是' if field.name in table.primary_keys else '否',
                    '字段注释': field.comment or '',
                    '表注释': table.comment or ''
                })
        return data
    
    def _clean_sheet_name(self, name: str) -> str:
        """清理Excel工作表名称"""
        # Excel工作表名不能包含这些字符: \ / ? * [ ] :
        invalid_chars = ['\\', '/', '?', '*', '[', ']', ':']
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Excel工作表名长度限制为31个字符
        if len(name) > 31:
            name = name[:31]
        
        return name
    
    def _get_file_extension(self, format_type: str) -> str:
        """获取文件扩展名"""
        extensions = {
            'excel': 'xlsx',
            'csv': 'csv',
            'json': 'json'
        }
        return extensions.get(format_type, 'txt')
    
    def get_export_summary(self, tables: List[TableInfo]) -> Dict[str, Any]:
        """获取导出摘要信息"""
        schema_count = len(set(table.schema for table in tables))
        table_count = len(tables)
        field_count = sum(len(table.fields) for table in tables)
        
        return {
            'schema_count': schema_count,
            'table_count': table_count,
            'field_count': field_count,
            'schemas': list(set(table.schema for table in tables))
        }