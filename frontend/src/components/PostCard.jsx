import { Link } from 'react-router-dom'

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

export default function PostCard({ post }) {
  const preview = post.content?.length > 180
    ? post.content.slice(0, 180).trimEnd() + '…'
    : post.content

  const date = new Date(post.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })

  return (
    <Link to={`/posts/${post.id}`} className="block group">
      <div className="bg-white border border-gray-100 rounded-xl sm:rounded-2xl p-4 sm:p-5 hover:border-teal-200 hover:shadow-sm transition-all">
        {/* Header */}
        <div className="flex items-start justify-between gap-2 sm:gap-4 mb-2">
          <h2 className="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors leading-snug min-w-0 break-words">
            {post.title}
          </h2>
          <span className="text-sm text-gray-400 whitespace-nowrap flex items-center gap-1 flex-shrink-0 pt-0.5">
            <span className="text-teal-500">▲</span> {post.upvotes}
          </span>
        </div>

        {/* Meta */}
        <p className="text-xs text-gray-400 mb-3">
          by <span className="font-medium text-gray-500">{post.author_username}</span> · {date}
        </p>

        {/* Tags */}
        {(post.disease || post.symptoms?.length > 0 || post.medications?.length > 0) && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {post.disease && <Tag label={post.disease} color="blue" />}
            {post.symptoms?.slice(0, 3).map((s) => (
              <Tag key={s} label={s} color="teal" />
            ))}
            {post.medications?.slice(0, 2).map((m) => (
              <Tag key={m} label={m} color="purple" />
            ))}
            {post.outcome && <Tag label={post.outcome} color="orange" />}
          </div>
        )}

        {/* Content preview */}
        <p className="text-sm text-gray-600 leading-relaxed">{preview}</p>
      </div>
    </Link>
  )
}
