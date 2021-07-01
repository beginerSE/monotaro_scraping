import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
import os
import csv
import traceback

# ファイル名をからカテゴリ番号を取得
pyfile_name = os.path.basename(__file__)
category_num = int(pyfile_name[-5:-3])
print(pyfile_name, category_num)

home_url = 'https://www.monotaro.com'

headers = {
    'User-Agent':'Mozilla/5.0',
    "referer":home_url,
    "authority":home_url
}

# 税率10%
tax_rate = 1.1

# ページに表示される検索数(現在のところ40)
page_search_result_count = 40


# 目当ての各商品上を格納するリスト
product_content_data = []

df = pd.read_csv('monotaro_bigmiddle_category_list.csv', encoding='CP932')
link_data = df[df['カテゴリ番号'] == category_num]

# csvに書き出す準備(エンコードエラーが出る場合はerrors='ignore'を付けるかエンコーディングをUTF-8にする)
f = open('monotaro_product_data' + str(category_num) +'.csv', 'w', encoding='cp932',  newline="", errors='ignore')
writer = csv.writer(f)

csv_header = 'カテゴリNo','所属カテゴリ名1','所属カテゴリ名2','所属カテゴリ名3', '所属カテゴリ名4', \
             '所属カテゴリURL1', '所属カテゴリURL2', '所属カテゴリURL3', '所属カテゴリURL4',\
             'メーカー名', 'バリュエーションNo', 'バリュエーションURL', 'バリュエーション名',\
             'キャッチコピー', '注意書き', '注文コード', '自ページurl', '商品名', '商品内容量', '各種情報', \
             '内容量', '品番', '販売価格(税込み)', '定期注文価格(税込)', '販売価格(税抜き)',\
             '補足情報', '商品キャッチコピー', '各種情報',

writer.writerow(csv_header)

def get_product_data(list_, url_, df_data, headers=headers):
    print(47, url_)
    res = requests.get(url_, headers=headers)
    product_soup = BeautifulSoup(res.content, "html.parser") # 詳細カテゴリーに該当する商品リスト
    total_search_count = product_soup.find_all('div', class_='citem_count')[0].find_all('strong')[0].text.replace(",","")
    # 最初のページの商品情報を取得する
    product_url_list = []
    first_product_url = product_soup.find_all('div', class_='item first_item variation_item data-ee-imp')[0].find_all('a',class_='product_name')[0].get('href')
    product_url_list.append(first_product_url)
    try:
        other_product_url = product_soup.find_all('div', class_='item variation_item data-ee-imp')
        if len(other_product_url) >= 1:
            for one_product_data in other_product_url:
                product_url = one_product_data.find_all('a',class_='product_name')[0].get('href')
                product_url_list.append(product_url)
    except:
        pass
    try:
        other_product_url2 = product_soup.find_all('div', class_='item variation_item abolition_item data-ee-imp')
        if len(other_product_url2) >= 1:
            for one_product_data in other_product_url2:
                product_url = one_product_data.find_all('a',class_='product_name')[0].get('href')
                product_url_list.append(product_url)
    except:
        pass
    try:
        last_product_url = product_soup.find_all('div', class_='item last_item variation_item abolition_item data-ee-imp')[0].find_all('a',class_='product_name')[0].get('href')
        product_url_list.append(last_product_url)
    except:
        last_product_url = product_soup.find_all('div', class_='item last_item variation_item data-ee-imp')[0].find_all('a',class_='product_name')[0].get('href')
        product_url_list.append(last_product_url)
    finally:
        pass
    roop_count = int(total_search_count) // page_search_result_count
    #print('product_url_list', len(product_url_list))
    #print('ページ数',roop_count+1)
    # 複数ページある場合は、2ページ目以降の商品情報も取得する
    if roop_count > 0 and int(total_search_count) != page_search_result_count:
        for page in range(2, roop_count+2):
            if page == roop_count+1:
                #print('最終ページ')
                final_product_pagelink = url_ + 'page-' + str(page)
                res = requests.get(final_product_pagelink, headers=headers)
                #print(final_product_pagelink)
                final_product_soup = BeautifulSoup(res.content, "html.parser") # 詳細カテゴリーに該当する商品リスト
                try:
                    final_first_product_url = final_product_soup.find_all('div', class_='item first_item variation_item abolition_item data-ee-imp')[0].find_all('a',class_='product_name')[0].get('href')
                except:
                    final_first_product_url = final_product_soup.find_all('div', class_='item first_item variation_item data-ee-imp')[0].find_all('a',class_='product_name')[0].get('href')
                product_url_list.append(final_first_product_url)
                try:
                    final_other_product_data = final_product_soup.find_all('div', class_='item variation_item abolition_item data-ee-imp')
                    if len(final_other_product_data) >= 1:
                       for final_one_product_data in final_other_product_data:
                            final_product_url = final_one_product_data.find_all('a',class_='product_name')[0].get('href')
                            product_url_list.append(final_product_url)
                except:
                    pass
                try:
                    final_other_product_data2 = final_product_soup.find_all('div', class_='item variation_item data-ee-imp')
                    if len(final_other_product_data2) >= 1:
                        for final_one_product_data in final_other_product_data2:
                            final_product_url = final_one_product_data.find_all('a',class_='product_name')[0].get('href')
                            product_url_list.append(final_product_url)
                except:
                    pass
                try:
                    final_last_product_url = final_product_soup.find_all('div', class_='item last_item variation_item abolition_item data-ee-imp')[0].find_all('a',class_='product_name')[0].get('href')
                    product_url_list.append(final_last_product_url)
                except:
                    final_last_product_url = final_product_soup.find_all('div', class_='item last_item variation_item data-ee-imp')[0].find_all('a',class_='product_name')[0].get('href')
                    product_url_list.append(final_last_product_url)
                finally:
                    break
            else:
                next_product_pagelink = url_ + 'page-' + str(page)
                res = requests.get(next_product_pagelink, headers=headers)
                next_product_soup = BeautifulSoup(res.content, "html.parser") # 詳細カテゴリーに該当する商品リスト
                #next_product_count = next_product_soup.find_all('div', class_='citem_count')[0].find_all('strong')[0].text # 詳細カテゴリー数
                try:
                    next_first_product_url = next_product_soup.find_all('div', class_='item first_item variation_item abolition_item data-ee-imp')[0].find_all('a',class_='product_name')[0].get('href')
                except:
                    next_first_product_url = next_product_soup.find_all('div', class_='item first_item variation_item data-ee-imp')[0].find_all('a',class_='product_name')[0].get('href')
                product_url_list.append(next_first_product_url)
                try:
                    next_other_product_data = next_product_soup.find_all('div', class_='item variation_item data-ee-imp')
                    if len(next_other_product_data) >= 1:
                        for next_one_product_data in next_other_product_data:
                            next_product_url = next_one_product_data.find_all('a',class_='product_name')[0].get('href')
                            product_url_list.append(next_product_url)
                except:
                    pass

                try:
                    next_other_product_data2 = next_product_soup.find_all('div', class_='item variation_item abolition_item data-ee-imp')
                    if len(next_other_product_data2) >= 1:
                        for next_one_product_data in next_other_product_data2:
                            next_product_url = next_one_product_data.find_all('a',class_='product_name')[0].get('href')
                            product_url_list.append(next_product_url)
                except:
                    pass

                try:
                    next_last_product_url = next_product_soup.find_all('div', class_='item last_item variation_item abolition_item data-ee-imp')[0].find_all('a',class_='product_name')[0].get('href')
                    product_url_list.append(next_last_product_url)
                except:
                    next_last_product_url = next_product_soup.find_all('div', class_='item last_item variation_item data-ee-imp')[0].find_all('a',class_='product_name')[0].get('href')
                    product_url_list.append(next_last_product_url)
                #time.sleep(3)
    print(url_, 'の該当件数は', len(product_url_list),'件です')
    #print(product_url_list)
    # 商品情報を取得する
    for product_individual_url in product_url_list:
        #print(86, product_individual_url)
        product_individual_url = home_url + product_individual_url
        res = requests.get(product_individual_url, headers=headers)
        product_individual_soup = BeautifulSoup(res.content, "html.parser") # 詳細カテゴリーに該当する商品リスト
        try:
            maker_name = product_individual_soup.find_all('div', class_='pd_brand_name itd_brand')[0].find_all('strong', class_='st pd_brand_name')[0].text
        except:
            maker_name = 'モノタロウ'
        description = product_individual_soup.find_all('div', class_='product_data-property')[0].text.replace( '\n' , '' )
        val_name = product_individual_soup.find_all('h1', class_='pd_product_name')[0].text
        try:
            caution_text = product_individual_soup.find_all('dl', class_='product_data_caution')[0].find_all('dd', class_='product_data_caution-content')[0].text
        except:
            caution_text = ''
        order_number_list = product_individual_soup.find_all('div', class_='products_details')[0].find_all('tr', class_='pd_list data-ee-sku')
        categorys = product_individual_soup.find_all('div', class_='cl_parents breadcrumb-mdata clearfix')[0].find_all('li')
        category_list = []
        for category in categorys:
            if category.text != '工具の通販モノタロウ':
                category_list.append(category.text)
        # 各商品コードの個別ページの情報をスクレイピング
        for order_code in order_number_list:
            #print('order_number_list', len(order_number_list))
            order_number_path = order_code.find_all('td', class_='pd_list')[0].find_all('a')[0].get('href')
            code = order_code.find_all('td', class_='pd_list')[0].text
            val_url = home_url + order_number_path
            res = requests.get(val_url, headers=headers)
            order_number_soup = BeautifulSoup(res.content, "html.parser")
            product_name = order_number_soup.find_all('span', class_='TextLink')[0].text
            try:
                product_volume = order_number_soup.find_all('span', class_='ProductName__Sub')[0].text
            except:
                product_volume = ''
            tag_list = []
            tags = order_number_soup.find_all('span', class_='Label Label--Md Label--ShipToday Label--ShippingSpeed u-FontSize--Default')
            for tag in tags:
                tag_list.append(tag.text)
            content_infos = order_number_soup.find_all('div', class_='u-Table')[0].find_all('span', class_='AttributeLabel__Wrap')
            code_number = ''
            content_value = ''
            for content_info in content_infos:
                #print(content_info.text)
                if '内容量' in content_info.text:
                    content_value = content_info.text
                if '品番' in content_info.text:
                    code_number = content_info.text
            try:
                sell_price = int(re.sub(r"\D", "", order_number_soup.find_all('span', class_='Price Price--Lg')[0].text))
                tax_sell_price = int(sell_price * tax_rate)
            except:
                # 取り扱っていない場合は価格が表示されない
                sell_price = '' 
                tax_sell_price = ''
            try:
                sub_sell_price = int(re.sub(r"\D", "", order_number_soup.find_all('span', class_='Price Price--Md')[0].text))
                tax_sub_sell_price = int(sub_sell_price * tax_rate)
            except:
                sub_sell_price = ''
                tax_sub_sell_price = ''
            try:
                support_infomation = order_number_soup.find_all('span', class_='VariationText u-FontSize--Md')[0].text
            except:
                support_infomation = ''
            try:
                order_description = order_number_soup.find_all('div', class_='DescriptionArea')[0].text
            except:
                order_description = ''
            info_list = []
            try:
                infos = order_number_soup.find_all('div', class_='Section__Inner')[0].find_all('div', class_='AttributeLabel u-InlineMarginClear')[0].find_all('span', class_='AttributeLabel__Wrap')
                for info in infos:
                    info_list.append(info.text)
            except:
                pass
            if len(df_data) == 5:
                csv_data = [df_data[0], df_data[1], df_data[2], '', '', df_data[3], df_data[4],'','', maker_name, product_individual_url[27:-1], product_individual_url, val_name, description, caution_text, code, val_url, product_name, product_volume, tag_list, content_value, code_number, tax_sell_price, tax_sub_sell_price, sell_price, support_infomation, order_description, info_list]
                writer.writerow(csv_data)
            elif len(df_data) == 7:
                csv_data = [df_data[0], df_data[1], df_data[2], df_data[3], '', df_data[4],df_data[5], df_data[6],'', maker_name, product_individual_url[27:-1], product_individual_url, val_name, description, caution_text, code, val_url, product_name, product_volume, tag_list, content_value, code_number, tax_sell_price, tax_sub_sell_price, sell_price, support_infomation, order_description, info_list]
                writer.writerow(csv_data)
            elif len(df_data) == 9:
                csv_data = [df_data[0],df_data[1],df_data[2], df_data[3], df_data[4], df_data[5],df_data[6],df_data[7],df_data[8], maker_name,product_individual_url[27:-1], product_individual_url, val_name, description, caution_text, code, val_url, product_name, product_volume, tag_list, content_value, code_number, tax_sell_price, tax_sub_sell_price, sell_price, support_infomation, order_description, info_list]
                writer.writerow(csv_data)
            #print(csv_data)
        print(product_individual_url, '書き込み完了')
        #time.sleep(2)


ca_link_data = []

# csvを読み込んで該当カテゴリのものだけ抜粋
# 中カテゴリから小カテゴリを取得
for index, category_data in link_data.iterrows():
    category_data[3] = category_data[3].replace('\n', '')
    print('category_data', category_data)
    ca_link = home_url + category_data[-1]
    res = requests.get(ca_link, headers=headers)
    ca_soup = BeautifulSoup(res.content, "html.parser")
    try:
        ca_data = ca_soup.find_all('ul', class_="visualcategory-container")[0]
        ca_table_data = ca_data.find_all('li', class_="visualcategory-item")
        for sub_data in ca_table_data:
            ca_name =sub_data.find_all('div', class_="visualcategory-item_mainname")[0].text.replace('\n','')
            ca_url = sub_data.find_all('a')[0].get('href')
            #print(ca_name, ca_url) # 小カテゴリを表示
            ca_link_data.append([category_data[0], category_data[1],  category_data[3], ca_name, category_data[2], category_data[4],  ca_url])
            #time.sleep(2)
    except:
        try:
            get_product_data(product_content_data, ca_link, category_data)
        except:
            print("cエラー情報\n" + traceback.format_exc())
            print(179,res, ca_link)
            pass
        pass

print('ca_link_data', len(ca_link_data))

de_link_data = []

# 小カテゴリから詳細カテゴリを取得
for ca_data_one in ca_link_data:
    de_link = home_url + ca_data_one[-1]
    res = requests.get(de_link, headers=headers)
    de_soup = BeautifulSoup(res.content, "html.parser")
    print('de_link', de_link)
    try:
        de_data = de_soup.find_all('ul', class_="visualcategory-container")[0]
        de_table_data = ca_data.find_all('li', class_="visualcategory-item")
        for sub_sub_data in de_table_data:
            de_name = sub_sub_data.find_all('div', class_="visualcategory-item_mainname")[0].text.replace('\n','')
            de_url = sub_sub_data.find_all('a')[0].get('href')
            #print(de_name, de_url) # 詳細カテゴリを表示
            de_link_data.append([ca_data_one[0],ca_data_one[1],ca_data_one[2],ca_data_one[3], de_name, ca_data_one[4],ca_data_one[5],ca_data_one[6],  de_url])
    except:
        #try:
        #    get_product_data(product_content_data, de_link, ca_data_one)
        #except:
        #    print("dエラー情報\n" + traceback.format_exc()) #エラー発生時のエラー内容確認
        #    print(res, de_link)
        #    pass
        pass

print('例外カテゴリの処理完了、正規カテゴリの取得処理開始')
# 残りの詳細カテゴリの商品データを取得する
for de_product_link in de_link_data:
    get_product_data(product_content_data, home_url+de_product_link[-1], de_product_link)

# ファイルを閉じる
f.close()
