import pymysql
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox, QDialog
from mysqlmodel.connection_dialog import ConnectionDialog
from mysqlmodel.execute_sql_dialog import ExecuteSQLDialog
from mysqlmodel.import_file_dialog import ImportFileDialog

class DbMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据库")
        self.setGeometry(200, 200, 2200, 1200)
        self.initUI()
        self.connection = None
        self.is_connected = False  # 新增一个标志变量
        # 设置窗口最大化
        #self.showMaximized()

    def initUI(self):
        # 创建菜单栏
        menubar = self.menuBar()
        db_menu = menubar.addMenu('数据库')

        # 添加菜单项
        new_conn_action = QAction('新建连接', self)
        new_conn_action.triggered.connect(self.open_connection_dialog)
        db_menu.addAction(new_conn_action)

        exec_sql_action = QAction('执行SQL', self)
        exec_sql_action.triggered.connect(self.open_execute_sql_dialog)
        db_menu.addAction(exec_sql_action)

        import_file_action = QAction('文件导入', self)
        import_file_action.triggered.connect(self.open_import_file_dialog)
        db_menu.addAction(import_file_action)

    def open_connection_dialog(self):
        dialog = ConnectionDialog(self) # 传递 self 作为父窗口
        if dialog.exec_() == QDialog.Accepted:
            self.connection = dialog.connection  # 直接从 dialog 获取连接对象

    def open_execute_sql_dialog(self):
        if not self.connection:
            QMessageBox.critical(self, "错误", "请先连接数据库")
            return
        dialog = ExecuteSQLDialog(self.connection, self)
        dialog.exec_()

    def open_import_file_dialog(self):
        if not self.connection:
            QMessageBox.critical(self, "错误", "请先连接数据库")
            return
        dialog = ImportFileDialog(self.connection, self)
        dialog.exec_()

    def update_window_title(self, host):
        # 更新窗口标题，显示当前连接的服务器地址
        self.setWindowTitle(f"数据库（{host}）")

    def showEvent(self, event):
        super().showEvent(event)
        if not self.is_connected:
            QTimer.singleShot(500, self.load_connection)  # 延迟500毫秒后调用 load_connection 方法

    def load_connection(self):
        connection_info = ConnectionDialog.load_connection_info()
        if connection_info:
            try:
                self.connection = pymysql.connect(
                    host=connection_info['host'],
                    port=connection_info['port'],
                    user=connection_info['user'],
                    password=connection_info['password']
                )
                self.is_connected = True  # 设置为已连接
                self.update_window_title(connection_info['host'])
                #QMessageBox.information(self, "成功", "自动连接成功")
            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "错误", f"自动连接失败: {e}")