import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
from flask import Flask, render_template, request

def clean_tweet(tweet):
    return ' '.join(re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def get_tweet_sentiment(tweet):
    analysis = TextBlob(clean_tweet(tweet))
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity == 0:
        return "neutral"
    else:
        return "negative"

consumer_key = '43wTDoeOeczV5mJzUmIgGV9ZN'
consumer_secret = 'Fmybe3r10QlKp4iLz2d86xAbw38hZU5EwCZ8V1ERNw6o9MqASF'
access_token = '1233398298901434370-XMG19Y0OkXGarkhLjHqFBsVTRl5Wt9'
access_token_secret = 'sv3LQBoolZWYfCWDvriQzzwmyslL3U2HELquCzEqHBf6O'

try:
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
except Exception as e:
    print("Error: Authentication Failed", e)

application = Flask(__name__)
application.static_folder = 'static'

@application.route('/')
def home():
    return render_template("index.html")

@application.route("/predict", methods=['POST'])
def pred():
    query = request.form.get('query')
    count = request.form.get('num')
    if query and count:
        fetched_tweets = get_tweets(api, query, count)
        return render_template('result.html', result=fetched_tweets)
    else:
        return "Please provide both query and count."

@application.route("/predict1", methods=['POST'])
def pred1():
    text = request.form.get('txt')
    if text:
        blob = TextBlob(text)
        if blob.sentiment.polarity > 0:
            text_sentiment = "positive"
        elif blob.sentiment.polarity == 0:
            text_sentiment = "neutral"
        else:
            text_sentiment = "negative"
        return render_template('result1.html', msg=text, result=text_sentiment)
    else:
        return "Please provide a text."

def get_tweets(api, query, count=5):
    count = int(count)
    tweets = []
    try:
        fetched_tweets = tweepy.Cursor(api.search_tweets, q=query, lang='en', tweet_mode='extended').items(count)  # Changed from api.search to api.search_tweets
        for tweet in fetched_tweets:
            parsed_tweet = {}
            if 'retweeted_status' in dir(tweet):
                parsed_tweet['text'] = tweet.retweeted_status.full_text
            else:
                parsed_tweet['text'] = tweet.full_text
            parsed_tweet['sentiment'] = get_tweet_sentiment(parsed_tweet['text'])
            if tweet.retweet_count > 0:
                if parsed_tweet not in tweets:
                    tweets.append(parsed_tweet)
            else:
                tweets.append(parsed_tweet)
        return tweets
    except tweepy.TweepyException as e:
        print("Error : " + str(e))
        return []

if __name__ == '__main__':
    application.run(debug=True)
