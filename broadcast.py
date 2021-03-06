# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
import re
import time
from bs4 import BeautifulSoup
from flask import Flask, request
from firebase import Firebase

import random


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
    }
]


def send_news():
    fb = Firebase('https://welse-141512.firebaseio.com/items')
    old_items = fb.get()
    if(old_items == None):
        old_items = scrap()

    new_items = scrap()
    new_send = getNew(old_items, new_items)
    counts = 0
    el = []

    users_fb = Firebase('https://welse-141512.firebaseio.com/ocz/')
    users = users_fb.get()
    for u in users:
        user = Firebase('https://welse-141512.firebaseio.com/ocz/' + str(u))
        user_data = user.get()
        for type_u in user_data:
            if(user_data[type_u]['subcribe'] == 1):
                print new_send[type_u]
                if len(new_send[type_u]) != 0:
                    el = []

                    for item in new_send[type_u]:
                        el.append({
                            "title": item['name'],
                            "subtitle": item['subtitle'],
                            "image_url": item['image'],
                            "buttons": [{
                                "title": "View",
                                "type": "web_url",
                                "url": item['link'],
                            },
                            {
                                "type":"element_share"
                            }],
                            "default_action": {
                                "type": "web_url",
                                "url": item['link']
                            }
                        })
                        print counts
                        if(counts >= 9 or new_send[type_u][-1]['name'] == item['name']):
                            print "send"
                            send_message(u, 'ใหม่!! ' + str(type_u) + ' ' + str(len(el)) + ' กระทู้ฝอยจัดให้!!')
                            send_generic(u, el)
                            r = random.uniform(0, 1)
                            counts = 0
                            el = []
                            break
                        counts += 1
                else:
                    r = random.uniform(0, 1)
                    # if r > 0.98:
                        # send_message(u, 'ตลาดเงียบเหงาโคตร แต่ไม่ต้องกลัว ฝอยคอยจับตาดูให้อยู่ตลอด')
    fb.set(new_items)

def send_generic(recipient_id, elements):
    print "sending to " + str(recipient_id)
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
            "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements
                }
            },
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_message(recipient_id, message_text):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text,
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def log(message):  
    print str(message)
    sys.stdout.flush()

def convert(content):
    content = content.lower();
    ret = re.sub('[!=@\-\*/:"]+',"", content);
    ret = re.sub("[\s]+", " ", ret);
    return ret

def scrap():
    items = {}
    for slug in type_item:
        print "Loading:",slug['slug']
        if not items.has_key('mobile'):
            items[slug['slug']] = []
        for i in xrange(1,3):
            url = "https://www.overclockzone.com/forums/forumdisplay.php/"+slug['value']+"/page" + str(i) + "?prefixid=Sell"
            r  = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data, "html.parser")
            for item in soup.find_all('div', {'class':'inner'}):
                if("Today" in item.find_all('span',{'class':'label'})[0].get_text()):
                    for title in item.find_all('a', {'class':'title'}):
                        items[slug['slug']].append(
                            {
                                'name': convert(title.get_text()),
                                'subtitle': item.find_all('span', {'class':'label'})[0].get_text().split(",")[0],
                                'link': "https://www.overclockzone.com/forums/" +title['href'],
                                'type': slug['slug'],
                                'image': slug['image']
                            }
                        )
    return items

def getNew(old,new):
    new_i = {}
    for t in type_item:
        new_i[t['slug']] = []
        for n in new[t['slug']]:
            found = 0
            if old.has_key(t['slug']):
                for o in old[t['slug']]:
                    if o:
                        if n['name'] == o['name']:
                            found = 1
                if not found:
                    new_i[t['slug']].append(n)
            else:
                new_i[t['slug']].append(n)
    return new_i

if __name__ == '__main__':
    send_news()