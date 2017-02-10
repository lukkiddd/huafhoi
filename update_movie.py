# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from os import system
import re
import time
from firebase import Firebase

def scrap_movie():
    movies = []
    for page in range(1,6):
        url = "http://www.moviehd-master.com/page/" + str(page)
        r  = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data)
        for movie in soup.find_all('div', {'class':'item'}):
            sound = movie.find('span', {'class':'soundmovie'})
            imdb = movie.find('span',{'class','imdb'}).get_text()
            if sound != None and "N/A" not in imdb:
                imdb = float(imdb)
                link = movie.find('a')['href']
                title = movie.find('h2').get_text()
                sound = sound.get_text().replace(" ","")
                image = movie.find('img')['src']
                resolution = movie.find('span', {'class':'calidad2'}).get_text() if movie.find('span', {'class':'calidad2'}) != None else ""
                if imdb > 5:
                    movies.append({
                        "title": title.lower(),
                        "image": image,
                        "imdb": imdb,
                        "link": link,
                        "resolution": resolution,
                        "sound": sound
                    })
    return movies


def clear_firebase():
	q = Firebase('https://welse-141512.firebaseio.com/movies')
	if q != None:
		q.remove()

f = Firebase('https://welse-141512.firebaseio.com/movies');
clear_firebase()
movies = scrap_movie()
f.set(movies)

