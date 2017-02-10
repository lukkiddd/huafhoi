# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
import re
import time
from bs4 import BeautifulSoup
from flask import Flask, request, render_template
from firebase import Firebase
import random
import urllib

app = Flask(__name__, static_url_path='')

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return render_template('index.html')
    # return "Hello world", 200

@app.route('/beta', methods=['GET'])
def beta():
    return render_template('beta.html')

@app.route('/policy', methods=['GET'])
def policy():
    return render_template('policy.html')

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
                        return "ok", 200

                    message_text = messaging_event["message"]["text"].lower()  # the message's text

                    if u"หาร้าน" in message_text:
                        message_text_split = message_text.split(' ')
                        if len(message_text_split) > 1:
                            query_restaurant = message_text_split[1]
                        else:
                            send_message(sender_id, "ร้านอะไรไม่บอก บุฟเฟ่ต์ แน่ๆ จัดไป")
                            query_restaurant = "บุฟเฟต์"
                        restaurants = scrap_restaurant(query_restaurant);
                        el = []
                        for rest in restaurants:
                            el.append({
                                "title": rest['title'],
                                "subtitle": "Rating: " + str(rest['rating']),
                                "image_url": rest['image'],
                                "buttons": [{
                                    "title": u"แผนที่",
                                    "type": "web_url",
                                    "url": rest['map_link'],
                                },{
                                    "title": u"รายละเอียด",
                                    "type": "web_url",
                                    "url": rest['link'],
                                }
                                ],
                                "default_action": {
                                    "type": "web_url",
                                    "url": rest['link']
                                }})
                            if len(el) == 10 or rest['title'] == restaurants[-1]['title']:
                                    send_generic(sender_id, el, 2, rest['link'])
                                    send_message(sender_id, "ขอให้อิ่มหนำสำราญ~!!")
                                    return "ok", 200
                        return "ok", 200
                    # if u"เลิกติดตามหนัง" in message_text:
                    #     movies = Firebase('https://welse-141512.firebaseio.com/submovies/' + str(sender_id));
                    #     movies.remove();
                    #     return "ok", 200

                    # if u"ตามหนัง" in message_text:
                    #     movie_name = message_text.split(" ")[1].lower()
                    #     movies = Firebase('https://welse-141512.firebaseio.com/movies').get();
                    #     el = []
                    #     for m in movies:
                    #         if movie_name in m['title']:
                    #             el.append({
                    #                 "title": m['title'],
                    #                 "subtitle": "imdb " + str(m['imdb']),
                    #                 "image_url": m['image'],
                    #                 "buttons": [{
                    #                     "title": u"ดู",
                    #                     "type": "web_url",
                    #                     "url": m['link'],
                    #                 }],
                    #                 "default_action": {
                    #                     "type": "web_url",
                    #                     "url": m['link']
                    #                 }})
                    #             send_generic(sender_id, el, 2, m['link'])
                    #             send_message(sender_id, "จัดไป ไม่ต้องตาม มีพร้อมดู อิอิ เจี้ยมไปเลย~!!")
                    #             break
                    #     else:
                    #         movies_sub = Firebase('https://welse-141512.firebaseio.com/submovies/' + str(sender_id));
                    #         movies_sub.push({"name": movie_name})
                    #     return "ok", 200
                    if u"หนังไก่" in message_text or u"หนังหี" in message_text or u"หนังหมู" in message_text \
                    or u"หนัง ไก่" in message_text or u"หนังสือ" in message_text or u"หนัง สือ" in message_text \
                    or u"หนังเหี่ยว" in message_text or u"หนัง เหี่ยว" in message_text:
                        send_message(sender_id, "ไม่ได้แดกกูหรอก :D")
                        return "ok", 200

                    if u"โป๊" in message_text or u"xxx" in message_text or u"porn" in message_text or u"แตด" in message_text:
                        send_message(sender_id, "เฮ้อ ก็แบบนี้ตลอด เหนื่อยใจ")
                        return "ok", 200

                    if u"มีถั่วไหม" in message_text:
                        send_message(sender_id, "ถามบังหน้าบ้านดิ!")
                        return "ok", 200

                    if u"หนัง" in message_text:
                        movies = Firebase('https://welse-141512.firebaseio.com/movies').get();
                        if len(message_text.split(" ")) > 1:
                            print "ranked"
                            movies = get_movie(message_text.lower(), movies)

                        if u"สุ่ม" in message_text:
                            random.shuffle(movies)

                        if movies != None:
                            if len(movies) == 0:
                                send_message(sender_id, "ไม่มีหนังที่หาอยู่น้า~!!")
                                return "ok", 200
                            el = []
                            for m in movies:
                                el.append({
                                    "title": m['title'],
                                    "subtitle": "imdb: " + str(m['imdb']),
                                    "image_url": m['image'],
                                    "buttons": [{
                                        "title": u"ดู",
                                        "type": "web_url",
                                        "url": m['link'],
                                    }],
                                    "default_action": {
                                        "type": "web_url",
                                        "url": m['link']
                                    }})
                                if len(el) == 10 or m['title'] == movies[-1]['title']:
                                    send_generic(sender_id, el, 2, m['link'])
                                    send_message(sender_id, "เลือกดูกัน ตามสบายยย~!!")
                                    return "ok", 200
                            return "ok", 200
                    else:    
                        if u"หยุด" in message_text or u"พอแล้ว" in message_text or u"เลิกติดตาม" in message_text:
                            send_message(sender_id, "โอเค อยากได้อะไรคราวหน้าบอกฝอยละกัน")
                            send_message(sender_id, "ใคร ๆ ก็รู้ ตลาดนี้ ฝอยคุม ง่อววว!")
                            uf = Firebase('https://welse-141512.firebaseio.com/ocz/' + str(sender_id))
                            uf.remove()
                            send_message(sender_id, "เอาเป็นว่าคราวหน้า ถ้าอยากได้อะไรก็ทักฝอยได้เลย")
                            return "ok", 200
                        history = Firebase('https://huafhoi.firebaseio.com/history/' + str(sender_id) + '/text')
                        history.push({'text':message_text})

                        if u"หมวดหมู่" in message_text:
                            send_message(sender_id, "ตอนนี้ฝอยคุมตลาด ram, monitor, cpu, storage, macbook, toys (พวก Gadgets)")
                            send_message(sender_id, "ตลาดอื่น ๆ เดี๋ยวฝอยจะไปคุมให้ เร็ว ๆ นี้")
                            send_image(sender_id, "https://media.tenor.co/images/fdd5dbcc25782675259f821fc18de50d/raw")
                            return "ok", 200

                        filtered_item = Firebase('https://huafhoi.firebaseio.com/items_filter').get();

                        ranked_item = get_item_by_rank(message_text, filtered_item)
                        el = []
                        send_message(sender_id, u"(beta) ค้นหาตาม keywords")
                        if(len(ranked_item) == 0):
                            send_message(sender_id, "ฝอยลองหาแล้วนะ เมื่อวานกับวันนี้อะ")
                            send_message(sender_id, "หาไม่เจอเลย~ แย่จางงงง")
                            return "ok", 200

                        for item in ranked_item:
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
                            if (len(el) % 4 == 0 and len(el) != 0) or item['name'] == ranked_item[-1]['name']:
                                if len(el) <= 4 and len(el) > 1:
                                    send_elements(sender_id, el, 2, item['type'], [
                                        {
                                            "title": "ดูอีก",
                                            "type": "postback",
                                            "payload": "filter"                        
                                        }
                                    ])
                                else:
                                    send_generic(sender_id, el, 2, item['type'])
                                el = []
                                next_items = Firebase('https://huafhoi.firebaseio.com/next/' + str(sender_id)).get();
                                if next_items != None:
                                    temp = Firebase('https://huafhoi.firebaseio.com/next/' + str(sender_id) + '/' + next_items.keys()[-1]).remove();
                                temp = Firebase('https://huafhoi.firebaseio.com/next/' + str(sender_id))
                                temp.push(ranked_item[5:])
                                return "ok", 200
                            
                    return "ok", 200
                        
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

                    if(not messaging_event["postback"].has_key('payload')):
                        return "ok", 200

                    if(messaging_event['postback']['payload'] == "done"):
                        send_message(sender_id, "โอเค อยากได้อะไรคราวหน้าบอกฝอยละกัน")
                        send_message(sender_id, "ใคร ๆ ก็รู้ ตลาดนี้ ฝอยคุม ง่อววว!")
                        uf = Firebase('https://welse-141512.firebaseio.com/ocz/' + str(sender_id))
                        uf.remove()
                        send_message(sender_id, "เอาเป็นว่าคราวหน้า ถ้าอยากได้อะไรก็ทักฝอยได้เลย")
                        return "ok", 200

                    if(messaging_event['postback']['payload'] == "other"):
                        send_message(sender_id, "หาอะไรอยู่ บอกฝอยเลย ไม่ว่าจะเป็น ram, monitor, cpu ก็ตาม เดะจัดให้")
                        return "ok", 200

                    if(messaging_event['postback']['payload'] == "menu"):
                        initial_conversation(sender_id, "หาไรอยู่ มีให้เลือกตามนี้ จิ้มเลย เดะฝอยจะเช็คตลาดให้")
                        return "ok", 200

                    if(messaging_event["postback"]["payload"] == 'hey'):
                        send_message(sender_id, "เฮ้ โย่ว หวัดเด")
                        send_image(sender_id, "https://media.tenor.co/images/a4932ffb7bd04392cfd220e4cbd325f1/raw")
                        send_message(sender_id, "หาไรอยู่ บอกเลย!! เดะฝอยจะเช็คตลาดให้")
                        return "ok", 200

                    message_text = messaging_event["postback"]["payload"].split(",")[0].lower()
                    if(message_text == "sub"):
                        sub = messaging_event["postback"]["payload"].split(",")[1].lower()
                        if sub == "0":
                            uf = Firebase('https://welse-141512.firebaseio.com/ocz/' + str(sender_id))
                            uf.remove()
                            return "ok", 200
                        sub_type = messaging_event["postback"]["payload"].split(",")[2].lower()
                        uf = Firebase('https://welse-141512.firebaseio.com/ocz/' + str(sender_id) + "/" + sub_type)
                        uf.set({"subcribe": sub})
                        if(sub == "1"):
                            send_message(sender_id, "EZ มาก เดะฝอยดูตลาดให้")
                            send_message(sender_id, "ของมาปั๊บ ทักหาทันที สวย ๆ อยากได้ไรเพิ่มบอกฝอย!!")
                            send_message(sender_id, "อยากดูอะไรเพิ่มอีกก็บอกฝอยได้เลยนะจ๊ะ")
                            return "ok", 200
                    
                    if u"หนัง" in message_text:
                        movies = Firebase('https://welse-141512.firebaseio.com/movies').get();

                        if len(message_text.split(" ")) > 1:
                            print "ranked"
                            movies = get_movie(message_text.lower(), movies)

                        if u"สุ่ม" in message_text:
                            random.shuffle(movies)

                        if movies != None:
                            if len(movies) == 0:
                                send_message(sender_id, "ไม่มีหนังที่หาอยู่น้า~!!")
                                return "ok", 200
                            el = []
                            for m in movies:
                                el.append({
                                    "title": m['title'],
                                    "subtitle": "imdb: " + str(m['imdb']),
                                    "image_url": m['image'],
                                    "buttons": [{
                                        "title": u"ดู",
                                        "type": "web_url",
                                        "url": m['link'],
                                    }],
                                    "default_action": {
                                        "type": "web_url",
                                        "url": m['link']
                                    }})
                                if len(el) == 10 or m['title'] == movies[-1]['title']:
                                    send_generic(sender_id, el, 2, m['link'])
                                    send_message(sender_id, "เลือกดูกัน ตามสบายยย~!!")
                                    return "ok", 200
                            return "ok", 200
                    else:
                        history_count = Firebase('https://huafhoi.firebaseio.com/history/' + str(sender_id) + '/count')
                        history_count.push({'count':message_text})

                        next_items = Firebase('https://huafhoi.firebaseio.com/next/' + str(sender_id)).get();
                        if next_items == None:
                            send_message(sender_id, "หมดแล้ว!! บ๋อแบ๋")
                            send_image(sender_id, "https://media.tenor.co/images/ab096f70ea512a3881e85756d3175c26/raw")
                            return "ok", 200
                        else:
                            items = Firebase('https://huafhoi.firebaseio.com/next/' + str(sender_id) + '/' + next_items.keys()[-1]).get();
                            remove = Firebase('https://huafhoi.firebaseio.com/next/' + str(sender_id) + '/' + next_items.keys()[-1]).remove();
                        if items != None:
                            temp = Firebase('https://huafhoi.firebaseio.com/next/' + str(sender_id))
                            temp.push(items[5:])
                            # counts = 0
                            el = []
                            for item in items:
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
                                if (len(el) % 4 == 0 and len(el) != 0) or item['name'] == items[-1]['name']:
                                    if len(el) <= 4 and len(el) > 1:
                                        send_elements(sender_id, el, 2, item['type'], [
                                            {
                                                "title": "ดูอีก",
                                                "type": "postback",
                                                "payload": "filter"                        
                                            }
                                        ])
                                    else:
                                        send_generic(sender_id, el, 2, item['type'])
                                    el = []
                                    return "ok", 200
                                # counts += 1
                        else:
                            pass
                            # send_message(sender_id, "ฝอยไม่เข้าใจคำนี้อะ พิมที่เข้าใจหน่อยเด้")

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
                "title":"แรม ddr3",
                "payload":"แรมddr3"
              },
              {
                "content_type":"text",
                "title":"จอ",
                "payload":"จอ"
              },
              {
                "content_type":"text",
                "title":"SSD",
                "payload":"ssd"
              },
              {
                "content_type":"text",
                "title":"Macbook",
                "payload":"macbook"
              },
              {
                "content_type":"text",
                "title":"ps4",
                "payload":"ps4"
              },
              {
                "content_type":"text",
                "title":"มือถือ",
                "payload":"มือถือ"
              },
              {
                "content_type": "text",
                "title": "การ์ดจอ",
                "payload":"การ์ดจอ"
              },
              {
                "content_type":"text",
                "title":"i5",
                "payload":"i5"
              },
              {
                "content_type": "text",
                "title": "สุ่มหนัง",
                "payload": "สุ่มหนัง"
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
                "text": u"ดู " + message_text + u" เยอะขนาดนี้ ให้ฝอยช่วยดูของให้ไหม ของใหม่มา ทักหาทันที" ,
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
                        "title": "ตลาด มือถือ",
                        "subtitle": "ตลาดมือถือ iPhone, Samsung, HTC และ อีกมากมาย",
                        "image_url": "http://spyapps.net/wp-content/uploads/2016/11/How-to-spy-on-a-mobile-phone.jpg",
                        "buttons": [{
                            "title": "ดูตลาดมือถือ",
                            "type": "postback",
                            "payload": "sub,1,mobile"
                        }]
                    },
                    {
                        "title": "ตลาด Graphic Card",
                        "subtitle": "ตลาด GPU",
                        "image_url": "http://di.lnwfile.com/_/di/_raw/pd/eg/76.jpg",
                        "buttons": [{
                            "title": "ดูตลาด GPU",
                            "type": "postback",
                            "payload": "sub,1,gpu"
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

def send_elements(recipient_id, elements, page, item_type, buttons):
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
                    "buttons": buttons
                }
            },
            "quick_replies":[
              {
                "content_type":"text",
                "title":"แรม ddr3",
                "payload":"แรมddr3"
              },
              {
                "content_type":"text",
                "title":"จอ",
                "payload":"จอ"
              },
              {
                "content_type":"text",
                "title":"SSD",
                "payload":"ssd"
              },
              {
                "content_type":"text",
                "title":"Macbook",
                "payload":"macbook"
              },
              {
                "content_type":"text",
                "title":"PS4",
                "payload":"ps4"
              },
              {
                "content_type":"text",
                "title":"มือถือ",
                "payload":"มือถือ"
              },
              {
                "content_type": "text",
                "title": "การ์ดจอ",
                "payload":"การ์ดจอ"
              },
              {
                "content_type":"text",
                "title":"i5",
                "payload":"i5"
              },
              {
                "content_type": "text",
                "title": "สุ่มหนัง",
                "payload": "สุ่มหนัง"
              }
            ]
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
                }
            },
            "quick_replies":[
              {
                "content_type":"text",
                "title":"แรม ddr3",
                "payload":"แรมddr3"
              },
              {
                "content_type":"text",
                "title":"จอ",
                "payload":"จอ"
              },
              {
                "content_type":"text",
                "title":"SSD",
                "payload":"ssd"
              },
              {
                "content_type":"text",
                "title":"Macbook",
                "payload":"macbook"
              },
              {
                "content_type":"text",
                "title":"ps4",
                "payload":"ps4"
              },
              {
                "content_type":"text",
                "title":"มือถือ",
                "payload":"มือถือ"
              },
              {
                "content_type": "text",
                "title": "การ์ดจอ",
                "payload":"การ์ดจอ"
              },
              {
                "content_type":"text",
                "title":"i5",
                "payload":"i5"
              },
              {
                "content_type": "text",
                "title": "สุ่มหนัง",
                "payload": "สุ่มหนัง"
              }
            ]
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def get_item_by_rank(query,items):
    if items == None:
        return None
    i = items[:]
    for item in i:
        item['rank'] = 0
        for k in item['keywords']:
            if k in query:
                item['rank'] += 1

    ranked = []
    for item in i:
        if item['rank'] >= len(query.split(" ")) and item['rank'] > 0:
            ranked.append(item)
    ranked_item = sorted(ranked, key=lambda k: (k['rank'],k['time']), reverse=True)
    return ranked_item

def get_movie(query, movies):
    query_string = query.split(" ")
    ret_m = []
    for m in movies:
        m['rank'] = 0
        for q in query_string:
            if q in m['title']:
                m['rank'] += 1;
        if m['rank'] != 0:
            ret_m.append(m)
    ret_m = sorted(ret_m, key=lambda k: (k['rank']), reverse=True)
    return ret_m

def scrap_restaurant(query):
    restaurant = []
    for page in range(1,2):
        url = "https://www.wongnai.com/businesses?q="+urllib.quote_plus(query)
        r  = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data)
        for rest in soup.find_all('div', {'class':'top'}):
            title = rest.find('div', {'class':'head'}).find('a').get_text()
            link = rest['data-url']
            rating = float(rest.find('span', {'class':'rating'}).get_text()) if rest.find('span', {'class':'rating'}) else u"ไม่ระบุ"
            map_link = "https://www.google.co.th/maps/@"+rest.find('span', {'class':'lat'}).get_text()+","+rest.find('span', {'class':'lng'}).get_text()+",20z"
            image = rest.find('a', {'class':'photoC'}).find('img')['src']
            restaurant.append({
                    "title": title,
                    "link": link,
                    "rating": rating,
                    "image": image,
                    "map_link": map_link
                })
            if len(restaurant) == 10:
                break
    return restaurant

def log(message):  
    print str(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)
