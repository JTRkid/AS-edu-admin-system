<template>
  <div class="my-scores">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>我的成绩</span>
          <el-button size="small" @click="loadScores" :loading="loading">刷新</el-button>
        </div>
      </template>
      <el-table :data="scores" stripe v-loading="loading" empty-text="暂无成绩">
        <el-table-column prop="chapter_no" label="章" width="60" />
        <el-table-column prop="chapter_name" label="章名" min-width="120" />
        <el-table-column prop="section_no" label="节" width="60" />
        <el-table-column prop="section_name" label="节名" min-width="120" />
        <el-table-column prop="score" label="成绩" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.score >= 60 ? '#67c23a' : '#f56c6c', fontWeight: 600 }">
              {{ row.score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="score_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.score_type === 'experiment' ? 'warning' : 'primary'" size="small">
              {{ row.score_type === 'experiment' ? '实验' : '总成绩' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="sourceTag(row.source)">{{ sourceMap[row.source] || row.source }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="evaluator" label="评分方" width="120" />
        <el-table-column label="提交时间" width="170">
          <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
/** 学生端我的成绩 — 查看本人所有课程节对应的成绩 */
import { ref, onMounted } from 'vue'
import { scoreAPI, extractList } from '../../api'
import { sourceMap, formatTime } from '../../utils/constants'

const scores = ref([])
const loading = ref(false)

async function loadScores() {
  loading.value = true
  try {
    const res = await scoreAPI.myScores()
    scores.value = extractList(res)
  } catch (e) {
    console.error('加载成绩失败', e)
  } finally {
    loading.value = false
  }
}

function sourceTag(source) {
  const map = { auto_script: 'success', manual: '', import: 'warning', experiment: 'danger' }
  return map[source] || ''
}

onMounted(loadScores)
</script>

<style scoped>
.my-scores { max-width: 1100px; margin: 0 auto; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.score-green { color: #67c23a; font-weight: 700; font-size: 15px; }
.score-red { color: #f56c6c; font-weight: 700; font-size: 15px; }
</style>
