import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({ baseURL: BASE_URL })

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('healnet_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default client

export const authApi = {
  register: (email, password, username) =>
    client.post('/auth/register', { email, password, username }),

  login: (email, password) => {
    const form = new FormData()
    form.append('username', email)
    form.append('password', password)
    return client.post('/auth/login', form)
  },

  me: () => client.get('/auth/me'),
}

export const postsApi = {
  list: (skip = 0, limit = 20) => client.get(`/posts/?skip=${skip}&limit=${limit}`),
  get: (id) => client.get(`/posts/${id}`),
  create: (data) => client.post('/posts/', data),
  analyze: (title, content) => client.post('/posts/analyze', { title, content }),
  update: (id, data) => client.put(`/posts/${id}`, data),
  remove: (id) => client.delete(`/posts/${id}`),
  upvote: (id) => client.post(`/posts/${id}/upvote`),
  getComments: (id) => client.get(`/posts/${id}/comments`),
  addComment: (id, content) => client.post(`/posts/${id}/comments`, { content }),
  removeComment: (postId, commentId) => client.delete(`/posts/${postId}/comments/${commentId}`),
}

export const searchApi = {
  search: (q, limit = 10) =>
    client.get(`/search/?q=${encodeURIComponent(q)}&limit=${limit}`),
}

export const chatApi = {
  send: (query, disease, symptoms, medications) =>
    client.post('/chat/', { query, disease, symptoms, medications }),
}
