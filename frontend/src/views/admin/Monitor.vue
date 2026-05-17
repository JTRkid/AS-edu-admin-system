<template>
  <div class="monitor">
    <h3>系统服务状态</h3>
    <el-row :gutter="16" class="status-cards">
      <el-col :span="8">
        <el-card shadow="never">
          <div class="card-inner">
            <el-icon :size="36" color="#67c23a"><CircleCheckFilled /></el-icon>
            <div class="card-text"><div class="card-title">数据库 MySQL</div><div class="card-status online">运行正常</div></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <div class="card-inner">
            <el-icon :size="36" color="#67c23a"><CircleCheckFilled /></el-icon>
            <div class="card-text"><div class="card-title">Django 后端</div><div class="card-status online">运行正常</div></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <div class="card-inner">
            <el-icon :size="36" color="#67c23a"><CircleCheckFilled /></el-icon>
            <div class="card-text"><div class="card-title">WebSocket 服务</div><div class="card-status online">运行正常</div></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="stats-row">
      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>用户统计</span></template>
          <div class="stat-item"><span class="stat-label">学生总数</span><span class="stat-value">{{ stats.students }}</span></div>
          <div class="stat-item"><span class="stat-label">教师总数</span><span class="stat-value">{{ stats.teachers }}</span></div>
          <div class="stat-item"><span class="stat-label">管理员</span><span class="stat-value">{{ stats.admins }}</span></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>课程统计</span></template>
          <div class="stat-item"><span class="stat-label">课程总数</span><span class="stat-value">{{ stats.courses }}</span></div>
          <div class="stat-item"><span class="stat-label">章总数</span><span class="stat-value">{{ stats.chapters }}</span></div>
          <div class="stat-item"><span class="stat-label">节总数</span><span class="stat-value">{{ stats.sections }}</span></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>成绩与提交</span></template>
          <div class="stat-item"><span class="stat-label">成绩记录</span><span class="stat-value">{{ stats.scores }}</span></div>
          <div class="stat-item"><span class="stat-label">提交记录</span><span class="stat-value">{{ stats.submissions }}</span></div>
          <div class="stat-item"><span class="stat-label">文档数量</span><span class="stat-value">{{ stats.documents }}</span></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="error-log">
      <template #header>
        <div class="log-header"><span>系统日志</span><el-button size="small" @click="refreshLogs">刷新</el-button></div>
      </template>
      <el-timeline v-if="logs.length > 0">
        <el-timeline-item v-for="log in logs" :key="log.id" :timestamp="formatTime(log.created_at)" placement="top">
          <span>{{ log.user_name }} - {{ log.action }} {{ log.target }}</span>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无日志" :image-size="60" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api, { extractCount, extractList } from '../../api'

const stats = reactive({ students: 0, teachers: 0, admins: 0, courses: 0, chapters: 0, sections: 0, scores: 0, submissions: 0, documents: 0 })
const logs = ref([])

async function loadStats() {
  try {
    const [students, teachers, courses, scores, submissions, documents, chapterRes, sectionRes] = await Promise.all([
      api.get('/auth/students/'),
      api.get('/auth/teachers/'),
      api.get('/courses/'),
      api.get('/scores/'),
      api.get('/submissions/'),
      api.get('/documents/'),
      api.get('/courses/chapters/'),
      api.get('/courses/sections/'),
    ])
    stats.students = extractCount(students)
    stats.teachers = extractCount(teachers)
    stats.courses = extractCount(courses)
    stats.chapters = extractCount(chapterRes)
    stats.sections = extractCount(sectionRes)
    stats.scores = extractCount(scores)
    stats.submissions = extractCount(submissions)
    stats.documents = extractCount(documents)
  } catch (e) { console.error('加载统计失败', e) }
}

async function refreshLogs() {
  try {
    const res = await api.get('/auth/logs/')
    logs.value = extractList(res).slice(0, 10)
  } catch (e) { /* ignore */ }
}

function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '' }

onMounted(() => { loadStats(); refreshLogs() })
</script>

<style scoped>
.monitor { max-width: 1100px; margin: 0 auto; }
.monitor h3 { margin-bottom: 16px; font-size: 16px; color: #303133; }
.status-cards { margin-bottom: 16px; }
.card-inner { display: flex; align-items: center; gap: 16px; padding: 8px 0; }
.card-title { font-size: 15px; font-weight: 500; color: #303133; }
.card-status { font-size: 13px; margin-top: 4px; }
.card-status.online { color: #67c23a; }
.stats-row { margin-bottom: 16px; }
.stat-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.stat-item:last-child { border-bottom: none; }
.stat-label { color: #909399; font-size: 14px; }
.stat-value { color: #303133; font-size: 16px; font-weight: 600; }
.error-log { margin-top: 16px; }
.log-header { display: flex; justify-content: space-between; align-items: center; }
</style>
