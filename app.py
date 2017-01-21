import os
import sys
import json
import requests
import re
import time
from bs4 import BeautifulSoup
from flask import Flask, request
# from firebase import Firebase

# f = Firebase('https://welse-141512.firebaseio.com/items')

app = Flask(__name__)

def convert(content):
    content = content.lower();
    ret = re.sub('[!=@\-\*/:"]+',"", content);
    ret = re.sub("[\s]+", " ", ret);
    return ret
def scrap():
    items = []
    items_link = []
    for i in xrange(1,5):
        url = "https://www.overclockzone.com/forums/forumdisplay.php/158-Monitor/page" + str(i) + "?prefixid=Sell"
        r  = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data)
        for item in soup.find_all('div', {'class':'inner'}):
            if("Today" in item.find_all('span',{'class':'label'})[0].get_text() or
               "Yesterday" in item.find_all('span',{'class':'label'})[0].get_text()):
                for title in item.find_all('a', {'class':'title'}):
                    items.append({'name': convert(title.get_text()), 'link': "https://www.overclockzone.com/forums/" +title['href']})
    return items

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
                    message_text = messaging_event["message"]["text"]  # the message's text
                    scan(sender_id)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

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


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

def scan(sender_id):
    oldlen = 0
    count = 0
    new_item = []
    while(1):
        print count
        items = scrap()
        if(oldlen != len(items)):
            for i in items:
                if i not in new_item:
                      print(i['name'])
                      send_message(sender_id, i['name'] + "\n LINK:" + i['link'])
                      new_item.append(i)
            oldlen = len(items)
        time.sleep(1)
        count += 1

if __name__ == '__main__':
    app.run(debug=True)
