
#instead of importing flask, we import blueprint
from flask import Blueprint, render_template
import json
import html.parser as htmlparser
from datetime import datetime
import requests
import pandas as pd


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

    
    url = 'https://api.stocktwits.com/api/2/streams/symbol/' + symbol + '.json'

    stockTwits = requests.get(url.format(symbol)).json()
    stockTwits_data = []
    new_sent = ''

    for index in range (0,30):
        
        message = stockTwits['messages'][index]['body']
        username = stockTwits['messages'][index]['user']['username']
        sentiment = str(stockTwits['messages'][index]['entities']['sentiment'])
        avatar = stockTwits['messages'][index]['user']['avatar_url_ssl']

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
            
        }
        
        stockTwits_data.append(stockTwitsData)

    '''
    stockTwits_data = []

    for x in range (0,30):
        
        stockTwitsData = {
            'message' : "I dont think that there is much for them to do with the stock from this point out. Not looking too good IMO",
            'username' : "Brian",
            'sentiment' : "Bullish",
            'avatar' : "https://s3.amazonaws.com/st-avatars/images/default_avatar_thumb.jpg",
            
        }
        
        stockTwits_data.append(stockTwitsData)
    '''
    return render_template('page/dash.1.html',stockTwits_data=stockTwits_data,stock_info=stock_info)
