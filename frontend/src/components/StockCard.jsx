import ScoreBar from './ScoreBar';

const fmt = (v, suffix = '') => v != null ? `${Number(v).toFixed(1)}${suffix}` : 'N/A';
const fmtPrice = (v) => v != null ? `¥${Number(v).toLocaleString()}` : 'N/A';

const scoreColor = (score) => {
  if (score >= 70) return '#22c55e';
  if (score >= 50) return '#f59e0b';
  return '#ef4444';
};

const StockCard = ({ stock, rank, aiAnalysis }) => {
  const breakdown = stock.score_breakdown || {};

  return (
    <div style={{
      background: '#1e293b',
      border: '1px solid #334155',
      borderRadius: '12px',
      padding: '20px',
      position: 'relative',
      transition: 'border-color 0.2s',
    }}
      onMouseEnter={e => e.currentTarget.style.borderColor = '#3b82f6'}
      onMouseLeave={e => e.currentTarget.style.borderColor = '#334155'}
    >
      {/* ランクバッジ */}
      <div style={{
        position: 'absolute',
        top: '-10px',
        left: '16px',
        background: rank <= 3 ? '#f59e0b' : '#3b82f6',
        color: '#fff',
        borderRadius: '99px',
        padding: '2px 10px',
        fontSize: '12px',
        fontWeight: 700,
      }}>
        #{rank}
      </div>

      {/* ヘッダー */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
        <div>
          <div style={{ fontSize: '16px', fontWeight: 700, color: '#f1f5f9', marginBottom: '2px' }}>
            {stock.name}
          </div>
          <div style={{ fontSize: '12px', color: '#64748b' }}>{stock.ticker} · {stock.sector}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{
            fontSize: '24px',
            fontWeight: 800,
            color: scoreColor(stock.screening_score),
          }}>
            {stock.screening_score}
          </div>
          <div style={{ fontSize: '10px', color: '#64748b' }}>/ 100点</div>
        </div>
      </div>

      {/* 主要指標 */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '10px',
        marginBottom: '14px',
      }}>
        {[
          { label: '株価', value: fmtPrice(stock.price) },
          { label: 'PER', value: fmt(stock.per, '倍') },
          { label: 'PBR', value: fmt(stock.pbr, '倍') },
          { label: 'ROE', value: fmt(stock.roe, '%') },
          { label: '売上成長', value: fmt(stock.revenue_growth_yoy, '%') },
          { label: '52週騰落', value: fmt(stock.momentum_52w, '%') },
        ].map(({ label, value }) => (
          <div key={label} style={{
            background: '#0f172a',
            borderRadius: '8px',
            padding: '8px 10px',
          }}>
            <div style={{ fontSize: '10px', color: '#64748b', marginBottom: '2px' }}>{label}</div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0' }}>{value}</div>
          </div>
        ))}
      </div>

      {/* スコア内訳 */}
      <div style={{ marginBottom: aiAnalysis ? '14px' : 0 }}>
        <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '8px', fontWeight: 600 }}>スコア内訳</div>
        <ScoreBar label="売上成長率" score={breakdown.revenue_growth ?? 0} maxScore={25} color="#3b82f6" />
        <ScoreBar label="営業利益率" score={breakdown.operating_margin ?? 0} maxScore={20} color="#8b5cf6" />
        <ScoreBar label="PER（割安度）" score={breakdown.per ?? 0} maxScore={20} color="#06b6d4" />
        <ScoreBar label="ROE" score={breakdown.roe ?? 0} maxScore={15} color="#22c55e" />
        <ScoreBar label="モメンタム" score={breakdown.momentum ?? 0} maxScore={10} color="#f59e0b" />
        <ScoreBar label="PBR" score={breakdown.pbr ?? 0} maxScore={10} color="#ec4899" />
      </div>

      {/* AI分析 */}
      {aiAnalysis && (
        <div style={{
          background: '#0f172a',
          borderRadius: '8px',
          padding: '12px',
          borderLeft: '3px solid #8b5cf6',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', color: '#8b5cf6', fontWeight: 700 }}>Claude AI 分析</span>
            <span style={{ fontSize: '11px' }}>
              {'★'.repeat(aiAnalysis.upside_rating)}{'☆'.repeat(5 - aiAnalysis.upside_rating)}
            </span>
          </div>
          <div style={{ fontSize: '12px', color: '#cbd5e1', lineHeight: 1.6, marginBottom: '6px' }}>
            {aiAnalysis.investment_thesis}
          </div>
          <div style={{ fontSize: '11px', color: '#f87171' }}>
            リスク: {aiAnalysis.risks}
          </div>
        </div>
      )}
    </div>
  );
};

export default StockCard;
