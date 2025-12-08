# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WaterfallWidgetMFPxvE.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(402, 424)
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
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_connection = QVBoxLayout()
        self.verticalLayout_connection.setObjectName(u"verticalLayout_connection")
        self.verticalLayout_connection.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)

        self.horizontalLayout.addLayout(self.verticalLayout_connection)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout_settings = QVBoxLayout()
        self.verticalLayout_settings.setObjectName(u"verticalLayout_settings")
        self.verticalLayout_settings.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        self.horizontalLayout.addLayout(self.verticalLayout_settings)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_integrationTime = QLabel(self.frame)
        self.label_integrationTime.setObjectName(u"label_integrationTime")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_integrationTime.sizePolicy().hasHeightForWidth())
        self.label_integrationTime.setSizePolicy(sizePolicy1)

        self.horizontalLayout_5.addWidget(self.label_integrationTime)

        self.doubleSpinBox_zOffset = QDoubleSpinBox(self.frame)
        self.doubleSpinBox_zOffset.setObjectName(u"doubleSpinBox_zOffset")

        self.horizontalLayout_5.addWidget(self.doubleSpinBox_zOffset)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_6.addWidget(self.label_2)

        self.comboBox_colormap = QComboBox(self.frame)
        self.comboBox_colormap.setObjectName(u"comboBox_colormap")

        self.horizontalLayout_6.addWidget(self.comboBox_colormap)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_status = QLabel(self.frame)
        self.label_status.setObjectName(u"label_status")

        self.horizontalLayout_4.addWidget(self.label_status)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.checkBox_autoScale = QCheckBox(self.frame)
        self.checkBox_autoScale.setObjectName(u"checkBox_autoScale")

        self.horizontalLayout_4.addWidget(self.checkBox_autoScale)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

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

        self.widget_plot = QWidget(self.frame)
        self.widget_plot.setObjectName(u"widget_plot")
        sizePolicy.setHeightForWidth(self.widget_plot.sizePolicy().hasHeightForWidth())
        self.widget_plot.setSizePolicy(sizePolicy)
        self.widget_plot.setMinimumSize(QSize(380, 200))

        self.verticalLayout.addWidget(self.widget_plot)


        self.gridLayout.addWidget(self.frame, 1, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Waterfall", None))
        self.label_integrationTime.setText(QCoreApplication.translate("Form", u"Z-Offset:", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Colormap:", None))
        self.label_status.setText(QCoreApplication.translate("Form", u"Status", None))
        self.checkBox_autoScale.setText(QCoreApplication.translate("Form", u"Auto Scale", None))
        self.pushButton_clear.setText(QCoreApplication.translate("Form", u"Clear", None))
        self.pushButton_savePlot.setText(QCoreApplication.translate("Form", u"Save Plot", None))
        self.pushButton_saveData.setText(QCoreApplication.translate("Form", u"Save Data", None))
    # retranslateUi

