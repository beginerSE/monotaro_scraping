import requests
import time
import pandas as pd
from bs4 import BeautifulSoup

url = 'https://www.monotaro.com/'

headers = {
    'User-Agent':'Mozilla/5.0',
    "referer":url,
    "authority":url
}


# モノタロウトップページの情報を取得
res=requests.get(url, headers= headers)
soup = BeautifulSoup(res.content, "html.parser")

link_data = []
category_class_num = 0

# 大カテゴリを取得
parse_data = soup.find_all('div', class_="category4column")[0].find_all('dl')
for data in parse_data:
    dt = data.find_all('dt')
    dds = data.find_all('dd')
    # 中カテゴリを取得
    for dd in dds:
        link_data.append([category_class_num, dt[0].get_text(), dt[0].find_all('a')[0].get('href'), dd.get_text()[1:], dd.find_all('a')[0].get('href')])
        print('カテゴリ:',link_data[-1])
    category_class_num += 1

# csvに出力する
df = pd.DataFrame(link_data, columns=['カテゴリ番号', '大カテゴリ', '大カテゴリURL', '中カテゴリ', '中カテゴリURL']).to_csv('monotaro_bigmiddle_category_list.csv', encoding='cp932', index=False)