<template>
  <div class="teacher-manage">
    <div class="toolbar">
      <el-button type="primary" @click="showAddDialog = true">添加教师</el-button>
    </div>

    <div class="search-bar">
      <el-input
        v-model="searchKey"
        placeholder="搜索教师号/姓名/部门"
        prefix-icon="Search"
        clearable
        style="width: 300px"
        @input="search"
      />
    </div>

    <el-table :data="teachers" border stripe v-loading="loading" class="table">
      <el-table-column prop="teacher_no" label="教师号" sortable width="120" />
      <el-table-column prop="name" label="姓名" sortable width="100" />
      <el-table-column prop="department" label="部门" width="120" />
      <el-table-column label="管理员" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small">
            {{ row.is_admin ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.user?.is_active ? 'success' : 'danger'" size="small">
            {{ row.user?.is_active ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="280">
        <template #default="{ row }">
          <el-button v-if="!row.is_admin" size="small" type="success" @click="setAdmin(row)">设为管理员</el-button>
          <el-button v-else size="small" type="warning" @click="revokeAdmin(row)">撤销管理员</el-button>
          <el-button size="small" @click="resetPwd(row.user_id)">重置密码</el-button>
          <el-button size="small" :type="row.user?.is_active ? 'danger' : 'success'" @click="toggleActive(row)">
            {{ row.user?.is_active ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-if="total > 20"
      v-model:current-page="page"
      :total="total"
      :page-size="20"
      layout="prev, pager, next"
      @current-change="loadTeachers"
      class="pagination"
    />

    <!-- Add Teacher Dialog -->
    <el-dialog v-model="showAddDialog" title="添加教师" width="420px">
      <el-form :model="teacherForm" label-width="80px">
        <el-form-item label="教师号">
          <el-input v-model="teacherForm.teacher_no" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="teacherForm.name" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="teacherForm.department" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="teacherForm.password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTeacher">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/** 教师管理页 — 教师CRUD、管理员任命/撤销、账号启停、密码重置 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { teacherAPI, extractList, extractCount } from '../../api'

const teachers = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const searchKey = ref('')

const showAddDialog = ref(false)
const teacherForm = reactive({ teacher_no: '', name: '', department: '', password: '123456' })

let searchTimer = null

async function loadTeachers() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (searchKey.value) params.search = searchKey.value
    const res = await teacherAPI.list(params)
    teachers.value = extractList(res)
    total.value = extractCount(res)
  } catch (e) {
    ElMessage.error('加载教师列表失败')
  } finally {
    loading.value = false
  }
}

function search() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; loadTeachers() }, 300)
}

async function saveTeacher() {
  try {
    await teacherAPI.create(teacherForm)
    ElMessage.success('添加成功')
    showAddDialog.value = false
    Object.assign(teacherForm, { teacher_no: '', name: '', department: '', password: '123456' })
    loadTeachers()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

async function setAdmin(row) {
  try {
    await ElMessageBox.confirm('确定将此教师设为管理员？', '确认', { type: 'warning' })
    await teacherAPI.setAdmin(row.user_id)
    ElMessage.success('已设为管理员')
    loadTeachers()
  } catch (e) { /* cancelled */ }
}

async function revokeAdmin(row) {
  try {
    await ElMessageBox.confirm('确定撤销此教师的管理员身份？', '确认', { type: 'warning' })
    await teacherAPI.revokeAdmin(row.user_id)
    ElMessage.success('已撤销管理员')
    loadTeachers()
  } catch (e) { /* cancelled */ }
}

async function toggleActive(row) {
  try {
    await teacherAPI.toggleActive(row.user_id)
    ElMessage.success('状态已切换')
    loadTeachers()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function resetPwd(userId) {
  try {
    await ElMessageBox.confirm('确定重置密码为 123456？', '确认', { type: 'warning' })
    await teacherAPI.resetPassword(userId, { password: '123456' })
    ElMessage.success('密码已重置')
  } catch (e) { /* cancelled */ }
}

onMounted(loadTeachers)
</script>

<style scoped>
.teacher-manage { max-width: 960px; margin: 0 auto; }
.toolbar { margin-bottom: 16px; }
.search-bar { margin-bottom: 16px; }
.table { width: 100%; }
.pagination { margin-top: 16px; text-align: center; }
</style>
