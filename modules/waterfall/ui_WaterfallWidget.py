# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WaterfallWidgetSgvNju.ui'
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
        Form.resize(446, 296)
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
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.label_integrationTime = QLabel(self.frame)
        self.label_integrationTime.setObjectName(u"label_integrationTime")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
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
        self.verticalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy3)

        self.verticalLayout_3.addWidget(self.label_2)

        self.comboBox_colormap = QComboBox(self.frame)
        self.comboBox_colormap.setObjectName(u"comboBox_colormap")
        sizePolicy2.setHeightForWidth(self.comboBox_colormap.sizePolicy().hasHeightForWidth())
        self.comboBox_colormap.setSizePolicy(sizePolicy2)
        self.comboBox_colormap.setMaximumSize(QSize(200, 16777215))

        self.verticalLayout_3.addWidget(self.comboBox_colormap)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.line_3 = QFrame(self.frame)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line_3)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.pushButton_savePlot = QPushButton(self.frame)
        self.pushButton_savePlot.setObjectName(u"pushButton_savePlot")
        sizePolicy1.setHeightForWidth(self.pushButton_savePlot.sizePolicy().hasHeightForWidth())
        self.pushButton_savePlot.setSizePolicy(sizePolicy1)

        self.verticalLayout_5.addWidget(self.pushButton_savePlot)

        self.pushButton_saveData = QPushButton(self.frame)
        self.pushButton_saveData.setObjectName(u"pushButton_saveData")
        sizePolicy1.setHeightForWidth(self.pushButton_saveData.sizePolicy().hasHeightForWidth())
        self.pushButton_saveData.setSizePolicy(sizePolicy1)

        self.verticalLayout_5.addWidget(self.pushButton_saveData)


        self.horizontalLayout.addLayout(self.verticalLayout_5)

        self.line_4 = QFrame(self.frame)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line_4)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalSpacer = QSpacerItem(20, 26, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.pushButton_clear = QPushButton(self.frame)
        self.pushButton_clear.setObjectName(u"pushButton_clear")
        sizePolicy1.setHeightForWidth(self.pushButton_clear.sizePolicy().hasHeightForWidth())
        self.pushButton_clear.setSizePolicy(sizePolicy1)

        self.verticalLayout_6.addWidget(self.pushButton_clear)


        self.horizontalLayout.addLayout(self.verticalLayout_6)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Waterfall", None))
        self.label_integrationTime.setText(QCoreApplication.translate("Form", u"History Lines:", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Colormap:", None))
        self.pushButton_savePlot.setText(QCoreApplication.translate("Form", u"Save Plot", None))
        self.pushButton_saveData.setText(QCoreApplication.translate("Form", u"Save Data", None))
        self.pushButton_clear.setText(QCoreApplication.translate("Form", u"Clear", None))
    # retranslateUi

