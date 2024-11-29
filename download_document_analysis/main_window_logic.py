# main_window_logic.py
import subprocess

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QListView
from PyQt5.QtCore import QStringListModel

from script_runner.script_runner import ScriptRunner
from view.main_view import Ui_MainWindow  # 确保导入语句匹配新的文件名
from view.fenxi import Ui_widget
from view.setinput import Ui_setinput
from mysql_ctrl import MySQLMiddleware
import os,json
import pandas as pd
from loadmodel.load import TencentDocDownloaderApp
from mysqlmodel.db_menu import  DbMenu
import pymysql
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox, QDialog
from mysqlmodel.connection_dialog import ConnectionDialog
from mysqlmodel.execute_sql_dialog import ExecuteSQLDialog
from mysqlmodel.import_file_dialog import ImportFileDialog



class MainWindowLogic(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindowLogic, self).__init__(parent)
        self.setupUi(self)  # 初始化界面
        # 设置窗口最大化
        self.showMaximized()
        self.connection = None


        self.analysis_window = QtWidgets.QMainWindow()
        self.ui = Ui_widget()
        self.ui.setupUi(self.analysis_window)

        self.setinput_window = QtWidgets.QMainWindow()
        self.setinput_ui = Ui_setinput()
        self.setinput_ui.setupUi(self.setinput_window)

        # self.menu.triggered.connect(self.open_analysis_window)
        #点击主界面【项目分析】-》【查看】-【弹项目分析界面】
        self.menu_2.triggered.connect(self.open_analysis_window)
        #点击主界面【腾讯文档】-》【查看】-【弹腾讯文档界面】
        self.menu.triggered.connect(self.open_load_window)
        #数据库 模块
        #self.menu_3.triggered.connect(self.open_mysql_window)
        self.action_6.triggered.connect(self.open_connection_dialog)
        self.action_8.triggered.connect(self.open_execute_sql_dialog)
        self.action_9.triggered.connect(self.open_import_file_dialog)
        #执行器
        self.menu_4.triggered.connect(self.open_runner_window)

        #点击【项目分析】界面 左侧列表：
        self.ui.listView.clicked.connect(self.on_list_view_item_clicked)
        #点击【项目分析】界面【自定义热键】弹【自定义窗口】
        self.ui.pushButton_3.clicked.connect(self.open_setinput_window)
        
        self.ui.pushButton_4.clicked.connect(self.down_huizong)
        self.ui.pushButton_5.clicked.connect(self.down_qingdan)
        ##self.ui.pushButton.clicked.connect(self.on_pushButton_clicked)
        #点击【自定义窗口】的提交按键
        self.setinput_ui.pushButton.clicked.connect(self.setinput_get_button)

        self.list = []
        self.fenxi_name = ""
        self.fenxi_sql_txt = ""
        self.qingdan_sql_txt = ""

    def open_load_window(self):
        # subprocess.Popen(['python','load.py'])
        self.load_window = TencentDocDownloaderApp()
        self.load_window.show()

    def open_runner_window(self):
        self.runner_window = ScriptRunner()
        self.runner_window.show()

    # def connect_list_view_signals(self, listView, textEdit):
    #     listView.itemClicked.connect(lambda item: self.on_list_view_item_clicked(item, textEdit))
    # 点击选项
    def on_list_view_item_clicked(self, item):
        print(item.row())
        print(self.list[item.row()])
        self.fenxi_name = self.list[item.row()]
        data = self.load_json_data()
        # print(self.ui.listView[item.row()])
        self.fenxi_sql_txt = data['fenxi'][self.list[item.row()]]
        self.qingdan_sql_txt = data['qingdan'][self.list[item.row()]]
        self.ui.textEdit.setText(self.fenxi_sql_txt)
        # fenxi_data = middleware.sql_ctrl(fenxi_sql_txt).fetchall()
        # qingdan_data = middleware.sql_ctrl(qingdan_sql_txt).fetchall()
        # print(qingdan_data)

        if self.fenxi_sql_txt:
            print(f"找到的 SQL 语句：{self.fenxi_sql_txt}")
            # 这里可以继续执行 sql_statement
            self.select_and_printtablewidget(self.fenxi_sql_txt, self.ui.tableWidget)
        else:
            print(f"未找到SQL 语句。")

        if self.qingdan_sql_txt:
            print(f"找到的 SQL 语句：{self.qingdan_sql_txt}")
            # 这里可以继续执行 sql_statement
            self.select_and_printtablewidget(self.qingdan_sql_txt, self.ui.tableWidget_2)
        else:
            print(f"未找到SQL 语句。")

    # 打开项目分析界面
    def open_analysis_window(self):
        if os.path.exists('conf/connection.json'):
            with open('conf/connection.json', 'r', encoding='utf-8') as file:
                data_base = json.load(file)
            print(data_base)
            self.middleware = MySQLMiddleware(host=data_base['host'], username=data_base['user'],
                                              password=data_base['password'])
            # print("进入新窗口函数")
            # 创建分析窗口的实例
            # self.analysis_window = QtWidgets.QMainWindow()
            # self.ui = Ui_Form()
            # self.ui.setupUi(self.analysis_window)

            # 获取 listView 和 textEdit 的实例
            listView = self.ui.listView
            textEdit = self.ui.textEdit
            print(self.ui.listView)
            print(listView)
            # 填充列表视图并设置连接 #读取json
            self.populate_list_view(listView)
            # self.connect_list_view_signals(listView, textEdit)
            # 显示分析窗口
            self.analysis_window.show()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"没有数据库文件，先设置数据库连接")

    # 导出汇总
    def down_huizong(self):
        # 弹出目录选择器，让用户选择保存路径
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", "",
                                                               QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)
        # 如果用户选择了路径，则构造完整的文件路径并保存文件
        if directory:
            file_name = self.fenxi_name + "-汇总.xlsx"
            file_path = QtCore.QDir(directory).filePath(file_name)
            self.select_and_save_to_excel(self.fenxi_sql_txt, file_path)

    # 导出清单
    def down_qingdan(self):
        # 弹出目录选择器，让用户选择保存路径
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", "",
                                                               QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)
        # 如果用户选择了路径，则构造完整的文件路径并保存文件
        if directory:
            file_name = self.fenxi_name + "-清单.xlsx"
            file_path = QtCore.QDir(directory).filePath(file_name)
            self.select_and_save_to_excel(self.qingdan_sql_txt, file_path)

    # 打开自定义增加sql窗口
    def open_setinput_window(self):
        self.setinput_window.show()

    # 填充listview
    def populate_list_view(self, listView):
        print("zheli")
        try:
            data = self.load_json_data()
            print(data)
            # 创建一个 QStringListModel 实例
            model = QStringListModel()
            print(2)
            # 清空现有的项
            # model.clear()
            # 添加新的项
            self.list = []
            for key in data['fenxi']:
                self.list.append(key)  # 使用 addItem() 方法添加每个 key
                print(3)
            # listView.setModel(model)  # 设置模型到 listView
            print(4)
            model.setStringList(self.list)
            print(5)
            listView.setModel(model)  # 列表填充到模型中

        except Exception as e:
            print(f"An error occurred in populate_list_view: {e}")

    # 读取json
    def load_json_data(self):
        with open('conf/package.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data

    # 将查询数据库并填充listview
    def select_and_printtablewidget(self, sql_txt, tableWidget):
        try:
            # 执行查询
            result = self.middleware.sql_ctrl(sql_txt)

            # 获取字段名称
            field_names = result.keys() if result.keys else []

            # 清空 tableWidget_2
            tableWidget.setRowCount(0)
            tableWidget.setColumnCount(0)

            # 如果有数据，则设置列数和表头
            if field_names:
                tableWidget.setColumnCount(len(field_names))
                # 设置表头
                tableWidget.setHorizontalHeaderLabels(field_names)

                # 填充数据
                for row_data in result:
                    row_position = tableWidget.rowCount()
                    tableWidget.insertRow(row_position)
                    for column, data_item in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(str(data_item) if data_item is not None else "")
                        tableWidget.setItem(row_position, column, item)
            else:
                # 如果没有字段名称，显示提示信息
                tableWidget.setRowCount(1)
                tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem("No data"))

        except Exception as e:
            # 输出错误信息到控制台
            print(f"An error occurred: {e}")
            # 可以选择显示一个错误消息框
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    # 自定义增加SQL窗口的逻辑代码
    # 点击提交操作逻辑
    def setinput_get_button(self):
        title_text = self.setinput_ui.lineEdit.text()
        fenxi_sql_text = self.setinput_ui.textEdit.toPlainText()
        qingdan_sql_text = self.setinput_ui.textEdit_2.toPlainText()
        if title_text == "" or fenxi_sql_text == "" or qingdan_sql_text == "":
            QtWidgets.QMessageBox.critical(self, "Error", f"请把内容全填完")
        else:
            # 尝试加载JSON数据，如果文件不存在或内容为空，则初始化一个新的JSON结构
            try:
                with open('conf/package.json', 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                json_data = {"fenxi": {}, "qingdan": {}}

            if self.search_key(json_data, title_text):
                QtWidgets.QMessageBox.critical(self, "Error", f"这个标题已经有了")

            else:
                try:
                    fenxi_df = self.middleware.query_table_to_dataframe(fenxi_sql_text)
                    qingdan_df = self.middleware.query_table_to_dataframe(qingdan_sql_text)
                    if fenxi_df.empty:
                        QtWidgets.QMessageBox.critical(self, "Error",
                                                       f"该分析SQL在数据库中查不出数据，请先添加到数据库中")
                    elif qingdan_df.empty:
                        QtWidgets.QMessageBox.critical(self, "Error",
                                                       f"该清单SQL在数据库中查不出数据，请先添加到数据库中")
                    else:
                        # 往"fenxi"中添加"分析查询":"查询语句"
                        json_data["fenxi"][title_text] = fenxi_sql_text

                        # 往"qingdan"中添加"清单查询":"查询语句"
                        json_data["qingdan"][title_text] = qingdan_sql_text
                        # 将修改后的字典转换回JSON字符串
                        modified_json_data = json.dumps(json_data, indent=2, ensure_ascii=False)

                        # 将新的JSON数据写入package.json文件
                        with open('conf/package.json', 'w', encoding='utf-8') as f:
                            f.write(modified_json_data)
                        QtWidgets.QMessageBox.information(self, "Success", f"你很棒哦，给你存进去了")
                        self.populate_list_view(self.ui.listView)
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error",
                                                   f"语句报错了，请确认语句是否正确！错误信息：{str(e)}")

    # 以下为工具方法
    # 定义一个函数来递归搜索键名为“tile”的数据
    def search_key(self, data, key):
        if isinstance(data, dict):
            for k, v in data.items():
                if k == key:
                    return True
                if isinstance(v, (dict, list)):
                    if self.search_key(v, key):
                        return True
        elif isinstance(data, list):
            for item in data:
                if self.search_key(item, key):
                    return True
        return False

    # 查询并导出excel
    def select_and_save_to_excel(self, sql_txt, file_path):
        try:
            # 执行查询
            result = self.middleware.sql_ctrl(sql_txt)

            # 获取字段名称作为表头
            field_names = result.keys() if result.keys else []

            # 将查询结果转换为pandas DataFrame，并指定列名
            df = pd.DataFrame(result, columns=field_names)

            # 保存到Excel文件
            df.to_excel(file_path, index=False)

            print(f"Data has been saved to {file_path}")
            QtWidgets.QMessageBox.critical(self, "Good", f"导出成功，文件为：{file_path}")

        except Exception as e:
            # 输出错误信息到控制台
            print(f"An error occurred: {e}")
            # 可以选择显示一个错误消息框
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    # 下面的是旧代码
    def on_treeWidgetItem_clicked(self, item, column):
        print('当前点击的节点为：', item.text(column))
        i = item.text(column)
        if i == '【分系统研发投入】分析':
            self.stackedWidget.setCurrentIndex(1)
            # self.on_pushButton_2_clicked()
            # self.show_data_in_table_widget()
        elif i == '【分小组研发投入】分析':
            self.stackedWidget.setCurrentIndex(2)

    def show_data_in_table_widget(self):
        ctrl_txt = self.read_txt('【分系统研发投入】分析.txt')
        data = self.middleware.sql_ctrl(ctrl_txt).fetchall()
        print(data)

        self.tableWidget_2.setRowCount(0)
        self.tableWidget_2.setColumnCount(0)
        column_count = len(data[0]) if data else 0
        self.tableWidget_2.setColumnCount(column_count)
        self.tableWidget_2.setHorizontalHeaderLabels(['stock_code', 'stock_name', 'concept_code'])

        for row_data in data:
            row_position = self.tableWidget_2.rowCount()
            self.tableWidget_2.insertRow(row_position)
            for column, data_item in enumerate(row_data):
                self.tableWidget_2.setItem(row_position, column, QtWidgets.QTableWidgetItem(str(data_item)))

    # 【分系统研发投入】分析-是否跳转清单
    def on_pushButton_clicked(self):
        self.new_window = QtWidgets.QMainWindow()
        self.ui = Ui_Form()  # 确保你也有一个 Ui_Form 类
        self.ui.setupUi(self.new_window)
        self.new_window.show()

        # 定义文件路径
        folder_path = 'sql_txt'
        file_name = 'sql_select.txt'
        file_path = os.path.join(folder_path, file_name)
        tag = '【分系统研发投入】清单'
        ctrl_txt = self.get_sql_statement_by_tag(file_path, tag)

        if ctrl_txt:
            print(f"找到的 SQL 语句：{ctrl_txt}")
            # 这里可以继续执行 sql_statement
            try:
                # 执行查询
                result = self.middleware.sql_ctrl(ctrl_txt)

                # 获取字段名称
                field_names = result.keys() if result.keys else []

                # 清空 tableWidget_2
                self.ui.table_list.setRowCount(0)
                self.ui.table_list.setColumnCount(0)

                # 如果有数据，则设置列数和表头
                if field_names:
                    self.ui.table_list.setColumnCount(len(field_names))
                    # 设置表头
                    self.ui.table_list.setHorizontalHeaderLabels(field_names)

                    # 填充数据
                    for row_data in result:
                        row_position = self.ui.table_list.rowCount()
                        self.ui.table_list.insertRow(row_position)
                        for column, data_item in enumerate(row_data):
                            item = QtWidgets.QTableWidgetItem(str(data_item) if data_item is not None else "")
                            self.ui.table_list.setItem(row_position, column, item)
                else:
                    # 如果没有字段名称，显示提示信息
                    self.ui.table_list.setRowCount(1)
                    self.ui.table_list.setItem(0, 0, QtWidgets.QTableWidgetItem("No data"))

            except Exception as e:
                # 输出错误信息到控制台
                print(f"An error occurred: {e}")
                # 可以选择显示一个错误消息框
                QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {e}")

        else:
            print(f"未找到标记为 {tag} 的 SQL 语句。")

    # 【分系统研发投入】分析-查询SQL语句
    def on_pushButton_2_clicked(self):
        # 定义文件路径
        folder_path = 'sql_txt'
        file_name = 'sql_select.txt'
        file_path = os.path.join(folder_path, file_name)
        tag = '【分系统研发投入】分析'
        ctrl_txt = self.get_sql_statement_by_tag(file_path, tag)

        if ctrl_txt:
            print(f"找到的 SQL 语句：{ctrl_txt}")
            # 这里可以继续执行 sql_statement
        else:
            print(f"未找到标记为 {tag} 的 SQL 语句。")

        # 将内容显示在 textEdit 中
        self.textEdit.setText(ctrl_txt)

    # 【分系统研发投入】分析-确定查看此SQL
    def on_pushButton_clicked(self):
        ctrl_text = self.ui.textEdit.toPlainText()
        try:
            # 执行查询
            result = self.middleware.sql_ctrl(ctrl_text)

            # 获取字段名称
            field_names = result.keys() if result.keys else []

            # 清空 tableWidget_2
            self.ui.tableView_2.setRowCount(0)
            self.ui.tableView_2.setColumnCount(0)

            # 如果有数据，则设置列数和表头
            if field_names:
                self.ui.tableView_2.setColumnCount(len(field_names))
                # 设置表头
                self.ui.tableView_2.setHorizontalHeaderLabels(field_names)

                # 填充数据
                for row_data in result:
                    row_position = self.ui.tableView_2.rowCount()
                    self.ui.tableView_2.insertRow(row_position)
                    for column, data_item in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(str(data_item) if data_item is not None else "")
                        self.ui.tableView_2.setItem(row_position, column, item)
            else:
                # 如果没有字段名称，显示提示信息
                self.ui.tableView_2.setRowCount(1)
                self.ui.tableView_2.setItem(0, 0, QtWidgets.QTableWidgetItem("No data"))

        except Exception as e:
            # 输出错误信息到控制台
            print(f"An error occurred: {e}")
            # 可以选择显示一个错误消息框
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def on_pushButton_4_clicked(self):
        # 定义文件路径
        folder_path = 'sql_txt'
        file_name = 'sql_select.txt'
        file_path = os.path.join(folder_path, file_name)
        tag = '【分小组研发投入】分析'
        ctrl_txt = self.get_sql_statement_by_tag(file_path, tag)
        # 将内容显示在 textEdit 中
        self.textEdit_2.setText(ctrl_txt)

    def on_pushButton_5_clicked(self):
        ctrl_text = self.textEdit_2.toPlainText()
        try:
            # 执行查询
            result = self.middleware.sql_ctrl(ctrl_text)

            # 获取字段名称
            field_names = result.keys() if result.keys else []

            # 清空 tableWidget_2
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)

            # 如果有数据，则设置列数和表头
            if field_names:
                self.tableWidget.setColumnCount(len(field_names))
                # 设置表头
                self.tableWidget.setHorizontalHeaderLabels(field_names)

                # 填充数据
                for row_data in result:
                    row_position = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(row_position)
                    for column, data_item in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(str(data_item) if data_item is not None else "")
                        self.tableWidget.setItem(row_position, column, item)
            else:
                # 如果没有字段名称，显示提示信息
                self.tableWidget.setRowCount(1)
                self.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem("No data"))

        except Exception as e:
            # 输出错误信息到控制台
            print(f"An error occurred: {e}")
            # 可以选择显示一个错误消息框
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def get_sql_statement_by_tag(self, file_path, tag):
        """
        根据标记读取并返回 SQL 文件中对应的 SQL 语句。

        :param file_path: SQL 文件路径
        :param tag: SQL 语句前的标记
        :return: 对应标记的 SQL 语句，如果没有找到则返回 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                current_tag = None
                sql_statement = ""
                for line in file:
                    line = line.strip()
                    if line.startswith(f"# {tag}"):
                        current_tag = tag
                    elif current_tag and line:
                        sql_statement += line + " "
                    elif current_tag and not line and sql_statement:
                        break
                if current_tag and sql_statement:
                    return sql_statement.strip()
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
        except Exception as e:
            print(f"读取文件时发生错误：{e}")
        return None

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
        self.setWindowTitle(f"在线分析工具（{host}）")

    def showEvent(self, event):
        super().showEvent(event)
        self.load_connection()
        #if not self.is_connected:
        #    QTimer.singleShot(500, self.load_connection)  # 延迟500毫秒后调用 load_connection 方法

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
                self.update_window_title(connection_info['host'])
                #QMessageBox.information(self, "成功", "自动连接成功")
            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "错误", f"自动连接失败: {e}")


# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = MainWindowLogic()
#     ui.setupUi(MainWindow)
#     MainWindow.show()
#     sys.exit(app.exec_())