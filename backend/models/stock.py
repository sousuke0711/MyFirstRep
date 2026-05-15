from pydantic import BaseModel
from typing import Optional


class StockMetrics(BaseModel):
    ticker: str
    name: str
    sector: str
    price: Optional[float]
    market_cap: Optional[float]
    per: Optional[float]
    pbr: Optional[float]
    roe: Optional[float]
    revenue_growth_yoy: Optional[float]
    operating_margin: Optional[float]
    momentum_52w: Optional[float]
    dividend_yield: Optional[float]
    screening_score: Optional[float]
    score_breakdown: Optional[dict]


class AIAnalysis(BaseModel):
    ticker: str
    name: str
    investment_thesis: str
    risks: str
    upside_rating: int  # 1-5
    summary: str


class ScreeningResult(BaseModel):
    stocks: list[StockMetrics]
    total: int
    generated_at: str


class AnalysisResult(BaseModel):
    analyses: list[AIAnalysis]
    generated_at: str
