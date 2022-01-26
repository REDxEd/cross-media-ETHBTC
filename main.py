from datetime import datetime
from multiprocessing.dummy import current_process
from operator import contains
import sched
from unicodedata import name

from aiohttp import client

import os
from binance.client import Client

import pandas as pd
import numpy as np
#matplotlib is not necessary now
import matplotlib.pyplot as plt

#necessary to work on heroku
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

#put binance data in dataframe
def get_daily_dataframe():
    starttime= '1 month ago UTC'
    interval = '1d'
    bars = client.get_historical_klines(symbol, interval, starttime)
    for line in bars:
        del line[5:]
    
    df = pd.DataFrame(bars, columns=['date','open', 'high', 'low', 'close'])
    return df


#trigger process to make orderMarket buy or sell
def buy_or_sell(buy_sell_list, df):

    current_price = current_price = client.get_symbol_ticker(symbol=symbol) 
    #get the penultimate element of the list because it is the last closed candle
    index=len(buy_sell_list)-1
    
    print()
                
    
    if buy_sell_list[index] == 1:
        print(df['Buy'][index])
            
        if current_price['price'] < df['Buy'][index]:
            
            btc=client.get_asset_balance(asset='BTC')
            quantity = round((float(btc['free'])/current_price)-0.0001,4)

            try:
                print('try Buy...')
                buy_order = client.order_market_buy(symbol=symbol, quantity=quantity)
                print(buy_order)
                print('DONE! *_*')
            except:
                print('Error create buy order')
            print('**************************************')

    elif buy_sell_list[index]==-1.0:
        print()            
        print(df['Sell'][index])       
        
        if current_price['price'] > df['Sell'][index]:
            quantity=round(float(client.get_asset_balance(asset='ETH')['free'])-0.0001,4)                    
            
            try:
                print('try sell...')
                sell_order = client.order_market_sell(symbol=symbol, quantity=quantity)
                print(sell_order)
                print('DONE! *_*')
            except:
                print('Error create sell order')
            print('**************************************')
    else:
            print()            
            print('No signal...')
            print('**************************************')


def main():
    print('inner main')
    
    
    @sched.scheduled_job('cron', day_of_week='mon,tue,wed,thu,fri,sat,sun', hour='01', minute='10')
    
    
    def sma_trade_logic():
        #dataframe for daily candles
        symbol_df = get_daily_dataframe()

        #create colluns, media 9days and media 22days
        symbol_df['9d_sma'] = symbol_df['close'].rolling(9).mean()
        symbol_df['22d_sma'] = symbol_df['close'].rolling(22).mean()

        symbol_df.set_index('date', inplace=True)
        symbol_df.index = pd.to_datetime(symbol_df.index, unit='ms')

        '''in this case more work is needed. the logic here would also be used to test signals over a longer period of time. in this way we could calculate PnL. As I am phlegmatic, this task is for later -_-'''
        symbol_df['Signal'] = np.where(symbol_df['9d_sma'] > symbol_df['22d_sma'], 1, 0)

        symbol_df['Position'] = symbol_df['Signal'].diff()

        symbol_df['Buy'] = np.where(symbol_df['Position'] == 1,symbol_df['close'], np.NaN )
        symbol_df['Sell'] = np.where(symbol_df['Position'] == -1,symbol_df['close'], np.NaN )

        #can be ignored
        with open('output.txt', 'w') as f:
            f.write(
                    symbol_df.to_string()
                   )
                   
        buy_sell_list = symbol_df['Position'].tolist()

        buy_or_sell(buy_sell_list, symbol_df)
    
    sched.start()

if __name__ == "__main__":
    
    api_key = os.environ['API_KEY']
    api_secret = os.environ['API_SECRET']
    
    client = Client(api_key, api_secret)


    symbol = 'ETHBTC'
    print('Start...app')
    
    main()


