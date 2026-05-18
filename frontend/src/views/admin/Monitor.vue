<template>
  <div class="monitor">
    <h3 class="page-title">系统服务状态</h3>
    <el-row :gutter="16" class="status-cards">
      <el-col :span="8" v-for="(svc, i) in services" :key="svc.name">
        <el-card shadow="hover" class="status-card" :style="{ animationDelay: i * 0.1 + 's' }">
          <div class="card-inner">
            <div class="icon-wrap">
              <el-icon :size="32"><CircleCheckFilled /></el-icon>
            </div>
            <div class="card-text">
              <div class="card-title">{{ svc.name }}</div>
              <div class="card-status online">{{ svc.desc }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="stats-row">
      <el-col :span="8" v-for="(group, gi) in statGroups" :key="gi">
        <el-card shadow="hover" class="stat-card" :style="{ animationDelay: (gi + 3) * 0.1 + 's' }">
          <template #header>
            <div class="stat-header"><span>{{ group.title }}</span><div class="header-line" /></div>
          </template>
          <div class="stat-item" v-for="(item, si) in group.items" :key="si" :style="{ animationDelay: (gi * 3 + si) * 0.08 + 's' }">
            <span class="stat-label">{{ item.label }}</span>
            <span class="stat-value">{{ stats[item.key] }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="error-log">
      <template #header>
        <div class="log-header"><span>系统日志</span><el-button size="small" type="primary" @click="refreshLogs" :loading="logLoading">刷新</el-button></div>
      </template>
      <el-timeline v-if="logs.length > 0">
        <el-timeline-item
          v-for="(log, i) in logs" :key="log.id"
          :timestamp="formatTime(log.created_at)" placement="top"
          :color="logColors[i % logColors.length]"
          :style="{ animationDelay: i * 0.05 + 's' }"
          class="log-item"
        >
          <span class="log-user">{{ log.user_name }}</span>
          <span class="log-action">{{ log.action }}</span>
          <span class="log-target">{{ log.target }}</span>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无日志" :image-size="60" />
    </el-card>
  </div>
</template>

<script setup>
/** 管理员仪表盘 — 系统状态概览、各模块数据统计、最近操作日志 */
import { ref, reactive, onMounted } from 'vue'
import api, { extractCount, extractList } from '../../api'
import { formatTime } from '../../utils/constants'

const stats = reactive({ students: 0, teachers: 0, admins: 0, courses: 0, chapters: 0, sections: 0, scores: 0, submissions: 0, documents: 0 })
const logs = ref([])
const logLoading = ref(false)

const services = [
  { name: '数据库 MySQL', desc: '运行正常' },
  { name: 'Django 后端', desc: '运行正常' },
  { name: 'WebSocket 服务', desc: '运行正常' },
]
const statGroups = [
  { title: '用户统计', items: [{ label: '学生总数', key: 'students' }, { label: '教师总数', key: 'teachers' }, { label: '管理员', key: 'admins' }] },
  { title: '课程统计', items: [{ label: '课程总数', key: 'courses' }, { label: '章总数', key: 'chapters' }, { label: '节总数', key: 'sections' }] },
  { title: '成绩与提交', items: [{ label: '成绩记录', key: 'scores' }, { label: '提交记录', key: 'submissions' }, { label: '文档数量', key: 'documents' }] },
]
const logColors = ['#11998e', '#667eea', '#e6a23c', '#67c23a', '#f56c6c', '#409eff']

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
  logLoading.value = true
  try {
    const res = await api.get('/auth/logs/')
    logs.value = extractList(res).slice(0, 10)
  } catch (e) { /* ignore */ }
  finally { logLoading.value = false }
}

onMounted(() => { loadStats(); refreshLogs() })
</script>

<style scoped>
.monitor { max-width: 1100px; margin: 0 auto; }
.page-title {
  margin-bottom: 20px; font-size: 18px; font-weight: 700;
  color: #1a1a2e;
}

/* 服务状态卡片 */
.status-cards { margin-bottom: 20px; }
.status-card {
  border-radius: 12px; transition: all .35s ease;
  animation: slideUp .5s ease both;
  border-top: 3px solid #67c23a;
}
.status-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(103,194,58,.15);
}
.card-inner { display: flex; align-items: center; gap: 18px; padding: 6px 0; }
.icon-wrap {
  width: 56px; height: 56px; border-radius: 14px;
  background: #e1f3d8;
  display: flex; align-items: center; justify-content: center;
  animation: pulse 2.5s ease-in-out infinite;
}
.icon-wrap .el-icon { color: #67c23a; }
.card-title { font-size: 15px; font-weight: 600; color: #303133; }
.card-status { font-size: 13px; margin-top: 4px; }
.card-status.online { color: #67c23a; font-weight: 500; }

/* 统计卡片 */
.stats-row { margin-bottom: 20px; }
.stat-card {
  border-radius: 12px; transition: all .35s ease;
  animation: slideUp .5s ease both;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(26,26,46,.1);
}
.stat-header { position: relative; }
.stat-header span { font-weight: 600; color: #303133; }
.header-line {
  height: 3px; width: 36px; border-radius: 2px;
  background: #1a1a2e;
  margin-top: 6px;
}
.stat-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 4px; border-bottom: 1px solid #f5f5f5;
  animation: slideUp .4s ease both;
  transition: background .2s;
}
.stat-item:last-child { border-bottom: none; }
.stat-item:hover { background: #fafafa; border-radius: 6px; padding-left: 8px; padding-right: 8px; }
.stat-label { color: #909399; font-size: 14px; }
.stat-value {
  color: #1a1a2e; font-size: 20px; font-weight: 700;
  font-variant-numeric: tabular-nums;
}

/* 日志卡片 */
.error-log {
  margin-top: 20px; border-radius: 12px;
  animation: slideUp .5s ease both;
  animation-delay: .3s;
}
.error-log:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,.06);
}
.log-header { display: flex; justify-content: space-between; align-items: center; }
.log-header span { font-weight: 600; }

.log-item {
  animation: slideUp .4s ease both;
}
.log-user { font-weight: 600; color: #303133; }
.log-action {
  display: inline-block; margin: 0 6px; padding: 2px 8px;
  background: #ecf5ff; color: #409eff; border-radius: 4px;
  font-size: 12px;
}
.log-target { color: #909399; }
</style>
