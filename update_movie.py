from bs4 import BeautifulSoup
import requests
from os import system
import re
import time
from firebase import Firebase

def scrap_movie():
    movies = []
    for page in range(1,2):
        url = "https://www.moviehd-master.com/page/" + str(page)
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
                resolution = movie.find('span', {'class':'calidad2'}).get_text() if movie.find('span', {'class':'calidad2'}) != None else u"ไม่ระบุ"
                if imdb > 5:
                    title = ' '.join([title, resolution, sound])
                    movies.append({
                        "title": title.lower(),
                        "image": image,
                        "imdb": imdb,
                        "link": link
                    })
    return movies


def clear_firebase():
	a = f.get()
	if a != None:
		for i in a:
			q = Firebase('https://welse-141512.firebaseio.com/movies'+'/'+i)
			q.remove()

f = Firebase('https://welse-141512.firebaseio.com/movies');
clear_firebase()
movies = scrap_movie()
f.set(movies)

