# 東証プライム 銘柄スクリーナー

東証プライム上場企業の決算・財務指標を自動スクリーニングし、Claude AIが値上がり期待銘柄をランキングするアプリです。

## 機能

- **ファンダメンタルズスクリーニング**: PER・PBR・ROE・売上成長率・営業利益率・52週モメンタムを100点満点でスコアリング
- **Claude AI 分析**: 上位N社を Claude Opus AIが深掘り分析し、投資テーマ・リスク・評価点(★1〜5)を提示
- **カード / テーブル 表示切替**: スコア内訳バー付きカードビューと一覧テーブルビュー
- **リアルタイム更新**: ボタン1クリックでyfinanceから最新データを再取得

## スコアリング基準

| 指標 | 配点 | 高評価の条件 |
|------|------|------------|
| 売上成長率 (YoY) | 25点 | 20%以上で満点 |
| 営業利益率 | 20点 | 20%以上で満点 |
| PER（割安度） | 20点 | 10倍未満で満点 |
| ROE | 15点 | 20%以上で満点 |
| 52週モメンタム | 10点 | 30%以上で満点 |
| PBR | 10点 | 1.0未満で満点 |

## セットアップ

### 必要なもの

- Python 3.12+
- Node.js 20+
- Anthropic API キー（AI分析機能を使う場合）

### バックエンド起動

```bash
cd backend
cp .env.example .env
# .env の ANTHROPIC_API_KEY を設定

pip install -r requirements.txt
uvicorn main:app --reload
# → http://localhost:8000
# API ドキュメント: http://localhost:8000/docs
```

### フロントエンド起動

```bash
cd frontend
npm install
npm start
# → http://localhost:3000
```

### Docker Compose で一括起動

```bash
cp backend/.env.example backend/.env
# backend/.env の ANTHROPIC_API_KEY を設定

docker-compose up --build
```

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/api/stocks` | 銘柄一覧（スコア順） |
| GET | `/api/stocks/{ticker}` | 個別銘柄詳細 |
| POST | `/api/analyze?top_n=10` | Claude AI による上位N社の分析 |
| GET | `/api/sectors` | セクター一覧 |

### クエリパラメータ（/api/stocks）

- `min_score`: 最低スコア (0〜100, デフォルト: 0)
- `sector`: セクターフィルタ（部分一致）
- `limit`: 返却件数上限（デフォルト: 50）

## 注意事項

- データは yfinance 経由で取得するため、実際の市場データと若干の乖離がある場合があります
- 本アプリの情報は投資助言ではありません。投資判断は自己責任で行ってください
- API レート制限のため、初回取得には数分かかる場合があります（以降はキャッシュ済み）

## 技術スタック

- **Backend**: FastAPI, yfinance, pandas, Anthropic SDK
- **Frontend**: React 18, Recharts, Axios
- **AI**: Claude Opus (claude-opus-4-7)
