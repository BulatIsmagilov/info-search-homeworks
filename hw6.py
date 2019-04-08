import psycopg2
import math
import functools
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer 
import re

from lib import get_articlies_count
from lib import get_article_word_count
from lib import get_articles
from lib import proccess_text
from lib import tf
from lib import idf
from lib import get_query_vector
from lib import get_urls_by_article_ids

k = 1.2
b = 0.75

conn = psycopg2.connect(database="info_search_development", user="ismglv", password="", host="localhost")

articles_count = 0
article_words_count = get_articlies_count(conn)

article_words_count = {}
article_words_count = get_article_word_count(conn)

avgdl = functools.reduce(lambda x, y: x + y, article_words_count.values()) / articles_count

def search(query):
    words = proccess_text(query)
    articles = get_articles(conn, words)

    article_score = []
    for article in articles:
        score = 0
        for word in words:
            prev_score = idf(conn, word) * (tf(conn, word, article) * (k + 1)) / (tf(conn, word, article) + k * (1 - b + b*articles_count / avgdl))
            if prev_score > 0:
                score += prev_score
        article_score.append((article, score))

    article_score = sorted(article_score, key=lambda a: a[1], reverse=True)

    url_cos = get_urls_by_article_ids(conn, article_score)

    for url, cos in url_cos.items()[0:10]:
        print(url, cos)

if __name__ == "__main__":
    import sys

    if len(sys.argv) <= 1:
        print("Search: ")
        query = input()
    else:
        query = sys.argv[1]

    search(query)
    conn.close()
