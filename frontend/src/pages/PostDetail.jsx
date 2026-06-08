import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { postsApi } from '../api/client'
import { useAuth } from '../context/AuthContext'

const getUpvotedIds = () => JSON.parse(localStorage.getItem('dermacom_upvoted') || '[]')
const saveUpvotedId = (id) => {
  const ids = getUpvotedIds()
  if (!ids.includes(id)) localStorage.setItem('dermacom_upvoted', JSON.stringify([...ids, id]))
}

function Tag({ label, color = 'teal' }) {
  const colors = {
    teal: 'bg-teal-50 text-teal-700',
    blue: 'bg-blue-50 text-blue-700',
    purple: 'bg-purple-50 text-purple-700',
    orange: 'bg-orange-50 text-orange-700',
  }
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colors[color]}`}>
      {label}
    </span>
  )
}

export default function PostDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [post, setPost] = useState(null)
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [upvoted, setUpvoted] = useState(() => getUpvotedIds().includes(id))

  // edit state
  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState('')
  const [editContent, setEditContent] = useState('')
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [editError, setEditError] = useState('')

  useEffect(() => {
    Promise.all([postsApi.get(id), postsApi.getComments(id)])
      .then(([postRes, commentsRes]) => {
        setPost(postRes.data)
        setComments(commentsRes.data)
      })
      .catch(() => navigate('/'))
      .finally(() => setLoading(false))
  }, [id])

  const isOwner = user && post && user.id === post.author_id

  const startEdit = () => {
    setEditTitle(post.title)
    setEditContent(post.content)
    setEditError('')
    setIsEditing(true)
  }

  const cancelEdit = () => setIsEditing(false)

  const handleSave = async () => {
    if (!editTitle.trim() || !editContent.trim()) return
    setSaving(true)
    setEditError('')
    try {
      const res = await postsApi.update(id, {
        title: editTitle,
        content: editContent,
        disease: post.disease,
        symptoms: post.symptoms,
        medications: post.medications,
        treatments: post.treatments,
        outcome: post.outcome,
      })
      setPost(res.data)
      setIsEditing(false)
    } catch (err) {
      setEditError(err.response?.data?.detail || 'Failed to save. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete this post? This cannot be undone.')) return
    setDeleting(true)
    try {
      await postsApi.remove(id)
      navigate('/')
    } catch {
      setDeleting(false)
    }
  }

  const handleUpvote = async () => {
    if (!user || upvoted) return
    const res = await postsApi.upvote(id)
    if (!res.data.already) setPost((p) => ({ ...p, upvotes: p.upvotes + 1 }))
    saveUpvotedId(id)
    setUpvoted(true)
  }

  const handleDeleteComment = async (commentId) => {
    await postsApi.removeComment(id, commentId)
    setComments((prev) => prev.filter((c) => c.id !== commentId))
  }

  const handleComment = async (e) => {
    e.preventDefault()
    if (!newComment.trim()) return
    setSubmitting(true)
    try {
      const res = await postsApi.addComment(id, newComment)
      setComments((prev) => [...prev, res.data])
      setNewComment('')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return (
    <div className="flex justify-center py-16">
      <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )

  if (!post) return null

  return (
    <div className="max-w-2xl mx-auto w-full min-w-0">
      <button onClick={() => navigate(-1)} className="text-sm text-gray-400 hover:text-gray-600 mb-3 sm:mb-4 flex items-center gap-1">
        ← Back to feed
      </button>

      <div className="bg-white rounded-xl sm:rounded-2xl shadow-sm border border-gray-100 p-4 sm:p-8 mb-4 sm:mb-6">

        {isEditing ? (
          /* ── Edit mode ── */
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Title</label>
              <input
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Your Story</label>
              <textarea
                rows={8}
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            {editError && (
              <p className="text-sm text-red-600">{editError}</p>
            )}
            <div className="flex gap-2 pt-1">
              <button
                onClick={cancelEdit}
                className="flex-1 border border-gray-200 text-gray-600 hover:bg-gray-50 text-sm font-medium py-2 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex-1 bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium py-2 rounded-lg transition-colors disabled:opacity-60"
              >
                {saving ? 'Saving…' : 'Save Changes'}
              </button>
            </div>
          </div>
        ) : (
          /* ── View mode ── */
          <>
            <div className="flex flex-col-reverse sm:flex-row sm:items-start sm:justify-between gap-3 sm:gap-4 mb-4">
              <div className="flex-1 min-w-0">
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 break-words">{post.title}</h1>
                <p className="text-sm text-gray-400">
                  by <span className="font-medium text-gray-600">{post.author_username}</span>{' '}
                  · {new Date(post.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
                </p>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0 self-start sm:self-auto">
                {isOwner && (
                  <>
                    <button
                      onClick={startEdit}
                      className="text-xs text-gray-400 hover:text-teal-600 border border-gray-200 hover:border-teal-300 px-2.5 py-1.5 rounded-lg transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={handleDelete}
                      disabled={deleting}
                      className="text-xs text-gray-400 hover:text-red-600 border border-gray-200 hover:border-red-300 px-2.5 py-1.5 rounded-lg transition-colors disabled:opacity-60"
                    >
                      {deleting ? '…' : 'Delete'}
                    </button>
                  </>
                )}
                <button
                  onClick={handleUpvote}
                  disabled={!user || upvoted}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                    upvoted
                      ? 'border-teal-500 bg-teal-50 text-teal-700'
                      : 'border-gray-200 hover:border-teal-400 hover:text-teal-600'
                  } disabled:cursor-default`}
                >
                  ▲ {post.upvotes}
                </button>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mb-5">
              {post.disease && <Tag label={post.disease} color="blue" />}
              {post.outcome && <Tag label={`Outcome: ${post.outcome}`} color="orange" />}
              {post.symptoms.map((s) => <Tag key={s} label={s} color="teal" />)}
              {post.medications.map((m) => <Tag key={m} label={m} color="purple" />)}
            </div>

            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{post.content}</p>

            {post.treatments.length > 0 && (
              <div className="mt-5 p-4 bg-gray-50 rounded-xl">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Treatments Used</p>
                <div className="flex flex-wrap gap-2">
                  {post.treatments.map((t) => <Tag key={t} label={t} color="teal" />)}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Comments */}
      <div className="bg-white rounded-xl sm:rounded-2xl shadow-sm border border-gray-100 p-4 sm:p-6">
        <h2 className="font-semibold text-gray-800 mb-4">
          {comments.length} Comment{comments.length !== 1 ? 's' : ''}
        </h2>

        {user && (
          <form onSubmit={handleComment} className="mb-6 flex flex-col sm:flex-row gap-2">
            <input
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add your thoughts or experience…"
              className="flex-1 min-w-0 border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
            <button
              type="submit"
              disabled={submitting || !newComment.trim()}
              className="w-full sm:w-auto bg-teal-600 text-white text-sm font-medium px-4 py-2.5 rounded-lg hover:bg-teal-700 transition-colors disabled:opacity-60"
            >
              Post
            </button>
          </form>
        )}

        <div className="space-y-4">
          {comments.map((c) => (
            <div key={c.id} className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center text-xs font-bold flex-shrink-0">
                {c.author_username[0].toUpperCase()}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-gray-800">{c.author_username}</span>
                  <span className="text-xs text-gray-400">
                    {new Date(c.created_at).toLocaleDateString()}
                  </span>
                  {user && String(user.id) === c.author_id && (
                    <button
                      onClick={() => handleDeleteComment(c.id)}
                      className="ml-auto text-xs text-gray-300 hover:text-red-500 transition-colors"
                    >
                      Delete
                    </button>
                  )}
                </div>
                <p className="text-sm text-gray-700">{c.content}</p>
              </div>
            </div>
          ))}
          {comments.length === 0 && (
            <p className="text-gray-400 text-sm text-center py-4">No comments yet. Be the first!</p>
          )}
        </div>
      </div>
    </div>
  )
}
