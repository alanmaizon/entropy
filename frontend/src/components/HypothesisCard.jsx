import { VerdictBadge } from './primitives.jsx';

export default function HypothesisCard({ entry, fresh }) {
  return (
    <div className={`hcard${fresh ? ' fresh' : ''}`}>
      <div className="hcard-eyebrow">
        <span>HYPOTHESIS · {entry.id}</span>
        <span>cycle {entry.cycle}</span>
      </div>
      <div className="hcard-statement">{entry.statement}</div>
      <div className="hcard-meta">
        <VerdictBadge verdict={entry.verdict} />
        <span>conf <b>{entry.score.toFixed(2)}</b></span>
        <span>·</span>
        <span>{entry.evidence} evidence chunks</span>
        <span>·</span>
        <span>{entry.topic}</span>
      </div>
      {entry.reasoning && (
        <div className="hcard-reasoning">"{entry.reasoning}"</div>
      )}
    </div>
  );
}
