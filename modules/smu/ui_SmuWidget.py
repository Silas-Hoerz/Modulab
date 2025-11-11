# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SmuWidgetcdQyDD.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLayout,
    QLineEdit, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QTableView, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(231, 570)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.horizontalLayout_6.addWidget(self.label)

        self.comboBox_port = QComboBox(self.frame)
        self.comboBox_port.setObjectName(u"comboBox_port")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_port.sizePolicy().hasHeightForWidth())
        self.comboBox_port.setSizePolicy(sizePolicy1)
        self.comboBox_port.setMaximumSize(QSize(250, 16777215))

        self.horizontalLayout_6.addWidget(self.comboBox_port)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.label_status = QLabel(self.frame)
        self.label_status.setObjectName(u"label_status")

        self.horizontalLayout.addWidget(self.label_status)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_connect = QPushButton(self.frame)
        self.pushButton_connect.setObjectName(u"pushButton_connect")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_connect.sizePolicy().hasHeightForWidth())
        self.pushButton_connect.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.pushButton_connect)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.line = QFrame(self.frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.lineEdit_level = QLineEdit(self.frame)
        self.lineEdit_level.setObjectName(u"lineEdit_level")
        sizePolicy1.setHeightForWidth(self.lineEdit_level.sizePolicy().hasHeightForWidth())
        self.lineEdit_level.setSizePolicy(sizePolicy1)
        self.lineEdit_level.setMaximumSize(QSize(250, 16777215))

        self.gridLayout.addWidget(self.lineEdit_level, 5, 0, 1, 2)

        self.lineEdit_limit = QLineEdit(self.frame)
        self.lineEdit_limit.setObjectName(u"lineEdit_limit")
        sizePolicy1.setHeightForWidth(self.lineEdit_limit.sizePolicy().hasHeightForWidth())
        self.lineEdit_limit.setSizePolicy(sizePolicy1)
        self.lineEdit_limit.setMaximumSize(QSize(250, 16777215))

        self.gridLayout.addWidget(self.lineEdit_limit, 7, 0, 1, 2)

        self.label_source = QLabel(self.frame)
        self.label_source.setObjectName(u"label_source")
        sizePolicy.setHeightForWidth(self.label_source.sizePolicy().hasHeightForWidth())
        self.label_source.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_source, 2, 0, 1, 1)

        self.radioButton_voltage = QRadioButton(self.frame)
        self.radioButton_voltage.setObjectName(u"radioButton_voltage")
        sizePolicy.setHeightForWidth(self.radioButton_voltage.sizePolicy().hasHeightForWidth())
        self.radioButton_voltage.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.radioButton_voltage, 3, 0, 1, 1)

        self.radioButton_channelA = QRadioButton(self.frame)
        self.radioButton_channelA.setObjectName(u"radioButton_channelA")
        sizePolicy.setHeightForWidth(self.radioButton_channelA.sizePolicy().hasHeightForWidth())
        self.radioButton_channelA.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.radioButton_channelA, 1, 0, 1, 1)

        self.radioButton_local = QRadioButton(self.frame)
        self.radioButton_local.setObjectName(u"radioButton_local")

        self.gridLayout.addWidget(self.radioButton_local, 8, 0, 1, 1)

        self.radioButton_remote = QRadioButton(self.frame)
        self.radioButton_remote.setObjectName(u"radioButton_remote")

        self.gridLayout.addWidget(self.radioButton_remote, 8, 1, 1, 1)

        self.label_level = QLabel(self.frame)
        self.label_level.setObjectName(u"label_level")
        sizePolicy.setHeightForWidth(self.label_level.sizePolicy().hasHeightForWidth())
        self.label_level.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_level, 4, 0, 1, 1)

        self.radioButton_current = QRadioButton(self.frame)
        self.radioButton_current.setObjectName(u"radioButton_current")
        sizePolicy.setHeightForWidth(self.radioButton_current.sizePolicy().hasHeightForWidth())
        self.radioButton_current.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.radioButton_current, 3, 1, 1, 1)

        self.label_channel = QLabel(self.frame)
        self.label_channel.setObjectName(u"label_channel")
        sizePolicy.setHeightForWidth(self.label_channel.sizePolicy().hasHeightForWidth())
        self.label_channel.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_channel, 0, 0, 1, 1)

        self.radioButton_channelB = QRadioButton(self.frame)
        self.radioButton_channelB.setObjectName(u"radioButton_channelB")
        sizePolicy.setHeightForWidth(self.radioButton_channelB.sizePolicy().hasHeightForWidth())
        self.radioButton_channelB.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.radioButton_channelB, 1, 1, 1, 1)

        self.label_limit = QLabel(self.frame)
        self.label_limit.setObjectName(u"label_limit")
        sizePolicy.setHeightForWidth(self.label_limit.sizePolicy().hasHeightForWidth())
        self.label_limit.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_limit, 6, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.pushButton_reset = QPushButton(self.frame)
        self.pushButton_reset.setObjectName(u"pushButton_reset")

        self.horizontalLayout_4.addWidget(self.pushButton_reset)

        self.pushButton_output = QPushButton(self.frame)
        self.pushButton_output.setObjectName(u"pushButton_output")
        self.pushButton_output.setCheckable(True)

        self.horizontalLayout_4.addWidget(self.pushButton_output)


        self.gridLayout.addLayout(self.horizontalLayout_4, 9, 0, 1, 2)


        self.verticalLayout_2.addLayout(self.gridLayout)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.line_2 = QFrame(self.frame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line_2)

        self.pushButton_measure = QPushButton(self.frame)
        self.pushButton_measure.setObjectName(u"pushButton_measure")

        self.verticalLayout_3.addWidget(self.pushButton_measure)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_voltage = QLabel(self.frame)
        self.label_voltage.setObjectName(u"label_voltage")

        self.horizontalLayout_5.addWidget(self.label_voltage)

        self.label_current = QLabel(self.frame)
        self.label_current.setObjectName(u"label_current")

        self.horizontalLayout_5.addWidget(self.label_current)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.tableView_measurements = QTableView(self.frame)
        self.tableView_measurements.setObjectName(u"tableView_measurements")
        self.tableView_measurements.setAutoFillBackground(False)

        self.verticalLayout_3.addWidget(self.tableView_measurements)


        self.verticalLayout.addWidget(self.frame)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"Port:", None))
        self.label_status.setText(QCoreApplication.translate("Form", u"not connected", None))
        self.pushButton_connect.setText(QCoreApplication.translate("Form", u"Connect", None))
        self.label_source.setText(QCoreApplication.translate("Form", u"Source:", None))
        self.radioButton_voltage.setText(QCoreApplication.translate("Form", u"Voltage", None))
        self.radioButton_channelA.setText(QCoreApplication.translate("Form", u"A", None))
        self.radioButton_local.setText(QCoreApplication.translate("Form", u"Local 2 Wire", None))
        self.radioButton_remote.setText(QCoreApplication.translate("Form", u"Remote 4 Wire", None))
#if QT_CONFIG(tooltip)
        self.label_level.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_level.setText(QCoreApplication.translate("Form", u"Level:", None))
        self.radioButton_current.setText(QCoreApplication.translate("Form", u"Current", None))
        self.label_channel.setText(QCoreApplication.translate("Form", u"Channel:", None))
        self.radioButton_channelB.setText(QCoreApplication.translate("Form", u"B", None))
        self.label_limit.setText(QCoreApplication.translate("Form", u"Limit:", None))
        self.pushButton_reset.setText(QCoreApplication.translate("Form", u"Reset", None))
        self.pushButton_output.setText(QCoreApplication.translate("Form", u"Output", None))
        self.pushButton_measure.setText(QCoreApplication.translate("Form", u"Measure", None))
        self.label_voltage.setText(QCoreApplication.translate("Form", u"--- V", None))
        self.label_current.setText(QCoreApplication.translate("Form", u"--- A", None))
    # retranslateUi

