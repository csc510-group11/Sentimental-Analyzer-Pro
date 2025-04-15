from pydantic import BaseModel

class SentimentScore(BaseModel):
    pos: float
    neu: float
    neg: float