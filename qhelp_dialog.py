import os

from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog

from config_data import Config_Data
from dialog_help import Ui_diaHelp


class QMyHelpDialog(QDialog):
    def __init__(self):
        super().__init__()

        uiCom = Ui_diaHelp()
        uiCom.setupUi(self)
        self.uiCom = uiCom

        self.setWindowTitle("使用帮助")
        self.setFixedSize(446, 312)

        iconPath = os.getcwd() + "\\resources\\ico-help.png"
        # 将图片路径设置为QLabel的背景
        uiCom.lblLogo.setPixmap(QPixmap(iconPath))
        # 确保图片适应标签大小
        uiCom.lblLogo.setScaledContents(True)

        # 设置icon
        self.setWindowIcon(Config_Data.MAIN_ICON)

        uiCom.btnOK.clicked.connect(self.on_ok_event)

    def on_ok_event(self):
        print("on_ok_event..")
        self.close()
