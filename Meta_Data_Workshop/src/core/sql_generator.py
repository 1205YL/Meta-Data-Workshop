from typing import List, Dict, Any, Optional
from .ddl_parser import TableInfo, FieldInfo

class SQLGenerator:
    """SQL语句生成器"""
    
    def __init__(self):
        self.sql_dialect = 'mysql'  # 默认方言
        
    def set_dialect(self, dialect: str):
        """设置SQL方言 (mysql, oracle, postgresql, sqlserver)"""
        self.sql_dialect = dialect.lower()
    
    def generate_drop_table_statements(self, tables: List[TableInfo], 
                                     include_if_exists: bool = True,
                                     add_comments: bool = True) -> List[str]:
        """
        生成DROP TABLE语句
        
        Args:
            tables: 表信息列表
            include_if_exists: 是否包含IF EXISTS子句
            add_comments: 是否添加注释
            
        Returns:
            DROP TABLE语句列表
        """
        drop_statements = []
        
        for table in tables:
            # 构建完整表名
            full_table_name = self._build_full_table_name(table)
            
            # 生成DROP语句
            if include_if_exists and self.sql_dialect in ['mysql', 'postgresql']:
                drop_sql = f"DROP TABLE IF EXISTS {full_table_name};"
            else:
                drop_sql = f"DROP TABLE {full_table_name};"
            
            # 添加注释
            if add_comments:
                comment = f"-- 删除表: {table.table}"
                if table.comment:
                    comment += f" ({table.comment})"
                drop_statements.append(comment)
            
            drop_statements.append(drop_sql)
            
            if add_comments:
                drop_statements.append("")  # 空行分隔
        
        return drop_statements
    
    def generate_create_table_statements(self, tables: List[TableInfo],
                                       include_if_not_exists: bool = True,
                                       add_comments: bool = True) -> List[str]:
        """
        生成CREATE TABLE语句
        
        Args:
            tables: 表信息列表
            include_if_not_exists: 是否包含IF NOT EXISTS子句
            add_comments: 是否添加注释
            
        Returns:
            CREATE TABLE语句列表
        """
        create_statements = []
        
        for table in tables:
            # 添加表注释
            if add_comments:
                comment = f"-- 创建表: {table.table}"
                if table.comment:
                    comment += f" ({table.comment})"
                create_statements.append(comment)
            
            # 构建CREATE TABLE语句
            full_table_name = self._build_full_table_name(table)
            
            if include_if_not_exists and self.sql_dialect in ['mysql', 'postgresql']:
                create_sql = f"CREATE TABLE IF NOT EXISTS {full_table_name} ("
            else:
                create_sql = f"CREATE TABLE {full_table_name} ("
            
            create_statements.append(create_sql)
            
            # 添加字段定义
            field_definitions = []
            for field in table.fields:
                field_def = self._generate_field_definition(field, table.primary_keys)
                field_definitions.append(f"    {field_def}")
            
            # 添加主键定义
            if table.primary_keys:
                pk_fields = ', '.join(table.primary_keys)
                field_definitions.append(f"    PRIMARY KEY ({pk_fields})")
            
            # 添加字段定义，正确处理逗号
            for i, field_def in enumerate(field_definitions):
                if i < len(field_definitions) - 1:
                    create_statements.append(field_def + ",")
                else:
                    create_statements.append(field_def)
            
            # 结束CREATE TABLE语句
            create_statements.append(");")
            
            if add_comments:
                create_statements.append("")  # 空行分隔
        
        return create_statements
    
    def generate_insert_select_statements(self, source_tables: List[TableInfo],
                                        target_tables: List[TableInfo],
                                        include_case_when: bool = False,
                                        field_mapping: Optional[Dict[str, Dict[str, str]]] = None) -> List[str]:
        """
        生成INSERT...SELECT语句
        
        Args:
            source_tables: 源表信息列表
            target_tables: 目标表信息列表
            include_case_when: 是否包含CASE WHEN逻辑
            field_mapping: 字段映射关系 {table_name: {source_field: target_field}}
            
        Returns:
            INSERT...SELECT语句列表
        """
        insert_statements = []
        
        # 创建表名到表信息的映射
        source_map = {f"{table.schema}.{table.table}": table for table in source_tables}
        target_map = {f"{table.schema}.{table.table}": table for table in target_tables}
        
        for table_key, target_table in target_map.items():
            if table_key not in source_map:
                continue
                
            source_table = source_map[table_key]
            
            # 生成INSERT...SELECT语句
            insert_sql = self._generate_insert_select_for_table(
                source_table, target_table, include_case_when, 
                field_mapping.get(table_key, {}) if field_mapping else {}
            )
            insert_statements.extend(insert_sql)
            insert_statements.append("")  # 空行分隔
        
        return insert_statements
    
    def _generate_insert_select_for_table(self, source_table: TableInfo, 
                                        target_table: TableInfo,
                                        include_case_when: bool,
                                        field_mapping: Dict[str, str]) -> List[str]:
        """为单个表生成INSERT...SELECT语句"""
        statements = []
        
        # 添加注释
        statements.append(f"-- 从 {source_table.schema}.{source_table.table} 迁移数据到 {target_table.schema}.{target_table.table}")
        
        # 构建目标字段列表
        target_fields = [field.name for field in target_table.fields]
        target_fields_str = ', '.join(target_fields)
        
        # 构建SELECT字段列表
        select_fields = []
        source_field_map = {field.name: field for field in source_table.fields}
        
        for target_field in target_table.fields:
            # 检查字段映射
            source_field_name = field_mapping.get(target_field.name, target_field.name)
            
            if source_field_name in source_field_map:
                source_field = source_field_map[source_field_name]
                
                if include_case_when:
                    # 生成CASE WHEN逻辑
                    case_when = self._generate_case_when_for_field(source_field, target_field)
                    select_fields.append(case_when)
                else:
                    select_fields.append(source_field_name)
            else:
                # 字段不存在，使用默认值或NULL
                if target_field.default_value:
                    select_fields.append(f"'{target_field.default_value}' AS {target_field.name}")
                else:
                    select_fields.append(f"NULL AS {target_field.name}")
        
        # 构建完整的INSERT...SELECT语句
        target_full_name = self._build_full_table_name(target_table)
        source_full_name = self._build_full_table_name(source_table)
        
        statements.append(f"INSERT INTO {target_full_name}")
        statements.append(f"({target_fields_str})")
        statements.append("SELECT")
        
        # 添加SELECT字段，除最后一个外都加逗号
        for i, field in enumerate(select_fields):
            if i < len(select_fields) - 1:
                statements.append(f"    {field},")
            else:
                statements.append(f"    {field}")
        
        statements.append(f"FROM {source_full_name};")
        
        return statements
    
    def _generate_case_when_for_field(self, source_field: FieldInfo, target_field: FieldInfo) -> str:
        """为字段生成CASE WHEN逻辑"""
        field_name = source_field.name
        
        # 根据字段类型生成不同的CASE WHEN逻辑
        if 'varchar' in source_field.type.lower() or 'char' in source_field.type.lower():
            # 字符串类型处理
            case_when = f"""CASE 
        WHEN {field_name} IS NULL OR {field_name} = '' THEN '{target_field.default_value or ''}'
        ELSE {field_name}
    END AS {target_field.name}"""
        elif 'int' in source_field.type.lower() or 'number' in source_field.type.lower():
            # 数值类型处理
            default_val = target_field.default_value or '0'
            case_when = f"""CASE 
        WHEN {field_name} IS NULL THEN {default_val}
        ELSE {field_name}
    END AS {target_field.name}"""
        elif 'date' in source_field.type.lower() or 'time' in source_field.type.lower():
            # 日期时间类型处理
            default_val = target_field.default_value or 'CURRENT_TIMESTAMP'
            case_when = f"""CASE 
        WHEN {field_name} IS NULL THEN {default_val}
        ELSE {field_name}
    END AS {target_field.name}"""
        else:
            # 其他类型的通用处理
            case_when = f"""CASE 
        WHEN {field_name} IS NULL THEN {target_field.default_value or 'NULL'}
        ELSE {field_name}
    END AS {target_field.name}"""
        
        return case_when
    
    def _generate_field_definition(self, field: FieldInfo, primary_keys: List[str]) -> str:
        """生成字段定义"""
        definition = f"{field.name} {field.type}"
        
        # 添加NULL约束
        if not field.nullable:
            definition += " NOT NULL"
        
        # 添加默认值
        if field.default_value:
            definition += f" DEFAULT {field.default_value}"
        
        # 添加注释（根据SQL方言）
        if field.comment:
            if self.sql_dialect == 'mysql':
                definition += f" COMMENT '{field.comment}'"
            elif self.sql_dialect == 'postgresql':
                # PostgreSQL在CREATE TABLE后单独添加注释
                pass
        
        return definition
    
    def _build_full_table_name(self, table: TableInfo) -> str:
        """构建完整的表名"""
        if table.database and table.database != 'default':
            if table.schema and table.schema != 'default':
                return f"{table.database}.{table.schema}.{table.table}"
            else:
                return f"{table.database}.{table.table}"
        elif table.schema and table.schema != 'default':
            return f"{table.schema}.{table.table}"
        else:
            return table.table
    
    def generate_table_statistics_query(self, tables: List[TableInfo]) -> List[str]:
        """生成表统计信息查询语句"""
        queries = []
        
        for table in tables:
            full_name = self._build_full_table_name(table)
            
            queries.append(f"-- 统计表 {table.table} 的记录数")
            queries.append(f"SELECT COUNT(*) AS record_count FROM {full_name};")
            queries.append("")
        
        return queries
    
    def generate_table_structure_query(self, tables: List[TableInfo]) -> List[str]:
        """生成表结构查询语句"""
        queries = []
        
        for table in tables:
            full_name = self._build_full_table_name(table)
            
            queries.append(f"-- 查看表 {table.table} 的结构")
            
            if self.sql_dialect == 'mysql':
                queries.append(f"DESCRIBE {full_name};")
            elif self.sql_dialect == 'postgresql':
                queries.append(f"\\d {full_name}")
            elif self.sql_dialect == 'oracle':
                queries.append(f"DESC {full_name};")
            elif self.sql_dialect == 'sqlserver':
                queries.append(f"SP_HELP '{full_name}';")
            
            queries.append("")
        
        return queries
    
    def save_sql_to_file(self, sql_statements: List[str], file_path: str) -> bool:
        """将SQL语句保存到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for statement in sql_statements:
                    f.write(statement + '\n')
            return True
        except Exception as e:
            print(f"保存SQL文件失败: {str(e)}")
            return False
    
    def generate_batch_sql_file(self, tables: List[TableInfo], output_path: str,
                              include_drop: bool = True,
                              include_create: bool = True,
                              include_statistics: bool = False) -> bool:
        """生成批量SQL文件"""
        all_statements = []
        
        # 添加文件头注释
        all_statements.extend([
            "-- ========================================",
            "-- Meta Data Workshop 自动生成的SQL脚本",
            f"-- 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"-- 总表数: {len(tables)}",
            "-- ========================================",
            ""
        ])
        
        if include_drop:
            all_statements.extend([
                "-- ========================================",
                "-- DROP TABLE 语句",
                "-- ========================================",
                ""
            ])
            all_statements.extend(self.generate_drop_table_statements(tables))
            all_statements.append("")
        
        if include_create:
            all_statements.extend([
                "-- ========================================", 
                "-- CREATE TABLE 语句",
                "-- ========================================",
                ""
            ])
            all_statements.extend(self.generate_create_table_statements(tables))
            all_statements.append("")
        
        if include_statistics:
            all_statements.extend([
                "-- ========================================",
                "-- 统计信息查询语句", 
                "-- ========================================",
                ""
            ])
            all_statements.extend(self.generate_table_statistics_query(tables))
        
        return self.save_sql_to_file(all_statements, output_path)