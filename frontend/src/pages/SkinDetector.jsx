import { useState } from 'react'
import { Link } from 'react-router-dom'
import { chatApi } from '../api/client'

function renderInline(text) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith('**') && part.endsWith('**') && part.length > 4
      ? <strong key={i} className="font-semibold">{part.slice(2, -2)}</strong>
      : part || null
  )
}

function MarkdownText({ content }) {
  const lines = content.split('\n')
  const result = []
  let listItems = [], listType = null, key = 0

  const flushList = () => {
    if (!listItems.length) return
    const items = listItems.map((item, i) => <li key={i} className="leading-relaxed">{renderInline(item)}</li>)
    result.push(
      listType === 'ol'
        ? <ol key={key++} className="list-decimal list-inside space-y-0.5 my-1.5 pl-1">{items}</ol>
        : <ul key={key++} className="list-disc list-inside space-y-0.5 my-1.5 pl-1">{items}</ul>
    )
    listItems = []; listType = null
  }

  for (const line of lines) {
    if (/^###\s/.test(line))      { flushList(); result.push(<p key={key++} className="font-semibold text-gray-800 mt-3 mb-0.5 text-sm">{renderInline(line.slice(4))}</p>) }
    else if (/^##\s/.test(line))  { flushList(); result.push(<p key={key++} className="font-bold text-gray-900 mt-3 mb-0.5">{renderInline(line.slice(3))}</p>) }
    else if (/^#\s/.test(line))   { flushList(); result.push(<p key={key++} className="font-bold text-gray-900 mt-2 mb-1">{renderInline(line.slice(2))}</p>) }
    else if (/^\d+\.\s/.test(line)) { if (listType && listType !== 'ol') flushList(); listType = 'ol'; listItems.push(line.replace(/^\d+\.\s+/, '')) }
    else if (/^[-*]\s/.test(line))  { if (listType && listType !== 'ul') flushList(); listType = 'ul'; listItems.push(line.slice(2)) }
    else if (line.trim() === '')    { flushList(); result.push(<div key={key++} className="h-2" />) }
    else                           { flushList(); result.push(<p key={key++} className="leading-relaxed">{renderInline(line)}</p>) }
  }
  flushList()
  return <>{result}</>
}

export default function SkinDetector() {
  const [disease, setDisease] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState('')

  const handleGetInsights = async (e) => {
    e.preventDefault()
    if (!disease.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await chatApi.send(
        `I have been diagnosed with ${disease.trim()}. What should I know about this skin condition — causes, symptoms, treatments, and what have others in the community experienced?`,
        disease.trim(),
        [],
        [],
      )
      setResult(res.data)
    } catch {
      setError('Failed to get insights. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto w-full min-w-0">
      <div className="mb-4 sm:mb-5">
        <h1 className="text-xl sm:text-2xl font-bold text-gray-900">AI Skin Disease Detector</h1>
        <p className="text-sm text-gray-400 mt-1 leading-relaxed">
          Upload your image below — then enter the detected condition to get community insights from DermaCom
        </p>
      </div>

      {/* ── Step 1: HF Space iframe ── */}
      <div className="bg-white rounded-xl sm:rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-4">
        <div className="px-4 sm:px-5 py-3 border-b border-gray-100 flex items-start gap-2">
          <span className="w-2 h-2 rounded-full bg-teal-500 flex-shrink-0 mt-1.5" />
          <span className="text-xs sm:text-sm font-medium text-gray-700 leading-snug">
            Step 1 — Upload your image and get a diagnosis
          </span>
        </div>
        <iframe
          src="https://jamesnixon94-skin-conditions.hf.space"
          title="Skin Disease Detector"
          allow="camera"
          className="w-full border-0 h-[55vh] min-h-[320px] sm:h-[580px] sm:min-h-0"
        />
      </div>

      {/* ── Step 2: Enter detected disease → RAG ── */}
      <div className="bg-white rounded-xl sm:rounded-2xl shadow-sm border border-gray-100 p-4 sm:p-6 mb-4">
        <div className="flex items-start gap-2 mb-4">
          <span className="w-2 h-2 rounded-full bg-teal-500 flex-shrink-0 mt-1.5" />
          <span className="text-xs sm:text-sm font-medium text-gray-700 leading-snug">
            Step 2 — Get DermaCom community insights for the detected condition
          </span>
        </div>

        <form onSubmit={handleGetInsights} className="flex flex-col sm:flex-row gap-2">
          <input
            value={disease}
            onChange={(e) => { setDisease(e.target.value); setResult(null) }}
            placeholder="e.g. Acne, Psoriasis, Eczema…"
            className="flex-1 min-w-0 border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
          <button
            type="submit"
            disabled={loading || !disease.trim()}
            className="w-full sm:w-auto bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium px-5 py-2.5 rounded-lg transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {loading
              ? <><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Loading…</>
              : 'Get Insights →'}
          </button>
        </form>

        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </div>

      {/* ── RAG results ── */}
      {result && (
        <div className="bg-white rounded-xl sm:rounded-2xl shadow-sm border border-gray-100 p-4 sm:p-6 mb-4">
          <div className="flex flex-wrap items-center gap-2 mb-4">
            <span className="text-sm font-semibold text-gray-800 w-full sm:w-auto">
              DermaCom Insights for {disease}
            </span>
            <span className="text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full font-medium">
              {result.mode === 'hybrid' ? 'Community + Knowledge Base' : 'AI Knowledge'}
            </span>
            {result.confidence && (
              <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">
                {result.confidence} confidence
              </span>
            )}
          </div>

          <div className="text-sm text-gray-700 space-y-1">
            <MarkdownText content={result.answer} />
          </div>

          {result.sources?.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-100">
              <p className="text-xs font-medium text-gray-400 mb-2">
                Community posts referenced {result.graph_used && '· Knowledge graph consulted'}
              </p>
              <div className="space-y-1">
                {result.sources.map((s) => (
                  <Link
                    key={s.post_id}
                    to={`/posts/${s.post_id}`}
                    className="block text-xs text-teal-600 hover:underline truncate"
                  >
                    ↗ {s.title}
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <p className="text-center text-xs text-gray-300 mt-2">
        Not a substitute for professional dermatological advice · Always consult a licensed dermatologist
      </p>
    </div>
  )
}
