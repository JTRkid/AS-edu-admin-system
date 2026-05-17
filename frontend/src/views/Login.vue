<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>教学平台</h1>
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
      <div class="login-footer">
        <el-link type="primary" :underline="false" @click="showResetDialog = true">忘记密码？</el-link>
      </div>
    </div>

    <!-- 找回密码 -->
    <el-dialog v-model="showResetDialog" title="找回密码" width="420px" :close-on-click-modal="false">
      <el-form :model="resetForm" :rules="resetRules" ref="resetFormRef" label-width="80px">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="resetForm.phone" placeholder="请输入绑定的手机号" />
        </el-form-item>
        <el-form-item label="验证码">
          <div style="display:flex;gap:10px">
            <el-input v-model="resetForm.verifyCode" placeholder="验证码" />
            <el-button :disabled="codeCooldown > 0" @click="sendCode">
              {{ codeCooldown > 0 ? `${codeCooldown}s` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="resetForm.newPassword" type="password" placeholder="新密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="resetForm.confirmPassword" type="password" placeholder="确认密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showResetDialog = false">取消</el-button>
        <el-button type="primary" :loading="resetLoading" @click="handleReset">重置密码</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { authAPI } from '../api'

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

const showResetDialog = ref(false)
const resetLoading = ref(false)
const codeCooldown = ref(0)
const resetForm = reactive({ phone: '', verifyCode: '', newPassword: '', confirmPassword: '' })
const resetRules = {
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }, { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }],
  newPassword: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: (r, v, cb) => v !== resetForm.newPassword ? cb(new Error('两次密码不一致')) : cb(), trigger: 'blur' },
  ],
}

async function sendCode() {
  if (!resetForm.phone) return ElMessage.warning('请先输入手机号')
  try {
    await authAPI.sendVerifyCode({ phone: resetForm.phone })
    ElMessage.success('验证码已发送（开发模式：123456）')
    codeCooldown.value = 60
    const t = setInterval(() => { codeCooldown.value--; if (codeCooldown.value <= 0) clearInterval(t) }, 1000)
  } catch (e) { ElMessage.error('发送失败') }
}

const resetFormRef = ref(null)
async function handleReset() {
  const valid = await resetFormRef.value.validate().catch(() => false)
  if (!valid) return
  resetLoading.value = true
  try {
    await authAPI.resetPassword(resetForm)
    ElMessage.success('密码重置成功，请登录')
    showResetDialog.value = false
  } catch (e) { ElMessage.error(e?.response?.data?.message || '重置失败') }
  finally { resetLoading.value = false }
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
.login-footer { text-align: right; margin-top: 4px; }
</style>
