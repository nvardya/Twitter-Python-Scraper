import requests
import os
import json
import pymysql
import boto3


#Credentials for connecting to the MySQL RDS
endpoint = os.environ['MySQL_Endpoint']
username = os.environ['MySQL_Username']
password = os.environ['MySQL_Password']
database_name = os.environ['MySQL_DB']

connection = pymysql.connect(host=endpoint, user=username, passwd=password, db=database_name)

#Boto3 is used to connect to the SNS Topic
sns_client = boto3.client('sns')

def QueryFromRDS():
    cursor = connection.cursor()
    cursor.execute("SELECT Username, Tweet, LikeCount FROM AllTweets INNER JOIN Users ON AllTweets.AuthorID = Users.ID ORDER BY LikeCount DESC LIMIT 10")
    result = cursor.fetchall()
    MasterString = ''
    for x in result:
        converted_Username = str(x[0])
        converted_Tweet = str(x[1])
        Record = 'Username: ' + converted_Username + '\n Tweet: ' + converted_Tweet + '\n \n'
        MasterString = MasterString + Record
        
     #Publishes the SQL query to the SNS Topic   
    sns_client.publish(TopicArn = os.environ['SNS_Topic'], Message = MasterString, Subject = 'Tweets About My Stocks')

    #Deletes all Tweets from the day from the Tweets table
    cursor1 = connection.cursor()
    cursor1.execute("DELETE FROM AllTweets")
    connection.commit()

    #Deletes all Users from the day from the Users table
    cursor2 = connection.cursor()
    cursor2.execute("DELETE FROM Users")
    connection.commit()

def lambda_handler(event, context):
    QueryFromRDS()
    
