import requests
from lxml import etree
import random
import time
import pandas as pd
from PIL import Image
import pytesseract
import re
import csv


# 多个请求头
def get_ua():
    user_agents = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 '
        'OPR/26.0.1656.60',
        'Opera/8.0 (Windows NT 5.1; U; en)',
        'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2 ',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 '
        'Safari/534.16',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 '
        'Safari/536.11',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 '
        'LBBROWSER',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X '
        'MetaSr 1.0',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE '
        '2.X'
        'MetaSr 1.0) ',
    ]
    user_agent = random.choice(user_agents)  # 随机选择一个ua
    return user_agent


def get_page(url):
    ua = get_ua()
    headers = {'User-Agent': ua}
    response = requests.get(url, headers=headers)   # 得到主页面html
    # print(response.text)

    tree = etree.HTML(response.text)
    # # result = tree.xpath("/html/body/section/div[3]/div[2]/div[1]/div[2]/h5/a/@href")
    room_list = tree.xpath("/html/body/section/div[3]/div[2]/div")
    # for room in room_list:
    #     href = room.xpath("./div[2]/h5/a/@href")
    #     print(href)          # href=['//wh.ziroom']
    # i = 1
    href_list = []
    house_info_list = []


    for room in room_list:
        href = room.xpath("./div[2]/h5/a/@href")
        if len(href) != 0:
            url_href = 'https:' + href[0]    # url_href = 'https://wh.ziroom.com/x/777603007.html'
            # print(url_href)
            response_href = requests.get(url_href, headers=headers)  # 进入子页面，得到响应
            #print(response_href.text)   # 子页面html
            tree = etree.HTML(response_href.text)
            name = tree.xpath("/html/body/div[1]/section/aside/h1/text()") # name = ['业主直租·光谷188国际社区·2居室']

            bgs = tree.xpath("/html/body/div[1]/section/aside/div[1]/i")
            # print(name)
            # print(bgs)
            price_list = []
            for bg in bgs:
                result = bg.xpath('./@style')
                imgs = re.finditer("position:(?P<position>.*?)px;.*?url\((?P<img_url>.*?)\)", result[0])
                #print(result)   # result = ['background-position:-62.48px;background-image: url(//static8.ziro]
                #print(imgs)
                for img in imgs:
                    position = img.group('position')
                    img_url = img.group('img_url')
                price_list.append(position)
            price = get_price(img_url, price_list)
            print(price)  # price = '3290'
            area = tree.xpath("/html/body/div[1]/section/aside/div[@class='Z_home_info']/div[1]/dl[1]/dd/text()")[0]
            # /html/body/div[1]/section/aside/div[3]/div[1]/dl[1]/dd
            house_type = tree.xpath("/html/body/div[1]/section/aside/div[@class='Z_home_info']/div[1]/dl[3]/dd/text()")[0]
            location = tree.xpath("/html/body/div[1]/section/aside/div[@class='Z_home_info']/ul/li[1]/span[2]/span/text()")[0]
            district = tree.xpath("/html/body/div[1]/div[3]/a[2]/text()")[0].strip()
            neighbourhood = district
            # print(area)
            # print(house_type)
            # print(location)
            # print(district)
            house_info_list.append([name, price, area,house_type,location,district,neighbourhood])

    response.close()
    response_href.close()
    return house_info_list


        # area = tree.xpath("/html/body/div[1]/section/aside/div[3]/div[1]/dl[1]/dd/text()")



def get_price(url, price_list):
    image = requests.get('https:' + url).content
    # 保存价格用图片到本地
    f = open('price.png', 'wb')
    f.write(image)
    f.close()
    # 调用函数（见下面函数定义）获取价格数字字符串
    text = get_price_text()
    # print(text)  # text = '7190864523'

    # 获取价格
    price = ''
    # print(price_list)
    for i in price_list:
        num = int(float(i) / -31.24)  # 对于不同情况中有折扣的是20，无折扣的是21.4
        price = price + text[num]
    return price


def get_price_text():
    # 给透明图片加白色背景
    im = Image.open('.\price.png')
    x, y = im.size
    try:
        p = Image.new('RGBA', im.size, (255, 255, 255))
        p.paste(im, (0, 0, x, y), im)
        p.save('.\price.png')
    except:
        pass

    # 获取图片中数字字符串
    text = pytesseract.image_to_string(Image.open(".\price.png"),
                                       config='--psm 10 --oem 3 -c tessedit_char_whitelist=1234567890',
                                       lang='eng')
    text = re.sub('\s', '', text)  # 将空格匹配成空字符

    return text


if __name__ == '__main__':
    pages = ['https://wh.ziroom.com/z/p{}/'.format(x) for x in
             range(35, 42)]
    f = open('wh_beike5.csv', 'w', encoding='utf-8',newline='')
    csvwriter = csv.writer(f)
    count = 0
    for page in pages:
        info_list = get_page(page)
        csvwriter.writerows(info_list)
        time.sleep(random.randint(3, 10))
        count +=1
        print('the ' + str(count) + ' page is sucessful')

# /html/body/section/div[3]/div[2]/div[1]/div[2]/h5/a
# 需要设置延时，怎么设置延时？
