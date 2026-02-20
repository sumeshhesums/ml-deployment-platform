import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/auth/refresh`, null, {
            params: { refresh_token: refreshToken }
          })
          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export { api }

export const authAPI = {
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  login: (data: { username: string; password: string }) =>
    api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
}

export const modelsAPI = {
  upload: (formData: FormData) =>
    api.post('/models/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  list: (skip = 0, limit = 100) =>
    api.get(`/models?skip=${skip}&limit=${limit}`),
  get: (id: number) => api.get(`/models/${id}`),
  update: (id: number, data: any) => api.put(`/models/${id}`, data),
  delete: (id: number) => api.delete(`/models/${id}`),
  predict: (id: number, inputData: any) =>
    api.post(`/models/${id}/predict`, { input_data: inputData }),
  getStats: (id: number) => api.get(`/models/${id}/stats`),
  getHistory: (id: number, skip = 0, limit = 50) =>
    api.get(`/models/${id}/history?skip=${skip}&limit=${limit}`),
}

export default api
