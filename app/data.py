"""This is for all the code used to interact with the AlphaVantage API
and the SQLite database. Remember that the API relies on a key that is
stored in your `.env` file and imported via the `config` module.
"""

import sqlite3
import pandas as pd
import requests
from .config import settings


class AlphaVantageAPI:
    def __init__(self, api_key = settings.alpha_api_key):
    
        self.__api_key = api_key

    def get_daily(self, ticker, output_size = "full"):

        """Get daily time series of an equity from AlphaVantage API.

        Parameters
        ----------
        ticker : str
            The ticker symbol of the equity.
        output_size : str, optionalss
            Number of observations to retrieve. "compact" returns the
            latest 100 observations. "full" returns all observations for
            equity. By default "full".

        Returns
        -------
        pd.DataFrame
            Columns are 'open', 'high', 'low', 'close', and 'volume'.
            All are numeric.
        """
        # Create URL
        url = (
            "https://www.alphavantage.co/query?"
            "function=TIME_SERIES_DAILY&"
            f"symbol={ticker}&"
            f"outputsize={output_size}&"
            f"datatype=json&"
            f"apikey={self.__api_key}"
        )

        # Send request to API 
        response = requests.get(url)

        #check for invalid ticker
        if "Time Series (Daily)" not in response.json():
            raise Exception(
                f"Invalid Api call: check that ticker symbol '{ticker}'.")

        # Extract JSON data from response
        response_data = response.json()
        stock_data = response_data["Time Series (Daily)"]

        # Read data into DataFrame
        df = pd.DataFrame.from_dict(stock_data, orient = "index", dtype = "float")

        # Convert index to `DatetimeIndex` named "date"
        df.index = pd.to_datetime(df.index)
        df.index.name = "date"
        # Remove numbering from columns 
        df.columns = [c.split(". ")[1] for c in df.columns]

        # Return DataFrame
        return df

    def check_ticker(self, ticker):
 
        url = (
            "https://www.alphavantage.co/query?"
            "function=SYMBOL_SEARCH&"
            f"keywords={ticker}&"
            f"apikey={self.__api_key}"
        )
        
        api_response = requests.get(url)
        data = api_response.json()

        return data

class SQLRepository:
    def __init__(self, connection):

        self.connection = connection

    def insert_table(self, table_name, records, if_exists = "fail"):
    
        """Insert DataFrame into SQLite database as table

        Parameters
        ----------
        table_name : str
        records : pd.DataFrame
        if_exists : str, optional
            How to behave if the table already exists.

            - 'fail': Raise a ValueError.
            - 'replace': Drop the table before inserting new values.
            - 'append': Insert new values to the existing table.

            Dafault: 'fail'

        Returns
        -------
        dict
            Dictionary has two keys:

            - 'transaction_successful', followed by bool
            - 'records_inserted', followed by int
        """
        
        n_results = records.to_sql(name = table_name, con = self.connection, if_exists = if_exists)
        return {"transaction_successful": True, "records_inserted": n_results}

    def read_table(self, table_name, limit):

        """Read table from database.

        Parameters
        ----------
        table_name : str
            Name of table in SQLite database.
        limit : int, None, optional
            Number of most recent records to retrieve. If `None`, all
            records are retrieved. By default, `None`.

        Returns
        -------
        pd.DataFrame
            Index is DatetimeIndex "date". Columns are 'open', 'high',
            'low', 'close', and 'volume'. All columns are numeric.
        """
        # Create SQL query (with optional limit)
        if limit:
            sql = f"SELECT * FROM '{table_name}' LIMIT {limit}"
        else:
            sql = f"SELECT * FROM '{table_name}'"

        # Retrieve data, read into DataFrame
        df = pd.read_sql(sql=sql, con = self.connection, parse_dates=["date"], index_col="date")

        # Return DataFrame
        return df
