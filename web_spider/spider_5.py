# -*- coding:UTF-8 -*-

import requests
from bs4 import BeautifulSoup
from lxml import html

import urllib
from urllib import request
import chardet

import time

########################################################################################################################
# requests get images from: 'http://www.shuaia.net/meinv/'
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

    requests_shuaia_meinv()
