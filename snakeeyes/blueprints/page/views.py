
#instead of importing flask, we import blueprint
from flask import Blueprint, render_template
import json
import html.parser as htmlparser
from datetime import datetime
import requests
import pandas as pd
import calendar
from dateutil import tz
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener


#create a blueprint with a name of 'page'
page = Blueprint('page', __name__, template_folder='templates')

#instead of doing app.route, we attach it to the blueprint route
@page.route('/')
def home():

    #renders a html template instead 
    return render_template('page/home.html')


@page.route('/dash')
def dash():

    API_KEY = '4HNDQOUQ2A1G90RW'
    symbol = 'AAPL'
    company = "Apple (AAPL)"
    
    #works but not for testing. Dont want to get rate limited
    #--------------ALPHA VANTAGE STARTS HERE------------------
    ''' 
    url1 = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=' + symbol + '&outputsize=compact&datatype=csv&apikey=' + API_KEY
    url2 = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + symbol + '&interval=5min&datatype=csv&apikey=' + API_KEY
    df_daily = pd.read_csv(url1, index_col="timestamp", parse_dates = True, na_values = ' ')
    df_current = pd.read_csv(url2, index_col="timestamp", parse_dates = True, na_values = ' ')

    df_daily['close'] = df_daily['adjusted_close']
    df_daily.index.names = ['date']
    df_current.index.names = ['date']

    


    current_price = '${:,.2f}'.format(df_current.iloc[0]['open'])
    high_price = '${:,.2f}'.format(df_daily.iloc[0]['high'])
    low_price = '${:,.2f}'.format(df_daily.iloc[0]['low'])
    volume = "{:,}".format(int(df_daily.iloc[0]['volume']))
    '''
    
    #use this for rate limiting testing purposes
    current_price = "$105.94"
    high_price = "$400.43"
    low_price = "$400.56"
    volume = "300,001"
    daily_change = "$2.43"

    stock_info = [company,current_price, daily_change,high_price, low_price, volume]
    
    parser = htmlparser.HTMLParser()

    #--------------ALPHA VANTAGE ENDS HERE------------------

    #--------------STOCK TWITS STARTS HERE------------------
    
    url = 'https://api.stocktwits.com/api/2/streams/symbol/' + symbol + '.json'

    stockTwits = requests.get(url.format(symbol)).json()
    stockTwits_data = []
    new_sent = ''

    for index in range (0,30):
        
        message = stockTwits['messages'][index]['body']
        username = stockTwits['messages'][index]['user']['username']
        sentiment = str(stockTwits['messages'][index]['entities']['sentiment'])
        avatar = stockTwits['messages'][index]['user']['avatar_url_ssl']
        tstamp = stockTwits['messages'][index]['created_at'] #this is used for the time 
        new_tstamp = tstamp[0:10] + " " + tstamp[11:19]


        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('America/New_York')
        utc = datetime.strptime(new_tstamp, '%Y-%m-%d %H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        local = utc.astimezone(to_zone)

        month = local.strftime("%b")
        day = local.strftime("%d")
        year = local.strftime("%Y")
        hour = local.strftime("%I")
        minutes = local.strftime("%M")
        am_pm = local.strftime("%p")

        pretty_date = month + " " + day + ", " + year + " @ " + hour + ":" + minutes + am_pm


        #find a better way to do this for sure...



        if(sentiment == "{'basic': 'Bullish'}"):
            new_sent = 'Bullish'
            

        elif(sentiment == "{'basic': 'Bearish'}"):
            new_sent = 'Bearish'
            
        else:
            new_sent = 'Neutral'
            

        new_message= parser.unescape(message)
        
        stockTwitsData = {
            'message' : new_message,
            'username' : username,
            'sentiment' : new_sent,
            'avatar' : avatar,
            'timestamp' : pretty_date,
            
        }
        
        stockTwits_data.append(stockTwitsData)

    
    #--------------STOCK TWITS ENDS HERE------------------

    #--------------TWITTER STARTS HERE------------------
    CONSUMER_KEY = 'HJMjz0h6yKNm2hxA6NNFXP3B4'
    CONSUMER_SECRET = 'hUvGlSFYCdeZsj0yMDrcmrXncWAt5bpnWOzFAvrF8fNvryu2Zx'
    ACCESS_TOKEN = '753677018957504512-OKBKXJMomxUk8Zz0L4HQKUvPSYbQvyE'
    ACCESS_SECRET = 'htvfswIINfuYfxxH546mun0OCPTIzESDNr7x5V4dCVgAR'

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    # Create the api to connect to twitter with your creadentials
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    tweets = []

    #remove -filter:retweets to show retweets as well
    for status in tweepy.Cursor(api.search,q="$AAPl -filter:retweets", tweet_mode='extended').items(30):
        
        tweet = status.full_text
        username = status.user.screen_name
        tweet_id = status.id_str
        link = 'https://twitter.com/statuses/' + tweet_id
        timestamp = status.created_at
        avatar = status.user.profile_image_url_https

        tweetData = {
            'tweet' : tweet,
            'username' : username,
            'link' : link,
            'avatar' : avatar,
            'timestamp' : timestamp,
                
        }
            
        tweets.append(tweetData)

    #--------------TWITTER ENDS HERE------------------
    return render_template('page/dash.1.html',stockTwits_data=stockTwits_data,stock_info=stock_info, tweets=tweets)
