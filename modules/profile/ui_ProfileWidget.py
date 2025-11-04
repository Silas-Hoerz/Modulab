# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ProfileWidgetZtsESG.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(297, 201)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)

        self.verticalLayout_2.addWidget(self.label)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.listWidget_profiles = QListWidget(Form)
        self.listWidget_profiles.setObjectName(u"listWidget_profiles")

        self.horizontalLayout_2.addWidget(self.listWidget_profiles)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButton_new = QPushButton(Form)
        self.pushButton_new.setObjectName(u"pushButton_new")

        self.verticalLayout.addWidget(self.pushButton_new)

        self.pushButton_delete = QPushButton(Form)
        self.pushButton_delete.setObjectName(u"pushButton_delete")

        self.verticalLayout.addWidget(self.pushButton_delete)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.pushButton_done = QPushButton(Form)
        self.pushButton_done.setObjectName(u"pushButton_done")

        self.verticalLayout.addWidget(self.pushButton_done)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle("")
        self.label.setText(QCoreApplication.translate("Form", u"Profile", None))
        self.pushButton_new.setText(QCoreApplication.translate("Form", u"New ", None))
        self.pushButton_delete.setText(QCoreApplication.translate("Form", u"Delete", None))
        self.pushButton_done.setText(QCoreApplication.translate("Form", u"Done", None))
    # retranslateUi

