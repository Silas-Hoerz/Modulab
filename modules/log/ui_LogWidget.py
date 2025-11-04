# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LogWidgetvVBOjD.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QHBoxLayout,
    QPushButton, QSizePolicy, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 298)
        Form.setStyleSheet(u"/* Basis-Stil, gilt IMMER */\n"
"QCheckBox {\n"
"    margin: 0px;           \n"
"    padding: 2px;   \n"
"    border-radius: 5px;       \n"
"    border: 1px;\n"
"	border-color: rgb(68, 68, 68);\n"
"    /* Standard-Zustand (entspricht \"info\") */\n"
"    background-color: transparent;\n"
"    color: white;\n"
"}\n"
"\n"
"/* Versteckt die Checkbox-Box */\n"
"QCheckBox::indicator {\n"
"    border: none;\n"
"    background: transparent;\n"
"    width: 0px;\n"
"    height: 0px;\n"
"}\n"
"\n"
"/* --- Dynamische Zust\u00e4nde --- */\n"
"\n"
"QCheckBox[logStatus=\"info\"] {\n"
"    background-color: transparent;\n"
"    color: white;\n"
"}\n"
"\n"
"QCheckBox[logStatus=\"warning\"] {\n"
"    background-color: rgb(220, 255, 62);  \n"
"    color: black;\n"
"}\n"
"\n"
"QCheckBox[logStatus=\"error\"] {\n"
"    background-color: rgb(255, 56, 56);  /* Rot */\n"
"    color: white;\n"
"}")
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(2, -1, 2, 2)
        self.history_text = QTextEdit(Form)
        self.history_text.setObjectName(u"history_text")

        self.verticalLayout_2.addWidget(self.history_text)

        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_3 = QHBoxLayout(self.widget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.status_label = QCheckBox(self.widget)
        self.status_label.setObjectName(u"status_label")
        self.status_label.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status_label.sizePolicy().hasHeightForWidth())
        self.status_label.setSizePolicy(sizePolicy)
        self.status_label.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.status_label)

        self.widget_2 = QWidget(self.widget)
        self.widget_2.setObjectName(u"widget_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy1)
        self.widget_2.setStyleSheet(u"/* Basis-Stil, gilt IMMER */\n"
"QWidget {\n"
"\n"
"    border-radius: 5px;         /* Abgerundete Ecken */\n"
"    \n"
"    /* Standard-Zustand (entspricht \"info\") */\n"
"    background-color: rgba(255, 255, 255, 30);\n"
"    color: white;\n"
"}\n"
"\n"
"QPushButton{\n"
"\n"
"    border-radius: 5px;         /* Abgerundete Ecken */\n"
"    padding: 2px 10px 2px 10px;\n"
"    /* Standard-Zustand (entspricht \"info\") */\n"
"    background-color: rgba(255, 255, 255, 0);\n"
"    color: white;\n"
"}\n"
"\n"
"Line{\n"
"\n"
" 	color: white;\n"
"	 background-color: rgba(255, 255, 255,50);\n"
"\n"
"}\n"
"\n"
"\n"
"\n"
"")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(3, 0, 3, 0)
        self.pushButton_profile = QPushButton(self.widget_2)
        self.pushButton_profile.setObjectName(u"pushButton_profile")

        self.horizontalLayout_4.addWidget(self.pushButton_profile)

        self.line = QFrame(self.widget_2)
        self.line.setObjectName(u"line")
        self.line.setMaximumSize(QSize(2, 16777215))
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_4.addWidget(self.line)

        self.pushButton_device = QPushButton(self.widget_2)
        self.pushButton_device.setObjectName(u"pushButton_device")

        self.horizontalLayout_4.addWidget(self.pushButton_device)


        self.horizontalLayout_3.addWidget(self.widget_2)


        self.verticalLayout_2.addWidget(self.widget)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        Form.setProperty(u"status", "")
        self.status_label.setText(QCoreApplication.translate("Form", u"Ready", None))
        self.pushButton_profile.setText(QCoreApplication.translate("Form", u"No Profile", None))
        self.pushButton_device.setText(QCoreApplication.translate("Form", u"No Device", None))
    # retranslateUi

