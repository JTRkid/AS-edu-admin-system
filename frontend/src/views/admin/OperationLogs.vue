<template>
  <div class="log-manage">
    <div class="page-header">
      <h3 class="page-title">操作日志</h3>
      <el-button size="small" @click="loadLogs" :loading="loading">
        <el-icon style="margin-right:4px"><Refresh /></el-icon>刷新
      </el-button>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table :data="logs" stripe v-loading="loading" class="table">
        <el-table-column prop="user_name" label="操作人" width="100">
          <template #default="{ row }">
            <span class="user-cell">{{ row.user_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作类型" width="120">
          <template #default="{ row }">
            <el-tag :type="actionTag(row.action)" size="small" effect="dark">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="操作对象" width="160" />
        <el-table-column prop="detail" label="详情" min-width="200">
          <template #default="{ row }">
            <span class="detail-text">{{ row.detail || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="140">
          <template #default="{ row }">
            <code class="ip-code">{{ row.ip_address }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            <span class="time-cell">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="total > 20"
        v-model:current-page="page"
        :total="total"
        :page-size="20"
        layout="prev, pager, next"
        @current-change="loadLogs"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
/** 操作日志页 — 分页展示管理员/教师操作记录 */
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import api, { extractList, extractCount } from '../../api'
import { formatTime } from '../../utils/constants'

const logs = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)

async function loadLogs() {
  loading.value = true
  try {
    const res = await api.get('/auth/logs/', { params: { page: page.value } })
    logs.value = extractList(res)
    total.value = extractCount(res)
  } catch (e) {
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

function actionTag(action) {
  const map = { '创建': 'success', '删除': 'danger', '修改': 'warning', '登录': '', '导入': 'success', '导出': '' }
  return map[action] || 'info'
}

onMounted(loadLogs)
</script>

<style scoped>
.log-manage { max-width: 1100px; margin: 0 auto; animation: pageIn .4s ease; }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 18px;
}
.page-title {
  font-size: 18px; font-weight: 700;
  color: #1a1a2e;
}
.table-card {
  border-radius: 12px; overflow: hidden;
  animation: slideUp .5s ease;
}
.table { width: 100%; }
.pagination { margin-top: 18px; text-align: center; }

.user-cell { font-weight: 500; color: #303133; }
.detail-text { color: #606266; }
.ip-code {
  padding: 2px 6px; background: #f5f7fa; border-radius: 4px;
  font-size: 12px; color: #909399;
}
.time-cell { color: #909399; font-size: 13px; }
</style>
