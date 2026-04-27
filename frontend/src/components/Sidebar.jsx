import { Icon } from './primitives.jsx';

export default function Sidebar({ active, onNav, counts }) {
  const items = [
    { id: 'reasoning', label: 'Reasoning', icon: 'loop' },
    { id: 'memory', label: 'Memory', icon: 'ingest', count: counts.chunks },
    { id: 'graph', label: 'Knowledge Graph', icon: 'graph', count: counts.nodes },
    { id: 'episodes', label: 'Episodes', icon: 'episode', count: counts.episodes },
  ];
  return (
    <aside className="sidebar">
      <div className="sb-brand">
        <div className="glyph">∂</div>
        <div className="word">Entropy</div>
      </div>
      <div className="sb-section">Workspace</div>
      {items.map(it => (
        <div
          key={it.id}
          className={`sb-item${active === it.id ? ' active' : ''}`}
          onClick={() => onNav(it.id)}
        >
          <Icon name={it.icon} />
          <span>{it.label}</span>
          {it.count !== undefined && <span className="count">{it.count}</span>}
        </div>
      ))}
      <div className="sb-section">System</div>
      <div className="sb-item" onClick={() => onNav('settings')}>
        <Icon name="settings" />
        <span>Settings</span>
      </div>
    </aside>
  );
}
