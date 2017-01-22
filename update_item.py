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
    }
]


def convert(content):
    content = content.lower();
    ret = re.sub('[!=@\-\*/:"]+',"", content);
    ret = re.sub("[\s]+", " ", ret);
    return ret

def scrap():
    items = {}
    for slug in type_item:
        c = 0
        page = 1
        print "Loading:",slug['slug']
        items[slug['slug']] = {}
        items[slug['slug']]['page'+str(page)] = []
        for i in xrange(1,5):
            url = "https://www.overclockzone.com/forums/forumdisplay.php/"+slug['value']+"/page" + str(i) + "?prefixid=Sell"
            r  = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data)
            for item in soup.find_all('div', {'class':'inner'}):
                if("Today" in item.find_all('span',{'class':'label'})[0].get_text() or
                    "Yesterday" in item.find_all('span',{'class':'label'})[0].get_text()):
                    for title in item.find_all('a', {'class':'title'}):
                        if c % 4 == 0 and c != 0:
                            c = 0
                            page += 1
                        if(not items[slug['slug']].has_key('page'+str(page))):
                            items[slug['slug']]['page'+str(page)] = []
                        # f = Firebase('https://welse-141512.firebaseio.com/items/'+slug['slug']+'/page'+str(page))
                        items[slug['slug']]['page'+str(page)].append(
                            {
                            'name': convert(title.get_text()),
                            'subtitle': item.find_all('span', {'class':'label'})[0].get_text(),
                            'link': "https://www.overclockzone.com/forums/" +title['href'],
                            'type': slug['slug'],
                            'time': item.find_all('span', {'class':'label'})[0].get_text().split(",")[1],
                            'image': slug['image']
                            },
                            )
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
# if f.get() == None:
f.set(items)
# else:
    # f.update(items)
# time.sleep(1)
# oldlen = 0
# count = 0
# c = 0
# page = 1
# new_item = []
# while(1):
#     items = scrap()
#     if(oldlen != len(items)):
#         for i in items:
#             if i not in new_item:
#                   f = Firebase('https://welse-141512.firebaseio.com/items/'+i['type']+'/page'+str(page))
#             	  f.push(i)
#             	  print(i['name'])
#                   c += 1
#             	  new_item.append(i)
#         oldlen = len(items)
#     time.sleep(1)
#     count += 1
