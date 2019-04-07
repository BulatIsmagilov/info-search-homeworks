from pymystem3 import Mystem
from nltk.stem.snowball import SnowballStemmer
import nltk
import json
from IPython import embed
from db import DB
import re
import string
import uuid

m = Mystem()
stemmer_rus = SnowballStemmer('russian')

db = DB()

articles = db.get_articles()

puncList = [".",";",":","!","?","/","\\",",","#","@","$","&",")","(","\""]

filename = "/Users/ismglv/dev/info-search-homeworks/stop-words.txt"
with open(filename, 'r') as f:
    stopwords = [line.strip() for line in f]   # save numbers to a list

words = []
for (id, article) in articles:
    article = ''.join(article).translate(string.punctuation)
    for punc in puncList:
        for word in article:
            article = article.replace(punc,'')
    words = article.split()

    my_stem = []
    for word in words:
        if(word not in stopwords):
            t = m.lemmatize(word)[0]
            my_stem.append(t)
            db.insert_my_stem(str(uuid.uuid4()), t, id)

    porter = []
    for word in words:
        if(word not in stopwords):
            t = stemmer_rus.stem(word)
            porter.append(t)
            db.insert_porter(str(uuid.uuid4()), t, id)
