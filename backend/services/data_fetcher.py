import yfinance as yf
import numpy as np
from cachetools import TTLCache
from datetime import date
import time
import os

BATCH_SIZE = 50
BATCH_INTERVAL_DAYS = 2  # 何日ごとに入れ替えるか

# 東証プライム主要銘柄プール（200社）
# バッチ数 = 200 / 50 = 4バッチ → 2日×4 = 8日で全社一巡
_ALL_STOCKS: list[tuple[str, str]] = [
    # ── 輸送用機器 ──
    ("7203.T", "トヨタ自動車"),
    ("7267.T", "本田技研工業"),
    ("7201.T", "日産自動車"),
    ("7269.T", "スズキ"),
    ("7270.T", "SUBARU"),
    ("7202.T", "いすゞ自動車"),
    ("7261.T", "マツダ"),
    ("6902.T", "デンソー"),
    # ── 電機・精密 ──
    ("6758.T", "ソニーグループ"),
    ("6861.T", "キーエンス"),
    ("6954.T", "ファナック"),
    ("6981.T", "村田製作所"),
    ("6367.T", "ダイキン工業"),
    ("8035.T", "東京エレクトロン"),
    ("6752.T", "パナソニックHD"),
    ("6501.T", "日立製作所"),
    ("6594.T", "ニデック"),
    ("6503.T", "三菱電機"),
    ("6506.T", "安川電機"),
    ("6645.T", "オムロン"),
    ("6971.T", "京セラ"),
    ("6762.T", "TDK"),
    ("6857.T", "アドバンテスト"),
    ("6963.T", "ローム"),
    ("6988.T", "日東電工"),
    ("7731.T", "ニコン"),
    ("7751.T", "キヤノン"),
    # ── 情報・通信・IT ──
    ("9984.T", "ソフトバンクグループ"),
    ("9432.T", "日本電信電話"),
    ("9433.T", "KDDI"),
    ("9434.T", "ソフトバンク"),
    ("4689.T", "LINEヤフー"),
    ("3659.T", "ネクソン"),
    ("6702.T", "富士通"),
    ("6701.T", "NEC"),
    ("9613.T", "NTTデータグループ"),
    ("4307.T", "野村総合研究所"),
    ("4704.T", "トレンドマイクロ"),
    # ── 製薬・医療 ──
    ("4502.T", "武田薬品工業"),
    ("4503.T", "アステラス製薬"),
    ("4519.T", "中外製薬"),
    ("4523.T", "エーザイ"),
    ("4568.T", "第一三共"),
    ("4507.T", "塩野義製薬"),
    ("4151.T", "協和キリン"),
    ("4543.T", "テルモ"),
    ("7733.T", "オリンパス"),
    # ── 金融 ──
    ("8306.T", "三菱UFJフィナンシャルG"),
    ("8316.T", "三井住友フィナンシャルG"),
    ("8411.T", "みずほフィナンシャルG"),
    ("8591.T", "オリックス"),
    ("8766.T", "東京海上HD"),
    ("8750.T", "第一生命HD"),
    ("8604.T", "野村ホールディングス"),
    ("8601.T", "大和証券グループ"),
    # ── 化学・素材 ──
    ("4063.T", "信越化学工業"),
    ("4901.T", "富士フイルムHD"),
    ("4452.T", "花王"),
    ("3407.T", "旭化成"),
    ("4183.T", "三井化学"),
    ("4188.T", "三菱ケミカルG"),
    ("4042.T", "東ソー"),
    ("4021.T", "日産化学"),
    ("3436.T", "SUMCO"),
    # ── 素材・鉄鋼 ──
    ("5401.T", "日本製鉄"),
    ("5411.T", "JFEホールディングス"),
    ("5108.T", "ブリヂストン"),
    ("5101.T", "横浜ゴム"),
    # ── 小売 ──
    ("9983.T", "ファーストリテイリング"),
    ("8267.T", "イオン"),
    ("3382.T", "セブン＆アイHD"),
    ("3086.T", "Jフロントリテイリング"),
    ("8252.T", "丸井グループ"),
    # ── 食品・飲料 ──
    ("2914.T", "日本たばこ産業"),
    ("2502.T", "アサヒグループHD"),
    ("2503.T", "キリンHD"),
    ("2801.T", "キッコーマン"),
    ("2802.T", "味の素"),
    ("2871.T", "ニチレイ"),
    # ── 不動産・建設 ──
    ("8801.T", "三井不動産"),
    ("8802.T", "三菱地所"),
    ("8830.T", "住友不動産"),
    ("1925.T", "大和ハウス工業"),
    ("1928.T", "積水ハウス"),
    ("1801.T", "大成建設"),
    ("1802.T", "大林組"),
    ("1803.T", "清水建設"),
    ("3289.T", "東急不動産HD"),
    # ── 商社 ──
    ("8002.T", "丸紅"),
    ("8058.T", "三菱商事"),
    ("8053.T", "住友商事"),
    ("8031.T", "三井物産"),
    ("8001.T", "伊藤忠商事"),
    # ── エネルギー ──
    ("5020.T", "ENEOSホールディングス"),
    ("5019.T", "出光興産"),
    # ── 重工業・機械 ──
    ("7011.T", "三菱重工業"),
    ("7012.T", "川崎重工業"),
    ("7013.T", "IHI"),
    ("6301.T", "コマツ"),
    ("6326.T", "クボタ"),
    # ── 輸送・物流 ──
    ("9020.T", "東日本旅客鉄道"),
    ("9021.T", "西日本旅客鉄道"),
    ("9022.T", "東海旅客鉄道"),
    ("9001.T", "東武鉄道"),
    ("9005.T", "東急"),
    ("9008.T", "小田急電鉄"),
    ("9009.T", "京成電鉄"),
    ("9101.T", "日本郵船"),
    ("9104.T", "商船三井"),
    ("9107.T", "川崎汽船"),
    # ── サービス・人材 ──
    ("6098.T", "リクルートHD"),
    ("2413.T", "エムスリー"),
    ("4661.T", "オリエンタルランド"),
    # ── エンタメ・ゲーム ──
    ("7974.T", "任天堂"),
    ("3659.T", "ネクソン"),
    ("9766.T", "コナミグループ"),
    ("7832.T", "バンダイナムコHD"),
    ("6460.T", "セガサミーHD"),
    ("3635.T", "コーエーテクモHD"),
    # ── その他 ──
    ("4911.T", "資生堂"),
    ("4912.T", "ライオン"),
    ("3401.T", "帝人"),
    ("3402.T", "東レ"),
    ("3861.T", "王子HD"),
]

# 重複除去（順序を保持）
_seen: set[str] = set()
_UNIQUE_STOCKS: list[tuple[str, str]] = []
for ticker, name in _ALL_STOCKS:
    if ticker not in _seen:
        _seen.add(ticker)
        _UNIQUE_STOCKS.append((ticker, name))

_cache = TTLCache(maxsize=300, ttl=int(os.getenv("CACHE_TTL_SECONDS", 3600)))


def get_current_batch_info() -> dict:
    """現在のバッチ番号・入れ替え日・次の入れ替え日を返す。"""
    total = len(_UNIQUE_STOCKS)
    num_batches = max(1, total // BATCH_SIZE)
    epoch = date(2024, 1, 1)
    days_since_epoch = (date.today() - epoch).days
    batch_index = (days_since_epoch // BATCH_INTERVAL_DAYS) % num_batches
    start = batch_index * BATCH_SIZE
    end = start + BATCH_SIZE

    days_in_current = days_since_epoch % BATCH_INTERVAL_DAYS
    days_until_next = BATCH_INTERVAL_DAYS - days_in_current

    return {
        "batch_index": batch_index,
        "num_batches": num_batches,
        "total_stocks": total,
        "batch_size": BATCH_SIZE,
        "batch_interval_days": BATCH_INTERVAL_DAYS,
        "next_rotation_in_days": days_until_next,
        "start": start,
        "end": min(end, total),
    }


def get_stock_universe() -> list[dict]:
    """本日のバッチに対応する50銘柄を返す。"""
    info = get_current_batch_info()
    batch = _UNIQUE_STOCKS[info["start"]:info["end"]]
    return [{"ticker": t, "name": n} for t, n in batch]


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

    # 429が来たらリトライ（最大3回、指数バックオフ）
    for attempt in range(3):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info or len(info) < 5:
                raise ValueError("empty response")
            break
        except Exception as e:
            msg = str(e)
            if "429" in msg or "Too Many Requests" in msg:
                wait = 10 * (2 ** attempt)  # 10s, 20s, 40s
                print(f"[429] {ticker}: リトライまで{wait}秒待機")
                time.sleep(wait)
                if attempt == 2:
                    print(f"[ERROR] {ticker}: リトライ上限に達しました")
                    return None
            else:
                print(f"[ERROR] {ticker}: {e}")
                return None
    else:
        return None

    try:

        price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
        market_cap = _safe_float(info.get("marketCap"))

        per = _safe_float(info.get("trailingPE") or info.get("forwardPE"))
        pbr = _safe_float(info.get("priceToBook"))
        roe = _safe_float(info.get("returnOnEquity"))
        if roe is not None:
            roe = roe * 100

        revenue_growth = _safe_float(info.get("revenueGrowth"))
        if revenue_growth is not None:
            revenue_growth = revenue_growth * 100

        operating_margin = _safe_float(info.get("operatingMargins"))
        if operating_margin is not None:
            operating_margin = operating_margin * 100

        dividend_yield = _safe_float(info.get("dividendYield"))
        if dividend_yield is not None:
            dividend_yield = dividend_yield * 100

        hist = stock.history(period="1y")
        momentum_52w = None
        if len(hist) > 10 and price:
            year_ago_price = hist["Close"].iloc[0]
            if year_ago_price and year_ago_price > 0:
                momentum_52w = ((price - float(year_ago_price)) / float(year_ago_price)) * 100

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
