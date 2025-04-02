# Stock Volatility Forecasting with GARCH Models

## Overview

This project provides an end-to-end solution for collecting stock market data, building GARCH (Generalized Autoregressive Conditional Heteroskedasticity) models for volatility forecasting, and deploying these models via a FastAPI web service. The system implements a complete ETL pipeline and offers RESTful endpoints for model training and prediction.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [ETL Pipeline](#etl-pipeline)
- [GARCH Modeling](#garch-modeling)
- [API Documentation](#api-documentation)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [License](#license)

## Features

- Automated data collection from Alpha Vantage API
- SQLite database integration for data persistence
- GARCH model training and volatility forecasting
- REST API with FastAPI for easy integration
- Comprehensive error handling and validation
- Model persistence and caching

## Project Structure
project/
│
├── app/
│   ├── __init__.py           # Make it a package
│   ├── main.py               # FastAPI application
│   ├── models.py             # Data models
│   ├── etl.py                # ETL process implementation
│   ├── garch_model.py        # GARCH model building and prediction
│   ├── config.py             # Configuration settings
│   ├── data.py               # Data handling classes (SQLRepository, AlphaVantageAPI)
│   └── settings.py           # Additional settings (if needed)
│
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation

## ETL Pipeline

The data processing workflow:

1. **Extraction**:
   - Fetch stock data from Alpha Vantage API
   - Support for multiple endpoints (daily, intraday, etc.)
   - Automatic rate limiting handling

2. **Transformation**:
   - Data cleaning and normalization
   - Calculation of daily returns
   - Outlier detection and handling
   - Stationarity checks

3. **Loading**:
   - SQLite database storage with SQLAlchemy ORM
   - Data versioning and updates
   - Efficient querying for model training

## GARCH Modeling

### Model Implementation

- Supports GARCH(p,q) with configurable parameters
- Automatic model selection based on AIC/BIC
- Residual analysis and model diagnostics
- Volatility forecasting capabilities

### Training Process

1. Data preparation and stationarity checks
2. Parameter estimation via maximum likelihood
3. Model validation and backtesting
4. Serialization for future use

## API Documentation

The FastAPI application provides automatic documentation at `/docs` and `/redoc` endpoints.

### Key Endpoints

**POST `/api/v1/models/fit`**
- Train a GARCH model for specified ticker
- Parameters:
  - `ticker`: Stock symbol (e.g., "AAPL")
  - `n_observations`: Number of historical observations to use
  - `model_params`: GARCH order parameters (p, q)
  - `force_retrain`: Bypass cached model

**POST `/api/v1/models/predict`**
- Generate volatility forecasts
- Parameters:
  - `ticker`: Stock symbol
  - `horizon`: Forecast horizon in days
  - `confidence_level`: Prediction interval (default: 0.95)

**GET `/api/v1/data/{ticker}`**
- Checks if ticker exists
- returns possible matches


## Getting Started

### Prerequisites

- Python 3.8+
- Alpha Vantage API key
- SQLite (or other database)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stock-volatility.git
   cd stock-volatility
   ```

2. Set up virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (see below)

### Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

Access the API at `http://localhost:8000`

## Configuration

Create a `.env` file with the following variables:

```ini
# API Configuration
alpha_api_key="your_api_key_here"
db_name=sqlite:///./data/volatility.db
model_directory=./models


## Dependencies

Main requirements:
- FastAPI
- Uvicorn
- SQLAlchemy
- Pandas
- NumPy
- Arch
- Requests
- Python-dotenv

