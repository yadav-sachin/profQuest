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


def process_query(query, request_args):

    loaded_cnt_vct = pickle.load(open("web_data/count_vectorizer.pkl", "rb"))
    loaded_tfidf_new_matrix = pickle.load(open("web_data/tfidf_new_matrix.pkl", "rb"))
    loaded_docID = pickle.load(open("web_data/doc_id_dict.pkl", "rb"))
    loaded_mat_activeness = pickle.load(open("web_data/mat_activeness.pkl", "rb"))
    loaded_ranking_metrics = pickle.load(open("web_data/ranking_metrics.pkl", "rb"))
    loaded_documents = pickle.load(open("web_data/documents.pkl", "rb"))


    def get_tf_idf_vec(query):
        query = process_string(query)
        cnt_matrix_query = loaded_cnt_vct.transform([query])
        cnt_matrix_query = csr_matrix.transpose(cnt_matrix_query)

        result = loaded_tfidf_new_matrix * cnt_matrix_query
        result = csr_matrix.transpose(result)
        result = result.toarray()[0]
        
        return result

    def get_active_vec(year):
        col = year-1
        citations = loaded_mat_activeness[:,col].squeeze()
        return citations

    def get_slope_vec():
        return loaded_ranking_metrics[:,0].squeeze()

    def get_hindex_vec():
        return loaded_ranking_metrics[:,1].squeeze()
        
    def get_insti_vec():
        return loaded_ranking_metrics[:,2].squeeze()

    def normalise(x):
        return x/np.linalg.norm(x)


    def query_subject(user_input):
        #parameters
        params = ['tfidf', 'active', 'slope', 'hindex', 'insti']
        ranks={}
        for param in params:
            ranks[param]={}

        #set weight factors
        ranks['tfidf']['wt'] = user_input['tfidf_score']
        ranks['active']['wt'] = user_input['active_score']
        ranks['hindex']['wt'] = user_input['hindex_score']
        ranks['slope']['wt'] = user_input['slope_score']
        ranks['insti']['wt'] = user_input['insti_score']
        
        # print(ranks)

        #scale up 
        total_user_input_wt = 0
        for key,val in ranks.items():
            total_user_input_wt += val['wt']
        factor = 100/total_user_input_wt
        for key,val in ranks.items():
            val['wt'] *= factor
        
        ranks['tfidf']['vec'] = normalise(get_tf_idf_vec(user_input['query_string']))
        ranks['active']['vec'] = normalise(get_active_vec(user_input['active_yr']))
        ranks['slope']['vec'] = normalise(get_slope_vec())
        ranks['hindex']['vec'] = normalise(get_hindex_vec())
        ranks['insti']['vec'] = normalise(get_insti_vec())

        final_sc = np.zeros(ranks['tfidf']['vec'].size)
        for key,val in ranks.items():
            final_sc += val['wt']*val['vec']
            
        indices = final_sc.argsort()
        indices = indices[::-1]
        profs = [(i,loaded_documents[i],loaded_docID[i],final_sc[i]) for i in indices]
        metrics = []
        # for ind in indices:
        #     metrics.append([ind,
        #                     ranks['tfidf']['vec'][ind],
        #                     ranks['active']['vec'][ind],
        #                     ranks['slope']['vec'][ind],
        #                 ranks['hindex']['vec'][ind],
        #                     ranks['insti']['vec'][ind],
        #                 ])
        return profs

    #generate in code using user input

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
        input_obj['slope_score'] = int(request_args['slope-citations__weight'])
    else:
        input_obj['slope_score'] = 0

    # Institute Reputation
    if 'inst-reputation__checkbox' in request_args and 'inst-reputation__weight' in request_args:
        input_obj['insti_score'] = int(request_args['inst-reputation__weight'])
    else:
        input_obj['insti_score'] = 0

    # input_obj = dict()
    # input_obj['query_string'] = request_args['q']
    # input_obj['active_yr'] = null_if_not_exists(request_args,'activeness__years')
    # input_obj['tfidf_score'] = null_if_not_exists(request_args,'tfidf__weight')
    # input_obj['active_score'] = null_if_not_exists(request_args,'activeness__weight')
    # input_obj['hindex_score'] = null_if_not_exists(request_args,'h-index__weight')
    # input_obj['slope_score'] = null_if_not_exists(request_args,'slope-citations__weight')
    # input_obj['insti_score'] = null_if_not_exists(request_args,'inst-reputation__weight')

    related_profs = query_subject(input_obj)
    related_result_docs=[]

    rank=1
    for profdata in related_profs:
        if ("country" not in request_args) or (profdata[1]['country'] in request_args.getlist('country')):
            if ("institute" not in request_args) or (profdata[1]['institute'] in request_args.getlist('institute')):
                related_result_docs.append((rank,round(profdata[3],3),profdata[1]))
                rank+=1


    docs_len = min(len(related_result_docs),1000)
    
    return related_result_docs[:docs_len]




def process_name_query(query, request_args):

    loaded_documents = pickle.load(open("web_data/documents.pkl", "rb"))
    loaded_prof_names = pickle.load(open("web_data/prof_names.pkl", "rb"))

    def get_close_matches_indexes(word, possibilities, n=10, cutoff=0.4):
    
        """Use SequenceMatcher to return a list of the indexes of the best 
        "good enough" matches. word is a sequence for which close matches 
        are desired (typically a string).
        possibilities is a list of sequences against which to match word
        (typically a list of strings).
        Optional arg n (default 3) is the maximum number of close matches to
        return.  n must be > 0.
        Optional arg cutoff (default 0.6) is a float in [0, 1].  Possibilities
        that don't score at least that similar to word are ignored.
        """

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


    inds = get_close_matches_indexes(query, loaded_prof_names, n=len(loaded_prof_names))
    related_result_docs=[]

    # tuple -> index, score, doc
    rank = 1

    for ind in inds:
        if ("country" not in request_args) or (loaded_documents[ind]['country'] in request_args.getlist('country')):
            if ("institute" not in request_args) or (loaded_documents[ind]['institute'] in request_args.getlist('institute')):
                related_result_docs.append((rank,0,loaded_documents[ind]))
                rank+=1

    docs_len = min(len(related_result_docs),1000)
    
    return related_result_docs[:docs_len]