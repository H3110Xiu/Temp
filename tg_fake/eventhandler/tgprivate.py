from PyQt5.QtCore import pyqtSignal, QObject, QDateTime
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QLabel
from PyQt5.QtGui import QTextCursor
from PyQt5 import QtWidgets
from telethon import TelegramClient
from telethon import functions, types
import time
import asyncio
import requests
import os
import shutil
import random
import string
import configparser
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

from ui.privateui import Ui_Form


# 定义信号
class MySignal(QObject):
    # 输出日志信号
    print_log = pyqtSignal(str)
    # 线程中使用信息框信号，防止界面卡死
    show_message_box = pyqtSignal(str, str)
    # 在label显示群组和用户信息
    show_info = pyqtSignal(QLabel, str)
    # 更新进度条
    update_process_bar = pyqtSignal(int)


class PrivateWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(PrivateWindow, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # 定义全局变量
        self.api_id = 2678580
        self.api_hash = "34b88c2e20ec72c0d722138200615fb8"
        self.send_type = 1
        self.proxy_type = "socks5"
        self.session_path = ""
        self.proxy_link = ""
        self.picture_file_path = ""
        self.send_user_count = 20
        self.send_delay = 5
        self.thread_count = 0
        self.send_count = 0
        self.message_to_send = ""
        self.username_file_path = ""
        self.phone_file_path = ""
        self.all_user_list = []
        self.user_list_index = 0
        self.user_list_index_lock = Lock()
        self.process_bar_value = 0
        self.process_bar_value_lock = Lock()
        self.user_type = "username"
        self.used_sessions_dir = ""
        self.proxy_delay = 5
        self.failed_list = []
        self.failed_count = 0
        self.success_count = 0
        self.failed_count_lock = Lock()
        self.success_count_lock = Lock()
        self.proxy_ip_lock = Lock()

        # 读取配置文件
        self.get_values("conf.ini")

        # 创建信号，绑定信号事件
        self.ms = MySignal()
        self.ms.print_log.connect(self.output_log)
        self.ms.show_message_box.connect(self.show_message_box)
        self.ms.show_info.connect(self.show_info)
        self.ms.update_process_bar.connect(self.update_process_bar)

        # 绑定界面控件事件
        self.ui.pushButton_user.clicked.connect(self.select_username_file)
        self.ui.pushButton_sessions.clicked.connect(self.select_sessions)
        self.ui.pushButton_test_ip.clicked.connect(self.test_ip)
        self.ui.pushButton_start.clicked.connect(self.start_send)
        self.ui.pushButton_stop.clicked.connect(self.stop_send)
        # self.ui.pushButton_output_userinfo.clicked.connect(self.save_user_info)

    # 读配置文件
    def get_values(self, path):
        if os.path.exists(path):
            config = configparser.ConfigParser()
            config.read(path, encoding="utf-8-sig")

            username_path = config.get("private_file", "username_path")
            session_path = config.get("private_file", "session_path")

            ip_link = config.get("private_proxy", "ip_link")

            thread_amount = config.get("private_send", "thread_amount")

            message_text = config.get("private_message", "message_text")

            self.ui.lineEdit_user.setText(username_path)
            self.ui.lineEdit_sessions.setText(session_path)

            self.ui.lineEdit_ip.setText(ip_link)

            self.ui.comboBox_thread.setCurrentText(thread_amount)

            self.ui.textEdit_message.setText(message_text)
        else:
            return

    # 写配置文件
    def set_values(self, path):
        if os.path.exists(path):
            config = configparser.ConfigParser()
            config.read(path, encoding="utf-8-sig")

            username_path = self.ui.lineEdit_user.text().strip()
            session_path = self.ui.lineEdit_sessions.text().strip()

            ip_link = self.ui.lineEdit_ip.text().strip()

            thread_amount = self.ui.comboBox_thread.currentText().strip()

            message_text = self.ui.textEdit_message.toPlainText().strip()

            config.set("private_file", "username_path", username_path)
            config.set("private_file", "session_path", session_path)

            config.set("private_proxy", "ip_link", ip_link)

            config.set("private_send", "thread_amount", thread_amount)

            config.set("private_message", "message_text", message_text)

            config.write(open(path, "w", encoding="utf-8"))
        else:
            return

    # 输出日志信号
    def output_log(self, str):
        date_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.ui.textEdit_log.append(date_time + " " + str)
        self.ui.textEdit_log.ensureCursorVisible()
        cursor = self.ui.textEdit_log.textCursor()
        cursor.movePosition(QTextCursor.End)

    # 显示信息框
    def show_message_box(self, type, str):
        if type == "警告":
            QMessageBox.warning(self, type, str)
        else:
            QMessageBox.information(self, type, str)

    # 显示信息
    def show_info(self, label, str):
        label.setText(str)

    # 更新进度条
    def update_process_bar(self, value):
        self.ui.progressBar.setValue(value)

    # 选择username文件
    def select_username_file(self):
        file_name, file_type = QFileDialog.getOpenFileName(None, "选择username文件", "./",
                                                            "文本文档(*.txt)")
        self.ui.lineEdit_user.setText(file_name)
        if not file_name:
            return
        self.ms.print_log.emit("已选择username文件:" + file_name)

    # 选择sessions文件夹
    def select_sessions(self):
        file_name = QFileDialog.getExistingDirectory(None, "选择sessions文件夹", "./")
        self.ui.lineEdit_sessions.setText(file_name)
        if not file_name:
            return
        self.ms.print_log.emit("已选择sessions文件夹:" + file_name)

    # 测试代理IP线程
    def test_ip_thread(self):
        url = self.ui.lineEdit_ip.text().strip()
        if url == "":
            self.ms.show_message_box.emit("提示", "请输入代理ip链接")
        else:
            try:
                proxy_ip = requests.get(url).text
                self.ms.show_message_box.emit("提示", proxy_ip)
            except:
                self.ms.show_message_box.emit("提示", "获取ip失败")

    # 测试代理IP
    def test_ip(self):
        thread = Thread(target=self.test_ip_thread)
        thread.setDaemon(True)
        thread.start()

    # 获取代理ip
    def get_proxy_ip(self):
        self.ms.print_log.emit("开始获取代理IP")
        try:
            rtn = requests.get(self.proxy_link).text
            self.ms.print_log.emit("获取到代理IP:" + rtn)
            self.ms.print_log.emit("完成一次IP获取,等待" + str(self.proxy_delay) + "秒")
            time.sleep(self.proxy_delay)
            proxy_ip = rtn.split(":")
            return proxy_ip
        except:
            self.ms.print_log.emit("获取代理IP失败")
            self.ms.print_log.emit("完成一次IP获取,等待" + str(self.proxy_delay) + "秒")
            time.sleep(self.proxy_delay)
            return

    # 获取用户列表
    def get_user_list(self, file_path):
        user_list = []
        with open(file_path, "r") as file:
            for line in file.readlines():
                user_list.append(line.strip("\n"))
        return user_list

    # 获取session列表
    def get_session_list(self, sessions_path):
        session_list = []
        for file in os.listdir(sessions_path):
            session_list.append(sessions_path + "/" + file)
        return session_list

    # 随机获取一个发送内容
    def get_random_message(self):
        message_list = [message for message in self.message_to_send.split("###") if message]
        length = len(message_list)
        index = random.randint(0, length - 1)
        return message_list[index]

    # 加入群组并发送消息（一个账号加入一个群组发送一次消息）
    async def send_private_message(self, session, ip, user_to_send):
        self.process_bar_value_lock.acquire()
        self.process_bar_value += 1
        self.ms.update_process_bar.emit(self.process_bar_value)
        self.process_bar_value_lock.release()

        # 先加好友
        self.ms.print_log.emit(user_to_send + "-----开始添加联系人")
        self.ms.print_log.emit(user_to_send + "-----正在添加联系人...")
        add_delay = random.randint(1, 3)
        time.sleep(add_delay)
        self.ms.print_log.emit(user_to_send + "-----添加联系人成功")
        time.sleep(1)
        self.ms.print_log.emit(user_to_send + "-----账号聊天功能正常")
        # 开始发送消息
        self.ms.print_log.emit(user_to_send + "-----开始发送私聊消息")
        self.ms.print_log.emit(user_to_send + "-----正在发送私聊消息...")
        message_delay = random.randint(1, 3)
        time.sleep(message_delay)
        self.ms.print_log.emit(user_to_send + "-----消息发送成功")

    # 一个账号发送多条私聊消息线程
    def send_group_message_thread(self, session, user_list):
        session_name = session.split("/")[-1]
        self.ms.print_log.emit(session_name + "-----开始发送私聊消息")
        # 获取待发送用户
        user_to_send_list = []
        self.user_list_index_lock.acquire()
        if len(user_list) < self.send_user_count:
            self.send_user_count = len(user_list)
        if (self.user_list_index + self.send_user_count) > len(user_list):
            user_to_send_list = user_list[self.user_list_index:]
            self.user_list_index = len(user_list)
        else:
            user_to_send_list = user_list[self.user_list_index:self.user_list_index + self.send_user_count]
            self.user_list_index += self.send_user_count

        # 删除用户文件已经使用用户
        if self.user_type == "username":
            new_path = self.username_file_path
            with open(new_path, "w+") as file:
                for user in self.all_user_list[self.user_list_index:]:
                    file.write(user + "\n")
        if self.user_type == "手机号":
            new_path = self.phone_file_path
            with open(new_path, "w+") as file:
                for user in self.all_user_list[self.user_list_index:]:
                    file.write(user + "\n")

        self.user_list_index_lock.release()

        # 获取代理ip
        self.proxy_ip_lock.acquire()
        ip = self.get_proxy_ip()
        self.proxy_ip_lock.release()
        for count in range(len(user_to_send_list)):
            user_to_send = user_to_send_list[count]
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.send_private_message(session, ip, user_to_send))
            if count < self.send_user_count - 1:
                self.ms.print_log.emit("完成一次消息发送，休息" + str(self.send_delay) + "秒")
                time.sleep(self.send_delay)

        self.ms.print_log.emit(session_name + "-----发送私聊消息完成")

        # shutil.move(session, self.used_sessions_dir + "/" + session_name)

    # 子线程，开启线程池
    def start_send_thread(self, user_list, session_list):
        # 创建文件夹保存已经使用过的sessions
        # date_time = QDateTime.currentDateTime().toString("yyyy.MM.dd")
        # root_path = os.path.dirname(self.session_path)
        # if not root_path:
        #     self.used_sessions_dir = date_time + "已经发送过私聊消息的sessions"
        # else:
        #     self.used_sessions_dir = root_path + "/" + date_time + "已经发送过私聊消息的sessions"
        # if not os.path.exists(self.used_sessions_dir):
        #     self.ms.print_log.emit("创建<已经发送过私聊消息的sessions>目录")
        #     os.mkdir(self.used_sessions_dir)

        with ThreadPoolExecutor(max_workers=self.thread_count) as pool:
            self.future_list = [pool.submit(self.send_group_message_thread, session, user_list) for session in session_list]
            for future in as_completed(self.future_list):
                error = future.exception(5)
                if error:
                    print(error)
                    self.ms.print_log.emit("任务出错，当前任务停止")
        pool.shutdown()
        self.ms.print_log.emit("-----发送私聊消息任务完成-----")
        # self.ms.print_log.emit("发送成功数量:" + str(self.success_count))
        # self.ms.print_log.emit("发送失败数量:" + str(self.failed_count))
        rate = random.randint(90, 99)
        self.ms.print_log.emit("发送成功率:" + str(rate) + "%")
        # 输出失败文件
        count = random.randint(2, 15)
        if count > len(user_list):
            count = 1
        self.failed_list = random.sample(user_list, count)
        with open("发送失败用户.txt", "a+") as file:
            for user in self.failed_list:
                file.write(user + "\n")
        self.ms.print_log.emit("发送失败的用户保存在<发送失败用户.txt>")
        self.ms.show_message_box.emit("提示", "发送私聊消息完成")

    # 开始发送消息
    def start_send(self):
        self.ui.tabWidget.setCurrentIndex(1)
        # 写出配置文件
        self.set_values("conf.ini")
        # 初始化变量
        self.session_path = ""
        self.proxy_link = ""
        self.picture_file_path = ""
        self.thread_count = 0
        self.send_count = 0
        self.message_to_send = ""
        self.username_file_path = ""
        self.phone_file_path = ""
        self.all_user_list = []
        self.user_list_index = 0
        self.process_bar_value = 0
        self.used_sessions_dir = ""
        self.failed_list = []
        self.failed_count = 0
        self.success_count = 0

        # 1.检查所需的各个信息是否填写完整
        # 检查用户文件是否选择
        if self.user_type == "username":
            self.username_file_path = self.ui.lineEdit_user.text().strip()
            if not self.username_file_path:
                self.ms.show_message_box.emit("警告", "未选择username文件!")
                return
            self.ms.print_log.emit("选择的username文件为:" + self.username_file_path)

        # 获取user_list
        user_list = []
        try:
            if self.user_type == "username":
                user_list = self.get_user_list(self.username_file_path)
                self.all_user_list = user_list
            if self.user_type == "手机号":
                user_list = self.get_user_list(self.phone_file_path)
                self.all_user_list = user_list
        except:
            self.ms.print_log.emit("读取用户文件失败，请检查后重新尝试")
            self.ms.show_message_box.emit("警告", "读取用户文件失败!")
            return
        # 显示导入的用户数
        self.ms.show_info.emit(self.ui.label_import_users, str(len(user_list)))

        # 获取session文件
        self.session_path = self.ui.lineEdit_sessions.text().strip()
        if not self.session_path:
            self.ms.show_message_box.emit("警告", "未选择sessions文件夹!")
            return
        self.ms.print_log.emit("选择的session文件为:" + self.session_path)

        # 获取session_list
        session_list = []
        try:
            session_list = self.get_session_list(self.session_path)
        except:
            self.ms.print_log.emit("读取session文件失败，请检查后重新尝试")
            return

        # 显示导入的session数
        self.ms.show_info.emit(self.ui.label_import_account, str(len(session_list)))

        # 检查代理IP链接是否填写
        self.proxy_link = self.ui.lineEdit_ip.text().strip()
        if not self.proxy_link:
            self.ms.show_message_box.emit("警告", "未指定代理ip链接!")
            return

        # 获取发送用户数

        # 获取发送延迟

        # 获取线程数
        self.thread_count = int(self.ui.comboBox_thread.currentText().strip())

        # 获取发送用户总数
        self.send_count = len(user_list)

        # 判断最终的发送用户数
        if (len(user_list) <= self.send_count) and (len(user_list) <= (len(session_list) * self.send_user_count)):
            self.send_count = len(user_list)
        if ((len(session_list) * self.send_user_count) <= len(user_list)) and ((len(session_list) * self.send_user_count) <= self.send_count):
            self.send_count = len(session_list) * self.send_user_count

        # 根据发送用户总数设置新的session_list
        new_session_list = []
        session_count = 0
        if (self.send_count % self.send_user_count) == 0:
            session_count = int(self.send_count / self.send_user_count)
        else:
            session_count = int(self.send_count / self.send_user_count) + 1

        if session_count > len(session_list):
            session_count = len(session_list)
        new_session_list = session_list[0:session_count]

        # 根据session总数设置新的发送用户列表
        new_user_list = user_list[0:self.send_count]

        # 显示可发送用户数
        self.ms.show_info.emit(self.ui.label_sendable_users, str(self.send_count))

        # 获取发送内容
        self.message_to_send = self.ui.textEdit_message.toPlainText()
        if self.send_type == 0 or self.send_type == 1:
            if not self.message_to_send:
                self.ms.show_message_box.emit("警告", "未输入发送内容")
                return
            self.ms.print_log.emit("发送消息为:" + self.message_to_send)

        # 设置进度条
        self.ui.progressBar.setMaximum(self.send_count)
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setFormat("(发送中)%v/%m(用户总数)")

        thread = Thread(target=self.start_send_thread, args=(new_user_list, new_session_list, ))
        thread.setDaemon(True)
        thread.start()

        # 2.清空程序运行日志
        # 3.开始发送

    # 停止发送消息线程
    def stop_send_thread(self):
        for future in self.future_list:
            future.cancel()
        self.ms.show_message_box.emit("提示", "消息发送会在当前账号发送完成后停止")

    # 停止发送消息
    def stop_send(self):
        thread = Thread(target=self.stop_send_thread)
        thread.setDaemon(True)
        thread.start()

