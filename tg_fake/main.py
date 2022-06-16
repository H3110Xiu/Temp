from PyQt5.QtWidgets import QApplication, QStackedLayout
from PyQt5 import QtWidgets
from QCandyUi import CandyWindow

import sys

from qss.qss import qss

from ui.mainui import Ui_Form
from eventhandler import tgcollect
from eventhandler import tguserinfo
from eventhandler import tggroup
from eventhandler import tginvite
from eventhandler import tgprivate


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.pushButton_fun_collect.clicked.connect(self.show_panel)
        self.ui.pushButton_fun_get_user.clicked.connect(self.show_panel)
        self.ui.pushButton_fun_group_send.clicked.connect(self.show_panel)
        self.ui.pushButton_fun_private_send.clicked.connect(self.show_panel)
        self.ui.pushButton_fun_invite.clicked.connect(self.show_panel)

        # frame控件设置堆叠布局
        self.qsl = QStackedLayout(self.ui.frame)

        # 创建注册和筛选窗口
        private_send_widget = tgprivate.PrivateWindow()
        group_send_widget = tggroup.GroupWindow()
        collect_widget = tgcollect.CollectWindow()
        get_user_widget = tguserinfo.UserWindow()
        invite_widget = tginvite.InviteWindow()

        self.qsl.addWidget(private_send_widget)
        self.qsl.addWidget(group_send_widget)
        self.qsl.addWidget(collect_widget)
        self.qsl.addWidget(get_user_widget)
        self.qsl.addWidget(invite_widget)

        self.ui.pushButton_fun_private_send.setEnabled(False)

    def show_panel(self):
        dic = {
            "pushButton_fun_private_send": 0,
            "pushButton_fun_group_send": 1,
            "pushButton_fun_collect": 2,
            "pushButton_fun_get_user": 3,
            "pushButton_fun_invite": 4
        }
        btn = self.sender().objectName()
        if btn == "pushButton_fun_group_send":
            self.ui.pushButton_fun_group_send.setEnabled(False)
            self.ui.pushButton_fun_private_send.setEnabled(True)
            self.ui.pushButton_fun_collect.setEnabled(True)
            self.ui.pushButton_fun_get_user.setEnabled(True)
            self.ui.pushButton_fun_invite.setEnabled(True)
        if btn == "pushButton_fun_private_send":
            self.ui.pushButton_fun_group_send.setEnabled(True)
            self.ui.pushButton_fun_private_send.setEnabled(False)
            self.ui.pushButton_fun_collect.setEnabled(True)
            self.ui.pushButton_fun_get_user.setEnabled(True)
            self.ui.pushButton_fun_invite.setEnabled(True)
        if btn == "pushButton_fun_collect":
            self.ui.pushButton_fun_group_send.setEnabled(True)
            self.ui.pushButton_fun_private_send.setEnabled(True)
            self.ui.pushButton_fun_collect.setEnabled(False)
            self.ui.pushButton_fun_get_user.setEnabled(True)
            self.ui.pushButton_fun_invite.setEnabled(True)
        if btn == "pushButton_fun_get_user":
            self.ui.pushButton_fun_group_send.setEnabled(True)
            self.ui.pushButton_fun_private_send.setEnabled(True)
            self.ui.pushButton_fun_collect.setEnabled(True)
            self.ui.pushButton_fun_get_user.setEnabled(False)
            self.ui.pushButton_fun_invite.setEnabled(True)
        if btn == "pushButton_fun_invite":
            self.ui.pushButton_fun_group_send.setEnabled(True)
            self.ui.pushButton_fun_private_send.setEnabled(True)
            self.ui.pushButton_fun_collect.setEnabled(True)
            self.ui.pushButton_fun_get_user.setEnabled(True)
            self.ui.pushButton_fun_invite.setEnabled(False)
        index = dic[self.sender().objectName()]
        self.sender().setEnabled(False)
        self.qsl.setCurrentIndex(index)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()

    # style_path = "qss/Aqua.qss"
    # qss = LoadQss.read_qss(style_path)
    # main_window.setStyleSheet(qss)
    main_window = CandyWindow.createWindow(main_window, "customize", title="营销工具", ico_path=":ico/icon/telegram.ico")

    main_window.show()
    sys.exit(app.exec_())

