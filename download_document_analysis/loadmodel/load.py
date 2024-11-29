import sys  
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QMessageBox, QCompleter, QGridLayout  
from PyQt5.QtWidgets import QMainWindow,QVBoxLayout, QHBoxLayout,QTextEdit
from PyQt5.QtCore import Qt  
import requests
import hashlib
import json
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup  
import os
class OpenDoc:  
    def __init__(self, document_url, doc_id,cookie_str):  
        self.document_url = document_url  
        self.doc_id = doc_id  
        #self.tab = tab  
        self.headers = {  
            'Referer': self.document_url,  
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
            "Cookie": cookie_str,
            'u': '1'  
        }    
    @staticmethod  
    def _md5(raw_data):  
        md5 = hashlib.md5()  
        md5.update(raw_data.encode('utf8'))  
        return md5.hexdigest().lower()  
  
    def get_data(self):  
        params = {
            #'tab': self.tab,
            'u': '',
            'noEscape': 1,
            'enableSmartsheetSplit': 1,
            'startrow': 0,
            'endrow': 60,
            'needSheetState': 1,
            'id': self.doc_id,
            'normal': 1,
            'outformat': 1,
            'wb': 1,
            'nowb': 0,
            'callback': 'clientVarsCallback',
            'xsrf': '',
            't': self._md5('{}'.format(int(time.time())))
        }
        #target_url = 'https://doc.weixin.qq.com/dop-api/opendoc'
        target_url = 'https://docs.qq.com/dop-api/opendoc'  
        res = requests.get(target_url, headers=self.headers, params=params)  
        try:   
            json_str = res.text[19: -1] 
            json_data = json.loads(json_str)  
            globalPadIdvalue = json_data.get('clientVars', {}).get('globalPadId')  
            if globalPadIdvalue:  
                # 存在 globalPadIdvalue，直接返回  
                return globalPadIdvalue  
            else:  
                print("字典中不存在 'globalPadIdvalue' 键")  
                return None  
        except json.JSONDecodeError:  
            print("解析 JSON 时出错")  
            return None  
        except Exception as e:  
            print(f"发生未知错误: {e}")  
            return None  
    def get_padtype(self):  
        params = {
            #'tab': self.tab,
            'u': '',
            'noEscape': 1,
            'enableSmartsheetSplit': 1,
            'startrow': 0,
            'endrow': 60,
            'needSheetState': 1,
            'id': self.doc_id,
            'normal': 1,
            'outformat': 1,
            'wb': 1,
            'nowb': 0,
            'callback': 'clientVarsCallback',
            'xsrf': '',
            't': self._md5('{}'.format(int(time.time())))
        }
        #target_url = 'https://doc.weixin.qq.com/dop-api/opendoc'
        target_url = 'https://docs.qq.com/dop-api/opendoc'  
        res = requests.get(target_url, headers=self.headers, params=params)  
        try:   
            json_str = res.text[19: -1] 
            json_data = json.loads(json_str)  
            padType = json_data.get('clientVars', {}).get('padType')  
            if padType:  
                # 存在 globalPadIdvalue，直接返回  
                return padType  
            else:  
                print("字典中不存在 'padType' 键")  
                return None  
        except json.JSONDecodeError:  
            print("解析 JSON 时出错")  
            return None  
        except Exception as e:  
            print(f"发生未知错误: {e}")  
            return None  
  
#def getOperationId(self, export_excel_url, pad_id):  # 修改方法名和添加参数  
#    body = {"docId": pad_id, "version": "2"}  
#    res = requests.post(url=export_excel_url, headers=self.headers, data=body, verify=False)  
#    operation_id = res.json()["operationId"]
#    return operation_id
    def getOperationId(self, export_excel_url, pad_id):  # 修改方法名和添加参数  
        body = {"docId": pad_id, "version": "2"}  
        res = requests.post(url=export_excel_url, headers=self.headers, data=body, verify=False)  
        # 检查响应状态码，确保请求成功  
        if res.status_code == 200:  
            operation_id = res.json().get("operationId", None)  # 使用get方法安全访问  
            if operation_id is None:  
                print(f"Warning: 'operationId' not found in the response for docId {pad_id}.")  
                # 这里可以抛出异常，或者返回一个错误码/错误信息  
                return None  # 或者其他适当的错误处理  
            return operation_id  
        else:  
            print(f"Error: Request to {export_excel_url} failed with status code {res.status_code}.")  
            # 根据需要处理错误，比如抛出异常或返回错误码  
            return None  # 或者抛出异常
    
    def ExcelDownload(self, check_progress_url, file_name):  
        start_time = time.time()  
        file_url = ""  
  
        while True:  
            try:  
                res = requests.get(url=check_progress_url, headers=self.headers, verify=False, timeout=10)  # 添加超时设置  
                res.raise_for_status()  # 检查响应状态码  
                progress = res.json()["progress"]  
                if progress == 100:  
                    file_url = res.json()["file_url"]  
                    break  
                elif time.time() - start_time > 30:  
                    print("准备超时,请排查")  
                    break  
            except requests.exceptions.RequestException as e:  
                print(f"请求错误: {e}")  
                break  # 可以选择在这里退出循环或进行其他错误处理  
  
        if file_url:  
            try:  
                res = requests.get(url=file_url, headers=self.headers, verify=False, stream=True)  # 使用stream模式下载大文件  
                res.raise_for_status()  
                with open(file_name, "wb") as f:  
                    for chunk in res.iter_content(chunk_size=8192):  
                        if chunk:  
                            f.write(chunk)  
                QMessageBox.information(None,"提示", "下载成功,文件路径: " + file_name)  
            except requests.exceptions.RequestException as e:  
                print(f"下载文件时发生错误: {e}")  
        else:  
            print("下载文件地址获取失败, 下载excel文件不成功")  

class TencentDocDownloaderApp(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.load_data()

    def initUI(self):
        self.setWindowTitle('腾讯文档下载器')
        self.setGeometry(500, 150, 800, 600)
        # 创建中心部件
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # 使用QGridLayout来组织布局
        self.layout_main = QGridLayout(self.central_widget)
        self.entry_fields = []  # 存储输入框的列表
        self.history = []  # 用于存储历史链接

        # Cookie 输入部分
        self.cookie_label = QLabel("请输入Cookie:")
        self.cookie_entry = QTextEdit()
        self.cookie_instruction = QLabel("注释:浏览器F12/Fn+F12查看->点击网络->点击XHR->选取GET/POST->Request Headers->Cookie")

        # 使用QVBoxLayout组织Cookie部分
        cookie_layout = QVBoxLayout()
        cookie_layout.addWidget(self.cookie_label)
        cookie_layout.addWidget(self.cookie_entry)
        cookie_layout.addWidget(self.cookie_instruction)
        cookie_layout.addStretch(1)  # 添加弹性空间，使布局更美观

        # 将Cookie布局添加到网格布局的指定位置
        self.layout_main.addLayout(cookie_layout, 0, 0, 1, 2)  # 占据第0行，第0、1列
        # 文件夹选择部分

        self.folder_label = QLabel("请选择文件夹:")
        self.folder_entry = QLineEdit()
        self.select_folder_button = QPushButton("选择文件夹")
        self.select_folder_button.clicked.connect(self.select_folder)


        # 使用QHBoxLayout组织文件夹选择部分
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_entry)
        folder_layout.addWidget(self.select_folder_button)
 
        # 将文件夹选择布局添加到网格布局的指定位置

        self.layout_main.addLayout(folder_layout, 1, 0, 1, 2)  # 占据第1行，第0、1列
        # 动态添加链接输入框的容器布局
        self.entry_container_layout = QVBoxLayout()

        # 初始添加一个输入框
        self.add_entry_field(initial=True)
        # 将链接输入框容器布局添加到网格布局的指定位置
        entry_container_widget = QWidget()  # 创建一个容器小部件来容纳QVBoxLayout
        entry_container_widget.setLayout(self.entry_container_layout)
        self.layout_main.addWidget(entry_container_widget, 2, 0, 1, 2)  # 占据第2行，第0、1列
        
        # 按钮布局部分
        self.clear_button = QPushButton("清除链接")
        self.clear_button.clicked.connect(self.clear_entry)
        self.add_entry_button = QPushButton("添加链接")
        self.add_entry_button.clicked.connect(self.add_entry_field)
        self.download_button = QPushButton("下载文档链接")
        self.download_button.clicked.connect(self.download_document)

        # 使用QHBoxLayout组织按钮部分
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.add_entry_button)
        button_layout.addWidget(self.download_button)
        #button_layout.addStretch(1)  # 添加弹性空间，使布局更美观

        # 将按钮布局添加到网格布局的指定位置
        self.layout_main.addLayout(button_layout, 3, 0, 1, 2)  # 占据第3行，第0、1列
        # 设置网格布局的间距和边距
        self.layout_main.setSpacing(10)
        self.layout_main.setContentsMargins(20, 30, 30, 20)

        # 设置控件的字体和大小

        '''self.setStyleSheet(
            QLabel {
                font-size: 22px;
                font-weight: normal;
                color: #333333;  /* 设置字体颜色 */
                padding: 5px;    /* 可选，根据需要调整 */
            }
        
            QLineEdit {
                font-size: 22px;
                padding: 5px;
                color: #333333;  /* 设置字体颜色 */
                border: 1px solid #d3d3d3;  /* 添加边框 */
                border-radius: 4px;  /* 添加圆角 */
                background-color: #ffffff;  /* 设置背景颜色 */
            }
        
            QPushButton {
                font-size: 22px;
                padding: 5px 10px;
                margin: 5px;
                color: #333333;  /* 设置字体颜色 */
                background-color: #ffffff;  /* 设置背景颜色 */
                border: none;  /* 去除默认边框 */
                border-radius: 4px;  /* 添加圆角 */
            }
            
            QTextEdit {
                font-size: 22px;
                padding: 5px 10px;
                margin: 5px;
                color: #333333;  /* 设置字体颜色 */
                background-color: #ffffff;  /* 设置背景颜色 */
                border: 1px solid #d3d3d3;  /* 添加边框 */
                border-radius: 4px;  /* 添加圆角 */
            }       
            QPushButton:hover {
                background-color: #add8e6;  /* 鼠标悬停时改变背景颜色 */
            }
        
            QPushButton:pressed {
                background-color: #87CEEB;  /* 按下按钮时改变背景颜色 */
            }
        )'''
  
        # 状态栏  
        statusbar = self.statusBar()  
        statusbar.showMessage('准备就绪', 30000)  
  
    def add_entry_field(self, initial=False):  
        entry_layout = QHBoxLayout()  
  
        new_entry_label = QLabel("请输入腾讯在线文档的链接:")  
        new_entry = QLineEdit()  
        delete_button = QPushButton("删除链接")  
  
        # 连接删除按钮的点击事件  
        delete_button.clicked.connect(lambda: self.delete_entry(new_entry_label, new_entry, delete_button))  
        # 设置QCompleter  
        completer = QCompleter(self.history, self)  
        completer.setCaseSensitivity(0)  # 不区分大小写  
        new_entry.setCompleter(completer)  
        new_entry.completer_ref = completer  # 保存引用  
        new_entry.textEdited.connect(self.update_history)  # 更新历史数据  
  
        entry_layout.addWidget(new_entry_label)  
        entry_layout.addWidget(new_entry)  
        entry_layout.addWidget(delete_button)  
  
        if initial or not self.entry_fields:  
            self.entry_container_layout.addLayout(entry_layout)  
        else:  
            self.entry_container_layout.insertLayout(self.entry_container_layout.count() - 1, entry_layout)  # 插入到最后一个元素之前，因为最后一个元素是添加链接的按钮布局  
  
        self.entry_fields.append(new_entry)  
  
    def delete_entry(self, label, entry, button):  
        # 获取包含这些控件的布局  
        entry_layout = label.parentWidget().layout()  
        
        # 从布局和列表中移除控件  
        entry_layout.removeWidget(label)  
        entry_layout.removeWidget(entry)  
        entry_layout.removeWidget(button)  
        
        # 删除控件（这将确保它们被正确销毁）  
        label.deleteLater()  
        entry.deleteLater()  
        button.deleteLater()  
        
        # 从列表中移除输入框  
        self.entry_fields = [e for e in self.entry_fields if e is not entry] 
    def update_history(self, text):  
        if text and text not in self.history:  
            self.history.append(text)  
            self.save_data()  # 保存数据到文件
            # 更新所有输入框的QCompleter  
            for entry in self.entry_fields:  
                entry.setCompleter(QCompleter(self.history, self))  
  
    def save_data(self):  
        data = {  
            'cookie': self.cookie_entry.toPlainText(),  
            'links': [entry.text() for entry in self.entry_fields],  
            'history': self.history  
        }
        config_dir = "conf"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)  # 创建文件夹

        config_file = f"{config_dir}/data.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

  
    def load_data(self):
        config_dir = "conf"
        config_file = f"{config_dir}/data.json"
        if not os.path.exists(config_file):
            return  
  
        try:  
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)  
  
            self.cookie_entry.setText(data.get('cookie', ''))  
            links = data.get('links', [])  
            history = data.get('history', [])  
            self.history = history  
  
            for i, link in enumerate(links):  
                if len(self.entry_fields) <= i:  
                    self.add_entry_field()  
                self.entry_fields[i].setText(link)  
            # 更新所有输入框的补全器  
            for entry in self.entry_fields:  
                self.update_entry_completer(self.entry_fields.index(entry))  
  
        except Exception as e:  
            print(f"Error loading data: {e}")    
    def update_entry_completer(self, index):  
        if 0 <= index < len(self.entry_fields):  
            completer = QCompleter(self.history, self)  
            completer.setCaseSensitivity(Qt.CaseInsensitive)  
            self.entry_fields[index].setCompleter(completer)  
  
    def _set_data_file_path(self, filename):  
        self._data_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)  
  
    @property  
    def data_file_path(self):  
        return self._data_file_path  
  
    def closeEvent(self, event):  
        self.save_data()  
        super().closeEvent(event)  

    def select_folder(self):  
        root_dir = QFileDialog.getExistingDirectory(self, "选择文件夹")  
        self.folder_entry.setText(root_dir)  
  
    def clear_entry(self):  
        for entry in self.entry_fields:  
            entry.clear()  
  
    def download_document(self):  
        urls = [entry.text().strip() for entry in self.entry_fields if entry.text().strip()]  # 过滤掉空字符串
        cookie_str = self.cookie_entry.toPlainText()   
        if not urls:  
            QMessageBox.critical(self, "错误", "请输入至少一个有效的文档URL")  
            return    
        documents = []  
        doc_ids = []  
        pad_ids= []
        padtypes = []  
        operation_ids = []  # 用于存储每个文档的操作ID  
        
        for i, url in enumerate(urls, start=1):  
            if not url:  
                continue  # 跳过空URL  
            doc_id = urlparse(url).path.strip('/').split('/')[-1]  
            doc = OpenDoc(url, doc_id, cookie_str)  
            documents.append(doc)  
            doc_ids.append(doc_id)
            pad_id=doc.get_data()
            pad_ids.append(pad_id)                 
            padtype = doc.get_padtype()  # 假设这个方法存在  
            padtypes.append(padtype)
            export_excel_url = 'https://docs.qq.com/v1/export/export_office'  
            # 获取每个文档的操作ID  
            operation_id = doc.getOperationId(export_excel_url, pad_id)  # 确保这个方法接受 URL 和 doc_id  
            if not operation_id:  
                QMessageBox.critical(f"错误（文档{i}）", "无法获取操作ID")  
                continue  # 跳过当前循环迭代，继续下一个URL
            operation_ids.append(operation_id)  
            check_progress_url = f'https://docs.qq.com/v1/export/query_progress?operationId={operation_id}'

            headers = {'Cookie': cookie_str} if cookie_str else {}  
            # 发送 GET 请求  
            response = requests.get(url, headers=headers)  
            # 检查响应状态码  
            if response.status_code != 200:  
                QMessageBox.critical(f"错误（文档{i})", f"无法访问 URL: {url}")  
                continue  
            # 解析 HTML  
            soup = BeautifulSoup(response.text, "html.parser")  
            # 尝试获取标题  
            title = soup.title.string if soup.title else "无标题"  
            root_dir =self.folder_entry.text()
            if padtype == 'doc':  
                file_name = os.path.join(root_dir, f'{title}.docx')
            elif padtype == 'sheet':  
                file_name = os.path.join(root_dir, f'{title}.xlsx')
            else:  
                file_name = os.path.join(root_dir, f'{title}.ppt')
                #print(f"获取到的操作ID为: {operation_id}")  
            doc.ExcelDownload(check_progress_url, file_name)
