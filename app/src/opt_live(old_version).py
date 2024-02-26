import pandas as pd
from datetime import date, datetime
from datetime import timedelta
from pytz import timezone
import time
import os
import numpy as np
from threading import Timer

from requests_html import HTMLSession
import requests


import logging
logger = logging.getLogger('download_yahoo_finance')
hdlr = logging.FileHandler('download_yahoo_finance.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def download_opt(ticker = 'VIX', freq_in_seconds =60):
    
    url_base = f'https://finance.yahoo.com/quote/%5E{ticker}/options'
    
    session = HTMLSession()
    resp = session.get(url_base)
    
    html = resp.html.raw_html.decode()
    
    splits = html.split("</option>")
    
    session.close()
    
    expiry_dates = [elt[elt.rfind(">"):].strip(">") for elt in splits]
    expiry_dates = [elt for elt in expiry_dates if elt != '']
    

    today = date.today()
    
    output_dir = './data/' + str(today).replace('-', '') + '/'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    
    start_time = datetime.now()  
    stop_time  = datetime(year=today.year, month=today.month, day=today.day, hour=22, minute=45, second=0)
    
    delta      = timedelta(seconds = freq_in_seconds)
    timestamps = []
    time_x = start_time
    while time_x < stop_time :
      time_x += delta
      timestamps.append(time_x) 

    while (datetime.now() < stop_time):
        df = pd.DataFrame()
        
        
        for d in expiry_dates[:30]:
            print(d)
        
            url = url_base + '?date=' + str(int(pd.Timestamp(d).timestamp())) 
            
            agent = 'Mozilla/5.0'
            headers = {'User-Agent': agent}
            
            try:
                re = requests.get(url, headers=headers)
                results = pd.read_html(re.text)
                
            except Exception as e:
                logger.error(f'Failed to extract the data of expiry-{d} from html: {e}')
                pass
                
                
            try:
                if len(results) == 2:
                    call = results[0]
                    put  = results[1]
                
                    call.loc[:, 'Type'] = 'C'
                    put.loc[:, 'Type']  = 'P'
                    call.loc[:, 'Maturity'] = str(d)
                    put.loc[:, 'Maturity'] = str(d)
                    
                    df = pd.concat([df, call])
                    df = pd.concat([df, put])
                    
                else:
                    
                    for re in results:
                        re.loc[:, 'Type'] = ''
                        re.loc[:, 'Maturity'] = str(d)
                        df = pd.concat([df, re])
        
            except Exception as e:
                logger.error(f'Failed to store data of expiry-{d} to dataframe: {e}')
                pass
        
        
        exchange_time = datetime.now(timezone('America/Chicago'))
        
        time_str = str(exchange_time)
        
        time_str2 = time_str[:19].replace(':', '-')
                
        df.to_csv(output_dir + f'{ticker}opt_' +  time_str2 + '.csv')            
    
        print( "-- i will wait now---")
        print(str(datetime.now(timezone('Europe/Amsterdam'))))
        
        now_ts = datetime.now()
        next_ts = timestamps[np.where(np.asarray(timestamps)> now_ts )[0][0]]
        
        wait_time = next_ts - now_ts
        
        time.sleep(wait_time.total_seconds())
        print("i finish waiting")
    
    
    print(f'-------------- finish downloading at {datetime.now()}-------------------------------')


x = datetime.today()

start_time = x.replace(day = x.day   , hour = 16, minute = 43, second = 13, microsecond = 0)

delta = start_time -x 

t = Timer(delta.seconds + 1, download_opt)
t.start()
print('waiting to start')
