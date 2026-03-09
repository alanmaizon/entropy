import React, { useState, useEffect } from 'react'

export default function KnowledgeGraphViewer() {
  const [nodes, setNodes] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchGraph = async () => {
    setLoading(true)
    try {
      const res = await fetch('/graph')
      const data = await res.json()
      setNodes(data.nodes || [])
    } catch (err) {
      console.error('Failed to fetch graph:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGraph()
  }, [])

  return (
    <div>
      <button onClick={fetchGraph} disabled={loading}>
        {loading ? 'Loading…' : 'Refresh Graph'}
      </button>
      {nodes.length === 0 ? (
        <p>No knowledge nodes yet. Ingest documents and generate hypotheses to populate the graph.</p>
      ) : (
        <ul>
          {nodes.map((node, i) => (
            <li key={i}>
              <strong>{node.label}</strong> [{node.node_type}]
              {node.confidence !== undefined && <> — confidence: {node.confidence?.toFixed(2)}</>}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
