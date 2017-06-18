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
        'image': 'https://www.iconexperience.com/_img/g_collection_png/standard/512x512/cpu2.png'
    },
    {
        'slug': 'blackberry',
        'value': '171-BlackBerry',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg'
    },
    {
        'slug': 'monitor',
        'value': '158-Monitor',
        'image': 'https://www.iconexperience.com/_img/g_collection_png/standard/512x512/monitor.png'
    },
    {
        'slug': 'ram',
        'value': '94-Memory-(RAM)',
        'image': 'http://th.seaicons.com/wp-content/uploads/2016/07/RAM-Drive-icon.png'
    },
    {
        'slug': 'storage',
        'value': '96-Storage',
        'image': 'http://pngwebicons.com/upload/small/hard_disk_png9158.png'
    },
    {
        'slug': 'macbook',
        'value': '162-MacBook',
        'image': 'https://support.apple.com/content/dam/edam/applecare/images/en_US/macbook/psp-mini-hero-macbook_2x.png'
    },
    {
        'slug': 'toys',
        'value': '109-Toys',
        'image': 'http://www.gadgetguysnc.com/wp-content/uploads/2016/01/consoles.jpg'
    },
    {
        'slug': 'gpu',
        'value': '97-Display',
        'image': 'http://di.lnwfile.com/_/di/_raw/pd/eg/76.jpg',
    },
    {
        'slug':'mobile',
        'value': '208-iPhone',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg'
    },
    {
        'slug': 'mobile',
        'value': '210-ASUS',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg'
    },
    {
        'slug': 'mobile',
        'value': '166-SAMSUNG',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg'
    },
    {
        'slug': 'mobile',
        'value': '167-HTC',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg'
    },
    {
        'slug': 'mobile',
        'value': '168-LG',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg'
    },
    {
        'slug': 'mobile',
        'value': '169-Motorola',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg'
    },
    {
        'slug': 'mobile',
        'value': '172-Sony',
        'image': 'http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg'
    }
]


def convert(content):
    content = content.lower();
    ret = re.sub('[!=@\-\*/:"]+',"", content);
    ret = re.sub("[\s]+", " ", ret);
    return ret

def sort_scrap_item(items):
    today_list = {}
    yesterday_list = {}
    totald = {}
    for key in items:
        today_list[key] = []
        yesterday_list[key] = []
        for o in items[key]:
            if "Today" in o['time']:
                today_list[key].append(o)
            else:
                yesterday_list[key].append(o)
        ntd = sorted(today_list[key], key=lambda k: k['time'], reverse=True)
        nyd = sorted(yesterday_list[key], key=lambda k: k['time'], reverse=True)
        totald[key] = ntd + nyd
    return totald

def create_item_page(items):
    new_list = {}
    for key in items:
        count = 0
        page = 1
        new_list[key] = {}
        new_list[key]["page"+str(page)] = []
        for item in items[key]:
            if(count % 4 == 0 and count != 0):
                count = 0
                page += 1
                new_list[key]["page"+str(page)] = []
            new_list[key]["page"+str(page)].append(item)
            count += 1
    return new_list

def scrap():
    items = {}
    for slug in type_item:
        if slug['slug'] != 'mobile' or not items.has_key('mobile'):
            c = 0
            page = 1
            items[slug['slug']] = []

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
                        item_data = {
                            'name': convert(title.get_text()),
                            'subtitle': item.find_all('span', {'class':'label'})[0].get_text(),
                            'link': "https://www.overclockzone.com/forums/" +title['href'],
                            'type': slug['slug'],
                            'time': item.find_all('span', {'class':'label'})[0].get_text().split(",")[1],
                            'image': slug['image']
                            }
                        items[slug['slug']].append(item_data)
                        c += 1
    return items

def clear_firebase():
	a = f.get()
	if a != None:
		for i in a:
			q = Firebase('https://welse-141512.firebaseio.com/items'+'/'+i)
			q.remove()


f = Firebase('https://welse-141512.firebaseio.com/items');
clear_firebase()
items = scrap()
sorted_item = sort_scrap_item(items)
paged_item = create_item_page(sorted_item)
f.set(paged_item)

