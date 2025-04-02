from pydantic import BaseModel

# `FitIn` class
class FitIn(BaseModel):
    ticker: str
    n_observations: int
    use_new_data: bool
    p: int
    q: int

# `FitOut` class
class FitOut(FitIn):
    success: bool
    message: str

# `PredictIn` class
class PredictIn(BaseModel):
    n_days: int
    ticker: str
    use_new_data: bool

# `PredictOut` class
class PredictOut(PredictIn):
    forecast: dict
    success: bool
    message: str

# `SymbolIn` class
class SymbolIn(BaseModel):
    ticker: str

# `SymbolOut` class
class SymbolOut(SymbolIn):
    result: dict
    success: bool