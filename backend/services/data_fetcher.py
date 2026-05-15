import yfinance as yf
import numpy as np
import json
import random
from pathlib import Path
from datetime import date
import time
import os
from curl_cffi import requests as curl_requests

BATCH_SIZE = 50
BATCH_INTERVAL_DAYS = 2
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", 86400))  # デフォルト24時間
CACHE_FILE = Path(__file__).parent.parent / "stock_cache.json"

# Chrome TLSフィンガープリントを偽装したセッション
# curl_cffi が User-Agent を含む Chrome のリクエストヘッダを自動設定する
_curl_session = curl_requests.Session(impersonate="chrome124")

# ── 銘柄プール（約200社） ─────────────────────────────────────────────────────
_ALL_STOCKS: list[tuple[str, str]] = [
    # 輸送用機器
    ("7203.T", "トヨタ自動車"),
    ("7267.T", "本田技研工業"),
    ("7201.T", "日産自動車"),
    ("7269.T", "スズキ"),
    ("7270.T", "SUBARU"),
    ("7202.T", "いすゞ自動車"),
    ("7261.T", "マツダ"),
    ("6902.T", "デンソー"),
    # 電機・精密
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
    # 情報・通信・IT
    ("9984.T", "ソフトバンクグループ"),
    ("9432.T", "日本電信電話"),
    ("9433.T", "KDDI"),
    ("9434.T", "ソフトバンク"),
    ("4689.T", "LINEヤフー"),
    ("6702.T", "富士通"),
    ("6701.T", "NEC"),
    ("9613.T", "NTTデータグループ"),
    ("4307.T", "野村総合研究所"),
    ("4704.T", "トレンドマイクロ"),
    # 製薬・医療
    ("4502.T", "武田薬品工業"),
    ("4503.T", "アステラス製薬"),
    ("4519.T", "中外製薬"),
    ("4523.T", "エーザイ"),
    ("4568.T", "第一三共"),
    ("4507.T", "塩野義製薬"),
    ("4151.T", "協和キリン"),
    ("4543.T", "テルモ"),
    ("7733.T", "オリンパス"),
    # 金融
    ("8306.T", "三菱UFJフィナンシャルG"),
    ("8316.T", "三井住友フィナンシャルG"),
    ("8411.T", "みずほフィナンシャルG"),
    ("8591.T", "オリックス"),
    ("8766.T", "東京海上HD"),
    ("8750.T", "第一生命HD"),
    ("8604.T", "野村ホールディングス"),
    ("8601.T", "大和証券グループ"),
    # 化学・素材
    ("4063.T", "信越化学工業"),
    ("4901.T", "富士フイルムHD"),
    ("4452.T", "花王"),
    ("3407.T", "旭化成"),
    ("4183.T", "三井化学"),
    ("4188.T", "三菱ケミカルG"),
    ("4042.T", "東ソー"),
    ("4021.T", "日産化学"),
    ("3436.T", "SUMCO"),
    # 鉄鋼
    ("5401.T", "日本製鉄"),
    ("5411.T", "JFEホールディングス"),
    ("5108.T", "ブリヂストン"),
    ("5101.T", "横浜ゴム"),
    # 小売
    ("9983.T", "ファーストリテイリング"),
    ("8267.T", "イオン"),
    ("3382.T", "セブン＆アイHD"),
    # 食品・飲料
    ("2914.T", "日本たばこ産業"),
    ("2502.T", "アサヒグループHD"),
    ("2503.T", "キリンHD"),
    ("2801.T", "キッコーマン"),
    ("2802.T", "味の素"),
    # 不動産・建設
    ("8801.T", "三井不動産"),
    ("8802.T", "三菱地所"),
    ("8830.T", "住友不動産"),
    ("1925.T", "大和ハウス工業"),
    ("1928.T", "積水ハウス"),
    ("1801.T", "大成建設"),
    ("1802.T", "大林組"),
    ("1803.T", "清水建設"),
    # 商社
    ("8002.T", "丸紅"),
    ("8058.T", "三菱商事"),
    ("8053.T", "住友商事"),
    ("8031.T", "三井物産"),
    ("8001.T", "伊藤忠商事"),
    # エネルギー
    ("5020.T", "ENEOSホールディングス"),
    ("5019.T", "出光興産"),
    # 重工業・機械
    ("7011.T", "三菱重工業"),
    ("7012.T", "川崎重工業"),
    ("7013.T", "IHI"),
    ("6301.T", "コマツ"),
    ("6326.T", "クボタ"),
    # 輸送・インフラ
    ("9020.T", "東日本旅客鉄道"),
    ("9021.T", "西日本旅客鉄道"),
    ("9022.T", "東海旅客鉄道"),
    ("9101.T", "日本郵船"),
    ("9104.T", "商船三井"),
    ("9107.T", "川崎汽船"),
    # サービス
    ("6098.T", "リクルートHD"),
    ("2413.T", "エムスリー"),
    ("4661.T", "オリエンタルランド"),
    # エンタメ・ゲーム
    ("7974.T", "任天堂"),
    ("9766.T", "コナミグループ"),
    ("7832.T", "バンダイナムコHD"),
    ("6460.T", "セガサミーHD"),
    ("3635.T", "コーエーテクモHD"),
    # その他
    ("4911.T", "資生堂"),
    ("3401.T", "帝人"),
    ("3402.T", "東レ"),
    ("3861.T", "王子HD"),
    ("3659.T", "ネクソン"),
]

# 重複除去
_seen: set[str] = set()
_UNIQUE_STOCKS: list[tuple[str, str]] = []
for _t, _n in _ALL_STOCKS:
    if _t not in _seen:
        _seen.add(_t)
        _UNIQUE_STOCKS.append((_t, _n))


# ── ファイルキャッシュ ─────────────────────────────────────────────────────────

def _load_disk_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        raw = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        now = time.time()
        return {k: v for k, v in raw.items() if v.get("_expires_at", 0) > now}
    except Exception:
        return {}


def _save_disk_cache(cache: dict) -> None:
    try:
        CACHE_FILE.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"[WARN] キャッシュ保存失敗: {e}")


_disk_cache: dict = _load_disk_cache()
print(f"[INFO] キャッシュ読込: {len(_disk_cache)}件")


# ── バッチ管理 ─────────────────────────────────────────────────────────────────

def get_current_batch_info() -> dict:
    total = len(_UNIQUE_STOCKS)
    num_batches = max(1, total // BATCH_SIZE)
    epoch = date(2024, 1, 1)
    days_since_epoch = (date.today() - epoch).days
    batch_index = (days_since_epoch // BATCH_INTERVAL_DAYS) % num_batches
    start = batch_index * BATCH_SIZE
    end = min(start + BATCH_SIZE, total)
    days_until_next = BATCH_INTERVAL_DAYS - (days_since_epoch % BATCH_INTERVAL_DAYS)
    return {
        "batch_index": batch_index,
        "num_batches": num_batches,
        "total_stocks": total,
        "batch_size": BATCH_SIZE,
        "batch_interval_days": BATCH_INTERVAL_DAYS,
        "next_rotation_in_days": days_until_next,
        "start": start,
        "end": end,
    }


def get_stock_universe() -> list[dict]:
    info = get_current_batch_info()
    batch = _UNIQUE_STOCKS[info["start"]:info["end"]]
    return [{"ticker": t, "name": n} for t, n in batch]


# ── データ取得 ─────────────────────────────────────────────────────────────────

def _safe_float(val) -> float | None:
    try:
        v = float(val)
        return None if (np.isnan(v) or np.isinf(v)) else v
    except (TypeError, ValueError):
        return None


def _fetch_single(ticker: str, name: str) -> dict | None:
    """
    1銘柄分の価格・財務指標を ticker.info から取得する。
    curl_cffi セッションが Chrome の User-Agent / TLS フィンガープリントを自動設定する。
    """
    try:
        stock = yf.Ticker(ticker, session=_curl_session)
        info = stock.info
        if not info or len(info) < 5:
            print(f"[WARN] {ticker}: 空レスポンス")
            return None

        def pct(key):
            v = _safe_float(info.get(key))
            return round(v * 100, 2) if v is not None else None

        # 52週モメンタムを履歴から計算
        momentum_52w = None
        price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
        try:
            hist = stock.history(period="1y")
            if len(hist) > 10 and price:
                year_ago = float(hist["Close"].iloc[0])
                if year_ago > 0:
                    momentum_52w = round((price - year_ago) / year_ago * 100, 1)
        except Exception:
            pass

        return {
            "ticker": ticker,
            "name": name,
            "sector": info.get("sector") or info.get("industry") or "その他",
            "price": price,
            "market_cap": _safe_float(info.get("marketCap")),
            "per": _safe_float(info.get("trailingPE") or info.get("forwardPE")),
            "pbr": _safe_float(info.get("priceToBook")),
            "roe": pct("returnOnEquity"),
            "revenue_growth_yoy": pct("revenueGrowth"),
            "operating_margin": pct("operatingMargins"),
            "momentum_52w": momentum_52w,
            "dividend_yield": pct("dividendYield"),
        }
    except Exception as e:
        if "429" in str(e) or "Expecting value" in str(e):
            print(f"[429] {ticker}: レート制限（スキップ）")
        else:
            print(f"[ERROR] {ticker}: {e}")
        return None


def fetch_all_metrics(universe: list[dict]) -> list[dict]:
    """バッチ全銘柄を1件ずつランダムインターバルで取得して返す。"""
    tickers = [s["ticker"] for s in universe]
    names = {s["ticker"]: s["name"] for s in universe}

    to_fetch = [t for t in tickers if t not in _disk_cache]
    results: list[dict] = [_disk_cache[t] for t in tickers if t in _disk_cache]

    if not to_fetch:
        print(f"[INFO] 全{len(tickers)}件キャッシュ済み")
        return results

    print(f"[INFO] {len(results)}件キャッシュ済み / {len(to_fetch)}件を新規取得")
    expires_at = time.time() + CACHE_TTL

    for i, ticker in enumerate(to_fetch):
        if i > 0:
            wait = random.uniform(2, 5)
            print(f"[WAIT] {wait:.1f}秒待機...")
            time.sleep(wait)

        entry = _fetch_single(ticker, names[ticker])
        if entry is None:
            continue

        entry["_expires_at"] = expires_at
        _disk_cache[ticker] = entry
        results.append(entry)
        print(f"[OK] {ticker} {names[ticker]}: ¥{entry.get('price', 'N/A')}")

    _save_disk_cache(_disk_cache)
    return results
