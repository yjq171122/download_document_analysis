from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QFileDialog, QMessageBox
import pymysql

class ExecuteSQLDialog(QDialog):
    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("执行SQL")
        self.initUI()
        self.resize(1400, 900)

    def initUI(self):
        layout = QVBoxLayout()

        # SQL输入框
        self.sql_entry = QTextEdit()
        layout.addWidget(self.sql_entry)


        execbutton_layout = QHBoxLayout()
        execbutton_layout.addStretch()
        # 执行SQL按钮
        self.execute_button = QPushButton("执行SQL")
        self.execute_button.setFixedWidth(200)  # 设置按钮的固定宽度
        self.execute_button.setFixedHeight(40)
        self.execute_button.clicked.connect(self.run_sql)
        execbutton_layout.addWidget(self.execute_button)
        layout.addLayout(execbutton_layout)

        # 选择文件
        self.sql_file_path = QLineEdit()
        self.sql_file_path.setReadOnly(True)
        layout.addWidget(self.sql_file_path)

        self.setLayout(layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.browse_button = QPushButton("选择SQL文件")
        self.browse_button.setFixedWidth(200)  # 设置按钮的固定宽度
        self.browse_button.setFixedHeight(40)
        self.browse_button.clicked.connect(self.browse_sql_file)
        buttons_layout.addWidget(self.browse_button)

        self.execute_sqlfile_button = QPushButton("执行SQL文件")
        self.execute_sqlfile_button.setFixedWidth(200)  # 设置按钮的固定宽度
        self.execute_sqlfile_button.setFixedHeight(40)
        self.execute_sqlfile_button.clicked.connect(self.execute_sql_file)
        buttons_layout.addWidget(self.execute_sqlfile_button)

        layout.addLayout(buttons_layout)

    def run_sql(self):
        sql = self.sql_entry.toPlainText().strip()
        if not sql:
            QMessageBox.critical(self, "错误", "SQL语句不能为空")
            return

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                self.connection.commit()  # 对于需要提交的操作，如INSERT、UPDATE、DELETE
            QMessageBox.information(self, "成功", "SQL执行成功")
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "错误", f"SQL执行失败: {e}")

    def browse_sql_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择SQL文件", "", "SQL Files (*.sql);;All Files (*)")
        if file_path:
            self.sql_file_path.setText(file_path)

    def execute_sql_file(self):
        file_path = self.sql_file_path.text()
        if not file_path:
            QMessageBox.critical(self, "错误", "未选择SQL文件")
            return

        try:
            with open(file_path, 'r') as file:
                sql_commands = file.read().strip().split(';')
            with self.connection.cursor() as cursor:
                for command in sql_commands:
                    if command.strip():
                        cursor.execute(command)
                self.connection.commit()
            QMessageBox.information(self, "成功", "SQL文件执行成功")
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "错误", f"SQL文件执行失败: {e}")
        except FileNotFoundError:
            QMessageBox.critical(self, "错误", "SQL文件未找到")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"未知错误: {e}")