import pandas as pd
import os
import requests
from datetime import datetime, timedelta
from requests_html import HTMLSession
from threading import Timer
from io import StringIO
import logging
from pytz import timezone
import argparse
import math
from utils import str2bool, CETFormatter


# ===================== Initialize the parser
parser = argparse.ArgumentParser(description='Download options data for a given ticker up to a specified end time.')

# Add the arguments
parser.add_argument('--ticker', type=str, default='VIX', help='Ticker symbol for the options data')
parser.add_argument('--end_time_h', type=int, default=22, help='Hour of the day to end downloading (0-23, in CET timezone)')
parser.add_argument('--end_time_m', type=int, default=45, help='Minute of the hour to end downloading (0-59, in CET timezone)')
parser.add_argument('--test_mode', type=str2bool, default=False, help='Whether to run the code in test mode or not')

# Parse the arguments
args = parser.parse_args()


# =====================  Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(os.path.join('./data/raw_data', 'download_yahoo_finance.log'))
handler.setFormatter(CETFormatter('%(asctime)s | %(levelname)s | %(message)s', '%Y-%m-%d %H:%M:%S'))
logger.addHandler(handler)
# Prevent the logger from propagating messages to the root logger
logger.propagate = False

# ===================== Download options
def setup_directories(base_dir='./data/raw_data'):
    """Ensure the output directory exists."""
    today = datetime.now(timezone('CET')).strftime('%Y%m%d')
    output_dir = os.path.join(base_dir, today)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def download_data(ticker, url_base, expiry_dates, output_dir):
    """Download options data for the specified ticker and expiry dates."""
    logger.info(f'Starting download for {ticker}')
    all_df = []
    with requests.Session() as session:
        for expiry_date in expiry_dates[:30]:
            url = f'{url_base}?date={int(pd.Timestamp(expiry_date).timestamp())}'
            try:                
                response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                dfs = pd.read_html(StringIO(response.text))

                if len(dfs) == 2:
                    call = dfs[0]
                    put  = dfs[1]
                
                    call.loc[:, 'Type'] = 'C'
                    put.loc[:, 'Type']  = 'P'
                    call.loc[:, 'Maturity'] = str(expiry_date)
                    put.loc[:, 'Maturity'] = str(expiry_date)
                    all_df.append(call)
                    all_df.append(put)
                else:  # have more then two dataframe return!!?
                    for df in dfs:
                        df.loc[:, 'Type'] = ''
                        df.loc[:, 'Maturity'] = str(expiry_date)
                        all_df.append(df)
            except Exception as e:
                logger.error(f'!!!!! Failed to process expiry date {expiry_date}: {e}')
        # save to csv
        all_df = pd.concat(all_df)
        exchange_time = str(datetime.now(timezone('America/Chicago')))[:19].replace(':', '-')
        all_df.to_csv(os.path.join(output_dir, f'{ticker}_opt_{exchange_time}.csv'), index=False)

def download_options(ticker='VIX', end_time_h=22, end_time_m=45, test_mode=False, freq_in_seconds=60):
    """Main function to download options data."""

    # check the ending time
    end_time = datetime.now(timezone('CET'))
    end_time = datetime(year=end_time.year, month=end_time.month, day=end_time.day, 
                        hour=end_time_h, minute=end_time_m, second=0)
    if int(math.ceil(datetime.now(timezone('CET')).timestamp())) >= int(end_time.timestamp()):
        logger.info(f'======= Ending scheduled downloads for {ticker} as the end time{end_time} has been reached.')
        return None
    
    # download options
    url_base = f'https://finance.yahoo.com/quote/%5E{ticker}/options'
    session = HTMLSession()
    response = session.get(url_base)
    expiry_dates = [line[line.rfind(">"):].strip(">") for line in response.html.raw_html.decode().split("</option>")]
    expiry_dates = [line for line in expiry_dates if line != '']
    session.close()

    output_dir = setup_directories()
    download_data(ticker, url_base, expiry_dates, output_dir)

    if test_mode:
        print('Test mode only download once')
        return None
    
    # Schedule the next run
    next_run = (datetime.now(timezone('CET')) + timedelta(seconds=freq_in_seconds)).replace(microsecond=0)
    wait_time = (next_run - datetime.now(timezone('CET'))).total_seconds()    
    Timer(wait_time, download_options, [ticker, end_time_h, end_time_m, test_mode, freq_in_seconds]).start()


if __name__ == "__main__":
    print('Download scheduled. Check the logs for details.')
    exec_day = str(datetime.now(timezone('CET')))[:19].replace(':', '-')
    logger.info(f'========== Download started from {exec_day} ==========')
    download_options(args.ticker, args.end_time_h, args.end_time_m, args.test_mode)
