import React, { useState } from 'react'
import IngestionForm from './components/IngestionForm.jsx'
import HypothesisList from './components/HypothesisList.jsx'
import KnowledgeGraphViewer from './components/KnowledgeGraphViewer.jsx'

export default function App() {
  const [hypotheses, setHypotheses] = useState([])

  const addHypothesis = (entry) => {
    setHypotheses((prev) => [entry, ...prev])
  }

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 900, margin: '0 auto', padding: 24 }}>
      <h1>Enthropy</h1>
      <p>Continual-learning knowledge engine</p>

      <section>
        <h2>Ingest Document</h2>
        <IngestionForm />
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>Generate Hypothesis</h2>
        <HypothesisList onNew={addHypothesis} entries={hypotheses} />
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>Knowledge Graph</h2>
        <KnowledgeGraphViewer />
      </section>
    </div>
  )
}
