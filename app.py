from flask import Flask, render_template, request, redirect
from tfidf_model import process_query

app = Flask(__name__)

@app.route("/")
def home():
    countries_list = []
    with open("web_data/countries_list.txt") as country_file:
        countries_list = [line.strip() for line in country_file]
    return render_template("index.html", countries = countries_list)

@app.route("/search/subject")
def search_subject():
    if 'q' in request.args: 
        query = request.args['q']
        numInEachPage = 25
        pageNum = 1
        query_docs = process_query(query)
        if 'page' in request.args:
            pageNum = int(request.args['page'])
        query_docs = query_docs[(pageNum - 1)*(numInEachPage) : (pageNum)*(numInEachPage)]
        return render_template("search_results.html", query_docs = query_docs, pageNum = pageNum)

if __name__ == "__main__":
    app.run(debug=True)
