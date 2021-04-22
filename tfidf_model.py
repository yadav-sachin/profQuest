import nltk 
import re 
import math
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

def process_card(idx, doc):
    return f"""
        <div class="card">
            <img src="{doc['imgLink']}" class="card-img-top" alt="HeadImg">
            <div class="card-body">
                <h5 class="card-title">{doc['name']}</h5>
                <p class="card-text">{doc['institute']}</p>
                <p class="card-text">{doc['subjects']}</p>
                <a href="#" class="btn btn-primary">{doc['scholarPage']}</a>
            </div>
        </div>
        """


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

def process_query(query):
    loaded_vectorizer = pickle.load(open("web_data/tfidf_vectorizer.pkl","rb"))
    loaded_matrix = pickle.load(open("web_data/tfidf_matrix.pkl","rb"))
    loaded_docID = pickle.load(open("web_data/doc_id_dict.pkl", "rb"))
    query = process_string(query)
    result_matrix = loaded_vectorizer.transform([query])
    cosine_similarities = linear_kernel(result_matrix, loaded_matrix).flatten()
    related_docs_indices = cosine_similarities.argsort()[:-1000:-1]
    related_results = [loaded_docID[i] for i in related_docs_indices]
    doc_index_results = {}
    for idx, result in enumerate(related_results):
        doc_index_results[result] = idx
    related_result_docs = []
    with jsonlines.open('data_india_sample.jl') as reader:
        for obj in reader:
            if obj['user'] in related_results:
                related_result_docs.append( (doc_index_results[obj['user']], obj) )
    related_result_docs.sort(key = lambda x: x[0])
    # related_result_docs = [doc for idx, doc in related_result_docs]
    return related_result_docs