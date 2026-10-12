# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'design.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(799, 600)
        MainWindow.setStyleSheet(u"* {\n"
"	font-family: \"Garamond\";\n"
"	font-size: 12;\n"
"	font-weight: bold\n"
"}\n"
"\n"
"#period_selection_frame, #statement_file_frame, #spreadsheet_file_frame, #statement_spreadsheet_reconciliation_frame, #spreadsheet_kintone_reconciliation_frame, #grey_border_frame {\n"
"	border: 1px solid rgba(0,0,0,.2);\n"
"}\n"
"\n"
"#statement_file_name, #spreadsheet_file_name {\n"
"	border: 2px dashed grey;\n"
"}")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.mpesa_statement_page = QWidget()
        self.mpesa_statement_page.setObjectName(u"mpesa_statement_page")
        self.verticalLayout_2 = QVBoxLayout(self.mpesa_statement_page)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(24, 24, 24, 24)
        self.statement_page_body_frame = QFrame(self.mpesa_statement_page)
        self.statement_page_body_frame.setObjectName(u"statement_page_body_frame")
        self.statement_page_body_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.statement_page_body_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.statement_page_body_frame)
        self.verticalLayout_3.setSpacing(16)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.frame_2 = QFrame(self.statement_page_body_frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_2)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.app_title = QLabel(self.frame_2)
        self.app_title.setObjectName(u"app_title")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.app_title.sizePolicy().hasHeightForWidth())
        self.app_title.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"Garamond"])
        font.setPointSize(16)
        font.setBold(True)
        self.app_title.setFont(font)

        self.verticalLayout_4.addWidget(self.app_title)


        self.verticalLayout_3.addWidget(self.frame_2)

        self.frame_9 = QFrame(self.statement_page_body_frame)
        self.frame_9.setObjectName(u"frame_9")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_9.sizePolicy().hasHeightForWidth())
        self.frame_9.setSizePolicy(sizePolicy1)
        self.frame_9.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_9)
        self.verticalLayout_6.setSpacing(8)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.frame_4 = QFrame(self.frame_9)
        self.frame_4.setObjectName(u"frame_4")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy2)
        font1 = QFont()
        font1.setFamilies([u"Garamond"])
        font1.setPointSize(12)
        font1.setBold(True)
        self.frame_4.setFont(font1)
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_4)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.page_title = QLabel(self.frame_4)
        self.page_title.setObjectName(u"page_title")
        self.page_title.setFont(font1)

        self.verticalLayout_5.addWidget(self.page_title)


        self.verticalLayout_6.addWidget(self.frame_4)

        self.period_selection_frame = QFrame(self.frame_9)
        self.period_selection_frame.setObjectName(u"period_selection_frame")
        sizePolicy2.setHeightForWidth(self.period_selection_frame.sizePolicy().hasHeightForWidth())
        self.period_selection_frame.setSizePolicy(sizePolicy2)
        self.period_selection_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.period_selection_frame.setFrameShadow(QFrame.Shadow.Plain)
        self.period_selection_frame.setLineWidth(1)
        self.horizontalLayout = QHBoxLayout(self.period_selection_frame)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(16, 16, 16, 16)
        self.label_3 = QLabel(self.period_selection_frame)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.month_input_combo = QComboBox(self.period_selection_frame)
        self.month_input_combo.addItem("")
        self.month_input_combo.addItem("")
        self.month_input_combo.addItem("")
        self.month_input_combo.addItem("")
        self.month_input_combo.addItem("")
        self.month_input_combo.addItem("")
        self.month_input_combo.addItem("")
        self.month_input_combo.addItem("")
        self.month_input_combo.addItem("")
        self.month_input_combo.addItem("")
        self.month_input_combo.addItem("")
        self.month_input_combo.addItem("")
        self.month_input_combo.setObjectName(u"month_input_combo")

        self.horizontalLayout.addWidget(self.month_input_combo)

        self.label_4 = QLabel(self.period_selection_frame)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout.addWidget(self.label_4)

        self.year_input_combo = QComboBox(self.period_selection_frame)
        self.year_input_combo.addItem("")
        self.year_input_combo.addItem("")
        self.year_input_combo.addItem("")
        self.year_input_combo.addItem("")
        self.year_input_combo.addItem("")
        self.year_input_combo.addItem("")
        self.year_input_combo.addItem("")
        self.year_input_combo.addItem("")
        self.year_input_combo.addItem("")
        self.year_input_combo.addItem("")
        self.year_input_combo.addItem("")
        self.year_input_combo.setObjectName(u"year_input_combo")

        self.horizontalLayout.addWidget(self.year_input_combo)

        self.horizontalSpacer = QSpacerItem(270, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(2, 1)
        self.horizontalLayout.setStretch(3, 2)
        self.horizontalLayout.setStretch(4, 4)

        self.verticalLayout_6.addWidget(self.period_selection_frame)

        self.statement_file_frame = QFrame(self.frame_9)
        self.statement_file_frame.setObjectName(u"statement_file_frame")
        sizePolicy2.setHeightForWidth(self.statement_file_frame.sizePolicy().hasHeightForWidth())
        self.statement_file_frame.setSizePolicy(sizePolicy2)
        self.statement_file_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.statement_file_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.statement_file_frame)
        self.verticalLayout_7.setSpacing(16)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(16, 16, 16, 16)
        self.frame_5 = QFrame(self.statement_file_frame)
        self.frame_5.setObjectName(u"frame_5")
        sizePolicy2.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy2)
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.frame_5)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.label_5)


        self.verticalLayout_7.addWidget(self.frame_5)

        self.frame_3 = QFrame(self.statement_file_frame)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy2.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy2)
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setSpacing(8)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.browse_statement_file_button = QPushButton(self.frame_3)
        self.browse_statement_file_button.setObjectName(u"browse_statement_file_button")

        self.horizontalLayout_3.addWidget(self.browse_statement_file_button)

        self.statement_file_name = QFrame(self.frame_3)
        self.statement_file_name.setObjectName(u"statement_file_name")
        self.statement_file_name.setFrameShape(QFrame.Shape.StyledPanel)
        self.statement_file_name.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_3.addWidget(self.statement_file_name)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 5)
        self.horizontalLayout_3.setStretch(2, 4)

        self.verticalLayout_7.addWidget(self.frame_3)

        self.frame_6 = QFrame(self.statement_file_frame)
        self.frame_6.setObjectName(u"frame_6")
        sizePolicy2.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy2)
        self.frame_6.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_4.setSpacing(8)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_6 = QLabel(self.frame_6)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_4.addWidget(self.label_6)

        self.password_input = QLineEdit(self.frame_6)
        self.password_input.setObjectName(u"password_input")

        self.horizontalLayout_4.addWidget(self.password_input)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 5)
        self.horizontalLayout_4.setStretch(2, 4)

        self.verticalLayout_7.addWidget(self.frame_6)

        self.frame_8 = QFrame(self.statement_file_frame)
        self.frame_8.setObjectName(u"frame_8")
        sizePolicy2.setHeightForWidth(self.frame_8.sizePolicy().hasHeightForWidth())
        self.frame_8.setSizePolicy(sizePolicy2)
        self.frame_8.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_5.setSpacing(8)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.unlock_file_button = QPushButton(self.frame_8)
        self.unlock_file_button.setObjectName(u"unlock_file_button")

        self.horizontalLayout_5.addWidget(self.unlock_file_button)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_4)

        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(1, 9)

        self.verticalLayout_7.addWidget(self.frame_8)


        self.verticalLayout_6.addWidget(self.statement_file_frame)

        self.frame_7 = QFrame(self.frame_9)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame_7)
        self.gridLayout.setSpacing(16)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer = QSpacerItem(20, 176, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 1, 1, 1, 1)

        self.to_spreadsheet_page_button = QPushButton(self.frame_7)
        self.to_spreadsheet_page_button.setObjectName(u"to_spreadsheet_page_button")
        self.to_spreadsheet_page_button.setMinimumSize(QSize(160, 0))

        self.gridLayout.addWidget(self.to_spreadsheet_page_button, 0, 2, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_5, 0, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 176, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 1, 2, 1, 1)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_8, 0, 0, 1, 1)


        self.verticalLayout_6.addWidget(self.frame_7)


        self.verticalLayout_3.addWidget(self.frame_9)


        self.verticalLayout_2.addWidget(self.statement_page_body_frame)

        self.stackedWidget.addWidget(self.mpesa_statement_page)
        self.spreadsheet_records_page = QWidget()
        self.spreadsheet_records_page.setObjectName(u"spreadsheet_records_page")
        self.verticalLayout_13 = QVBoxLayout(self.spreadsheet_records_page)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(24, 24, 24, 24)
        self.spreadsheet_page_body_frame = QFrame(self.spreadsheet_records_page)
        self.spreadsheet_page_body_frame.setObjectName(u"spreadsheet_page_body_frame")
        self.spreadsheet_page_body_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.spreadsheet_page_body_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.spreadsheet_page_body_frame)
        self.verticalLayout_8.setSpacing(16)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.frame_10 = QFrame(self.spreadsheet_page_body_frame)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame_10)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.app_title_2 = QLabel(self.frame_10)
        self.app_title_2.setObjectName(u"app_title_2")
        sizePolicy.setHeightForWidth(self.app_title_2.sizePolicy().hasHeightForWidth())
        self.app_title_2.setSizePolicy(sizePolicy)
        self.app_title_2.setFont(font)

        self.verticalLayout_9.addWidget(self.app_title_2)


        self.verticalLayout_8.addWidget(self.frame_10)

        self.frame_14 = QFrame(self.spreadsheet_page_body_frame)
        self.frame_14.setObjectName(u"frame_14")
        sizePolicy1.setHeightForWidth(self.frame_14.sizePolicy().hasHeightForWidth())
        self.frame_14.setSizePolicy(sizePolicy1)
        self.frame_14.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_14.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.frame_14)
        self.verticalLayout_10.setSpacing(8)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.frame_11 = QFrame(self.frame_14)
        self.frame_11.setObjectName(u"frame_11")
        sizePolicy2.setHeightForWidth(self.frame_11.sizePolicy().hasHeightForWidth())
        self.frame_11.setSizePolicy(sizePolicy2)
        self.frame_11.setFont(font1)
        self.frame_11.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_11.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.frame_11)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.page_title_2 = QLabel(self.frame_11)
        self.page_title_2.setObjectName(u"page_title_2")
        self.page_title_2.setFont(font1)

        self.verticalLayout_11.addWidget(self.page_title_2)


        self.verticalLayout_10.addWidget(self.frame_11)

        self.spreadsheet_file_frame = QFrame(self.frame_14)
        self.spreadsheet_file_frame.setObjectName(u"spreadsheet_file_frame")
        sizePolicy2.setHeightForWidth(self.spreadsheet_file_frame.sizePolicy().hasHeightForWidth())
        self.spreadsheet_file_frame.setSizePolicy(sizePolicy2)
        self.spreadsheet_file_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.spreadsheet_file_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.spreadsheet_file_frame)
        self.verticalLayout_12.setSpacing(16)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(16, 16, 16, 16)
        self.frame_12 = QFrame(self.spreadsheet_file_frame)
        self.frame_12.setObjectName(u"frame_12")
        sizePolicy2.setHeightForWidth(self.frame_12.sizePolicy().hasHeightForWidth())
        self.frame_12.setSizePolicy(sizePolicy2)
        self.frame_12.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_12.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_12)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.label_9 = QLabel(self.frame_12)
        self.label_9.setObjectName(u"label_9")
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)

        self.horizontalLayout_7.addWidget(self.label_9)


        self.verticalLayout_12.addWidget(self.frame_12)

        self.frame_13 = QFrame(self.spreadsheet_file_frame)
        self.frame_13.setObjectName(u"frame_13")
        sizePolicy2.setHeightForWidth(self.frame_13.sizePolicy().hasHeightForWidth())
        self.frame_13.setSizePolicy(sizePolicy2)
        self.frame_13.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_13.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_13)
        self.horizontalLayout_8.setSpacing(8)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.browse_spreadsheet_file_button = QPushButton(self.frame_13)
        self.browse_spreadsheet_file_button.setObjectName(u"browse_spreadsheet_file_button")

        self.horizontalLayout_8.addWidget(self.browse_spreadsheet_file_button)

        self.spreadsheet_file_name = QFrame(self.frame_13)
        self.spreadsheet_file_name.setObjectName(u"spreadsheet_file_name")
        self.spreadsheet_file_name.setFrameShape(QFrame.Shape.StyledPanel)
        self.spreadsheet_file_name.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_8.addWidget(self.spreadsheet_file_name)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_7)

        self.horizontalLayout_8.setStretch(0, 1)
        self.horizontalLayout_8.setStretch(1, 5)
        self.horizontalLayout_8.setStretch(2, 4)

        self.verticalLayout_12.addWidget(self.frame_13)

        self.frame_15 = QFrame(self.spreadsheet_file_frame)
        self.frame_15.setObjectName(u"frame_15")
        sizePolicy2.setHeightForWidth(self.frame_15.sizePolicy().hasHeightForWidth())
        self.frame_15.setSizePolicy(sizePolicy2)
        self.frame_15.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_15.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_15)
        self.horizontalLayout_10.setSpacing(8)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.validate_file_button = QPushButton(self.frame_15)
        self.validate_file_button.setObjectName(u"validate_file_button")

        self.horizontalLayout_10.addWidget(self.validate_file_button)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_9)

        self.horizontalLayout_10.setStretch(0, 1)
        self.horizontalLayout_10.setStretch(1, 9)

        self.verticalLayout_12.addWidget(self.frame_15)


        self.verticalLayout_10.addWidget(self.spreadsheet_file_frame)

        self.statement_spreadsheet_reconciliation_frame = QFrame(self.frame_14)
        self.statement_spreadsheet_reconciliation_frame.setObjectName(u"statement_spreadsheet_reconciliation_frame")
        sizePolicy2.setHeightForWidth(self.statement_spreadsheet_reconciliation_frame.sizePolicy().hasHeightForWidth())
        self.statement_spreadsheet_reconciliation_frame.setSizePolicy(sizePolicy2)
        self.statement_spreadsheet_reconciliation_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.statement_spreadsheet_reconciliation_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.statement_spreadsheet_reconciliation_frame)
        self.verticalLayout_14.setSpacing(16)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(16, 16, 16, 16)
        self.label = QLabel(self.statement_spreadsheet_reconciliation_frame)
        self.label.setObjectName(u"label")

        self.verticalLayout_14.addWidget(self.label)

        self.frame_17 = QFrame(self.statement_spreadsheet_reconciliation_frame)
        self.frame_17.setObjectName(u"frame_17")
        self.frame_17.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_17.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_17)
        self.horizontalLayout_6.setSpacing(8)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.reconcile_statement_spreadsheet_button = QPushButton(self.frame_17)
        self.reconcile_statement_spreadsheet_button.setObjectName(u"reconcile_statement_spreadsheet_button")

        self.horizontalLayout_6.addWidget(self.reconcile_statement_spreadsheet_button)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_6)

        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(1, 9)

        self.verticalLayout_14.addWidget(self.frame_17)


        self.verticalLayout_10.addWidget(self.statement_spreadsheet_reconciliation_frame)

        self.frame_16 = QFrame(self.frame_14)
        self.frame_16.setObjectName(u"frame_16")
        self.frame_16.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_16.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_16)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_10, 0, 1, 1, 1)

        self.to_kintone_page = QPushButton(self.frame_16)
        self.to_kintone_page.setObjectName(u"to_kintone_page")
        self.to_kintone_page.setMinimumSize(QSize(160, 0))

        self.gridLayout_2.addWidget(self.to_kintone_page, 0, 2, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 176, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_3, 1, 1, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 176, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_4, 1, 2, 1, 1)

        self.back_to_statement_page = QPushButton(self.frame_16)
        self.back_to_statement_page.setObjectName(u"back_to_statement_page")
        self.back_to_statement_page.setMinimumSize(QSize(160, 0))

        self.gridLayout_2.addWidget(self.back_to_statement_page, 0, 0, 1, 1)


        self.verticalLayout_10.addWidget(self.frame_16)


        self.verticalLayout_8.addWidget(self.frame_14)


        self.verticalLayout_13.addWidget(self.spreadsheet_page_body_frame)

        self.stackedWidget.addWidget(self.spreadsheet_records_page)
        self.kintone_page = QWidget()
        self.kintone_page.setObjectName(u"kintone_page")
        self.verticalLayout_21 = QVBoxLayout(self.kintone_page)
        self.verticalLayout_21.setSpacing(8)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(24, 24, 24, 24)
        self.kintone_page_body_frame = QFrame(self.kintone_page)
        self.kintone_page_body_frame.setObjectName(u"kintone_page_body_frame")
        self.kintone_page_body_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.kintone_page_body_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.kintone_page_body_frame)
        self.verticalLayout_15.setSpacing(16)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.frame_18 = QFrame(self.kintone_page_body_frame)
        self.frame_18.setObjectName(u"frame_18")
        self.frame_18.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_18.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_16 = QVBoxLayout(self.frame_18)
        self.verticalLayout_16.setSpacing(0)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.app_title_3 = QLabel(self.frame_18)
        self.app_title_3.setObjectName(u"app_title_3")
        sizePolicy.setHeightForWidth(self.app_title_3.sizePolicy().hasHeightForWidth())
        self.app_title_3.setSizePolicy(sizePolicy)
        self.app_title_3.setFont(font)

        self.verticalLayout_16.addWidget(self.app_title_3)


        self.verticalLayout_15.addWidget(self.frame_18)

        self.frame_19 = QFrame(self.kintone_page_body_frame)
        self.frame_19.setObjectName(u"frame_19")
        sizePolicy1.setHeightForWidth(self.frame_19.sizePolicy().hasHeightForWidth())
        self.frame_19.setSizePolicy(sizePolicy1)
        self.frame_19.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_19.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_17 = QVBoxLayout(self.frame_19)
        self.verticalLayout_17.setSpacing(8)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.frame_20 = QFrame(self.frame_19)
        self.frame_20.setObjectName(u"frame_20")
        sizePolicy2.setHeightForWidth(self.frame_20.sizePolicy().hasHeightForWidth())
        self.frame_20.setSizePolicy(sizePolicy2)
        self.frame_20.setFont(font1)
        self.frame_20.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_20.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_18 = QVBoxLayout(self.frame_20)
        self.verticalLayout_18.setSpacing(0)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.page_title_3 = QLabel(self.frame_20)
        self.page_title_3.setObjectName(u"page_title_3")
        self.page_title_3.setFont(font1)

        self.verticalLayout_18.addWidget(self.page_title_3)


        self.verticalLayout_17.addWidget(self.frame_20)

        self.spreadsheet_kintone_reconciliation_frame = QFrame(self.frame_19)
        self.spreadsheet_kintone_reconciliation_frame.setObjectName(u"spreadsheet_kintone_reconciliation_frame")
        sizePolicy2.setHeightForWidth(self.spreadsheet_kintone_reconciliation_frame.sizePolicy().hasHeightForWidth())
        self.spreadsheet_kintone_reconciliation_frame.setSizePolicy(sizePolicy2)
        self.spreadsheet_kintone_reconciliation_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.spreadsheet_kintone_reconciliation_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_20 = QVBoxLayout(self.spreadsheet_kintone_reconciliation_frame)
        self.verticalLayout_20.setSpacing(16)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(16, 16, 16, 16)
        self.label_2 = QLabel(self.spreadsheet_kintone_reconciliation_frame)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_20.addWidget(self.label_2)

        self.frame_24 = QFrame(self.spreadsheet_kintone_reconciliation_frame)
        self.frame_24.setObjectName(u"frame_24")
        self.frame_24.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_24.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_13 = QHBoxLayout(self.frame_24)
        self.horizontalLayout_13.setSpacing(8)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.reconcile_spreadsheet_kintone_button = QPushButton(self.frame_24)
        self.reconcile_spreadsheet_kintone_button.setObjectName(u"reconcile_spreadsheet_kintone_button")

        self.horizontalLayout_13.addWidget(self.reconcile_spreadsheet_kintone_button)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_12)

        self.horizontalLayout_13.setStretch(0, 1)
        self.horizontalLayout_13.setStretch(1, 9)

        self.verticalLayout_20.addWidget(self.frame_24)


        self.verticalLayout_17.addWidget(self.spreadsheet_kintone_reconciliation_frame)

        self.frame_25 = QFrame(self.frame_19)
        self.frame_25.setObjectName(u"frame_25")
        self.frame_25.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_25.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_3 = QGridLayout(self.frame_25)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer_5 = QSpacerItem(20, 176, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_5, 1, 1, 1, 1)

        self.verticalSpacer_6 = QSpacerItem(20, 176, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_6, 1, 2, 1, 1)

        self.to_cloudia_evidence_page = QPushButton(self.frame_25)
        self.to_cloudia_evidence_page.setObjectName(u"to_cloudia_evidence_page")
        self.to_cloudia_evidence_page.setMinimumSize(QSize(160, 0))

        self.gridLayout_3.addWidget(self.to_cloudia_evidence_page, 0, 2, 1, 1)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_13, 0, 1, 1, 1)

        self.back_to_spreadsheet_page = QPushButton(self.frame_25)
        self.back_to_spreadsheet_page.setObjectName(u"back_to_spreadsheet_page")
        self.back_to_spreadsheet_page.setMinimumSize(QSize(160, 0))

        self.gridLayout_3.addWidget(self.back_to_spreadsheet_page, 0, 0, 1, 1)


        self.verticalLayout_17.addWidget(self.frame_25)


        self.verticalLayout_15.addWidget(self.frame_19)


        self.verticalLayout_21.addWidget(self.kintone_page_body_frame)

        self.stackedWidget.addWidget(self.kintone_page)
        self.cloudia_evidence_page = QWidget()
        self.cloudia_evidence_page.setObjectName(u"cloudia_evidence_page")
        self.verticalLayout_31 = QVBoxLayout(self.cloudia_evidence_page)
        self.verticalLayout_31.setSpacing(8)
        self.verticalLayout_31.setObjectName(u"verticalLayout_31")
        self.verticalLayout_31.setContentsMargins(24, 24, 24, 24)
        self.statement_page_body_frame_2 = QFrame(self.cloudia_evidence_page)
        self.statement_page_body_frame_2.setObjectName(u"statement_page_body_frame_2")
        self.statement_page_body_frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.statement_page_body_frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_26 = QVBoxLayout(self.statement_page_body_frame_2)
        self.verticalLayout_26.setSpacing(16)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.verticalLayout_26.setContentsMargins(0, 0, 0, 0)
        self.frame_28 = QFrame(self.statement_page_body_frame_2)
        self.frame_28.setObjectName(u"frame_28")
        self.frame_28.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_28.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_27 = QVBoxLayout(self.frame_28)
        self.verticalLayout_27.setSpacing(0)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.verticalLayout_27.setContentsMargins(0, 0, 0, 0)
        self.app_title_5 = QLabel(self.frame_28)
        self.app_title_5.setObjectName(u"app_title_5")
        sizePolicy.setHeightForWidth(self.app_title_5.sizePolicy().hasHeightForWidth())
        self.app_title_5.setSizePolicy(sizePolicy)
        self.app_title_5.setFont(font)

        self.verticalLayout_27.addWidget(self.app_title_5)


        self.verticalLayout_26.addWidget(self.frame_28)

        self.frame_29 = QFrame(self.statement_page_body_frame_2)
        self.frame_29.setObjectName(u"frame_29")
        sizePolicy1.setHeightForWidth(self.frame_29.sizePolicy().hasHeightForWidth())
        self.frame_29.setSizePolicy(sizePolicy1)
        self.frame_29.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_29.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_28 = QVBoxLayout(self.frame_29)
        self.verticalLayout_28.setSpacing(8)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.verticalLayout_28.setContentsMargins(0, 0, 0, 0)
        self.frame_30 = QFrame(self.frame_29)
        self.frame_30.setObjectName(u"frame_30")
        sizePolicy2.setHeightForWidth(self.frame_30.sizePolicy().hasHeightForWidth())
        self.frame_30.setSizePolicy(sizePolicy2)
        self.frame_30.setFont(font1)
        self.frame_30.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_30.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_29 = QVBoxLayout(self.frame_30)
        self.verticalLayout_29.setSpacing(0)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.verticalLayout_29.setContentsMargins(0, 0, 0, 0)
        self.page_title_5 = QLabel(self.frame_30)
        self.page_title_5.setObjectName(u"page_title_5")
        self.page_title_5.setFont(font1)

        self.verticalLayout_29.addWidget(self.page_title_5)


        self.verticalLayout_28.addWidget(self.frame_30)

        self.grey_border_frame = QFrame(self.frame_29)
        self.grey_border_frame.setObjectName(u"grey_border_frame")
        sizePolicy2.setHeightForWidth(self.grey_border_frame.sizePolicy().hasHeightForWidth())
        self.grey_border_frame.setSizePolicy(sizePolicy2)
        self.grey_border_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.grey_border_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_30 = QVBoxLayout(self.grey_border_frame)
        self.verticalLayout_30.setSpacing(16)
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.verticalLayout_30.setContentsMargins(16, 16, 16, 16)
        self.frame_31 = QFrame(self.grey_border_frame)
        self.frame_31.setObjectName(u"frame_31")
        sizePolicy2.setHeightForWidth(self.frame_31.sizePolicy().hasHeightForWidth())
        self.frame_31.setSizePolicy(sizePolicy2)
        self.frame_31.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_31.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.frame_31)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.label_11 = QLabel(self.frame_31)
        self.label_11.setObjectName(u"label_11")
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)

        self.horizontalLayout_11.addWidget(self.label_11)


        self.verticalLayout_30.addWidget(self.frame_31)

        self.frame_34 = QFrame(self.grey_border_frame)
        self.frame_34.setObjectName(u"frame_34")
        sizePolicy2.setHeightForWidth(self.frame_34.sizePolicy().hasHeightForWidth())
        self.frame_34.setSizePolicy(sizePolicy2)
        self.frame_34.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_34.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_16 = QHBoxLayout(self.frame_34)
        self.horizontalLayout_16.setSpacing(8)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.unlock_file_button_2 = QPushButton(self.frame_34)
        self.unlock_file_button_2.setObjectName(u"unlock_file_button_2")

        self.horizontalLayout_16.addWidget(self.unlock_file_button_2)

        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_18)

        self.horizontalLayout_16.setStretch(0, 1)
        self.horizontalLayout_16.setStretch(1, 9)

        self.verticalLayout_30.addWidget(self.frame_34)


        self.verticalLayout_28.addWidget(self.grey_border_frame)

        self.frame_35 = QFrame(self.frame_29)
        self.frame_35.setObjectName(u"frame_35")
        self.frame_35.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_35.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_5 = QGridLayout(self.frame_35)
        self.gridLayout_5.setSpacing(16)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer_10 = QSpacerItem(20, 176, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer_10, 1, 3, 1, 1)

        self.verticalSpacer_9 = QSpacerItem(20, 176, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer_9, 1, 2, 1, 1)

        self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_5.addItem(self.horizontalSpacer_20, 0, 1, 1, 1)

        self.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_5.addItem(self.horizontalSpacer_19, 0, 2, 1, 1)

        self.back_to_kintone_page = QPushButton(self.frame_35)
        self.back_to_kintone_page.setObjectName(u"back_to_kintone_page")
        self.back_to_kintone_page.setMinimumSize(QSize(160, 0))

        self.gridLayout_5.addWidget(self.back_to_kintone_page, 0, 0, 1, 1)


        self.verticalLayout_28.addWidget(self.frame_35)


        self.verticalLayout_26.addWidget(self.frame_29)


        self.verticalLayout_31.addWidget(self.statement_page_body_frame_2)

        self.stackedWidget.addWidget(self.cloudia_evidence_page)

        self.verticalLayout.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(2)
        self.month_input_combo.setCurrentIndex(9)
        self.year_input_combo.setCurrentIndex(6)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Accounting Management ", None))
        self.app_title.setText(QCoreApplication.translate("MainWindow", u"ACCOUNTING MANAGEMENT", None))
        self.page_title.setText(QCoreApplication.translate("MainWindow", u"M-PESA STATEMENT", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Month", None))
        self.month_input_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"January", None))
        self.month_input_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"February", None))
        self.month_input_combo.setItemText(2, QCoreApplication.translate("MainWindow", u"March", None))
        self.month_input_combo.setItemText(3, QCoreApplication.translate("MainWindow", u"April", None))
        self.month_input_combo.setItemText(4, QCoreApplication.translate("MainWindow", u"May", None))
        self.month_input_combo.setItemText(5, QCoreApplication.translate("MainWindow", u"June", None))
        self.month_input_combo.setItemText(6, QCoreApplication.translate("MainWindow", u"July", None))
        self.month_input_combo.setItemText(7, QCoreApplication.translate("MainWindow", u"August", None))
        self.month_input_combo.setItemText(8, QCoreApplication.translate("MainWindow", u"September", None))
        self.month_input_combo.setItemText(9, QCoreApplication.translate("MainWindow", u"October", None))
        self.month_input_combo.setItemText(10, QCoreApplication.translate("MainWindow", u"November", None))
        self.month_input_combo.setItemText(11, QCoreApplication.translate("MainWindow", u"December", None))

        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Year", None))
        self.year_input_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"2020", None))
        self.year_input_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"2021", None))
        self.year_input_combo.setItemText(2, QCoreApplication.translate("MainWindow", u"2022", None))
        self.year_input_combo.setItemText(3, QCoreApplication.translate("MainWindow", u"2023", None))
        self.year_input_combo.setItemText(4, QCoreApplication.translate("MainWindow", u"2024", None))
        self.year_input_combo.setItemText(5, QCoreApplication.translate("MainWindow", u"2025", None))
        self.year_input_combo.setItemText(6, QCoreApplication.translate("MainWindow", u"2026", None))
        self.year_input_combo.setItemText(7, QCoreApplication.translate("MainWindow", u"2027", None))
        self.year_input_combo.setItemText(8, QCoreApplication.translate("MainWindow", u"2028", None))
        self.year_input_combo.setItemText(9, QCoreApplication.translate("MainWindow", u"2029", None))
        self.year_input_combo.setItemText(10, QCoreApplication.translate("MainWindow", u"2030", None))

        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Select M-Pesa Statement File", None))
        self.browse_statement_file_button.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Password", None))
        self.unlock_file_button.setText(QCoreApplication.translate("MainWindow", u"Unlock File and Capture", None))
        self.to_spreadsheet_page_button.setText(QCoreApplication.translate("MainWindow", u">>> Spreadsheet Records", None))
        self.app_title_2.setText(QCoreApplication.translate("MainWindow", u"ACCOUNTING MANAGEMENT", None))
        self.page_title_2.setText(QCoreApplication.translate("MainWindow", u"SPREADSHEET RECORDS", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Select Spreadsheet File", None))
        self.browse_spreadsheet_file_button.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.validate_file_button.setText(QCoreApplication.translate("MainWindow", u"Validate file and capture", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"M-Pesa Statement >>> Spreadsheet Records Reconciliation", None))
        self.reconcile_statement_spreadsheet_button.setText(QCoreApplication.translate("MainWindow", u"Reconcile", None))
        self.to_kintone_page.setText(QCoreApplication.translate("MainWindow", u">>> Kintone Records", None))
        self.back_to_statement_page.setText(QCoreApplication.translate("MainWindow", u"<<< M-Pesa Statement", None))
        self.app_title_3.setText(QCoreApplication.translate("MainWindow", u"ACCOUNTING MANAGEMENT", None))
        self.page_title_3.setText(QCoreApplication.translate("MainWindow", u"KINTONE RECORDS", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Spreadsheet Records >>> Kintone Reconciliation", None))
        self.reconcile_spreadsheet_kintone_button.setText(QCoreApplication.translate("MainWindow", u"Reconcile", None))
        self.to_cloudia_evidence_page.setText(QCoreApplication.translate("MainWindow", u">>> Cloudia Evidence", None))
        self.back_to_spreadsheet_page.setText(QCoreApplication.translate("MainWindow", u"<<< Spreadsheet Records", None))
        self.app_title_5.setText(QCoreApplication.translate("MainWindow", u"ACCOUNTING MANAGEMENT", None))
        self.page_title_5.setText(QCoreApplication.translate("MainWindow", u"CLOUDIA EVIDENCE", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Generate Cloudia evidence folder based on Kintone records", None))
        self.unlock_file_button_2.setText(QCoreApplication.translate("MainWindow", u"Generate", None))
        self.back_to_kintone_page.setText(QCoreApplication.translate("MainWindow", u"<<< Kintone Records", None))
    # retranslateUi

