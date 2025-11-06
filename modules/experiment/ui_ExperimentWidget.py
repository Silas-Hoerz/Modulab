# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ExperimentWidgetTFuteD.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(424, 121)
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
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBox_experiments = QComboBox(Form)
        self.comboBox_experiments.setObjectName(u"comboBox_experiments")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_experiments.sizePolicy().hasHeightForWidth())
        self.comboBox_experiments.setSizePolicy(sizePolicy)
        self.comboBox_experiments.setMinimumSize(QSize(0, 0))

        self.horizontalLayout.addWidget(self.comboBox_experiments)

        self.pushButton_start = QPushButton(Form)
        self.pushButton_start.setObjectName(u"pushButton_start")
        self.pushButton_start.setMinimumSize(QSize(50, 0))
        self.pushButton_start.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_start)

        self.pushButton_pause = QPushButton(Form)
        self.pushButton_pause.setObjectName(u"pushButton_pause")
        self.pushButton_pause.setMinimumSize(QSize(50, 0))
        self.pushButton_pause.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_pause)

        self.pushButton_stop = QPushButton(Form)
        self.pushButton_stop.setObjectName(u"pushButton_stop")
        self.pushButton_stop.setMinimumSize(QSize(50, 0))
        self.pushButton_stop.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_stop)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.label_progress = QLabel(Form)
        self.label_progress.setObjectName(u"label_progress")

        self.verticalLayout_2.addWidget(self.label_progress)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        Form.setProperty(u"status", "")
        self.pushButton_start.setText(QCoreApplication.translate("Form", u"Start", None))
        self.pushButton_pause.setText(QCoreApplication.translate("Form", u"Pause", None))
        self.pushButton_stop.setText(QCoreApplication.translate("Form", u"Stop", None))
        self.label_progress.setText(QCoreApplication.translate("Form", u"TextLabel", None))
    # retranslateUi

