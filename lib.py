import psycopg2
import nltk
from nltk.corpus import stopwords
nltk.download("stopwords")
from nltk.stem.snowball import SnowballStemmer
import re
import functools
import math

stopwords = set(stopwords.words('russian'))

def count_cos_measure(v1, v2):
    pairs = zip(v1, v2)
    num = sum(pair[0] * pair[1] for pair in pairs)
    den = math.sqrt(sum(el * el for el in v1)) * math.sqrt(sum(el * el for el in v2))
    return num/den if den != 0 else 0

def proccess_text(query: str):
    words = re.split(r'\W+', query)
    words = [word.lower() for word in words if word.isalpha()]
    words = [word for word in words if not word in stopwords]

    stem = SnowballStemmer('russian')
    return [stem.stem(word) for word in words]

def get_articlies_count(conn):
    with conn.cursor() as cur:
        cur.execute('SELECT count(*) FROM articles;')
        return cur.fetchone()[0]

def get_article_word_count(conn):
    article_words_count = {}
    with conn.cursor() as cur:
        cur.execute('SELECT article_id, count(term) as c FROM words_porter GROUP BY article_id;')
        for row in cur:
            article_words_count[row[0]] = row[1]
        return article_words_count


def get_articles(conn, words):
    words = tuple(words)
    articles = {}
    with conn.cursor() as cur: 
        cur.execute("SELECT a.article_id, t.term_text, a.tf_idf FROM article_term a INNER JOIN terms_list t ON a.term_id = t.term_id WHERE t.term_text IN %s", (words,))
        for article_id, term_text, tf_idf in cur:
            if article_id not in articles:
                articles[article_id] = {}
            terms = articles[article_id]
            terms[term_text] = tf_idf
    return articles

def get_query_vector(conn, words):
    vector = {}
    for word in words:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM (SELECT DISTINCT article_id FROM words_porter WHERE term = %s) a", (word,))
            word_included_article = cur.fetchone()[0]
        idf = math.log2(articles_count / word_included_article)
        vector[word] = idf
    return vector

def get_urls_by_article_ids(conn, ids_and_cos):
    url_cos = {}
    for _id, cos in ids_and_cos:
        with conn.cursor() as cur:
            cur.execute("SELECT url FROM articles WHERE id = %s", (_id,))
            url = cur.fetchone()[0]
            url_cos[url] = cos
    return url_cos


def tf(conn, term, article_id):
    with conn.cursor() as cur:
        cur.execute("select count(id) from words_porter group by term, article_id HAVING term = %s AND article_id=%s;", (term, article_id))
        try:
            document_word_includes_count = cur.fetchone()[0]
        except:
            document_word_includes_count = 0
    global article_words_count
    tf = document_word_includes_count / article_words_count[article_id]
    return tf

def idf(conn, term):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM (SELECT DISTINCT article_id FROM words_porter WHERE term = %s) a", (term,))
        word_included_article = cur.fetchone()[0]

    global articles_count
    idf = math.log2((articles_count - word_included_article + 0.5) / (word_included_article + 0.5))
    return idf


def sort(conn, words):
    sql = "select count(article_id) from article_term article INNER JOIN (select * from terms_list where term_text = %s) t ON t.term_id = article.term_id ;"
    with conn.cursor() as cur:
        word_includes = []
        for word in words:
            cur.execute(sql, (word,))
            includes = cur.fetchone()[0]
            word_includes.append((word, includes))
        return [i[0] for i in sorted(word_includes, key= lambda w: w[1], reverse=True)]

