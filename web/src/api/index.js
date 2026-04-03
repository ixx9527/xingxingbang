import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截 - 添加 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截 - 处理错误
api.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// 认证
export const auth = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data)
}

// 邀请码
export const inviteCodes = {
  list: () => api.get('/invite-codes'),
  create: (data) => api.post('/invite-codes', data),
  delete: (id) => api.delete(`/invite-codes/${id}`)
}

// 孩子
export const children = {
  list: () => api.get('/children'),
  get: (id) => api.get(`/children/${id}`),
  create: (data) => api.post('/children', data),
  getScores: (id) => api.get(`/children/${id}/scores`),
  getLevel: (id) => api.get(`/children/${id}/level`),
  getChart: (id, days) => api.get(`/children/${id}/scores/chart?days=${days || 30}`),
  getRecords: (id, params) => api.get(`/children/${id}/records`, { params })
}

// 行为
export const behaviors = {
  list: (category) => api.get('/behaviors', { params: { category } }),
  create: (data) => api.post('/behaviors', data),
  update: (id, data) => api.put(`/behaviors/${id}`, data),
  delete: (id) => api.delete(`/behaviors/${id}`),
  reset: () => api.post('/behaviors/reset')
}

// 打卡记录
export const records = {
  create: (childId, data) => api.post(`/children/${childId}/records`, data)
}

export default api