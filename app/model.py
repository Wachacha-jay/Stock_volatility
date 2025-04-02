import os
from glob import glob

import joblib
import pandas as pd
from arch import arch_model
from .config import settings
from .data import AlphaVantageAPI, SQLRepository
import re

class GarchModel:
    """Class for training GARCH model and generating predictions.

    Atttributes
    -----------
    ticker : str
        Ticker symbol of the equity whose volatility will be predicted.
    repo : SQLRepository
        The repository where the training data will be stored.
    use_new_data : bool
        Whether to download new data from the AlphaVantage API to train
        the model or to use the existing data stored in the repository.
    model_directory : str
        Path for directory where trained models will be stored.

    Methods
    -------
    wrangle_data
        Generate equity returns from data in database.
    fit
        Fit model to training data.
    predict
        Generate volatilty forecast from trained model.
    dump
        Save trained model to file.
    load
        Load trained model from file.
    """

    def __init__(self, ticker, repo, use_new_data = False):
    
        self.ticker = ticker
        self.repo = repo
        self.use_new_data = use_new_data
        self.model_directory = settings.model_directory

    def wrangle_data(self, n_observations):

        """Extract data from database (or get from AlphaVantage), transform it
        for training model, and attach it to `self.data`.

        Parameters
        ----------
        n_observations : int
            Number of observations to retrieve from database

        Returns
        -------
        None
        """
        # Add new data to database if required
        if self.use_new_data:
            #instantiate alphavantage_api
            api = AlphaVantageAPI()
            
            #get daily records for the indicated ticker
            new_data = api.get_daily(ticker = self.ticker)
            
            #insert data to the database
            self.repo.insert_table(table_name = self.ticker, records = new_data, if_exists = "replace")
            

        # Pull data from SQL database
        df = self.repo.read_table(table_name=self.ticker, limit = n_observations + 1)

        # Clean data, attach to class as `data` attribute
        df.sort_index(ascending = True, inplace = True)
        # Create "return" column
        df["return"] = df["close"].pct_change() * 100

        self.data = df["return"].dropna()

    def fit(self, p, q):

        """Create model, fit to `self.data`, and attach to `self.model` attribute.
        For assignment, also assigns adds metrics to `self.aic` and `self.bic`.

        Parameters
        ----------
        p : int
            Lag order of the symmetric innovation

        q : ind
            Lag order of lagged volatility

        Returns
        -------
        None
        """
        # Train Model, attach to `self.model`
        self.model = arch_model(self.data, p=p, q=q, rescale = False).fit(disp = 0)
        self.aic = self.model.aic
        self.bic = self.model.bic

    def __clean_prediction(self, prediction):

        """Reformat model prediction to JSON.

        Parameters
        ----------
        prediction : pd.DataFrame
            Variance from a `ARCHModelForecast`

        Returns
        -------
        dict
            Forecast of volatility. Each key is date in ISO 8601 format.
            Each value is predicted volatility.
        """
        # Calculate forecast start date
        start = prediction.index[0] + pd.DateOffset(days = 1)

        # Create date range
        prediction_dates = pd.bdate_range(start = start, periods = prediction.shape[1])

        # Create prediction index labels, ISO 8601 format
        prediction_index = [d.isoformat() for d in prediction_dates]

        # Extract predictions from DataFrame, get square root

        data = prediction.values.flatten() ** 0.5
        # Combine `data` and `prediction_index` into Series

        prediction_formatted = pd.Series(data, index = prediction_index)
        # Return Series as dictionary
        return prediction_formatted.to_dict()

    def predict_volatility(self, horizon):

        """Predict volatility using `self.model`

        Parameters
        ----------
        horizon : int
            Horizon of forecast, by default 5.

        Returns
        -------
        dict
            Forecast of volatility. Each key is date in ISO 8601 format.
            Each value is predicted volatility.
        """
        # Generate variance forecast from `self.model`
        prediction = self.model.forecast(horizon = horizon, reindex = False).variance

        # Format prediction with `self.__clean_predction`
        prediction_formatted = self.__clean_prediction(prediction)

        # Return `prediction_formatted`
        return prediction_formatted

    def dump(self):
        """Save model to `self.model_directory` with timestamp.
    
        Returns
        -------
        str
            filepath where model was saved.
        """
        # Create timestamp and make it filesystem-safe
        timestamp = pd.Timestamp.now().isoformat()
        # Replace colons and periods with hyphens for Windows compatibility
        safe_timestamp = timestamp.replace(':', '-').replace('.', '-')
        
        # Sanitize the ticker to remove any invalid characters
        sanitized_ticker = re.sub(r'[<>:"/\\|?*]', '_', self.ticker).replace('.', '_')
        
        # Ensure the model directory exists
        if not os.path.exists(self.model_directory):
            os.makedirs(self.model_directory)
        
        # Create filepath, including `self.model_directory`
        filepath = os.path.join(self.model_directory, f"{safe_timestamp}_{sanitized_ticker}.pkl")
        
        # Print the filepath for debugging
        print("Saving model to:", filepath)
        
        try:
            # Save `self.model`
            joblib.dump(self.model, filepath)
        except Exception as e:
            print(f"Failed to save model: {e}")
            raise
        
        # Return filepath
        return filepath

    def load(self):
        """Load most recent model in `model_directory` for the given ticker.
        
        Parameters
        ----------
        ticker : str
            The ticker symbol to load (e.g., "SHOPERSTOP.BSE")
        model_directory : str
            Path to directory containing saved models
            
        Returns
        -------
        object
            The loaded model, or None if loading failed
        """
        try:
            # Sanitize the ticker to match how it was saved
            sanitized_ticker = re.sub(r'[<>:"/\\|?*]', '_', self.ticker).replace('.', '_')
            
            # Create pattern for glob search (match any timestamp + our ticker)
            pattern = os.path.join(self.model_directory, f"*_{sanitized_ticker}.pkl")
            
            # Get all matching files
            matching_files = glob(pattern)
            
            if not matching_files:
                print(f"No model files found for ticker: {ticker}")
                return None
                
            # Sort files by modification time (newest first)
            matching_files.sort(key=os.path.getmtime, reverse=True)
            
            # Get the most recent file
            latest_file = matching_files[0]
            
            # Load the model
            self.model = joblib.load(latest_file)
            print(f"Successfully loaded model from: {latest_file}")
            return self.model
            
        except IndexError:
            print(f"No valid model files found for pattern: {pattern}")
        except FileNotFoundError:
            print(f"Model directory not found: {self.model_directory}")
        except Exception as e:
            print(f"Error loading model for {self.ticker}: {str(e)}")
        
        return None
