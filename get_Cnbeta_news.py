import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
from datetime import datetime

HOMEPAGE_URL = 'https://www.cnbeta.com/'
JSON_URL = HOMEPAGE_URL + 'home/more'
AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36 OPR/52.0.2871.99'
HEADERS = {
    'User-Agent' :  AGENT,
    'Accept-Language' : 'zh-CN,zh;q=0.9',
    'referer' : HOMEPAGE_URL}

def get_resource(url, headers):
    try:
        r = requests.get(url, headers = headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        #print('URL: ' + r.url)
    except Exception as e:
        print(e)
        r = None
    finally:
        return r

def get_csrf(res):
    if res is None:
        return None, None
    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.head.find('title').get_text()
    param = soup.head.find(attrs={'name':'csrf-param'})['content']
    token = soup.head.find(attrs={'name':'csrf-token'})['content']
    print('Page Title: ' + title)
    #print(param + ' = ' + token)
    return {'param' : param, 'token' : token}

def get_timestamp_ms():
    return round(time.time()*1000)

def get_json_url(csrf, page):
    params = {}
    params['type'] = 'all'
    params['page'] = page
    params[csrf['param']] = csrf['token']
    params['_'] = get_timestamp_ms()
    params_str = urllib.parse.urlencode(params)
    return JSON_URL + '?&' + params_str

def get_latest_days_of_year(n):
    today = datetime.now().timetuple().tm_yday
    if today >= n:
        return range(today, today - n, -1)
    else:
        return range(today, 0, -1)

def print_news(news_data, days):
    if news_data['result'] is None:
        return True
    end = False
    for news in news_data['result']['list']:
        news_day = datetime.strptime(news['inputtime'], '%Y-%m-%d %H:%M').timetuple().tm_yday
        if news_day not in get_latest_days_of_year(days):
            end = True
            break
        print("{inputtime} {label[name]} {title:<40} {url_show}".format(**news))
    return end

def main():
    n = input("获取最近多少天的Cnbeta新闻:") or '1'
    homepage_res =  get_resource(HOMEPAGE_URL, HEADERS)
    csrf = get_csrf(homepage_res)

    days = int(n)
    page = 1
    end = False
    while not end:
        json_url = get_json_url(csrf, page)
        json_res = get_resource(json_url, HEADERS)
        news_data = json_res.json()
        end = print_news(news_data, days)
        page = page + 1

if __name__ == '__main__':
    main()
