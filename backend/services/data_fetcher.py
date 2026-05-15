import yfinance as yf
import pandas as pd
import numpy as np
from cachetools import TTLCache
import os

# TSE Prime主要銘柄リスト（業種バランスを考慮）
TSE_PRIME_STOCKS = {
    # 輸送用機器
    "7203.T": "トヨタ自動車",
    "7267.T": "本田技研工業",
    "7201.T": "日産自動車",
    "7269.T": "スズキ",
    "7270.T": "SUBARU",
    # 電機・精密
    "6758.T": "ソニーグループ",
    "6861.T": "キーエンス",
    "6954.T": "ファナック",
    "6981.T": "村田製作所",
    "6367.T": "ダイキン工業",
    "8035.T": "東京エレクトロン",
    "6752.T": "パナソニックHD",
    "6501.T": "日立製作所",
    "6594.T": "日本電産（ニデック）",
    "6902.T": "デンソー",
    "4523.T": "エーザイ",
    # 情報・通信
    "9984.T": "ソフトバンクグループ",
    "9432.T": "日本電信電話",
    "9433.T": "KDDI",
    "9434.T": "ソフトバンク",
    "4689.T": "LINEヤフー",
    "3659.T": "ネクソン",
    # 小売
    "9983.T": "ファーストリテイリング",
    "8267.T": "イオン",
    "3382.T": "セブン＆アイHD",
    # 金融
    "8306.T": "三菱UFJフィナンシャルG",
    "8316.T": "三井住友フィナンシャルG",
    "8411.T": "みずほフィナンシャルG",
    "8591.T": "オリックス",
    "8766.T": "東京海上HD",
    # 化学・素材
    "4063.T": "信越化学工業",
    "4901.T": "富士フイルムHD",
    "4452.T": "花王",
    "3407.T": "旭化成",
    "4183.T": "三井化学",
    # 製薬・医療
    "4502.T": "武田薬品工業",
    "4503.T": "アステラス製薬",
    "4519.T": "中外製薬",
    # 不動産・建設
    "8801.T": "三井不動産",
    "8802.T": "菱地所",
    "1925.T": "大和ハウス工業",
    # サービス・人材
    "6098.T": "リクルートHD",
    "2413.T": "エムスリー",
    "4307.T": "野村総合研究所",
    # エネルギー・資源
    "5020.T": "ENEOSホールディングス",
    "8002.T": "丸紅",
    "8058.T": "三菱商事",
    "8053.T": "住友商事",
    # エンタメ・ゲーム
    "7974.T": "任天堂",
    "9022.T": "東海旅客鉄道",
}

_cache = TTLCache(maxsize=200, ttl=int(os.getenv("CACHE_TTL_SECONDS", 3600)))


def _safe_float(val) -> float | None:
    try:
        v = float(val)
        return None if (np.isnan(v) or np.isinf(v)) else v
    except (TypeError, ValueError):
        return None


def fetch_stock_metrics(ticker: str, name: str) -> dict | None:
    cache_key = f"metrics_{ticker}"
    if cache_key in _cache:
        return _cache[cache_key]

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # 株価・時価総額
        price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
        market_cap = _safe_float(info.get("marketCap"))

        # バリュエーション
        per = _safe_float(info.get("trailingPE") or info.get("forwardPE"))
        pbr = _safe_float(info.get("priceToBook"))
        roe = _safe_float(info.get("returnOnEquity"))
        if roe is not None:
            roe = roe * 100  # パーセント変換

        # 成長性
        revenue_growth = _safe_float(info.get("revenueGrowth"))
        if revenue_growth is not None:
            revenue_growth = revenue_growth * 100

        # 収益性
        operating_margin = _safe_float(info.get("operatingMargins"))
        if operating_margin is not None:
            operating_margin = operating_margin * 100

        # 配当
        dividend_yield = _safe_float(info.get("dividendYield"))
        if dividend_yield is not None:
            dividend_yield = dividend_yield * 100

        # 52週モメンタム
        hist = stock.history(period="1y")
        momentum_52w = None
        if len(hist) > 10 and price:
            year_ago_price = hist["Close"].iloc[0]
            if year_ago_price and year_ago_price > 0:
                momentum_52w = ((price - float(year_ago_price)) / float(year_ago_price)) * 100

        # セクター
        sector = info.get("sector") or info.get("industry") or "その他"

        result = {
            "ticker": ticker,
            "name": name,
            "sector": sector,
            "price": price,
            "market_cap": market_cap,
            "per": per,
            "pbr": pbr,
            "roe": roe,
            "revenue_growth_yoy": revenue_growth,
            "operating_margin": operating_margin,
            "momentum_52w": momentum_52w,
            "dividend_yield": dividend_yield,
        }
        _cache[cache_key] = result
        return result

    except Exception as e:
        print(f"[ERROR] {ticker}: {e}")
        return None


def get_stock_universe() -> list[dict]:
    return [{"ticker": t, "name": n} for t, n in TSE_PRIME_STOCKS.items()]
