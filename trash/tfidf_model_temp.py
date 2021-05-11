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
from difflib import SequenceMatcher
from heapq import nlargest as _nlargest

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

def get_tf_idf_vec(query, loaded_cnt_vct, loaded_tfidf_new_matrix):
    query = process_string(query)
    cnt_matrix_query = loaded_cnt_vct.transform([query])
    cnt_matrix_query = csr_matrix.transpose(cnt_matrix_query)

    result = loaded_tfidf_new_matrix * cnt_matrix_query
    result = csr_matrix.transpose(result)
    result = result.toarray()[0]
    
    return result

def get_active_vec(year, loaded_mat_activeness):
    col = year-1
    citations = loaded_mat_activeness[:,col].squeeze()
    return citations

def get_slope_vec(loaded_ranking_metrics):
    return loaded_ranking_metrics[:,0].squeeze()

def get_hindex_vec(loaded_ranking_metrics):
    return loaded_ranking_metrics[:,1].squeeze()
    
def get_insti_vec(loaded_ranking_metrics):
    return loaded_ranking_metrics[:,2].squeeze()

def normalise(x):
    return x/np.linalg.norm(x)


def query_subject(user_input, loaded_cnt_vct, loaded_tfidf_new_matrix, loaded_docID, loaded_mat_activeness, loaded_ranking_metrics):
    
    #parameters
    params = ['tfidf', 'active', 'hindex', 'slope', 'insti']
    ranks={}
    for param in params:
        ranks[param]={}
    
    #set weight factors
    ranks['tfidf']['wt'] = user_input['tfidf_score']
    ranks['active']['wt'] = user_input['active_score']
    ranks['hindex']['wt'] = user_input['hindex_score']
    ranks['slope']['wt'] = user_input['slope_score']
    ranks['insti']['wt'] = user_input['insti_score']
    
    #scale up 
    total_user_input_wt = 0
    for key,val in ranks.items():
        total_user_input_wt += val['wt']
    factor = 100/total_user_input_wt
    for key,val in ranks.items():
        val['wt'] *= factor

    
    #tf-idf
    ranks['tfidf']['vec'] = normalise(get_tf_idf_vec(user_input['query_string'], loaded_cnt_vct, loaded_tfidf_new_matrix))

    #activeness
    ranks['active']['vec'] = normalise(get_active_vec(user_input['active_yr'], loaded_mat_activeness))
    
    #slope of citations
    ranks['slope']['vec'] = normalise(get_slope_vec(loaded_ranking_metrics))
    
    #h-index
    ranks['hindex']['vec'] = normalise(get_hindex_vec(loaded_ranking_metrics))
    
    #institute reputation
    ranks['insti']['vec'] = normalise(get_insti_vec(loaded_ranking_metrics))
    
    #final score
    #final score
    final_sc = np.zeros(ranks['tfidf']['vec'].size)
    for key,val in ranks.items():
        final_sc += val['wt']*val['vec']
        
    indices = final_sc.argsort()
    indices = indices[::-1]
    profs = [(loaded_docID[i],final_sc[i]) for i in indices]
    
    return profs

def process_query(query, request_args):
    loaded_cnt_vct = pickle.load(open("web_data/count_vectorizer.pkl", "rb"))
    loaded_tfidf_new_matrix = pickle.load(open("web_data/tfidf_new_matrix.pkl", "rb"))
    loaded_docID = pickle.load(open("web_data/doc_id_dict.pkl", "rb"))
    loaded_mat_activeness = pickle.load(open("web_data/mat_activeness.pkl", "rb"))
    loaded_ranking_metrics = pickle.load(open("web_data/ranking_metrics.pkl", "rb"))

    input_obj = dict()
    input_obj['query_string'] = request_args['q']
    # TFIDF weight
    if 'tfidf__weight' in request_args:
        input_obj['tfidf_score'] = int(request_args['tfidf__weight'])
    else:
        input_obj['tfidf_score'] = 10
    # Activeness over the years
    if 'activeness__checkbox' in request_args and 'activeness__years' in request_args:
        input_obj['active_score'] = int(request_args['activeness__weight'])
        input_obj['active_yr'] = int(request_args['activeness__years'])
    else:
        input_obj['active_score'] = 0
        input_obj['active_yr'] = 5
    # H-index
    if 'h-index__checkbox' in request_args and 'h-index__weight' in request_args:
        input_obj['hindex_score'] = int(request_args['h-index__weight'])
    else:
        input_obj['hindex_score'] = 0
    #Slope of Citations
    if 'slope-citations__checkbox' in request_args and 'slope-citations__weight' in request_args:
        input_obj['slope_score'] = request_args['slope-citations__weight']
    else:
        input_obj['slope_score'] = 0

    # Institute Reputation
    if 'inst-reputation__checkbox' in request_args and 'inst-reputation__weight' in request_args:
        input_obj['insti_score'] = int(request_args['inst-reputation__weight'])
    else:
        input_obj['insti_score'] = 0

    query_results = query_subject(input_obj, loaded_cnt_vct, loaded_tfidf_new_matrix, loaded_docID, loaded_mat_activeness, loaded_ranking_metrics)

    userID_to_doc = {}
    with jsonlines.open('data_india_sample2.jl') as reader:
        for obj in reader:
            if ("country" not in request_args) or (obj['country'] in request_args.getlist('country')):
                if ("institute" not in request_args) or (obj['institute'] in request_args.getlist('institute')):
                    userID_to_doc[obj['user']] = obj

    final_results = []
    for userID, score in query_results:
        if userID in userID_to_doc:
            doc_details = len(final_results) + 1, score, userID_to_doc[userID]
            final_results.append(doc_details)

    return final_results[:1000]

def get_close_matches_indexes(word, possibilities, n=3, cutoff=0.6):
    if not n >  0:
        raise ValueError("n must be > 0: %r" % (n,))
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))
    result = []
    s = SequenceMatcher()
    s.set_seq2(word)
    for idx, x in enumerate(possibilities):
        s.set_seq1(x)
        if s.real_quick_ratio() >= cutoff and \
            s.quick_ratio() >= cutoff and \
            s.ratio() >= cutoff:
            result.append((s.ratio(), idx))

    # Move the best scorers to head of list
    result = _nlargest(n, result)

    # Strip scores for the best n matches
    return [x for score, x in result]

def process_name_query(query_name, request_args):
    name_query = query_name
    prof_names = []
    prof_ids = []

    userIndex = {}
    with jsonlines.open('data_india_sample2.jl') as reader:
        for obj in tqdm(reader, leave=False):
            if obj['user'] not in userIndex:
                prof_names.append(obj['name'])
                prof_ids.append(obj['user'])

    inds = get_close_matches_indexes(name_query, prof_names, n = len(prof_names))
    # Professor names, Scholar ID
    query_results = [prof_ids[i] for i in inds]

    userID_to_doc = {}
    with jsonlines.open('data_india_sample2.jl') as reader:
        for obj in reader:
            if ("country" not in request_args) or (obj['country'] in request_args.getlist('country')):
                if ("institute" not in request_args) or (obj['institute'] in request_args.getlist('institute')):
                    userID_to_doc[obj['user']] = obj
    final_results = []

    for userID in query_results:
        if userID in userID_to_doc:
            doc_details = len(final_results) + 1, 0, userID_to_doc[userID]
            final_results.append(doc_details)

    return final_results[:1000]