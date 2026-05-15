const ScoreBar = ({ label, score, maxScore, color = '#3b82f6' }) => {
  const pct = maxScore > 0 ? Math.min((score / maxScore) * 100, 100) : 0;

  return (
    <div style={{ marginBottom: '6px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '3px', color: '#94a3b8' }}>
        <span>{label}</span>
        <span style={{ color: '#e2e8f0', fontWeight: 600 }}>{score}/{maxScore}</span>
      </div>
      <div style={{ background: '#1e293b', borderRadius: '4px', height: '6px', overflow: 'hidden' }}>
        <div
          style={{
            width: `${pct}%`,
            height: '100%',
            background: color,
            borderRadius: '4px',
            transition: 'width 0.6s ease',
          }}
        />
      </div>
    </div>
  );
};

export default ScoreBar;
