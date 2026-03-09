import React, { useState } from 'react'

export default function IngestionForm() {
  const [text, setText] = useState('')
  const [source, setSource] = useState('')
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setStatus(null)
    try {
      const res = await fetch('/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, source }),
      })
      const data = await res.json()
      if (res.ok) {
        setStatus(`✅ Stored ${data.chunks_stored} chunk(s).`)
        setText('')
        setSource('')
      } else {
        setStatus(`❌ Error: ${data.detail}`)
      }
    } catch (err) {
      setStatus(`❌ Network error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Source label<br />
          <input value={source} onChange={e => setSource(e.target.value)} placeholder="e.g. paper.pdf" style={{ width: '100%' }} />
        </label>
      </div>
      <div style={{ marginTop: 8 }}>
        <label>Document text<br />
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            rows={6}
            style={{ width: '100%' }}
            placeholder="Paste document text here…"
            required
          />
        </label>
      </div>
      <button type="submit" disabled={loading} style={{ marginTop: 8 }}>
        {loading ? 'Ingesting…' : 'Ingest'}
      </button>
      {status && <p>{status}</p>}
    </form>
  )
}
