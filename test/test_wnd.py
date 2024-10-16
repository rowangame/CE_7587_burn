# -*- coding: UTF-8 -*-
# @Time    : 2024/10/109:50
# @Author  : xielunguo
# @Email   : xielunguo@cosonic.com
# @File    : test_wnd.py
# @IDE     : PyCharm

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableView, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Resizable QTableView and QTextEdit")

        # 创建中心小部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 设置垂直布局
        layout = QVBoxLayout(central_widget)

        # 创建 QTableView
        self.table_view = QTableView()
        self.model = QStandardItemModel(10, 2)  # 10 行 2 列
        for row in range(10):
            for column in range(2):
                item = QStandardItem(f"Item {row}, {column}")
                self.model.setItem(row, column, item)
        self.table_view.setModel(self.model)

        # 创建 QTextEdit
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type here...")

        # 将控件添加到布局中
        layout.addWidget(self.table_view)
        layout.addWidget(self.text_edit)

        # 设置布局伸缩性
        layout.setStretch(0, 1)  # QTableView 占用大部分空间
        layout.setStretch(1, 2)  # QTextEdit 也占用空间


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.resize(800, 600)  # 设置初始窗口大小
    main_window.show()
    sys.exit(app.exec_())