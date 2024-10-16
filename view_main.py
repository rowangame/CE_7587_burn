# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_main.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_main_view(object):
    def setupUi(self, main_view):
        main_view.setObjectName("main_view")
        main_view.resize(1024, 768)
        self.centralwidget = QtWidgets.QWidget(main_view)
        self.centralwidget.setObjectName("centralwidget")
        main_view.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_view)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1024, 26))
        self.menubar.setObjectName("menubar")
        self.mnuOp = QtWidgets.QMenu(self.menubar)
        self.mnuOp.setObjectName("mnuOp")
        self.mnuSerial = QtWidgets.QMenu(self.menubar)
        self.mnuSerial.setObjectName("mnuSerial")
        self.mnuAbout = QtWidgets.QMenu(self.menubar)
        self.mnuAbout.setObjectName("mnuAbout")
        self.mnuType = QtWidgets.QMenu(self.menubar)
        self.mnuType.setObjectName("mnuType")
        self.mnuBinType = QtWidgets.QMenu(self.menubar)
        self.mnuBinType.setObjectName("mnuBinType")
        self.menuQueryDev = QtWidgets.QMenu(self.menubar)
        self.menuQueryDev.setObjectName("menuQueryDev")
        main_view.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_view)
        self.statusbar.setObjectName("statusbar")
        main_view.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(main_view)
        self.toolBar.setIconSize(QtCore.QSize(40, 40))
        self.toolBar.setObjectName("toolBar")
        main_view.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionQuit = QtWidgets.QAction(main_view)
        self.actionQuit.setObjectName("actionQuit")
        self.actionList = QtWidgets.QAction(main_view)
        self.actionList.setObjectName("actionList")
        self.actionFWSelect = QtWidgets.QAction(main_view)
        self.actionFWSelect.setObjectName("actionFWSelect")
        self.actionHelp = QtWidgets.QAction(main_view)
        self.actionHelp.setObjectName("actionHelp")
        self.actionVersion = QtWidgets.QAction(main_view)
        self.actionVersion.setObjectName("actionVersion")
        self.actionBinFile = QtWidgets.QAction(main_view)
        self.actionBinFile.setObjectName("actionBinFile")
        self.actionC = QtWidgets.QAction(main_view)
        self.actionC.setObjectName("actionC")
        self.actionPython = QtWidgets.QAction(main_view)
        self.actionPython.setObjectName("actionPython")
        self.actionQueryDevInfo = QtWidgets.QAction(main_view)
        self.actionQueryDevInfo.setObjectName("actionQueryDevInfo")
        self.mnuOp.addAction(self.actionQuit)
        self.mnuSerial.addAction(self.actionList)
        self.mnuSerial.addSeparator()
        self.mnuSerial.addAction(self.actionBinFile)
        self.mnuAbout.addAction(self.actionHelp)
        self.mnuAbout.addSeparator()
        self.mnuAbout.addAction(self.actionVersion)
        self.menuQueryDev.addAction(self.actionQueryDevInfo)
        self.menubar.addAction(self.mnuOp.menuAction())
        self.menubar.addAction(self.mnuSerial.menuAction())
        self.menubar.addAction(self.mnuType.menuAction())
        self.menubar.addAction(self.mnuBinType.menuAction())
        self.menubar.addAction(self.menuQueryDev.menuAction())
        self.menubar.addAction(self.mnuAbout.menuAction())

        self.retranslateUi(main_view)
        QtCore.QMetaObject.connectSlotsByName(main_view)

    def retranslateUi(self, main_view):
        _translate = QtCore.QCoreApplication.translate
        main_view.setWindowTitle(_translate("main_view", "CE_7587_7588烧入工具"))
        self.mnuOp.setTitle(_translate("main_view", "操 作"))
        self.mnuSerial.setTitle(_translate("main_view", "配 置"))
        self.mnuAbout.setTitle(_translate("main_view", "关 于"))
        self.mnuType.setTitle(_translate("main_view", "协议"))
        self.mnuBinType.setTitle(_translate("main_view", "类型"))
        self.menuQueryDev.setTitle(_translate("main_view", "查询"))
        self.toolBar.setWindowTitle(_translate("main_view", "toolBar"))
        self.actionQuit.setText(_translate("main_view", "退 出"))
        self.actionList.setText(_translate("main_view", "选择串口"))
        self.actionFWSelect.setText(_translate("main_view", "选择文件"))
        self.actionHelp.setText(_translate("main_view", "使用帮助"))
        self.actionVersion.setText(_translate("main_view", "关于软件"))
        self.actionBinFile.setText(_translate("main_view", "选择文件 (bin)"))
        self.actionC.setText(_translate("main_view", "C++"))
        self.actionPython.setText(_translate("main_view", "Python"))
        self.actionQueryDevInfo.setText(_translate("main_view", "设备信息"))