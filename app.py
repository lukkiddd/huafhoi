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

app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    if(not messaging_event["message"].has_key('text')):
                        break
                    message_text = messaging_event["message"]["text"].lower()  # the message's text
                    uf = Firebase('https://welse-141512.firebaseio.com/ocz/' + str(sender_id))
                    uf.push(message_text)
                    if message_text == 'cpu' or message_text == 'ram' or message_text == 'monitor' or message_text == 'storage':
                        f = Firebase('https://welse-141512.firebaseio.com/items/' + message_text + '/page1')
                        items_array = f.get()
                        if items_array == None:
                            send_message(sender_id, "Nothing new!")
                            break
                        el = []
                        counts = 0
                        for item in items_array:
                            if counts == 4 :
                                break
                            # send_message(sender_id, 'https://welse-141512.firebaseio.com/items/' + message_text + '/page1/' + str(i))
                            # q = Firebase('https://welse-141512.firebaseio.com/items/' + message_text + '/page1/' + str(i))
                            # item = q.get()
                            # print("\n\n\n")
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
                        send_elements(sender_id, el, 2, item['type'])
                    else:
                        send_message(sender_id, "NO item from " + message_text + ' category')

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    if(not messaging_event["postback"].has_key('payload')):
                        break
                    message_text = messaging_event["postback"]["payload"].split(",")[0].lower()

                    page = messaging_event["postback"]["payload"].split(",")[1] 
                    if message_text == 'cpu' or message_text == 'ram' or message_text == 'monitor' or message_text == 'storage':
                        f = Firebase('https://welse-141512.firebaseio.com/items/' + message_text + '/page' + str(page))
                        items_array = f.get()
                        if items_array == None:
                            send_message(sender_id, "Nothing new!")
                            break
                        el = []
                        counts = 0
                        for item in items_array:
                            if counts == 4 :
                                break
                            # q = Firebase('https://welse-141512.firebaseio.com/items/' + message_text + '/page' + str(page) + '/' + i)
                            # item = q.get()
                            # print("\n\n\n")
                            el.append(
                                {
                                    "title": item['name'],
                                    "subtitle": item['subtitle'],
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
                        next_page = int(page) + 1
                        send_elements(sender_id, el, next_page, item['type'])
                    else:
                        send_message(sender_id, "NO item from " + message_text + ' category')

    return "ok", 200

def send_news(sender):
    old_items = scrap()
    while(1):
        send_message(sender, "CHECKING")
        new_items = scrap()
        new_items = getNew(old_items, new_items)
        counts = 0
        send_message(sender, "new: " + str(len(new_items)))
        send_message(sender, "old: " + str(len(old_items)))
        if( len(new_items) == 0 ):
            continue
        for item in new_items:
            if counts == 4:
                f = Firebase('https://welse-141512.firebaseio.com/ocz/')
                user = f.get()
                for u in user:
                    send_elements(u, el, 2, item['type'])
                break
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
        time.sleep(5)
        old_items = new_items

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

    # log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
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
        # {
        #     'slug': 'cpu',
        #     'value': '93-CPU',
        #     'image': 'https://www.iconexperience.com/_img/g_collection_png/standard/512x512/cpu2.png'
        # },
        # {
        #     'slug': 'monitor',
        #     'value': '158-Monitor',
        #     'image': 'https://www.iconexperience.com/_img/g_collection_png/standard/512x512/monitor.png'
        # },
        {
            'slug': 'ram',
            'value': '94-Memory-(RAM)',
            'image': 'http://th.seaicons.com/wp-content/uploads/2016/07/RAM-Drive-icon.png'
        }
        # {
        #     'slug': 'storage',
        #     'value': '96-Storage',
        #     'image': 'http://pngwebicons.com/upload/small/hard_disk_png9158.png'
        # }
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
    app.run(debug=True)
