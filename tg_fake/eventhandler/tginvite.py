from PyQt5.QtCore import pyqtSignal, QObject, QDateTime
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QLabel
from PyQt5.QtGui import QTextCursor
from PyQt5 import QtWidgets
from telethon import TelegramClient
from telethon import functions, types
from telethon import errors
from telethon.tl.types import InputPeerUser
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

from ui.inviteui import Ui_Form
from operate.excel_operate import MyExcel


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


class InviteWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(InviteWindow, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # 定义全局变量
        self.api_id = 2678580
        self.api_hash = "34b88c2e20ec72c0d722138200615fb8"
        self.proxy_type = "socks5"
        self.session_path = ""
        self.proxy_link = ""
        self.invite_user_count = 20
        self.invite_delay = 5
        self.thread_count = 0
        self.invite_count = 0
        self.username_file_path = ""
        self.phone_file_path = ""
        self.all_user_list = []
        self.user_list_index = 0
        self.user_list_index_lock = Lock()
        self.process_bar_value = 0
        self.process_bar_value_lock = Lock()
        self.user_type = "username"
        self.used_sessions_dir = ""
        self.group_url = ""
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
        # self.ui.pushButton_picture.clicked.connect(self.select_picture)
        self.ui.pushButton_sessions.clicked.connect(self.select_sessions)
        self.ui.pushButton_test_ip.clicked.connect(self.test_ip)
        self.ui.pushButton_start.clicked.connect(self.start_invite)
        self.ui.pushButton_stop.clicked.connect(self.stop_send)
        # self.ui.pushButton_output_userinfo.clicked.connect(self.save_user_info)

    # 读配置文件
    def get_values(self, path):
        if os.path.exists(path):
            config = configparser.ConfigParser()
            config.read(path, encoding="utf-8-sig")

            username_path = config.get("invite_file", "username_path")
            session_path = config.get("invite_file", "session_path")

            group_url = config.get("invite_invite", "group_url")
            thread_amount = config.get("invite_invite", "thread_amount")

            ip_link = config.get("invite_proxy", "ip_link")

            self.ui.lineEdit_user.setText(username_path)
            self.ui.lineEdit_sessions.setText(session_path)

            self.ui.lineEdit_group_url.setText(group_url)
            self.ui.comboBox_thread.setCurrentText(thread_amount)

            self.ui.lineEdit_ip.setText(ip_link)
        else:
            return

    # 写配置文件
    def set_values(self, path):
        if os.path.exists(path):
            config = configparser.ConfigParser()
            config.read(path, encoding="utf-8-sig")

            username_path = self.ui.lineEdit_user.text().strip()
            session_path = self.ui.lineEdit_sessions.text().strip()

            group_url = self.ui.lineEdit_group_url.text().strip()
            thread_amount = self.ui.comboBox_thread.currentText().strip()

            ip_link = self.ui.lineEdit_ip.text().strip()

            config.set("invite_file", "username_path", username_path)
            config.set("invite_file", "session_path", session_path)

            config.set("invite_invite", "group_url", group_url)
            config.set("invite_invite", "thread_amount", thread_amount)

            config.set("invite_proxy", "ip_link", ip_link)

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

    # 加入群组并邀请用户（一个账号加入一个群组邀请一组用户）
    async def invite_user_to_group(self, session, user_to_invite_list):
        session_name = session.split("/")[-1]
        if self.user_type == "username":
            flag = 3
            while flag:
                self.proxy_ip_lock.acquire()
                ip = self.get_proxy_ip()
                self.proxy_ip_lock.release()
                self.ms.print_log.emit(session_name + "-----正在登录...")
                try:
                    async with TelegramClient(session, self.api_id, self.api_hash,
                                          proxy=(self.proxy_type, ip[0], int(ip[1]))) as client:
                        # 加入群组
                        self.ms.print_log.emit(session_name + "-----登录成功")
                        self.ms.print_log.emit(session_name + "-----正在加入群组...")
                        try:
                            join_ret = await client(functions.channels.JoinChannelRequest(
                                channel=self.group_url
                            ))
                            if join_ret:
                                self.ms.print_log.emit(session_name + "-----加入群组成功")
                        except errors.ChannelBannedError:
                            self.ms.print_log.emit(session_name + "-----加入群组失败，群组被封禁")
                            return
                        except errors.ChannelInvalidError:
                            self.ms.print_log.emit(session_name + "-----加入群组失败，无效群组")
                            return
                        except errors.ChannelPrivateError:
                            self.ms.print_log.emit(session_name + "-----加入群组失败，私有群组，没有访问权限")
                            return
                        except errors.ChannelsTooMuchError:
                            self.ms.print_log.emit(session_name + "-----加入群组失败，加入过多群组")
                            return
                        except:
                            self.ms.print_log.emit(session_name + "-----加入群组失败")
                            return

                        self.ms.print_log.emit(session_name + "-----开始邀请用户进群")
                        self.ms.print_log.emit(session_name + "-----正在邀请用户进群...")
                        for user in user_to_invite_list:
                            # 更新进度条
                            self.process_bar_value_lock.acquire()
                            self.process_bar_value += 1
                            self.ms.update_process_bar.emit(self.process_bar_value)
                            self.process_bar_value_lock.release()
                            try:
                                invite_ret = await client(functions.channels.InviteToChannelRequest(
                                    channel=self.group_url,
                                    users=[user]
                                ))
                                if invite_ret:
                                    self.ms.print_log.emit(user + "-----邀请用户进群成功")
                                    self.success_count_lock.acquire()
                                    self.success_count += 1
                                    self.success_count_lock.release()
                                else:
                                    self.ms.print_log.emit(user + "-----邀请用户进群失败")
                                    self.failed_list.append(user)
                                    self.failed_count_lock.acquire()
                                    self.failed_count += 1
                                    self.failed_count_lock.release()
                                    continue
                                if user != user_to_invite_list[-1]:
                                    self.ms.print_log.emit("完成一次用户邀请，休息" + str(self.invite_delay) + "秒")
                                    time.sleep(self.invite_delay)
                            except Exception as e:
                                self.ms.print_log.emit(user + "-----邀请用户进群失败")
                                self.failed_list.append(user)
                                self.failed_count_lock.acquire()
                                self.failed_count += 1
                                self.failed_count_lock.release()
                                continue
                        return

                except Exception as e:
                    flag -= 1
                    print(e)
                    self.ms.print_log.emit(session_name + "-----登录账号失败")
                    self.ms.print_log.emit(session_name + "-----邀请用户进群失败")
                    continue

        if self.user_type == "手机号":
            flag_p = 3
            while flag_p:
                self.proxy_ip_lock.acquire()
                ip = self.get_proxy_ip()
                self.proxy_ip_lock.release()
                self.ms.print_log.emit(session_name + "-----正在登录...")
                try:
                    async with TelegramClient(session, self.api_id, self.api_hash,
                                          proxy=(self.proxy_type, ip[0], int(ip[1]))) as client:
                        # 先加好友
                        self.ms.print_log.emit(session_name + "-----登录成功")

                        # 加入群组
                        self.ms.print_log.emit(session_name + "-----正在加入群组...")
                        try:
                            ret = await client(functions.channels.JoinChannelRequest(
                                channel=self.group_url
                            ))
                            if ret:
                                self.ms.print_log.emit(session_name + "-----加入群组成功")
                            else:
                                self.ms.print_log.emit(session_name + "-----加入群组失败")
                                return
                        except errors.ChannelBannedError:
                            self.ms.print_log.emit(session_name + "-----加入群组失败，群组被封禁")
                            return
                        except errors.ChannelInvalidError:
                            self.ms.print_log.emit(session_name + "-----加入群组失败，无效群组")
                            return
                        except errors.ChannelPrivateError:
                            self.ms.print_log.emit(session_name + "-----加入群组失败，私有群组，没有访问权限")
                            return
                        except errors.ChannelsTooMuchError:
                            self.ms.print_log.emit(session_name + "-----加入群组失败，加入过多群组")
                            return
                        except:
                            self.ms.print_log.emit(session_name + "-----加入群组失败")
                            return

                        # 添加联系人
                        self.ms.print_log.emit(session_name + "-----开始添加联系人")
                        self.ms.print_log.emit(session_name + "-----正在添加联系人...")

                        for user in user_to_invite_list:
                            # 更新进度条
                            self.process_bar_value_lock.acquire()
                            self.process_bar_value += 1
                            self.ms.update_process_bar.emit(self.process_bar_value)
                            self.process_bar_value_lock.release()

                            # 添加联系人
                            try:
                                result = await client(functions.contacts.ImportContactsRequest(
                                    contacts=[types.InputPhoneContact(
                                        client_id=random.randrange(-2**63, 2**63),
                                        phone=user,
                                        first_name="".join(random.sample(string.ascii_lowercase, 5)),
                                        last_name=''.join(random.sample(string.ascii_lowercase, 5))
                                    )]
                                ))
                                if result.imported:
                                    self.ms.print_log.emit(session_name + "-----添加联系人成功")
                                    # 邀请用户进群
                                    try:
                                        invite_ret = await client(functions.channels.InviteToChannelRequest(
                                            channel=self.group_url,
                                            users=[user]
                                        ))
                                        if invite_ret:
                                            self.ms.print_log.emit(user + "-----邀请用户进群成功")
                                            self.success_count_lock.acquire()
                                            self.success_count += 1
                                            self.success_count_lock.release()
                                        else:
                                            self.ms.print_log.emit(user + "-----邀请用户进群失败")
                                            self.failed_list.append(user)
                                            self.failed_count_lock.acquire()
                                            self.failed_count += 1
                                            self.failed_count_lock.release()
                                            continue
                                        if user != user_to_invite_list[-1]:
                                            self.ms.print_log.emit("完成一次用户邀请，休息" + str(self.invite_delay) + "秒")
                                            time.sleep(self.invite_delay)
                                    except Exception as e:
                                        self.ms.print_log.emit(user + "-----邀请用户进群失败")
                                        self.failed_list.append(user)
                                        self.failed_count_lock.acquire()
                                        self.failed_count += 1
                                        self.failed_count_lock.release()
                                        continue

                                else:
                                    self.ms.print_log.emit(session_name + "-----添加联系人失败")
                                    self.ms.print_log.emit(session_name + "-----邀请用户进群失败")
                                    self.failed_list.append(user)
                                    self.failed_count_lock.acquire()
                                    self.failed_count += 1
                                    self.failed_count_lock.release()
                                    continue
                            except:
                                self.ms.print_log.emit(session_name + "-----添加联系人失败")
                                self.ms.print_log.emit(session_name + "-----邀请用户进群失败")
                                self.failed_list.append(user)
                                self.failed_count_lock.acquire()
                                self.failed_count += 1
                                self.failed_count_lock.release()
                                continue
                        return

                except:
                    flag_p -= 1
                    self.ms.print_log.emit(session_name + "-----登录账号失败")
                    self.ms.print_log.emit(session_name + "-----邀请用户进群失败")
                    continue

    # 一个账号邀请用户进群线程
    def invite_to_group_thread(self, session, user_list):
        session_name = session.split("/")[-1]
        self.ms.print_log.emit(session_name + "-----开始邀请用户进群任务")
        # 获取待邀请用户
        user_to_invite_list = []
        self.user_list_index_lock.acquire()
        if len(user_list) < self.invite_user_count:
            self.invite_user_count = len(user_list)
        if (self.user_list_index + self.invite_user_count) > len(user_list):
            user_to_invite_list = user_list[self.user_list_index:]
            self.user_list_index = len(user_list)
        else:
            user_to_invite_list = user_list[self.user_list_index:self.user_list_index + self.invite_user_count]
            self.user_list_index += self.invite_user_count

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

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.invite_user_to_group(session, user_to_invite_list))

        self.ms.print_log.emit(session_name + "-----邀请用户进群完成")
        time.sleep(2)
        shutil.move(session, self.used_sessions_dir + "/" + session_name)

    # 子线程，开启线程池
    def start_invite_thread(self, user_list, session_list):
        # 创建文件夹保存已经使用过的sessions
        date_time = QDateTime.currentDateTime().toString("yyyy.MM.dd")
        root_path = os.path.dirname(self.session_path)
        if not root_path:
            self.used_sessions_dir = date_time + "已经邀请过用户的sessions"
        else:
            self.used_sessions_dir = root_path + "/" + date_time + "已经邀请过用户的sessions"
        if not os.path.exists(self.used_sessions_dir):
            self.ms.print_log.emit("创建<已经邀请过用户的sessions>目录")
            os.mkdir(self.used_sessions_dir)

        with ThreadPoolExecutor(max_workers=self.thread_count) as pool:
            self.future_list = [pool.submit(self.invite_to_group_thread, session, user_list) for session in session_list]
            for future in as_completed(self.future_list):
                error = future.exception(5)
                if error:
                    print(error)
                    self.ms.print_log.emit("任务出错，当前任务停止")
        pool.shutdown()
        self.ms.print_log.emit("-----发送私聊消息任务完成-----")
        self.ms.print_log.emit("邀请成功数量:" + str(self.success_count))
        self.ms.print_log.emit("邀请失败数量:" + str(self.failed_count))
        # 输出失败文件
        with open("邀请失败用户.txt", "a+") as file:
            for user in self.failed_list:
                file.write(user + "\n")
        self.ms.print_log.emit("邀请失败的用户保存在<邀请失败用户.txt>")
        self.ms.show_message_box.emit("提示", "邀请用户进群完成")

    # 开始发送消息
    def start_invite(self):
        self.ui.tabWidget.setCurrentIndex(1)
        # 写出配置文件
        self.set_values("conf.ini")
        # 初始化变量
        self.session_path = ""
        self.proxy_link = ""
        self.thread_count = 0
        self.username_file_path = ""
        self.phone_file_path = ""
        self.all_user_list = []
        self.user_list_index = 0
        self.process_bar_value = 0
        self.used_sessions_dir = ""
        self.group_url = ""
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

        # 检查群组链接是否填写
        self.group_url = self.ui.lineEdit_group_url.text().strip()
        if not self.group_url:
            self.ms.show_message_box.emit("警告", "未指定群组链接!")
            return

        # 检查代理IP链接是否填写
        self.proxy_link = self.ui.lineEdit_ip.text().strip()
        if not self.proxy_link:
            self.ms.show_message_box.emit("警告", "未指定代理ip链接!")
            return

        # 获取线程数
        self.thread_count = int(self.ui.comboBox_thread.currentText().strip())

        # 获取邀请用户总数
        self.invite_count = len(user_list)

        # 判断最终的邀请用户数
        if (len(user_list) <= self.invite_count) and (len(user_list) <= (len(session_list) * self.invite_user_count)):
            self.invite_count = len(user_list)
        if ((len(session_list) * self.invite_user_count) <= len(user_list)) and ((len(session_list) * self.invite_user_count) <= self.invite_count):
            self.invite_count = len(session_list) * self.invite_user_count

        # 根据发送用户总数设置新的session_list
        new_session_list = []
        session_count = 0
        if (self.invite_count % self.invite_user_count) == 0:
            session_count = int(self.invite_count / self.invite_user_count)
        else:
            session_count = int(self.invite_count / self.invite_user_count) + 1

        if session_count > len(session_list):
            session_count = len(session_list)
        new_session_list = session_list[0:session_count]

        # 根据session总数设置新的发送用户列表
        new_user_list = user_list[0:self.invite_count]

        # 显示可发送用户数
        self.ms.show_info.emit(self.ui.label_inviteable_users, str(self.invite_count))

        # 设置进度条
        self.ui.progressBar.setMaximum(self.invite_count)
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setFormat("(邀请中)%v/%m(用户总数)")

        thread = Thread(target=self.start_invite_thread, args=(new_user_list, new_session_list,))
        thread.setDaemon(True)
        thread.start()

    # 停止发送消息线程
    def stop_invite_thread(self):
        for future in self.future_list:
            future.cancel()
        self.ms.show_message_box.emit("提示", "用户邀请会在当前账号发送完成后停止")

    # 停止发送消息
    def stop_send(self):
        thread = Thread(target=self.stop_invite_thread)
        thread.setDaemon(True)
        thread.start()

