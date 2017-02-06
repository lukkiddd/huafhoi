# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from os import system
import re
import time
from firebase import Firebase

type_item = [
    {
        'slug': 'cpu',
        'value': '93-CPU',
        'image': 'https://www.iconexperience.com/_img/g_collection_png/standard/512x512/cpu2.png',
        'keywords': [ u"cpu", u"ซีพียู"]
    },
    {
        'slug': 'monitor',
        'value': '158-Monitor',
        'image': 'https://www.iconexperience.com/_img/g_collection_png/standard/512x512/monitor.png',
        'keywords': [u"จอ",u"monitor",u"dell",u"lg",u"led",u"lcd"]
    },
    {
        'slug': 'ram',
        'value': '94-Memory-(RAM)',
        'image': 'http://th.seaicons.com/wp-content/uploads/2016/07/RAM-Drive-icon.png',
        'keywords': [u"แรม",u"ram",u"ddr"]
    },
    {
        'slug': 'storage',
        'value': '96-Storage',
        'image': 'http://pngwebicons.com/upload/small/hard_disk_png9158.png',
        'keywords': [u"hdd",u"ssd",u"harddisk",u"storage",u"hard disk",u"solid state drive",u"ฮาดดิส",u"ฮาร์ดดิส",u"ฮาร์ดดิสก์"]
    },
    {
        'slug': 'macbook',
        'value': '162-MacBook',
        'image': 'https://support.apple.com/content/dam/edam/applecare/images/en_US/macbook/psp-mini-hero-macbook_2x.png',
        'keywords': [u"แมค",u"macbook",u"mac",u"แมก"]
    },
    {
        'slug': 'toys',
        'value': '109-Toys',
        'image': 'http://www.gadgetguysnc.com/wp-content/uploads/2016/01/consoles.jpg',
        'keywords': [u"3ds",u"ps4",u"nintendo",u"play4",u"playstation 4"u"เพล"]
    },
    {
        'slug':'mobile',
        'value': '208-iPhone',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg',
        'keywords': [u"iphone",u"mobile",u"มือถือ",u"ไอโฟน",u"5s"]
    },
    {
        'slug': 'mobile',
        'value': '210-ASUS',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg',
        'keywords': [u"asus",u"mobile",u"มือถือ",u"zenphone"]
    },
    {
        'slug': 'mobile',
        'value': '166-SAMSUNG',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg',
        'keywords': [u"samsung",u"mobile",u"มือถือ"]
    },
    {
        'slug': 'mobile',
        'value': '167-HTC',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg',
        'keywords': [u"mobile",u"มือถือ",u"htc"]
    },
    {
        'slug': 'mobile',
        'value': '168-LG',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg',
        'keywords': [u"mobile",u"มือถือ",u"lg"]
    },
    {
        'slug': 'mobile',
        'value': '169-Motorola',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg',
        'keywords': [u"mobile",u"มือถือ",u"motorola",u"โมโต"]
    },
    {
        'slug': 'mobile',
        'value': '172-Sony',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg',
        'keywords': [u"mobile",u"xperia",u"sony",u"มือถือ"]
    },
    {
        'slug': 'gpu',
        'value': '97-Display',
        'image': 'http://di.lnwfile.com/_/di/_raw/pd/eg/76.jpg',
        'keywords': [u"การ์ดจอ",u"display card",u"กาดจอ",u"graphic card"]
    }
]

def scrap():
    items = []
    for slug in type_item:
        print "Loading:",slug['slug']
        for i in xrange(1,5):
            url = "https://www.overclockzone.com/forums/forumdisplay.php/"+slug['value']+"/page" + str(i) + "?prefixid=Sell"
            r  = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data)
            for item in soup.find_all('div', {'class':'inner'}):
                if("Today" in item.find_all('span',{'class':'label'})[0].get_text() or
                    "Yesterday" in item.find_all('span',{'class':'label'})[0].get_text()):
                    for title in item.find_all('a', {'class':'title'}):
                        keywords = re.split("\s+",convert(title.get_text()))
                        item_data = {
                            'name': convert(title.get_text()),
                            'subtitle': item.find_all('span', {'class':'label'})[0].get_text(),
                            'link': "https://www.overclockzone.com/forums/" +title['href'],
                            'type': slug['slug'],
                            'time': item.find_all('span', {'class':'label'})[0].get_text().split(",")[1],
                            'image': slug['image']
                        }
                        item_data['keywords'] = slug['keywords'][:]
                        for keyword in keywords:
                            if len(keyword) > 0:  
                                item_data['keywords'].append(keyword)
                        items.append(item_data)
    return items


def convert(content):
    content = content.lower();
    ret = re.sub('[!=@\-\*/:"]+',"", content);
    ret = re.sub("[\s]+", " ", ret);
    return ret

def sort_scrap_item(items):
    today_list = []
    yesterday_list = []
    totald = []
    for o in items:
        if "Today" in o['time']:
            today_list.append(o)
        else:
            yesterday_list.append(o)
    ntd = sorted(today_list, key=lambda k: k['time'], reverse=True)
    nyd = sorted(yesterday_list, key=lambda k: k['time'], reverse=True)
    totald = ntd + nyd
    return totald

def clear_firebase():
	a = f.get()
	if a != None:
		for i in a:
			q = Firebase('https://huafhoi.firebaseio.com/items_filter'+'/'+i)
			q.remove()


f = Firebase('https://huafhoi.firebaseio.com/items_filter');
clear_firebase()
items = scrap()
sorted_item = sort_scrap_item(items)
f.set(sorted_item)

