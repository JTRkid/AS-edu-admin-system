<template>
  <div class="login-container">
    <div class="login-bg"></div>
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="40"><School /></el-icon>
        </div>
        <h1>AS-edu-system</h1>
        <p>在线教学管理系统</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" class="login-form" @submit.prevent="handleLogin">
        <el-form-item prop="account">
          <el-input
            v-model="form.account"
            placeholder="请输入学号或教师号"
            prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="rememberMe" style="float:left">记住账号</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleLogin" class="login-btn">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
/** 登录页 — 学号/教师号登录、记住账号 */
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const rememberMe = ref(false)
const form = reactive({ account: '', password: '' })
const rules = {
  account: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

// 加载记住的账号
function loadSavedCredentials() {
  try {
    const saved = localStorage.getItem('saved_account')
    if (saved) {
      form.account = saved
      rememberMe.value = true
    }
  } catch (e) { /* ignore */ }
}

onMounted(async () => {
  await nextTick()
  loadSavedCredentials()
})

async function handleLogin() {
  loading.value = true
  try {
    const data = await authStore.login(form.account, form.password)
    // 记住账号
    if (rememberMe.value) {
      localStorage.setItem('saved_account', form.account)
    } else {
      localStorage.removeItem('saved_account')
    }
    ElMessage.success('登录成功')
    const role = data.user.role
    if (role === 'student') router.push('/student')
    else if (role === 'teacher') router.push('/teacher')
    else if (role === 'admin') router.push('/admin')
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || e?.response?.data?.non_field_errors?.[0] || '登录失败')
  } finally {
    loading.value = false
  }
}

</script>

<style scoped>
.login-container {
  height: 100vh; display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  background:
    #f5f7fa,
    linear-gradient(0deg, rgba(225,233,245,.3) 1px, transparent 1px),
    linear-gradient(90deg, rgba(225,233,245,.3) 1px, transparent 1px);
  background-size: 24px 24px;
}
.login-bg {
  position: absolute; inset: 0;
  background:
    radial-gradient(circle at 0% 0%, rgba(255,214,208,.4) 0%, transparent 38%),
    radial-gradient(circle at 100% 100%, rgba(255,232,212,.4) 0%, transparent 38%),
    radial-gradient(circle at 0% 100%, rgba(199,236,255,.4) 0%, transparent 38%),
    radial-gradient(circle at 100% 0%, rgba(199,236,255,.4) 0%, transparent 38%);
}
.login-card {
  width: 420px; background: rgba(255,255,255,.72); border-radius: 24px;
  padding: 48px 44px 40px; position: relative; z-index: 1;
  box-shadow: 0 8px 32px rgba(0,0,0,.08);
  animation: scaleIn .5s ease-out;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,.25);
}
.login-header { text-align: center; margin-bottom: 36px; }
.logo-icon {
  width: 64px; height: 64px; border-radius: 16px;
  background: #7cb9e8;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px; color: #fff;
  animation: pulse 2s ease-in-out infinite;
}
.login-header h1 { font-size: 24px; color: #303133; font-weight: 700; margin-bottom: 6px; }
.login-header p { font-size: 14px; color: #909399; }
.login-form { margin-top: 8px; }
.login-btn {
  width: 100%; height: 46px; font-size: 16px; letter-spacing: 6px;
  background: #7cb9e8; border: none;
  color: #fff;
  transition: all .3s ease;
}
.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(124,185,232,.45);
}

</style>
