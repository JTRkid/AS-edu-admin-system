<template>
  <div class="log-manage">
    <el-table :data="logs" border stripe v-loading="loading" class="table">
      <el-table-column prop="user_name" label="操作人" width="100" />
      <el-table-column prop="action" label="操作类型" width="120" />
      <el-table-column prop="target" label="操作对象" width="160" />
      <el-table-column prop="detail" label="详情" min-width="200" />
      <el-table-column prop="ip_address" label="IP地址" width="140" />
      <el-table-column prop="created_at" label="操作时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
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
  </div>
</template>

<script setup>
/** 操作日志页 — 分页展示管理员/教师操作记录 */
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
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

onMounted(loadLogs)
</script>

<style scoped>
.log-manage { max-width: 1100px; margin: 0 auto; }
.table { width: 100%; }
.pagination { margin-top: 16px; text-align: center; }
</style>
