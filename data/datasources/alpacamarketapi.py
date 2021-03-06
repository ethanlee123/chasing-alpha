import datetime

from alpaca_trade_api.rest import TimeFrame, TimeFrameUnit, APIError, REST
from dotenv import load_dotenv, find_dotenv

from data.datasources.yahoo_finance import get_all_tickers
from utils.timer import Timer
from datetime import date
from ratelimit import limits, sleep_and_retry
from typing import Final
import os

'''
Requires .env file placed at root level.
'''

config = load_dotenv(find_dotenv())
ALPACA_API_VERSION = "v2"
ALPACA_API_KEY: Final = os.getenv("ALPACA_MARKET_DATA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_MARKET_DATA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
HOURLY_TIMEFRAME = TimeFrame(59, TimeFrameUnit.Minute)
FIVE_MINUTE_TIMEFRAME = TimeFrame(5, TimeFrameUnit.Minute)
ALPACA_API_CALL_LIMIT = 199
ONE_MIN_ONE_SEC = 61

ONE_WEEK_AGO = (date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
FIVE_YEARS_AGO = (date.today() - datetime.timedelta(days=(365*5))).strftime("%Y-%m-%d")


class AlpacaMarketDataApi:

    def __init__(self):
        self.api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version=ALPACA_API_VERSION)

        # Number of tickers whose data was successfully retrieved and stored
        self.actual_tickers_processed = 0

    @sleep_and_retry
    @limits(calls=ALPACA_API_CALL_LIMIT, period=ONE_MIN_ONE_SEC)
    def get_data_by_ticker(self, ticker: str, time_frame, start: str, end: str):
        """
        start and end date format: %Y-%m-%d (2020-01-01)
        API calls limited to 199 per 61 seconds to conform to Alpaca rate limit.
        :param ticker: the name of the ticker symbol
        :param time_frame: the candlestick time period
        :param start: the start date in which to query data from
        :param end: the end date in which to stop querying data from
        :return: a pandas dataframe
        """
        try:
            dataframe = self.api.get_bars(ticker, time_frame, start, end, adjustment='raw').df
            return dataframe
        except APIError:
            print(f"APIError: unable to retrieve {ticker}")

    def save_all_ticker_data(self):
        """
        Saves up to 1000 tickers (found in list) to a csv file.
        :return: void
        """
        list_of_all_tickers = get_all_tickers()

        Timer.start("save_all_tickers")
        for ticker in list_of_all_tickers[0]:
            dataframe = self.get_data_by_ticker(ticker, HOURLY_TIMEFRAME, FIVE_YEARS_AGO, ONE_WEEK_AGO)

            if dataframe is not None:
                self.actual_tickers_processed += 1
                dataframe.to_csv(r'D:\data\market_data.csv', mode="a", index=False, header=False)
                print(f"Tickers processed so far: {self.actual_tickers_processed}")
            if self.actual_tickers_processed == 1000:
                total_time_elapsed = Timer.stop("save_all_tickers")
                print(f"Done. Tickers processed: {self.actual_tickers_processed}. Total time elapsed: {total_time_elapsed}")
                return

