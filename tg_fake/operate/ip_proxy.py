import requests


class ProxyIProla:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = ""

    # 获取本机ip
    @staticmethod
    def get_ip():
        ip_api_url = 'http://whois.pconline.com.cn/ipJson.jsp?json=true'
        rtn = requests.get(ip_api_url)
        ip = rtn.json()['ip']
        return ip

    # 获取token
    def login(self):
        '''
        :param username: 用户名
        :param password: 密码
        :return: 成功返回token，失败返回error
        '''
        login_url = 'http://admin.rola-ip.co/login?user_name=' + self.username + '&password=' + self.password
        rtn = requests.get(login_url)
        code = rtn.json()['code']
        if code == 0:
            self.token = rtn.json()['data']['token']
            return "success"
        else:
            return "error"

    # 检查ip是否在白名单
    def check_whitelist(self, ip):
        '''
        :param token: str
        :param ip: str
        :return: Bool
        '''
        check_whitelist_url = 'http://admin.rola-ip.co/user_get_whitelist?token=' + self.token
        rtn = requests.get(check_whitelist_url)
        if ip in str(rtn.json()):
            return True
        else:
            return False

    # 添加ip到白名单
    def add_whitelist(self, ip, remark=""):
        '''
        :param token:
        :param ip:
        :return: Bool
        '''
        add_whitelist_url = 'http://admin.rola-ip.co/user_add_whitelist?token=' + self.token + '&remark=' + remark + '&ip=' + ip
        rtn = requests.get(add_whitelist_url)
        code = rtn.json()['code']
        if code == 0:
            return True
        else:
            return False

    # 获取代理ip
    def get_proxy_ip(self, count="1", time="3", protocol="socks5"):
        '''
        :param token:
        :param count: 获取数目
        :return: 成功返回ip port，失败返回error
        '''
        ip_url = 'http://list.rola-ip.site:8088/user_get_ip_list?token=' + self.token + '&qty=' + \
                 count + '&country=&time=' + time + '&format=json&protocol=' + protocol + '&filter=1'
        try:
            rtn = requests.get(ip_url)
            code = rtn.json()['code']
            if code == 0:
                data = rtn.json()['data'][0]
                ip = data.split(':')
                return ip[0], int(ip[1])
        except:
            return "error"
        return "error"

class ProxyIpidea:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    # 登录
    def login(self):
        url = "https://api.ipidea.net/index/users/login_do"
        data = {
            "phone": self.username,
            "password": self.password,
            "remember": 0
        }

        res = requests.post(url, data=data)
        print(res.text)

    def get_info(self):
        url = "https://www.ipidea.net/getapi/"
        res = requests.get(url)
        res.encoding = "utf-8"
        print(res.text)

if __name__ == '__main__':
    my_proxy = ProxyIpidea("18620869700", "jay526060")
    my_proxy.login()
    my_proxy.get_info()



# if __name__ == '__main__':
    # print(get_ip())
    # check_whitelist('VbnWojDld2ZilBbp1599291218972', '180.25.201.19')
    # add_whitelist('VbnWojDld2ZilBbp1599291218972', '180.25.251.19')

    # my_proxy = ProxyIProla("dasd", "dsad")
    # proxy_ip = my_proxy.get_proxy_ip()
    # print(proxy_ip)

