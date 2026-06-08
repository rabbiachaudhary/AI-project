import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function NavLinks({ user, linkCls, anchorCls, onNavigate }) {
  if (user) {
    return (
      <>
        <Link to="/#community" className={anchorCls} onClick={onNavigate}>
          Community
        </Link>
        <NavLink to="/chat" className={linkCls} onClick={onNavigate}>
          AI Chat
        </NavLink>
        <NavLink to="/detect" className={linkCls} onClick={onNavigate}>
          Skin Detector
        </NavLink>
      </>
    )
  }

  return (
    <>
      <NavLink to="/" end className={linkCls} onClick={onNavigate}>
        Home
      </NavLink>
      <Link to="/#features" className={anchorCls} onClick={onNavigate}>
        Features
      </Link>
      <Link to="/#community" className={anchorCls} onClick={onNavigate}>
        Community
      </Link>
      <NavLink to="/chat" className={linkCls} onClick={onNavigate}>
        AI Chat
      </NavLink>
      <NavLink to="/detect" className={linkCls} onClick={onNavigate}>
        Skin Detector
      </NavLink>
    </>
  )
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
    setMenuOpen(false)
  }

  const closeMenu = () => setMenuOpen(false)

  const linkCls = ({ isActive }) =>
    `block sm:inline text-base sm:text-sm font-medium transition-colors py-2 sm:py-0 ${
      isActive ? 'text-teal-600' : 'text-gray-600 sm:text-gray-500 hover:text-gray-900'
    }`

  const anchorCls =
    'text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors block sm:inline py-2 sm:py-0'

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="h-14 flex items-center justify-between gap-3">
          {/* Brand */}
          <Link
            to={user ? '/#community' : '/'}
            className="flex items-center gap-2 flex-shrink-0"
            onClick={closeMenu}
          >
            <div className="w-7 h-7 bg-teal-600 rounded-lg flex items-center justify-center">
              <span className="text-white text-xs font-bold">D</span>
            </div>
            <span className="font-bold text-gray-900">DermaCom</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-5 lg:gap-6">
            <NavLinks user={user} linkCls={linkCls} anchorCls={anchorCls} />
          </div>

          {/* Desktop auth */}
          <div className="hidden sm:flex items-center gap-2 sm:gap-3 flex-shrink-0">
            {user ? (
              <>
                <Link
                  to="/create"
                  className="bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap"
                >
                  + Share
                </Link>
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center text-xs font-bold">
                    {user.username?.[0]?.toUpperCase() ?? '?'}
                  </div>
                  <button
                    onClick={handleLogout}
                    className="text-sm text-gray-400 hover:text-gray-600 transition-colors hidden md:inline"
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
                  className="bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap"
                >
                  Join free
                </Link>
              </>
            )}
          </div>

          {/* Mobile: compact auth + menu toggle */}
          <div className="flex sm:hidden items-center gap-2">
            {user ? (
              <Link
                to="/create"
                onClick={closeMenu}
                className="bg-teal-600 hover:bg-teal-700 text-white text-xs font-medium px-2.5 py-1.5 rounded-lg transition-colors"
              >
                + Share
              </Link>
            ) : (
              <Link
                to="/register"
                onClick={closeMenu}
                className="bg-teal-600 hover:bg-teal-700 text-white text-xs font-medium px-2.5 py-1.5 rounded-lg transition-colors"
              >
                Join
              </Link>
            )}
            <button
              type="button"
              onClick={() => setMenuOpen((o) => !o)}
              className="p-2 -mr-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
              aria-label={menuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={menuOpen}
            >
              {menuOpen ? (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile menu panel */}
        {menuOpen && (
          <div className="md:hidden border-t border-gray-100 py-3 pb-4 space-y-1 px-2">
            <NavLinks user={user} linkCls={linkCls} anchorCls={anchorCls} onNavigate={closeMenu} />

            <div className="pt-3 mt-2 border-t border-gray-100 flex flex-col gap-2 px-2">
              {user ? (
                <>
                  <div className="flex items-center gap-2 py-1">
                    <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center text-sm font-bold">
                      {user.username?.[0]?.toUpperCase() ?? '?'}
                    </div>
                    <span className="text-sm font-medium text-gray-700">{user.username}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left py-2 text-base font-medium text-gray-600 hover:text-red-600"
                  >
                    Sign out
                  </button>
                </>
              ) : (
                <Link
                  to="/login"
                  onClick={closeMenu}
                  className="block py-2 text-base font-medium text-gray-600 hover:text-gray-900"
                >
                  Sign in
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
