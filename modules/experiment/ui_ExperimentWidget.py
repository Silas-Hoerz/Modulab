# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ExperimentWidgetrEqxAI.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(263, 74)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBox_experiments = QComboBox(self.frame)
        self.comboBox_experiments.setObjectName(u"comboBox_experiments")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_experiments.sizePolicy().hasHeightForWidth())
        self.comboBox_experiments.setSizePolicy(sizePolicy1)
        self.comboBox_experiments.setMinimumSize(QSize(0, 0))

        self.horizontalLayout.addWidget(self.comboBox_experiments)

        self.pushButton_start = QPushButton(self.frame)
        self.pushButton_start.setObjectName(u"pushButton_start")
        sizePolicy.setHeightForWidth(self.pushButton_start.sizePolicy().hasHeightForWidth())
        self.pushButton_start.setSizePolicy(sizePolicy)
        self.pushButton_start.setMinimumSize(QSize(50, 0))
        self.pushButton_start.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_start)

        self.pushButton_pause = QPushButton(self.frame)
        self.pushButton_pause.setObjectName(u"pushButton_pause")
        sizePolicy.setHeightForWidth(self.pushButton_pause.sizePolicy().hasHeightForWidth())
        self.pushButton_pause.setSizePolicy(sizePolicy)
        self.pushButton_pause.setMinimumSize(QSize(50, 0))
        self.pushButton_pause.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_pause)

        self.pushButton_stop = QPushButton(self.frame)
        self.pushButton_stop.setObjectName(u"pushButton_stop")
        sizePolicy.setHeightForWidth(self.pushButton_stop.sizePolicy().hasHeightForWidth())
        self.pushButton_stop.setSizePolicy(sizePolicy)
        self.pushButton_stop.setMinimumSize(QSize(50, 0))
        self.pushButton_stop.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_stop)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.label_progress = QLabel(self.frame)
        self.label_progress.setObjectName(u"label_progress")

        self.verticalLayout.addWidget(self.label_progress)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.verticalLayout_2.addWidget(self.frame)


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

