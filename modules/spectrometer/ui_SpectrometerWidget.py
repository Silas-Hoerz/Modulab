# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SpectrometerWidgetUdjLIV.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLayout,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(503, 347)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QSize(400, 0))
        Form.setAutoFillBackground(False)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 6)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(9, 9, -1, -1)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_connection = QVBoxLayout()
        self.verticalLayout_connection.setObjectName(u"verticalLayout_connection")
        self.verticalLayout_connection.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.label_device = QLabel(self.frame)
        self.label_device.setObjectName(u"label_device")
        sizePolicy.setHeightForWidth(self.label_device.sizePolicy().hasHeightForWidth())
        self.label_device.setSizePolicy(sizePolicy)

        self.verticalLayout_connection.addWidget(self.label_device)

        self.comboBox_deviceList = QComboBox(self.frame)
        self.comboBox_deviceList.setObjectName(u"comboBox_deviceList")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_deviceList.sizePolicy().hasHeightForWidth())
        self.comboBox_deviceList.setSizePolicy(sizePolicy1)
        self.comboBox_deviceList.setMinimumSize(QSize(200, 0))

        self.verticalLayout_connection.addWidget(self.comboBox_deviceList)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.pushButton_connect = QPushButton(self.frame)
        self.pushButton_connect.setObjectName(u"pushButton_connect")
        sizePolicy.setHeightForWidth(self.pushButton_connect.sizePolicy().hasHeightForWidth())
        self.pushButton_connect.setSizePolicy(sizePolicy)
        self.pushButton_connect.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.horizontalLayout_3.addWidget(self.pushButton_connect)


        self.verticalLayout_connection.addLayout(self.horizontalLayout_3)


        self.horizontalLayout.addLayout(self.verticalLayout_connection)

        self.verticalLayout_settings = QVBoxLayout()
        self.verticalLayout_settings.setObjectName(u"verticalLayout_settings")
        self.verticalLayout_settings.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.label_integrationTime = QLabel(self.frame)
        self.label_integrationTime.setObjectName(u"label_integrationTime")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_integrationTime.sizePolicy().hasHeightForWidth())
        self.label_integrationTime.setSizePolicy(sizePolicy2)

        self.verticalLayout_settings.addWidget(self.label_integrationTime)

        self.spinBox_integrationTime = QSpinBox(self.frame)
        self.spinBox_integrationTime.setObjectName(u"spinBox_integrationTime")
        sizePolicy2.setHeightForWidth(self.spinBox_integrationTime.sizePolicy().hasHeightForWidth())
        self.spinBox_integrationTime.setSizePolicy(sizePolicy2)
        self.spinBox_integrationTime.setMinimumSize(QSize(0, 0))
        self.spinBox_integrationTime.setMaximum(100000)
        self.spinBox_integrationTime.setValue(100000)

        self.verticalLayout_settings.addWidget(self.spinBox_integrationTime)

        self.checkBox_correctDarkCounts = QCheckBox(self.frame)
        self.checkBox_correctDarkCounts.setObjectName(u"checkBox_correctDarkCounts")
        sizePolicy2.setHeightForWidth(self.checkBox_correctDarkCounts.sizePolicy().hasHeightForWidth())
        self.checkBox_correctDarkCounts.setSizePolicy(sizePolicy2)

        self.verticalLayout_settings.addWidget(self.checkBox_correctDarkCounts)

        self.checkBox_correctNonLinearity = QCheckBox(self.frame)
        self.checkBox_correctNonLinearity.setObjectName(u"checkBox_correctNonLinearity")
        sizePolicy2.setHeightForWidth(self.checkBox_correctNonLinearity.sizePolicy().hasHeightForWidth())
        self.checkBox_correctNonLinearity.setSizePolicy(sizePolicy2)

        self.verticalLayout_settings.addWidget(self.checkBox_correctNonLinearity)


        self.horizontalLayout.addLayout(self.verticalLayout_settings)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout_acquisition = QVBoxLayout()
        self.verticalLayout_acquisition.setObjectName(u"verticalLayout_acquisition")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton_acquire = QPushButton(self.frame)
        self.pushButton_acquire.setObjectName(u"pushButton_acquire")
        sizePolicy2.setHeightForWidth(self.pushButton_acquire.sizePolicy().hasHeightForWidth())
        self.pushButton_acquire.setSizePolicy(sizePolicy2)
        self.pushButton_acquire.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_acquire)


        self.verticalLayout_acquisition.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addLayout(self.verticalLayout_acquisition)

        self.widget_plot = QWidget(self.frame)
        self.widget_plot.setObjectName(u"widget_plot")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.widget_plot.sizePolicy().hasHeightForWidth())
        self.widget_plot.setSizePolicy(sizePolicy3)
        self.widget_plot.setMinimumSize(QSize(300, 100))

        self.verticalLayout.addWidget(self.widget_plot)


        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Spectrometer", None))
        self.label_device.setText(QCoreApplication.translate("Form", u"No_Spectrometer", None))
        self.pushButton_connect.setText(QCoreApplication.translate("Form", u"Connect", None))
        self.label_integrationTime.setText(QCoreApplication.translate("Form", u"Integration Time [us]", None))
        self.checkBox_correctDarkCounts.setText(QCoreApplication.translate("Form", u"Correct dark counts", None))
        self.checkBox_correctNonLinearity.setText(QCoreApplication.translate("Form", u"Correct non linearity", None))
        self.pushButton_acquire.setText(QCoreApplication.translate("Form", u"Single measurement", None))
    # retranslateUi

