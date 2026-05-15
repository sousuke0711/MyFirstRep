const fmt = (v, suffix = '') => v != null ? `${Number(v).toFixed(1)}${suffix}` : '-';

const scoreColor = (score) => {
  if (score >= 70) return '#22c55e';
  if (score >= 50) return '#f59e0b';
  return '#ef4444';
};

const StockTable = ({ stocks }) => {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #334155', color: '#64748b', textAlign: 'left' }}>
            {['順位', '銘柄名', 'コード', 'セクター', '株価', 'PER', 'PBR', 'ROE%', '売上成長%', '52週%', 'スコア'].map(h => (
              <th key={h} style={{ padding: '10px 12px', fontWeight: 600, whiteSpace: 'nowrap' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {stocks.map((s, i) => (
            <tr
              key={s.ticker}
              style={{ borderBottom: '1px solid #1e293b', transition: 'background 0.15s' }}
              onMouseEnter={e => e.currentTarget.style.background = '#1e293b'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <td style={{ padding: '10px 12px', color: '#64748b', fontWeight: 700 }}>#{i + 1}</td>
              <td style={{ padding: '10px 12px', fontWeight: 600, color: '#f1f5f9', whiteSpace: 'nowrap' }}>{s.name}</td>
              <td style={{ padding: '10px 12px', color: '#94a3b8' }}>{s.ticker}</td>
              <td style={{ padding: '10px 12px', color: '#94a3b8', whiteSpace: 'nowrap', maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis' }}>{s.sector}</td>
              <td style={{ padding: '10px 12px' }}>{s.price != null ? `¥${Number(s.price).toLocaleString()}` : '-'}</td>
              <td style={{ padding: '10px 12px' }}>{fmt(s.per, '倍')}</td>
              <td style={{ padding: '10px 12px' }}>{fmt(s.pbr, '倍')}</td>
              <td style={{ padding: '10px 12px', color: s.roe >= 15 ? '#22c55e' : '#e2e8f0' }}>{fmt(s.roe, '%')}</td>
              <td style={{ padding: '10px 12px', color: s.revenue_growth_yoy >= 10 ? '#22c55e' : s.revenue_growth_yoy < 0 ? '#ef4444' : '#e2e8f0' }}>
                {fmt(s.revenue_growth_yoy, '%')}
              </td>
              <td style={{ padding: '10px 12px', color: s.momentum_52w >= 0 ? '#22c55e' : '#ef4444' }}>
                {fmt(s.momentum_52w, '%')}
              </td>
              <td style={{ padding: '10px 12px' }}>
                <span style={{
                  background: scoreColor(s.screening_score) + '22',
                  color: scoreColor(s.screening_score),
                  padding: '3px 8px',
                  borderRadius: '6px',
                  fontWeight: 700,
                }}>
                  {s.screening_score}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StockTable;
