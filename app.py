# importing all necessary modules
import tweepy
from noaa_sdk import NOAA
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import numpy as np
from rank_bm25 import BM25Okapi
import re
from flask import Flask, render_template, request, jsonify

# Declare application
app= Flask(__name__)

# Declare data stores
class DataStore():
    CityName=None
    WeatherVals=None
    WeatherObs=None
    CloudLyr=None
    SentVals=None
    TweetTerms=None
data=DataStore()

# Define main code
@app.route("/main",methods=["GET","POST"])

@app.route("/",methods=["GET","POST"])

def homepage():

    # Get city selected from user submission, default is Chicago
    CityName = request.form.get('City_field','Chicago')

    q = CityName.lower()

    geocode = {
        #"new york" : '11430',
        "los angeles" : '90045',
        "chicago" : '60666',
        #"washington dc" : '22202',
        "san francisco" : '94128',
        "boston" : '02128',
        "dallas" : '75261',
        "houston" : '77032',
        #"philadelphia" : '19113',
        "atlanta" : '30320',
        "miami" : '33142',
        "detroit" : '48174',
        "phoenix" : '85034',
        "seattle" : '98158',
        "orlando" : '32827',
        "minneapolis" : '55450',
        "denver" : '80249',
        "cleveland" : '44135',
        "san diego" : '92101',
        "portland" : '97202',
        "tampa" : '33614',
        "st louis" : '63145',
        "charlotte" : '28208',
        "salt lake" : '84122',
        "sacramento" : '95837',
    }

    zip = geocode[q]

    n = NOAA()

    # each row will record an hourly observation
    obs = pd.DataFrame(columns=['timestamp', 'textDescription', 'temperature', 'windSpeed', 'visibility',
                        'precipitationLastHour', 'relativeHumidity', 'windChill', 'heatIndex'],#, 'cloudLayers'],
                        index=range(1, len(list(n.get_observations(zip,'US')))))

    # get NWS observations from last 7 days for city using zip code
    observations = n.get_observations(zip,'US')
    rowNum = 0

    for observation in observations:
        obs['timestamp'][rowNum] = observation['timestamp']
        obs['textDescription'][rowNum] = observation['textDescription']
        #print(observation['textDescription'])
        if type(observation['temperature']['value']) == int or type(observation['temperature']['value']) == float:
            # convert to Fahrenheit
            obs['temperature'][rowNum] = float(observation['temperature']['value'])*9/5+32
        if type(observation['windSpeed']['value']) == int or type(observation['windSpeed']['value']) == float:
            # convert to mph
            obs['windSpeed'][rowNum] = float(observation['windSpeed']['value']) * 0.621371
        if type(observation['visibility']['value']) == int or type(observation['visibility']['value']) == float:
            # convert to miles
            obs['visibility'][rowNum] = float(observation['visibility']['value']) * 0.000621371
        if type(observation['relativeHumidity']['value']) == int or type(observation['relativeHumidity']['value']) == float:
            # percent humidity
            obs['relativeHumidity'][rowNum] = observation['relativeHumidity']['value']
        if type(observation['windChill']['value']) == int or type(observation['windChill']['value']) == float:
            # convert to Fahrenheit
            obs['windChill'][rowNum] = float(observation['windChill']['value'])*9/5+32
        if type(observation['heatIndex']['value']) == int or type(observation['heatIndex']['value']) == float:
            # convert to Fahrenheit
            obs['heatIndex'][rowNum] = float(observation['heatIndex']['value'])*9/5+32
        #if len(observation['cloudLayers']) > 1:
            # amount of cloud cover
        #    obs['cloudLayers'][rowNum] = observation['cloudLayers'][0]['amount']
        rowNum = rowNum + 1

    # pull data from observations to create data we want to display in UI
    try:
        descriptions = obs['textDescription'].tolist()
        list_of_weather_obs = []
        for row in descriptions:
            items = re.split(" and ", row)
            for item in items:
                if item != '':
                    list_of_weather_obs.append(item)
        weather_obs = pd.Series(list_of_weather_obs).value_counts()
    except:
        weather_obs = pd.Series(dtype='int')
    try:
        temp = "Temperature (F):  Max: {} Avg: {} Min: {}".format(
                int(np.nanmax(obs['temperature'])),
                int(np.nanmean(obs['temperature'])),
                int(np.nanmin(obs['temperature'])))
    except:
        temp = "Temperature NA"
    try:
        wind_sp = "Wind Speed (mph):  Max: {} Avg: {} Min: {}".format(
                int(np.nanmax(obs['windSpeed'])),
                int(np.nanmean(obs['windSpeed'])),
                int(np.nanmin(obs['windSpeed'])))
    except:
        wind_sp = "Wind Speed NA"
    try:
        vis = "Visibility (miles):  Max: {} Avg: {} Min: {}".format(
                int(np.nanmax(obs['visibility'])),
                int(np.nanmean(obs['visibility'])),
                int(np.nanmin(obs['visibility'])))
    except:
        vis = "Visibility NA"
                
    try:
        hum = "Rel Humidity (percent):  Max: {} Avg: {} Min: {}".format(
                int(np.nanmax(obs['relativeHumidity'])),
                int(np.nanmean(obs['relativeHumidity'])),
                int(np.nanmin(obs['relativeHumidity'])))
    except:
        hum = "Rel Humidity NA"
    try:
        wind_ch = "Wind Chill (F):  Max: {} Avg: {} Min: {}".format(
                int(np.nanmax(obs['windChill'])),
                int(np.nanmean(obs['windChill'])),
                int(np.nanmin(obs['windChill'])))
    except:
        wind_ch = "Wind Chill NA"
    try:
        heat_ind = "Heat Index (F):  Max: {} Avg: {} Min: {}".format(
                int(np.nanmax(obs['heatIndex'])),
                int(np.nanmean(obs['heatIndex'])),
                int(np.nanmin(obs['heatIndex'])))
    except:
        heat_ind = "Heat Index NA"

    #try:
    #    cloud_lyr = obs['cloudLayers'].value_counts()
    #except:
    #    cloud_lyr = pd.Series({'NA': 'NA'})

    data.WeatherObs = []

    # get value counts to be used for bar chart
    for name, weight in weather_obs.items():
        data.WeatherObs.append({'name': name, 'weight' : weight})

    data.WeatherVals = dict({'names' : ['temp', 'wind_sp', 'vis', 'hum', 'wind_ch', 'heat_ind'], 
                                'values': [temp, wind_sp, vis, hum, wind_ch, heat_ind]})
    #data.CloudLyr = dict({'names': list(cloud_lyr.axes[0]), 'weights' : cloud_lyr.values.tolist()})

    # get tweepy bearer token from txt file
    with open('bearer_token.txt') as bt:
        betk = bt.readline()

    # create client with bearer token
    client = tweepy.Client(bearer_token=betk)

    # Get tweets that match queries
    # -is:retweet means I don't wantretweets
    # lang:en is asking for the tweets to be in english

    # for entire corpus from queries
    corpus = []
    # for tweet ids
    ids = []
    # for bm25 ranking scores
    scores = pd.DataFrame(columns=['id', 'document', 'score'])

    # generates one request for several queries containing city + weather term
    query = '({0} {1} OR {0} {2} OR {0} {3} OR {0} {4} OR {0} {5} OR {0} {6} OR {0} {7}) -is:retweet lang:en'.format(
            q, 'weather', 'rain', 'snow', 'sunny', 'hot', 'cold', 'warm')
    tweets = tweepy.Paginator(client.search_recent_tweets, query=query,
            tweet_fields=['context_annotations', 'author_id'], max_results=100).flatten(limit=1000)
    for tweet in tweets:
        ids.append(tweet.author_id)
        corpus.append(tweet.text)

    # generate bm25 scores for relevance to weather terms and store in scores
    tokenized_corpus = [doc.split(" ") for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    bm25_query = "{} weather rain snow sunny hot cold warm"
    tokenized_query = bm25_query.split(" ")
    doc_scores = bm25.get_scores(tokenized_query)
    scores_temp = pd.concat([pd.Series(ids, name='id'), pd.Series(corpus, name='document'), pd.Series(doc_scores, name='score')], axis=1)
    scores = pd.concat([scores, scores_temp])

    # don't want duplicate tweets
    scores = scores.drop_duplicates()

    # remove documents(tweets) with 0 relevance scores
    scores = scores[scores['score'] > 0]
    scores.reset_index(drop=True, inplace=True)

    # get sentiment values for each document
    sentiment = SentimentIntensityAnalyzer()
    sentiments = pd.DataFrame(columns=["id", "document", "neg", "neu", "pos", "compound"])

    for i in range(scores.shape[0]):
            sent = sentiment.polarity_scores(scores['document'][i])
            sentiments.loc[len(sentiments.index)] = [scores['id'][i], scores['document'][i],
                    sent['neg'], sent['neu'], sent['pos'], sent['compound']]

    sents = sentiments
    sents.drop(columns=['document'])

    # so we only have one entry per user, average all sentiment outputs for each individual user account
    sents = sents.groupby('id', as_index=False, sort=False).mean(numeric_only=True)

    # initialize and assign sentiment outputs
    comp_mean = '%.3f' % np.mean(sents['compound'])
    comp_size = len(sents['compound'])
    pos = '%.1f' % (100 * sum(sents['compound'] > 0.1)/comp_size)
    neu = '%.1f' % (100 * sum(0.1 >= abs(sents['compound']))/comp_size)
    neg = '%.1f' % (100 * sum(sents['compound'] < -0.1)/comp_size)

    data.SentVals = dict({'names' : ['comp_mean', 'pos', 'neu', 'neg'], 
                                'values': [comp_mean, pos, neu, neg]})

    # borrow some stopwords from nltk library and add a few others giving problems
    stop_words = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
        "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
        "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what",
        "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a",
        "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by",
        "for", "with", "about", "against", "between", "into", "through", "during", "before", "after",
        "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
        "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all",
        "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
        "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don",
        "should", "now", 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'co', 'new',
        'york', 'los', 'angeles', 'chicago', 'washington', 'dc', 'san', 'francisco', 'boston',
        'dallas', 'houston', 'philadelphia', 'atlanta', 'miami', 'detroit', 'phoenix', 'seattle', 
        'orlando', 'minneapolis', 'denver', 'cleveland', 'diego', 'portland', 'tampa', 'st', 
        'louis', 'charlotte', 'salt', 'lake', 'sacramento', 'buffalo', 'alabama', 'al', 'alaska',
        'ak', 'arizona', 'az', 'arkansas', 'ar', 'california', 'ca', 'colorado', 'connecticut',
        'ct', 'delaware', 'de', 'florida', 'fl', 'georgia', 'ga', 'hawaii', 'hi', 'idaho', 'id',
        'illinois','indiana', 'in', 'iowa', 'ia', 'kansas', 'ks', 'kentucky', 'ky', 'louisiana',
        'la', 'maine', 'me', 'maryland', 'md', 'massachusetts', 'ma', 'michigan', 'mi', 'minnesota',
        'mn', 'mississippi', 'ms', 'missouri', 'mo', 'montana', 'mt', 'nebraska', 'ne', 'nevada',
        'nv', 'new', 'hampshire', 'nh', 'jersey', 'nj', 'mexico', 'nm', 'york', 'ny', 'north',
        'carolina', 'nc', 'dakota', 'nd', 'ohio', 'oh', 'oklahoma', 'ok', 'oregon', 'or',
        'pennsylvania', 'pa', 'rhode island', 'ri', 'south', 'sc', 'sd', 'tennessee', 'tn', 'texas',
        'tx', 'utah', 'ut', 'vermont', 'vt', 'virginia', 'va', 'wa', 'west', 'wv', 'wisconsin', 'wi',
        'wyoming', 'wy', 'https', 'weather', 'will', 'great', '', ' '}

    # gather all terms from all documents
    doc_terms = ' '.join(sentiments['document'])
    # split the values with non-alpha as delimiter
    tokens = re.split('[^a-zA-Z]', doc_terms)
        
    # convert each token into lowercase
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()

    # use list comprehension to remove stopwords
    filtered_tweet_terms = [i for i in tokens if i not in stop_words]

    data.TweetTerms = []

    # get value counts to be used for bar chart
    tweet_terms = pd.Series(filtered_tweet_terms).value_counts()
    for name, weight in tweet_terms.items():
        data.TweetTerms.append({'name': name, 'weight' : weight})
    
    return render_template("index.html",CityName=CityName)

# Provide route for all data
@app.route("/get-wv-data",methods=["GET","POST"])
def returnWVData():
    g=data.WeatherVals

    return jsonify(g)

@app.route("/get-wo-data",methods=["GET","POST"])
def returnWOData():
    h=data.WeatherObs

    return jsonify(h)

#@app.route("/get-cl-data",methods=["GET","POST"])
#def returnCLData():
#    m=data.CloudLyr

#    return jsonify(m)

@app.route("/get-sv-data",methods=["GET","POST"])
def returnSVData():
    f=data.SentVals

    return jsonify(f)

@app.route("/get-tt-data",methods=["GET","POST"])
def returnTTData():
    n=data.TweetTerms

    return jsonify(n)

if __name__ == "__main__":
    app.run(debug=True)

