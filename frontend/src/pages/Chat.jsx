import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { chatApi } from '../api/client'

const toArray = (str) => str.split(',').map((s) => s.trim()).filter(Boolean)

function renderInline(text) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
      return <strong key={i} className="font-semibold">{part.slice(2, -2)}</strong>
    }
    return part || null
  })
}

function MarkdownText({ content }) {
  const lines = content.split('\n')
  const result = []
  let listItems = []
  let listType = null
  let key = 0

  const flushList = () => {
    if (listItems.length === 0) return
    const items = listItems.map((item, i) => (
      <li key={i} className="leading-relaxed">{renderInline(item)}</li>
    ))
    result.push(
      listType === 'ol'
        ? <ol key={key++} className="list-decimal list-inside space-y-0.5 my-1.5 pl-1">{items}</ol>
        : <ul key={key++} className="list-disc list-inside space-y-0.5 my-1.5 pl-1">{items}</ul>
    )
    listItems = []
    listType = null
  }

  for (const line of lines) {
    if (/^###\s/.test(line)) {
      flushList()
      result.push(<p key={key++} className="font-semibold text-gray-800 mt-3 mb-0.5 text-sm">{renderInline(line.slice(4))}</p>)
    } else if (/^##\s/.test(line)) {
      flushList()
      result.push(<p key={key++} className="font-bold text-gray-900 mt-3 mb-0.5">{renderInline(line.slice(3))}</p>)
    } else if (/^#\s/.test(line)) {
      flushList()
      result.push(<p key={key++} className="font-bold text-gray-900 mt-2 mb-1">{renderInline(line.slice(2))}</p>)
    } else if (/^\d+\.\s/.test(line)) {
      if (listType && listType !== 'ol') flushList()
      listType = 'ol'
      listItems.push(line.replace(/^\d+\.\s+/, ''))
    } else if (/^[-*]\s/.test(line)) {
      if (listType && listType !== 'ul') flushList()
      listType = 'ul'
      listItems.push(line.slice(2))
    } else if (line.trim() === '') {
      flushList()
      result.push(<div key={key++} className="h-2" />)
    } else {
      flushList()
      result.push(<p key={key++} className="leading-relaxed">{renderInline(line)}</p>)
    }
  }
  flushList()
  return <>{result}</>
}

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm HealNet's AI skin health assistant. I answer questions about skin conditions using real experiences shared by our community and a dermatology knowledge graph. Ask me about skin symptoms, conditions like acne, eczema or psoriasis, skincare treatments, or medications.",
    },
  ])
  const [input, setInput] = useState('')
  const [filters, setFilters] = useState({ disease: '', symptoms: '', medications: '' })
  const [showFilters, setShowFilters] = useState(false)
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await chatApi.send(
        input,
        filters.disease || null,
        toArray(filters.symptoms),
        toArray(filters.medications),
      )
      const { answer, sources, graph_used } = res.data
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: answer, sources, graph_used },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto flex flex-col h-full min-h-0">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 mb-3 sm:mb-4 flex-shrink-0">
        <div className="min-w-0">
          <h1 className="text-lg sm:text-xl font-bold text-gray-900">HealNet AI</h1>
          <p className="text-xs text-gray-400 leading-relaxed">
            Skin health answers from community experiences + dermatology knowledge
          </p>
        </div>
        <button
          onClick={() => setShowFilters((f) => !f)}
          className="text-sm text-teal-600 hover:underline self-start sm:self-auto flex-shrink-0"
        >
          {showFilters ? 'Hide filters' : 'Context filters'}
        </button>
      </div>

      {showFilters && (
        <div className="bg-teal-50 border border-teal-100 rounded-xl p-3 sm:p-4 mb-3 sm:mb-4 grid grid-cols-1 sm:grid-cols-3 gap-3 flex-shrink-0">
          <div>
            <label className="text-xs font-medium text-gray-600 block mb-1">Disease</label>
            <input
              value={filters.disease}
              onChange={(e) => setFilters({ ...filters, disease: e.target.value })}
              className="w-full text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Acne, Psoriasis…"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 block mb-1">Symptoms</label>
            <input
              value={filters.symptoms}
              onChange={(e) => setFilters({ ...filters, symptoms: e.target.value })}
              className="w-full text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Itching, Rash, Redness…"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 block mb-1">Medications</label>
            <input
              value={filters.medications}
              onChange={(e) => setFilters({ ...filters, medications: e.target.value })}
              className="w-full text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Benzoyl Peroxide…"
            />
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto overscroll-contain space-y-3 sm:space-y-4 pr-0.5 sm:pr-1 min-h-0">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[92%] sm:max-w-[85%] rounded-2xl px-3 py-2.5 sm:px-4 sm:py-3 text-sm break-words ${
                msg.role === 'user'
                  ? 'bg-teal-600 text-white rounded-br-sm'
                  : 'bg-white border border-gray-100 text-gray-800 rounded-bl-sm shadow-sm'
              }`}
            >
              <MarkdownText content={msg.content} />

              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <p className="text-xs font-medium text-gray-400 mb-1.5">
                    Sources from community {msg.graph_used && '· Knowledge graph used'}
                  </p>
                  <div className="space-y-1">
                    {msg.sources.map((s) => (
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
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="mt-3 sm:mt-4 flex gap-2 flex-shrink-0 pb-1">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          placeholder="Ask about skin conditions, symptoms…"
          className="flex-1 min-w-0 border border-gray-200 rounded-xl px-3 sm:px-4 py-2.5 sm:py-3 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-teal-600 hover:bg-teal-700 text-white px-4 sm:px-5 py-2.5 sm:py-3 rounded-xl transition-colors disabled:opacity-60 flex-shrink-0"
          aria-label="Send message"
        >
          →
        </button>
      </form>

      <p className="text-center text-xs text-gray-300 mt-1.5 sm:mt-2 flex-shrink-0 px-1">
        Not a substitute for professional dermatological advice. Always consult a licensed dermatologist.
      </p>
    </div>
  )
}
