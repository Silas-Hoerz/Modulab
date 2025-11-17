# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SmuWidgeteXuXir.ui'
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
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTableView,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(393, 411)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
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

        self.pushButton_connect = QPushButton(self.frame)
        self.pushButton_connect.setObjectName(u"pushButton_connect")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_connect.sizePolicy().hasHeightForWidth())
        self.pushButton_connect.setSizePolicy(sizePolicy2)

        self.horizontalLayout_6.addWidget(self.pushButton_connect)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer)

        self.label_status = QLabel(self.frame)
        self.label_status.setObjectName(u"label_status")

        self.horizontalLayout_6.addWidget(self.label_status)


        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.line_5 = QFrame(self.frame)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line_5)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.line_3 = QFrame(self.frame)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_3)

        self.gridLayout_channelA = QGridLayout()
        self.gridLayout_channelA.setObjectName(u"gridLayout_channelA")
        self.pushButton_measureA = QPushButton(self.frame)
        self.pushButton_measureA.setObjectName(u"pushButton_measureA")

        self.gridLayout_channelA.addWidget(self.pushButton_measureA, 10, 1, 1, 1)

        self.lineEdit_levelA = QLineEdit(self.frame)
        self.lineEdit_levelA.setObjectName(u"lineEdit_levelA")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lineEdit_levelA.sizePolicy().hasHeightForWidth())
        self.lineEdit_levelA.setSizePolicy(sizePolicy3)
        self.lineEdit_levelA.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_channelA.addWidget(self.lineEdit_levelA, 3, 1, 1, 1)

        self.label_limitA = QLabel(self.frame)
        self.label_limitA.setObjectName(u"label_limitA")
        sizePolicy.setHeightForWidth(self.label_limitA.sizePolicy().hasHeightForWidth())
        self.label_limitA.setSizePolicy(sizePolicy)

        self.gridLayout_channelA.addWidget(self.label_limitA, 5, 0, 1, 1)

        self.lineEdit_limitA = QLineEdit(self.frame)
        self.lineEdit_limitA.setObjectName(u"lineEdit_limitA")

        self.gridLayout_channelA.addWidget(self.lineEdit_limitA, 5, 1, 1, 1)

        self.pushButton_currentA = QPushButton(self.frame)
        self.pushButton_currentA.setObjectName(u"pushButton_currentA")
        self.pushButton_currentA.setCheckable(True)

        self.gridLayout_channelA.addWidget(self.pushButton_currentA, 2, 1, 1, 1)

        self.label_levelA = QLabel(self.frame)
        self.label_levelA.setObjectName(u"label_levelA")
        sizePolicy.setHeightForWidth(self.label_levelA.sizePolicy().hasHeightForWidth())
        self.label_levelA.setSizePolicy(sizePolicy)

        self.gridLayout_channelA.addWidget(self.label_levelA, 3, 0, 1, 1)

        self.pushButton_outputA = QPushButton(self.frame)
        self.pushButton_outputA.setObjectName(u"pushButton_outputA")
        self.pushButton_outputA.setCheckable(True)

        self.gridLayout_channelA.addWidget(self.pushButton_outputA, 8, 1, 1, 1)

        self.label_voltageA = QLabel(self.frame)
        self.label_voltageA.setObjectName(u"label_voltageA")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_voltageA.sizePolicy().hasHeightForWidth())
        self.label_voltageA.setSizePolicy(sizePolicy4)
        self.label_voltageA.setAutoFillBackground(False)
        self.label_voltageA.setStyleSheet(u"QLabel {\n"
"    color: palette(dark);             /* Akzentfarbe */\n"
"    background-color: palette(accent);     /* Standard Hintergrund */\n"
"    border: 0px solid palette(light);       /* Standard dunkler Rahmen */\n"
"    border-radius: 5px;\n"
"    padding: 5px;\n"
"    font-family: monospace;\n"
"    font-size: 14px;\n"
"}\n"
"")
        self.label_voltageA.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_channelA.addWidget(self.label_voltageA, 11, 0, 1, 1)

        self.pushButton_remoteA = QPushButton(self.frame)
        self.pushButton_remoteA.setObjectName(u"pushButton_remoteA")
        self.pushButton_remoteA.setCheckable(True)

        self.gridLayout_channelA.addWidget(self.pushButton_remoteA, 7, 1, 1, 1)

        self.pushButton_voltageA = QPushButton(self.frame)
        self.pushButton_voltageA.setObjectName(u"pushButton_voltageA")
        self.pushButton_voltageA.setCheckable(True)
        self.pushButton_voltageA.setChecked(True)

        self.gridLayout_channelA.addWidget(self.pushButton_voltageA, 2, 0, 1, 1)

        self.label_currentA = QLabel(self.frame)
        self.label_currentA.setObjectName(u"label_currentA")
        sizePolicy4.setHeightForWidth(self.label_currentA.sizePolicy().hasHeightForWidth())
        self.label_currentA.setSizePolicy(sizePolicy4)
        self.label_currentA.setStyleSheet(u"QLabel {\n"
"    color: palette(dark);             /* Akzentfarbe */\n"
"    background-color: palette(accent);     /* Standard Hintergrund */\n"
"    border: 0px solid palette(light);       /* Standard dunkler Rahmen */\n"
"    border-radius: 5px;\n"
"    padding: 5px;\n"
"    font-family: monospace;\n"
"    font-size: 14px;\n"
"}\n"
"")
        self.label_currentA.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_channelA.addWidget(self.label_currentA, 11, 1, 1, 1)

        self.line_2 = QFrame(self.frame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setMinimumSize(QSize(0, 20))
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_channelA.addWidget(self.line_2, 9, 0, 1, 2)

        self.pushButton_localA = QPushButton(self.frame)
        self.pushButton_localA.setObjectName(u"pushButton_localA")
        self.pushButton_localA.setCheckable(True)
        self.pushButton_localA.setChecked(True)

        self.gridLayout_channelA.addWidget(self.pushButton_localA, 7, 0, 1, 1)

        self.label_6 = QLabel(self.frame)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)

        self.gridLayout_channelA.addWidget(self.label_6, 1, 0, 1, 1)

        self.pushButton_resetA = QPushButton(self.frame)
        self.pushButton_resetA.setObjectName(u"pushButton_resetA")

        self.gridLayout_channelA.addWidget(self.pushButton_resetA, 8, 0, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_channelA)

        self.tableView_measurementsA = QTableView(self.frame)
        self.tableView_measurementsA.setObjectName(u"tableView_measurementsA")
        self.tableView_measurementsA.setAutoFillBackground(False)

        self.verticalLayout_2.addWidget(self.tableView_measurementsA)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.line_6 = QFrame(self.frame)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.Shape.VLine)
        self.line_6.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line_6)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_channel = QLabel(self.frame)
        self.label_channel.setObjectName(u"label_channel")
        sizePolicy.setHeightForWidth(self.label_channel.sizePolicy().hasHeightForWidth())
        self.label_channel.setSizePolicy(sizePolicy)

        self.verticalLayout_4.addWidget(self.label_channel)

        self.line_4 = QFrame(self.frame)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_4.addWidget(self.line_4)

        self.gridLayout_channelB = QGridLayout()
        self.gridLayout_channelB.setObjectName(u"gridLayout_channelB")
        self.label_currentB = QLabel(self.frame)
        self.label_currentB.setObjectName(u"label_currentB")
        sizePolicy4.setHeightForWidth(self.label_currentB.sizePolicy().hasHeightForWidth())
        self.label_currentB.setSizePolicy(sizePolicy4)
        self.label_currentB.setStyleSheet(u"QLabel {\n"
"    color: palette(dark);             /* Akzentfarbe */\n"
"    background-color: palette(accent);     /* Standard Hintergrund */\n"
"    border: 0px solid palette(light);       /* Standard dunkler Rahmen */\n"
"    border-radius: 5px;\n"
"    padding: 5px;\n"
"    font-family: monospace;\n"
"    font-size: 14px;\n"
"}\n"
"")
        self.label_currentB.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_channelB.addWidget(self.label_currentB, 10, 1, 1, 1)

        self.pushButton_measureB = QPushButton(self.frame)
        self.pushButton_measureB.setObjectName(u"pushButton_measureB")

        self.gridLayout_channelB.addWidget(self.pushButton_measureB, 9, 1, 1, 1)

        self.pushButton_remoteB = QPushButton(self.frame)
        self.pushButton_remoteB.setObjectName(u"pushButton_remoteB")
        self.pushButton_remoteB.setCheckable(True)

        self.gridLayout_channelB.addWidget(self.pushButton_remoteB, 6, 1, 1, 1)

        self.line = QFrame(self.frame)
        self.line.setObjectName(u"line")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy5)
        self.line.setMinimumSize(QSize(0, 20))
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_channelB.addWidget(self.line, 8, 0, 1, 2)

        self.pushButton_currentB = QPushButton(self.frame)
        self.pushButton_currentB.setObjectName(u"pushButton_currentB")
        self.pushButton_currentB.setCheckable(True)

        self.gridLayout_channelB.addWidget(self.pushButton_currentB, 1, 1, 1, 1)

        self.label_limitB = QLabel(self.frame)
        self.label_limitB.setObjectName(u"label_limitB")

        self.gridLayout_channelB.addWidget(self.label_limitB, 4, 0, 1, 1)

        self.label_voltageB = QLabel(self.frame)
        self.label_voltageB.setObjectName(u"label_voltageB")
        sizePolicy4.setHeightForWidth(self.label_voltageB.sizePolicy().hasHeightForWidth())
        self.label_voltageB.setSizePolicy(sizePolicy4)
        self.label_voltageB.setStyleSheet(u"QLabel {\n"
"    color: palette(dark);             /* Akzentfarbe */\n"
"    background-color: palette(accent);     /* Standard Hintergrund */\n"
"    border: 0px solid palette(light);       /* Standard dunkler Rahmen */\n"
"    border-radius: 5px;\n"
"    padding: 5px;\n"
"    font-family: monospace;\n"
"    font-size: 14px;\n"
"}\n"
"")
        self.label_voltageB.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_channelB.addWidget(self.label_voltageB, 10, 0, 1, 1)

        self.label_levelB = QLabel(self.frame)
        self.label_levelB.setObjectName(u"label_levelB")

        self.gridLayout_channelB.addWidget(self.label_levelB, 2, 0, 1, 1)

        self.pushButton_voltageB = QPushButton(self.frame)
        self.pushButton_voltageB.setObjectName(u"pushButton_voltageB")
        self.pushButton_voltageB.setCheckable(True)
        self.pushButton_voltageB.setChecked(True)

        self.gridLayout_channelB.addWidget(self.pushButton_voltageB, 1, 0, 1, 1)

        self.pushButton_localB = QPushButton(self.frame)
        self.pushButton_localB.setObjectName(u"pushButton_localB")
        self.pushButton_localB.setCheckable(True)
        self.pushButton_localB.setChecked(True)

        self.gridLayout_channelB.addWidget(self.pushButton_localB, 6, 0, 1, 1)

        self.pushButton_resetB = QPushButton(self.frame)
        self.pushButton_resetB.setObjectName(u"pushButton_resetB")

        self.gridLayout_channelB.addWidget(self.pushButton_resetB, 7, 0, 1, 1)

        self.pushButton_outputB = QPushButton(self.frame)
        self.pushButton_outputB.setObjectName(u"pushButton_outputB")
        self.pushButton_outputB.setCheckable(True)

        self.gridLayout_channelB.addWidget(self.pushButton_outputB, 7, 1, 1, 1)

        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_channelB.addWidget(self.label_3, 0, 0, 1, 1)

        self.lineEdit_levelB = QLineEdit(self.frame)
        self.lineEdit_levelB.setObjectName(u"lineEdit_levelB")

        self.gridLayout_channelB.addWidget(self.lineEdit_levelB, 2, 1, 1, 1)

        self.lineEdit_limitB = QLineEdit(self.frame)
        self.lineEdit_limitB.setObjectName(u"lineEdit_limitB")

        self.gridLayout_channelB.addWidget(self.lineEdit_limitB, 4, 1, 1, 1)


        self.verticalLayout_4.addLayout(self.gridLayout_channelB)

        self.tableView_measurementsB = QTableView(self.frame)
        self.tableView_measurementsB.setObjectName(u"tableView_measurementsB")

        self.verticalLayout_4.addWidget(self.tableView_measurementsB)


        self.horizontalLayout.addLayout(self.verticalLayout_4)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.frame)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"Port:", None))
        self.pushButton_connect.setText(QCoreApplication.translate("Form", u"Connect", None))
        self.label_status.setText(QCoreApplication.translate("Form", u"No connection", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Channel A", None))
        self.pushButton_measureA.setText(QCoreApplication.translate("Form", u"Measure", None))
        self.label_limitA.setText(QCoreApplication.translate("Form", u"Limit [A]", None))
        self.pushButton_currentA.setText(QCoreApplication.translate("Form", u"Current", None))
#if QT_CONFIG(tooltip)
        self.label_levelA.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_levelA.setText(QCoreApplication.translate("Form", u"Level [V]", None))
        self.pushButton_outputA.setText(QCoreApplication.translate("Form", u"OFF", None))
        self.label_voltageA.setText(QCoreApplication.translate("Form", u"--- V", None))
        self.pushButton_remoteA.setText(QCoreApplication.translate("Form", u"Remote 4 Wire", None))
        self.pushButton_voltageA.setText(QCoreApplication.translate("Form", u"Voltage", None))
        self.label_currentA.setText(QCoreApplication.translate("Form", u"--- A", None))
        self.pushButton_localA.setText(QCoreApplication.translate("Form", u"Local 2 Wire", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"Source:", None))
        self.pushButton_resetA.setText(QCoreApplication.translate("Form", u"Reset", None))
        self.label_channel.setText(QCoreApplication.translate("Form", u"Channel B", None))
        self.label_currentB.setText(QCoreApplication.translate("Form", u"--- A", None))
        self.pushButton_measureB.setText(QCoreApplication.translate("Form", u"Measure", None))
        self.pushButton_remoteB.setText(QCoreApplication.translate("Form", u"Remote 4 Wire", None))
        self.pushButton_currentB.setText(QCoreApplication.translate("Form", u"Current", None))
        self.label_limitB.setText(QCoreApplication.translate("Form", u"Limit [A]", None))
        self.label_voltageB.setText(QCoreApplication.translate("Form", u"--- V", None))
        self.label_levelB.setText(QCoreApplication.translate("Form", u"Level [V]", None))
        self.pushButton_voltageB.setText(QCoreApplication.translate("Form", u"Voltage", None))
        self.pushButton_localB.setText(QCoreApplication.translate("Form", u"Local 2 Wire", None))
        self.pushButton_resetB.setText(QCoreApplication.translate("Form", u"Reset", None))
        self.pushButton_outputB.setText(QCoreApplication.translate("Form", u"OFF", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Source", None))
    # retranslateUi

