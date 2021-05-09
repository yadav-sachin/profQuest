from flask import Flask, render_template, request, redirect
from tfidf_model import process_query
from tfidf_model import process_name_query

app = Flask(__name__)

@app.route("/")
def home():
    countries_list = []
    with open("web_data/countries_list.txt") as country_file:
        countries_list = [line.strip() for line in country_file]
    institutions_list = []
    for country in countries_list:
        with open("web_data/{}_institutes.txt".format(country)) as institutes_file:
            institutions_list.extend([line.strip() for line in institutes_file])
    return render_template("index.html", countries = countries_list, institutes = institutions_list)

@app.route("/search")
def search_subject():
    countries_list = []
    with open("web_data/countries_list.txt") as country_file:
        countries_list = [line.strip() for line in country_file]
    institutions_list = []
    for country in countries_list:
        with open("web_data/{}_institutes.txt".format(country)) as institutes_file:
            institutions_list.extend([line.strip() for line in institutes_file])
    if 'q' in request.args: 
        query = request.args['q']
        pageSize = 25
        if 'pagesize' in request.args:
            pageSize = request.args['pagesize']
        pageNum = 1
        query_docs = []
        isNameSearch = False
        if request.args['searchType'] == 'subject':
            query_docs = process_query(query, request.args)
            isNameSearch = False
        else:
            query_docs = process_name_query(query, request.args)
            isNameSearch = True
        if 'page' in request.args:
            pageNum = int(request.args['page'])
        query_docs = query_docs[(pageNum - 1)*(pageSize) : (pageNum)*(pageSize)]
        return render_template("search_results.html", query_docs = query_docs, pageNum = pageNum, countries = countries_list, institutes = institutions_list, request_args = request.args, isNameQuery = isNameSearch)
    else:
        return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)