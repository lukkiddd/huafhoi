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



def send_news():
    fb = Firebase('https://welse-141512.firebaseio.com/movies')
    old_items = fb.get()

    if(old_items == None):
        old_items = scrap()

    new_items = scrap()
    new_send = getNew(old_items, new_items)

    users_fb = Firebase('https://welse-141512.firebaseio.com/submovies/')
    users = users_fb.get()
    for u in users:
        user = Firebase('https://welse-141512.firebaseio.com/submovies/' + str(u))
        user_data = user.get()
        for m in user_data:
            el = []
            for newMovie in new_items:
                if m['name'] == newMovie['title']
                    el.append({
                    "title": newMovie['title'],
                    "subtitle": str(newMovie['imdb']),
                    "image_url": newMovie['image'],
                    "buttons": [{
                        "title": u"ดู",
                        "type": "web_url",
                        "url": newMovie['link'],
                    }],
                    "default_action": {
                        "type": "web_url",
                        "url": newMovie['link']
                    }})
                if len(el) == 10 or newMovie['title'] == new_items[-1]['title']:
                    send_generic(sender_id, el)
                    break
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

def scrap_movie():
    movies = []
    for page in range(1,3):
        url = "https://www.mastermovie-hd.com/page/"+str(page)
        r  = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data)
        for movie in soup.find_all('div', {'class':'item'}):
            imdb = movie.find('div',{'class','imdb'})
            imdb = imdb.find('p').get_text() if imdb != None else "N/A"
            imdb = re.sub("\s+","",imdb)
            if "N/A" not in imdb:
                imdb = float(imdb)
                if imdb > 5:
                    content = movie.find('div', {'class','item-content'})
                    title = content.find('a').get_text()
                    image = movie.find('img')['data-lazy-original']
                    link = movie.find('a')['href']
                    movies.append({
                        "title": title.lower(),
                        "image": image,
                        "imdb": imdb,
                        "link": link
                    })
    return movies

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