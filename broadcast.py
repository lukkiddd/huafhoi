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

def send_news():
    fb = Firebase('https://welse-141512.firebaseio.com/item_list')
    old_items = fb.get()
    if(old_items == None):
        old_items = scrap()

    new_items = scrap()
    new_items = getNew(old_items, new_items)
    counts = 0
    el = []
    broadcast_text("Checking:: " + str(len(old_items)) + " | " + str(len(new_items)))
    broadcast_text(str(len(new_items) - len(old_items)) + ' อัพเดทใหม่จ้า')
    if( len(new_items) == len(old_items) ):
        broadcast_text("ยังไม่มีของใหม่นะ")
    else:
        for item in new_items:
            if counts == 1:
                broadcast_element(el, 2, item['type'])
                counts = 0
                el = []
            el.append(
                {
                    "title": item['name'],
                    "subtitle": item['subtitle'],
                    "image_url": item['image'],
                    "buttons": [{
                        "title": "View",
                        "type": "web_url",
                        "url": item['link'],
                    }],
                    "default_action": {
                        "type": "web_url",
                        "url": item['link']
                    }
                }
            )
            counts += 1
    fb.set(new_items)

def broadcast_text(message_text):
    f = Firebase('https://welse-141512.firebaseio.com/ocz/')
    user = f.get()
    for u in user:
        send_message(u, message_text)

def broadcast_element(elements, page, item_type):
    f = Firebase('https://welse-141512.firebaseio.com/ocz/')
    user = f.get()
    for u in user:
        send_elements(u, elements, page, item_type)

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
            "quick_replies":[
              {
                "content_type":"text",
                "title":"Ram",
                "payload": "ram,1"
              },
              {
                "content_type":"text",
                "title":"Monitor",
                "payload": "monitor,1"
              },
              {
                "content_type":"text",
                "title":"CPU",
                "payload": "cpu,1"
              },
              {
                "content_type":"text",
                "title":"Storage",
                "payload": "storage,1"
              }
            ]
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_elements(recipient_id, elements, page, item_type):
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
                    "template_type": "list",
                    "top_element_style": "compact",
                    "elements": elements,
                    "buttons": [
                        {
                            "title": "View More",
                            "type": "postback",
                            "payload": item_type+","+str(page)                        
                        }
                    ]  
                }
            },
            "quick_replies":[
              {
                "content_type":"text",
                "title":"Ram",
                "payload": "ram,1"
              },
              {
                "content_type":"text",
                "title":"Monitor",
                "payload": "monitor,1"
              },
              {
                "content_type":"text",
                "title":"CPU",
                "payload": "cpu,1"
              },
              {
                "content_type":"text",
                "title":"Storage",
                "payload": "storage,1"
              }
            ]
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

def convert(content):
    content = content.lower();
    ret = re.sub('[!=@\-\*/:"]+',"", content);
    ret = re.sub("[\s]+", " ", ret);
    return ret

def scrap():
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
    items = []
    for slug in type_item:
        print "Loading:",slug['slug']
        for i in xrange(1,5):
            url = "https://www.overclockzone.com/forums/forumdisplay.php/"+slug['value']+"/page" + str(i) + "?prefixid=Sell"
            r  = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data)
            for item in soup.find_all('div', {'class':'inner'}):
                if("Today" in item.find_all('span',{'class':'label'})[0].get_text()):
                    for title in item.find_all('a', {'class':'title'}):
                        items.append(
                            {
                            'name': convert(title.get_text()),
                            'subtitle': item.find_all('span', {'class':'label'})[0].get_text(),
                            'link': "https://www.overclockzone.com/forums/" +title['href'],
                            'type': slug['slug'],
                            'time': item.find_all('span', {'class':'label'})[0].get_text().split(",")[1],
                            'image': slug['image']
                            }
                          )
    return items

def getNew(old,new):
    oldlen = len(old)
    new_item = new
    print "Checking New"
    if(oldlen != len(new)):
        for i in new:
            if i not in new_item:
                new_item.append(i)
        oldlen = len(new)
    return new_item

if __name__ == '__main__':
    send_news()