import psycopg2
import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import re
import functools
import lib
from lib import proccess_text
from lib import sort
import math
import uuid

conn = psycopg2.connect(database="info_search_development", user="ismglv", password="", host="localhost")

# create table terms_list(term_id uuid DEFAULT uuid_generate_v4 (), term_text text UNIQUE)
# create table article_term(article_id uuid, term_id uuid)

# -----------------------
# with conn.cursor() as cur:
#     cur.execute("SELECT * FROM words_porter") 
#     term_arcticles = {}
#
#     for item in cur:
#         word = item[1]
#         article_id = item[2]
#         if not word in term_arcticles:
#             term_arcticles[word] = set()
#         term_arcticles[word].add(article_id)
#
#     for term, articles in term_arcticles.items():
#         term_id = str(uuid.uuid4())
#         cur.execute("INSERT INTO terms_list VALUES(%s, %s)", (term_id, term))
#
#         for a in articles:
#             cur.execute("INSERT INTO article_term(term_id, article_id) VALUES(%s, %s)", (term_id, a))
#
#     conn.commit()
# -----------------------

def search(query: str):
    queries = sort(conn, proccess_text(query))
    sql = "select article_id from article_term article INNER JOIN (select * from terms_list where term_text = %s) t ON article.term_id = t.term_id;"
    includes = []
    for word in queries:
        s = set()
        with conn.cursor() as cur:
            cur.execute(sql, (word,))
            for item in cur:
                s.add(item[0])
        includes.append(s)
    intersection = list(functools.reduce(lambda x,y: x&y, includes))

    titles = []
    for item in intersection:
        with conn.cursor() as cur:
            cur.execute("SELECT title from articles WHERE id = %s", (item,))
            t = cur.fetchone()[0]
            titles.append(t)

    print(titles)

if __name__ == "__main__":
    import sys
    if len(sys.argv) <= 1:
        print("search: ")
        query = input()
    else:
        query = sys.argv[1]

    search(query)
    conn.close()
