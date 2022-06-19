# Twitter-Python-Scraper
A multi-service AWS architecture used to scrape news about specific stocks from Twitter's API endpoint. AWS Lambda (Python), MySQL, and Pub/Sub services were used to create this project

![TwitterScraperArchitecture](https://user-images.githubusercontent.com/53916435/167712993-cd8fafc8-b954-442e-bf56-6880f1803fdc.jpg)

I have a passion for financial markets, so naturally I use Twitter to follow news about the stocks that are of interest to me. However, there's so many tweets about stocks each day and it's hard to pick out the noteworthy ones. So I decided to create a solution to scrape Twitter for the tweets that really matter. ***The objective of this solution is to create a daily email notification of the 10 most popular (most likes) tweets from the day relating to the stocks I am interested in***

**Step 1: Create Cloudwatch EventBridge for Invoking AWS Lambda Function (Scraping from Twitter)**
Due to the limitations with the Twitter API endpoints, I could not simply make a single API call to Twitter to pull the most popular tweets from the day. Instead, I needed to scrape tweets frequently throughout the day. I decided that I would scrape from Twitter every 30 minutes. I needed to create a CloudWatch EventBridge to schedule these frequent calls to the Twitter API endpoints. Per the below screenshot, you can see I have the CloudWatch EventBridge triggered every 30 minutes during business hours (since that is when tweets about stocks are most frequently sent)

![image](https://user-images.githubusercontent.com/53916435/167719262-8d362491-5a55-45f3-b604-3761d92fc8ac.png)

**Step 2: Connect CloudWatch EventBridge to AWS Lambda Function**
When my CloudWacth EventBridge is triggered via the schedule I configured in the previous step, it will need to trigger my AWS Lambda function to pull data from Twitter's API endpoint. This step involves setting up that connection, which can be done on the CloudWatch EventBridge record (simple configuration)

**Step 3: Create AWS Lambda Function to scrape data from Twitter via API**
Creating the Lambda function to pull tweets from Twitter is where most of my effort was spent for this project. I decided to create my Lambda function in Python 3.8. Before performing this step, I had to create a Twitter API account to access their API endpoints. You will receive a bearer token upon making the account - you can view my code to see how I used the bearer token to access my Twitter API account.

One challenge that I had with this project was the limitations with Titter's API parameters. To give some background, tweets about stocks often include the cashtag symbol along with the ticker of the stock (i.e. $APPL, $TSLA, $ABNB). However, only enteprise level Twitter development accounts can query on cashtags. Instead, I had to query on hashtags which is not as meaningful for tweets about stocks (you can see the entire query in my code)
```python
query_params = {'query': '(#TSLA -is:retweet is:verified) OR (#ABNB -is:retweet is:verified) OR (#WISH -is:retweet is:verified) OR (#NFLX -is:retweet is:verified)', 'tweet.fields': 'id,text,public_metrics', 'start_time': rfc_date,
```

**Step 4: Sending Twitter data to MySQL database**
Once I pulled the tweets from Twitter, I sent them to the MySQL RDS that I created. Each time my Lambda function was invoked by the EventBridge rule, the data received from Twitter was send to the MYSQL RDS. One thing to note here is that I created two tables in the MySQL database: 1 for tweets, 1 for users (creators of the Tweet). Based off the complicated JSON structure that Twitter gives as a response, I had to break down the tweets and user data into seprate tables. You can see the below queries for the actual Insert statements into the tables
```python
#Inserting the Tweets into the MySQL RDS
sql = "INSERT INTO AllTweets (TweetID, AuthorID, LikeCount, Tweet) VALUES (%s, %s, %s, %s)"
val = (tweet_id, author_id, like_count, tweet_text)
cursor.execute(sql, val)
connection.commit()
```
```python
#Inserting the Users into the MySQL RDS
sql2 = "INSERT INTO Users (ID, Name, Username) VALUES (%s, %s, %s)"
val2 = (author_id, name, username)
cursor2.execute(sql2, val2)
connection.commit()  
```
**Step 5: Create a 2nd Cloudwatch EventBridge for Invoking a 2nd AWS Lambda Function (Query from RDS + Publish to SNS Topic)**
Another CloudWatch EventBridge is needed to invoke another AWS Lambda Function to query from the RDS and subseuqently send it to SNS. This CloudWatch EventBridge is scheudled once a day at the end of the business day to invoke the AWS Lambda Function (we will see the details of this 2nd AWS Lambda Function in Step 7)

**Step 6: Connect CloudWatch EventBridge to AWS Lambda Function**
When my CloudWacth EventBridge is triggered via the schedule I configured in the previous step, it will need to trigger my AWS Lambda function to query from the MySQL dataase. This step involves setting up that connection, which can be done on the CloudWatch EventBridge record (simple configuration)

**Step 7: Create AWS Lambda Function to query from MySQL database**
This AWS Lambda Function involved executing a query from the MySQL database. As I mentioned in Step 4, I had to create 2 tables in this database: 1 for tweets, 1 for users. My SQL query creates an INNER JOIN on both tables to pull the data correctly
```python
cursor = connection.cursor()
cursor.execute("SELECT Username, Tweet, LikeCount FROM AllTweets INNER JOIN Users ON AllTweets.AuthorID = Users.ID ORDER BY LikeCount DESC LIMIT 10")
result = cursor.fetchall()
```

**Step 8: Publishing SQL Query to SNS Topic**
SNS is a Amazon's Pub/Sub service. Applications publish (send the data) to an SNS Topic or applications subscribe (receive the data) to an SNS Topic. In this case, I published the results returned from my SQL query to the SNS Topic (I created my SNS Topic beforehand). This step was accomplished via the 2nd Lambda Function
```python
#Publishes the SQL query to the SNS Topic   
sns_client.publish(TopicArn = os.environ['SNS_Topic'], Message = MasterString, Subject = 'Tweets About My Stocks')
```
**Step 9: Subscribing via Email to the SNS Topic**
I set up my personal email address to subscribe to the SNS Topic. Since my AWS Lambda Function publishes to the SNS Topic once per day, I will receive a single email at the end of the day that contains the 10 most liked tweets from the day about the stocks I am interested in

![image](https://user-images.githubusercontent.com/53916435/167733351-00f1af5a-d0b1-4907-965c-c50c7359d586.png)

