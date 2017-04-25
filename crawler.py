import sys
import re
import json
import time
import requests
from lxml import etree
from bs4 import BeautifulSoup

stock_list_url = "http://quote.eastmoney.com/stocklist.html"
stock_info_url="http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id=%s&token=beb0a0047196124721f56b0f0ff5a27c"
# stock_info_url="http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id=3000332&token=beb0a0047196124721f56b0f0ff5a27c"

def main():
    try:

        stock_list = reqStockList()
        stock_list = cleanStock(stock_list)
        reqStockTradeInfo(stock_list)

    except Exception as e:
        print('执行主函数失败->%s'%(str(e)))

def cleanStock(stock_list):
    __stock_list = list()
    try:
        for stock in stock_list:
            stock_info = ''.join(stock).strip()
            stock = __filter__(stock_info)
            if stock:
                __stock_list.append(stock)
            else:
                continue

    except Exception as e:
        print(str(e))

    return __stock_list

def __filter__(stock_name):
    try:
        stock_code = re.search(r'\((.*?)\)', stock_name).group(1)
        stock_name = re.search(r'(.*?)\(', stock_name).group(1)

        # if stock_code.startswith('3'):
        if stock_code.startswith('6') or stock_code.startswith('3') or stock_code.startswith('0'):
            return (stock_code, stock_name)
        else:
            return None

    except Exception as e:
        # print('过滤失败->%s'%(str(e)))
        return None

def generateUrl(stock_code):
    try:
        if stock_code.startswith('6'):
            stock_code = stock_code + u'1'
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            stock_code = stock_code + u'2'
        else:
            pass

        url = stock_info_url%(stock_code)
        return url
    except:
        return None

def storeTradeData(html):
    try:
        a = bytes.decode(html)
        text = re.search(r'({.*?})', a).group(1)
        data = json.loads(text)
        value = data['Value']
        value = ','.join(value)+'\n'
        fp.writelines(value)

    except Exception as e:
        print('存储数据失败->%s'%(str(e)))

def reqStockTradeInfo(stock_list):
    try:
        for stock in stock_list:
            url = generateUrl(stock[0])
            if not url:
                continue

            print('请求url->%s'%(url))
            res = requests.get(url)
            html = res._content
            storeTradeData(html)
            time.sleep(0.1)

    except Exception as e:
        print('请求股票详细失败->%s'%(str(e)))

def reqStockList():
    stock_list = list()

    try:
        res = requests.get(stock_list_url)
        html = res._content
        html = html.decode("gbk")

        #这里有坑,lxml解析会导致数据丢失，强烈建议以后解析都用html.parser !!!
        soup = BeautifulSoup(html, 'html.parser')
        # soup = BeautifulSoup(html, 'lxml')
        html = soup.prettify()
        tree = etree.HTML(html)
        stock_list = tree.xpath('.//li/a/text()')
    except Exception as e:
        print('获取股票列表失败->%s'%(str(e)))

    return stock_list

if __name__ == "__main__":
    t = time.strftime('%Y_%m_%d')
    fp = open('stock_trade_data_%s.csv'%(str(t)), 'w')
    main()
    fp.close()