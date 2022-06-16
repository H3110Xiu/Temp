import requests
import time
import asyncio


class MyPhoneDefu:
    def __init__(self, username, password):
        '''
        # 初始化
        :param username:
        :param password:
        '''
        self.username = username
        self.password = password
        self.token = ''

    def login(self):
        '''
        # 用户登录
        :return: 成功返回token，失败返回'error'
        '''
        url = r'http://cf.do668.com:81/api/logins?username=' + self.username + '&password=' + self.password
        rtn = requests.get(url).json()
        message = rtn['message']

        if message == '登录成功':
            token = rtn['token']
            self.token = token
            return token
        else:
            return 'error'

    def get_balance(self):
        '''
        # 获取余额
        :param token:
        :return: 成功返回余额，失败返回'error'
        '''
        url = r'http://cf.do668.com:81/api/get_myinfo?token=' + self.token
        rtn = requests.get(url).json()
        message = rtn['message']

        if message == 'ok':
            balance = rtn['data'][0]['money']
            return balance
        else:
            return 'error'

    def get_phone(self, project_id, loop='1', operator='', phone_num='',
                  scope='', address='', api_id='67672', scope_black=''):
        '''
        # 获取手机号
        :param token:登录返回的token
        :param project_id:项目ID.普通项目填普通项目的ID，专属类型填写专属项目的对接码
        :param loop:是否过滤项目 1过滤 2不过滤 默认不过滤
        :param operator:运营商 (0=默认 1=移动 2=联通 3=电信 4=实卡 5=虚卡) 可空
        :param phone_num:指定取号的话 这里填要取的手机号
        :param scope:指定号段 最多支持号码前5位. 例如可以为165，也可以为16511
        :param address:归属地选择 例如 湖北 甘肃 不需要带省字
        :param api_id:如果是开发者,此处填写你的用户ID才有收益，注意是用户ID不是登录账号
        :param scope_black:排除号段最长支持7位且可以支持多个,最多支持20个号段。用逗号分隔 比如150,1511111,15522
        :return:成功返回手机号，失败返回'error'
        '''
        url = r'http://cf.do668.com:81/api/get_mobile?token=' + self.token + '&project_id=' + project_id \
              + '&loop=' + loop +  '&operator=' + operator + '&phone_num=' + phone_num + '&scope=' + \
              scope + '&address=' + address + '&api_id=' + api_id + '&scope_black=' + scope_black
        rtn = requests.get(url).json()
        print(rtn)
        message = rtn['message']

        if message == 'ok':
            mobile = rtn['mobile']
            return mobile
        else:
            return 'error'

    def get_code(self, project_id, phone_num):
        '''
        # 获取验证码
        :param project_id:
        :param phone_num:
        :return: 成功返回验证码，失败返回'error'
        '''
        url = r'http://cf.do668.com:81/api/get_message?token=' + self.token + '&project_id=' + \
              project_id + '&phone_num=' + phone_num

        count = 0
        while True:
            rtn = requests.get(url).json()
            message = rtn['message']
            data = rtn['data']
            print(rtn)

            if message == '短信还未到达,请继续获取':
                count += 1
                time.sleep(1)
                if count >= 30:
                    return 'error'
                continue
            elif message == 'ok':
                code = rtn['code']
                return code
            else:
                return 'error'

    def release_phone(self, phone_num=''):
        '''
        # 释放手机号
        :param phone_num: 为空，则释放全部
        :return: 成功返回'success'，失败返回'error'
        '''
        url = r'http://cf.do668.com:81/api/free_mobile?token=' + self.token + '&phone_num=' + phone_num
        rtn = requests.get(url).json()
        message = rtn['message']

        if message == 'ok':
            return 'success'
        else:
            return 'error'

    def add_blacklist(self, project_id, phone_num):
        '''
        # 加黑号码
        :param project_id:
        :param phone_num:
        :return: 成功返回'success'，失败返回'error'
        '''
        url = r'http://cf.do668.com:81/api/add_blacklist?token=' + self.token + '&project_id=' + \
              project_id + '&phone_num=' + phone_num
        rtn = requests.get(url).json()
        message = rtn['message']

        if message == '拉黑成功':
            return 'success'
        else:
            return 'error'

    # def get_exclusive(self):
    #     url = r'http://cf.do668.com:81/api/api/get_exclusive?token=' + self.token
    #     rtn = requests.get(url)
    #     print(rtn)

class MyPhoneNaicha:
    def __init__(self, api_name, password):
        self.api_name = api_name
        self.password = password
        self.token = ''

    def login(self):
        url = r"http://web.szjct888.com/yhapi.ashx?act=login&ApiName=" + self.api_name + "&PassWord=" + self.password
        rtn = ""
        try:
            rtn = requests.get(url, timeout=30).text
        except:
            rtn = "server error"
            return rtn

        state = rtn.split("|")[0]
        if state == "1":
            self.token = rtn.split("|")[1]
            return "success"
        else:
            return "error"

    def get_info(self):
        url = r"http://web.szjct888.com/yhapi.ashx?act=myInfo&token=" + self.token
        rtn = requests.get(url).text
        state = rtn.split("|")[0]
        if state == "1":
            balance = rtn.split("|")[1]
            level = rtn.split("|")[2]
            integral = rtn.split("|")[3]
            return balance, level, integral
        else:
            return "error"

    def get_phone(self, iid, seq, did="fb18e95c6de055ab1c488796a0727bf8_142", operator="", provi="", city="", mobile=""):
        '''
        :param iid:项目ID，在用户端查看
        :param seq:号段选择，0 或 1 或 2；0代表不限号段，1代表只获取虚拟号段，2代表只获取正常号段
        :param did:开发者ID
        :param operator:运营商，汉字请url编码
        :param provi:归属地-省，汉字请url编码
        :param city:归属地-市，汉字请url编码
        :param mobile:获取指定的手机号
        :return:
        '''
        url = r"http://web.szjct888.com/yhapi.ashx?act=getPhone&token=" + self.token + "&iid=" + iid + "&did=" + did + \
              "&operator=" + operator + "&provi=" + provi + "&city=" + city + "&seq=" + seq + "&mobile=" +mobile
        rtn = requests.get(url).text
        state = rtn.split("|")[0]
        if state == "1":
            phone = rtn.split("|")[3]
            return phone
        else:
            return "error"

    def get_code(self, iid, mobile):
        url = "http://web.szjct888.com/yhapi.ashx?act=getPhoneCode&token=" + self.token + "&iid=" + iid + "&mobile=" + mobile
        count = 0
        while True:
            rtn = requests.get(url).text
            state = rtn.split("|")[0]
            print(rtn)

            if state == "1":
                code = rtn.split("|")[1]
                return code
            else:
                count += 1
                time.sleep(1)
                if count >= 45:
                    return "error"

    def release_phone(self, iid, mobile):
        url = "http://web.szjct888.com/yhapi.ashx?act=setRel&token=" + self.token + "&iid=" + iid + "&mobile=" + mobile
        rtn = requests.get(url).text
        print(rtn)
        state = rtn[0]
        if state == "1":
            return "success"
        else:
            return "error"

    def add_blacklist(self, iid, mobile, reason="used"):
        url = "http://web.szjct888.com/yhapi.ashx?act=addBlack&token=" + self.token + "&iid=" + iid + "&mobile=" + \
              mobile + "&reason=" + reason
        rtn = requests.get(url).text
        state = rtn[0]
        if state == "1":
            return "success"
        else:
            return "error"


# 发发接码平台
class MyPhoneFafa:
    # 使用token直接获取相关信息
    def __init__(self, token="7feab548b90c76a2f92b2c408199cc26", business_code="T10020AM12"):
        self.token = token
        self.project_id = business_code

    # 获取手机号
    def get_phone(self, country=""):
        url = r"http://www.sesames.online/outsideapi/gpmni?token=" + self.token + \
              "&business_code=" + self.project_id + "&country=" + country
        try:
            rtn = requests.get(url).json()
        except:
            print("可能是网络原因导致出错")
            return "error"
        print(rtn)
        code = rtn["code"]
        message = rtn["message"]

        if code == "200" and message == "success":
            phone_number = rtn['data']['phone_number_group'][0]['phone_number']
            order_id = rtn['data']['phone_number_group'][0]['order_id']
            return phone_number, order_id
        else:
            return "error"

    # 获取验证码
    def get_code(self, order_id):
        url = "http://www.sesames.online/outsideapi/gvc?token=" + self.token + \
              "&order_id=" + order_id

        count = 0
        while True:
            rtn = requests.get(url).json()
            code = rtn["code"]

            if code == "200":
                verification_code = rtn["data"]["verification_code"]
                if verification_code:
                    return verification_code
                else:
                    count += 1
                    time.sleep(1)
                    print("正在获取验证码...")
                    if count >= 45:
                        return "error"
            else:
                return "error"

    # 获取国家号码数量
    def get_country_phone_count(self):
        url = r"http://www.sesames.online/outsideapi/gMenu?token=" + self.token + \
              "&business_code=" + self.project_id
        country_num = []
        rtn = requests.get(url).json()
        print(rtn)
        code = rtn["code"]
        if code == "200":
            data = rtn["data"]
            for line in data:
                country_num.append((line["country"], line["number"]))
            return country_num
        else:
            return "error"


# 柠檬接码平台
class MyPhoneNingmeng:
    def __init__(self, username, password, proxies):
        self.username = username
        self.password = password
        self.proxies = proxies

    def get_score(self):
        url = r"http://opapi.smspva.net/out/ext_api/getUserInfo?name=" + self.username + \
              "&pwd=" + self.password
        try:
            rtn = requests.get(url, proxies=self.proxies).json()
        except Exception as e:
            print("出错，可能由于网络原因")
            return "error"
        print(rtn)
        code = rtn["code"]
        if code == 200:
            score = str(rtn["data"]["score"])
            return score
        else:
            return "error"

    def get_phone(self, cuy, pid, num="1", noblack="1", serial="2"):
        '''
        name：用户名*
        pwd：用户密码*
        cuy：国家代码(二位缩写，不必须，默认所有国家)查看
        pex：过滤号码前缀。格式：86135，国家代码(86，参照cuy国家代码)+前缀(135)，总长度：2-6位
        pid：项目ID*
        num：获取手机号条数（1-10）*
        noblack：过滤黑名单规则（0，1）：0:只过滤自己添加的黑名单，1:过滤所有用户添加的黑名单*
        serial：是否多条(1:为多条,2为单条)*
        secret_key：特殊项目参数,如需添加联系管理员.否则为空*
        vip：vip专属通道*
        '''
        url = r"http://opapi.smspva.net/out/ext_api/getMobile?name=" + self.username + \
              "&pwd=" + self.password + "&cuy="+ cuy +"&pid=" + pid + "&num=" + num + \
              "&noblack=" + noblack + "&serial=" + serial + "&secret_key=null&vip=null"
        rtn = requests.get(url, proxies=self.proxies).json()
        print(rtn)
        code = rtn["code"]
        if code == 200:
            phone = rtn["data"]
            return phone
        else:
            return "error"

    def get_code(self, phone, pid, serial="2"):
        url = "http://opapi.smspva.net/out/ext_api/getMsg?name=" + self.username + "&pwd=" + \
              self.password + "&pn=" + phone + "&pid=" + pid + "&serial=" + serial
        count = 0
        while True:
            rtn = requests.get(url, proxies=self.proxies).json()
            print(rtn)
            code = rtn["code"]
            print("正在获取验证码...")
            if code == 200:
                data = rtn["data"]
                return data
            elif code == 908:
                count += 1
                time.sleep(1)
                if count >= 45:
                    return "error"
            else:
                return "error"

    def release_phone(self, phone, pid, serial="2"):
        url = "http://opapi.smspva.net/out/ext_api/passMobile?name=" + self.username + "&pwd=" + \
              self.password + "&pn=" + phone + "&pid=" + pid + "&serial=" + serial
        rtn = requests.get(url, proxies=self.proxies).json()
        print(rtn)
        code = rtn["code"]
        if code == 200:
            return "success"
        else:
            return "error"

    def add_blacklist(self, phone, pid):
        url = "http://opapi.smspva.net/out/ext_api/addBlack?name=" + self.username + "&pwd=" + \
              self.password + "&pn=" + phone + "&pid=" + pid
        rtn = requests.get(url, proxies=self.proxies).json()
        print(rtn)
        code = rtn["code"]
        if code == 200:
            return "success"
        else:
            return "error"

    def get_country_phone_count(self, pid):
        url = "http://opapi.smspva.net/out/ext_api/getCountryPhoneNum?name=" + self.username + \
              "&pwd=" + self.password + "&pid=" + pid + "&vip=null"
        rtn = requests.get(url, proxies=self.proxies).json()
        code = rtn["code"]
        if code == 200:
            data = rtn["data"]
            return data
        else:
            return "error"

if __name__ == '__main__':
    pass
    # proxies = {'http': 'socks5://127.0.0.1:10808', 'https': 'socks5://127.0.0.1:10808'}

    # my_phone = MyPhoneNingmeng("jay5260", "jay526060", proxies)
    # country = my_phone.get_country_phone_count("0257")
    # print(country)
    # score = my_phone.get_info()
    # print(score)
    # phone = my_phone.get_phone("so", "0257")
    # print(phone)
    # time.sleep(5)
    # rtn = my_phone.release_phone(phone, "0257")
    # print(rtn)
    #
    # rtn = my_phone.add_blacklist(phone, "0257")
    # print(rtn)
    # flag = input("输入选项:")
    # if flag == "1":
    #     code = my_phone.get_code(phone, "0257")
    #     print(code)



    # # 测试发发
    # my_phone = MyPhoneFafa()
    # data = my_phone.get_country_phone_count()
    # print(data)
    # phone = my_phone.get_phone()
    # print(phone)
    # choice = input("请输入选项：")
    # if choice == "1":
    #     code = my_phone.get_code(phone[1])
    #     print(code)



    # # 德芙验证
    # phone = MyPhoneDefu('dajiahao123', 'asd123654')
    # token = phone.login()
    # print(token)
    # balance = phone.get_balance()
    # print('余额:' + balance)
    # while True:
    #     mobile = phone.get_phone('19949', '1', '4', api_id='67672')
    #     print(mobile)
    #     temp = input('输入:')
    #     if temp == '1':
    #         print("----------开始获取验证码----------")
    #         code = phone.get_code('19949', mobile)
    #         print("验证码:",code)
    #     elif temp == '0':
    #         black = phone.add_blacklist('19949', mobile)
    #         print('拉黑结果:' + black)
    #     else:
    #         release = phone.release_phone(mobile)
    #         if release == "success":
    #             print("释放成功")
    #         break

    # phone = MyPhoneNaicha("dajiahao12352", "asd123654")
    # token = phone.login()
    # print(token)

    # 测试加黑名单后释放
    # mobile = phone.get_phone("1135", "2")
    # print(mobile)
    # time.sleep(20)
    # black_ret = phone.add_blacklist('1135', mobile)
    # print(black_ret)
    # time.sleep(20)
    # release_ret = phone.release_phone("1135", mobile)
    # print(release_ret)


    # info = phone.get_info()
    # balance = info[0]
    # print(balance)
    #
    # while True:
    #     mobile = phone.get_phone()
    #     print(mobile)
    #     temp = input('输入:')
    #     if temp == '1':
    #         print("----------开始获取验证码----------")
    #         code = phone.get_code('1135', mobile)
    #         print("验证码:",code)
    #     elif temp == '0':
    #         black = phone.add_blacklist('1135', mobile)
    #         print('拉黑结果:' + black)
    #     else:
    #         release = phone.release_phone("1135", mobile)
    #         if release == "success":
    #             print("释放成功")
    #         break

    # # 测试奶茶
    # my_phone = MyPhoneNaicha("dajiahao12352", "asd123654")
    # rtn = my_phone.login()
    # print(rtn)
    # phone = my_phone.get_phone("1135", "2")
    # print(phone)
    # release = my_phone.release_phone("1135", phone)
    # print(release)


