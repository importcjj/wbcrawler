# -*- coding:utf-8 -*-

import re
import sys
import json
import base64
import urllib
import urllib2
import binascii
import cookielib
try:
    import rsa
except ImportError as e:
    print "Please install module rsa first!"
    sys.exit()


class LoginFailed(Exception):
    pass


class LoginData(dict):

    def __init__(self):
        self['su'] = ''
        self['sp'] = ''
        self['from'] = ''
        self['nonce'] = ''
        self['pagerefer'] = ''
        self['servertime'] = ''
        self['entry'] = 'weibo'
        self['vsnf'] = 1
        self['gateway'] = 1
        self['savestate'] = 7
        self['userticket'] = 1
        self['pwencode'] = 'rsa2'
        self['encoding'] = 'UTF-8'
        self['returntype'] = 'META'
        self['service'] = 'miniblog'
        self['rsakv'] = '1330428213'
        self['url'] = 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.s'\
            'inaSSOController.feedBackUrlCallBack'


class WeiboLoginer(object):

    servertime_nonce_re = re.compile(r'\((.+?)\)')
    direct_url_re = re.compile(
        r"location.replace\('(.+?)'\)")

    def __init__(self, username, password):
        self._username = username
        self._password = password
        # 新建一个能够处理cookie的opener实例
        self._cookies = cookielib.LWPCookieJar()
        self._opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self._cookies))

    def easy_login(self):
        """登录微博
        """
        postdata = self.fetch_data()
        response = self.request(
            'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)',
            postdata).read()
        if 'retcode=0' not in response:
            raise LoginFailed("Failed")
        # 处理相关cookies 非常重要！！！！！！！
        url = self.direct_url_re.findall(response)[0]
        self.request(url).read()

    @property
    def cookie(self):
        """获取相关cookies
        """
        return self._cookies

    @property
    def opener(self):
        """获取opener
        """
        return self._opener

    @property
    def data(self):
        """获取data
        """
        return self._data

    def fetch_data(self):
        """获取用于登录的数据
        """
        self._data = LoginData()
        # 首先,将用户名转码
        su = self._convert_username()
        # 获取最新的servertime 和 nonce
        (servertime, nonce) = self._get_servertime_and_nonce(su)
        # 将用户的密码通过rsa2算法加密
        sp = self._convert_pwd(servertime, nonce)
        # 修改需要post登录的postdata
        self._data['servertime'] = servertime
        self._data['nonce'] = nonce
        self._data['su'] = su
        self._data['sp'] = sp

        return self._data

    def request(self, url, data=None):
        """以get或者post方法打开一个页面,并返回响应内容
        """
        req = urllib2.Request(url)
        req.add_header(
            'User-Agent',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) '
            'Gecko/20100101 Firefox/34.0')
        if data:
            data = urllib.urlencode(data)
            req.add_data(data)
        return self._opener.open(req)

    def _get_servertime_and_nonce(self, username):
        """获取最新的servertime 和 nonce
        """
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaS'\
            'SOController.preloginCallBack&su={}&rsakt=mod&client=ssologin.js(v1.4.18)'\
            .format(username)
        response = self.request(url).read()
        try:
            json_data = self.servertime_nonce_re.findall(response)[
                0]
            response = json.loads(json_data)
            servertime = str(response['servertime'])
            nonce = response['nonce']
            return servertime, nonce
        except Exception:
            raise LoginFailed('Can not get servertime or nonce')

    def _convert_pwd(self, servertime, nonce):
        """采用rsa2加密算法,得到加密过的的用户密码
        """
        pubkey = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC25306288'\
            '2729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD39'\
            '93CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F67398'\
            '84B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'
        rsa_publickey = int(pubkey, 16)
        key = rsa.PublicKey(rsa_publickey, 65537)
        message = str(servertime) + '\t' + str(nonce) + \
            '\n' + str(self._password)
        passwd = rsa.encrypt(message, key)
        passwd = binascii.b2a_hex(passwd)
        return passwd

    def _convert_username(self):
        """将用户名转化成base64编码形式
        """
        username = urllib.quote(self._username)
        username = base64.encodestring(username)[:-1]
        return username

    def _get_id(self, url):
        """从页面怕爬取uid 和 pid
        """
        html = self.request(url).read()
        re_id = re.compile(r"\['page_id'\]='(.+?)'")
        _id = re_id.findall(html)[0]
        return _id


if __name__ == '__main__':
    wbl = WeiboLoginer('18362976187', '7895123')
    wbl.easy_login()
    cookies = wbl.cookie
    cookies.save('1.txt')
    # login_sina('1939249931@qq.com', '1993lgq1023@tq!')
    # login_sina('762485264@qq.com','DuHao@931018')
