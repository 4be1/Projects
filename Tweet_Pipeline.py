import os
import requests
os.environ['TOKEN'] = 'TOKEN'
import json
import pandas as pd
import csv
import datetime, dateutil.parser, unicodedata
import time

def auth():
    return os.getenv('TOKEN')

def create_headers(bearer_token):
headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

return headers


def create_url(keyword, start_date, end_date, max_results = 10):
    
    # you can change this do a diffrent endpoint 
    search_url = "https://api.twitter.com/2/tweets/search/recent"
    
    
    
    # change parameters based on the endpoint you are using 
    
    query_params = {'query': keyword,
                'start_time': start_date,
                'end_time': end_date,
                'max_results': max_results,
                'expansions': 'author_id,in_reply_to_user_id,geo.place_id,referenced_tweets.id',
                'tweet.fields': 'id,author_id,created_at,public_metrics,source',
                 'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                 'next_token':{}}
    return (search_url,query_params)

def connect_to_endpoint(url, headers, params):
    params['next_token'] = next_token 
    # params object received from create_url function 
    response = requests.request("Get", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

bearer_token = auth()
headers = create_headers(bearer_token)
keyword = "CES lang:en"
start_time = "2022-01-08T00:00:00.000Z"
end_time = "2022-01-09T08:59:00.000Z"
# plus one day and 8:50 = 11:50pm (for most recent tweets)


url = create_url(keyword,start_time,end_time,max_results)

json_response = connect_to_endpoint(url[0], headers, url[1])

max_results = 15


#View Raw JSON respponse
#json_response['data']


#View Dictionary Keys
#json_response.keys()


#########################################################################################################

#Take JSON response, select fields and place into DataFrame

tweet_list = []
for t in json_response['data']:
    tweet_list.append([t['id'],t['author_id'],t['text']])


tweet_list = pd.DataFrame(tweet_list)


metrics_list = []
for t in json_response['data']:
    metrics_list.append(t['public_metrics'])

metrics_list = pd.DataFrame(metrics_list)


#user_list = []
#for t in json_response['includes']['users']:
#    user_list.append([t['id']
#                    ,t['username']])
#user_list = pd.DataFrame(user_list)


#Take DataFrames, transform and concat to form table

table = pd.concat([tweet_list,metrics_list],axis=1)
table = table.rename(columns={0:"id",1:"author_id",2:"text"})
#table

############################################################################################################

#Store DF in SQL table

import pymysql
import sqlalchemy 
from sqlalchemy import *


db = pymysql.connect(host = 'HOST',user = 'USER',password = 'PASSWORD')
cursor = db.cursor()

cursor.execute('CREATE DATABASE twitter')

table.to_sql('twitter',con=cursor)


