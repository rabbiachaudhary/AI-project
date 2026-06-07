import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const linkCls = ({ isActive }) =>
    `text-sm font-medium transition-colors ${
      isActive ? 'text-teal-600' : 'text-gray-500 hover:text-gray-900'
    }`

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2">
          <div className="w-7 h-7 bg-teal-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-xs font-bold">H</span>
          </div>
          <span className="font-bold text-gray-900">HealNet</span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-6">
          <NavLink to="/" end className={linkCls}>
            Feed
          </NavLink>
          <NavLink to="/chat" className={linkCls}>
            AI Chat
          </NavLink>
          <NavLink to="/detect" className={linkCls}>
            Skin Detector
          </NavLink>
        </div>

        {/* Auth */}
        <div className="flex items-center gap-3">
          {user ? (
            <>
              <Link
                to="/create"
                className="bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium px-3 py-1.5 rounded-lg transition-colors"
              >
                + Share
              </Link>
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center text-xs font-bold">
                  {user.username?.[0]?.toUpperCase() ?? '?'}
                </div>
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
                >
                  Sign out
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm text-gray-500 hover:text-gray-900 font-medium transition-colors">
                Sign in
              </Link>
              <Link
                to="/register"
                className="bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium px-3 py-1.5 rounded-lg transition-colors"
              >
                Join free
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
