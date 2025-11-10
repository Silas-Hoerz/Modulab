# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SpectrometerWidgetnhdMyN.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(401, 184)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_connection = QVBoxLayout()
        self.verticalLayout_connection.setObjectName(u"verticalLayout_connection")
        self.label_device = QLabel(Form)
        self.label_device.setObjectName(u"label_device")

        self.verticalLayout_connection.addWidget(self.label_device)

        self.comboBox_deviceList = QComboBox(Form)
        self.comboBox_deviceList.setObjectName(u"comboBox_deviceList")

        self.verticalLayout_connection.addWidget(self.comboBox_deviceList)

        self.pushButton_connect = QPushButton(Form)
        self.pushButton_connect.setObjectName(u"pushButton_connect")

        self.verticalLayout_connection.addWidget(self.pushButton_connect)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_connection.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout_connection)

        self.verticalLayout_settings = QVBoxLayout()
        self.verticalLayout_settings.setObjectName(u"verticalLayout_settings")
        self.label_integrationTime = QLabel(Form)
        self.label_integrationTime.setObjectName(u"label_integrationTime")

        self.verticalLayout_settings.addWidget(self.label_integrationTime)

        self.spinBox_integrationTime = QSpinBox(Form)
        self.spinBox_integrationTime.setObjectName(u"spinBox_integrationTime")
        self.spinBox_integrationTime.setMaximum(100000)
        self.spinBox_integrationTime.setValue(100000)

        self.verticalLayout_settings.addWidget(self.spinBox_integrationTime)

        self.checkBox_correctDarkCounts = QCheckBox(Form)
        self.checkBox_correctDarkCounts.setObjectName(u"checkBox_correctDarkCounts")

        self.verticalLayout_settings.addWidget(self.checkBox_correctDarkCounts)

        self.checkBox_correctNonLinearity = QCheckBox(Form)
        self.checkBox_correctNonLinearity.setObjectName(u"checkBox_correctNonLinearity")

        self.verticalLayout_settings.addWidget(self.checkBox_correctNonLinearity)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_settings.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addLayout(self.verticalLayout_settings)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout_acquisition = QVBoxLayout()
        self.verticalLayout_acquisition.setObjectName(u"verticalLayout_acquisition")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_acquire = QPushButton(Form)
        self.pushButton_acquire.setObjectName(u"pushButton_acquire")

        self.horizontalLayout_2.addWidget(self.pushButton_acquire)


        self.verticalLayout_acquisition.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addLayout(self.verticalLayout_acquisition)

        self.widget_plot = QWidget(Form)
        self.widget_plot.setObjectName(u"widget_plot")

        self.verticalLayout.addWidget(self.widget_plot)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_device.setText(QCoreApplication.translate("Form", u"No_Spectrometer", None))
        self.pushButton_connect.setText(QCoreApplication.translate("Form", u"Connect", None))
        self.label_integrationTime.setText(QCoreApplication.translate("Form", u"Integration Time [us]", None))
        self.checkBox_correctDarkCounts.setText(QCoreApplication.translate("Form", u"Correct dark counts", None))
        self.checkBox_correctNonLinearity.setText(QCoreApplication.translate("Form", u"Correct non linearity", None))
        self.pushButton_acquire.setText(QCoreApplication.translate("Form", u"Single measurement", None))
    # retranslateUi

