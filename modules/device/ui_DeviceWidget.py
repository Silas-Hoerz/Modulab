# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DeviceWidgetWoWDOh.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(326, 402)
        self.horizontalLayout_2 = QHBoxLayout(Dialog)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.comboBox_activeDevice = QComboBox(Dialog)
        self.comboBox_activeDevice.setObjectName(u"comboBox_activeDevice")
        self.comboBox_activeDevice.setMinimumSize(QSize(100, 0))

        self.verticalLayout.addWidget(self.comboBox_activeDevice)

        self.pushButton_newDevice = QPushButton(Dialog)
        self.pushButton_newDevice.setObjectName(u"pushButton_newDevice")

        self.verticalLayout.addWidget(self.pushButton_newDevice)

        self.pushButton_deleteDevice = QPushButton(Dialog)
        self.pushButton_deleteDevice.setObjectName(u"pushButton_deleteDevice")

        self.verticalLayout.addWidget(self.pushButton_deleteDevice)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.groupBox_editor = QGroupBox(Dialog)
        self.groupBox_editor.setObjectName(u"groupBox_editor")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_editor)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.groupBox_editor)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.lineEdit_name = QLineEdit(self.groupBox_editor)
        self.lineEdit_name.setObjectName(u"lineEdit_name")

        self.verticalLayout_2.addWidget(self.lineEdit_name)

        self.line_2 = QFrame(self.groupBox_editor)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_2)

        self.label_2 = QLabel(self.groupBox_editor)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.comboBox_geometry = QComboBox(self.groupBox_editor)
        self.comboBox_geometry.setObjectName(u"comboBox_geometry")

        self.verticalLayout_2.addWidget(self.comboBox_geometry)

        self.stackedWidget_dims = QStackedWidget(self.groupBox_editor)
        self.stackedWidget_dims.setObjectName(u"stackedWidget_dims")
        self.stackedWidget_dims.setFrameShape(QFrame.Shape.NoFrame)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_4 = QVBoxLayout(self.page_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_6 = QLabel(self.page_2)
        self.label_6.setObjectName(u"label_6")

        self.verticalLayout_4.addWidget(self.label_6)

        self.lineEdit_radius = QLineEdit(self.page_2)
        self.lineEdit_radius.setObjectName(u"lineEdit_radius")

        self.verticalLayout_4.addWidget(self.lineEdit_radius)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_6)

        self.stackedWidget_dims.addWidget(self.page_2)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.verticalLayout_3 = QVBoxLayout(self.page)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_4 = QLabel(self.page)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_3.addWidget(self.label_4)

        self.lineEdit_length = QLineEdit(self.page)
        self.lineEdit_length.setObjectName(u"lineEdit_length")

        self.verticalLayout_3.addWidget(self.lineEdit_length)

        self.label_5 = QLabel(self.page)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout_3.addWidget(self.label_5)

        self.lineEdit_width = QLineEdit(self.page)
        self.lineEdit_width.setObjectName(u"lineEdit_width")

        self.verticalLayout_3.addWidget(self.lineEdit_width)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_5)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.stackedWidget_dims.addWidget(self.page)

        self.verticalLayout_2.addWidget(self.stackedWidget_dims)

        self.label_area = QLabel(self.groupBox_editor)
        self.label_area.setObjectName(u"label_area")
        self.label_area.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_2.addWidget(self.label_area)

        self.line = QFrame(self.groupBox_editor)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line)

        self.label_3 = QLabel(self.groupBox_editor)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_2.addWidget(self.label_3)

        self.lineEdit_tags = QLineEdit(self.groupBox_editor)
        self.lineEdit_tags.setObjectName(u"lineEdit_tags")

        self.verticalLayout_2.addWidget(self.lineEdit_tags)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.pushButton_saveDevice = QPushButton(self.groupBox_editor)
        self.pushButton_saveDevice.setObjectName(u"pushButton_saveDevice")

        self.horizontalLayout_3.addWidget(self.pushButton_saveDevice)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout_2.addWidget(self.groupBox_editor)


        self.retranslateUi(Dialog)

        self.stackedWidget_dims.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.pushButton_newDevice.setText(QCoreApplication.translate("Dialog", u"New Device", None))
        self.pushButton_deleteDevice.setText(QCoreApplication.translate("Dialog", u"Delete Device", None))
        self.groupBox_editor.setTitle(QCoreApplication.translate("Dialog", u"Edit", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Name", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Geometry", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"Radius", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Length", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"Width", None))
        self.label_area.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Tags", None))
        self.pushButton_saveDevice.setText(QCoreApplication.translate("Dialog", u"Save Device", None))
    # retranslateUi

