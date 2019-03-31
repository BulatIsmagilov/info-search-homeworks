import psycopg2
import nltk
from nltk.corpus import stopwords
nltk.download("stopwords")
from nltk.stem.snowball import SnowballStemmer
import re
import functools

stopwords = set(stopwords.words('russian'))

def proccess_text(query: str):
    words = re.split(r'\W+', query)
    words = [word.lower() for word in words if word.isalpha()]
    words = [word for word in words if not word in stopwords]

    stem = SnowballStemmer('russian')
    return [stem.stem(word) for word in words]

def get_articles(words):
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

def get_query_vector(words):
    vector = {}
    for word in words:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM (SELECT DISTINCT article_id FROM words_porter WHERE term = %s) a", (word,))
            word_included_article = cur.fetchone()[0]
        idf = math.log2(articles_count / word_included_article)
        vector[word] = idf
    return vector

def get_urls_by_article_ids(ids_and_cos):
    url_cos = {}
    for _id, cos in ids_and_cos:
        with conn.cursor() as cur:
            cur.execute("SELECT url FROM articles WHERE id = %s", (_id,))
            url = cur.fetchone()[0]
            url_cos[url] = cos
    return url_cos


def tf(term, article_id):
    with conn.cursor() as cur:
        cur.execute("select count(id) from words_porter group by term, article_id HAVING term = %s AND article_id=%s;", (term, article_id))
        try:
            document_word_includes_count = cur.fetchone()[0]
        except:
            document_word_includes_count = 0
    global article_words_count
    tf = document_word_includes_count / article_words_count[article_id]
    return tf

def idf(term):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM (SELECT DISTINCT article_id FROM words_porter WHERE term = %s) a", (term,))
        word_included_article = cur.fetchone()[0]
    
    global articles_count
    idf = math.log2((articles_count - word_included_article + 0.5) / (word_included_article + 0.5))
    return idf

