import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { postsApi, searchApi } from '../api/client'
import { useAuth } from '../context/AuthContext'
import PostCard from '../components/PostCard'

export default function Home() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [searchResults, setSearchResults] = useState(null)

  useEffect(() => {
    postsApi.list()
      .then((res) => setPosts(res.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) { setSearchResults(null); return }
    setSearching(true)
    try {
      const res = await searchApi.search(searchQuery)
      setSearchResults(res.data.results)
    } catch (err) {
      console.error(err)
    } finally {
      setSearching(false)
    }
  }

  const displayed = searchResults ?? posts

  return (
    <div>
      {/* Hero */}
      <div className="bg-gradient-to-r from-teal-600 to-teal-700 rounded-2xl p-8 mb-8 text-white">
        <h1 className="text-3xl font-bold mb-2">HealNet</h1>
        <p className="text-teal-100 mb-5">
          Real health experiences from real people. Learn from the community, share your story.
        </p>
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); if (!e.target.value) setSearchResults(null) }}
            placeholder="Search symptoms, diseases, medications…"
            className="flex-1 rounded-lg px-4 py-2 text-gray-900 text-sm focus:outline-none"
          />
          <button
            type="submit"
            disabled={searching}
            className="bg-white text-teal-700 font-medium px-5 py-2 rounded-lg hover:bg-teal-50 transition-colors disabled:opacity-60"
          >
            {searching ? '…' : 'Search'}
          </button>
        </form>
      </div>

      {/* Actions bar */}
      <div className="flex justify-between items-center mb-5">
        <h2 className="font-semibold text-gray-700">
          {searchResults ? `${searchResults.length} results for "${searchQuery}"` : 'Recent Experiences'}
        </h2>
        <div className="flex gap-2">
          {searchResults && (
            <button
              onClick={() => { setSearchResults(null); setSearchQuery('') }}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              ✕ Clear
            </button>
          )}
          {user ? (
            <Link
              to="/create"
              className="bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              + Share Experience
            </Link>
          ) : (
            <Link to="/login" className="text-sm text-teal-600 hover:underline">
              Sign in to share
            </Link>
          )}
        </div>
      </div>

      {/* Feed */}
      {loading ? (
        <div className="flex justify-center py-16">
          <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : displayed.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <p className="text-lg mb-2">No experiences found</p>
          <p className="text-sm">Be the first to share your health story</p>
        </div>
      ) : (
        <div className="space-y-4">
          {displayed.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  )
}
