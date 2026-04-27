import { useState } from 'react';
import Sidebar from './components/Sidebar.jsx';
import IngestionPanel from './components/IngestionPanel.jsx';
import HypothesisPanel from './components/HypothesisPanel.jsx';
import KnowledgeGraph from './components/KnowledgeGraph.jsx';
import EpisodeLog from './components/EpisodeLog.jsx';

function timeNow() {
  return new Date().toTimeString().slice(0, 8);
}

export default function App() {
  const [active, setActive] = useState('reasoning');
  const [chunks, setChunks] = useState(0);
  const [graphNodes, setGraphNodes] = useState([]);
  const [episodes, setEpisodes] = useState([]);
  const [loopRunning, setLoopRunning] = useState(false);
  const [cycleCount, setCycleCount] = useState(0);

  const onIngest = ({ source, chunks: c }) => {
    setChunks(prev => prev + c);
    setEpisodes(prev => [
      { time: timeNow(), actor: 'Ingestion', verb: 'stored', target: source, detail: `${c} chunks · embedded`, cycle: '—' },
      ...prev,
    ]);
  };

  const onResult = (r) => {
    const cycle = r.cycle;
    setCycleCount(prev => Math.max(prev, parseInt(cycle) || 0));
    setEpisodes(prev => [
      { time: timeNow(), actor: 'Critic', verb: 'scored', target: r.id, detail: `verdict ${r.verdict} · conf ${r.score.toFixed(2)}`, cycle },
      { time: timeNow(), actor: 'Explorer', verb: 'proposed', target: r.id, detail: `topic: ${r.topic}`, cycle },
      ...prev,
    ]);
    if (r.verdict === 'ACCEPTED') {
      const id = 'n' + Math.random().toString(36).slice(2, 5);
      const glyph = r.statement.match(/[A-Z]/)?.[0] || '⊢';
      setGraphNodes(prev => [...prev, { id, kind: 'claim', glyph, label: r.statement.slice(0, 40), fresh: true }]);
      setEpisodes(prev => [
        { time: timeNow(), actor: 'Updater', verb: 'wrote node to', target: 'graph', detail: '+1 claim', cycle },
        ...prev,
      ]);
    }
  };

  return (
    <div className="app">
      <Sidebar
        active={active}
        onNav={setActive}
        counts={{ chunks, nodes: graphNodes.length, episodes: episodes.length }}
      />
      <div className="shell-main">
        <div className="topbar">
          <div className="topbar-title">
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--fg-3)', letterSpacing: '.14em', textTransform: 'uppercase' }}>
              Workspace /
            </span>
            <span>Reasoning</span>
          </div>
          <div className="topbar-meta">
            <span>cycles · {String(cycleCount).padStart(2, '0')}</span>
            <span>chunks · {chunks}</span>
            <span className="live">{loopRunning ? 'loop running' : 'idle'}</span>
          </div>
        </div>
        <div className="workspace">
          <IngestionPanel onIngest={onIngest} />
          <EpisodeLog episodes={episodes.slice(0, 8)} />
          <div className="span2">
            <HypothesisPanel onResult={onResult} onLoopState={setLoopRunning} />
          </div>
          <div className="span2">
            <KnowledgeGraph extraNodes={graphNodes} />
          </div>
        </div>
      </div>
    </div>
  );
}
