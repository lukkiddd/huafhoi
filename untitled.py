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


def send_news():
	fb = Firebase('https://welse-141512.firebaseio.com/items_test')
	old_items = fb.get()
	if(old_items == None):
		old_items = scrap()

	new_items = scrap()
	new_send = getNew(old_items, new_items)
	counts = 0
	el = []
	if( new_send == 0 ):
		return 0
	else:



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
		items[slug['slug']] = []
		for i in xrange(1,3):
			url = "https://www.overclockzone.com/forums/forumdisplay.php/"+slug['value']+"/page" + str(i) + "?prefixid=Sell"
			r  = requests.get(url)
			data = r.text
			soup = BeautifulSoup(data)
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
	new_i = []
	for t in type_item:
		print new[t]
		# for n in new:
		# 	found = 0
		# 	for o in old:
		# 		if n['name'] == o['name']:
		# 			found = 1
		# 	if not found:
		# 		new_i.append(n)
	return new_i

if __name__ == '__main__':
	send_news()