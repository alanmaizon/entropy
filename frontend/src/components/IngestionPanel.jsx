import { useState } from 'react';
import { Icon, Button, Field } from './primitives.jsx';

export default function IngestionPanel({ onIngest }) {
  const [text, setText] = useState('');
  const [source, setSource] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch('/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, source }),
      });
      const data = await res.json();
      if (res.ok) {
        const chunks = data.chunks_stored ?? Math.max(1, Math.round(text.length / 180));
        onIngest({ source: source || 'untitled', chunks });
        setStatus({ type: 'ok', msg: `✓  Stored ${chunks} chunk${chunks > 1 ? 's' : ''} · indexed` });
        setText('');
        setSource('');
      } else {
        setStatus({ type: 'err', msg: `✗  ${data.detail || 'Ingest failed'}` });
      }
    } catch (err) {
      setStatus({ type: 'err', msg: `✗  Network error: ${err.message}` });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <div className="panel-head">
        <div className="panel-title"><Icon name="ingest" /> Ingest document</div>
        <div className="panel-meta">POST /ingest</div>
      </div>
      <div className="panel-body">
        <form onSubmit={submit} className="col">
          <Field label="Source label">
            <input className="input" value={source} placeholder="e.g. paper.pdf"
              onChange={e => setSource(e.target.value)} />
          </Field>
          <Field label="Document text">
            <textarea className="textarea" value={text}
              placeholder="Paste document text here…"
              onChange={e => setText(e.target.value)} required />
          </Field>
          <div className="row">
            <Button type="submit" disabled={loading} icon="arrow">
              {loading ? 'Ingesting…' : 'Ingest'}
            </Button>
            <span className="spacer" />
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--fg-3)' }}>
              chunk · embed · entities
            </span>
          </div>
          {status && <div className={`status-line ${status.type}`}>{status.msg}</div>}
        </form>
      </div>
    </div>
  );
}
