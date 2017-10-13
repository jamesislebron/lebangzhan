#-*- coding:utf8 -*-
import re

import os
from hashlib import md5
from multiprocessing.pool import Pool

import pymongo
import requests
import json

from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from urllib.parse import urlencode
from config import *
from multiprocessing import Pool
from json.decoder import JSONDecodeError

###some tips：主要增加了存储到mongoDB的过程，图片本身存储在本地，使用md5命名避免重复下载；然后使用了多线程，提高了效率。
###another tips

#url = 'http://www.toutiao.com/search_content/?offset=0&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&cur_tab=1'
client = pymongo.MongoClient(MONGO_URL, connect=False) #由于使用多进程，有的进程并没有建立连接，加false可以进程执行时再建立client
db = client[MONGO_DB]

def get_index_page(offset,keyword):
    header = {
        'offset':  offset,
        'format':  'json',
        'keyword': keyword,
        'autoload':  'true',
        'count':  20,
        'cur_tab':  3
    }
    url = 'http://www.toutiao.com/search_content/?' + urlencode(header)
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.text
        return None
    except RequestException:
        print('访问index页面错误')
        return None


def parse_index_page(html):
    try:
        res_json = json.loads(html)
        if res_json and 'data' in res_json.keys():
            pic_index = []
            for item in res_json['data']:
                if item and 'url' in item.keys():
        #            pic_index.append({'url':item['url'],'title':item['title']})
                    pic_index.append(item['url'])
        return pic_index
    except JSONDecodeError:
        pass


def get_detail_page(url):
    if not re.search('http://toutiao.com/group/.+?', url):
        print('detail页面不是图集')
        return None
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.text
        return None
    except RequestException:
        print('访问detail页面错误')
        return None

def parse_detail_page(html, url):
    soup = BeautifulSoup(html ,'html.parser')
    title = soup.select('title')[0].get_text()
    pattern = re.compile('    gallery: (.+?)siblingList',re.S)
    aaa = re.search(pattern, html).group(1).rstrip().rstrip(',')
    try:
        res_json = json.loads(aaa)
        if res_json and 'sub_images' in res_json.keys():
            images = [item['url'] for item in res_json['sub_images']]
            for image in images:
                download_image(image)
            return {
                'title': title,
                'images': images,
                'url' : url
            }
    except JSONDecodeError:
        pass

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到MONGO成功', result)
        return True
    return False

def save_image(content):
    file_path = '{0}/{1}/{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()

def download_image(url):
    try:
        res = requests.get(url)
        if res.status_code == 200
            save_image(res.content)
        return None
    except RequestException:
        print('访问图片页面错误')
        return None


def main(offset):
    #url = 'http://toutiao.com/group/6469524934560317966/'
    html = get_index_page(offset, KEYWORD)
    for url in parse_index_page(html):
        #print(url)
        html = get_detail_page(url)
        if html:
            result = parse_detail_page(html, url)
            if result:
                save_to_mongo(result)

if __name__ == '__main__':
    groups = [x * 20 for x in range(GROUP_START, GROUP_END)]
    pool = Pool()
    pool.map(main, groups)