"""This module extracts information from your `.env` file so that
you can use your AplhaVantage API key in other parts of the application.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


def get_env_path(filename: str = ".env") -> str:
    """
    Returns the absolute path to the .env file in the project root.
    Assumes the .env file is in the parent directory of this config file.
    """
    current_file_path = Path(__file__).absolute()
    project_root = current_file_path.parent.parent  # Go up two levels from app/config.py
    env_path = project_root / filename
    
    if not env_path.exists():
        raise FileNotFoundError(f"No .env file found at: {env_path}")
    
    return str(env_path)


class Settings(BaseSettings):
    """Project settings validated using Pydantic."""
    
    alpha_api_key: str
    db_name: str
    model_dir: str
    
    class Config:
        env_file = get_env_path()
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = 'ignore'  # Ignore extra variables in .env


# Singleton instance of settings to import throughout the application
settings = Settings()