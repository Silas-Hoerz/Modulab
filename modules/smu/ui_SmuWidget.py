# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SmuWidgetaPDbdE.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLayout,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTableView, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(523, 530)
        Form.setStyleSheet(u"QPushButton[tempState=\"warning\"] {\n"
"                background-color: #ffff00; \n"
"                color: black; \n"
"}\n"
"QLineEdit[tempState=\"warning\"] {\n"
"                background-color: #ffff00; \n"
"                color: black; \n"
"}\n"
"QLabel[tempState=\"on\"] {\n"
"                color: #00FF00; /* Gr\u00fcn leuchtend f\u00fcr bessere Lesbarkeit */\n"
"                background-color: black;\n"
"                /*border: 1px solid #00FF00;*/\n"
"                border-radius: 5px;\n"
"                padding: 5px;\n"
"            }\n"
"            QLabel[tempState=\"off\"] {\n"
"                color: white;\n"
"                background-color:black; /* Dunkelgrau statt hartem Schwarz */\n"
"                /*border: 1px solid gray;*/\n"
"                border-radius: 5px;\n"
"                padding: 5px;\n"
"            }\n"
"")
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"")
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
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_port.sizePolicy().hasHeightForWidth())
        self.comboBox_port.setSizePolicy(sizePolicy1)
        self.comboBox_port.setMinimumSize(QSize(150, 0))
        self.comboBox_port.setMaximumSize(QSize(250, 16777215))

        self.horizontalLayout_6.addWidget(self.comboBox_port)

        self.pushButton_connect = QPushButton(self.frame)
        self.pushButton_connect.setObjectName(u"pushButton_connect")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_connect.sizePolicy().hasHeightForWidth())
        self.pushButton_connect.setSizePolicy(sizePolicy2)
        self.pushButton_connect.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_connect.setCheckable(True)
        self.pushButton_connect.setChecked(False)

        self.horizontalLayout_6.addWidget(self.pushButton_connect)

        self.horizontalSpacer = QSpacerItem(0, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

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
        font = QFont()
        font.setPointSize(10)
        font.setBold(False)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_2)

        self.line_3 = QFrame(self.frame)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_3)

        self.gridLayout_channelA = QGridLayout()
        self.gridLayout_channelA.setObjectName(u"gridLayout_channelA")
        self.label_6 = QLabel(self.frame)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)

        self.gridLayout_channelA.addWidget(self.label_6, 1, 0, 1, 1)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.pushButton_resetA = QPushButton(self.frame)
        self.pushButton_resetA.setObjectName(u"pushButton_resetA")
        self.pushButton_resetA.setStyleSheet(u"QPushButton:checked {color:black;}")

        self.horizontalLayout_10.addWidget(self.pushButton_resetA)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_2)

        self.pushButton_applyA = QPushButton(self.frame)
        self.pushButton_applyA.setObjectName(u"pushButton_applyA")

        self.horizontalLayout_10.addWidget(self.pushButton_applyA)


        self.gridLayout_channelA.addLayout(self.horizontalLayout_10, 9, 0, 1, 2)

        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy3)

        self.gridLayout_channelA.addWidget(self.label_4, 6, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.pushButton_voltageA = QPushButton(self.frame)
        self.pushButton_voltageA.setObjectName(u"pushButton_voltageA")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.pushButton_voltageA.sizePolicy().hasHeightForWidth())
        self.pushButton_voltageA.setSizePolicy(sizePolicy4)
        self.pushButton_voltageA.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_voltageA.setCheckable(True)
        self.pushButton_voltageA.setChecked(True)

        self.horizontalLayout_5.addWidget(self.pushButton_voltageA)

        self.pushButton_currentA = QPushButton(self.frame)
        self.pushButton_currentA.setObjectName(u"pushButton_currentA")
        sizePolicy4.setHeightForWidth(self.pushButton_currentA.sizePolicy().hasHeightForWidth())
        self.pushButton_currentA.setSizePolicy(sizePolicy4)
        self.pushButton_currentA.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_currentA.setCheckable(True)

        self.horizontalLayout_5.addWidget(self.pushButton_currentA)


        self.gridLayout_channelA.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)

        self.lineEdit_levelA = QLineEdit(self.frame)
        self.lineEdit_levelA.setObjectName(u"lineEdit_levelA")
        sizePolicy4.setHeightForWidth(self.lineEdit_levelA.sizePolicy().hasHeightForWidth())
        self.lineEdit_levelA.setSizePolicy(sizePolicy4)
        self.lineEdit_levelA.setMinimumSize(QSize(0, 26))
        self.lineEdit_levelA.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_channelA.addWidget(self.lineEdit_levelA, 3, 1, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.pushButton_localA = QPushButton(self.frame)
        self.pushButton_localA.setObjectName(u"pushButton_localA")
        self.pushButton_localA.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_localA.setCheckable(True)
        self.pushButton_localA.setChecked(True)

        self.horizontalLayout_8.addWidget(self.pushButton_localA)

        self.pushButton_remoteA = QPushButton(self.frame)
        self.pushButton_remoteA.setObjectName(u"pushButton_remoteA")
        self.pushButton_remoteA.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_remoteA.setCheckable(True)

        self.horizontalLayout_8.addWidget(self.pushButton_remoteA)


        self.gridLayout_channelA.addLayout(self.horizontalLayout_8, 6, 1, 1, 1)

        self.lineEdit_limitA = QLineEdit(self.frame)
        self.lineEdit_limitA.setObjectName(u"lineEdit_limitA")
        self.lineEdit_limitA.setMinimumSize(QSize(0, 26))

        self.gridLayout_channelA.addWidget(self.lineEdit_limitA, 5, 1, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_voltageA = QLabel(self.frame)
        self.label_voltageA.setObjectName(u"label_voltageA")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.label_voltageA.sizePolicy().hasHeightForWidth())
        self.label_voltageA.setSizePolicy(sizePolicy5)
        self.label_voltageA.setMinimumSize(QSize(0, 36))
        self.label_voltageA.setMaximumSize(QSize(16777215, 36))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        self.label_voltageA.setFont(font1)
        self.label_voltageA.setAutoFillBackground(False)
        self.label_voltageA.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_13.addWidget(self.label_voltageA)

        self.label_currentA = QLabel(self.frame)
        self.label_currentA.setObjectName(u"label_currentA")
        sizePolicy5.setHeightForWidth(self.label_currentA.sizePolicy().hasHeightForWidth())
        self.label_currentA.setSizePolicy(sizePolicy5)
        self.label_currentA.setMinimumSize(QSize(0, 36))
        self.label_currentA.setMaximumSize(QSize(16777215, 36))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(12)
        font2.setBold(True)
        self.label_currentA.setFont(font2)
        self.label_currentA.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_13.addWidget(self.label_currentA)


        self.verticalLayout_6.addLayout(self.horizontalLayout_13)

        self.label_statsA = QLabel(self.frame)
        self.label_statsA.setObjectName(u"label_statsA")
        self.label_statsA.setMouseTracking(False)
        self.label_statsA.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_statsA)


        self.horizontalLayout_3.addLayout(self.verticalLayout_6)

        self.pushButton_outputA = QPushButton(self.frame)
        self.pushButton_outputA.setObjectName(u"pushButton_outputA")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.pushButton_outputA.sizePolicy().hasHeightForWidth())
        self.pushButton_outputA.setSizePolicy(sizePolicy6)
        self.pushButton_outputA.setMinimumSize(QSize(40, 40))
        self.pushButton_outputA.setMaximumSize(QSize(40, 40))
        self.pushButton_outputA.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_outputA.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.pushButton_outputA)


        self.gridLayout_channelA.addLayout(self.horizontalLayout_3, 12, 0, 1, 2)

        self.label_limitA = QLabel(self.frame)
        self.label_limitA.setObjectName(u"label_limitA")
        sizePolicy3.setHeightForWidth(self.label_limitA.sizePolicy().hasHeightForWidth())
        self.label_limitA.setSizePolicy(sizePolicy3)
        self.label_limitA.setMinimumSize(QSize(50, 0))

        self.gridLayout_channelA.addWidget(self.label_limitA, 5, 0, 1, 1)

        self.label_levelA = QLabel(self.frame)
        self.label_levelA.setObjectName(u"label_levelA")
        sizePolicy.setHeightForWidth(self.label_levelA.sizePolicy().hasHeightForWidth())
        self.label_levelA.setSizePolicy(sizePolicy)

        self.gridLayout_channelA.addWidget(self.label_levelA, 3, 0, 1, 1)

        self.line_7 = QFrame(self.frame)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShape(QFrame.Shape.HLine)
        self.line_7.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_channelA.addWidget(self.line_7, 8, 0, 1, 2)

        self.line_2 = QFrame(self.frame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setMinimumSize(QSize(0, 0))
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_channelA.addWidget(self.line_2, 11, 0, 1, 2)


        self.verticalLayout_2.addLayout(self.gridLayout_channelA)

        self.pushButton_singleA = QPushButton(self.frame)
        self.pushButton_singleA.setObjectName(u"pushButton_singleA")
        sizePolicy2.setHeightForWidth(self.pushButton_singleA.sizePolicy().hasHeightForWidth())
        self.pushButton_singleA.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.pushButton_singleA)

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
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.label_channel.sizePolicy().hasHeightForWidth())
        self.label_channel.setSizePolicy(sizePolicy7)
        font3 = QFont()
        font3.setPointSize(10)
        self.label_channel.setFont(font3)
        self.label_channel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_channel)

        self.line_4 = QFrame(self.frame)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_4.addWidget(self.line_4)

        self.gridLayout_channelB = QGridLayout()
        self.gridLayout_channelB.setObjectName(u"gridLayout_channelB")
        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")
        sizePolicy3.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy3)

        self.gridLayout_channelB.addWidget(self.label_3, 0, 0, 1, 1)

        self.lineEdit_levelB = QLineEdit(self.frame)
        self.lineEdit_levelB.setObjectName(u"lineEdit_levelB")
        self.lineEdit_levelB.setMinimumSize(QSize(0, 26))

        self.gridLayout_channelB.addWidget(self.lineEdit_levelB, 2, 1, 1, 1)

        self.label_limitB = QLabel(self.frame)
        self.label_limitB.setObjectName(u"label_limitB")
        sizePolicy3.setHeightForWidth(self.label_limitB.sizePolicy().hasHeightForWidth())
        self.label_limitB.setSizePolicy(sizePolicy3)
        self.label_limitB.setMinimumSize(QSize(50, 0))

        self.gridLayout_channelB.addWidget(self.label_limitB, 4, 0, 1, 1)

        self.lineEdit_limitB = QLineEdit(self.frame)
        self.lineEdit_limitB.setObjectName(u"lineEdit_limitB")
        self.lineEdit_limitB.setMinimumSize(QSize(0, 26))

        self.gridLayout_channelB.addWidget(self.lineEdit_limitB, 4, 1, 1, 1)

        self.label_levelB = QLabel(self.frame)
        self.label_levelB.setObjectName(u"label_levelB")
        sizePolicy3.setHeightForWidth(self.label_levelB.sizePolicy().hasHeightForWidth())
        self.label_levelB.setSizePolicy(sizePolicy3)

        self.gridLayout_channelB.addWidget(self.label_levelB, 2, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.pushButton_voltageB = QPushButton(self.frame)
        self.pushButton_voltageB.setObjectName(u"pushButton_voltageB")
        sizePolicy4.setHeightForWidth(self.pushButton_voltageB.sizePolicy().hasHeightForWidth())
        self.pushButton_voltageB.setSizePolicy(sizePolicy4)
        self.pushButton_voltageB.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_voltageB.setCheckable(True)
        self.pushButton_voltageB.setChecked(True)

        self.horizontalLayout_7.addWidget(self.pushButton_voltageB)

        self.pushButton_currentB = QPushButton(self.frame)
        self.pushButton_currentB.setObjectName(u"pushButton_currentB")
        sizePolicy4.setHeightForWidth(self.pushButton_currentB.sizePolicy().hasHeightForWidth())
        self.pushButton_currentB.setSizePolicy(sizePolicy4)
        self.pushButton_currentB.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_currentB.setCheckable(True)

        self.horizontalLayout_7.addWidget(self.pushButton_currentB)


        self.gridLayout_channelB.addLayout(self.horizontalLayout_7, 0, 1, 1, 1)

        self.label_5 = QLabel(self.frame)
        self.label_5.setObjectName(u"label_5")
        sizePolicy3.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy3)

        self.gridLayout_channelB.addWidget(self.label_5, 5, 0, 1, 1)

        self.line = QFrame(self.frame)
        self.line.setObjectName(u"line")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy8)
        self.line.setMinimumSize(QSize(0, 0))
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_channelB.addWidget(self.line, 10, 0, 1, 2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_voltageB = QLabel(self.frame)
        self.label_voltageB.setObjectName(u"label_voltageB")
        sizePolicy5.setHeightForWidth(self.label_voltageB.sizePolicy().hasHeightForWidth())
        self.label_voltageB.setSizePolicy(sizePolicy5)
        self.label_voltageB.setMinimumSize(QSize(0, 36))
        self.label_voltageB.setMaximumSize(QSize(16777215, 36))
        self.label_voltageB.setFont(font2)
        self.label_voltageB.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_14.addWidget(self.label_voltageB)

        self.label_currentB = QLabel(self.frame)
        self.label_currentB.setObjectName(u"label_currentB")
        sizePolicy5.setHeightForWidth(self.label_currentB.sizePolicy().hasHeightForWidth())
        self.label_currentB.setSizePolicy(sizePolicy5)
        self.label_currentB.setMinimumSize(QSize(0, 36))
        self.label_currentB.setMaximumSize(QSize(16777215, 36))
        self.label_currentB.setFont(font1)
        self.label_currentB.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_14.addWidget(self.label_currentB)


        self.verticalLayout_7.addLayout(self.horizontalLayout_14)

        self.label_statsB = QLabel(self.frame)
        self.label_statsB.setObjectName(u"label_statsB")
        self.label_statsB.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_7.addWidget(self.label_statsB)


        self.horizontalLayout_4.addLayout(self.verticalLayout_7)

        self.pushButton_outputB = QPushButton(self.frame)
        self.pushButton_outputB.setObjectName(u"pushButton_outputB")
        sizePolicy6.setHeightForWidth(self.pushButton_outputB.sizePolicy().hasHeightForWidth())
        self.pushButton_outputB.setSizePolicy(sizePolicy6)
        self.pushButton_outputB.setMinimumSize(QSize(40, 40))
        self.pushButton_outputB.setMaximumSize(QSize(40, 40))
        self.pushButton_outputB.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_outputB.setCheckable(True)

        self.horizontalLayout_4.addWidget(self.pushButton_outputB)


        self.gridLayout_channelB.addLayout(self.horizontalLayout_4, 11, 0, 1, 2)

        self.line_8 = QFrame(self.frame)
        self.line_8.setObjectName(u"line_8")
        self.line_8.setFrameShape(QFrame.Shape.HLine)
        self.line_8.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_channelB.addWidget(self.line_8, 7, 0, 1, 2)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.pushButton_localB = QPushButton(self.frame)
        self.pushButton_localB.setObjectName(u"pushButton_localB")
        self.pushButton_localB.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_localB.setCheckable(True)
        self.pushButton_localB.setChecked(True)

        self.horizontalLayout_9.addWidget(self.pushButton_localB)

        self.pushButton_remoteB = QPushButton(self.frame)
        self.pushButton_remoteB.setObjectName(u"pushButton_remoteB")
        self.pushButton_remoteB.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.pushButton_remoteB.setCheckable(True)

        self.horizontalLayout_9.addWidget(self.pushButton_remoteB)


        self.gridLayout_channelB.addLayout(self.horizontalLayout_9, 5, 1, 1, 1)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.pushButton_resetB = QPushButton(self.frame)
        self.pushButton_resetB.setObjectName(u"pushButton_resetB")
        self.pushButton_resetB.setStyleSheet(u"QPushButton:checked {color:black;}")

        self.horizontalLayout_11.addWidget(self.pushButton_resetB)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_3)

        self.pushButton_applyB = QPushButton(self.frame)
        self.pushButton_applyB.setObjectName(u"pushButton_applyB")

        self.horizontalLayout_11.addWidget(self.pushButton_applyB)


        self.gridLayout_channelB.addLayout(self.horizontalLayout_11, 8, 0, 1, 2)


        self.verticalLayout_4.addLayout(self.gridLayout_channelB)

        self.pushButton_singleB = QPushButton(self.frame)
        self.pushButton_singleB.setObjectName(u"pushButton_singleB")
        sizePolicy2.setHeightForWidth(self.pushButton_singleB.sizePolicy().hasHeightForWidth())
        self.pushButton_singleB.setSizePolicy(sizePolicy2)

        self.verticalLayout_4.addWidget(self.pushButton_singleB)

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
        Form.setWindowTitle(QCoreApplication.translate("Form", u"SMU", None))
        self.label.setText(QCoreApplication.translate("Form", u"Device:", None))
        self.pushButton_connect.setText(QCoreApplication.translate("Form", u"Connect", None))
        self.label_status.setText(QCoreApplication.translate("Form", u"No connection", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Channel A", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"Source", None))
        self.pushButton_resetA.setText(QCoreApplication.translate("Form", u"Reset", None))
        self.pushButton_applyA.setText(QCoreApplication.translate("Form", u"Apply", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"State", None))
        self.pushButton_voltageA.setText(QCoreApplication.translate("Form", u"Voltage", None))
        self.pushButton_currentA.setText(QCoreApplication.translate("Form", u"Current", None))
        self.pushButton_localA.setText(QCoreApplication.translate("Form", u"Local 2 Wire", None))
        self.pushButton_remoteA.setText(QCoreApplication.translate("Form", u"Remote 4 Wire", None))
        self.label_voltageA.setText(QCoreApplication.translate("Form", u"--- V", None))
        self.label_currentA.setText(QCoreApplication.translate("Form", u"--- A", None))
        self.label_statsA.setText(QCoreApplication.translate("Form", u"Stats", None))
        self.pushButton_outputA.setText(QCoreApplication.translate("Form", u"OFF", None))
        self.label_limitA.setText(QCoreApplication.translate("Form", u"Limit [A]", None))
#if QT_CONFIG(tooltip)
        self.label_levelA.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_levelA.setText(QCoreApplication.translate("Form", u"Level [V]", None))
        self.pushButton_singleA.setText(QCoreApplication.translate("Form", u"Single", None))
        self.label_channel.setText(QCoreApplication.translate("Form", u"Channel B", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Source", None))
        self.label_limitB.setText(QCoreApplication.translate("Form", u"Limit [A]", None))
        self.label_levelB.setText(QCoreApplication.translate("Form", u"Level [V]", None))
        self.pushButton_voltageB.setText(QCoreApplication.translate("Form", u"Voltage", None))
        self.pushButton_currentB.setText(QCoreApplication.translate("Form", u"Current", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"State", None))
        self.label_voltageB.setText(QCoreApplication.translate("Form", u"--- V", None))
        self.label_currentB.setText(QCoreApplication.translate("Form", u"--- A", None))
        self.label_statsB.setText(QCoreApplication.translate("Form", u"Stats", None))
        self.pushButton_outputB.setText(QCoreApplication.translate("Form", u"OFF", None))
        self.pushButton_localB.setText(QCoreApplication.translate("Form", u"Local 2 Wire", None))
        self.pushButton_remoteB.setText(QCoreApplication.translate("Form", u"Remote 4 Wire", None))
        self.pushButton_resetB.setText(QCoreApplication.translate("Form", u"Reset", None))
        self.pushButton_applyB.setText(QCoreApplication.translate("Form", u"Apply", None))
        self.pushButton_singleB.setText(QCoreApplication.translate("Form", u"Single", None))
    # retranslateUi

