# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LogWidgetnUxuWG.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QSizePolicy, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 300)
        Form.setStyleSheet(u"/* Basis-Stil, gilt IMMER */\n"
"QCheckBox {\n"
"    margin: 0px;                /* Au\u00dfenabstand: 0 (b\u00fcndig) */\n"
"    padding: 3px 6px 3px 6px;   /* Dein gew\u00fcnschter Innenabstand */\n"
"    border-radius: 5px;         /* Abgerundete Ecken */\n"
"    \n"
"    /* Standard-Zustand (entspricht \"info\") */\n"
"    background-color: transparent;\n"
"    color: black;\n"
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
"    color: black;\n"
"}\n"
"\n"
"QCheckBox[logStatus=\"warning\"] {\n"
"    background-color: #FFC000;  /* Orange */\n"
"    color: black;\n"
"}\n"
"\n"
"QCheckBox[logStatus=\"error\"] {\n"
"    background-color: #C00000;  /* Rot */\n"
"    color: white;\n"
"}")
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.history_text = QTextEdit(Form)
        self.history_text.setObjectName(u"history_text")

        self.verticalLayout_2.addWidget(self.history_text)

        self.status_label = QCheckBox(Form)
        self.status_label.setObjectName(u"status_label")
        self.status_label.setEnabled(True)
        self.status_label.setCheckable(True)

        self.verticalLayout_2.addWidget(self.status_label)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        Form.setProperty(u"status", "")
        self.status_label.setText(QCoreApplication.translate("Form", u"Bereit", None))
    # retranslateUi

