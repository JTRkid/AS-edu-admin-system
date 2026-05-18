<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
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
  background: #f0f2f5;
}
.login-card {
  width: 400px; background: #fff; border-radius: 12px; padding: 48px 40px 36px;
  box-shadow: 0 2px 12px rgba(0,0,0,.06);
}
.login-header { text-align: center; margin-bottom: 36px; }
.login-header h1 { font-size: 26px; color: #303133; font-weight: 600; margin-bottom: 8px; }
.login-header p { font-size: 14px; color: #909399; }
.login-form { margin-top: 8px; }
.login-btn { width: 100%; height: 44px; font-size: 16px; letter-spacing: 4px; }

</style>
