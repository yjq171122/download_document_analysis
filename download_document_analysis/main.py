import sys
from PyQt5.QtGui import QFont
from PyQt5 import QtWidgets
from main_window_logic import MainWindowLogic
#pyuic5 -o fenxi.py JMV5.ui
#pyuic5 -o setinput.py SETINPUT.ui
#打包
#python -m venv venv 虚拟环境
#pyinstaller -D -w main.py  打包命令
#打包所需要下载的库
# pip install PyQt5
# pip install sqlalchemy
# pip install pandas
# pip install requests
# pip install beautifulsoup4
# pip install pymysql
# pip install pyinstaller

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # 设置全局字体
    font = QFont("SimSun", 12)  # 设置字体为宋体，大小为18
    app.setFont(font)
    mainWin = MainWindowLogic()
    mainWin.show()
    sys.exit(app.exec_())

