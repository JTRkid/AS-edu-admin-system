<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="header-left">
        <span class="logo">AS-edu-system · 教师端</span>
      </div>
      <div class="header-right">
        <span>{{ user?.name }}</span>
        <el-dropdown>
          <el-avatar :size="32" icon="UserFilled" />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="showChangePwd = true">修改密码</el-dropdown-item>
              <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container class="main">
      <el-aside width="260px" class="aside">
        <el-menu :default-active="activeMenu" router class="side-menu">
          <el-menu-item index="/teacher/courses">
            <el-icon><Document /></el-icon>
            <span>课程管理</span>
          </el-menu-item>
          <el-menu-item index="/teacher/questions">
            <el-icon><Edit /></el-icon>
            <span>题目管理</span>
          </el-menu-item>
          <el-menu-item index="/teacher/students">
            <el-icon><User /></el-icon>
            <span>学生管理</span>
          </el-menu-item>
          <el-menu-item index="/teacher/scores">
            <el-icon><Trophy /></el-icon>
            <span>成绩管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>

    <ChangePassword v-model="showChangePwd" />
  </el-container>
</template>

<script setup>
/** 教师端布局 — 顶部导航 + 侧边栏（课程/题目/学生/成绩管理） */
// TODO: 与 AdminLayout.vue 脚本部分完全相同（>90%重复），建议抽取为通用布局组件
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import ChangePassword from '../components/ChangePassword.vue'
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const user = authStore.user
const activeMenu = computed(() => route.path)
const showChangePwd = ref(false)
function handleLogout() { authStore.logout(); router.push('/login') }
onMounted(async () => {
  await authStore.fetchUser()
})
</script>

<style scoped>
.layout { height: 100vh; }
.header {
  display: flex; align-items: center; justify-content: space-between;
  background: #11998e;
  padding: 0 24px; height: 56px; color: #fff;
  box-shadow: 0 2px 8px rgba(17,153,142,.25);
}
.header-left, .header-right { display: flex; align-items: center; gap: 12px; color: #fff; }
.logo { font-size: 17px; font-weight: 700; color: #fff; }
.header-right .el-avatar { box-shadow: 0 0 0 2px rgba(255,255,255,.3); }
.aside {
  background: #fff; border-right: 1px solid #ebeef5;
  box-shadow: 2px 0 8px rgba(0,0,0,.04);
}
.side-menu { border-right: none; height: 100%; background: transparent; padding-top: 8px; font-size: 16px; }
.side-menu :deep(.el-menu-item) { font-size: 16px; height: 52px; line-height: 52px; }
.content { padding: 24px; background: #f5f7fa; }
</style>
