# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SweepWidgetBHajms.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QPlainTextEdit,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_Sweep(object):
    def setupUi(self, Sweep):
        if not Sweep.objectName():
            Sweep.setObjectName(u"Sweep")
        Sweep.resize(362, 600)
        self.verticalLayout = QVBoxLayout(Sweep)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(Sweep)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"QPushButton:checked {color:black;}")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.widget_configuration = QWidget(self.frame)
        self.widget_configuration.setObjectName(u"widget_configuration")
        self.verticalLayout_3 = QVBoxLayout(self.widget_configuration)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_configuration = QGridLayout()
        self.gridLayout_configuration.setObjectName(u"gridLayout_configuration")
        self.doubleSpinBox_limit = QDoubleSpinBox(self.widget_configuration)
        self.doubleSpinBox_limit.setObjectName(u"doubleSpinBox_limit")
        self.doubleSpinBox_limit.setMinimumSize(QSize(200, 0))
        self.doubleSpinBox_limit.setDecimals(3)
        self.doubleSpinBox_limit.setMinimum(-200.000000000000000)
        self.doubleSpinBox_limit.setMaximum(200.000000000000000)
        self.doubleSpinBox_limit.setSingleStep(0.100000000000000)

        self.gridLayout_configuration.addWidget(self.doubleSpinBox_limit, 4, 1, 1, 1)

        self.label_2 = QLabel(self.widget_configuration)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFrameShape(QFrame.Shape.NoFrame)

        self.gridLayout_configuration.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_3 = QLabel(self.widget_configuration)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_configuration.addWidget(self.label_3, 4, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButton_returnZero = QPushButton(self.widget_configuration)
        self.pushButton_returnZero.setObjectName(u"pushButton_returnZero")
        self.pushButton_returnZero.setCheckable(True)
        self.pushButton_returnZero.setChecked(True)

        self.horizontalLayout_3.addWidget(self.pushButton_returnZero)

        self.pushButton_holdFinal = QPushButton(self.widget_configuration)
        self.pushButton_holdFinal.setObjectName(u"pushButton_holdFinal")
        self.pushButton_holdFinal.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.pushButton_holdFinal)


        self.gridLayout_configuration.addLayout(self.horizontalLayout_3, 5, 1, 1, 1)

        self.comboBox_mode = QComboBox(self.widget_configuration)
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.setObjectName(u"comboBox_mode")
        self.comboBox_mode.setMinimumSize(QSize(0, 0))

        self.gridLayout_configuration.addWidget(self.comboBox_mode, 2, 1, 1, 1)

        self.label_4 = QLabel(self.widget_configuration)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_configuration.addWidget(self.label_4, 3, 0, 1, 1)

        self.label_5 = QLabel(self.widget_configuration)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_configuration.addWidget(self.label_5, 5, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_voltage = QPushButton(self.widget_configuration)
        self.pushButton_voltage.setObjectName(u"pushButton_voltage")
        self.pushButton_voltage.setCheckable(True)
        self.pushButton_voltage.setChecked(True)

        self.horizontalLayout_2.addWidget(self.pushButton_voltage)

        self.pushButton_current = QPushButton(self.widget_configuration)
        self.pushButton_current.setObjectName(u"pushButton_current")
        self.pushButton_current.setCheckable(True)

        self.horizontalLayout_2.addWidget(self.pushButton_current)


        self.gridLayout_configuration.addLayout(self.horizontalLayout_2, 3, 1, 1, 1)

        self.label = QLabel(self.widget_configuration)
        self.label.setObjectName(u"label")

        self.gridLayout_configuration.addWidget(self.label, 2, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_channelA = QPushButton(self.widget_configuration)
        self.pushButton_channelA.setObjectName(u"pushButton_channelA")
        self.pushButton_channelA.setCheckable(True)
        self.pushButton_channelA.setChecked(True)

        self.horizontalLayout.addWidget(self.pushButton_channelA)

        self.pushButton_channelB = QPushButton(self.widget_configuration)
        self.pushButton_channelB.setObjectName(u"pushButton_channelB")
        self.pushButton_channelB.setCheckable(True)

        self.horizontalLayout.addWidget(self.pushButton_channelB)


        self.gridLayout_configuration.addLayout(self.horizontalLayout, 1, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_configuration)


        self.verticalLayout_2.addWidget(self.widget_configuration)

        self.line_2 = QFrame(self.frame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_2)

        self.widget_StandardPage = QWidget(self.frame)
        self.widget_StandardPage.setObjectName(u"widget_StandardPage")
        self.verticalLayout_6 = QVBoxLayout(self.widget_StandardPage)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_StandardPage = QGridLayout()
        self.gridLayout_StandardPage.setObjectName(u"gridLayout_StandardPage")
        self.label_8 = QLabel(self.widget_StandardPage)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_StandardPage.addWidget(self.label_8, 2, 0, 1, 1)

        self.label_7 = QLabel(self.widget_StandardPage)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_StandardPage.addWidget(self.label_7, 1, 0, 1, 1)

        self.label_6 = QLabel(self.widget_StandardPage)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_StandardPage.addWidget(self.label_6, 0, 0, 1, 1)

        self.label_9 = QLabel(self.widget_StandardPage)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_StandardPage.addWidget(self.label_9, 3, 0, 1, 1)

        self.doubleSpinBox_start = QDoubleSpinBox(self.widget_StandardPage)
        self.doubleSpinBox_start.setObjectName(u"doubleSpinBox_start")
        self.doubleSpinBox_start.setMinimumSize(QSize(200, 0))
        self.doubleSpinBox_start.setMinimum(-200.000000000000000)
        self.doubleSpinBox_start.setMaximum(200.000000000000000)
        self.doubleSpinBox_start.setSingleStep(0.100000000000000)

        self.gridLayout_StandardPage.addWidget(self.doubleSpinBox_start, 0, 1, 1, 1)

        self.doubleSpinBox_end = QDoubleSpinBox(self.widget_StandardPage)
        self.doubleSpinBox_end.setObjectName(u"doubleSpinBox_end")
        self.doubleSpinBox_end.setMinimum(-200.000000000000000)
        self.doubleSpinBox_end.setMaximum(200.000000000000000)
        self.doubleSpinBox_end.setSingleStep(0.100000000000000)

        self.gridLayout_StandardPage.addWidget(self.doubleSpinBox_end, 1, 1, 1, 1)

        self.spinBox_steps = QSpinBox(self.widget_StandardPage)
        self.spinBox_steps.setObjectName(u"spinBox_steps")
        self.spinBox_steps.setMinimum(2)
        self.spinBox_steps.setMaximum(10000000)
        self.spinBox_steps.setValue(10)

        self.gridLayout_StandardPage.addWidget(self.spinBox_steps, 2, 1, 1, 1)

        self.doubleSpinBox_delay = QDoubleSpinBox(self.widget_StandardPage)
        self.doubleSpinBox_delay.setObjectName(u"doubleSpinBox_delay")
        self.doubleSpinBox_delay.setDecimals(3)
        self.doubleSpinBox_delay.setMaximum(600.000000000000000)
        self.doubleSpinBox_delay.setSingleStep(0.100000000000000)
        self.doubleSpinBox_delay.setValue(0.100000000000000)

        self.gridLayout_StandardPage.addWidget(self.doubleSpinBox_delay, 3, 1, 1, 1)


        self.verticalLayout_6.addLayout(self.gridLayout_StandardPage)


        self.verticalLayout_2.addWidget(self.widget_StandardPage)

        self.widget_customPage = QWidget(self.frame)
        self.widget_customPage.setObjectName(u"widget_customPage")
        self.verticalLayout_5 = QVBoxLayout(self.widget_customPage)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_customPage = QGridLayout()
        self.gridLayout_customPage.setObjectName(u"gridLayout_customPage")
        self.label_10 = QLabel(self.widget_customPage)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_customPage.addWidget(self.label_10, 1, 0, 1, 1)

        self.doubleSpinBox_delayCustom = QDoubleSpinBox(self.widget_customPage)
        self.doubleSpinBox_delayCustom.setObjectName(u"doubleSpinBox_delayCustom")
        self.doubleSpinBox_delayCustom.setMinimumSize(QSize(200, 0))
        self.doubleSpinBox_delayCustom.setDecimals(3)
        self.doubleSpinBox_delayCustom.setMaximum(600.000000000000000)
        self.doubleSpinBox_delayCustom.setSingleStep(0.100000000000000)
        self.doubleSpinBox_delayCustom.setValue(0.100000000000000)

        self.gridLayout_customPage.addWidget(self.doubleSpinBox_delayCustom, 1, 1, 1, 1)

        self.plainTextEdit_customPoints = QPlainTextEdit(self.widget_customPage)
        self.plainTextEdit_customPoints.setObjectName(u"plainTextEdit_customPoints")

        self.gridLayout_customPage.addWidget(self.plainTextEdit_customPoints, 0, 0, 1, 2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.pushButton_saveCustom = QPushButton(self.widget_customPage)
        self.pushButton_saveCustom.setObjectName(u"pushButton_saveCustom")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_saveCustom.sizePolicy().hasHeightForWidth())
        self.pushButton_saveCustom.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.pushButton_saveCustom)

        self.pushButton_loadCustom = QPushButton(self.widget_customPage)
        self.pushButton_loadCustom.setObjectName(u"pushButton_loadCustom")
        sizePolicy.setHeightForWidth(self.pushButton_loadCustom.sizePolicy().hasHeightForWidth())
        self.pushButton_loadCustom.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.pushButton_loadCustom)


        self.gridLayout_customPage.addLayout(self.horizontalLayout_4, 2, 0, 1, 2)


        self.verticalLayout_5.addLayout(self.gridLayout_customPage)


        self.verticalLayout_2.addWidget(self.widget_customPage)

        self.line = QFrame(self.frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line)

        self.widget_execution = QWidget(self.frame)
        self.widget_execution.setObjectName(u"widget_execution")
        self.verticalLayout_4 = QVBoxLayout(self.widget_execution)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_execution = QGridLayout()
        self.gridLayout_execution.setObjectName(u"gridLayout_execution")
        self.pushButton_stop = QPushButton(self.widget_execution)
        self.pushButton_stop.setObjectName(u"pushButton_stop")
        self.pushButton_stop.setEnabled(False)
        sizePolicy.setHeightForWidth(self.pushButton_stop.sizePolicy().hasHeightForWidth())
        self.pushButton_stop.setSizePolicy(sizePolicy)
        self.pushButton_stop.setMinimumSize(QSize(0, 40))
        font = QFont()
        font.setPointSize(10)
        font.setBold(False)
        self.pushButton_stop.setFont(font)

        self.gridLayout_execution.addWidget(self.pushButton_stop, 1, 1, 1, 1)

        self.progressBar = QProgressBar(self.widget_execution)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.gridLayout_execution.addWidget(self.progressBar, 1, 0, 1, 1)

        self.widget_preview = QWidget(self.widget_execution)
        self.widget_preview.setObjectName(u"widget_preview")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget_preview.sizePolicy().hasHeightForWidth())
        self.widget_preview.setSizePolicy(sizePolicy1)
        self.widget_preview.setMinimumSize(QSize(0, 100))

        self.gridLayout_execution.addWidget(self.widget_preview, 0, 0, 1, 3)

        self.pushButton_start_pause = QPushButton(self.widget_execution)
        self.pushButton_start_pause.setObjectName(u"pushButton_start_pause")
        sizePolicy.setHeightForWidth(self.pushButton_start_pause.sizePolicy().hasHeightForWidth())
        self.pushButton_start_pause.setSizePolicy(sizePolicy)
        self.pushButton_start_pause.setMinimumSize(QSize(0, 40))
        self.pushButton_start_pause.setFont(font)
        self.pushButton_start_pause.setCheckable(True)

        self.gridLayout_execution.addWidget(self.pushButton_start_pause, 1, 2, 1, 1)


        self.verticalLayout_4.addLayout(self.gridLayout_execution)


        self.verticalLayout_2.addWidget(self.widget_execution)


        self.verticalLayout.addWidget(self.frame)


        self.retranslateUi(Sweep)

        QMetaObject.connectSlotsByName(Sweep)
    # setupUi

    def retranslateUi(self, Sweep):
        Sweep.setWindowTitle(QCoreApplication.translate("Sweep", u"Form", None))
        self.doubleSpinBox_limit.setSuffix(QCoreApplication.translate("Sweep", u" A", None))
        self.label_2.setText(QCoreApplication.translate("Sweep", u"Channel:", None))
        self.label_3.setText(QCoreApplication.translate("Sweep", u"Limit:", None))
        self.pushButton_returnZero.setText(QCoreApplication.translate("Sweep", u"Return to zero", None))
        self.pushButton_holdFinal.setText(QCoreApplication.translate("Sweep", u"Hold final value", None))
        self.comboBox_mode.setItemText(0, QCoreApplication.translate("Sweep", u"Linear Single", None))
        self.comboBox_mode.setItemText(1, QCoreApplication.translate("Sweep", u"Linear Dual", None))
        self.comboBox_mode.setItemText(2, QCoreApplication.translate("Sweep", u"Logarithmic", None))
        self.comboBox_mode.setItemText(3, QCoreApplication.translate("Sweep", u"Custom List", None))

        self.comboBox_mode.setPlaceholderText(QCoreApplication.translate("Sweep", u"Mode", None))
        self.label_4.setText(QCoreApplication.translate("Sweep", u"Source:", None))
        self.label_5.setText(QCoreApplication.translate("Sweep", u"Behavior termination:", None))
        self.pushButton_voltage.setText(QCoreApplication.translate("Sweep", u"Voltage", None))
        self.pushButton_current.setText(QCoreApplication.translate("Sweep", u"Current", None))
        self.label.setText(QCoreApplication.translate("Sweep", u"Sweep Mode:", None))
        self.pushButton_channelA.setText(QCoreApplication.translate("Sweep", u"A", None))
        self.pushButton_channelB.setText(QCoreApplication.translate("Sweep", u"B", None))
        self.label_8.setText(QCoreApplication.translate("Sweep", u"Steps:", None))
        self.label_7.setText(QCoreApplication.translate("Sweep", u"End:", None))
        self.label_6.setText(QCoreApplication.translate("Sweep", u"Start:", None))
        self.label_9.setText(QCoreApplication.translate("Sweep", u"Delay:", None))
        self.doubleSpinBox_start.setSuffix(QCoreApplication.translate("Sweep", u" V", None))
        self.doubleSpinBox_end.setSuffix(QCoreApplication.translate("Sweep", u" V", None))
        self.spinBox_steps.setSuffix(QCoreApplication.translate("Sweep", u" pts", None))
        self.doubleSpinBox_delay.setSuffix(QCoreApplication.translate("Sweep", u" s", None))
        self.label_10.setText(QCoreApplication.translate("Sweep", u"Delay:", None))
        self.doubleSpinBox_delayCustom.setSuffix(QCoreApplication.translate("Sweep", u" s", None))
#if QT_CONFIG(tooltip)
        self.plainTextEdit_customPoints.setToolTip(QCoreApplication.translate("Sweep", u"Enter a list of voltages (comma-separated or on a new line).", None))
#endif // QT_CONFIG(tooltip)
        self.plainTextEdit_customPoints.setPlaceholderText(QCoreApplication.translate("Sweep", u"0, 1.5, 3.0, 1.5, 0, -1.5...", None))
        self.pushButton_saveCustom.setText(QCoreApplication.translate("Sweep", u"Save", None))
        self.pushButton_loadCustom.setText(QCoreApplication.translate("Sweep", u"Load from CSV / TXT...", None))
        self.pushButton_stop.setText(QCoreApplication.translate("Sweep", u"Stop", None))
        self.pushButton_start_pause.setText(QCoreApplication.translate("Sweep", u"Start", None))
    # retranslateUi

