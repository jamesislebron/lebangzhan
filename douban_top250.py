import requests
from bs4 import BeautifulSoup
import os
import pandas

'''
res = requests.get('https://movie.douban.com/top250')
res.encoding = 'utf-8'
soup = BeautifulSoup(res.text, 'html.parser')
a = soup.select('.item')[0]
'''
def getFilmName(item):
    film_name = ''
    for i in item.select('a span'):
        film_name += i.text
    return film_name

def getFilmInfo(item):
    try:
        film_info = item.select('p')[0].text
    except IndexError as Info:
        print('some error ocurr: s' % Info)
    return film_info

def getFilmInq(item):
    try:
        film_inq = item.select('.inq')[0].text
    except IndexError as Info:
        film_inq = ''
        print('some error ocurr: this item has no inq')
    return film_inq

def getFilmLink(item):
    film_link = item.select('a')[0]['href']
    return film_link

def getFilmRank(item):
    film_rank = item.select('em')[0].text
    return film_rank

def getFilmAll(item):
    film_all = {}
    film_all['name'] = getFilmName(item)
    film_all['info'] = getFilmInfo(item)
    film_all['inq'] = getFilmInq(item)
    film_all['link'] = getFilmLink(item)
    film_all['rank'] = getFilmRank(item)
    return film_all

def getPageList(url):
    page_list = []
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    for i in soup.select('.item'):
        page_list.append(getFilmAll(i))
    return page_list

def getDoubanTop250():
    page_all = []
    url = 'https://movie.douban.com/top250?start={}&filter='
    for i in range(0,250,25):
        page_all.extend(getPageList(url.format(i)))
    return page_all

url = 'https://movie.douban.com/top250?start=125&filter='
result = getDoubanTop250()
d = pandas.DataFrame(result)
d.to_excel('C:/Users/james.duan/Desktop/doubantop250.xlsx')

