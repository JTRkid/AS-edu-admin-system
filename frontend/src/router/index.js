/** 路由配置 — 基于角色的路由守卫，学生/教师/管理员三套布局 */

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/student',
    component: () => import('../layouts/StudentLayout.vue'),
    meta: { role: 'student', requiresAuth: true },
    children: [
      { path: '', redirect: '/student/dashboard' },
      { path: 'dashboard', name: 'StudentDashboard', component: () => import('../views/student/Dashboard.vue') },
      { path: 'scores', name: 'StudentScores', component: () => import('../views/student/MyScores.vue') },
    ],
  },
  {
    path: '/teacher',
    component: () => import('../layouts/TeacherLayout.vue'),
    meta: { role: 'teacher', requiresAuth: true },
    children: [
      { path: '', redirect: '/teacher/courses' },
      { path: 'courses', name: 'TeacherCourses', component: () => import('../views/teacher/CourseManage.vue') },
      { path: 'questions', name: 'TeacherQuestions', component: () => import('../views/teacher/QuestionManage.vue') },
      { path: 'students', name: 'TeacherStudents', component: () => import('../views/teacher/StudentManage.vue') },
      { path: 'scores', name: 'TeacherScores', component: () => import('../views/teacher/ScoreManage.vue') },
    ],
  },
  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { role: 'admin', requiresAuth: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('../views/admin/Monitor.vue') },
      { path: 'teachers', name: 'AdminTeachers', component: () => import('../views/admin/TeacherManage.vue') },
      { path: 'logs', name: 'AdminLogs', component: () => import('../views/admin/OperationLogs.vue') },
    ],
  },
  { path: '/', redirect: '/login' },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

/** 全局路由守卫：检查登录状态和角色权限，未登录跳转/login，无权限跳转/login */
router.beforeEach((to, from, next) => {
  const token = sessionStorage.getItem('access_token')
  const user = JSON.parse(sessionStorage.getItem('user') || 'null')

  if (to.meta.public) {
    if (token && to.name === 'Login') {
      const role = user?.role
      if (role === 'student') return next('/student')
      if (role === 'teacher') return next('/teacher')
      if (role === 'admin') return next('/admin')
    }
    return next()
  }
  if (!token) return next('/login')

  const requiredRole = to.meta.role
  if (requiredRole) {
    const userRole = user?.role
    if (userRole === 'admin') return next()
    if (userRole !== requiredRole) return next('/login')
  }
  next()
})

export default router
