# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog_admin.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dia_admin(object):
    def setupUi(self, dia_admin):
        dia_admin.setObjectName("dia_admin")
        dia_admin.resize(220, 120)
        self.label = QtWidgets.QLabel(dia_admin)
        self.label.setGeometry(QtCore.QRect(10, 21, 61, 16))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(dia_admin)
        self.label_2.setGeometry(QtCore.QRect(14, 55, 51, 16))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.edtName = QtWidgets.QLineEdit(dia_admin)
        self.edtName.setGeometry(QtCore.QRect(75, 20, 131, 21))
        self.edtName.setMaxLength(20)
        self.edtName.setObjectName("edtName")
        self.edtPsw = QtWidgets.QLineEdit(dia_admin)
        self.edtPsw.setGeometry(QtCore.QRect(75, 54, 131, 21))
        self.edtPsw.setMaxLength(20)
        self.edtPsw.setObjectName("edtPsw")
        self.btnOK = QtWidgets.QPushButton(dia_admin)
        self.btnOK.setGeometry(QtCore.QRect(82, 86, 61, 21))
        self.btnOK.setObjectName("btnOK")

        self.retranslateUi(dia_admin)
        QtCore.QMetaObject.connectSlotsByName(dia_admin)

    def retranslateUi(self, dia_admin):
        _translate = QtCore.QCoreApplication.translate
        dia_admin.setWindowTitle(_translate("dia_admin", "授权登陆"))
        self.label.setText(_translate("dia_admin", "用户名："))
        self.label_2.setText(_translate("dia_admin", "密    码："))
        self.btnOK.setText(_translate("dia_admin", "确定"))
