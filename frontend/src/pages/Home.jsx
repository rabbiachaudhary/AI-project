import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { postsApi, searchApi } from '../api/client'
import { useAuth } from '../context/AuthContext'
import PostCard from '../components/PostCard'

const FEATURES = [
  {
    icon: '💬',
    title: 'Community Stories',
    description:
      'Read real experiences from people who faced similar symptoms, diagnoses, and treatments — tagged and searchable.',
    link: '#community',
    linkLabel: 'Browse stories',
  },
  {
    icon: '🤖',
    title: 'AI Health Assistant',
    description:
      'Ask questions and get answers grounded in community posts and dermatology knowledge — not generic web results.',
    link: '/chat',
    linkLabel: 'Try AI Chat',
  },
  {
    icon: '🔬',
    title: 'Skin Condition Detector',
    description:
      'Upload a skin image for AI-powered analysis, then get personalized insights linked to real community experiences.',
    link: '/detect',
    linkLabel: 'Detect now',
  },
]

const STEPS = [
  { step: '01', title: 'Share or search', text: 'Post your health journey or find others with similar experiences.' },
  { step: '02', title: 'Get AI insights', text: 'Our assistant analyzes stories and connects you to relevant knowledge.' },
  { step: '03', title: 'Make informed decisions', text: 'Use community wisdom alongside professional medical advice.' },
]

export default function Home() {
  const { user } = useAuth()
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [searchResults, setSearchResults] = useState(null)

  useEffect(() => {
    postsApi
      .list()
      .then((res) => setPosts(res.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) {
      setSearchResults(null)
      return
    }
    setSearching(true)
    try {
      const res = await searchApi.search(searchQuery)
      setSearchResults(res.data.results)
      document.getElementById('community')?.scrollIntoView({ behavior: 'smooth' })
    } catch (err) {
      console.error(err)
    } finally {
      setSearching(false)
    }
  }

  const displayed = searchResults ?? posts
  const previewPosts = displayed.slice(0, 6)

  return (
    <div className="bg-gray-50">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-teal-600 via-teal-700 to-emerald-800" />
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-teal-300 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-10 pb-16 sm:pt-20 sm:pb-28">
          <div className="max-w-3xl mx-auto text-center">
            <span className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm border border-white/20 text-teal-50 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
              <span className="w-2 h-2 bg-emerald-300 rounded-full animate-pulse" />
              AI-powered health community
            </span>

            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-bold text-white tracking-tight leading-tight mb-4 sm:mb-5">
              Real health stories.
              <span className="block text-teal-200">Smarter decisions.</span>
            </h1>

            <p className="text-base sm:text-xl text-teal-100/90 leading-relaxed mb-6 sm:mb-8 max-w-2xl mx-auto px-1">
              HealNet connects you with community experiences, an AI health assistant, and skin
              condition detection — so you never navigate health alone.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-10">
              {user ? (
                <>
                  <Link
                    to="/create"
                    className="w-full sm:w-auto bg-white text-teal-700 font-semibold px-8 py-3 rounded-xl hover:bg-teal-50 transition-colors shadow-lg shadow-teal-900/20"
                  >
                    Share your story
                  </Link>
                  <a
                    href="#community"
                    className="w-full sm:w-auto border border-white/30 text-white font-medium px-8 py-3 rounded-xl hover:bg-white/10 transition-colors"
                  >
                    Browse community
                  </a>
                </>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="w-full sm:w-auto bg-white text-teal-700 font-semibold px-8 py-3 rounded-xl hover:bg-teal-50 transition-colors shadow-lg shadow-teal-900/20"
                  >
                    Get started free
                  </Link>
                  <Link
                    to="/login"
                    className="w-full sm:w-auto border border-white/30 text-white font-medium px-8 py-3 rounded-xl hover:bg-white/10 transition-colors"
                  >
                    Sign in
                  </Link>
                </>
              )}
            </div>

            <form onSubmit={handleSearch} className="max-w-xl mx-auto flex flex-col sm:flex-row gap-2 w-full">
              <input
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  if (!e.target.value) setSearchResults(null)
                }}
                placeholder="Search symptoms, diseases, medications…"
                className="flex-1 min-w-0 rounded-xl px-4 py-3 text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-white/50 shadow-lg"
              />
              <button
                type="submit"
                disabled={searching}
                className="w-full sm:w-auto bg-teal-900/40 backdrop-blur-sm border border-white/20 text-white font-medium px-6 py-3 rounded-xl hover:bg-teal-900/60 transition-colors disabled:opacity-60"
              >
                {searching ? '…' : 'Search'}
              </button>
            </form>
          </div>

          {/* Stats strip */}
          <div className="mt-10 sm:mt-16 grid grid-cols-3 gap-2 sm:gap-4 max-w-lg mx-auto">
            {[
              { value: posts.length || '—', label: 'Stories shared' },
              { value: '3', label: 'AI tools' },
              { value: 'Free', label: 'To join' },
            ].map(({ value, label }) => (
              <div key={label} className="text-center">
                <p className="text-2xl sm:text-3xl font-bold text-white">{value}</p>
                <p className="text-xs sm:text-sm text-teal-200/80 mt-1">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20">
        <div className="text-center mb-8 sm:mb-14">
          <h2 className="text-2xl sm:text-4xl font-bold text-gray-900 mb-3 sm:mb-4">
            Everything you need in one place
          </h2>
          <p className="text-gray-500 text-base sm:text-lg max-w-2xl mx-auto">
            From sharing your journey to getting AI-powered insights — HealNet is built for
            skin health and beyond.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="bg-white rounded-xl sm:rounded-2xl border border-gray-100 p-5 sm:p-7 hover:border-teal-200 hover:shadow-md transition-all group"
            >
              <div className="w-12 h-12 bg-teal-50 rounded-xl flex items-center justify-center text-2xl mb-5 group-hover:scale-110 transition-transform">
                {f.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed mb-4">{f.description}</p>
              {f.link.startsWith('/') ? (
                <Link to={f.link} className="text-sm font-medium text-teal-600 hover:text-teal-700">
                  {f.linkLabel} →
                </Link>
              ) : (
                <a href={f.link} className="text-sm font-medium text-teal-600 hover:text-teal-700">
                  {f.linkLabel} →
                </a>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-white border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20">
          <div className="text-center mb-8 sm:mb-14">
            <h2 className="text-2xl sm:text-4xl font-bold text-gray-900 mb-3 sm:mb-4">How it works</h2>
            <p className="text-gray-500 text-base sm:text-lg">Three simple steps to get value from HealNet</p>
          </div>

          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8">
            {STEPS.map((s) => (
              <div key={s.step} className="relative text-center md:text-left">
                <span className="text-5xl font-bold text-teal-100">{s.step}</span>
                <h3 className="text-lg font-semibold text-gray-900 mt-2 mb-2">{s.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{s.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Community feed */}
      <section id="community" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6 sm:mb-8">
          <div className="min-w-0">
            <h2 className="text-2xl sm:text-4xl font-bold text-gray-900 mb-2">
              {searchResults ? 'Search results' : 'Community feed'}
            </h2>
            <p className="text-gray-500">
              {searchResults
                ? `${searchResults.length} results for "${searchQuery}"`
                : 'Recent health experiences from the community'}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {searchResults && (
              <button
                onClick={() => {
                  setSearchResults(null)
                  setSearchQuery('')
                }}
                className="text-sm text-gray-500 hover:text-gray-700 px-3 py-2"
              >
                Clear search
              </button>
            )}
            {user ? (
              <Link
                to="/create"
                className="flex-1 sm:flex-none text-center bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium px-5 py-2.5 rounded-xl transition-colors"
              >
                + Share experience
              </Link>
            ) : (
              <Link
                to="/register"
                className="flex-1 sm:flex-none text-center bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium px-5 py-2.5 rounded-xl transition-colors"
              >
                Join to share
              </Link>
            )}
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : previewPosts.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
            <p className="text-lg text-gray-400 mb-2">No experiences yet</p>
            <p className="text-sm text-gray-400 mb-6">Be the first to share your health story</p>
            <Link
              to={user ? '/create' : '/register'}
              className="inline-block bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium px-6 py-2.5 rounded-xl transition-colors"
            >
              {user ? 'Share your story' : 'Get started'}
            </Link>
          </div>
        ) : (
          <>
            <div className="grid sm:grid-cols-2 gap-4">
              {previewPosts.map((post) => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
            {displayed.length > 6 && (
              <p className="text-center text-sm text-gray-400 mt-6">
                Showing 6 of {displayed.length} experiences — use search to find more
              </p>
            )}
          </>
        )}
      </section>

      {/* Bottom CTA */}
      {!user && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12 sm:pb-20">
          <div className="bg-gradient-to-r from-teal-600 to-teal-700 rounded-2xl sm:rounded-3xl px-5 py-10 sm:px-16 sm:py-14 text-center">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">
              Ready to join the community?
            </h2>
            <p className="text-teal-100 mb-8 max-w-lg mx-auto">
              Create a free account to share your experience, upvote stories, and unlock the full
              HealNet experience.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                to="/register"
                className="w-full sm:w-auto bg-white text-teal-700 font-semibold px-8 py-3 rounded-xl hover:bg-teal-50 transition-colors"
              >
                Create free account
              </Link>
              <Link
                to="/login"
                className="w-full sm:w-auto text-white font-medium px-8 py-3 rounded-xl border border-white/30 hover:bg-white/10 transition-colors"
              >
                I already have an account
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
          <div className="flex flex-col items-center gap-5 sm:gap-4 text-center sm:text-left sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 bg-teal-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-xs font-bold">H</span>
              </div>
              <span className="font-bold text-gray-900">HealNet</span>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-sm text-gray-500">
              <Link to="/chat" className="hover:text-gray-900 transition-colors">AI Chat</Link>
              <Link to="/detect" className="hover:text-gray-900 transition-colors">Skin Detector</Link>
              <Link to="/login" className="hover:text-gray-900 transition-colors">Sign in</Link>
              <Link to="/register" className="hover:text-gray-900 transition-colors">Sign up</Link>
            </div>
            <p className="text-xs text-gray-400 max-w-xs sm:max-w-none">
              Not a substitute for professional medical advice.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
