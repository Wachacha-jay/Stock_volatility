import sqlite3

from fastapi import FastAPI
from .config import settings  # Importing settings from config.py
from .data import SQLRepository, AlphaVantageAPI  # Importing data handling classes
from .model import GarchModel  # Importing the GARCH model class
from .models import FitIn, FitOut, PredictIn, PredictOut, SymbolIn, SymbolOut  # Importing Pydantic models


    
# build model method to aggregate the functions
def build_model(ticker, use_new_data):

    # Create DB connection
    connection = sqlite3.connect(settings.db_name, check_same_thread = False)

    # Create `SQLRepository`
    repo = SQLRepository(connection = connection)

    # Create model
    model = GarchModel(repo=repo, ticker = ticker, use_new_data=use_new_data)

    # Return model
    return model


#inititate app
app = FastAPI()


# test app
# `"/hello" path with 200 status code
@app.get("/hello", status_code = 200)
def hello():
    """Return dictionary with greeting message."""
    return {"message": "Hello world"}



# "/fit" path, 200 status code
@app.post("/fit", status_code = 200, response_model = FitOut)
def fit_model(request: FitIn):

    """Fit model, return confirmation message.

    Parameters
    ----------
    request : FitIn

    Returns
    ------
    dict
        Must conform to `FitOut` class
    """
    # Create `response` dictionary from `request`
    response = request.dict()

    # Create try block to handle exceptions
    try:
        # Build model with `build_model` function
        model = build_model(ticker = request.ticker, use_new_data = request.use_new_data)

        # Wrangle data
        model.wrangle_data(n_observations = request.n_observations)

        # Fit model
        model.fit(p = request.p, q = request.q)

        # Save model
        filename = model.dump()

        # Add `"success"` key to `response`
        response["success"] = True

        # Add `"message"` key to `response` with `filename`
        response["message"] = f"Trained and saved '{filename}'."

    # Create except block
    except Exception as e:
        # Add `"success"` key to `response`
        response["success"] = False

        # Add `"message"` key to `response` with error message
        response["message"] = str(e)

    # Return response
    return response


#"/predict" path, 200 status code
@app.post("/predict", status_code = 200, response_model = PredictOut)
def get_prediction(request: PredictIn):

    # Create `response` dictionary from `request`
    response = request.dict()

    # Create try block to handle exceptions
    try:
        # Build model with `build_model` function
        model = build_model(ticker = request.ticker, use_new_data = request.use_new_data)

        # Load stored model
        model.load()

        # Generate prediction
        prediction = model.predict_volatility(horizon = request.n_days)

        # Add `"success"` key to `response`
        response["success"] = True

        # Add `"forecast"` key to `response`
        response["forecast"] = prediction

        # Add `"message"` key to `response`
        response["message"] = ""

    # Create except block
    except Exception as e:
        # Add `"success"` key to `response`
        response["success"] = False

        # Add `"forecast"` key to `response`
        response["forecast"] = {}

        #  Add `"message"` key to `response`
        response["message"] = str(e)

    # Return response
    return response


@app.post("/check_ticker", response_model=SymbolOut)
def ticker_check(request: SymbolIn):
    response = request.dict()
    try:
        av = AlphaVantageAPI()
        data = av.check_ticker(ticker = request.ticker)
        response["result"] = data
        response["success"] = True

    except Exception as e:
        response["result"] = {}
        response["success"] = False

    return response