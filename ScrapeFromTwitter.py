import requests
import os
import json
import datetime
from datetime import date, datetime, timezone
from time import strftime
import pymysql

#Twitter API Bearer Token
bearer_token = os.environ['TwitterBearerToken']


search_url = "https://api.twitter.com/2/tweets/search/recent"

#Credentials for connecting to the RDS
endpoint = os.environ['MySQL_Endpoint']
username = os.environ['MySQL_Username']
password = os.environ['MySQL_Password']
database_name = os.environ['MySQL_DB']

connection = pymysql.connect(host=endpoint, user=username, passwd=password, db=database_name)

today_date = date.today()
converted_today_date = str(today_date)
x = "T00:01:00+00:00"
rfc_date = converted_today_date + x


#CHANGE max_results to 100 (only changing so I don't reach the limit)
query_params = {'query': '(#TSLA -is:retweet is:verified) OR (#ABNB -is:retweet is:verified) OR (#WISH -is:retweet is:verified) OR (#NFLX -is:retweet is:verified)', 'tweet.fields': 'id,text,public_metrics', 'start_time': rfc_date,
                'max_results': 10, 'expansions': 'author_id',
                'user.fields': 'name,username'}



def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentTweetCountsPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", search_url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def ScrapeFromTwitter():
    #Making the GET call to the Twitter API endpoint
    json_response = connect_to_endpoint(search_url, query_params)
    z = json.dumps(json_response, indent=4, sort_keys=True)
    python_dict_format = json.loads(z)
    
    #Accessing the Tweets section of the response returned by Twitter
    cleaned_up_dict = python_dict_format['data']

    for x in cleaned_up_dict:
        tweet_id = x['id']
        author_id = x['author_id']
        like_count = x['public_metrics']['like_count']
        tweet_text = x['text']
        cursor = connection.cursor()
        
        #Inserting the Tweets into the MySQL RDS
        sql = "INSERT INTO AllTweets (TweetID, AuthorID, LikeCount, Tweet) VALUES (%s, %s, %s, %s)"
        val = (tweet_id, author_id, like_count, tweet_text)
        cursor.execute(sql, val)
        connection.commit()
   
    #Accessing the User section of the response returned by Twitter   
    cleaned_up_dict_user = python_dict_format['includes']['users']
   
    for w in cleaned_up_dict_user:
        author_id = w['id']
        name = w['name']
        username = w['username']
        cursor2 = connection.cursor()
        
        #Inserting the Users into the MySQL RDS
        sql2 = "INSERT INTO Users (ID, Name, Username) VALUES (%s, %s, %s)"
        val2 = (author_id, name, username)
        cursor2.execute(sql2, val2)
        connection.commit()
    print(z)     

    
def Handler(event, context):
    ScrapeFromTwitter()
    
