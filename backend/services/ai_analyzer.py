import anthropic
import os
import json
from datetime import date


def analyze_stocks_with_claude(stocks: list[dict]) -> list[dict]:
    """
    スクリーニング上位銘柄をClaude APIで分析し、投資候補をランキングする。
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    stock_summaries = []
    for s in stocks:
        summary = (
            f"- {s['name']} ({s['ticker']}): "
            f"セクター={s.get('sector','不明')}, "
            f"株価={s.get('price','N/A')}円, "
            f"PER={s.get('per','N/A')}, "
            f"PBR={s.get('pbr','N/A')}, "
            f"ROE={_fmt(s.get('roe'))}%, "
            f"売上成長率={_fmt(s.get('revenue_growth_yoy'))}%, "
            f"営業利益率={_fmt(s.get('operating_margin'))}%, "
            f"52週モメンタム={_fmt(s.get('momentum_52w'))}%, "
            f"スクリーニングスコア={s.get('screening_score','N/A')}"
        )
        stock_summaries.append(summary)

    stocks_text = "\n".join(stock_summaries)
    today = date.today().strftime("%Y年%m月%d日")

    prompt = f"""あなたは東京証券取引所の上場企業を専門とする株式アナリストです。
{today}時点で以下のスクリーニングを通過した東証プライム銘柄について、
ファンダメンタルズ分析の観点から今後値上がりが期待できる銘柄を評価してください。

【対象銘柄と財務指標】
{stocks_text}

各銘柄について以下のJSON形式で分析結果を返してください。
必ず有効なJSONのみを返し、余分なテキストは含めないでください。

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
- 1点: 売り推奨。リスクが大きい

upside_ratingの高い順に並べて返してください。"""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    # JSON部分を抽出
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    data = json.loads(raw)
    return data.get("analyses", [])


def _fmt(val) -> str:
    if val is None:
        return "N/A"
    return f"{val:.1f}"
