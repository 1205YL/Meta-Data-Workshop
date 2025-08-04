import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from typing import List, Optional

# 添加父目录到路径以导入核心模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ddl_parser import DDLParser, TableInfo
from core.metadata_exporter import MetadataExporter
from core.field_manager import FieldManager
from core.sql_generator import SQLGenerator
try:
    from .dialogs import ExportDialog, FieldManagementDialog, SQLGenerationDialog
except ImportError:
    from gui.dialogs import ExportDialog, FieldManagementDialog, SQLGenerationDialog

class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Meta Data Workshop - 数据库元数据处理工具 v1.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # 初始化核心组件
        self.ddl_parser = DDLParser()
        self.metadata_exporter = MetadataExporter()
        self.field_manager = FieldManager()
        self.sql_generator = SQLGenerator()
        
        # 数据存储
        self.current_tables: List[TableInfo] = []
        self.original_tables: List[TableInfo] = []
        self.current_file_path = ""
        
        # 创建界面
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 设置主题
        try:
            style.theme_use('clam')
        except:
            pass
        
        # 自定义样式
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Info.TLabel', foreground='blue')
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建菜单栏
        self.create_menu()
        
        # 创建主要区域
        self.create_main_area()
        
        # 创建状态栏
        self.create_status_bar()
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开DDL文件", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Ctrl+Q")
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="字段类型转换", command=self.open_field_conversion_dialog)
        tools_menu.add_command(label="添加系统字段", command=self.open_system_fields_dialog)
        tools_menu.add_command(label="生成SQL脚本", command=self.open_sql_generation_dialog)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        
        # 绑定快捷键
        self.root.bind_all("<Control-o>", lambda e: self.open_file())
        self.root.bind_all("<Control-q>", lambda e: self.root.quit())
        
    def create_main_area(self):
        """创建主要区域"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建上部控制区域
        self.create_control_area(main_frame)
        
        # 创建中部内容区域
        self.create_content_area(main_frame)
        
    def create_control_area(self, parent):
        """创建控制区域"""
        control_frame = ttk.LabelFrame(parent, text="文件操作")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 文件选择区域
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_frame, text="DDL文件:").pack(side=tk.LEFT)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state='readonly')
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        ttk.Button(file_frame, text="浏览", command=self.open_file).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(file_frame, text="解析", command=self.parse_file).pack(side=tk.RIGHT, padx=(10, 0))
        
        # 快速操作区域
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(action_frame, text="导出元数据", 
                  command=self.export_metadata).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="字段管理", 
                  command=self.open_field_management).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="生成SQL", 
                  command=self.generate_sql).pack(side=tk.LEFT, padx=(0, 10))
        
    def create_content_area(self, parent):
        """创建内容区域"""
        # 创建笔记本控件
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 数据概览标签页
        self.create_overview_tab()
        
        # 表详情标签页
        self.create_table_details_tab()
        
        # 日志标签页
        self.create_log_tab()
        
    def create_overview_tab(self):
        """创建数据概览标签页"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="数据概览")
        
        # 统计信息区域
        stats_frame = ttk.LabelFrame(overview_frame, text="统计信息")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        stats_inner = ttk.Frame(stats_frame)
        stats_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # 统计标签
        self.stats_labels = {}
        stats_items = [
            ("总表数", "table_count"),
            ("总字段数", "field_count"),
            ("Schema数", "schema_count")
        ]
        
        for i, (label, key) in enumerate(stats_items):
            ttk.Label(stats_inner, text=f"{label}:").grid(row=0, column=i*2, sticky=tk.W, padx=(0, 5))
            self.stats_labels[key] = ttk.Label(stats_inner, text="0", font=('Arial', 10, 'bold'))
            self.stats_labels[key].grid(row=0, column=i*2+1, sticky=tk.W, padx=(0, 20))
        
        # Schema列表
        schema_frame = ttk.LabelFrame(overview_frame, text="Schema列表")
        schema_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 创建树形视图
        columns = ("Schema", "表数量", "字段数量")
        self.schema_tree = ttk.Treeview(schema_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.schema_tree.heading(col, text=col)
            self.schema_tree.column(col, width=150)
        
        # 添加滚动条
        schema_scrollbar = ttk.Scrollbar(schema_frame, orient=tk.VERTICAL, command=self.schema_tree.yview)
        self.schema_tree.configure(yscrollcommand=schema_scrollbar.set)
        
        self.schema_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        schema_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
    def create_table_details_tab(self):
        """创建表详情标签页"""
        details_frame = ttk.Frame(self.notebook)
        self.notebook.add(details_frame, text="表详情")
        
        # 分割窗口
        paned = ttk.PanedWindow(details_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：表列表
        left_frame = ttk.LabelFrame(paned, text="表列表")
        paned.add(left_frame, weight=1)
        
        # 表列表
        self.table_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE)
        self.table_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        
        # 右侧：字段详情
        right_frame = ttk.LabelFrame(paned, text="字段详情")
        paned.add(right_frame, weight=2)
        
        # 字段详情表格
        field_columns = ("字段名", "类型", "可空", "默认值", "主键", "注释")
        self.field_tree = ttk.Treeview(right_frame, columns=field_columns, show='headings')
        
        for col in field_columns:
            self.field_tree.heading(col, text=col)
            self.field_tree.column(col, width=100)
        
        # 字段表格滚动条
        field_scrollbar_v = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.field_tree.yview)
        field_scrollbar_h = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=self.field_tree.xview)
        self.field_tree.configure(yscrollcommand=field_scrollbar_v.set, xscrollcommand=field_scrollbar_h.set)
        
        self.field_tree.grid(row=0, column=0, sticky='nsew', padx=(10, 0), pady=10)
        field_scrollbar_v.grid(row=0, column=1, sticky='ns', pady=10)
        field_scrollbar_h.grid(row=1, column=0, sticky='ew', padx=(10, 0))
        
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
    def create_log_tab(self):
        """创建日志标签页"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="操作日志")
        
        # 日志文本区域
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 清空日志按钮
        ttk.Button(log_frame, text="清空日志", command=self.clear_log).pack(pady=(0, 10))
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.status_bar, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=10, pady=5)
        
    def log_message(self, message: str, level: str = "INFO"):
        """记录日志消息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        
    def set_status(self, message: str):
        """设置状态栏消息"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def start_progress(self):
        """开始进度条"""
        self.progress.start()
        
    def stop_progress(self):
        """停止进度条"""
        self.progress.stop()
        
    def open_file(self):
        """打开文件对话框"""
        file_types = [
            ("DDL文件", "*.sql;*.txt;*.ddl"),
            ("SQL文件", "*.sql"),
            ("文本文件", "*.txt"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择DDL文件",
            filetypes=file_types
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.current_file_path = file_path
            self.log_message(f"选择文件: {file_path}")
            
    def parse_file(self):
        """解析DDL文件"""
        if not self.current_file_path:
            messagebox.showwarning("警告", "请先选择DDL文件")
            return
            
        def parse_worker():
            try:
                self.set_status("正在解析DDL文件...")
                self.start_progress()
                
                # 解析文件
                tables = self.ddl_parser.parse_file(self.current_file_path)
                
                # 更新界面
                self.root.after(0, lambda: self.update_ui_after_parse(tables))
                
            except Exception as e:
                self.root.after(0, lambda: self.handle_parse_error(str(e)))
                
        # 在后台线程中执行解析
        threading.Thread(target=parse_worker, daemon=True).start()
        
    def update_ui_after_parse(self, tables: List[TableInfo]):
        """解析完成后更新界面"""
        try:
            self.current_tables = tables
            self.original_tables = [table for table in tables]  # 备份原始数据
            
            self.update_overview()
            self.update_table_list()
            
            self.log_message(f"解析完成，共找到 {len(tables)} 个表")
            messagebox.showinfo("成功", f"解析完成！\n共解析出 {len(tables)} 个表")
            
        except Exception as e:
            self.handle_parse_error(str(e))
        finally:
            self.stop_progress()
            self.set_status("就绪")
            
    def handle_parse_error(self, error_msg: str):
        """处理解析错误"""
        self.log_message(f"解析失败: {error_msg}", "ERROR")
        messagebox.showerror("错误", f"解析文件失败：\n{error_msg}")
        self.stop_progress()
        self.set_status("就绪")
        
    def update_overview(self):
        """更新数据概览"""
        if not self.current_tables:
            for key in self.stats_labels:
                self.stats_labels[key].config(text="0")
            return
            
        # 更新统计信息
        table_count = len(self.current_tables)
        field_count = sum(len(table.fields) for table in self.current_tables)
        schemas = set(table.schema for table in self.current_tables)
        schema_count = len(schemas)
        
        self.stats_labels["table_count"].config(text=str(table_count))
        self.stats_labels["field_count"].config(text=str(field_count))
        self.stats_labels["schema_count"].config(text=str(schema_count))
        
        # 更新Schema树形视图
        for item in self.schema_tree.get_children():
            self.schema_tree.delete(item)
            
        schema_stats = {}
        for table in self.current_tables:
            schema = table.schema
            if schema not in schema_stats:
                schema_stats[schema] = {"tables": 0, "fields": 0}
            schema_stats[schema]["tables"] += 1
            schema_stats[schema]["fields"] += len(table.fields)
            
        for schema, stats in schema_stats.items():
            self.schema_tree.insert("", tk.END, values=(
                schema, stats["tables"], stats["fields"]
            ))
            
    def update_table_list(self):
        """更新表列表"""
        self.table_listbox.delete(0, tk.END)
        
        for table in self.current_tables:
            display_name = f"{table.schema}.{table.table}"
            self.table_listbox.insert(tk.END, display_name)
            
    def on_table_select(self, event):
        """表选择事件处理"""
        selection = self.table_listbox.curselection()
        if not selection:
            return
            
        table_index = selection[0]
        if 0 <= table_index < len(self.current_tables):
            table = self.current_tables[table_index]
            self.update_field_details(table)
            
    def update_field_details(self, table: TableInfo):
        """更新字段详情"""
        # 清空现有数据
        for item in self.field_tree.get_children():
            self.field_tree.delete(item)
            
        # 添加字段数据
        for field in table.fields:
            is_primary = "是" if field.name in table.primary_keys else "否"
            nullable = "是" if field.nullable else "否"
            
            self.field_tree.insert("", tk.END, values=(
                field.name,
                field.type,
                nullable,
                field.default_value or "",
                is_primary,
                field.comment or ""
            ))
            
    def export_metadata(self):
        """导出元数据"""
        if not self.current_tables:
            messagebox.showwarning("警告", "没有可导出的数据，请先解析DDL文件")
            return
            
        # 打开导出对话框
        ExportDialog(self.root, self.current_tables, self.metadata_exporter)
        
    def open_field_management(self):
        """打开字段管理对话框"""
        if not self.current_tables:
            messagebox.showwarning("警告", "没有数据，请先解析DDL文件")
            return
            
        # 打开字段管理对话框
        FieldManagementDialog(self.root, self.current_tables, self.field_manager, self.on_tables_updated)
        
    def generate_sql(self):
        """生成SQL脚本"""
        if not self.current_tables:
            messagebox.showwarning("警告", "没有数据，请先解析DDL文件")
            return
            
        # 打开SQL生成对话框
        SQLGenerationDialog(self.root, self.current_tables, self.sql_generator)
        
    def on_tables_updated(self, updated_tables: List[TableInfo]):
        """表数据更新回调"""
        self.current_tables = updated_tables
        self.update_overview()
        self.update_table_list()
        self.log_message("数据已更新")
        
    # 对话框相关方法
    def open_field_conversion_dialog(self):
        """打开字段类型转换对话框"""
        self.open_field_management()
        
    def open_system_fields_dialog(self):
        """打开系统字段添加对话框"""
        self.open_field_management()
        
    def open_sql_generation_dialog(self):
        """打开SQL生成对话框"""
        self.generate_sql()
        
    def show_help(self):
        """显示帮助信息"""
        help_text = """
Meta Data Workshop 使用说明

1. 文件操作：
   - 点击"浏览"选择DDL文件
   - 点击"解析"解析文件内容

2. 元数据导出：
   - 支持导出为Excel、CSV、JSON格式
   - 可按Schema、表分层导出

3. 字段管理：
   - 批量转换字段类型
   - 添加系统字段（如审计字段）

4. SQL生成：
   - 生成DROP TABLE语句
   - 生成CREATE TABLE语句
   - 生成INSERT...SELECT语句

5. 快捷键：
   - Ctrl+O: 打开文件
   - Ctrl+Q: 退出程序
        """
        messagebox.showinfo("使用说明", help_text)
        
    def show_about(self):
        """显示关于信息"""
        about_text = """
Meta Data Workshop v1.0

数据库元数据处理工具

功能特点：
• DDL文件解析
• 元数据导出
• 字段类型转换
• 系统字段管理
• SQL脚本生成

开发者：Meta Data Workshop Team
        """
        messagebox.showinfo("关于", about_text)
        
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.run()