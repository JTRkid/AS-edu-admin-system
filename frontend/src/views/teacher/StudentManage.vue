<template>
  <div class="student-manage">
    <div class="toolbar">
      <el-button type="primary" @click="openAdd">添加学生</el-button>
      <el-upload :show-file-list="false" :before-upload="handleImport" accept=".xlsx,.xls" style="display:inline-block;margin-left:8px">
        <el-button>导入Excel</el-button>
      </el-upload>
      <el-button @click="downloadTemplate" style="margin-left:8px">下载导入模板</el-button>
      <el-button @click="exportStudents" style="margin-left:8px">导出学生名单</el-button>
    </div>

    <div class="search-bar">
      <el-input v-model="searchKey" placeholder="搜索学号/姓名/班级" prefix-icon="Search" clearable style="width:300px" @input="searchStudents" />
      <el-select v-model="filterClass" placeholder="班级筛选" clearable style="width:160px;margin-left:10px" @change="loadStudents">
        <el-option v-for="cls in classList" :key="cls" :value="cls" />
      </el-select>
    </div>

    <el-table :data="students" border stripe v-loading="loading" class="table">
      <el-table-column prop="student_no" label="学号" sortable width="140" />
      <el-table-column prop="name" label="姓名" sortable width="120" />
      <el-table-column prop="class_name" label="班级" sortable width="140" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.user?.is_active ? 'success' : 'danger'" size="small">
            {{ row.user?.is_active ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="220">
        <template #default="{ row }">
          <el-button size="small" @click="editStudent(row)">编辑</el-button>
          <el-button size="small" type="warning" @click="resetPwd(row.user_id)">重置密码</el-button>
          <el-button size="small" type="danger" @click="deleteStudent(row.user_id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-if="total > 20"
      v-model:current-page="page" :total="total" :page-size="20"
      layout="prev, pager, next" @current-change="loadStudents" class="pagination"
    />

    <el-dialog v-model="showDialog" :title="editing ? '编辑学生' : '添加学生'" width="420px">
      <el-form :model="form" label-width="80px" :rules="formRules" ref="formRef">
        <el-form-item label="学号" prop="student_no">
          <el-input v-model="form.student_no" maxlength="13" placeholder="13位数字" />
        </el-form-item>
        <el-form-item label="姓名" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="班级号" prop="class_name">
          <el-input v-model="form.class_name" maxlength="9" placeholder="9位数字" />
        </el-form-item>
        <el-form-item label="密码" prop="password"><el-input v-model="form.password" show-password /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveStudent" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { studentAPI, extractList, extractCount, downloadFile } from '../../api'

const students = ref([])
const loading = ref(false)
const saving = ref(false)
const page = ref(1)
const total = ref(0)
const searchKey = ref('')
const filterClass = ref('')
const classList = ref([])
const showDialog = ref(false)
const editing = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const form = reactive({ student_no: '', name: '', class_name: '', password: '123456' })
const formRules = {
  student_no: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { pattern: /^\d{13}$/, message: '学号必须为13位数字', trigger: 'blur' },
  ],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  class_name: [
    { required: true, message: '请输入班级号', trigger: 'blur' },
    { pattern: /^\d{9}$/, message: '班级号必须为9位数字', trigger: 'blur' },
  ],
  password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }],
}
let searchTimer = null

async function loadStudents() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (searchKey.value) params.search = searchKey.value
    if (filterClass.value) params.class_name = filterClass.value
    const res = await studentAPI.list(params)
    students.value = extractList(res)
    total.value = extractCount(res)
    const classes = new Set(students.value.map(s => s.class_name))
    classList.value = [...classes]
  } catch (e) {
    ElMessage.error('加载学生列表失败: ' + (e?.response?.data?.message || e?.message || ''))
  } finally { loading.value = false }
}

function searchStudents() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; loadStudents() }, 300)
}

function openAdd() {
  editing.value = false; editingId.value = null
  Object.assign(form, { student_no: '', name: '', class_name: '', password: '123456' })
  formRef.value?.resetFields()
  showDialog.value = true
}

function editStudent(row) {
  editing.value = true; editingId.value = row.user_id
  Object.assign(form, { student_no: row.student_no, name: row.name, class_name: row.class_name, password: '' })
  formRef.value?.resetFields()
  showDialog.value = true
}

async function saveStudent() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (editing.value) {
      await studentAPI.update(editingId.value, form)
    } else {
      await studentAPI.create(form)
    }
    ElMessage.success(editing.value ? '更新成功' : '添加成功')
    showDialog.value = false
    loadStudents()
  } catch (e) {
    const msg = e?.response?.data?.message || e?.response?.data?.student_no?.[0] || '操作失败'
    ElMessage.error(msg)
  } finally { saving.value = false }
}

async function resetPwd(userId) {
  try {
    await ElMessageBox.confirm('确定重置该学生密码为 123456？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    await studentAPI.resetPassword(userId, { password: '123456' })
    ElMessage.success('密码已重置')
  } catch (e) { /* cancelled */ }
}

async function deleteStudent(userId) {
  try {
    await ElMessageBox.confirm('确定删除该学生？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    await studentAPI.delete(userId)
    ElMessage.success('已删除')
    loadStudents()
  } catch (e) { /* cancelled */ }
}

async function handleImport(file) {
  try {
    const res = await studentAPI.batchImport(file)
    const { created, errors } = res.data || res
    let msg = `导入完成，成功${created}条`
    if (errors && errors.length > 0) {
      msg += `，${errors.length}条错误`
      ElMessage.warning(msg)
      if (errors.length <= 5) {
        errors.forEach(e => ElMessage.error(e))
      } else {
        errors.slice(0, 5).forEach(e => ElMessage.error(e))
        ElMessage.error(`还有${errors.length - 5}条错误...`)
      }
    } else {
      ElMessage.success(msg)
    }
    loadStudents()
  } catch (e) { ElMessage.error('导入失败: ' + (e?.response?.data?.message || '')) }
  return false
}

async function downloadTemplate() {
  try { await downloadFile('/auth/students/download_template/', 'student_template.xlsx') } catch (e) { ElMessage.error('下载失败') }
}

async function exportStudents() {
  try { await downloadFile('/auth/students/export_excel/', 'students.xlsx') } catch (e) { ElMessage.error('导出失败') }
}

onMounted(loadStudents)
</script>

<style scoped>
.student-manage { max-width: 1100px; margin: 0 auto; }
.toolbar { margin-bottom: 16px; display: flex; align-items: center; }
.search-bar { display: flex; margin-bottom: 16px; }
.table { width: 100%; }
.pagination { margin-top: 16px; text-align: center; }
</style>
