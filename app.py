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
                    message_text = messaging_event["message"]["text"]  # the message's text
                    if message_text.lower() == 'cpu' or message_text.lower() == 'ram' or message_text.lower() == 'monitor' or message_text.lower() == 'storage':
                        f = Firebase('https://welse-141512.firebaseio.com/items/' + message_text + '/page1')
                        items_array = f.get()
                        if items_array == None:
                            send_message(sender_id, "Nothing new!")
                            break
                        el = []
                        counts = 0
                        for i in items_array:
                            if counts == 4 :
                                break
                            q = Firebase('https://welse-141512.firebaseio.com/items/' + message_text + '/page1/' + i)
                            item = q.get()
                            print("\n\n\n")
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
                    message_text = messaging_event["postback"]["payload"].split(",")[0] 
                    page = messaging_event["postback"]["payload"].split(",")[1] 
                    if message_text.lower() == 'cpu' or message_text.lower() == 'ram' or message_text.lower() == 'monitor' or message_text.lower() == 'storage':
                        f = Firebase('https://welse-141512.firebaseio.com/items/' + message_text + '/page' + str(page))
                        items_array = f.get()
                        if items_array == None:
                            send_message(sender_id, "Nothing new!")
                            break
                        el = []
                        counts = 0
                        for i in items_array:
                            if counts == 4 :
                                break
                            q = Firebase('https://welse-141512.firebaseio.com/items/' + message_text + '/page' + str(page) + '/' + i)
                            item = q.get()
                            print("\n\n\n")
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
                        page += 1
                        send_elements(sender_id, el, page, item['type'])
                    else:
                        send_message(sender_id, "NO item from " + message_text + ' category')

    return "ok", 200

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
            "text": message_text
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
            }
        }
        # "message": {
        #     "text": message_text
        # }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
