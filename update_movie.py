from bs4 import BeautifulSoup
import requests
from os import system
import re
import time
from firebase import Firebase

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

