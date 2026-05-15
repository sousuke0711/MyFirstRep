from .data_fetcher import fetch_all_metrics, get_stock_universe


def _score_stock(metrics: dict) -> tuple[float, dict]:
    breakdown = {}

    # 成長性 (25点)
    rev = metrics.get("revenue_growth_yoy")
    if rev is None:       g = 12.5
    elif rev >= 20:       g = 25
    elif rev >= 10:       g = 18
    elif rev >= 0:        g = 10
    else:                 g = 2
    breakdown["revenue_growth"] = round(g, 1)

    # 収益性 (20点)
    margin = metrics.get("operating_margin")
    if margin is None:    m = 10
    elif margin >= 20:    m = 20
    elif margin >= 10:    m = 15
    elif margin >= 5:     m = 8
    else:                 m = 2
    breakdown["operating_margin"] = round(m, 1)

    # PER割安度 (20点)
    per = metrics.get("per")
    if per is None or per <= 0:  p = 10
    elif per < 10:        p = 20
    elif per < 15:        p = 17
    elif per < 20:        p = 13
    elif per < 30:        p = 8
    else:                 p = 3
    breakdown["per"] = round(p, 1)

    # PBR (10点)
    pbr = metrics.get("pbr")
    if pbr is None or pbr <= 0: pb = 5
    elif pbr < 1:         pb = 10
    elif pbr < 1.5:       pb = 8
    elif pbr < 2.5:       pb = 5
    else:                 pb = 2
    breakdown["pbr"] = round(pb, 1)

    # ROE (15点)
    roe = metrics.get("roe")
    if roe is None:       r = 7.5
    elif roe >= 20:       r = 15
    elif roe >= 15:       r = 12
    elif roe >= 10:       r = 8
    elif roe >= 0:        r = 4
    else:                 r = 0
    breakdown["roe"] = round(r, 1)

    # モメンタム (10点)
    mom = metrics.get("momentum_52w")
    if mom is None:       mo = 5
    elif mom >= 30:       mo = 10
    elif mom >= 10:       mo = 8
    elif mom >= 0:        mo = 5
    elif mom >= -10:      mo = 3
    else:                 mo = 1
    breakdown["momentum"] = round(mo, 1)

    total = g + m + p + pb + r + mo
    return round(total, 1), breakdown


def run_screening(min_score: float = 0, sector_filter: str | None = None) -> list[dict]:
    universe = get_stock_universe()
    all_metrics = fetch_all_metrics(universe)

    results = []
    for metrics in all_metrics:
        if sector_filter and sector_filter.lower() not in (metrics.get("sector") or "").lower():
            continue
        score, breakdown = _score_stock(metrics)
        entry = {**metrics, "screening_score": score, "score_breakdown": breakdown}
        # キャッシュ内部フィールドは返さない
        entry.pop("_expires_at", None)
        if score >= min_score:
            results.append(entry)

    results.sort(key=lambda x: x["screening_score"], reverse=True)
    return results
