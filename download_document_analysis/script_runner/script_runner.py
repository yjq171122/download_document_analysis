import sys
import chardet
from PyQt5.QtWidgets import  QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QSizePolicy, \
    QHBoxLayout, QLabel, QMainWindow


class ScriptRunner(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.setGeometry(300, 300, 1800, 1000)
    def initUI(self):
        # 创建一个中心部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        input_layout = QVBoxLayout()
        self.input_label = QLabel("输入Python脚本：", central_widget)
        input_layout.addWidget(self.input_label)

        # 文本编辑区域
        self.script_edit = QTextEdit(central_widget)
        self.script_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        input_layout.addWidget(self.script_edit, 1)
        main_layout.addLayout(input_layout)

        output_layout = QVBoxLayout()
        self.output_label = QLabel("输出内容：", central_widget)
        output_layout.addWidget(self.output_label)

        # 输出区域
        self.output_area = QTextEdit(central_widget)
        self.output_area.setReadOnly(True)
        self.output_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        output_layout.addWidget(self.output_area)
        main_layout.addLayout(output_layout)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 添加一个拉伸空间，使按钮靠右对齐

        # 选择文件按钮
        self.file_button = QPushButton('选择文件', central_widget)
        self.file_button.clicked.connect(self.select_file)
        self.file_button.setFixedWidth(250)  # 设置按钮的固定宽度
        self.file_button.setFixedHeight(50)
        button_layout.addWidget(self.file_button)

        # 执行按钮
        self.run_button = QPushButton('执行脚本', central_widget)
        self.run_button.clicked.connect(self.exec_script)
        self.run_button.setFixedWidth(250)  # 设置按钮的固定宽度
        self.run_button.setFixedHeight(50)
        button_layout.addWidget(self.run_button)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

        # 设置窗口标题
        self.setWindowTitle('执行Python脚本')

    def select_file(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "选择Python脚本", "", "Python Files (*.py);;All Files (*)",
                                                       options=options)
            if file_name:
                with open(file_name, 'rb') as file:  # 以二进制模式打开文件
                    raw_data = file.read()
                    encoding = chardet.detect(raw_data)['encoding']  # 检测文件编码
                    script_content = raw_data.decode(encoding, errors='replace')  # 使用检测到的编码解码
                self.script_edit.setText(script_content)
        except Exception as e:
            self.output_area.append(f"选择文件时发生错误: {str(e)}")

    def exec_script(self):
        script_code = self.script_edit.toPlainText().strip()
        if not script_code:
            self.output_area.append("请输入或加载有效的Python脚本。")
            return

        try:
            # 重定向标准输出和标准错误
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = self
            sys.stderr = self

            self.output_area.clear()

            # 执行用户输入的脚本
            exec(script_code, {'__name__': '__main__', '__file__': '<user_input>'})

            # 恢复标准输出和标准错误
            sys.stdout = old_stdout
            sys.stderr = old_stderr


            self.output_area.append("脚本执行成功。")
        except Exception as e:
            self.output_area.append(f"无法执行脚本: {str(e)}")

    # 重写 write 方法，将输出重定向到 QTextEdit
    def write(self, text):
        self.output_area.insertPlainText(text)