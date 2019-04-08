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

def lsi(query, docs):
    a_matrix, query_vector = get_matrices(cur, docs, query)

    u, s, vt = svd(a_matrix, full_matrices=False)
    u_k = u[:, :RANK]
    s_k = np.diag(s[:RANK,])
    v_k = vt.transpose()[:, :RANK]
    q = np.matmul(query_vector, u_k) * np.linalg.inv(s_k)

    doc_ranks = rank_articles(cur, q, v_k, documents)
    return sorted(doc_ranks.items(), key=operator.itemgetter(1), reverse=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) <= 1:
        print("search: ")
        query = input()
    else:
        query = sys.argv[1]

    cur.execute('select id from articles')
    articles = [article[0] for article in cur.fetchall()]

    query = proccess_text(query)
    result = lsi(query, articles)

    print(result[:10])
