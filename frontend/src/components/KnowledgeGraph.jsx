import { useState, useEffect, useMemo } from 'react';
import { Icon, Button } from './primitives.jsx';

function nodeKind(nodeType) {
  if (!nodeType) return 'entity';
  const t = nodeType.toLowerCase();
  if (t === 'claim' || t === 'hypothesis') return 'claim';
  if (t === 'evidence' || t === 'source') return 'evidence';
  return 'entity';
}

function nodeGlyph(label) {
  return label?.match(/[A-Za-z]/)?.[0]?.toUpperCase() ?? '⊢';
}

export default function KnowledgeGraph({ extraNodes }) {
  const DEMO_NODES = [
    { id: 'n0', kind: 'entity',   glyph: 'M', label: 'mass' },
    { id: 'n1', kind: 'entity',   glyph: 'G', label: 'general relativity' },
    { id: 'n2', kind: 'claim',    glyph: '⊢', label: 'spacetime curvature' },
    { id: 'n3', kind: 'evidence', glyph: 'e', label: 'Eddington 1919' },
  ];

  const [apiNodes, setApiNodes] = useState(
    import.meta.env.VITE_DEMO === 'true' ? DEMO_NODES : []
  );
  const [loading, setLoading] = useState(false);

  const fetchGraph = async () => {
    if (import.meta.env.VITE_DEMO === 'true') return;
    setLoading(true);
    try {
      const res = await fetch('/graph');
      const data = await res.json();
      setApiNodes(
        (data.nodes || []).map((n, i) => ({
          id: n.id ?? `api-${i}`,
          kind: nodeKind(n.node_type),
          glyph: nodeGlyph(n.label),
          label: n.label ?? '',
        }))
      );
    } catch {
      // graph fetch is best-effort
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchGraph(); }, []);

  const allNodes = useMemo(() => {
    const seen = new Set(apiNodes.map(n => n.id));
    return [
      ...apiNodes,
      ...(extraNodes || []).filter(n => !seen.has(n.id)),
    ];
  }, [apiNodes, extraNodes]);

  const placed = useMemo(() => {
    return allNodes.map((n, i) => {
      const cols = 4;
      const col = i % cols;
      const row = Math.floor(i / cols);
      const x = 14 + col * 22 + (row % 2 ? 8 : 0);
      const y = 18 + row * 28;
      return { ...n, x, y };
    });
  }, [allNodes]);

  const edges = useMemo(() => {
    const e = [];
    for (let i = 0; i < placed.length - 1; i++) {
      if (Math.abs(placed[i].x - placed[i + 1].x) < 30) {
        e.push([placed[i], placed[i + 1]]);
      }
    }
    return e;
  }, [placed]);

  return (
    <div className="panel">
      <div className="panel-head">
        <div className="panel-title"><Icon name="graph" /> Knowledge graph</div>
        <div className="panel-meta" style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <span>GET /graph · {placed.length} nodes</span>
          <Button kind="quiet" size="sm" icon="refresh" onClick={fetchGraph} disabled={loading}>
            {loading ? 'Loading…' : 'Refresh'}
          </Button>
        </div>
      </div>
      <div className="panel-body" style={{ padding: 12 }}>
        <div className="graph-canvas">
          <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
            {edges.map(([a, b], i) => (
              <line key={i} x1={`${a.x}%`} y1={`${a.y}%`} x2={`${b.x}%`} y2={`${b.y}%`}
                stroke={a.kind === 'claim' ? '#c6f24a' : '#9f7aff'} strokeWidth="1" opacity=".4" />
            ))}
          </svg>
          {placed.map(n => (
            <div key={n.id} className={`gnode ${n.kind}${n.fresh ? ' fresh' : ''}`}
              style={{ left: `${n.x}%`, top: `${n.y}%` }}
              title={n.label}>
              {n.glyph}
            </div>
          ))}
          {placed.length === 0 && (
            <div className="empty" style={{ padding: 60 }}>
              No knowledge nodes yet. Ingest documents and generate hypotheses to populate the graph.
            </div>
          )}
          <div className="glegend">
            <div className="lr"><span className="ldot" style={{ borderColor: 'var(--node-entity)' }} />entity</div>
            <div className="lr"><span className="ldot" style={{ borderColor: 'var(--node-claim)' }} />claim</div>
            <div className="lr"><span className="ldot" style={{ borderColor: 'var(--node-evidence)' }} />evidence</div>
          </div>
        </div>
      </div>
    </div>
  );
}
