/** Pinia 认证 Store — 管理用户状态、JWT token、登录/登出/获取用户信息 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../api'

export const useAuthStore = defineStore('auth', () => {
  /** 用户状态从 sessionStorage 恢复，实现页面刷新后保持登录 */
  const user = ref(JSON.parse(sessionStorage.getItem('user') || 'null'))
  const token = ref(sessionStorage.getItem('access_token') || '')
  const refreshToken = ref(sessionStorage.getItem('refresh_token') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isStudent = computed(() => user.value?.role === 'student')
  const isTeacher = computed(() => user.value?.role === 'teacher')
  const isAdmin = computed(() => user.value?.role === 'admin')
  /** 登录：调用后端 API，将 token 和用户信息存入 sessionStorage */
  async function login(account, password) {
    const res = await authAPI.login({ account, password })
    const data = res.data
    user.value = data.user
    token.value = data.access_token
    refreshToken.value = data.refresh_token
    sessionStorage.setItem('user', JSON.stringify(data.user))
    sessionStorage.setItem('access_token', data.access_token)
    sessionStorage.setItem('refresh_token', data.refresh_token)
    return data
  }

  async function fetchUser() {
    try {
      const res = await authAPI.getMe()
      user.value = res.data
      sessionStorage.setItem('user', JSON.stringify(user.value))
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    refreshToken.value = ''
    sessionStorage.clear()
  }

  return { user, token, refreshToken, isLoggedIn, isStudent, isTeacher, isAdmin, login, fetchUser, logout }
})
