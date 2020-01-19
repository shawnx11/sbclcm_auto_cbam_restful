# -*- coding:UTF-8 -*-

import requests
from bs4 import BeautifulSoup
from lxml import html

import urllib
from urllib import request
import chardet

from urllib import parse
import json

########################################################################################################################
def spider_biqukan():
    server = 'http://www.biqukan.com/'
    target = 'http://www.biqukan.com/1_1094/'
    req = requests.get(url=target)
    req.encoding = "gbk"
    html = req.text
    div_bf = BeautifulSoup(html, features="lxml")
    div = div_bf.find_all('div', class_='listmain')
    a_bf = BeautifulSoup(str(div[0]))
    a = a_bf.find_all('a')
    for each in a:
        print(each.string, server + each.get('href'))

def spider_douban():
    # target = 'http://gitbook.cn/'
    target = 'https://movie.douban.com/review/1249387/'
    req = requests.get(url=target)
    # print(req.encoding)
    # req.encoding = "gbk"
    # print(req.text)
    html = req.text
    bf = BeautifulSoup(html, features="lxml")
    texts = bf.find_all('div', class_='review-content clearfix')
    # print(texts)
    # print(texts[0].text.replace('\xa0' * 8, '\n\n'))
    print(texts[0].text)

def spider_unsplash():
    # target = 'https://unsplash.com/'
    # req = requests.get(url=target)
    # print(req.text)

    target = 'http://unsplash.com/napi/feeds/home'
    req = requests.get(url=target, verify=False)
    print(req.text)

def urllib_test01():
    response = request.urlopen("https://fanyi.baidu.com")
    html = response.read()
    # html = html.decode()
    html = html.decode('utf-8')
    print(html)

# use chardet
def urllib_test02():
    # response = request.urlopen("https://fanyi.baidu.com")
    response = request.urlopen("https://confluence.app.alcatel-lucent.com/display/SBCTS/R19.5SP1910")
    html = response.read()
    charset = chardet.detect(html)
    # print(charset)
    html = html.decode(charset['encoding'])
    print(html)

# use proxy
#     import urllib.request
#
#     # set up authentication info
#     authinfo = urllib.request.HTTPBasicAuthHandler()
#     authinfo.add_password(realm='PDQ Application',
#                           uri='https://mahler:8092/site-updates.py',
#                           user='klem',
#                           passwd='geheim$parole')
#
#     proxy_support = urllib.request.ProxyHandler({"http": "http://ahad-haam:3128"})
#
#     # build a new opener that adds authentication and caching FTP handlers
#     opener = urllib.request.build_opener(proxy_support, authinfo,
#                                          urllib.request.CacheFTPHandler)
#
#     # install it
#     urllib.request.install_opener(opener)
#
#     f = urllib.request.urlopen('http://www.python.org/')
def urllib_test03():
    # http: // cnproxy.int.nokia - sbell.com / proxy.pac
    # 87.254.212.120:8080
    proxy_support = urllib.request.ProxyHandler({"https": "135.245.48.34:8000"})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)
    response = urllib.request.urlopen("https://fanyi.baidu.com")
    html = response.read()
    charset = chardet.detect(html)
    html = html.decode(charset['encoding'])
    print(html)

def urllib_test04():
    # req = request.Request("https://fanyi.baidu.com/")
    req = request.Request("http://fanyi.youdao.com/")
    response = request.urlopen(req)
    html = response.read()
    html = html.decode("utf-8")
    print(html)


########################################################################################################################
from urllib import parse
import json

# translate via fanyi.baidu
# Form Data
# from: en
# to: zh
# query: jack
# transtype: realtime
# simple_means_flag: 3
# sign: 143778.447123
# token: aaa2120faf3b3bdc65b393982d279071
def urllib_translate_baidu():

    # 对应上图的Request URL
    Request_URL = 'https://fanyi.baidu.com/v2transapi?from=en&to=zh'

    # 创建Form_Data字典，存储上图的Form Data
    fdata = {'from': 'en',
             'to': 'zh',
             'query': 'shawn',
             'transtype': 'realtime',
             'simple_means_flag': '3',
             'sign': '',
             'token': 'aaa2120faf3b3bdc65b393982d279071'}

    # # header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"}
    # header = {"User-Agent":"Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36"}
    #
    # data = parse.urlencode(fdata).encode('utf-8')
    # req = request.Request(Request_URL, data = data, headers = header)
    # response = request.urlopen(req)
    #
    # html = response.read()
    # html = html.decode("utf-8")
    # print(html)

    # 使用urlencode方法转换标准格式
    data = parse.urlencode(fdata).encode('utf-8')
    # 传递Request对象和转换完格式的数据
    response = request.urlopen(Request_URL, data)
    # 读取信息并解码
    html = response.read().decode('utf-8')
    print(html)

    # 使用JSON
    translate_results = json.loads(html)
    # 找到翻译结果
    translate_results = translate_results['translateResult'][0][0]['tgt']
    # 打印翻译信息
    print("翻译的结果是：%s" % translate_results)


########################################################################################################################
# translate via youdao
# http: // fanyi.youdao.com /
# in fanyi.min.js
# define("newweb/common/requestMoreTrans", ["./service", "./utils", "./md5", "./jquery-1.7"],
# function(e, t) {
#     var n = e("./jquery-1.7"),
#     r = e("./service");
#     e("./utils");
#     e("./md5");
#     var i = null;
#     t.asyRequest = function(e) {
#         var t = e.i,
#         o = r.generateSaltSign(t);
#         i && i.abort(),
#         i = n.ajax({
#             type: "POST",
#             contentType: "application/x-www-form-urlencoded; charset=UTF-8",
#             url: "/bbk/translate_m.do",
#             data: {
#                 i: e.i,
#                 client: e.client,
#                 salt: o.salt,
#                 sign: o.sign,
#                 ts: o.ts,
#                 bv: o.bv,
#                 tgt: e.tgt,
#                 from: e.from,
#                 to: e.to,
#                 doctype: "json",
#                 version: "3.0",
#                 cache: !0
#             },
#             dataType: "json",
#             success: function(t) {
#                 t && 0 == t.errorCode ? e.success && e.success(t) : e.error && e.error(t)
#             },
#             error: function(e) {}
#         })
#     }
# }),
#
# generateSaltSign at:
# define("newweb/common/service", ["./utils", "./md5", "./jquery-1.7"],
# function(e, t) {
#     var n = e("./jquery-1.7");
#     e("./utils");
#     e("./md5");
#     var r = function(e) {
#         var t = n.md5(navigator.appVersion),
#         r = "" + (new Date).getTime(),
#         i = r + parseInt(10 * Math.random(), 10);
#         return {
#             ts: r,
#             bv: t,
#             salt: i,
#             sign: n.md5("fanyideskweb" + e + i + "n%A-rKaT5fb[Gy?;N5@Tj")
#         }
#     };
#     t.recordUpdate = function(e) {
#         var t = e.i,
#         i = r(t);
#         n.ajax({
#             type: "POST",
#             contentType: "application/x-www-form-urlencoded; charset=UTF-8",
#             url: "/bettertranslation",
#             data: {
#                 i: e.i,
#                 client: "fanyideskweb",
#                 salt: i.salt,
#                 sign: i.sign,
#                 ts: i.ts,
#                 bv: i.bv,
#                 tgt: e.tgt,
#                 modifiedTgt: e.modifiedTgt,
#                 from: e.from,
#                 to: e.to
#             },
#             success: function(e) {},
#             error: function(e) {}
#         })
#     },
#     t.recordMoreResultLog_get = function(e) {
#         n.ajax({
#             type: "POST",
#             contentType: "application/x-www-form-urlencoded; charset=UTF-8",
#             url: "/ctlog",
#             data: {
#                 i: e.i,
#                 action: "GET_MORE_TRANSLATION",
#                 from: e.from,
#                 to: e.to
#             },
#             success: function(e) {},
#             error: function(e) {}
#         })
#     },
#     t.recordMoreResultLog_choose = function(e) {
#         n.ajax({
#             type: "POST",
#             contentType: "application/x-www-form-urlencoded; charset=UTF-8",
#             url: "/ctlog",
#             data: {
#                 i: e.i,
#                 tgt: e.tgt,
#                 systemName: e.systemName,
#                 pos: e.pos,
#                 action: "SELECT_OTHER_TRANSLATION",
#                 from: e.from,
#                 to: e.to
#             },
#             success: function(e) {},
#             error: function(e) {}
#         })
#     },
#     t.generateSaltSign = r
# }),
##########################################
#     var r = function(e) {
#         var t = n.md5(navigator.appVersion),
#         r = "" + (new Date).getTime(),
#         i = r + parseInt(10 * Math.random(), 10);
#         return {
#             ts: r,
#             bv: t,
#             salt: i,
#             sign: n.md5("fanyideskweb" + e + i + "n%A-rKaT5fb[Gy?;N5@Tj")
#         }
#     };

# We can know:
# （1）网站采用的是md5加密
# （2）ts = "" + (new Date).getTime()  ，为时间戳
# （3）salt = "" + (new Date).getTime() + parseInt(10 * Math.random(), 10)
# （4）sign = n.md5("fanyideskweb" + e + i + "n%A-rKaT5fb[Gy?;N5@Tj")
# 其中，e为要翻译内容，i为时间戳，等于ts，其余为固定字符串


##########################################

# From : https://blog.csdn.net/suixinlun/article/details/93976400
import hashlib
import random
import time
import requests
import json

class Youdao():
    def __init__(self, msg):
        self.msg = msg
        self.url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
        self.D = "n%A-rKaT5fb[Gy?;N5@Tj"
        self.salt = self.get_salt()
        self.sign = self.get_sign()
        self.ts = self.get_ts()

    def get_md(self, value):
        # md5加密
        m = hashlib.md5()
        # m.update(value)
        m.update(value.encode('utf-8'))
        return m.hexdigest()

    def get_salt(self):
        # 根据当前时间戳获取salt参数
        s = int(time.time() * 1000) + random.randint(0, 10)
        return str(s)

    def get_sign(self):
        # 使用md5函数和其他参数，得到sign参数
        s = "fanyideskweb" + self.msg + self.salt + self.D
        return self.get_md(s)

    def get_ts(self):
        # 根据当前时间戳获取ts参数
        s = int(time.time() * 1000)
        return str(s)

    def get_result(self):
        Form_Data = {
            'i': self.msg,
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': self.salt,
            'sign': self.sign,
            'ts': self.ts,
            'bv': '1c13ced10aeceb64c3dd73719a38cbcd',
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME'
        }

        headers = {
            'Cookie': 'OUTFOX_SEARCH_USER_ID=274146346@10.169.0.84; OUTFOX_SEARCH_USER_ID_NCOO=865680507.3766074; JSESSIONID=aaaED_UeTi2Os7D3exd5w; ___rl__test__cookies=1573090615968',
            'Referer': 'http://fanyi.youdao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }

        # set up proxy {"https": "135.245.48.34:8000"}
        proxies = {'http': '135.245.48.34:8000', 'https': '135.245.48.34:8000'}

        response = requests.post(self.url, proxies=proxies, data=Form_Data, headers=headers).text
        # print(response)           # {"translateResult":[[{"tgt":"肖恩","src":"shawn"}]],"errorCode":0,"type":"it2zh-CHS"}
        translate_results = json.loads(response)
        # print(translate_results)  #{'translateResult': [[{'tgt': '肖恩', 'src': 'shawn'}]], 'errorCode': 0, 'type': 'it2zh-CHS'}

        if 'translateResult' in translate_results:
            translate_results = translate_results['translateResult'][0][0]['tgt']
            print("翻译的结果是：%s" % translate_results)
        else:
            print(translate_results)


from urllib import request
from urllib import parse
import json

def requests_translate_youdao():
    Request_URL = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'

    data = Youdao('shawn')
    data.get_result()

    # Data example:
    # i: shawn
    # from: AUTO
    # to: AUTO
    # smartresult: dict
    # client: fanyideskweb
    # salt: 15730293344640
    # sign: d913f50d2567ba8333b5b2f74e5d491b
    # ts: 1573029334464
    # bv: 1c13ced10aeceb64c3dd73719a38cbcd
    # doctype: json
    # version: 2.1
    # keyfrom: fanyi.web
    # action: FY_BY_REALTlME
    # Data = {'i': 'shawn',
    #         'from': 'AUTO',
    #         'to': 'AUTO',
    #         'smartresult': 'dict',
    #         'client': 'fanyideskweb',
    #         # 'salt': '15730293344640',
    #         # 'sign': 'd913f50d2567ba8333b5b2f74e5d491b',
    #         # 'ts': '1573029334464',
    #         # 'bv': '1c13ced10aeceb64c3dd73719a38cbcd',
    #         'doctype': 'json',
    #         'version': '2.1',
    #         'keyfrom': 'fanyi.web',
    #         'action': 'FY_BY_REALTlME'
    #         }

    # # 使用urlencode方法转换标准格式
    # data = parse.urlencode(Data).encode('utf-8')
    # # 传递Request对象和转换完格式的数据
    # response = request.urlopen(Request_URL, data)
    # # 读取信息并解码
    # html = response.read().decode('utf-8')
    # print(html)
    # # 使用JSON
    # translate_results = json.loads(html)
    # # 找到翻译结果
    # translate_results = translate_results['translateResult'][0][0]['tgt']
    # # 打印翻译信息
    # print("翻译的结果是：%s" % translate_results)

def urllib_translate_youdao(tdata):

    Request_URL = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'

    # Data example:
    # i: shawn
    # from: AUTO
    # to: AUTO
    # smartresult: dict
    # client: fanyideskweb
    # salt: 15730293344640
    # sign: d913f50d2567ba8333b5b2f74e5d491b
    # ts: 1573029334464
    # bv: 1c13ced10aeceb64c3dd73719a38cbcd
    # doctype: json
    # version: 2.1
    # keyfrom: fanyi.web
    # action: FY_BY_REALTlME
    Data = {'i': 'shawn',
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': '',
            'sign': '',
            'ts': '',
            'bv': '1c13ced10aeceb64c3dd73719a38cbcd',
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME'
            }

    # How to get values for salt, sign, ts:
    #     var r = function(e) {
    #         var t = n.md5(navigator.appVersion),
    #         r = "" + (new Date).getTime(),
    #         i = r + parseInt(10 * Math.random(), 10);
    #         return {
    #             ts: r,
    #             bv: t,
    #             salt: i,
    #             sign: n.md5("fanyideskweb" + e + i + "n%A-rKaT5fb[Gy?;N5@Tj")
    #         }
    #     };

    # ts, salt
    r = int(time.time() * 1000)
    i = r + random.randint(0, 10)

    Data['ts'] = str(r)
    Data['salt'] = str(i)

    # bv
    navigator_appversion = "5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"
    m = hashlib.md5()
    m.update(navigator_appversion.encode('utf-8'))
    t = m.hexdigest()
    Data['bv'] = t

    # sign
    sign_str = "fanyideskweb" + tdata + str(i) + "n%A-rKaT5fb[Gy?;N5@Tj"
    n = hashlib.md5()
    n.update(sign_str.encode('utf-8'))
    Data['sign'] = n.hexdigest()

    # # 使用urlencode方法转换标准格式
    # data = parse.urlencode(Data).encode('utf-8')
    # # 传递Request对象和转换完格式的数据
    # response = request.urlopen(Request_URL, data)
    # # 读取信息并解码
    # html = response.read().decode('utf-8')
    # print(html)
    # # 使用JSON
    # translate_results = json.loads(html)
    # # 找到翻译结果
    # translate_results = translate_results['translateResult'][0][0]['tgt']
    # # 打印翻译信息
    # print("翻译的结果是：%s" % translate_results)

    headers = {
        'Cookie': 'OUTFOX_SEARCH_USER_ID=274146346@10.169.0.84; OUTFOX_SEARCH_USER_ID_NCOO=865680507.3766074; JSESSIONID=aaaED_UeTi2Os7D3exd5w; ___rl__test__cookies=1573090615968',
        'Referer': 'http://fanyi.youdao.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }

    data = parse.urlencode(Data).encode('utf-8')
    req = request.Request(Request_URL, data = data, headers = headers)
    response = request.urlopen(req)

    html = response.read()
    html = html.decode("utf-8")
    print(html, '\n')

    translate_results = json.loads(html)
    results = translate_results['translateResult'][0][0]['tgt']
    print('Translate Results: ', results)


########################################################################################################################
# Test urllib error
# class URLError(builtins.OSError)
# class HTTPError(URLError, urllib.response.addinfourl)
# class ContentTooShortError(URLError)
def urllib_URLError_test():

    from urllib import request
    from urllib import error

    # url that doesn't exist
    url = "http://www.iloveyou.com/"
    req = request.Request(url)

    try:
        response = request.urlopen(req)
        html = response.read().decode('utf-8')
        print(html)
    except error.URLError as e:
        # print(e.reason)
        print(e)


def urllib_HTTPError_test():

    from urllib import request
    from urllib import error

    # url that doesn't exist
    url = "http://www.douyu.com/shawnx.html"
    req = request.Request(url)

    # try:
    #     responese = request.urlopen(req)
    #     # html = responese.read()
    # except error.HTTPError as e:
    #     print(e.code)

    # try:
    #     responese = request.urlopen(req)
    # except error.URLError as e:
    #     if hasattr(e, 'code'):
    #         print("HTTPError")
    #         print(e.code)
    #     elif hasattr(e, 'reason'):
    #         print("URLError")
    #         print(e.reason)

    try:
        response = request.urlopen(req)
    except error.HTTPError as e:
        print('HTTPError')
        print(e)
    except error.URLError as e:
        print('URLError')
        print(e)


########################################################################################################################
# Test headers
# class Request(builtins.object)
#    	Request(url, data=None, headers={}, origin_req_host=None, unverifiable=False, method=None)

def urllib_headers_test():

    from urllib import request

    # url = 'https://www.zhihu.com'
    url = 'https://qd.lianjia.com/ershoufang/'
    headers = {}
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'

    # req = request.Request(url, headers=headers)
    # response = request.urlopen(req)
    # html = response.read().decode('utf-8')
    # print(html)

    req = request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36')
    response = request.urlopen(req)
    html = response.read().decode('utf-8')
    print(html)

########################################################################################################################
# urllib test cookies
def urllib_cookies():

    from urllib import request
    from http import cookiejar

    # 声明一个CookieJar对象实例来保存cookie
    cookie = cookiejar.CookieJar()
    # 利用urllib.request库的HTTPCookieProcessor对象来创建cookie处理器,也就CookieHandler
    handler = request.HTTPCookieProcessor(cookie)
    # 通过CookieHandler创建opener
    opener = request.build_opener(handler)
    # 此处的open方法打开网页
    response = opener.open('http://www.zhihu.com')
    # 打印cookie信息
    for item in cookie:
        print('Name = %s' % item.name)
        print('Value = %s' % item.value)


########################################################################################################################
#Test for BeautifulSoup
# find_all(name, attrs, recursive, text, limit, **kwargs)：
def bs4_test():

    from bs4 import BeautifulSoup

    html = """
    <html>
    <head>
    <title>HTML Test</title>
    </head>
    <body>
    <p class="title" name="Test"><b>My Test</b></p>
    <li><!--注释--></li>
    <a href="https://beautifulsoup.readthedocs.io/zh_CN/latest/" class="sister" id="link1">BeautifulSoup</a><br/>
    <a href="https://requests.kennethreitz.org//zh_CN/latest/user/quickstart.html" class="sister" id="link2">Requests</a><br/>
    </body>
    </html>
    """

    soup = BeautifulSoup(html, 'lxml')

    print(soup.prettify())


########################################################################################################################
#Test for BeautifulSoup
# https://www.biqukan.com/1_1094/5403177.html
def bs4_urllib_biqukan():

    from urllib import request
    from bs4 import BeautifulSoup
    import chardet

    # url = 'https://www.biqukan.com/1_1094/5403177.html'
    # response = request.urlopen(url)
    # html = response.read()
    # charset = chardet.detect(html)
    # # print(charset)
    # html = html.decode(charset['encoding'])
    # # print(html)
    #
    # soup = BeautifulSoup(html, 'lxml')
    # data = soup.find_all(attrs={"id":"content", "class": "showtxt"})
    #
    # texts = soup.find_all(id='content', class_='showtxt')
    #
    # print(texts)

    # download_url = 'http://www.biqukan.com/1_1094/5403177.html'
    # head = {}
    # head['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    # download_req = request.Request(url = download_url, headers = head)
    # download_response = request.urlopen(download_req)
    # download_html = download_response.read().decode('gbk','ignore')
    # soup_texts = BeautifulSoup(download_html, 'lxml')
    # texts = soup_texts.find_all(id = 'content', class_ = 'showtxt')
    # soup_text = BeautifulSoup(str(texts), 'lxml')
    #
    # print(soup_text.div.text.replace('\xa0',''))

    target_url = 'http://www.biqukan.com/1_1094/'
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
    target_req = request.Request(url=target_url, headers=head)
    target_response = request.urlopen(target_req)
    target_html = target_response.read().decode('gbk', 'ignore')

    listmain_soup = BeautifulSoup(target_html, 'lxml')

    chapters = listmain_soup.find_all('div', class_='listmain')

    download_soup = BeautifulSoup(str(chapters), 'lxml')

    begin_flag = False

    for child in download_soup.dl.children:
        if child != '\n':
            if child.string == u"《一念永恒》正文卷":
                begin_flag = True
            if begin_flag == True and child.a != None:
                download_url = "http://www.biqukan.com" + child.a.get('href')
                download_name = child.string
                print(download_name + " : " + download_url)


def bs4_requests_biqukan():

    from bs4 import BeautifulSoup
    import chardet
    import requests

    url = 'https://www.biqukan.com/1_1094/5403177.html'

    req = requests.get(url=url)
    req.encoding = "gbk"
    html = req.text
    # div_bf = BeautifulSoup(html, features="lxml")
    # div = div_bf.find_all('div', class_='listmain')
    # a_bf = BeautifulSoup(str(div[0]))
    # a = a_bf.find_all('a')
    # for each in a:
    #     print(each.string, server + each.get('href'))

    print(html)


########################################################################################################################
def selenium_test():

    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys

    # options = webdriver.ChromeOptions()
    # options.add_argument(
    #     'user-agent="Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19"')
    # driver = webdriver.Chrome(chrome_options=options)
    # driver.get('https://www.baidu.com/')

    # driver.get("https://www.python.org")
    # assert "Python" in driver.title
    # print(driver.title)
    #
    # # elem = driver.find_element_by_name("q")
    # elem = driver.find_element_by_id("id-search-field")
    # elem.clear()
    # elem.send_keys("pycon")
    # elem.send_keys(Keys.RETURN)
    # print(driver.page_source)
    # driver.close()

    # from selenium import webdriver
    # from selenium.webdriver.support.wait import WebDriverWait
    # import time
    # driver = webdriver.Firefox()
    # driver.get("http://www.baidu.com")
    # driver.execute_script("document.getElementById(\"kw\").value=\"selenium\"")
    # WebDriverWait(driver, 10).until(
    #     lambda driver: driver.find_element_by_xpath(".//*[@id='container']/div[2]/div/div[2]"))
    # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    # time.sleep(5)

    options = webdriver.ChromeOptions()
    # options.add_argument(
    #     'user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"')
    options.add_argument(
        'user-agent="Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19"')

    url = 'https://wenku.baidu.com/view/0f15a7515627a5e9856a561252d380eb62942396.html'

    driver = webdriver.Chrome(chrome_options=options)

    driver.get(url)

    # page = driver.find_elements_by_xpath("/html/body/div/div[2]/div[6]/div[2]/div[2]/div[1]/div")
    # page = driver.find_elements_by_xpath("/html/body/div/div[2]/div[6]/div[2]/div[2]/div[1]/div/div[1]")
    page = driver.find_elements_by_xpath("/html/body/div/div[2]/div[6]/div[2]/div[2]/div[1]/div/div[2]")

    # driver.execute_script("window.scrollTo(0,document.body.scrollHeight/5)")

    page[0].click()

    # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    # driver.execute_script('arguments[0].scrollIntoView();', page[-1])  # 拖动到可见的元素去
    # nextpage = driver.find_element_by_xpath("//a[@data-fun='next']")
    # page.click()

    # time.sleep(3000)


########################################################################################################################
# requests get images from: 'http://www.shuaia.net/meinv/'
#
    # # Here is test with one example url
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
    # proxies = {'http': '135.245.48.34:8000', 'https': '135.245.48.34:8000'}
    #
    # target_url = 'http://www.shuaia.net/meinv/2018-04-23/14941.html'
    # filename = 'test.jpg'
    # img_req = requests.get(url=target_url, headers=headers, proxies=proxies)
    # img_req.encoding = 'utf-8'
    # img_html = img_req.text
    # img_bf_1 = BeautifulSoup(img_html, 'lxml')
    # img_url = img_bf_1.find_all('div', class_='wr-single-content-list')
    # img_bf_2 = BeautifulSoup(str(img_url), 'lxml')
    # img_url = 'http://www.shuaia.net' + img_bf_2.div.img.get('src')
    # if 'images' not in os.listdir():
    #     os.makedirs('images')
    # urlretrieve(url=img_url, filename='images/' + filename)
    # print('Download completed!')

def requests_shuaia_meinv(page_num = 20):

    import requests
    from bs4 import BeautifulSoup
    from urllib.request import urlretrieve
    import os

    # url = 'http://www.shuaia.net/e/tags/?tagname=%E7%BE%8E%E5%A5%B3'
    # page 1: http://www.shuaia.net/meinv/
    # page 2: http://www.shuaia.net/meinv/index_2.html
    # This is meinv page 1
    url_prefix = 'http://www.shuaia.net'
    url = 'http://www.shuaia.net/meinv/'
    page_list = [url]
    # for i in range(2,page_num):
    for i in range(40, page_num+100):
        page_list.append(url + 'index_' + str(i) + '.html')
    print('Pages: ')
    print(page_list)
    print('\n')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
    # proxies = {'http': '135.245.48.34:8000', 'https': '135.245.48.34:8000'}
    proxies = {}

    # req = requests.get(url=url, headers=headers, proxies=proxies)
    # req.encoding = 'utf-8'
    # html = req.text
    #
    # url_list = []
    # bf = BeautifulSoup(html, 'lxml')
    # targets_url = bf.find_all(class_='item-img')
    # for each in targets_url:
    #     url_list.append(each.img.get('alt') + '=' + each.get('href'))
    # print(url_list)

    if 'images' not in os.listdir():
        os.makedirs('images')

    for page in page_list:
        print('Page: ' + page)
        req = requests.get(url=page, headers=headers, proxies=proxies)
        req.encoding = 'utf-8'
        html = req.text

        url_list = []
        url_dict = {}
        bf = BeautifulSoup(html, 'lxml')
        targets_url = bf.find_all(class_='item-img')
        for each in targets_url:
            name = each.img.get('alt')
            value = each.get('href')
            # url_list.append(each.img.get('alt') + '=' + each.get('href'))
            url_list.append(name + '=' + value)
            url_dict[name] = value

        # for i, j in url_dict.items():
        #     print(i, j)

        # Here we use dict to iterate all images on one page
        for image_name in url_dict.keys():
            target_url = url_dict[image_name]
            # filename = image_name+'.jpg'
            # filename = image_name+'.jpeg'
            img_req = requests.get(url=target_url, headers=headers, proxies=proxies)
            img_req.encoding = 'utf-8'
            img_html = img_req.text
            img_bf_1 = BeautifulSoup(img_html, 'lxml')
            img_url = img_bf_1.find_all('div', class_='wr-single-content-list')
            img_bf_2 = BeautifulSoup(str(img_url), 'lxml')
            # img_url = url_prefix + img_bf_2.div.img.get('src')
            if img_bf_2.div is None or img_bf_2.div.img is None:
                continue
            img_url = img_bf_2.div.img.get('src')
            if 'http:' not in img_url:
                # Then the src would look like: '/d/file/meinv/2018-10-03/2178ca324590fa3a944a906ca35b6324.jpg'
                # Handle this format
                img_url = url_prefix + img_url
            filename = img_url.split('/')[-1]
            print('Image url: ', img_url)
            urlretrieve(url=img_url, filename='images/' + filename)
            time.sleep(2)
            print('Download completed for: ', image_name, ' The filename is: ', filename)


########################################################################################################################
# Test Cookies
def requests_test_cookies01():

    import requests

    url = 'https://www.baidu.com/'
    headers = {'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en,zh;q=0.9,zh-CN;q=0.8,en-US;q=0.7',
               }
    proxies = {'http': '135.245.48.34:8000', 'https': '135.245.48.34:8000'}

    s = requests.Session()
    req = s.get(url=url, headers=headers, proxies=proxies)
    print(s.cookies)

########################################################################################################################
# Test Cookies
# Test PhantomJS
def requests_test_cookies02():

    import requests
    from selenium import webdriver

    url = 'http://pythonscraping.com'
    driver = webdriver.PhantomJS(executable_path='D:/Programs/JetBrains/PycharmProjects/py37projects/web_spider/phantomjs-2.1.1-windows/bin/phantomjs.exe')
    # driver = webdriver.PhantomJS()
    driver.get(url)
    driver.implicitly_wait(1)
    print(driver.get_cookies())


########################################################################################################################
# Test get IPs from https://www.xicidaili.com

def requests_test_proxies():

    import requests
    from bs4 import BeautifulSoup
    from lxml import etree

    S = requests.Session()

    target_url = 'https://www.xicidaili.com/nn'

    headers = {'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en,zh;q=0.9,zh-CN;q=0.8,en-US;q=0.7',
               }
    proxies = {'http': '135.245.48.34:8000', 'https': '135.245.48.34:8000'}

    target_response = S.get(url = target_url, headers = headers, proxies=proxies)
    target_response.encoding = 'utf-8'
    target_html = target_response.text
    bf1_ip_list = BeautifulSoup(target_html, 'lxml')
    bf2_ip_list = BeautifulSoup(str(bf1_ip_list.find_all(id = 'ip_list')), 'lxml')
    ip_list_info = bf2_ip_list.table.contents

    proxys_list = []
    for index in range(len(ip_list_info)):
        if index % 2 == 1 and index != 1:
            dom = etree.HTML(str(ip_list_info[index]))
            ip = dom.xpath('//td[2]')
            port = dom.xpath('//td[3]')
            protocol = dom.xpath('//td[6]')
            proxys_list.append(protocol[0].text.lower() + '#' + ip[0].text + '#' + port[0].text)
    print(proxys_list)

########################################################################################################################
# Test CBAM login
# https://10.75.44.14/vnfs?pageNum=1&pageSize=20&sortAsc=asc&sortBy=vnfInstanceName
# https://10.75.44.14/
def requests_test_cbam():

    import requests
    from bs4 import BeautifulSoup

    url = 'https://10.75.44.14/'
    client_id = 'lcm'
    client_secret = '-Assured11'
    headers = {'Accept': '*/*', 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    # authenticate
    address = url
    verify = False
    response = requests.post(
        address, data=data, headers=headers, verify=verify)

    # print('response: ', response)
    # print('response.headers: ', response.headers)
    # print('response.text: ', response.text)


########################################################################################################################
# setup proxy using urllib
def setup_proxy():
    # proxy_support = urllib.request.ProxyHandler({"https": "135.245.48.34:8000"})
    proxy_support = urllib.request.ProxyHandler({"http": "135.245.48.34:8000", "https": "135.245.48.34:8000"})
    opener = urllib.request.build_opener(proxy_support)
    # opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36')]
    urllib.request.install_opener(opener)

    # # another way
    # request.install_opener(opener)
    # response = request.urlopen(url)
    # html = response.read().decode("utf-8")

########################################################################################################################
if __name__ == '__main__':
    # setup_proxy()
    # requests_translate_youdao()
    # urllib_translate_youdao("Hi")

    requests_test_cbam()
