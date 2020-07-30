# -*- coding: utf-8 -*-
import requests
import shutil
import os
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def parse_page(url):
    """
    根据 url 下载页面并转换成 soup 对象
    :param url: 页面 url 链接
    :return: soup 对象
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }
    page = requests.get(url,headers=headers).content
    #print page
    return BeautifulSoup(page, 'html.parser')


def parse_page_num(soup):
    """
    解析页面，返回总页数
    :param soup: 页面 soup 对象
    :return: 总页数
    """
    total_page_num = 0
    page_div = soup.find('div', attrs={'class': 'page'})
    if page_div and page_div.span:
        page_span_str = page_div.span.string
        page_num_list = page_span_str.split(' / ')
        if len(page_num_list) == 2:
            total_page_num = int(page_num_list[1])
    return total_page_num


def parse_pic_names(soup):
    """
    解析页面，返回当前页面图片名
    :param soup: 页面 soup 对象
    :return: 图片名称列表
    """
    pic_names = []
    pic_a_list = soup.find_all('a', attrs={'class': 'mark'})
    for pic_a in pic_a_list:
        pic_a_href = pic_a['href']
        pic_url = pic_a_href.split('?')[0]
        pic_path_list = pic_url.split('/')
        pic_name = pic_path_list[len(pic_path_list) - 1]
        pic_names.append(pic_name)
    return pic_names

def parse_pic_infos(soup):
    pic_infos = []
    pic_a_list = soup.find_all('div', attrs={'class': 'item'})
    for pic_a in pic_a_list:
        pic_a_href = pic_a.find_all('a', attrs={'class': 'mark'})
        pic_url = pic_a_href[0]['href'].split('?')[0]
        pic_path_list = pic_url.split('/')
        pic_name = pic_path_list[len(pic_path_list) - 1]
        
        pic_a_desp = pic_a.find_all('div', attrs={'class': 'description'})
        pic_a_desp_h3 = pic_a_desp[0].find_all('h3')
        pic_desp = pic_a_desp_h3[0].string

        pic_a_cal = pic_a.find_all('p', attrs={'class': 'calendar'})
        pic_em = pic_a_cal[0].find_all('em', attrs={'class': 't'})
        pic_cal = pic_em[0].string

        pic_a_loc = pic_a.find_all('p', attrs={'class': 'location'})
        pic_loc = 'null'
        if len(pic_a_loc) > 0:
            pic_em = pic_a_loc[0].find_all('em', attrs={'class': 't'})
            pic_loc = pic_em[0].string

        pic_infos.append([pic_name, pic_desp, pic_cal, pic_loc])
    print 'pic infos %s' % pic_infos
    return pic_infos


def main():
    """ 爬虫主函数 """
    print '---------- Crawling Start ----------'
    base_page_url = 'https://bing.ioliu.cn'
    base_pic_url = 'http://h1.ioliu.cn/bing/%s_%s.jpg'
    all_pic_infos = []
    # 下载页面并转换成 soup 对象
    soup = parse_page(base_page_url)
    #print soup
    # 获取总页数
    total_page_num = 2#parse_page_num(soup)
    for page in xrange(total_page_num):
        print 'Processing page: %s' % (page + 1)
        page_url = base_page_url + '/?p=' + str(page + 1)
        soup = parse_page(page_url)
        # 获取当前页面所有图片名
        # pic_names = parse_pic_names(soup)
        pic_infos = parse_pic_infos(soup)
        all_pic_infos.extend(pic_infos)
    # 遍历所有图片名，解析并保存图片
    resolutions = ['1920x1200',
    '1920x1080',
    '1366x768',
    '1280x768',
    '1024x768',
    '800x600',
    '800x480',
    '768x1280',
    '720x1280',
    '640x480',
    '480x800',
    '400x240',
    '320x240',
    '240x320']
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }
    # 创建图片保存的目录
    file_dir = './wallpaper/'
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    for resolution in resolutions:
        resolution_dir = file_dir + resolution + '/'
        if not os.path.exists(resolution_dir):
            os.mkdir(resolution_dir)
    cnt = 0
    for pic_info in all_pic_infos:
        cnt = cnt + 1
        if cnt > 10:
            break
        pic_info_name = pic_info[2] + '.info'
        downloaded_resolutions = []
        for resolution in resolutions:
            img_url = base_pic_url % (pic_info[0], resolution)
            # pic_file_name = pic_info[2] + '_' + pic_info[3] + '_' + pic_info[0] + '_' + resolution + '_' + pic_info[1] + '.jpg'
            pic_file_name = pic_info[2] + '_' + pic_info[0] + '_' + resolution + '.jpg'
            print 'Get %s from %s' % (pic_file_name, img_url)
            img_stream = requests.get(img_url, stream=True, headers=headers)
            if img_stream.status_code == 200:
                with open(file_dir + resolution + '/' + pic_file_name, 'wb') as fw:
                    shutil.copyfileobj(img_stream.raw, fw)
                downloaded_resolutions.append(resolution)
        downloaded_size = len(downloaded_resolutions)
        downloaded_str = ''
        i = 0
        while i < downloaded_size - 1:
            downloaded_str = downloaded_str + downloaded_resolutions[i] + ','
            i = i + 1
            pass
        if downloaded_size > 0:
            downloaded_str = downloaded_str + downloaded_resolutions[downloaded_size - 1]
        f = open(file_dir + pic_info_name, 'wb')
        f.write('calendar:' + pic_info[2] + '\n' + 'location:' + pic_info[3] + '\n' + 'name:' + pic_info[0] + '\n' + 'description:' + pic_info[1] + '\n' + 'resolutions:' + downloaded_str)
        f.close()
    # 图片爬取结束
    print '---------- Crawling End ----------'

if __name__ == '__main__':
    main()
