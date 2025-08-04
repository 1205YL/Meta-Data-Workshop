import re
from typing import List, Dict, Any, Optional, Tuple
from .ddl_parser import TableInfo, FieldInfo

class FieldTypeConverter:
    """字段类型转换器"""
    
    def __init__(self):
        # 内置通用转换规则
        self.builtin_rules = {
            # MySQL到Oracle
            'mysql_to_oracle': {
                'INT': 'NUMBER(10)',
                'BIGINT': 'NUMBER(19)',
                'VARCHAR': 'VARCHAR2',
                'TEXT': 'CLOB',
                'DATETIME': 'DATE',
                'TIMESTAMP': 'TIMESTAMP',
                'DECIMAL': 'NUMBER',
                'TINYINT': 'NUMBER(3)',
                'SMALLINT': 'NUMBER(5)',
                'MEDIUMINT': 'NUMBER(7)',
                'FLOAT': 'BINARY_FLOAT',
                'DOUBLE': 'BINARY_DOUBLE'
            },
            # Oracle到MySQL
            'oracle_to_mysql': {
                'NUMBER': 'DECIMAL',
                'VARCHAR2': 'VARCHAR',
                'CLOB': 'TEXT',
                'DATE': 'DATETIME',
                'TIMESTAMP': 'TIMESTAMP',
                'BINARY_FLOAT': 'FLOAT',
                'BINARY_DOUBLE': 'DOUBLE'
            },
            # MySQL到PostgreSQL
            'mysql_to_postgresql': {
                'INT': 'INTEGER',
                'BIGINT': 'BIGINT',
                'VARCHAR': 'VARCHAR',
                'TEXT': 'TEXT',
                'DATETIME': 'TIMESTAMP',
                'TIMESTAMP': 'TIMESTAMP',
                'DECIMAL': 'DECIMAL',
                'TINYINT': 'SMALLINT',
                'SMALLINT': 'SMALLINT',
                'MEDIUMINT': 'INTEGER',
                'FLOAT': 'REAL',
                'DOUBLE': 'DOUBLE PRECISION'
            },
            # PostgreSQL到MySQL
            'postgresql_to_mysql': {
                'INTEGER': 'INT',
                'BIGINT': 'BIGINT',
                'VARCHAR': 'VARCHAR',
                'TEXT': 'TEXT',
                'TIMESTAMP': 'TIMESTAMP',
                'DECIMAL': 'DECIMAL',
                'SMALLINT': 'SMALLINT',
                'REAL': 'FLOAT',
                'DOUBLE PRECISION': 'DOUBLE'
            }
        }
        
        self.custom_rules = {}
    
    def add_custom_rule(self, rule_name: str, mapping: Dict[str, str]):
        """添加自定义转换规则"""
        self.custom_rules[rule_name] = mapping
    
    def get_available_rules(self) -> List[str]:
        """获取可用的转换规则列表"""
        return list(self.builtin_rules.keys()) + list(self.custom_rules.keys())
    
    def convert_field_type(self, field_type: str, rule_name: str) -> str:
        """
        转换字段类型
        
        Args:
            field_type: 原字段类型
            rule_name: 转换规则名称
            
        Returns:
            转换后的字段类型
        """
        rules = self.builtin_rules.get(rule_name) or self.custom_rules.get(rule_name)
        if not rules:
            return field_type
        
        # 提取基本类型（去除长度等修饰符）
        base_type = self._extract_base_type(field_type)
        
        # 查找转换规则
        for old_type, new_type in rules.items():
            if base_type.upper() == old_type.upper():
                # 保留原有的长度等修饰符
                return self._preserve_type_modifiers(field_type, new_type)
        
        return field_type
    
    def _extract_base_type(self, field_type: str) -> str:
        """提取基本数据类型"""
        match = re.match(r'^([A-Za-z_]+)', field_type)
        return match.group(1) if match else field_type
    
    def _preserve_type_modifiers(self, original_type: str, new_base_type: str) -> str:
        """保留类型修饰符（如长度、精度等）"""
        # 提取括号内的内容
        modifier_match = re.search(r'\(([^)]+)\)', original_type)
        if modifier_match:
            modifiers = modifier_match.group(1)
            return f"{new_base_type}({modifiers})"
        return new_base_type


class SystemFieldManager:
    """系统字段管理器"""
    
    def __init__(self):
        # 预定义系统字段模板
        self.system_field_templates = {
            'audit_fields': [
                FieldInfo('created_at', 'TIMESTAMP', False, 'CURRENT_TIMESTAMP', '创建时间'),
                FieldInfo('updated_at', 'TIMESTAMP', False, 'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', '更新时间'),
                FieldInfo('created_by', 'VARCHAR(50)', True, None, '创建人'),
                FieldInfo('updated_by', 'VARCHAR(50)', True, None, '更新人')
            ],
            'version_control': [
                FieldInfo('version', 'INT', False, '1', '版本号'),
                FieldInfo('is_deleted', 'TINYINT', False, '0', '是否删除（0:否，1:是）')
            ],
            'tenant_fields': [
                FieldInfo('tenant_id', 'VARCHAR(32)', False, None, '租户ID'),
                FieldInfo('org_id', 'VARCHAR(32)', True, None, '组织ID')
            ]
        }
    
    def get_system_field_templates(self) -> Dict[str, List[FieldInfo]]:
        """获取系统字段模板"""
        return self.system_field_templates
    
    def add_custom_template(self, template_name: str, fields: List[FieldInfo]):
        """添加自定义字段模板"""
        self.system_field_templates[template_name] = fields
    
    def add_system_fields_to_table(self, table: TableInfo, template_name: str, position: str = 'end') -> TableInfo:
        """
        为表添加系统字段
        
        Args:
            table: 表信息
            template_name: 字段模板名称
            position: 添加位置 ('start', 'end')
            
        Returns:
            更新后的表信息
        """
        if template_name not in self.system_field_templates:
            raise ValueError(f"未找到字段模板: {template_name}")
        
        system_fields = self.system_field_templates[template_name].copy()
        
        # 检查字段是否已存在
        existing_field_names = {field.name.lower() for field in table.fields}
        new_fields = [field for field in system_fields if field.name.lower() not in existing_field_names]
        
        if position == 'start':
            table.fields = new_fields + table.fields
        else:  # end
            table.fields.extend(new_fields)
        
        return table


class FieldManager:
    """字段管理器主类"""
    
    def __init__(self):
        self.type_converter = FieldTypeConverter()
        self.system_field_manager = SystemFieldManager()
    
    def batch_convert_field_types(self, tables: List[TableInfo], rule_name: str) -> List[TableInfo]:
        """
        批量转换字段类型
        
        Args:
            tables: 表信息列表
            rule_name: 转换规则名称
            
        Returns:
            转换后的表信息列表
        """
        converted_tables = []
        
        for table in tables:
            new_table = TableInfo(
                database=table.database,
                schema=table.schema,
                table=table.table,
                fields=[],
                primary_keys=table.primary_keys.copy(),
                comment=table.comment
            )
            
            for field in table.fields:
                new_field = FieldInfo(
                    name=field.name,
                    type=self.type_converter.convert_field_type(field.type, rule_name),
                    nullable=field.nullable,
                    default_value=field.default_value,
                    comment=field.comment
                )
                new_table.fields.append(new_field)
            
            converted_tables.append(new_table)
        
        return converted_tables
    
    def batch_add_system_fields(self, tables: List[TableInfo], template_name: str, 
                               position: str = 'end', filter_regex: Optional[str] = None) -> List[TableInfo]:
        """
        批量添加系统字段
        
        Args:
            tables: 表信息列表
            template_name: 字段模板名称
            position: 添加位置
            filter_regex: 表名过滤正则表达式
            
        Returns:
            更新后的表信息列表
        """
        updated_tables = []
        
        for table in tables:
            # 如果指定了过滤规则，检查表名是否匹配
            if filter_regex and not re.match(filter_regex, table.table, re.IGNORECASE):
                updated_tables.append(table)
                continue
            
            try:
                updated_table = self.system_field_manager.add_system_fields_to_table(
                    table, template_name, position
                )
                updated_tables.append(updated_table)
            except Exception as e:
                print(f"为表 {table.table} 添加系统字段失败: {str(e)}")
                updated_tables.append(table)
        
        return updated_tables
    
    def create_field_comparison_report(self, original_tables: List[TableInfo], 
                                     modified_tables: List[TableInfo]) -> Dict[str, Any]:
        """
        创建字段变更对比报告
        
        Args:
            original_tables: 原始表信息
            modified_tables: 修改后表信息
            
        Returns:
            对比报告
        """
        report = {
            'summary': {
                'total_tables': len(original_tables),
                'modified_tables': 0,
                'added_fields': 0,
                'modified_fields': 0
            },
            'details': []
        }
        
        # 创建表名到表信息的映射
        original_map = {f"{table.schema}.{table.table}": table for table in original_tables}
        modified_map = {f"{table.schema}.{table.table}": table for table in modified_tables}
        
        for table_key, original_table in original_map.items():
            if table_key not in modified_map:
                continue
                
            modified_table = modified_map[table_key]
            table_changes = self._compare_table_fields(original_table, modified_table)
            
            if table_changes['has_changes']:
                report['summary']['modified_tables'] += 1
                report['summary']['added_fields'] += len(table_changes['added_fields'])
                report['summary']['modified_fields'] += len(table_changes['modified_fields'])
                report['details'].append(table_changes)
        
        return report
    
    def _compare_table_fields(self, original_table: TableInfo, modified_table: TableInfo) -> Dict[str, Any]:
        """比较两个表的字段差异"""
        original_fields = {field.name: field for field in original_table.fields}
        modified_fields = {field.name: field for field in modified_table.fields}
        
        added_fields = []
        modified_field_changes = []
        
        # 检查新增字段
        for field_name, field in modified_fields.items():
            if field_name not in original_fields:
                added_fields.append({
                    'name': field.name,
                    'type': field.type,
                    'nullable': field.nullable,
                    'default_value': field.default_value,
                    'comment': field.comment
                })
        
        # 检查修改的字段
        for field_name, modified_field in modified_fields.items():
            if field_name in original_fields:
                original_field = original_fields[field_name]
                changes = {}
                
                if original_field.type != modified_field.type:
                    changes['type'] = {
                        'old': original_field.type,
                        'new': modified_field.type
                    }
                
                if original_field.nullable != modified_field.nullable:
                    changes['nullable'] = {
                        'old': original_field.nullable,
                        'new': modified_field.nullable
                    }
                
                if original_field.default_value != modified_field.default_value:
                    changes['default_value'] = {
                        'old': original_field.default_value,
                        'new': modified_field.default_value
                    }
                
                if changes:
                    modified_field_changes.append({
                        'field_name': field_name,
                        'changes': changes
                    })
        
        return {
            'table_name': f"{original_table.schema}.{original_table.table}",
            'has_changes': bool(added_fields or modified_field_changes),
            'added_fields': added_fields,
            'modified_fields': modified_field_changes
        }
    
    def get_conversion_rules(self) -> List[str]:
        """获取可用的类型转换规则"""
        return self.type_converter.get_available_rules()
    
    def get_system_field_templates(self) -> Dict[str, List[FieldInfo]]:
        """获取系统字段模板"""
        return self.system_field_manager.get_system_field_templates()
    
    def add_custom_conversion_rule(self, rule_name: str, mapping: Dict[str, str]):
        """添加自定义转换规则"""
        self.type_converter.add_custom_rule(rule_name, mapping)
    
    def add_custom_field_template(self, template_name: str, fields: List[FieldInfo]):
        """添加自定义字段模板"""
        self.system_field_manager.add_custom_template(template_name, fields)