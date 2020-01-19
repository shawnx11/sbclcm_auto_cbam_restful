# -*- coding:UTF-8 -*-
from bs4 import BeautifulSoup
import requests
from lxml import html

if __name__ == "__main__":

    server = 'https://www.liaoxuefeng.com'
    url = 'https://www.liaoxuefeng.com/wiki/1177760294764384'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}

    name_list = []
    url_list = []

    req = requests.get(url=url, headers=headers)
    html = req.text

    div_index = BeautifulSoup(html, features="lxml")
    div = div_index.find_all('div', id='1177760294764384')
    div_bf = BeautifulSoup(str(div[0]), features="lxml")
    a_bf = div_bf.find_all('a')

    for each in a_bf:
        name_list.append(each.string)
        url_list.append(server + each.get('href'))

    num = len(name_list)

    for i in range(num):
        print('Start to get content: ', name_list[i], ': ', url_list[i])
        url = url_list[i]
        req = requests.get(url=url, headers=headers)
        html = req.text
        div_content = BeautifulSoup(html, features="lxml")
        div = div_content.find_all('div', class_='x-wiki-content x-main-content')
        div_bf = BeautifulSoup(str(div[0]), features="lxml")
        # How to handle <table>?
        p_bf = div_bf.find_all(['p', 'li', 'code'])
        for content in p_bf:
            print(content.string)
        print('\n')


