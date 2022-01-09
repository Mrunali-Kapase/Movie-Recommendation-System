import flask
import joblib
import pandas as pd
from flask import Flask, render_template, request

sig_ker = joblib.load('sig_ker.pkl')
data = pd.read_csv('main.csv')
data= data.drop_duplicates(['movie_title'] , ignore_index=True)
def get_rec(title, sig=sig_ker):
    title = title.lower()
    indices = pd.Series(data.index, index=data['movie_title'])
    if title in (data['movie_title'].unique()):
        idx = indices[title]
        # idx= list(idx)
        # if len(idx)>1:
        #     idx = idx[0]
        # idx= idx[0]
        lst = list(enumerate(sig[idx]))
        score = sorted(lst, key = lambda x:x[1],reverse=True )
    #     print(score)
        ind = [x[0] for x in score[1:6]]
        rec = [data['movie_title'][i] for i in ind]
        return rec
    else:
        return (["Sorry, this movie name is not present in our database"])


from tmdbv3api import TMDb
# import json
import requests
tmdb = TMDb()
from tmdbv3api import Movie
tmdb_movie = Movie()
tmdb.api_key = '923c294a31ab55d16bdd504cf022acfb'

CONFIG_PATTERN = 'http://api.themoviedb.org/3/configuration?api_key={key}'
KEY = '923c294a31ab55d16bdd504cf022acfb'
IMG_PATTERN = 'http://api.themoviedb.org/3/movie/{imdbid}/images?api_key={key}' 

url = CONFIG_PATTERN.format(key=KEY)
r = requests.get(url)
config = r.json()

base_url = config['images']['base_url']
sizes = config['images']['poster_sizes']
"""
    'sizes' should be sorted in ascending order, so
        max_size = sizes[-1]
    should get the largest size as well.        
"""
def size_str_to_int(x):
    return float("inf") if x == 'original' else int(x[1:])
max_size = max(sizes, key=size_str_to_int)


def get_url(title):
    result = tmdb_movie.search(title)
    movie_id = result[0].get('id')
    r = requests.get(IMG_PATTERN.format(key=KEY,imdbid=movie_id))
    api_response = r.json()
    rel_path=api_response['posters'][0]['file_path']
    url = "{0}{1}{2}".format(base_url, max_size, rel_path)
    return url

#initializing the flask
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    movie_name = request.form.get('movie_name')
    # print(movie_name)
    rec_lst = get_rec(str(movie_name))
    poster = get_url(str(movie_name))
    result = tmdb_movie.search(movie_name)
    title = result[0].get('title')
    overview =result[0].get('overview')
    release_date =result[0].get('release_date')
    vote_average =result[0].get('vote_average')
    vote_count =result[0].get('vote_count')
    if str(movie_name).lower() in (data['movie_title'].unique()):
        genres = list(data[data['movie_title']==str(movie_name).lower()]['genres'])[0]
    else:
        genres = 'None'
    if len(rec_lst)==1:
        return render_template('home.html', recommended = rec_lst[0])
    if len(rec_lst)>1:
        return render_template('home.html', poster=poster, recommended1 = rec_lst[0].title(), poster1=get_url(rec_lst[0]),
         recommended2 = rec_lst[1].title(), poster2=get_url(rec_lst[1]),
         recommended3 = rec_lst[2].title(), poster3=get_url(rec_lst[2]),
         recommended4 = rec_lst[3].title(), poster4=get_url(rec_lst[3]),
         recommended5 = rec_lst[4].title(), poster5=get_url(rec_lst[4]),
          title=title,overview=overview, release_date=release_date, vote_average=vote_average , vote_count=vote_count, genres=genres)


if __name__ == '__main__':
    app.run(debug=True)
