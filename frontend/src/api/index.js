/** API 层 — Axios 实例、拦截器、辅助函数、所有后端 API 封装 */

import axios from 'axios'
import { ElMessage } from 'element-plus'

const BASE_URL = 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
})

// Request interceptor - attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor - handle errors globally
api.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        // Try refresh token
        const refreshToken = sessionStorage.getItem('refresh_token')
        if (refreshToken && !error.config._retry) {
          error.config._retry = true
          try {
            const res = await axios.post('http://localhost:8000/api/v1/auth/token/refresh/', {
              refresh: refreshToken,
            })
            const newToken = res.data.access
            sessionStorage.setItem('access_token', newToken)
            error.config.headers.Authorization = `Bearer ${newToken}`
            return api(error.config)
          } catch (refreshError) {
            sessionStorage.clear()
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }
        sessionStorage.clear()
        window.location.href = '/login'
      } else {
        ElMessage.error(data?.message || data?.detail || '请求失败')
      }
    }
    return Promise.reject(error)
  },
)

export default api

/** 从后端响应中提取列表数据，兼容分页(res.results)、包装(res.data)、数组三种格式 */
export function extractList(res, fallback = []) {
  if (Array.isArray(res)) return res
  if (res?.results) return res.results
  if (res?.data?.results) return res.data.results
  if (res?.data && Array.isArray(res.data)) return res.data
  return fallback
}

/** 从后端响应中提取数据总数，支持分页(res.count)和直接数组两种格式 */
export function extractCount(res) {
  if (res?.count !== undefined) return res.count
  if (res?.data?.count !== undefined) return res.data.count
  const list = extractList(res)
  return list.length
}

/** 带 JWT 认证的文件下载，通过 fetch + Blob 方式触发浏览器下载 */
export async function downloadFile(url, filename) {
  const token = sessionStorage.getItem('access_token')
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error('下载失败')
  const blob = await res.blob()
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)
}

// Auth APIs
export const authAPI = {
  login: (data) => api.post('/auth/login/', data),
  sendVerifyCode: (data) => api.post('/auth/verify-code/send/', data),
  getMe: () => api.get('/auth/user/me/'),
  changePassword: (data) => api.put('/auth/user/change-password/', data),
  bindPhone: (data) => api.post('/auth/user/bind-phone/', data),
}

// Student APIs
export const studentAPI = {
  list: (params) => api.get('/auth/students/', { params }),
  create: (data) => api.post('/auth/students/', data),
  update: (id, data) => api.patch(`/auth/students/${id}/`, data),
  delete: (id) => api.delete(`/auth/students/${id}/`),
  resetPassword: (id, data) => api.post(`/auth/students/${id}/reset_password/`, data),
  batchImport: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/auth/students/batch_import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// Teacher APIs
export const teacherAPI = {
  list: (params) => api.get('/auth/teachers/', { params }),
  create: (data) => api.post('/auth/teachers/', data),
  setAdmin: (id) => api.post(`/auth/teachers/${id}/set_admin/`),
  revokeAdmin: (id) => api.post(`/auth/teachers/${id}/revoke_admin/`),
  toggleActive: (id) => api.post(`/auth/teachers/${id}/toggle_active/`),
  resetPassword: (id, data) => api.post(`/auth/teachers/${id}/reset_password/`, data),
}

// Course APIs
export const courseAPI = {
  list: (params) => api.get('/courses/', { params }),
  create: (data) => api.post('/courses/', data),
  update: (id, data) => api.patch(`/courses/${id}/`, data),
  delete: (id) => api.delete(`/courses/${id}/`),
  tree: (id) => api.get(`/courses/${id}/tree/`),
}

export const chapterAPI = {
  list: (params) => api.get('/courses/chapters/', { params }),
  create: (data) => api.post('/courses/chapters/', data),
  update: (id, data) => api.patch(`/courses/chapters/${id}/`, data),
  delete: (id) => api.delete(`/courses/chapters/${id}/`),
}

export const sectionAPI = {
  list: (params) => api.get('/courses/sections/', { params }),
  create: (data) => api.post('/courses/sections/', data),
  update: (id, data) => api.patch(`/courses/sections/${id}/`, data),
  delete: (id) => api.delete(`/courses/sections/${id}/`),
  setActive: (id) => api.post(`/courses/sections/${id}/set_active/`),
  getActive: (courseId) => api.get('/courses/sections/active/', { params: { course_id: courseId } }),
}

// Document APIs
export const documentAPI = {
  list: (params) => api.get('/documents/', { params }),
  upload: (sectionId, file) => {
    const formData = new FormData()
    formData.append('section', sectionId)
    formData.append('title', file.name)
    formData.append('file', file)
    return api.post('/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  replace: (id, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/documents/${id}/replace/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  delete: (id) => api.delete(`/documents/${id}/`),
}

// Question APIs
export const questionAPI = {
  list: (params) => api.get('/questions/', { params }),
  create: (data) => api.post('/questions/', data),
  update: (id, data) => api.patch(`/questions/${id}/`, data),
  delete: (id) => api.delete(`/questions/${id}/`),
  publish: (id) => api.post(`/questions/${id}/publish/`),
  unpublish: (id) => api.post(`/questions/${id}/unpublish/`),
}

// Submission APIs
export const submissionAPI = {
  create: (data) => api.post('/submissions/', data),
  list: (params) => api.get('/submissions/', { params }),
  mySubmissions: (params) => api.get('/submissions/my/', { params }),
}

// Score APIs
export const scoreAPI = {
  list: (params) => api.get('/scores/', { params }),
  create: (data) => api.post('/scores/', data),
  update: (id, data) => api.patch(`/scores/${id}/`, data),
  delete: (id) => api.delete(`/scores/${id}/`),
  myScores: (params) => api.get('/scores/my_scores/', { params }),
  modify: (id, data) => api.put(`/scores/${id}/modify/`, data),
  exportExcel: (params) =>
    api.get('/scores/export_excel/', { params, responseType: 'blob' }),
  importExcel: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/scores/import_excel/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
