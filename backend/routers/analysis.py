from fastapi import APIRouter, HTTPException
from datetime import datetime
from services.screener import run_screening
from services.ai_analyzer import analyze_stocks_with_claude
import os

router = APIRouter()


@router.post("/analyze")
def analyze_top_stocks(top_n: int = 10):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEYが設定されていません。.envファイルを確認してください。",
        )

    max_stocks = int(os.getenv("MAX_STOCKS_FOR_AI", 10))
    top_n = min(top_n, max_stocks)

    stocks = run_screening(min_score=0)
    if not stocks:
        raise HTTPException(status_code=503, detail="スクリーニングデータが取得できませんでした")

    top_stocks = stocks[:top_n]

    try:
        analyses = analyze_stocks_with_claude(top_stocks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI分析エラー: {str(e)}")

    return {
        "analyses": analyses,
        "generated_at": datetime.now().isoformat(),
    }
