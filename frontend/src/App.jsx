import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import PostDetail from './pages/PostDetail'
import CreatePost from './pages/CreatePost'
import Chat from './pages/Chat'
import SkinDetector from './pages/SkinDetector'

function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )
  return user ? children : <Navigate to="/login" replace />
}

function AppLayout() {
  const { pathname } = useLocation()
  const isLanding = pathname === '/'
  const isChat = pathname === '/chat'

  const mainCls = isLanding
    ? ''
    : isChat
      ? 'max-w-4xl mx-auto px-4 sm:px-6 py-2 sm:py-4 w-full min-w-0 h-[calc(100dvh-3.5rem)] sm:h-auto sm:min-h-0'
      : 'max-w-4xl mx-auto px-4 sm:px-6 py-4 sm:py-8 w-full min-w-0'

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className={mainCls}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/posts/:id" element={<PostDetail />} />
          <Route path="/create" element={<PrivateRoute><CreatePost /></PrivateRoute>} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/detect" element={<SkinDetector />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </AuthProvider>
  )
}
