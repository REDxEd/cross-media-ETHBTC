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
import matplotlib.pyplot as plt

from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()
#execute main daily at 01:10 and 13:10

#create a daily candle's dataframe 
def get_daily_dataframe():
    starttime= '1 month ago UTC'
    interval = '1d'
    bars = client.get_historical_klines(symbol, interval, starttime)
    for line in bars:
        del line[5:]
    
    df = pd.DataFrame(bars, columns=['date','open', 'high', 'low', 'close'])
    return df



def buy_or_sell(buy_sell_list, df):

    current_price = current_price = client.get_symbol_ticker(symbol=symbol) 
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
    # schedule.every().day.at("01:10").do(sma_trade_logic)
    # schedule.every().day.at("13:10").do(sma_trade_logic)
    #sched.add_job(sma_trade_logic, 'cron', day_of_week='mon-fri', hour='01,13', minute='10')
    
    @sched.scheduled_job('cron', hour='01,18', minute='25')
    
    
    def sma_trade_logic():
        #dataframe for daily candle
        symbol_df = get_daily_dataframe()

        #colluns media 9days and media 22days
        symbol_df['9d_sma'] = symbol_df['close'].rolling(9).mean()
        symbol_df['22d_sma'] = symbol_df['close'].rolling(22).mean()

        symbol_df.set_index('date', inplace=True)
        symbol_df.index = pd.to_datetime(symbol_df.index, unit='ms')

        symbol_df['Signal'] = np.where(symbol_df['9d_sma'] > symbol_df['22d_sma'], 1, 0)

        symbol_df['Position'] = symbol_df['Signal'].diff()

        symbol_df['Buy'] = np.where(symbol_df['Position'] == 1,symbol_df['close'], np.NaN )
        symbol_df['Sell'] = np.where(symbol_df['Position'] == -1,symbol_df['close'], np.NaN )

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

    #pprint.pprint(client.get_account())
    symbol = 'ETHBTC'
    print('Start...app')
    
    main()


