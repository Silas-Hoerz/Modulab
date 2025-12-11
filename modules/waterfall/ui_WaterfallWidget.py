# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WaterfallWidgetiZsNtU.ui'
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
    QHBoxLayout, QLabel, QLayout, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(402, 331)
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
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(9, 9, -1, -1)
        self.widget_plot = QWidget(self.frame)
        self.widget_plot.setObjectName(u"widget_plot")
        sizePolicy.setHeightForWidth(self.widget_plot.sizePolicy().hasHeightForWidth())
        self.widget_plot.setSizePolicy(sizePolicy)
        self.widget_plot.setMinimumSize(QSize(380, 200))

        self.verticalLayout.addWidget(self.widget_plot)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.label_integrationTime = QLabel(self.frame)
        self.label_integrationTime.setObjectName(u"label_integrationTime")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_integrationTime.sizePolicy().hasHeightForWidth())
        self.label_integrationTime.setSizePolicy(sizePolicy1)

        self.verticalLayout_2.addWidget(self.label_integrationTime)

        self.spinBox_bufferSize = QSpinBox(self.frame)
        self.spinBox_bufferSize.setObjectName(u"spinBox_bufferSize")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.spinBox_bufferSize.sizePolicy().hasHeightForWidth())
        self.spinBox_bufferSize.setSizePolicy(sizePolicy2)
        self.spinBox_bufferSize.setMaximumSize(QSize(200, 16777215))
        self.spinBox_bufferSize.setMinimum(1)
        self.spinBox_bufferSize.setMaximum(1999999999)
        self.spinBox_bufferSize.setValue(100)

        self.verticalLayout_2.addWidget(self.spinBox_bufferSize)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.line = QFrame(self.frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_3.addWidget(self.label_2)

        self.comboBox_colormap = QComboBox(self.frame)
        self.comboBox_colormap.setObjectName(u"comboBox_colormap")
        sizePolicy2.setHeightForWidth(self.comboBox_colormap.sizePolicy().hasHeightForWidth())
        self.comboBox_colormap.setSizePolicy(sizePolicy2)
        self.comboBox_colormap.setMaximumSize(QSize(200, 16777215))

        self.verticalLayout_3.addWidget(self.comboBox_colormap)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.line_2 = QFrame(self.frame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_2)

        self.verticalLayout_acquisition = QVBoxLayout()
        self.verticalLayout_acquisition.setObjectName(u"verticalLayout_acquisition")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.pushButton_clear = QPushButton(self.frame)
        self.pushButton_clear.setObjectName(u"pushButton_clear")

        self.horizontalLayout_2.addWidget(self.pushButton_clear)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton_savePlot = QPushButton(self.frame)
        self.pushButton_savePlot.setObjectName(u"pushButton_savePlot")

        self.horizontalLayout_2.addWidget(self.pushButton_savePlot)

        self.pushButton_saveData = QPushButton(self.frame)
        self.pushButton_saveData.setObjectName(u"pushButton_saveData")

        self.horizontalLayout_2.addWidget(self.pushButton_saveData)


        self.verticalLayout_acquisition.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addLayout(self.verticalLayout_acquisition)


        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Waterfall", None))
        self.label_integrationTime.setText(QCoreApplication.translate("Form", u"History Lines:", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Colormap:", None))
        self.pushButton_clear.setText(QCoreApplication.translate("Form", u"Clear", None))
        self.pushButton_savePlot.setText(QCoreApplication.translate("Form", u"Save Plot", None))
        self.pushButton_saveData.setText(QCoreApplication.translate("Form", u"Save Data", None))
    # retranslateUi

