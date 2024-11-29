from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QFormLayout, QVBoxLayout, QHBoxLayout, QMessageBox
import pymysql
import json
import os

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建连接")
        self.initUI()
        self.connection = None  # 添加一个属性来存储连接对象
        self.resize(900, 450)
        # 检查配置文件并尝试加载连接信息
        connection_info = self.load_connection_info()
        if connection_info:
            self.host.setText(connection_info.get('host', ''))
            self.port.setText(str(connection_info.get('port', '3306')))
            self.user_entry.setText(connection_info.get('user', ''))
            self.password_entry.setText(connection_info.get('password', ''))

    def initUI(self):
        form_layout = QFormLayout()

        # 服务器地址输入框
        self.host = QLineEdit()
        form_layout.addRow("服务器地址:", self.host)

        # 端口输入框
        self.port = QLineEdit("3306")
        form_layout.addRow("端口:", self.port)

        # 用户输入框
        self.user_entry = QLineEdit()
        form_layout.addRow("用户名:", self.user_entry)

        # 密码输入框
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        form_layout.addRow("密码:", self.password_entry)

        # 连接按钮
        connect_button = QPushButton("连 接")
        connect_button.setFixedWidth(200)  # 设置按钮的固定宽度
        connect_button.setFixedHeight(40)
        connect_button.clicked.connect(self.connect_to_mysql)

        # 创建一个水平布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(connect_button)

        # 创建一个垂直布局来放置表单布局和按钮布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addStretch()  # 添加一个伸缩器，使按钮布局靠下
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def connect_to_mysql(self):
        host = self.host.text()
        port = int(self.port.text())
        user = self.user_entry.text()
        password = self.password_entry.text()

        try:
            self.connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password
            )
            QMessageBox.information(self, "成功", "连接成功")

            # 保存连接信息
            self.save_connection_info(host, port, user, password)

            # 通知父窗口更新标题
            self.parent().update_window_title(host)

            self.accept()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "错误", f"连接失败: {e}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接失败: {e}")

    def save_connection_info(self, host, port, user, password):
        connection_info = {
            'host': host,
            'port': port,
            'user': user,
            'password': password
        }

        config_dir = "conf"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)  # 创建文件夹

        config_file = f"{config_dir}/connection.json"
        with open(config_file, 'w') as file:
            json.dump(connection_info, file)

    @staticmethod
    def load_connection_info():
        config_dir = "conf"
        config_file = f"{config_dir}/connection.json"

        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                return json.load(file)
        return None