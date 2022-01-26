from datetime import datetime
from multiprocessing.dummy import current_process
from unicodedata import name

from aiohttp import client
import confg
import os
from binance.client import Client
import pprint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import schedule
import time

def get_daily_dataframe():
    starttime= '1 day ago UTC'
    interval = '5m'
    bars = client.get_historical_klines(symbol, interval, starttime)
    for line in bars:
        del line[5:]
    
    df = pd.DataFrame(bars, columns=['date','open', 'high', 'low', 'close'])
    return df


def sma_trade_logic():
    symbol_df = get_daily_dataframe()
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

def buy_or_sell(buy_sell_list, df):

    current_price = current_price = client.get_symbol_ticker(symbol=symbol) 
    index=len(buy_sell_list)-1
    now = datetime.now()

    if buy_sell_list[index] == 1:
        print(df['Buy'][index])
            
        if current_price['price'] < df['Buy'][index]:
            print()
            print('*****Buy...')
            print(now)
            print('*************************')
            # btc=client.get_asset_balance(asset='BTC')
            # quantity = round((float(btc['free'])/current_price)-0.0001,4)
            # buy_order = client.order_market_buy(symbol=symbol, quantity=quantity)
            # print(buy_order)

    elif buy_sell_list[index]==-1.0:
        print(df['Sell'][index])
        
        if current_price['price'] > df['Sell'][index]:
            print()
            print('*****Sell!!!!')
            print(now)
            print('*************************')
            # quantity=round(float(client.get_asset_balance(asset='ETH')['free'])-0.0001,4)                    
            # sell_order = client.order_market_sell(symbol=symbol, quantity=quantity)
            # print(sell_order)
    else:

        print()
        print('No signal...')
        print(now)
        print('*************************')

def main():
    schedule.every(5).minutes.do(sma_trade_logic)
    while True:
        schedule.run_pending()

if __name__ == "__main__":
    
    api_key = confg.API_KEY
    api_secret = confg.API_SECRET
    
    client = Client(api_key, api_secret)

    # pprint.pprint(client.get_account())
    print('client on!!!')

    symbol = 'ETHBTC'
    
    main()