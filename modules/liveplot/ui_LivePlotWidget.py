# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LivePlotWidgetoRYgep.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_LivePlot(object):
    def setupUi(self, LivePlot):
        if not LivePlot.objectName():
            LivePlot.setObjectName(u"LivePlot")
        LivePlot.resize(400, 300)
        self.verticalLayout_2 = QVBoxLayout(LivePlot)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tabWidget = QTabWidget(LivePlot)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout_2.addWidget(self.tabWidget)


        self.retranslateUi(LivePlot)

        QMetaObject.connectSlotsByName(LivePlot)
    # setupUi

    def retranslateUi(self, LivePlot):
        LivePlot.setWindowTitle(QCoreApplication.translate("LivePlot", u"Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("LivePlot", u"Tab 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("LivePlot", u"Tab 2", None))
    # retranslateUi

