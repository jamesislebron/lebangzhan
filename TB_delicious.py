#-*- coding:utf8 -*-
import os
import re

import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq


#os.environ["webdriver.chrome.driver"]
#chromedriver = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
#os.environ["webdriver.chrome.driver"]=chromedriver
browser = webdriver.PhantomJS()
wait = WebDriverWait(browser, 10)
browser.set_window_size(1400, 900)

def search_first_page():
    from selenium.common.exceptions import TimeoutException
    try:
        browser.get('https://www.taobao.com')
        input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
        #        EC.presence_of_element_located((By.CSS_SELECTOR, '##k'))
            )
        submit = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button"))
        #        EC.element_to_be_clickable((By.CSS_SELECTOR, '#su'))
            )
        input.send_keys('美食')
        print('打开首页完成，输入搜索信息...')
        submit.click()
        print('输入完成，点击搜索...')
        total = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total'))
            )
        parse_goods_info()
        return total.text
    except TimeoutException:
        return search_first_page()

def next_page(page_number):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit"))
        )
        input.clear()
        input.send_keys(page_number)
        print('输入页码',page_number)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number))
        )
        parse_goods_info()
        print('已翻页至第', page_number, '页')
    except TimeoutException:
        next_page(page_number)


def parse_goods_info():
    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-itemlist .items .item"))
        #    EC.presence_of_element_located((By.CSS_SELECTOR, "#J_itemlistPersonality > div > div:nth-child(12)"))
        )
        print('本页商品加载完成')
        html = browser.page_source
        doc = pq(html)
        items = doc('#mainsrp-itemlist .items .item').items()
        time.sleep(5)
        for item in items:
            goods = {
                'pic': item.find('.pic a').attr('href'),
                'good': item.find('.title').text(),
                'price': item.find('.price').text(),
                'deal': item.find('.deal-cnt').text()[:-3],
                'shop': item.find('.shop').text(),
                'index': item.attr('data-index')
            }
            print(goods)
    except TimeoutException:
        parse_goods_info()

def main():
    total = search_first_page()
    #total = int(re.compile('(\d+)').search(total).groups(1))
    for i in range(2, 3):
        next_page(i)

if __name__ == '__main__':
    main()