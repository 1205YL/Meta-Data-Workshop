import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from typing import List, Callable, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ddl_parser import TableInfo
from core.metadata_exporter import MetadataExporter
from core.field_manager import FieldManager
from core.sql_generator import SQLGenerator

class ExportDialog:
    """元数据导出对话框"""
    
    def __init__(self, parent, tables: List[TableInfo], exporter: MetadataExporter):
        self.parent = parent
        self.tables = tables
        self.exporter = exporter
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("导出元数据")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.center_window()
        
        # 创建界面
        self.create_widgets()
        
    def center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 导出格式选择
        format_frame = ttk.LabelFrame(main_frame, text="导出格式")
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.format_var = tk.StringVar(value="excel")
        ttk.Radiobutton(format_frame, text="Excel (.xlsx)", variable=self.format_var, value="excel").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Radiobutton(format_frame, text="CSV (.csv)", variable=self.format_var, value="csv").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Radiobutton(format_frame, text="JSON (.json)", variable=self.format_var, value="json").pack(anchor=tk.W, padx=10, pady=5)
        
        # 导出方式选择
        mode_frame = ttk.LabelFrame(main_frame, text="导出方式")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="merged")
        ttk.Radiobutton(mode_frame, text="全量合并导出", variable=self.mode_var, value="merged").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Radiobutton(mode_frame, text="按Schema分层导出", variable=self.mode_var, value="schema").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Radiobutton(mode_frame, text="按表单独导出", variable=self.mode_var, value="table").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Radiobutton(mode_frame, text="Excel多工作表", variable=self.mode_var, value="multi_sheet").pack(anchor=tk.W, padx=10, pady=5)
        
        # 表选择
        table_frame = ttk.LabelFrame(main_frame, text="选择表")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 全选/反选按钮
        button_frame = ttk.Frame(table_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="全选", command=self.select_all_tables).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="反选", command=self.deselect_all_tables).pack(side=tk.LEFT)
        
        # 表列表
        list_frame = ttk.Frame(table_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # 创建带复选框的列表
        columns = ("选择", "Schema", "表名", "字段数")
        self.table_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        self.table_tree.heading("选择", text="选择")
        self.table_tree.heading("Schema", text="Schema")
        self.table_tree.heading("表名", text="表名")
        self.table_tree.heading("字段数", text="字段数")
        
        self.table_tree.column("选择", width=50)
        self.table_tree.column("Schema", width=120)
        self.table_tree.column("表名", width=150)
        self.table_tree.column("字段数", width=80)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.table_tree.yview)
        self.table_tree.configure(yscrollcommand=scrollbar.set)
        
        self.table_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定点击事件
        self.table_tree.bind("<Button-1>", self.on_table_click)
        
        # 填充表数据
        self.selected_tables = set()
        for i, table in enumerate(self.tables):
            item_id = self.table_tree.insert("", tk.END, values=(
                "☐", table.schema, table.table, len(table.fields)
            ))
            # 默认选中所有表
            self.selected_tables.add(item_id)
            self.table_tree.set(item_id, "选择", "☑")
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="导出", command=self.export_data).pack(side=tk.RIGHT)
        
    def on_table_click(self, event):
        """处理表点击事件"""
        item = self.table_tree.identify('item', event.x, event.y)
        column = self.table_tree.identify('column', event.x, event.y)
        
        if item and column == "#1":  # 点击选择列
            if item in self.selected_tables:
                self.selected_tables.remove(item)
                self.table_tree.set(item, "选择", "☐")
            else:
                self.selected_tables.add(item)
                self.table_tree.set(item, "选择", "☑")
                
    def select_all_tables(self):
        """全选表"""
        self.selected_tables.clear()
        for item in self.table_tree.get_children():
            self.selected_tables.add(item)
            self.table_tree.set(item, "选择", "☑")
            
    def deselect_all_tables(self):
        """反选表"""
        for item in self.table_tree.get_children():
            if item in self.selected_tables:
                self.selected_tables.remove(item)
                self.table_tree.set(item, "选择", "☐")
            else:
                self.selected_tables.add(item)
                self.table_tree.set(item, "选择", "☑")
                
    def export_data(self):
        """执行导出"""
        if not self.selected_tables:
            messagebox.showwarning("警告", "请至少选择一个表")
            return
            
        # 获取选中的表
        selected_table_indices = []
        for item in self.selected_tables:
            index = self.table_tree.index(item)
            selected_table_indices.append(index)
            
        selected_tables = [self.tables[i] for i in selected_table_indices]
        
        format_type = self.format_var.get()
        mode = self.mode_var.get()
        
        try:
            if mode == "merged":
                self.export_merged(selected_tables, format_type)
            elif mode == "schema":
                self.export_by_schema(selected_tables, format_type)
            elif mode == "table":
                self.export_by_table(selected_tables, format_type)
            elif mode == "multi_sheet":
                self.export_multi_sheet(selected_tables)
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：\n{str(e)}")
            
    def export_merged(self, tables: List[TableInfo], format_type: str):
        """全量合并导出"""
        file_ext = self.exporter._get_file_extension(format_type)
        file_path = filedialog.asksaveasfilename(
            title="保存导出文件",
            defaultextension=f".{file_ext}",
            filetypes=[(f"{format_type.upper()}文件", f"*.{file_ext}")]
        )
        
        if file_path:
            success = self.exporter.export_all_merged(tables, file_path, format_type)
            if success:
                messagebox.showinfo("成功", f"导出完成！\n文件保存至：{file_path}")
                self.dialog.destroy()
                
    def export_by_schema(self, tables: List[TableInfo], format_type: str):
        """按Schema分层导出"""
        output_dir = filedialog.askdirectory(title="选择导出目录")
        
        if output_dir:
            success = self.exporter.export_by_schema(tables, output_dir, format_type)
            if success:
                messagebox.showinfo("成功", f"按Schema导出完成！\n文件保存至：{output_dir}")
                self.dialog.destroy()
                
    def export_by_table(self, tables: List[TableInfo], format_type: str):
        """按表单独导出"""
        output_dir = filedialog.askdirectory(title="选择导出目录")
        
        if output_dir:
            success = self.exporter.export_by_table(tables, output_dir, format_type)
            if success:
                messagebox.showinfo("成功", f"按表导出完成！\n文件保存至：{output_dir}")
                self.dialog.destroy()
                
    def export_multi_sheet(self, tables: List[TableInfo]):
        """Excel多工作表导出"""
        file_path = filedialog.asksaveasfilename(
            title="保存Excel文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx")]
        )
        
        if file_path:
            success = self.exporter.export_to_excel_multi_sheet(tables, file_path)
            if success:
                messagebox.showinfo("成功", f"多工作表导出完成！\n文件保存至：{file_path}")
                self.dialog.destroy()


class FieldManagementDialog:
    """字段管理对话框"""
    
    def __init__(self, parent, tables: List[TableInfo], field_manager: FieldManager, 
                 callback: Callable[[List[TableInfo]], None]):
        self.parent = parent
        self.tables = tables
        self.field_manager = field_manager
        self.callback = callback
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("字段管理")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.center_window()
        
        # 创建界面
        self.create_widgets()
        
    def center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_widgets(self):
        """创建界面组件"""
        # 创建笔记本控件
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 字段类型转换标签页
        self.create_type_conversion_tab(notebook)
        
        # 系统字段添加标签页
        self.create_system_fields_tab(notebook)
        
        # 按钮框架
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="关闭", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
    def create_type_conversion_tab(self, parent):
        """创建字段类型转换标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="字段类型转换")
        
        # 转换规则选择
        rule_frame = ttk.LabelFrame(frame, text="选择转换规则")
        rule_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.conversion_rule_var = tk.StringVar()
        rules = self.field_manager.get_conversion_rules()
        
        if rules:
            self.conversion_rule_var.set(rules[0])
            rule_combo = ttk.Combobox(rule_frame, textvariable=self.conversion_rule_var, 
                                    values=rules, state="readonly")
            rule_combo.pack(fill=tk.X, padx=10, pady=10)
        else:
            ttk.Label(rule_frame, text="没有可用的转换规则").pack(padx=10, pady=10)
        
        # 表选择
        table_frame = ttk.LabelFrame(frame, text="选择要转换的表")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 表列表
        columns = ("Schema", "表名", "字段数")
        self.conversion_table_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.conversion_table_tree.heading(col, text=col)
            self.conversion_table_tree.column(col, width=150)
        
        # 添加滚动条
        conv_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.conversion_table_tree.yview)
        self.conversion_table_tree.configure(yscrollcommand=conv_scrollbar.set)
        
        self.conversion_table_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        conv_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        # 填充表数据
        for table in self.tables:
            self.conversion_table_tree.insert("", tk.END, values=(
                table.schema, table.table, len(table.fields)
            ))
        
        # 执行转换按钮
        ttk.Button(table_frame, text="执行类型转换", 
                  command=self.execute_type_conversion).pack(pady=(0, 10))
        
    def create_system_fields_tab(self, parent):
        """创建系统字段添加标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="系统字段添加")
        
        # 字段模板选择
        template_frame = ttk.LabelFrame(frame, text="选择字段模板")
        template_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.field_template_var = tk.StringVar()
        templates = list(self.field_manager.get_system_field_templates().keys())
        
        if templates:
            self.field_template_var.set(templates[0])
            template_combo = ttk.Combobox(template_frame, textvariable=self.field_template_var, 
                                        values=templates, state="readonly")
            template_combo.pack(fill=tk.X, padx=10, pady=5)
            template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)
        
        # 模板预览
        preview_frame = ttk.LabelFrame(frame, text="字段预览")
        preview_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.template_preview = scrolledtext.ScrolledText(preview_frame, height=6, wrap=tk.WORD)
        self.template_preview.pack(fill=tk.X, padx=10, pady=10)
        
        # 初始化预览
        if templates:
            self.update_template_preview()
        
        # 添加位置选择
        position_frame = ttk.LabelFrame(frame, text="添加位置")
        position_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.position_var = tk.StringVar(value="end")
        ttk.Radiobutton(position_frame, text="表开头", variable=self.position_var, value="start").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Radiobutton(position_frame, text="表结尾", variable=self.position_var, value="end").pack(anchor=tk.W, padx=10, pady=5)
        
        # 表过滤
        filter_frame = ttk.LabelFrame(frame, text="表过滤规则（正则表达式，可选）")
        filter_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.filter_regex_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filter_regex_var).pack(fill=tk.X, padx=10, pady=10)
        
        # 执行添加按钮
        ttk.Button(frame, text="添加系统字段", 
                  command=self.execute_add_system_fields).pack(pady=10)
        
    def on_template_selected(self, event=None):
        """模板选择事件"""
        self.update_template_preview()
        
    def update_template_preview(self):
        """更新模板预览"""
        template_name = self.field_template_var.get()
        if not template_name:
            return
            
        templates = self.field_manager.get_system_field_templates()
        if template_name in templates:
            fields = templates[template_name]
            
            preview_text = f"模板：{template_name}\n\n"
            for field in fields:
                preview_text += f"字段名：{field.name}\n"
                preview_text += f"类型：{field.type}\n"
                preview_text += f"可空：{'是' if field.nullable else '否'}\n"
                if field.default_value:
                    preview_text += f"默认值：{field.default_value}\n"
                if field.comment:
                    preview_text += f"注释：{field.comment}\n"
                preview_text += "-" * 30 + "\n"
            
            self.template_preview.delete(1.0, tk.END)
            self.template_preview.insert(1.0, preview_text)
            
    def execute_type_conversion(self):
        """执行字段类型转换"""
        selected_items = self.conversion_table_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择要转换的表")
            return
            
        rule_name = self.conversion_rule_var.get()
        if not rule_name:
            messagebox.showwarning("警告", "请选择转换规则")
            return
            
        try:
            # 获取选中的表
            selected_indices = [self.conversion_table_tree.index(item) for item in selected_items]
            selected_tables = [self.tables[i] for i in selected_indices]
            
            # 执行转换
            converted_tables = self.field_manager.batch_convert_field_types(selected_tables, rule_name)
            
            # 更新表数据
            for i, converted_table in enumerate(converted_tables):
                original_index = selected_indices[i]
                self.tables[original_index] = converted_table
            
            # 回调更新主界面
            self.callback(self.tables)
            
            messagebox.showinfo("成功", f"字段类型转换完成！\n共转换 {len(converted_tables)} 个表")
            
        except Exception as e:
            messagebox.showerror("错误", f"字段类型转换失败：\n{str(e)}")
            
    def execute_add_system_fields(self):
        """执行添加系统字段"""
        template_name = self.field_template_var.get()
        if not template_name:
            messagebox.showwarning("警告", "请选择字段模板")
            return
            
        position = self.position_var.get()
        filter_regex = self.filter_regex_var.get() or None
        
        try:
            # 执行添加
            updated_tables = self.field_manager.batch_add_system_fields(
                self.tables, template_name, position, filter_regex
            )
            
            # 更新表数据
            self.tables[:] = updated_tables
            
            # 回调更新主界面
            self.callback(self.tables)
            
            messagebox.showinfo("成功", f"系统字段添加完成！\n模板：{template_name}")
            
        except Exception as e:
            messagebox.showerror("错误", f"添加系统字段失败：\n{str(e)}")


class SQLGenerationDialog:
    """SQL生成对话框"""
    
    def __init__(self, parent, tables: List[TableInfo], sql_generator: SQLGenerator):
        self.parent = parent
        self.tables = tables
        self.sql_generator = sql_generator
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("SQL脚本生成")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.center_window()
        
        # 创建界面
        self.create_widgets()
        
    def center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧配置区域
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # SQL类型选择
        type_frame = ttk.LabelFrame(left_frame, text="SQL类型")
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.sql_types = {
            "drop_table": tk.BooleanVar(value=True),
            "create_table": tk.BooleanVar(value=True),
            "insert_select": tk.BooleanVar(value=False),
            "statistics": tk.BooleanVar(value=False)
        }
        
        ttk.Checkbutton(type_frame, text="DROP TABLE语句", 
                       variable=self.sql_types["drop_table"]).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(type_frame, text="CREATE TABLE语句", 
                       variable=self.sql_types["create_table"]).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(type_frame, text="INSERT...SELECT语句", 
                       variable=self.sql_types["insert_select"]).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(type_frame, text="统计查询语句", 
                       variable=self.sql_types["statistics"]).pack(anchor=tk.W, padx=5, pady=2)
        
        # 数据库方言选择
        dialect_frame = ttk.LabelFrame(left_frame, text="数据库方言")
        dialect_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dialect_var = tk.StringVar(value="mysql")
        dialects = ["mysql", "oracle", "postgresql", "sqlserver"]
        dialect_combo = ttk.Combobox(dialect_frame, textvariable=self.dialect_var, 
                                   values=dialects, state="readonly")
        dialect_combo.pack(fill=tk.X, padx=5, pady=5)
        
        # 生成选项
        options_frame = ttk.LabelFrame(left_frame, text="生成选项")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.include_comments = tk.BooleanVar(value=True)
        self.include_if_exists = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="包含注释", 
                       variable=self.include_comments).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="包含IF EXISTS", 
                       variable=self.include_if_exists).pack(anchor=tk.W, padx=5, pady=2)
        
        # 表选择
        table_select_frame = ttk.LabelFrame(left_frame, text="选择表")
        table_select_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 全选按钮
        ttk.Button(table_select_frame, text="全选", command=self.select_all_tables).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(table_select_frame, text="全不选", command=self.deselect_all_tables).pack(fill=tk.X, padx=5, pady=2)
        
        # 表列表
        self.table_vars = {}
        table_list_frame = ttk.Frame(table_select_frame)
        table_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 滚动框
        canvas = tk.Canvas(table_list_frame)
        scrollbar = ttk.Scrollbar(table_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加表复选框
        for table in self.tables:
            var = tk.BooleanVar(value=True)
            self.table_vars[f"{table.schema}.{table.table}"] = var
            ttk.Checkbutton(scrollable_frame, text=f"{table.schema}.{table.table}", 
                           variable=var).pack(anchor=tk.W, pady=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 生成按钮
        generate_frame = ttk.Frame(left_frame)
        generate_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(generate_frame, text="生成SQL", command=self.generate_sql).pack(fill=tk.X, pady=2)
        ttk.Button(generate_frame, text="保存到文件", command=self.save_to_file).pack(fill=tk.X, pady=2)
        ttk.Button(generate_frame, text="关闭", command=self.dialog.destroy).pack(fill=tk.X, pady=2)
        
        # 右侧SQL显示区域
        right_frame = ttk.LabelFrame(main_frame, text="生成的SQL")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.sql_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=('Courier', 10))
        self.sql_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def select_all_tables(self):
        """全选表"""
        for var in self.table_vars.values():
            var.set(True)
            
    def deselect_all_tables(self):
        """全不选表"""
        for var in self.table_vars.values():
            var.set(False)
            
    def get_selected_tables(self) -> List[TableInfo]:
        """获取选中的表"""
        selected_tables = []
        for table in self.tables:
            table_key = f"{table.schema}.{table.table}"
            if table_key in self.table_vars and self.table_vars[table_key].get():
                selected_tables.append(table)
        return selected_tables
        
    def generate_sql(self):
        """生成SQL"""
        selected_tables = self.get_selected_tables()
        if not selected_tables:
            messagebox.showwarning("警告", "请至少选择一个表")
            return
            
        # 设置SQL方言
        self.sql_generator.set_dialect(self.dialect_var.get())
        
        sql_statements = []
        
        try:
            # 添加文件头注释
            sql_statements.extend([
                "-- ========================================",
                "-- Meta Data Workshop 自动生成的SQL脚本",
                f"-- 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"-- 数据库方言: {self.dialect_var.get().upper()}",
                f"-- 总表数: {len(selected_tables)}",
                "-- ========================================",
                ""
            ])
            
            # 生成DROP TABLE语句
            if self.sql_types["drop_table"].get():
                sql_statements.extend([
                    "-- ========================================",
                    "-- DROP TABLE 语句",
                    "-- ========================================",
                    ""
                ])
                drop_statements = self.sql_generator.generate_drop_table_statements(
                    selected_tables, 
                    include_if_exists=self.include_if_exists.get(),
                    add_comments=self.include_comments.get()
                )
                sql_statements.extend(drop_statements)
                sql_statements.append("")
            
            # 生成CREATE TABLE语句
            if self.sql_types["create_table"].get():
                sql_statements.extend([
                    "-- ========================================",
                    "-- CREATE TABLE 语句",
                    "-- ========================================",
                    ""
                ])
                create_statements = self.sql_generator.generate_create_table_statements(
                    selected_tables,
                    include_if_not_exists=self.include_if_exists.get(),
                    add_comments=self.include_comments.get()
                )
                sql_statements.extend(create_statements)
                sql_statements.append("")
            
            # 生成INSERT...SELECT语句
            if self.sql_types["insert_select"].get():
                sql_statements.extend([
                    "-- ========================================",
                    "-- INSERT...SELECT 语句",
                    "-- ========================================",
                    ""
                ])
                insert_statements = self.sql_generator.generate_insert_select_statements(
                    selected_tables, selected_tables, include_case_when=True
                )
                sql_statements.extend(insert_statements)
                sql_statements.append("")
            
            # 生成统计查询语句
            if self.sql_types["statistics"].get():
                sql_statements.extend([
                    "-- ========================================",
                    "-- 统计查询语句",
                    "-- ========================================",
                    ""
                ])
                stats_statements = self.sql_generator.generate_table_statistics_query(selected_tables)
                sql_statements.extend(stats_statements)
            
            # 显示生成的SQL
            self.sql_text.delete(1.0, tk.END)
            self.sql_text.insert(1.0, '\n'.join(sql_statements))
            
            messagebox.showinfo("成功", f"SQL生成完成！\n共生成 {len([s for s in sql_statements if s.strip()])} 行SQL")
            
        except Exception as e:
            messagebox.showerror("错误", f"SQL生成失败：\n{str(e)}")
            
    def save_to_file(self):
        """保存SQL到文件"""
        sql_content = self.sql_text.get(1.0, tk.END).strip()
        if not sql_content:
            messagebox.showwarning("警告", "没有SQL内容可保存，请先生成SQL")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="保存SQL文件",
            defaultextension=".sql",
            filetypes=[("SQL文件", "*.sql"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(sql_content)
                messagebox.showinfo("成功", f"SQL文件保存成功！\n文件路径：{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败：\n{str(e)}")