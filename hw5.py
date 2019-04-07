import psycopg2
import math
nltk.download("stopwords")
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer 
import re
import functools
from lib import proccess_text
from lib import get_articlies_count
from lib import get_article_word_count
from lib import get_articles
from lib import tf
from lib import idf
from lib import get_query_vector
from lib import get_urls_by_article_ids

conn = psycopg2.connect(database="info_search_development", user="ismglv", password="", host="localhost")

articles_count = 0
article_words_count = get_articlies_count(conn)

word_included_articles = {}

def get_vector_len(vector):
    _sum = 0
    for term, tf_idf in vector.items():
        _sum += tf_idf ** 2
        return math.sqrt(_sum)


def search(query: str):
    words = proccess_text(query)

    articles = get_articles(words)
    query_vector = get_query_vector(words)

    article_cos = {}
    for article_id, terms in articles.items():
        cos = 0
        for term_id, idf in terms.items():
            if term_id in query_vector:
                tf_idf = query_vector[term_id]
                cos += idf*tf_idf
        article_cos[article_id] = cos / (get_vector_len(terms) * get_vector_len(query_vector))

    article_ids_and_cos = [(k, article_cos[k]) for k in sorted(article_cos, key=article_cos.get, reverse=True)]

    url_cos = get_urls_by_article_ids(article_ids_and_cos)

    i = 0
    for url, cos in url_cos.items():
        print(url, cos)
        i += 1
        if i == 10:
            break

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        print("Number of arguments is too many!")
        conn.close()
        sys.exit()

    if len(sys.argv) <= 1:
        print("Enter your query: ")
        query = input()
    else:
        query = sys.argv[1]

    search(query)
    conn.close()
