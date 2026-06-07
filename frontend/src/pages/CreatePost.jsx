import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { postsApi } from '../api/client'

export default function CreatePost() {
  const navigate = useNavigate()

  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')

  // analysis state
  const [analysis, setAnalysis] = useState(null)   // null = not yet analyzed
  const [analyzing, setAnalyzing] = useState(false)
  const [posting, setPosting] = useState(false)
  const [error, setError] = useState('')

  /* ── Step 1: send to AI for extraction ── */
  const handleAnalyze = async (e) => {
    e.preventDefault()
    setError('')
    setAnalyzing(true)
    try {
      const res = await postsApi.analyze(title, content)
      setAnalysis(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  /* ── Step 2: submit the post ── */
  const handlePost = async () => {
    setError('')
    setPosting(true)
    try {
      const res = await postsApi.create({
        title,
        content,
        disease: analysis.disease || null,
        symptoms: analysis.symptoms || [],
        medications: analysis.medications || [],
        treatments: analysis.treatments || [],
        outcome: analysis.outcome || null,
      })
      navigate(`/posts/${res.data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to post. Please try again.')
    } finally {
      setPosting(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-gray-400 hover:text-gray-600 mb-4 flex items-center gap-1"
      >
        ← Back
      </button>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Share Your Experience</h1>
        <p className="text-gray-500 text-sm mb-6">
          Write your skin condition story — AI will extract the details for you
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 mb-5 text-sm">
            {error}
          </div>
        )}

        {/* ── STEP 1: Write ── */}
        {!analysis ? (
          <form onSubmit={handleAnalyze} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
              <input
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className={inputCls}
                placeholder="e.g. My experience managing eczema on my hands"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Your Story *</label>
              <p className="text-xs text-gray-400 mb-1">
                Write freely — mention your condition, symptoms, what you tried, and how it went
              </p>
              <textarea
                required
                rows={8}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className={inputCls}
                placeholder="e.g. I have been dealing with eczema on my hands for about a year. My skin gets very dry and itchy, especially in winter. I tried regular moisturiser at first but it didn't help much. My dermatologist prescribed a hydrocortisone cream and told me to use fragrance-free products. Avoiding hot water when washing hands helped a lot. Things have improved but I still get flare-ups..."
              />
            </div>

            <button
              type="submit"
              disabled={analyzing || !title.trim() || !content.trim()}
              className="w-full bg-teal-600 hover:bg-teal-700 text-white font-medium py-3 rounded-lg transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {analyzing ? (
                <>
                  <Spinner />
                  Analyzing your story…
                </>
              ) : (
                '✦ Analyze with AI →'
              )}
            </button>
          </form>
        ) : (
          /* ── STEP 2: Review AI analysis ── */
          <div className="space-y-5">
            {/* Original text summary */}
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-xs text-gray-400 font-medium uppercase tracking-wide mb-1">Your Story</p>
              <p className="text-sm font-semibold text-gray-800">{title}</p>
              <p className="text-sm text-gray-500 mt-1 line-clamp-3">{content}</p>
            </div>

            {/* AI extracted fields */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-sm font-medium text-gray-700">AI Analysis</span>
                <span className="text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full font-medium">✓ Extracted</span>
              </div>

              <div className="grid grid-cols-1 gap-3">
                <AnalysisRow
                  icon="🏥"
                  label="Condition"
                  value={analysis.disease}
                  empty="Not identified"
                />
                <AnalysisRow
                  icon="🤒"
                  label="Symptoms"
                  items={analysis.symptoms}
                  color="red"
                />
                <AnalysisRow
                  icon="💊"
                  label="Medications"
                  items={analysis.medications}
                  color="blue"
                />
                <AnalysisRow
                  icon="🔧"
                  label="Treatments"
                  items={analysis.treatments}
                  color="purple"
                />
                <AnalysisRow
                  icon="✅"
                  label="Outcome"
                  value={analysis.outcome}
                  empty="Not mentioned"
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                onClick={() => setAnalysis(null)}
                className="flex-1 border border-gray-200 text-gray-600 hover:bg-gray-50 font-medium py-2.5 rounded-lg transition-colors text-sm"
              >
                ← Edit Story
              </button>
              <button
                onClick={handlePost}
                disabled={posting}
                className="flex-2 flex-grow bg-teal-600 hover:bg-teal-700 text-white font-medium py-2.5 px-6 rounded-lg transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
              >
                {posting ? (
                  <>
                    <Spinner />
                    Posting…
                  </>
                ) : (
                  'Share Post →'
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

/* ── sub-components ── */

function AnalysisRow({ icon, label, value, items, color = 'teal', empty = 'None found' }) {
  const tagColors = {
    red: 'bg-red-50 text-red-700',
    blue: 'bg-blue-50 text-blue-700',
    purple: 'bg-purple-50 text-purple-700',
    teal: 'bg-teal-50 text-teal-700',
  }
  const tagCls = tagColors[color] || tagColors.teal

  return (
    <div className="flex items-start gap-3 bg-gray-50 rounded-lg px-4 py-3">
      <span className="text-lg mt-0.5">{icon}</span>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-gray-400 font-medium mb-1">{label}</p>
        {items !== undefined ? (
          items.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {items.map((item) => (
                <span key={item} className={`text-xs px-2 py-0.5 rounded-full font-medium ${tagCls}`}>
                  {item}
                </span>
              ))}
            </div>
          ) : (
            <span className="text-sm text-gray-400">{empty}</span>
          )
        ) : (
          <span className={`text-sm font-medium ${value ? 'text-gray-800' : 'text-gray-400'}`}>
            {value || empty}
          </span>
        )}
      </div>
    </div>
  )
}

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
    </svg>
  )
}

const inputCls =
  'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500'
