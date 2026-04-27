import { useState } from 'react';
import { Icon, Button } from './primitives.jsx';
import HypothesisCard from './HypothesisCard.jsx';

const STEPS = [
  { name: 'Observe',  desc: 'Embed topic vector',             dur: '0.12s' },
  { name: 'Memory',   desc: 'Vector search · top_k=5',        dur: '0.34s' },
  { name: 'Generate', desc: 'Explorer proposes hypothesis',   dur: '1.8s'  },
  { name: 'Critique', desc: 'Critic scores against evidence', dur: '1.4s'  },
  { name: 'Update',   desc: 'Write to graph if accepted',     dur: '0.21s' },
];

export default function HypothesisPanel({ onResult, onLoopState }) {
  const [topic, setTopic] = useState('');
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(-1);
  const [error, setError] = useState(null);

  const generate = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;
    setLoading(true);
    setStep(0);
    setError(null);
    onLoopState(true);

    // Animate through loop steps while the real request is in-flight
    let stepIdx = 0;
    const stepTimer = setInterval(() => {
      stepIdx++;
      if (stepIdx < STEPS.length) {
        setStep(stepIdx);
      } else {
        clearInterval(stepTimer);
      }
    }, 700 + Math.random() * 400);

    try {
      const res = await fetch('/hypothesis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });
      clearInterval(stepTimer);
      const data = await res.json();
      if (res.ok) {
        const id = 'h_' + Math.random().toString(36).slice(2, 6);
        const cycle = String(entries.length + 1).padStart(2, '0');
        const result = {
          id,
          cycle,
          topic,
          statement: data.hypothesis?.statement ?? data.statement ?? 'No statement returned',
          verdict: (data.critique?.verdict ?? data.verdict ?? 'UNCERTAIN').toUpperCase(),
          score: data.critique?.score ?? data.score ?? 0.5,
          reasoning: data.critique?.reasoning ?? data.reasoning ?? '',
          evidence: data.evidence_count ?? 3,
        };
        setEntries(prev => [result, ...prev]);
        onResult(result);
        setTopic('');
      } else {
        setError(data.detail || 'Generation failed');
      }
    } catch (err) {
      clearInterval(stepTimer);
      setError(`Network error: ${err.message}`);
    } finally {
      setLoading(false);
      setStep(-1);
      onLoopState(false);
    }
  };

  return (
    <div className="panel">
      <div className="panel-head">
        <div className="panel-title"><Icon name="hypothesis" /> Reasoning loop</div>
        <div className="panel-meta">POST /hypothesis</div>
      </div>
      <div className="panel-body">
        <form onSubmit={generate} className="row" style={{ marginBottom: 14 }}>
          <input className="input" style={{ flex: 1 }} value={topic}
            placeholder="Enter a topic…  e.g. dark matter halos"
            onChange={e => setTopic(e.target.value)} required />
          <Button type="submit" disabled={loading} icon="loop">
            {loading ? 'Reasoning…' : 'Generate'}
          </Button>
        </form>

        {loading && <div className="cursor-bar" />}

        {(loading || step >= 0) && (
          <div style={{ marginBottom: 14 }}>
            {STEPS.map((s, i) => {
              const cls = i < step ? 'done' : i === step ? 'active' : 'idle';
              return (
                <div key={i} className={`loop-step ${cls}`}>
                  <span className="idx">{String(i + 1).padStart(2, '0')}</span>
                  <span className="name">{s.name}</span>
                  <span className="desc">{s.desc}</span>
                  <span className="dur">{i <= step ? s.dur : '—'}</span>
                </div>
              );
            })}
          </div>
        )}

        {error && (
          <div className="status-line err" style={{ marginBottom: 12 }}>✗ {error}</div>
        )}

        {entries.length === 0 && !loading && (
          <div className="empty">No hypotheses yet. Enter a topic to begin reasoning.</div>
        )}

        <div className="col">
          {entries.map((e, i) => (
            <HypothesisCard key={e.id} entry={e} fresh={i === 0} />
          ))}
        </div>
      </div>
    </div>
  );
}
