import nltk 
import re 
import math
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity 
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import normalize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.util import ngrams
import pandas as pd   
import jsonlines
import json
from tqdm.notebook import tqdm
import pickle
from scipy.sparse import csr_matrix

def remove_string_special_characters(s):
    # removes special characters with ' '
    stripped = re.sub('[^a-zA-z\s]', ' ', s)
    stripped = re.sub('_', ' ', stripped)
      
    # Change any white space to one space
    stripped = re.sub('\s+', ' ', stripped)
      
    # Remove start and end white spaces
    stripped = stripped.strip()
    if stripped != '':
            return stripped.lower()

def stem_string(sentence):
    ps = PorterStemmer()
    
    words = word_tokenize(sentence)
    words = [ps.stem(word) for word in words]
    return " ".join(words)

def remove_stop_words(sentence):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(sentence)
    words = [word for word in words if word not in stop_words]
    return " ".join(words)
    
def process_string(sentence):
    sentence = remove_string_special_characters(sentence)
    sentence = stem_string(sentence)
    sentence = remove_stop_words(sentence)
    return sentence

def process_query(query, request_args):
    loaded_cnt_vct = pickle.load(open("web_data/count_vectorizer.pkl", "rb"))
    loaded_tfidf_new_matrix = pickle.load(open("web_data/tfidf_new_matrix.pkl", "rb"))
    loaded_docID = pickle.load(open("web_data/doc_id_dict.pkl", "rb"))

    query = process_string(query)

    cnt_matrix_query = loaded_cnt_vct.transform([query])
    cnt_matrix_query = csr_matrix.transpose(cnt_matrix_query)

    result = loaded_tfidf_new_matrix * cnt_matrix_query
    result = csr_matrix.transpose(result)
    result_matrix = result.toarray()[0]
    related_docs_indices = result_matrix.argsort()[::]

    tfidf_scores = [result_matrix[i] for i in related_docs_indices]
    max_tfidf_score = max(tfidf_scores)
    tfidf_scores = [ (score/max_tfidf_score)*100 for score in tfidf_scores]
    related_results = [loaded_docID[i] for i in related_docs_indices]

    doc_index_scores = {}
    for idx, result in enumerate(related_results):
        doc_index_scores[result] = tfidf_scores[idx]

    related_result_docs = []
    with jsonlines.open('data_india_sample.jl') as reader:
        for obj in reader:
            if obj['user'] in related_results:
                if ("country" not in request_args) or (obj['country'] in request_args.getlist('country')):
                    if ("institute" not in request_args) or (obj['institute'] in request_args.getlist('institute')):
                        related_result_docs.append( (doc_index_scores[obj['user']], obj) )

    related_result_docs.sort(key = lambda x: x[0], reverse=True)

    docs_len = min(len(related_result_docs), 1000)
    
    return related_result_docs[:docs_len]