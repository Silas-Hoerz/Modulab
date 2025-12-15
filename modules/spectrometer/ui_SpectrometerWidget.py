# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SpectrometerWidgetZZhfho.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(508, 398)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QSize(0, 0))
        Form.setAutoFillBackground(False)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 6)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setEnabled(True)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(9, 9, -1, -1)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout_4.addWidget(self.label)

        self.comboBox_deviceList = QComboBox(self.frame)
        self.comboBox_deviceList.setObjectName(u"comboBox_deviceList")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_deviceList.sizePolicy().hasHeightForWidth())
        self.comboBox_deviceList.setSizePolicy(sizePolicy1)
        self.comboBox_deviceList.setMinimumSize(QSize(150, 0))
        self.comboBox_deviceList.setMaximumSize(QSize(250, 16777215))

        self.horizontalLayout_4.addWidget(self.comboBox_deviceList)

        self.pushButton_connect = QPushButton(self.frame)
        self.pushButton_connect.setObjectName(u"pushButton_connect")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_connect.sizePolicy().hasHeightForWidth())
        self.pushButton_connect.setSizePolicy(sizePolicy2)
        self.pushButton_connect.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.pushButton_connect.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_connect.setCheckable(True)

        self.horizontalLayout_4.addWidget(self.pushButton_connect)

        self.horizontalSpacer = QSpacerItem(0, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.label_device = QLabel(self.frame)
        self.label_device.setObjectName(u"label_device")
        sizePolicy2.setHeightForWidth(self.label_device.sizePolicy().hasHeightForWidth())
        self.label_device.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.label_device)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.line_3 = QFrame(self.frame)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_connection = QVBoxLayout()
        self.verticalLayout_connection.setObjectName(u"verticalLayout_connection")
        self.verticalLayout_connection.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.label_integrationTime = QLabel(self.frame)
        self.label_integrationTime.setObjectName(u"label_integrationTime")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_integrationTime.sizePolicy().hasHeightForWidth())
        self.label_integrationTime.setSizePolicy(sizePolicy3)

        self.verticalLayout_connection.addWidget(self.label_integrationTime)

        self.spinBox_integrationTime = QSpinBox(self.frame)
        self.spinBox_integrationTime.setObjectName(u"spinBox_integrationTime")
        sizePolicy3.setHeightForWidth(self.spinBox_integrationTime.sizePolicy().hasHeightForWidth())
        self.spinBox_integrationTime.setSizePolicy(sizePolicy3)
        self.spinBox_integrationTime.setMinimumSize(QSize(0, 0))
        self.spinBox_integrationTime.setMaximumSize(QSize(250, 16777215))
        self.spinBox_integrationTime.setMaximum(100000)
        self.spinBox_integrationTime.setValue(100000)

        self.verticalLayout_connection.addWidget(self.spinBox_integrationTime)


        self.horizontalLayout.addLayout(self.verticalLayout_connection)

        self.line_2 = QFrame(self.frame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line_2)

        self.verticalLayout_settings = QVBoxLayout()
        self.verticalLayout_settings.setObjectName(u"verticalLayout_settings")
        self.verticalLayout_settings.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.checkBox_correctDarkCounts = QCheckBox(self.frame)
        self.checkBox_correctDarkCounts.setObjectName(u"checkBox_correctDarkCounts")
        self.checkBox_correctDarkCounts.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.checkBox_correctDarkCounts.sizePolicy().hasHeightForWidth())
        self.checkBox_correctDarkCounts.setSizePolicy(sizePolicy3)

        self.verticalLayout_settings.addWidget(self.checkBox_correctDarkCounts)

        self.checkBox_correctNonLinearity = QCheckBox(self.frame)
        self.checkBox_correctNonLinearity.setObjectName(u"checkBox_correctNonLinearity")
        sizePolicy3.setHeightForWidth(self.checkBox_correctNonLinearity.sizePolicy().hasHeightForWidth())
        self.checkBox_correctNonLinearity.setSizePolicy(sizePolicy3)

        self.verticalLayout_settings.addWidget(self.checkBox_correctNonLinearity)


        self.horizontalLayout.addLayout(self.verticalLayout_settings)

        self.line = QFrame(self.frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_actualTemp = QLabel(self.frame)
        self.label_actualTemp.setObjectName(u"label_actualTemp")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_actualTemp.sizePolicy().hasHeightForWidth())
        self.label_actualTemp.setSizePolicy(sizePolicy4)
        self.label_actualTemp.setMinimumSize(QSize(70, 0))
        self.label_actualTemp.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout_5.addWidget(self.label_actualTemp)

        self.doubleSpinBox_actualTemp = QDoubleSpinBox(self.frame)
        self.doubleSpinBox_actualTemp.setObjectName(u"doubleSpinBox_actualTemp")
        self.doubleSpinBox_actualTemp.setEnabled(True)
        sizePolicy3.setHeightForWidth(self.doubleSpinBox_actualTemp.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_actualTemp.setSizePolicy(sizePolicy3)
        self.doubleSpinBox_actualTemp.setMinimumSize(QSize(110, 24))
        self.doubleSpinBox_actualTemp.setMaximumSize(QSize(110, 16777215))
        self.doubleSpinBox_actualTemp.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.doubleSpinBox_actualTemp.setStyleSheet(u"QDoubleSpinBox[tempState=\"warning\"] {\n"
"                background-color: #ffff00; \n"
"                color: black; \n"
"}\n"
"QDoubleSpinBox[tempState=\"critical\"] {\n"
"                background-color: #ff2222; \n"
"                color: white; \n"
"}")
        self.doubleSpinBox_actualTemp.setReadOnly(True)
        self.doubleSpinBox_actualTemp.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBox_actualTemp.setDecimals(1)
        self.doubleSpinBox_actualTemp.setMinimum(-100.000000000000000)
        self.doubleSpinBox_actualTemp.setSingleStep(0.100000000000000)

        self.horizontalLayout_5.addWidget(self.doubleSpinBox_actualTemp)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        sizePolicy4.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy4)
        self.label_2.setMinimumSize(QSize(70, 0))
        self.label_2.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout_3.addWidget(self.label_2)

        self.doubleSpinBox = QDoubleSpinBox(self.frame)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        sizePolicy3.setHeightForWidth(self.doubleSpinBox.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox.setSizePolicy(sizePolicy3)
        self.doubleSpinBox.setMinimumSize(QSize(110, 0))
        self.doubleSpinBox.setMaximumSize(QSize(110, 16777215))
        self.doubleSpinBox.setDecimals(1)
        self.doubleSpinBox.setMinimum(-100.000000000000000)
        self.doubleSpinBox.setSingleStep(0.100000000000000)
        self.doubleSpinBox.setValue(-100.000000000000000)

        self.horizontalLayout_3.addWidget(self.doubleSpinBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.line_4 = QFrame(self.frame)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_4)

        self.verticalLayout_acquisition = QVBoxLayout()
        self.verticalLayout_acquisition.setObjectName(u"verticalLayout_acquisition")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.pushButton_acqurieDarkRead = QPushButton(self.frame)
        self.pushButton_acqurieDarkRead.setObjectName(u"pushButton_acqurieDarkRead")
        self.pushButton_acqurieDarkRead.setMinimumSize(QSize(0, 40))
        font = QFont()
        font.setPointSize(10)
        self.pushButton_acqurieDarkRead.setFont(font)

        self.horizontalLayout_2.addWidget(self.pushButton_acqurieDarkRead)

        self.spinBox_countDarkRead = QSpinBox(self.frame)
        self.spinBox_countDarkRead.setObjectName(u"spinBox_countDarkRead")
        self.spinBox_countDarkRead.setMinimum(1)
        self.spinBox_countDarkRead.setMaximum(100000)
        self.spinBox_countDarkRead.setValue(100)

        self.horizontalLayout_2.addWidget(self.spinBox_countDarkRead)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton_acquireSingle = QPushButton(self.frame)
        self.pushButton_acquireSingle.setObjectName(u"pushButton_acquireSingle")
        self.pushButton_acquireSingle.setMinimumSize(QSize(0, 40))
        self.pushButton_acquireSingle.setFont(font)

        self.horizontalLayout_2.addWidget(self.pushButton_acquireSingle)

        self.pushButton_acquireContinuous = QPushButton(self.frame)
        self.pushButton_acquireContinuous.setObjectName(u"pushButton_acquireContinuous")
        sizePolicy3.setHeightForWidth(self.pushButton_acquireContinuous.sizePolicy().hasHeightForWidth())
        self.pushButton_acquireContinuous.setSizePolicy(sizePolicy3)
        self.pushButton_acquireContinuous.setMinimumSize(QSize(0, 40))
        self.pushButton_acquireContinuous.setMaximumSize(QSize(16777215, 16777215))
        self.pushButton_acquireContinuous.setFont(font)
        self.pushButton_acquireContinuous.setStyleSheet(u"QPushButton:checked {color: black;}")
        self.pushButton_acquireContinuous.setCheckable(True)

        self.horizontalLayout_2.addWidget(self.pushButton_acquireContinuous)


        self.verticalLayout_acquisition.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addLayout(self.verticalLayout_acquisition)

        self.widget_plot = QWidget(self.frame)
        self.widget_plot.setObjectName(u"widget_plot")
        sizePolicy.setHeightForWidth(self.widget_plot.sizePolicy().hasHeightForWidth())
        self.widget_plot.setSizePolicy(sizePolicy)
        self.widget_plot.setMinimumSize(QSize(380, 200))

        self.verticalLayout.addWidget(self.widget_plot)


        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Spectrometer", None))
        self.label.setText(QCoreApplication.translate("Form", u"Device:", None))
        self.pushButton_connect.setText(QCoreApplication.translate("Form", u"Connect", None))
        self.label_device.setText(QCoreApplication.translate("Form", u"No connection", None))
        self.label_integrationTime.setText(QCoreApplication.translate("Form", u"Integration Time [us]:", None))
        self.checkBox_correctDarkCounts.setText(QCoreApplication.translate("Form", u"Correct dark counts", None))
        self.checkBox_correctNonLinearity.setText(QCoreApplication.translate("Form", u"Correct non linearity", None))
        self.label_actualTemp.setText(QCoreApplication.translate("Form", u"Actual Temp:", None))
        self.doubleSpinBox_actualTemp.setSuffix(QCoreApplication.translate("Form", u" \u00b0C", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Target Temp:", None))
        self.doubleSpinBox.setPrefix("")
        self.doubleSpinBox.setSuffix(QCoreApplication.translate("Form", u" \u00b0C", None))
        self.pushButton_acqurieDarkRead.setText(QCoreApplication.translate("Form", u"Read Dark", None))
        self.pushButton_acquireSingle.setText(QCoreApplication.translate("Form", u"Single", None))
        self.pushButton_acquireContinuous.setText(QCoreApplication.translate("Form", u"Start", None))
    # retranslateUi

