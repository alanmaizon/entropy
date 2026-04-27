import { Icon } from './primitives.jsx';

export default function EpisodeLog({ episodes }) {
  return (
    <div className="panel">
      <div className="panel-head">
        <div className="panel-title"><Icon name="episode" /> Episodic memory</div>
        <div className="panel-meta">GET /knowledge · {episodes.length} episodes</div>
      </div>
      <div className="panel-body">
        {episodes.length === 0 && (
          <div className="empty">No episodes yet. Run a reasoning cycle to record one.</div>
        )}
        {episodes.map((ep, i) => (
          <div key={i} className="ep-row">
            <span className="ep-time">{ep.time}</span>
            <span className="ep-text">
              <b>{ep.actor}</b> {ep.verb} <span className="term">{ep.target}</span>
              {ep.detail && <> · {ep.detail}</>}
            </span>
            <span className="ep-time">cycle {ep.cycle}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
