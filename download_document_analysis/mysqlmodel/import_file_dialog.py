from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QFileDialog, \
    QMessageBox, QSpacerItem, QSizePolicy, QLabel, QCompleter, QButtonGroup
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
import pymysql
import pandas as pd
import json
import os


class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal()

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit()
        super().mousePressEvent(event)

class ImportFileDialog(QDialog):
    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("文件导入")
        try:
            self.initUI()
            self.resize(2100, 800)  # 设置对话框的大小
        except Exception as e:
            QMessageBox.critical(self, "错误", f"初始化 ImportFileDialog 时发生错误: {e}")

    def initUI(self):
        try:
            main_layout = QVBoxLayout(self)

            # 添加标题行
            title_layout = QHBoxLayout()
            title_label = QLabel("输入或选择数据库名|表名|文件|Sheet页|标题行数|是否覆盖表：")
            title_layout.addWidget(title_label)
            main_layout.addLayout(title_layout)

            # 动态添加导入行
            self.import_rows = []
            self.load_import_info()  # 加载配置信息
            if not self.import_rows:  # 如果没有加载到任何信息，则添加第一行
                self.add_import_row()

            # 添加固定间距
            spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            main_layout.addItem(spacer)

            # 添加行按钮
            add_row_button = QPushButton("添加行")
            add_row_button.clicked.connect(self.add_import_row)
            add_row_button.setFixedWidth(200)  # 设置按钮的固定宽度
            add_row_button.setFixedHeight(40)
            main_layout.addWidget(add_row_button)

            # 导入按钮
            self.import_button = QPushButton("导入文件")
            self.import_button.setFixedWidth(200)  # 设置按钮的固定宽度
            self.import_button.setFixedHeight(40)
            # 创建一个水平布局来放置两个按钮
            button_layout = QHBoxLayout()
            button_layout.addStretch(1)  # 添加一个伸缩器，使按钮靠右
            button_layout.addWidget(add_row_button)
            button_layout.addWidget(self.import_button)

            # 将按钮布局添加到主布局的最下方
            main_layout.addLayout(button_layout)

            self.import_button.clicked.connect(self.import_data)
            self.setLayout(main_layout)  # 设置主布局

            # 加载数据库列表
            self.show_databases()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"初始化UI时发生错误: {e}")

    def create_completer(self, items):
        completer = QCompleter(items)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        return completer

    def show_databases(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                self.all_databases = [db[0] for db in cursor.fetchall()]
                return self.all_databases
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "错误", f"获取数据库列表失败: {e}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据库列表时发生未知错误: {e}")

    def on_database_selected(self, text, row_widgets):
        if text and text.strip() in self.all_databases:
            self.show_tables(text, row_widgets)
            #row_widgets['table_edit'].setEnabled(True)  # 启用表格选择
        else:
            #row_widgets['table_edit'].setEnabled(False)  # 禁用表格选择
            row_widgets['table_edit'].clear()
            row_widgets['table_edit'].setCompleter(self.create_completer([]))

    def show_tables(self, database, row_widgets):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"USE {database}")
                cursor.execute("SHOW TABLES")
                all_tables = [table[0] for table in cursor.fetchall()]
                row_widgets['table_edit'].setCompleter(self.create_completer(all_tables))
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "错误", f"获取表列表失败: {e}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载表列表时发生未知错误: {e}")

    def add_import_row(self):
        row_layout = QHBoxLayout()
        # 库名输入框
        database_edit = QLineEdit()
        database_edit.setPlaceholderText("输入库")
        database_edit.setCompleter(self.create_completer(self.show_databases()))
        database_edit.setFixedWidth(150)  # 设置按钮的固定宽度
        row_layout.addWidget(database_edit)
        # 表名输入框
        table_edit = QLineEdit()
        table_edit.setPlaceholderText("输入表")
        table_edit.setCompleter(self.create_completer([]))
        #table_edit.setEnabled(False)  # 初始状态下禁用表格选择
        table_edit.setFixedWidth(400)
        row_layout.addWidget(table_edit)
        # 文件路径输入框
        file_path = ClickableLineEdit()
        file_path.setPlaceholderText("点击选择文件")
        file_path.setReadOnly(True)
        file_path.clicked.connect(lambda: self.browse_data_file(file_path))
        row_layout.addWidget(file_path)
        # Sheet 选择下拉框
        sheet_var = QComboBox()
        sheet_var.setFixedWidth(300)
        sheet_var.addItem("选择Sheet页")  # 添加默认项
        sheet_var.setCurrentIndex(0)  # 设置默认项为当前选中项
        row_layout.addWidget(sheet_var)
        # 标题行数
        header_row_num = QLineEdit()
        header_row_num.setFixedWidth(200)
        header_row_num.setPlaceholderText("标题行数(默认0)")
        row_layout.addWidget(header_row_num)
        # 是否覆盖表数据的下拉框
        overwrite_combo = QComboBox()
        overwrite_combo.setFixedWidth(200)
        overwrite_combo.addItems(["覆盖表：否", "覆盖表：是"])
        overwrite_combo.setCurrentIndex(0)  # 默认选择“否”
        row_layout.addWidget(overwrite_combo)
        # 删除按钮
        remove_button = QPushButton("-")
        remove_button.setFixedSize(30, 30)
        remove_button.clicked.connect(lambda: self.remove_import_row(row_layout))
        row_layout.addWidget(remove_button)
        # 保存行控件
        row_widgets = {
            'database_edit': database_edit,
            'table_edit': table_edit,
            'file_path': file_path,
            'sheet_var': sheet_var,
            'header_row_num': header_row_num,
            'overwrite_combo': overwrite_combo,
            'remove_button': remove_button
        }
        # 连接库名输入框的文本变化信号
        database_edit.textChanged.connect(lambda text: self.on_database_selected(text, row_widgets))
        self.import_rows.append(row_widgets)
        insert_index = len(self.import_rows)
        self.layout().insertLayout(insert_index, row_layout)

    def remove_import_row(self, layout):
        # 获取传递进来的布局在主布局中的索引，并减1（因为删除按钮位于布局的最后一项）
        index = self.layout().indexOf(layout)-1
        # 检查索引是否有效（即确保它在合理的范围内）
        if 0 <= index < len(self.import_rows):
            # 根据索引移除对应的行控件字典，并将其赋值给row_widgets变量
            row_widgets = self.import_rows.pop(index)
            # 遍历行控件字典中的每个控件
            for widget in row_widgets.values():
                widget.deleteLater()
            # 从主布局中移除整个布局
            self.layout().removeItem(layout)

    def browse_data_file(self, file_path_widget):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Excel Files (*.xlsx *.xls)")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            file_path_widget.setText(selected_file)
            # 读取 Excel 文件并获取 Sheet 名称
            sheets = pd.ExcelFile(selected_file).sheet_names
            # 查找包含 file_path_widget 的行
            row_widgets = next((row for row in self.import_rows if row['file_path'] == file_path_widget), None)
            if row_widgets:
                row_widgets['sheet_var'].clear()
                row_widgets['sheet_var'].addItems(sheets)

    def import_data(self):
        try:
            import_rows = []
            for row_widgets in self.import_rows:
                database = row_widgets['database_edit'].text().strip()
                table_name = row_widgets['table_edit'].text().strip()
                file_path = row_widgets['file_path'].text().strip()
                sheet_name = row_widgets['sheet_var'].currentText()
                header_row_num = int(row_widgets['header_row_num'].text().strip()) if row_widgets[
                    'header_row_num'].text().strip() else 0
                overwrite = row_widgets['overwrite_combo'].currentText() == "覆盖表：是"

                if not database or not table_name or not file_path or not sheet_name:
                    continue

                # 读取 Excel 文件
                if header_row_num == 0:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                    df.columns = [f"col_{i}" for i in range(df.shape[1])]  # 生成默认列名
                else:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row_num)

                df = df.where(pd.notnull(df), '')
                placeholders = ', '.join(['%s' for _ in range(df.shape[1])])
                sql = f"INSERT INTO {database}.{table_name} VALUES ({placeholders})"

                if overwrite:
                    truncate_sql = f"TRUNCATE TABLE {database}.{table_name}"
                    with self.connection.cursor() as cursor:
                        cursor.execute(truncate_sql)

                data_to_insert = df.values.tolist()
                with self.connection.cursor() as cursor:
                    cursor.executemany(sql, data_to_insert)
                    self.connection.commit()

                import_rows.append({
                    'database': database,
                    'table_name': table_name,
                    'file_path': file_path,
                    'sheet_name': sheet_name,
                    'header_row_num': header_row_num,
                    'overwrite': overwrite
                })

            if import_rows:
                QMessageBox.information(self, "成功", "数据导入成功")
                self.save_import_info(import_rows)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据导入失败: {e}")

    def save_import_info(self, import_rows):
        config_dir = "conf"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)  # 创建文件夹
        config_file = f"{config_dir}/import_info.json"
        with open(config_file, 'w') as file:
            json.dump(import_rows, file)

    def load_import_info(self):
        config_dir = "conf"
        config_file = f"{config_dir}/import_info.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                import_rows = json.load(file)
                for row in import_rows:
                    self.add_import_row()
                    last_row_widgets = self.import_rows[-1]
                    last_row_widgets['database_edit'].setText(row['database'])
                    last_row_widgets['table_edit'].setText(row['table_name'])
                    last_row_widgets['file_path'].setText(row['file_path'])
                    # 读取 Excel 文件并获取 Sheet 名称
                    if os.path.exists(row['file_path']):
                        sheets = pd.ExcelFile(row['file_path']).sheet_names
                        last_row_widgets['sheet_var'].addItems(sheets)
                        last_row_widgets['sheet_var'].setCurrentText(row['sheet_name'])
                    last_row_widgets['header_row_num'].setText(str(row['header_row_num']))
                    if row['overwrite']:
                        last_row_widgets['overwrite_combo'].setCurrentIndex(1)  # 1 是 "是" 选项的索引
                    else:
                        last_row_widgets['overwrite_combo'].setCurrentIndex(0)  # 0 是 "否" 选项的索引