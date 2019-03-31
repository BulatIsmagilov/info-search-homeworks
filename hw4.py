import psycopg2
import math
import lib
from lib import get_articlies_count
from lib import get_article_word_count
from lib import get_articles
from lib import tf
from lib import idf

# ALTER TABLE IF EXISTS article_term ADD COLUMN tf_idf double precision NOT NULL DEFAULT 0.0;

conn = psycopg2.connect(database="info_search_development", user="ismglv", password="", host="localhost")

articles_count = 0
article_words_count = get_articlies_count(conn)

article_words_count = {}
article_words_count = get_article_word_count(conn)

terms_articles = []
with conn.cursor() as cur:
    cur.execute('select t.term_id, term_text, article_id from article_term article INNER JOIN terms_list t ON article.term_id = t.term_id;')
    for row in cur:
        terms_articles.append((row[0], row[1], row[2]))

word_included_articles = {}
tf_idf_matrix = []

for term_id, term, article_id in terms_articles:
    tf = tf(conn, term, article_id)

    idf = idf(conn, term)

    tf_idf_matrix.append((tf*idf, term_id, article_id))

for row in tf_idf_matrix:
    with conn.cursor() as cur:
        cur.execute('UPDATE article_term SET tf_idf = %s WHERE term_id = %s AND article_id = %s', row)

conn.commit()
conn.close()
