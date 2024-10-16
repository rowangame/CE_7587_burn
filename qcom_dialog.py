from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QFont, QColor
from PyQt5.QtWidgets import QDialog, QApplication, QCheckBox, QMessageBox

from center_delegate import CenterDelegate
from config_data import Config_Data
from dialog_com import Ui_dialogCom
import serial.tools.list_ports


class ComSelectDialog(QDialog):
    def __init__(self):
        super().__init__()

        uiCom = Ui_dialogCom()
        uiCom.setupUi(self)
        self.uiCom = uiCom

        self.setWindowTitle("选择串口")
        self.setWindowIcon(Config_Data.MAIN_ICON)

        # 设置对话框大小不可调节
        self.setFixedSize(460, 360)

        # 居中显示
        desktop = QApplication.desktop()
        tmpRect = self.geometry()
        tmpX = (desktop.width() - tmpRect.width()) // 2 - 200
        tmpY = (desktop.height() - tmpRect.height()) // 2
        self.move(int(tmpX), int(tmpY))

        self.comLst = []
        self.comLst.append("None")

        self.initEvents()

    def on_refresh_event(self):
        print("on_refresh...")

        plist = list(serial.tools.list_ports.comports())
        if len(plist) == 0:
            self.showWarningInfo("获取串口列表为空")
            return

        tmpView = self.getView()

        self.comLst.clear()
        self.comLst.append("None")
        for tmpP in plist:
            # print("plist=", tmpP.name)
           self.comLst.append(tmpP.name)

        max_row = len(self.comLst)
        max_col = 3
        self.model = QStandardItemModel(max_row, max_col)
        for row in range(0, max_row):
            if row == 0:
                self.model.setItem(row, 0, QStandardItem("序号"))
                self.model.setItem(row, 1, QStandardItem("串口"))
                self.model.setItem(row, 2, QStandardItem("操作"))
            else:
                self.model.setItem(row, 0, QStandardItem(str(row)))
                self.model.setItem(row, 1, QStandardItem(self.comLst[row]))

                tmpCheckBox = QStandardItem()
                tmpCheckBox.setCheckable(True)
                tmpCheckBox.setCheckState(Qt.Unchecked)
                self.model.setItem(row, 2, tmpCheckBox)

        tmpView.tableView.setModel(self.model)

        # 标题高亮显示
        for i in range(max_col):
            # 设置标题加粗显示
            tmpItem = self.model.item(0, i)
            # 设置字体颜色
            tmpItem.setForeground(QBrush(QColor(0, 0, 0)))
            # 设置字体加粗
            tmpItem.setFont(QFont("Times", 12, QFont.Black))
            # 设置背景颜色
            tmpItem.setBackground(QBrush(QColor(0, 200, 0)))

    def on_ok_event(self):
        try:
            sltComs = []
            # 判断当前是否选择了一个串口
            max_row = len(self.comLst)
            for i in range(1, max_row):
                tmpIndex = self.model.index(i, 2)
                if self.model.data(tmpIndex, Qt.CheckStateRole) == Qt.Checked:
                    # print(f"Row {i} is checked.")
                    sltComs.append(self.comLst[i])
                # else:
                #     print(f"Row {i} is unchecked.")
            if len(sltComs) == 0:
                Config_Data.mComNum = ""
                sInfo = "当前没有选择串口"
                self.showWarningInfo(sInfo)
            elif len(sltComs) > 1:
                Config_Data.mComNum = ""
                sInfo = "当前只能选择一个串口类型"
                self.showWarningInfo(sInfo)
            else:
                Config_Data.mComNum = sltComs[0]
                print(f"选择的串口:{Config_Data.mComNum}")
                self.close()
        except Exception as e:
            print(repr(e))

    def on_cancel_event(self):
        Config_Data.mComNum = ""
        self.close()

    def initEvents(self):
        tmpView = self.getView()
        tmpView.btnRefresh.clicked.connect(self.on_refresh_event)
        tmpView.btnOk.clicked.connect(self.on_ok_event)
        tmpView.btnCancel.clicked.connect(self.on_cancel_event)

        # 设置table view 标题
        max_row = 4
        max_col = 3
        self.model = QStandardItemModel(max_row, max_col)
        for row in range(0, max_row):
            if row == 0:
                self.model.setItem(row, 0, QStandardItem("序号"))
                self.model.setItem(row, 1, QStandardItem("串口"))
                self.model.setItem(row, 2, QStandardItem("操作"))
            break

        tmpView.tableView.setModel(self.model)
        # 标题高亮显示
        for i in range(max_col):
            # 设置标题加粗显示
            tmpItem = self.model.item(0, i)
            # 设置字体颜色
            tmpItem.setForeground(QBrush(QColor(0, 0, 0)))
            # 设置字体加粗
            tmpItem.setFont(QFont("Times", 12, QFont.Black))
            # 设置背景颜色
            tmpItem.setBackground(QBrush(QColor(0, 200, 0)))

        # 设置自定义的委托(单元格居中)
        delegate = CenterDelegate()
        tmpView.tableView.setItemDelegate(delegate)

    def getView(self):
        return self.uiCom

    def showWarningInfo(self, info):
        tmpView = self.getView()
        tmpView.mWarning = QMessageBox(QMessageBox.Warning, '警告', info)
        tmpView.mWarning.show()
