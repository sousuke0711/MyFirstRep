from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from services.screener import run_screening
from services.data_fetcher import fetch_stock_metrics, get_current_batch_info, get_stock_universe, _UNIQUE_STOCKS

router = APIRouter()


@router.get("/stocks")
def get_stocks(
    min_score: float = Query(default=0, ge=0, le=100),
    sector: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    stocks = run_screening(min_score=min_score, sector_filter=sector)
    batch = get_current_batch_info()
    return {
        "stocks": stocks[:limit],
        "total": len(stocks),
        "batch_info": batch,
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/batch")
def get_batch_info():
    """現在のバッチ情報と対象銘柄一覧を返す。"""
    info = get_current_batch_info()
    universe = get_stock_universe()
    return {
        **info,
        "stocks": universe,
        "today": datetime.now().date().isoformat(),
    }


@router.get("/stocks/{ticker}")
def get_stock_detail(ticker: str):
    stock_map = {t: n for t, n in _UNIQUE_STOCKS}
    name = stock_map.get(ticker)
    if name is None:
        raise HTTPException(status_code=404, detail="銘柄が見つかりません")

    metrics = fetch_stock_metrics(ticker, name)
    if metrics is None:
        raise HTTPException(status_code=503, detail="データ取得に失敗しました")

    return metrics


@router.get("/sectors")
def get_sectors():
    return {
        "sectors": [
            "Technology",
            "Consumer Cyclical",
            "Financial Services",
            "Healthcare",
            "Industrials",
            "Basic Materials",
            "Communication Services",
            "Consumer Defensive",
            "Energy",
            "Real Estate",
            "Utilities",
        ]
    }
