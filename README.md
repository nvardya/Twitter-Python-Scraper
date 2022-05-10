# Twitter-Python-Scraper
A serverless AWS architecture used to scrape news about specific stocks from Twitter's API endpoint. AWS Lambda (Python), MySQL, and Pub/Sub services were used to create this project

![TwitterScraperArchitecture](https://user-images.githubusercontent.com/53916435/167712993-cd8fafc8-b954-442e-bf56-6880f1803fdc.jpg)

I personally use Twitter to follow news about the stocks that I currently use. However, there's so many tweets about stocks each day and it's hard to pick the noteworthy tweets out of the noise. So I decided to create a solution to scrape Twitter for the tweets I actually care about. ***The objective of this solution is to create a daily email notification of the 10 most popular (most likes) tweets relating to my stocks from the day***

**Step 1: Create Cloudwatch EventBridge**
Due to the limitations with the Twitter API endpoints, I could not simply make a single API call to Twitter to pull the most popular tweets from the day. Instead, I needed to scrape tweets frequently throughout the day. I decided that I would scrape from Twitter every 30 minutes. I needed to create a CloudWatch EventBridge to schedule these frequent calls to the Twitter API endpoints. Per the below screenshot, you can see I have the CloudWatch EventBridge triggered every 30 minutes during business hours (since that is when tweets about stocks are most frequently sent)
![image](https://user-images.githubusercontent.com/53916435/167715757-72d44eca-e94d-41cb-a8f6-e09afac52551.png)


**Step 2: Connect CloudWatch EventBridge to AWS Lambda**
When my CloudWacth EventBridge is triggered via the schedule I configured in the previous step, it will need to trigger my AWS Lambda function to pull data from Twitter's API endpoint

**Step 3: Create AWS Lambda Function to scrape data from Twitter via API**
This is where most of the effort was 

