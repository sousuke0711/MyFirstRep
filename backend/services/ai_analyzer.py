import anthropic
import os
import json
import re
from datetime import date

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096
CHUNK_SIZE = 25  # 1リクエストあたりの最大銘柄数


def analyze_stocks_with_claude(stocks: list[dict]) -> list[dict]:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    today = date.today().strftime("%Y年%m月%d日")

    # 25件ずつチャンク分割してリクエスト
    all_analyses: list[dict] = []
    chunks = [stocks[i:i + CHUNK_SIZE] for i in range(0, len(stocks), CHUNK_SIZE)]

    for chunk_idx, chunk in enumerate(chunks):
        print(f"[AI] チャンク {chunk_idx + 1}/{len(chunks)} ({len(chunk)}銘柄) を分析中...")
        analyses = _analyze_chunk(client, chunk, today)
        all_analyses.extend(analyses)

    # upside_rating 降順でソート
    all_analyses.sort(key=lambda x: x.get("upside_rating", 0), reverse=True)
    return all_analyses


def _analyze_chunk(client: anthropic.Anthropic, stocks: list[dict], today: str) -> list[dict]:
    stocks_text = "\n".join(_format_stock(s) for s in stocks)

    prompt = f"""あなたは東京証券取引所の上場企業を専門とする株式アナリストです。
{today}時点で以下の東証プライム銘柄について、ファンダメンタルズ分析の観点から評価してください。

【対象銘柄と財務指標】
{stocks_text}

以下のJSON形式のみで返してください。前置きや後書きは不要です。

{{
  "analyses": [
    {{
      "ticker": "銘柄コード（例: 7203.T）",
      "name": "銘柄名",
      "investment_thesis": "投資テーマと値上がり期待理由（100〜150字）",
      "risks": "主なリスク要因（50〜80字）",
      "upside_rating": 評価点数（1〜5の整数、5が最も期待大）,
      "summary": "一言まとめ（30字以内）"
    }}
  ]
}}

評価基準:
- 5点: 強い買い推奨。複数の強い上昇材料あり
- 4点: 買い推奨。ファンダメンタルズ良好
- 3点: 中立。様子見
- 2点: やや売り。課題あり
- 1点: 売り推奨。リスクが大きい"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    return _extract_analyses(raw)


def _extract_analyses(raw: str) -> list[dict]:
    """LLMの出力からJSON部分を確実に抽出する。"""

    # 1. コードブロック除去
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    # 2. 正規表現で最外側の { ... } を抽出
    match = re.search(r'\{[\s\S]*\}', raw)
    if not match:
        raise ValueError(f"JSONオブジェクトが見つかりません: {raw[:200]}")
    raw = match.group(0)

    data = json.loads(raw)
    return data.get("analyses", [])


def _format_stock(s: dict) -> str:
    return (
        f"- {s['name']} ({s['ticker']}): "
        f"セクター={s.get('sector', '不明')}, "
        f"株価={s.get('price', 'N/A')}円, "
        f"PER={s.get('per', 'N/A')}, "
        f"PBR={s.get('pbr', 'N/A')}, "
        f"ROE={_fmt(s.get('roe'))}%, "
        f"売上成長率={_fmt(s.get('revenue_growth_yoy'))}%, "
        f"営業利益率={_fmt(s.get('operating_margin'))}%, "
        f"52週モメンタム={_fmt(s.get('momentum_52w'))}%, "
        f"スコア={s.get('screening_score', 'N/A')}"
    )


def _fmt(val) -> str:
    return f"{val:.1f}" if val is not None else "N/A"
