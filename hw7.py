import operator
from collections import defaultdict

import numpy as np
import psycopg2

from scipy.linalg import svd
from sklearn.feature_extraction.text import CountVectorizer

RANK = 5

from lib import proccess_text
from lib import count_cos_measure


conn = psycopg2.connect(database="info_search_development", user="ismglv", password="", host="localhost")
cur = conn.cursor()


def get_matrices(docs, query):
    cv = CountVectorizer(tokenizer=lambda doc: doc, lowercase=False)
    words_in_articles = []
    for doc in docs:
        cur.execute('select term from words_porter where article_id = %s', (doc,))
        words = [word[0] for word in cur.fetchall()]
        words_in_articles.append(words)

    a_matrix = cv.fit_transform(words_in_articles).toarray().transpose()
    query_vector = cv.transform([query]).toarray()  # already transposed
    return a_matrix, query_vector


def rank_articles(q, v, docs):
    result = defaultdict(float)
    q = np.diagonal(q)
    for i, doc in enumerate(docs):
        cur.execute('select url from articles where id = %s', (doc,))
        url = cur.fetchone()[0]

        similarity = count_cos_measure(q, v[i])
        result[url] = similarity
    return result


def lsi(query, docs):
    a_matrix, query_vector = get_matrices(docs, query)

    u, s, vt = svd(a_matrix, full_matrices=False)
    u_k = u[:, :RANK]
    s_k = np.diag(s[:RANK,])
    v_k = vt.transpose()[:, :RANK]
    q = np.matmul(query_vector, u_k) * np.linalg.inv(s_k)

    doc_ranks = rank_articles(q, v_k, documents)
    return sorted(doc_ranks.items(), key=operator.itemgetter(1), reverse=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) <= 1:
        print("search: ")
        query = input()
    else:
        query = sys.argv[1]

    cur.execute('select id from articles')
    documents = [doc[0] for doc in cur.fetchall()]

    query = proccess_text(query)
    result = lsi(query, documents)

    print(result[:10])
