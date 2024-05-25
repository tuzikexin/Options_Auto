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
from google_upload import upload_single_file_to_folder
from utils import str2bool, CETFormatter

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# ===================== Initialize the parser
parser = argparse.ArgumentParser(description='Download options data for a given ticker up to a specified end time.')

parser.add_argument('--tickers', type=str, nargs='+', default=['VIX', 'SPX'], help='Ticker symbols for the options data, separated by spaces.')
parser.add_argument('--start_time_h', type=int, default=8, help='Hour of the day to start downloading (0-23, in America/New_York timezone)')
parser.add_argument('--start_time_m', type=int, default=55, help='Minute of the hour to start downloading (0-59, in America/New_York timezone)')
parser.add_argument('--end_time_h', type=int, default=23, help='Hour of the day to end downloading (0-23, in America/New_York timezone)')
parser.add_argument('--end_time_m', type=int, default=55, help='Minute of the hour to end downloading (0-59, in America/New_York timezone)')
parser.add_argument('--test_mode', type=str2bool, default=False, help='Whether to run the code in test mode or not')

# Parse the arguments
args = parser.parse_args()

# ===================== Download options
def setup_directories(base_dir='./data/raw_data'):
    """Ensure the output directory exists."""
    today = datetime.now(timezone('America/New_York')).strftime('%Y%m%d')
    output_dir = os.path.join(base_dir, today)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir



def schedule_start(download_func, output_dir, tickers, start_time_h, start_time_m, end_time_h, end_time_m, test_mode, freq_in_seconds):
    """Schedules the start of the download function."""
    now = datetime.now(timezone('America/New_York'))
    start_time = now.replace(hour=start_time_h, minute=start_time_m, second=0, microsecond=0)

    if now >= start_time:  # example: 10:54 > 8:55
        logger.info(f'now {now} Starting download at {start_time}')
        download_func(output_dir, tickers, end_time_h, end_time_m, test_mode, freq_in_seconds)
    else:
        wait_time = (start_time - now).total_seconds()
        logger.info(f'Scheduling download to start at {start_time} (in {wait_time} seconds)')
        Timer(wait_time, download_func, [output_dir, tickers, end_time_h, end_time_m, test_mode, freq_in_seconds]).start()

def find_and_click_expire_button(driver, retries=2):
    """
    Function to find and click the expire button
    """
    attempts = 0
    while attempts < retries:
        # Find the container with the class name 'container svelte-1ur89ri'
        container = driver.find_element(By.CLASS_NAME, 'container.svelte-1ur89ri')

        # Extract the subelements with aria-haspopup='listbox'
        aria_elements = container.find_elements(By.XPATH, ".//*[@aria-haspopup='listbox']")

        # Filter out the aria_elements which aria-label is in ["All Strike Prices", "List", "All Options"]
        filtered_elements = [element for element in aria_elements if element.get_attribute('aria-label') not in ["All Strike Prices", "List", "All Options"]]

        # If no elements are found, retry
        if len(filtered_elements) > 0:
            # Click the expire_button
            expire_button = filtered_elements[0]
            expire_button.click()
            return True
        else:
            logger.info(f"Attempt {attempts + 1} failed: No elements found. Retrying...")
            attempts += 1
            driver.refresh()
            time.sleep(3)  # Wait for the page to reload

    logger.info(f"Max retries:{retries} reached!!! Unable to find and click the expire button.")
    return False

def get_expiry_day(url_base):
    """
    function to find the expiry dates
    """
    expiry_dates = []
    # Setup Selenium WebDriver
    options = Options()
    # options.add_argument("--start-maximized")  # ensures that the browser window opens in a maximized state

    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging

    # this is for MAC or ChromeDriverManager can find correct version
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) 
    
    # Manually specify the path to ChromeDriver / or in Linux ChromeDriverManager can't find correct version
    ## wget https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.78/linux64/chromedriver-linux64.zip
    ## unzip chromedriver-linux64.zip
    ## sudo mv chromedriver /usr/local/bin/
    ## sudo chmod +x /usr/local/bin/chromedriver
    # driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=options)

    # Open the webpage
    driver.get(url_base)

    # Wait for the page to fully load
    driver.implicitly_wait(3)

    # Find and click the expire button with a maximum of 2 retries
    if not find_and_click_expire_button(driver, retries=2):
        driver.quit()
        exit(1)

    # Wait for the expanded list to be visible
    time.sleep(2)  # Adjust the sleep time if necessary

    # Select the expanded list with the specified class name
    expanded_list = driver.find_element(By.CLASS_NAME, 'dialog-content.tw-top-10.svelte-q648fa')

    # Print all child nodes' dataset attribute values
    child_nodes = expanded_list.find_elements(By.XPATH, "./*")
    
    for node in child_nodes:
        expiry_dates.append(node.get_attribute('data-value'))

    # Close the WebDriver
    driver.quit()

    return expiry_dates

def download_options(output_dir, tickers=['VIX','SPX'], end_time_h=16, end_time_m=5, test_mode=False, freq_in_seconds=180):
    """Main function to download options data."""

    # check the ending time
    end_time = datetime.now(timezone('America/New_York')).replace(hour=end_time_h, minute=end_time_m, second=0, microsecond=0)
    if datetime.now(timezone('America/New_York')) >= end_time:  # example 17:23 > 16:20
        logger.info(f'======= Ending scheduled downloads for {tickers} as the end time {end_time} has been reached.')
        return None
    
    if len(tickers) > 1:
        for ticker in tickers:
            download_single_option(output_dir, ticker)
    else:
        download_single_option(output_dir, tickers[0])

    if test_mode:
        print('======= Ending Test mode only download once')
        return None
    
    # Schedule the next run
    next_run = (datetime.now(timezone('America/New_York')) + timedelta(seconds=freq_in_seconds)).replace(microsecond=0)
    wait_time = (next_run - datetime.now(timezone('America/New_York'))).total_seconds()    
    Timer(wait_time, download_options, [output_dir, tickers, end_time_h, end_time_m, test_mode, freq_in_seconds]).start()
    return None

def download_single_option(output_dir, ticker='VIX'):
    url_base = f'https://finance.yahoo.com/quote/%5E{ticker}/options'
    expiry_dates = get_expiry_day(url_base)

    data_zip_path = download_data(ticker, url_base, expiry_dates, output_dir)
    upload_single_file_to_folder(os.path.basename(data_zip_path), data_zip_path, ticker)
    t = f"upload {os.path.basename(data_zip_path)} to drive"
    print(t)
    logger.info(t)


def download_data(ticker, url_base, expiry_dates, output_dir):
    """Download options data for the specified ticker and expiry dates."""
    logger.info(f'Starting download for {ticker}')
    all_df = []
    with requests.Session() as session:
        for expiry_date in expiry_dates[:30]:
            url = f'{url_base}?date={expiry_date}'
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
                pass
        # save to csv
        all_df = pd.concat(all_df)
        exchange_time = str(datetime.now(timezone('America/Chicago')))[:19].replace(':', '-')
        data_name = f'{ticker}_opt_{exchange_time}'
        data_zip_path = os.path.join(output_dir, f'{data_name}.zip')
        all_df.to_csv(data_zip_path, index=False, compression={'method': 'zip', "archive_name" :f'{data_name}.csv'})
        return data_zip_path

if __name__ == "__main__":
    # make dir
    output_base_dir='./data/raw_data'
    daily_output_dir = setup_directories()

    # =====================  Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(
        os.path.join(output_base_dir, f"download_yahoo_{datetime.now(timezone('America/New_York')).strftime('%Y%m%d')}.log"))
    handler.setFormatter(CETFormatter('%(asctime)s | %(levelname)s | %(message)s', '%Y-%m-%d %H:%M:%S'))
    logger.addHandler(handler)
    # Prevent the logger from propagating messages to the root logger
    logger.propagate = False

    # =====================  start download
    exec_day = str(datetime.now(timezone('America/New_York')))[:19]
    t = f'========== Download started from {exec_day} =========='
    print(t)
    logger.info(t)
    
    schedule_start(download_options, daily_output_dir, args.tickers, args.start_time_h, args.start_time_m, args.end_time_h, args.end_time_m, args.test_mode, 180)

    exec_day = str(datetime.now(timezone('America/New_York')))[:19]
    t = f'========== Download End at {exec_day} =========='
    print(t)
    logger.info(t)
