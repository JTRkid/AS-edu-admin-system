<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="header-left">
        <span class="logo">教学平台 · 管理员端</span>
      </div>
      <div class="header-right">
        <span>{{ user?.name }}</span>
        <el-dropdown>
          <el-avatar :size="32" icon="UserFilled" />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container class="main">
      <el-aside width="200px" class="aside">
        <el-menu :default-active="activeMenu" router class="side-menu">
          <el-menu-item index="/admin/dashboard">
            <el-icon><Monitor /></el-icon>
            <span>服务监控</span>
          </el-menu-item>
          <el-menu-item index="/admin/teachers">
            <el-icon><UserFilled /></el-icon>
            <span>教师管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/logs">
            <el-icon><Clock /></el-icon>
            <span>操作日志</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const user = authStore.user
const activeMenu = computed(() => route.path)

function handleLogout() { authStore.logout(); router.push('/login') }
</script>

<style scoped>
.layout { height: 100vh; }
.header {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; border-bottom: 1px solid #ebeef5; padding: 0 20px; height: 56px;
}
.header-left, .header-right { display: flex; align-items: center; gap: 12px; }
.logo { font-size: 17px; font-weight: 600; color: #303133; }
.aside { background: #fafafa; border-right: 1px solid #ebeef5; }
.side-menu { border-right: none; height: 100%; background: transparent; }
.content { padding: 20px; background: #f0f2f5; }
</style>
