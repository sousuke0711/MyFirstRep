from .data_fetcher import fetch_stock_metrics, get_stock_universe
import time


def _score_stock(metrics: dict) -> tuple[float, dict]:
    """
    各指標にスコアを付与して合計100点で評価する。
    値が取得できない場合は中央値（50点）を付与する。
    """
    breakdown = {}

    # --- 成長性スコア (25点) ---
    rev = metrics.get("revenue_growth_yoy")
    if rev is None:
        g_score = 12.5
    elif rev >= 20:
        g_score = 25
    elif rev >= 10:
        g_score = 18
    elif rev >= 0:
        g_score = 10
    else:
        g_score = 2
    breakdown["revenue_growth"] = round(g_score, 1)

    # --- 収益性スコア (20点) ---
    margin = metrics.get("operating_margin")
    if margin is None:
        m_score = 10
    elif margin >= 20:
        m_score = 20
    elif margin >= 10:
        m_score = 15
    elif margin >= 5:
        m_score = 8
    else:
        m_score = 2
    breakdown["operating_margin"] = round(m_score, 1)

    # --- PERスコア (20点) 低いほど割安 ---
    per = metrics.get("per")
    if per is None or per <= 0:
        p_score = 10
    elif per < 10:
        p_score = 20
    elif per < 15:
        p_score = 17
    elif per < 20:
        p_score = 13
    elif per < 30:
        p_score = 8
    else:
        p_score = 3
    breakdown["per"] = round(p_score, 1)

    # --- PBRスコア (10点) ---
    pbr = metrics.get("pbr")
    if pbr is None or pbr <= 0:
        pb_score = 5
    elif pbr < 1:
        pb_score = 10
    elif pbr < 1.5:
        pb_score = 8
    elif pbr < 2.5:
        pb_score = 5
    else:
        pb_score = 2
    breakdown["pbr"] = round(pb_score, 1)

    # --- ROEスコア (15点) ---
    roe = metrics.get("roe")
    if roe is None:
        r_score = 7.5
    elif roe >= 20:
        r_score = 15
    elif roe >= 15:
        r_score = 12
    elif roe >= 10:
        r_score = 8
    elif roe >= 0:
        r_score = 4
    else:
        r_score = 0
    breakdown["roe"] = round(r_score, 1)

    # --- モメンタムスコア (10点) ---
    mom = metrics.get("momentum_52w")
    if mom is None:
        mo_score = 5
    elif mom >= 30:
        mo_score = 10
    elif mom >= 10:
        mo_score = 8
    elif mom >= 0:
        mo_score = 5
    elif mom >= -10:
        mo_score = 3
    else:
        mo_score = 1
    breakdown["momentum"] = round(mo_score, 1)

    total = g_score + m_score + p_score + pb_score + r_score + mo_score
    return round(total, 1), breakdown


def run_screening(min_score: float = 0, sector_filter: str | None = None) -> list[dict]:
    universe = get_stock_universe()
    results = []

    # 完全順次実行 + 2秒間隔で 429 を回避
    # キャッシュ済みの銘柄はネットワーク不使用なので間隔不要
    for i, s in enumerate(universe):
        if i > 0:
            time.sleep(2)
        metrics = fetch_stock_metrics(s["ticker"], s["name"])
        if metrics is None:
            continue

        if sector_filter and sector_filter.lower() not in (metrics.get("sector") or "").lower():
            continue

        score, breakdown = _score_stock(metrics)
        metrics["screening_score"] = score
        metrics["score_breakdown"] = breakdown

        if score >= min_score:
            results.append(metrics)

    results.sort(key=lambda x: x["screening_score"], reverse=True)
    return results
