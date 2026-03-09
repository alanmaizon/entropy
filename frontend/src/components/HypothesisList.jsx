import React, { useState } from 'react'

export default function HypothesisList({ onNew, entries }) {
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleGenerate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/hypothesis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      })
      const data = await res.json()
      if (res.ok) {
        onNew(data)
        setTopic('')
      } else {
        setError(data.detail)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleGenerate}>
        <input
          value={topic}
          onChange={e => setTopic(e.target.value)}
          placeholder="Enter a topic…"
          required
          style={{ width: 300 }}
        />
        <button type="submit" disabled={loading} style={{ marginLeft: 8 }}>
          {loading ? 'Generating…' : 'Generate'}
        </button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <ul style={{ listStyle: 'none', paddingLeft: 0, marginTop: 16 }}>
        {entries.map((entry, i) => (
          <li key={i} style={{ borderBottom: '1px solid #eee', paddingBottom: 12, marginBottom: 12 }}>
            <strong>Hypothesis:</strong> {entry.hypothesis?.statement}
            <br />
            <strong>Verdict:</strong> {entry.critique?.verdict} &nbsp;
            <strong>Score:</strong> {entry.critique?.score?.toFixed(2)}
            <br />
            <em>{entry.critique?.reasoning}</em>
          </li>
        ))}
      </ul>
    </div>
  )
}
