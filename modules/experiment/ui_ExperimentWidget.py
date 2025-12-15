# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ExperimentWidgetfbLhsg.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(368, 118)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
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
        self.comboBox_experiments = QComboBox(self.frame)
        self.comboBox_experiments.setObjectName(u"comboBox_experiments")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_experiments.sizePolicy().hasHeightForWidth())
        self.comboBox_experiments.setSizePolicy(sizePolicy1)
        self.comboBox_experiments.setMinimumSize(QSize(0, 0))

        self.verticalLayout.addWidget(self.comboBox_experiments)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_docs = QPushButton(self.frame)
        self.pushButton_docs.setObjectName(u"pushButton_docs")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_docs.sizePolicy().hasHeightForWidth())
        self.pushButton_docs.setSizePolicy(sizePolicy2)
        self.pushButton_docs.setMinimumSize(QSize(50, 0))
        self.pushButton_docs.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_docs)

        self.pushButton_edit = QPushButton(self.frame)
        self.pushButton_edit.setObjectName(u"pushButton_edit")
        sizePolicy2.setHeightForWidth(self.pushButton_edit.sizePolicy().hasHeightForWidth())
        self.pushButton_edit.setSizePolicy(sizePolicy2)
        self.pushButton_edit.setMinimumSize(QSize(50, 0))
        self.pushButton_edit.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_edit)

        self.pushButton_openDir = QPushButton(self.frame)
        self.pushButton_openDir.setObjectName(u"pushButton_openDir")
        self.pushButton_openDir.setMinimumSize(QSize(50, 0))
        self.pushButton_openDir.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_openDir)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.label_progress = QLabel(self.frame)
        self.label_progress.setObjectName(u"label_progress")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_progress.sizePolicy().hasHeightForWidth())
        self.label_progress.setSizePolicy(sizePolicy3)

        self.verticalLayout_4.addWidget(self.label_progress)


        self.horizontalLayout.addLayout(self.verticalLayout_4)

        self.pushButton_stop = QPushButton(self.frame)
        self.pushButton_stop.setObjectName(u"pushButton_stop")
        sizePolicy2.setHeightForWidth(self.pushButton_stop.sizePolicy().hasHeightForWidth())
        self.pushButton_stop.setSizePolicy(sizePolicy2)
        self.pushButton_stop.setMinimumSize(QSize(50, 50))
        self.pushButton_stop.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_stop)

        self.pushButton_pause = QPushButton(self.frame)
        self.pushButton_pause.setObjectName(u"pushButton_pause")
        sizePolicy2.setHeightForWidth(self.pushButton_pause.sizePolicy().hasHeightForWidth())
        self.pushButton_pause.setSizePolicy(sizePolicy2)
        self.pushButton_pause.setMinimumSize(QSize(50, 50))
        self.pushButton_pause.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_pause)

        self.pushButton_start = QPushButton(self.frame)
        self.pushButton_start.setObjectName(u"pushButton_start")
        sizePolicy2.setHeightForWidth(self.pushButton_start.sizePolicy().hasHeightForWidth())
        self.pushButton_start.setSizePolicy(sizePolicy2)
        self.pushButton_start.setMinimumSize(QSize(50, 50))
        self.pushButton_start.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_start)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.horizontalLayout_3.addLayout(self.verticalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.verticalLayout_2.addWidget(self.frame)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Experiments", None))
        Form.setProperty(u"status", "")
        self.pushButton_docs.setText(QCoreApplication.translate("Form", u"Help", None))
        self.pushButton_edit.setText(QCoreApplication.translate("Form", u"Edit", None))
        self.pushButton_openDir.setText(QCoreApplication.translate("Form", u"Folder", None))
        self.label_progress.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.pushButton_stop.setText(QCoreApplication.translate("Form", u"Stop", None))
        self.pushButton_pause.setText(QCoreApplication.translate("Form", u"Pause", None))
        self.pushButton_start.setText(QCoreApplication.translate("Form", u"Start", None))
    # retranslateUi

