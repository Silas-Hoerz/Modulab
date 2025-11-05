# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DeviceWidgetEditPXufEP.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGraphicsView,
    QHBoxLayout, QLayout, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(428, 334)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QSize(428, 300))
        Form.setMaximumSize(QSize(800, 334))
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.lineEdit_name = QLineEdit(Form)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setMinimumSize(QSize(150, 0))

        self.verticalLayout_2.addWidget(self.lineEdit_name)

        self.comboBox_geometry = QComboBox(Form)
        self.comboBox_geometry.setObjectName(u"comboBox_geometry")

        self.verticalLayout_2.addWidget(self.comboBox_geometry)

        self.lineEdit_length = QLineEdit(Form)
        self.lineEdit_length.setObjectName(u"lineEdit_length")

        self.verticalLayout_2.addWidget(self.lineEdit_length)

        self.lineEdit_width = QLineEdit(Form)
        self.lineEdit_width.setObjectName(u"lineEdit_width")

        self.verticalLayout_2.addWidget(self.lineEdit_width)

        self.lineEdit_radius = QLineEdit(Form)
        self.lineEdit_radius.setObjectName(u"lineEdit_radius")

        self.verticalLayout_2.addWidget(self.lineEdit_radius)

        self.checkBox_cutout = QCheckBox(Form)
        self.checkBox_cutout.setObjectName(u"checkBox_cutout")

        self.verticalLayout_2.addWidget(self.checkBox_cutout)

        self.lineEdit_cutout_length = QLineEdit(Form)
        self.lineEdit_cutout_length.setObjectName(u"lineEdit_cutout_length")

        self.verticalLayout_2.addWidget(self.lineEdit_cutout_length)

        self.lineEdit_cutout_width = QLineEdit(Form)
        self.lineEdit_cutout_width.setObjectName(u"lineEdit_cutout_width")

        self.verticalLayout_2.addWidget(self.lineEdit_cutout_width)

        self.lineEdit_cutout_radius = QLineEdit(Form)
        self.lineEdit_cutout_radius.setObjectName(u"lineEdit_cutout_radius")

        self.verticalLayout_2.addWidget(self.lineEdit_cutout_radius)

        self.lineEdit_area = QLineEdit(Form)
        self.lineEdit_area.setObjectName(u"lineEdit_area")
        self.lineEdit_area.setEnabled(False)

        self.verticalLayout_2.addWidget(self.lineEdit_area)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.graphicsView = QGraphicsView(Form)
        self.graphicsView.setObjectName(u"graphicsView")
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setMinimumSize(QSize(250, 250))
        self.graphicsView.setMaximumSize(QSize(250, 250))

        self.horizontalLayout.addWidget(self.graphicsView)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.pushButton_save = QPushButton(Form)
        self.pushButton_save.setObjectName(u"pushButton_save")

        self.horizontalLayout_3.addWidget(self.pushButton_save)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Edit Device", None))
        self.lineEdit_name.setPlaceholderText(QCoreApplication.translate("Form", u"Name", None))
        self.comboBox_geometry.setPlaceholderText(QCoreApplication.translate("Form", u"Geometry", None))
        self.lineEdit_length.setPlaceholderText(QCoreApplication.translate("Form", u"Length [nm]", None))
        self.lineEdit_width.setPlaceholderText(QCoreApplication.translate("Form", u"Width [nm]", None))
        self.lineEdit_radius.setPlaceholderText(QCoreApplication.translate("Form", u"Radius [nm]", None))
        self.checkBox_cutout.setText(QCoreApplication.translate("Form", u"Cutout", None))
        self.lineEdit_cutout_length.setPlaceholderText(QCoreApplication.translate("Form", u"Cutout Length [nm]", None))
        self.lineEdit_cutout_width.setPlaceholderText(QCoreApplication.translate("Form", u"Cutout Width [nm]", None))
        self.lineEdit_cutout_radius.setPlaceholderText(QCoreApplication.translate("Form", u"Cutout Radius [nm]", None))
        self.lineEdit_area.setPlaceholderText(QCoreApplication.translate("Form", u"Area [nm\u00b2]", None))
        self.pushButton_save.setText(QCoreApplication.translate("Form", u"Save Device", None))
    # retranslateUi

