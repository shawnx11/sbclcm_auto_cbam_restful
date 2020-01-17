# -*- coding:UTF-8 -*-

import requests
from bs4 import BeautifulSoup
from lxml import html

urls = []
authors = []
review_url = 'https://movie.douban.com/review/'
reviews = 'https://movie.douban.com/subject/1292720/reviews'
page_start = 'https://movie.douban.com/subject/1292720/reviews'
page_prefix = 'https://movie.douban.com/subject/1292720/reviews?start='
page2 = 'https://movie.douban.com/subject/1292720/reviews?start=20'
page3 = 'https://movie.douban.com/subject/1292720/reviews?start=40'
page_end = 'https://movie.douban.com/subject/1292720/reviews?start=4220'
reviews_dict = {}

pages_list = []
path = 'douban.txt'

def pages():

    pages_list.append(page_start)
    i = 0
    while (i < 4220):
        i += 20
        page = page_prefix + str(i)
        pages_list.append(page)

def spider_douban(reviews):
    # target = 'http://gitbook.cn/'
    # target = 'https://movie.douban.com/review/1249387/'
    # target = 'https://movie.douban.com/subject/1292720/reviews'
    print(reviews, '\n')
    req = requests.get(url=reviews)
    # print(req.encoding)
    # req.encoding = "gbk"
    html = req.text
    bf = BeautifulSoup(html, features="lxml")
    div_review_short = bf.find_all('div', class_='review-short')

    for i in div_review_short:
        short_id = i.get('data-rid')
        reviews_dict[short_id] = review_url + short_id
        # print(short_id)
        # urls.append(review_url + short_id)
        # authors.append(data_author)
        # print(review_url + short_id)

        # div = BeautifulSoup(str(i), features="lxml")
        # a = div.find_all('a')
        # urls.append(a.get('data-url'))
    #
    # print(urls)

    # for i, j in reviews_dict.items():
    #     print(i, '\n', j, '\n')

    for target in reviews_dict:
        req = requests.get(url=reviews_dict[target])
        html = req.text
        bf = BeautifulSoup(html, features="lxml")
        texts = bf.find_all('div', class_='review-content clearfix')
        # print(texts[0].text)
        text = texts[0].text

        with open(path, 'a', encoding='utf-8') as f:
            f.write(target + '\n')
            f.writelines(text)
            f.write('\n\n')

if __name__ == '__main__':

    # spider_douban()

    pages()

    for reviews in pages_list:
        spider_douban(reviews)

