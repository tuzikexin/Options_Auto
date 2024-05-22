@echo off
:: cd path to opt_download.py script
cd "C:\path\to\your\script"

:: "C:\path\to\python\python.exe" opt_download.py --tickers VIX SPX --start_time_h 8 --start_time_m 55 --end_time_h 16 --end_time_m 5 --test_mode False
"C:\path\to\python\python.exe" opt_download.py --tickers VIX SPX --start_time_h 8 --start_time_m 55 --end_time_h 16 --end_time_m 5 --test_mode False