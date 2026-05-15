import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import StockCard from './components/StockCard';
import StockTable from './components/StockTable';

const API = '/api';

const Spinner = () => (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', padding: '60px', color: '#64748b' }}>
    <div style={{
      width: '24px', height: '24px',
      border: '3px solid #334155',
      borderTop: '3px solid #3b82f6',
      borderRadius: '50%',
      animation: 'spin 0.8s linear infinite',
    }} />
    <span>データ取得中...</span>
    <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
  </div>
);

export default function App() {
  const [stocks, setStocks] = useState([]);
  const [batchInfo, setBatchInfo] = useState(null);
  const [aiAnalyses, setAiAnalyses] = useState({});
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aiError, setAiError] = useState(null);
  const [viewMode, setViewMode] = useState('card'); // 'card' | 'table'
  const [minScore, setMinScore] = useState(0);
  const [topN, setTopN] = useState(10);
  const [aiRan, setAiRan] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchStocks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API}/stocks`, { params: { min_score: minScore, limit: 50 } });
      setStocks(res.data.stocks || []);
      setBatchInfo(res.data.batch_info || null);
      setLastUpdated(new Date(res.data.generated_at));
    } catch (e) {
      setError('銘柄データの取得に失敗しました。バックエンドが起動しているか確認してください。');
    } finally {
      setLoading(false);
    }
  }, [minScore]);

  const runAIAnalysis = async () => {
    setAiLoading(true);
    setAiError(null);
    try {
      const res = await axios.post(`${API}/analyze`, null, { params: { top_n: topN } });
      const map = {};
      (res.data.analyses || []).forEach(a => { map[a.ticker] = a; });
      setAiAnalyses(map);
      setAiRan(true);
    } catch (e) {
      const msg = e.response?.data?.detail || 'AI分析に失敗しました';
      setAiError(msg);
    } finally {
      setAiLoading(false);
    }
  };

  useEffect(() => { fetchStocks(); }, [fetchStocks]);

  const displayStocks = stocks.slice(0, topN);

  return (
    <div style={{ minHeight: '100vh', background: '#0f172a' }}>
      {/* ヘッダー */}
      <header style={{
        background: '#1e293b',
        borderBottom: '1px solid #334155',
        padding: '16px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div>
          <h1 style={{ fontSize: '20px', fontWeight: 800, color: '#f1f5f9' }}>
            東証プライム 銘柄スクリーナー
          </h1>
          <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
            ファンダメンタルズ分析 + Claude AI スコアリング
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {lastUpdated && (
            <span style={{ fontSize: '11px', color: '#64748b' }}>
              更新: {lastUpdated.toLocaleTimeString('ja-JP')}
            </span>
          )}
          <button
            onClick={fetchStocks}
            disabled={loading}
            style={btnStyle('#334155', '#e2e8f0')}
          >
            {loading ? '更新中...' : '再取得'}
          </button>
        </div>
      </header>

      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>
        {/* コントロールパネル */}
        <div style={{
          background: '#1e293b',
          border: '1px solid #334155',
          borderRadius: '12px',
          padding: '20px',
          marginBottom: '24px',
          display: 'flex',
          gap: '20px',
          flexWrap: 'wrap',
          alignItems: 'flex-end',
        }}>
          <div>
            <label style={labelStyle}>最低スコア</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="range" min={0} max={90} step={5} value={minScore}
                onChange={e => setMinScore(Number(e.target.value))}
                style={{ width: '140px', accentColor: '#3b82f6' }}
              />
              <span style={{ color: '#f1f5f9', fontWeight: 700, minWidth: '35px' }}>{minScore}点</span>
            </div>
          </div>

          <div>
            <label style={labelStyle}>表示件数 / AI分析対象</label>
            <div style={{ display: 'flex', gap: '6px' }}>
              {[5, 10, 20, 30].map(n => (
                <button
                  key={n}
                  onClick={() => setTopN(n)}
                  style={btnStyle(topN === n ? '#3b82f6' : '#0f172a', topN === n ? '#fff' : '#94a3b8')}
                >
                  {n}件
                </button>
              ))}
            </div>
          </div>

          <div>
            <label style={labelStyle}>表示形式</label>
            <div style={{ display: 'flex', gap: '6px' }}>
              {[['card', 'カード'], ['table', 'テーブル']].map(([mode, label]) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  style={btnStyle(viewMode === mode ? '#3b82f6' : '#0f172a', viewMode === mode ? '#fff' : '#94a3b8')}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginLeft: 'auto' }}>
            <label style={labelStyle}>Claude AI 分析</label>
            <button
              onClick={runAIAnalysis}
              disabled={aiLoading || loading}
              style={{
                ...btnStyle('#8b5cf6', '#fff'),
                padding: '8px 20px',
                fontSize: '14px',
                fontWeight: 700,
                opacity: (aiLoading || loading) ? 0.5 : 1,
              }}
            >
              {aiLoading ? 'AI分析中...' : `上位${topN}件をAI分析`}
            </button>
          </div>
        </div>

        {/* バッチ情報バナー */}
        {batchInfo && (
          <div style={{
            background: '#0f2027',
            border: '1px solid #334155',
            borderRadius: '10px',
            padding: '12px 18px',
            marginBottom: '20px',
            display: 'flex',
            gap: '24px',
            flexWrap: 'wrap',
            alignItems: 'center',
            fontSize: '13px',
            color: '#94a3b8',
          }}>
            <span style={{ color: '#38bdf8', fontWeight: 700 }}>本日のスクリーニングバッチ</span>
            <span>バッチ <b style={{ color: '#f1f5f9' }}>{batchInfo.batch_index + 1}</b> / {batchInfo.num_batches}</span>
            <span>対象 <b style={{ color: '#f1f5f9' }}>{batchInfo.batch_size}社</b>（全{batchInfo.total_stocks}社プール）</span>
            <span>次の入れ替えまで <b style={{ color: '#f59e0b' }}>{batchInfo.next_rotation_in_days}日</b></span>
            <span style={{ color: '#64748b', fontSize: '11px' }}>※ {batchInfo.batch_interval_days || 2}日ごとに自動ローテーション</span>
          </div>
        )}

        {/* エラー表示 */}
        {(error || aiError) && (
          <div style={{
            background: '#7f1d1d',
            border: '1px solid #ef4444',
            borderRadius: '8px',
            padding: '12px 16px',
            marginBottom: '20px',
            color: '#fca5a5',
            fontSize: '13px',
          }}>
            {error || aiError}
          </div>
        )}

        {/* AI分析完了バナー */}
        {aiRan && !aiLoading && Object.keys(aiAnalyses).length > 0 && (
          <div style={{
            background: '#1e1b4b',
            border: '1px solid #8b5cf6',
            borderRadius: '8px',
            padding: '10px 16px',
            marginBottom: '20px',
            color: '#a78bfa',
            fontSize: '13px',
          }}>
            Claude AI による分析が完了しました。各カードに投資テーマとリスクを表示しています。
          </div>
        )}

        {/* サマリー */}
        {!loading && stocks.length > 0 && (
          <div style={{
            display: 'flex',
            gap: '16px',
            marginBottom: '24px',
            flexWrap: 'wrap',
          }}>
            {[
              { label: '対象銘柄数', value: `${stocks.length}社`, color: '#3b82f6' },
              { label: '平均スコア', value: `${(stocks.reduce((a, s) => a + s.screening_score, 0) / stocks.length).toFixed(1)}点`, color: '#f59e0b' },
              { label: '最高スコア', value: `${stocks[0]?.screening_score}点`, color: '#22c55e' },
              { label: 'AI分析済', value: `${Object.keys(aiAnalyses).length}社`, color: '#8b5cf6' },
            ].map(({ label, value, color }) => (
              <div key={label} style={{
                background: '#1e293b',
                border: `1px solid ${color}44`,
                borderRadius: '10px',
                padding: '14px 20px',
                minWidth: '140px',
              }}>
                <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '4px' }}>{label}</div>
                <div style={{ fontSize: '22px', fontWeight: 800, color }}>{value}</div>
              </div>
            ))}
          </div>
        )}

        {/* コンテンツ */}
        {loading ? (
          <Spinner />
        ) : viewMode === 'card' ? (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
            gap: '20px',
          }}>
            {displayStocks.map((stock, i) => (
              <StockCard
                key={stock.ticker}
                stock={stock}
                rank={i + 1}
                aiAnalysis={aiAnalyses[stock.ticker] || null}
              />
            ))}
          </div>
        ) : (
          <div style={{
            background: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '12px',
            overflow: 'hidden',
          }}>
            <StockTable stocks={displayStocks} />
          </div>
        )}

        {!loading && stocks.length === 0 && !error && (
          <div style={{ textAlign: 'center', color: '#64748b', padding: '60px' }}>
            条件に合う銘柄が見つかりませんでした。最低スコアを下げてみてください。
          </div>
        )}
      </main>
    </div>
  );
}

const btnStyle = (bg, color) => ({
  background: bg,
  color,
  border: '1px solid #334155',
  borderRadius: '8px',
  padding: '6px 14px',
  fontSize: '13px',
  cursor: 'pointer',
  fontFamily: 'inherit',
  transition: 'opacity 0.15s',
});

const labelStyle = {
  display: 'block',
  fontSize: '11px',
  color: '#64748b',
  marginBottom: '6px',
  fontWeight: 600,
};
