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
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    data = request.get_json()
    log(data)

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    if(not messaging_event["message"].has_key('text')):
                        break
                    message_text = messaging_event["message"]["text"].lower()  # the message's text

                    if Firebase('https://welse-141512.firebaseio.com/items/' + message_text).get() != None:
                        f = Firebase('https://welse-141512.firebaseio.com/items/' + message_text + '/page1')
                        items_array = f.get()
                        if items_array == None:
                            send_message(sender_id, "หมดแล้ว!! บ๋อแบ๋")
                            send_image(sender_id, "https://media.tenor.co/images/ab096f70ea512a3881e85756d3175c26/raw")
                            break
                        el = []
                        counts = 0
                        for item in items_array:
                            if (len(el) % 4 == 0 and len(el) != 0) or item['name'] == items_array[-1]['name']:
                                if len(el) <= 4:
                                    send_elements(sender_id, el, 2, item['type'])
                                else:
                                    send_generic(sender_id, el, 2, item['type'])
                                el = []
                                break
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
                            print item['name']
                            print el
                            counts += 1
                    else:
                        pass
                        # send_message(sender_id, "เลือกตามเมนูดิเห้ย !! เดี๋ยวตบหัวฟ่ำ!!")
                        # send_image(sender_id, "https://media.tenor.co/images/98c01672f3f5e6868d28d47ad4971a22/raw")


                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    if(not messaging_event["postback"].has_key('payload')):
                        break

                    if(messaging_event['postback']['payload'] == "done"):
                        send_message(sender_id, "โอเค อยากได้อะไรคราวหน้าบอกฝอยละกัน")
                        send_message(sender_id, "ใคร ๆ ก็รู้ ตลาดนี้ ฝอยคุม ง่อววว!")
                        uf = Firebase('https://welse-141512.firebaseio.com/ocz/' + str(sender_id))
                        uf.remove()
                        send_message(sender_id, "เอาเป็นว่าคราวหน้า ถ้าอยากได้อะไรก็ทักฝอยได้เลย")
                        break

                    if(messaging_event['postback']['payload'] == "menu"):
                        initial_conversation(sender_id, "หาไรอยู่ มีให้เลือกตามนี้ จิ้มเลย เดะฝอยจะเช็คตลาดให้")
                        break

                    if(messaging_event["postback"]["payload"] == 'hey'):
                        send_message(sender_id, "เฮ้ โย่ว หวัดเด")
                        send_image(sender_id, "https://media.tenor.co/images/a4932ffb7bd04392cfd220e4cbd325f1/raw")
                        send_message(sender_id, "หาไรอยู่ บอกเลย!! เดะฝอยจะเช็คตลาดให้")
                        break

                    message_text = messaging_event["postback"]["payload"].split(",")[0].lower()
                    if(message_text == "sub"):
                        sub = messaging_event["postback"]["payload"].split(",")[1].lower()
                        if sub == "0":
                            uf = Firebase('https://welse-141512.firebaseio.com/ocz/' + str(sender_id))
                            uf.remove()
                            break
                        sub_type = messaging_event["postback"]["payload"].split(",")[2].lower()
                        uf = Firebase('https://welse-141512.firebaseio.com/ocz/' + str(sender_id) + "/" + sub_type)
                        uf.set({"subcribe": sub})
                        if(sub == "1"):
                            send_message(sender_id, "EZ มาก เดะฝอยดูตลาดให้")
                            send_message(sender_id, "ของมาปั๊บ ทักหาทันที สวย ๆ อยากได้ไรเพิ่มบอกฝอย!!")
                            send_message(sender_id, "อยากดูอะไรเพิ่มอีกก็บอกฝอยได้เลยนะจ๊ะ")
                            
                    page = messaging_event["postback"]["payload"].split(",")[1]
                    if not page:
                        break
                    if Firebase('https://welse-141512.firebaseio.com/items/' + message_text).get() != None:
                        f = Firebase('https://welse-141512.firebaseio.com/items/' + message_text + '/page' + str(page))
                        items_array = f.get()
                        if items_array == None:
                            send_message(sender_id, "หมดแล้ว!! บ๋อแบ๋")
                            send_image(sender_id, "https://media.tenor.co/images/ab096f70ea512a3881e85756d3175c26/raw")
                            send_message(sender_id, "อยากดูอะไรเพิ่มอีกก็บอกฝอยได้เลยนะจ๊ะ")
                            break
                        el = []
                        counts = 0
                        for item in items_array:
                            if len(el) % 4 == 0 or item['name'] == items_array[-1]['name']:
                                if len(el) > 1:
                                    print "send elements"
                                    send_elements(sender_id, el, next_page, item['type'])
                                else:
                                    print "send generic"
                                    send_generic(sender_id, el, next_page, item['type'])
                                el = []
                                break
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
                        if(next_page == 4):
                            send_subscribe(sender_id, message_text)
                    else:
                        pass
                        # send_message(sender_id, "เลือกตามเมนูดิเห้ย !! เดี๋ยวตบหัวฟ่ำ!!")
                        # send_image(sender_id, "https://media.tenor.co/images/98c01672f3f5e6868d28d47ad4971a22/raw")

    return "ok", 200

def send_image(recipient_id, image):
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
        "message":{
            "attachment":{
              "type":"image",
              "payload":{
                "url": image
              }
            }
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
            "quick_replies":[
              {
                "content_type":"text",
                "title":"Ram",
                "payload":"ram,1"
              },
              {
                "content_type":"text",
                "title":"Monitor",
                "payload":"monitor,1"
              },
              {
                "content_type":"text",
                "title":"Cpu",
                "payload":"cpu,1"
              },
              {
                "content_type":"text",
                "title":"Storage",
                "payload":"storage,1"
              },
              {
                "content_type":"text",
                "title":"Macbook",
                "payload":"macbook,1"
              },
              {
                "content_type":"text",
                "title":"Monitor",
                "payload":"monitor,1"
              },
              {
                "content_type":"text",
                "title":"Toys",
                "payload":"toys,1"
              }
            ]
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_subscribe(recipient_id, message_text):
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
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"button",
                "text": "ดู " + message_text + " เยอะขนาดนี้ ให้ฝอยช่วยดูของให้ไหม ของใหม่มา ทักหาทันที" ,
                "buttons":[
                  {
                    "type":"postback",
                    "title":"สนใจ",
                    "payload": "sub,1," + message_text
                  }
                ]
              }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def initial_conversation(recipient_id, message_text):
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
                    "elements": [{
                        "title": "ตลาด Ram",
                        "subtitle": "ตลาดแรมเด็ดๆ จาก ocz",
                        "image_url": "http://dc.lnwfile.com/ezq63n.jpg",
                        "buttons": [{
                            "title": "ดูตลาด Ram",
                            "type": "postback",
                            "payload": "sub,1,ram"
                        }]
                    },{
                        "title": "ตลาด CPU",
                        "subtitle": "ตลาดซีพียูเด็ดๆ จาก ocz",
                        "image_url": "http://www.videoeditingsage.com/images/Computer12.jpg",
                        "buttons": [{
                            "title": "ดูตลาด CPU",
                            "type": "postback",
                            "payload": "sub,1,cpu"
                        }]
                    },{
                        "title": "ตลาด Monitor",
                        "subtitle": "ตลาดจอเด็ดๆ จาก ocz",
                        "image_url": "http://pisces.bbystatic.com/BestBuy_US/store/ee/2016/com/misc/flex_all_monitors5029703.jpg;maxHeight=460;maxWidth=460",
                        "buttons": [{
                            "title": "ดูตลาด Monitor",
                            "type": "postback",
                            "payload": "sub,1,monitor"
                        }]
                    },{
                        "title": "ตลาด Storage",
                        "subtitle": "ตลาด HDD, SSD เด็ดๆ จาก ocz",
                        "image_url": "http://topicstock.pantip.com/wahkor/topicstock/2008/11/X7197552/X7197552-0.jpg",
                        "buttons": [{
                            "title": "ดูตลาด Storage",
                            "type": "postback",
                            "payload": "sub,1,storage"
                        }]
                    },{
                        "title": "ตลาด Macbook",
                        "subtitle": "ซื้อ ขาย แลกเปลี่ยน MacBook ทุกรุ่น MacBook, MacBook Pro, MacBook Air",
                        "image_url": "https://support.apple.com/content/dam/edam/applecare/images/en_US/macbook/psp-mini-hero-macbook_2x.png",
                        "buttons": [{
                            "title": "ดูตลาด Macbook",
                            "type": "postback",
                            "payload": "sub,1,macbook"
                        }]
                    },
                    {
                        "title": "ตลาดของเล่น",
                        "subtitle": "ซื้อ ขาย แลกเปลี่ยน ของเล่น เกมส์ และอุปกรณ์ที่เกี่ยวข้อง ทุกชนิด",
                        "image_url": "http://www.gadgetguysnc.com/wp-content/uploads/2016/01/consoles.jpg",
                        "buttons": [{
                            "title": "ดูตลาดของเล่น",
                            "type": "postback",
                            "payload": "sub,1,toys"
                        }]
                    }]
                }
            }
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
                            "title": "ดูอีก",
                            "type": "postback",
                            "payload": item_type+","+str(page)                        
                        }
                    ]  
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_generic(recipient_id, elements, page, item_type):
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
                    "elements": elements,
                    "buttons": [
                        {
                            "title": "ดูอีก",
                            "type": "postback",
                            "payload": item_type+","+str(page)                        
                        }
                    ]  
                }
            },
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def log(message):  
    print str(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)
