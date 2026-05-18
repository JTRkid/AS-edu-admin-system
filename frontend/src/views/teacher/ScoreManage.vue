<template>
  <div class="score-manage">
    <!-- Score type tabs -->
    <div class="score-type-tabs">
      <el-radio-group v-model="scoreType" @change="onScoreTypeChange" size="default">
        <el-radio-button value="regular">总成绩</el-radio-button>
        <el-radio-button value="experiment">实验成绩</el-radio-button>
      </el-radio-group>
    </div>

    <div class="toolbar">
      <el-button type="primary" @click="openAdd">添加成绩</el-button>
      <el-button @click="exportScores">导出Excel</el-button>
      <el-button @click="downloadTemplate">下载导入模板</el-button>
      <el-upload :show-file-list="false" :before-upload="handleImport" accept=".xlsx,.xls" style="display:inline-block;margin-left:8px">
        <el-button>导入Excel修改</el-button>
      </el-upload>
    </div>

    <!-- Section tabs for filtering -->
    <div class="chapter-tabs" v-if="sectionTabs.length > 0">
      <el-button
        v-for="sec in sectionTabs"
        :key="sec.section_id"
        :type="filterSection === sec.section_id ? 'primary' : ''"
        size="small"
        @click="onSectionClick(sec.section_id)"
      >
        第{{ sec.chapter_no }}章 {{ sec.section_no }}节 {{ sec.section_name }}
        <el-badge :value="sec.count" :hidden="sec.count === 0" style="margin-left:4px" />
      </el-button>
      <el-button v-if="filterSection" size="small" @click="onSectionClick(null)">全部</el-button>
    </div>

    <div class="search-bar">
      <el-input v-model="searchKey" placeholder="搜索学号" prefix-icon="Search" clearable style="width:200px" @input="searchScores" />
      <el-input v-model="searchName" placeholder="搜索姓名" prefix-icon="Search" clearable style="width:160px;margin-left:10px" @input="searchScores" />
    </div>

    <el-table :data="scores" border stripe v-loading="loading" class="table" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="45" />
      <el-table-column prop="student_no" label="学号" sortable width="140" />
      <el-table-column prop="student_name" label="姓名" sortable width="100" />
      <el-table-column prop="class_name" label="班级" sortable width="120" />
      <el-table-column label="章节" width="220">
        <template #default="{ row }">
          第{{ row.chapter_no }}章 {{ row.chapter_name }} / {{ row.section_no }} {{ row.section_name }}
        </template>
      </el-table-column>
      <el-table-column prop="score" label="成绩" sortable width="90" />
      <el-table-column prop="source" label="来源" width="100">
        <template #default="{ row }">
          <el-tag :type="row.source==='auto_script'?'':row.source==='manual'?'warning':row.source==='experiment'?'success':'info'" size="small">
            {{ sourceMap[row.source] || row.source }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openModify(row)">修改</el-button>
          <el-button size="small" type="danger" @click="deleteScore(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-if="total > 20"
      v-model:current-page="page" :total="total" :page-size="20"
      layout="prev, pager, next" @current-change="loadScores" class="pagination"
    />

    <!-- Batch delete -->
    <div v-if="selectedScores.length > 0" class="batch-bar">
      <span>已选{{ selectedScores.length }}条</span>
      <el-button type="danger" size="small" @click="batchDelete">批量删除</el-button>
    </div>

    <!-- Add Score Dialog -->
    <el-dialog v-model="showAddDialog" title="添加成绩" width="480px">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="成绩类型">
          <el-radio-group v-model="addForm.score_type">
            <el-radio value="regular">总成绩</el-radio>
            <el-radio value="experiment">实验成绩</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="学生">
          <el-select v-model="addForm.student_id" filterable placeholder="搜索学号或姓名" style="width:100%">
            <el-option v-for="s in studentList" :key="s.user_id" :label="`${s.student_no} ${s.name} (${s.class_name})`" :value="s.user_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="节">
          <el-select v-model="addForm.section_id" filterable placeholder="选择节" style="width:100%">
            <el-option v-for="s in sectionList" :key="s.id" :label="`第${s.chapter_no}章 ${s.section_no} ${s.title}`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="成绩">
          <el-input-number v-model="addForm.score" :min="0" :max="100" :precision="1" />
        </el-form-item>
        <el-form-item label="评分详情">
          <el-input v-model="addForm.details" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveAddScore" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- Modify Score Dialog -->
    <el-dialog v-model="showModifyDialog" title="修改成绩" width="400px">
      <el-form label-width="80px">
        <el-form-item label="学生">{{ currentScore?.student_name }} ({{ currentScore?.student_no }})</el-form-item>
        <el-form-item label="当前成绩">{{ currentScore?.score }}</el-form-item>
        <el-form-item label="新成绩">
          <el-input-number v-model="newScore" :min="0" :max="100" :precision="1" />
        </el-form-item>
        <el-form-item label="修改原因"><el-input v-model="modifyReason" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showModifyDialog = false">取消</el-button>
        <el-button type="primary" @click="saveModify">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/** 成绩管理页 — 总成绩/实验成绩切换、手动录入、Excel导入导出、修改审计 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { scoreAPI, studentAPI, sectionAPI, extractList, extractCount, downloadFile } from '../../api'

const scores = ref([])
const loading = ref(false)
const saving = ref(false)
const page = ref(1)
const total = ref(0)
const searchKey = ref('')
const searchName = ref('')
const filterSection = ref(null)
const sectionTabs = ref([])
const selectedScores = ref([])
const scoreType = ref('regular')

const showAddDialog = ref(false)
const studentList = ref([])
const sectionList = ref([])
const addForm = reactive({ student_id: null, section_id: null, score: 0, details: '', score_type: 'regular' })

const showModifyDialog = ref(false)
const currentScore = ref(null)
const newScore = ref(0)
const modifyReason = ref('')

const sourceMap = { auto_script: '自动评分', manual: '手动录入', import: 'Excel导入', experiment: '实验成绩' }
let searchTimer = null

async function loadScores() {
  loading.value = true
  try {
    const params = { page: page.value, score_type: scoreType.value }
    if (searchKey.value) params.search = searchKey.value
    if (searchName.value) params.student_name = searchName.value
    if (filterSection.value) params.section = filterSection.value
    const res = await scoreAPI.list(params)
    scores.value = extractList(res)
    total.value = extractCount(res)
  } catch (e) { ElMessage.error('加载成绩失败') }
  finally { loading.value = false }
}

async function loadSectionTabs() {
  try {
    const res = await scoreAPI.list({ score_type: scoreType.value })
    const all = extractList(res)
    const map = new Map()
    for (const s of all) {
      const key = s.section
      if (!map.has(key)) {
        map.set(key, {
          section_id: s.section,
          chapter_no: s.chapter_no,
          section_no: s.section_no,
          section_name: s.section_name,
          count: 0,
        })
      }
      map.get(key).count++
    }
    sectionTabs.value = [...map.values()].sort((a, b) => a.chapter_no - b.chapter_no || a.section_no - b.section_no)
  } catch (e) { /* ignore */ }
}

function onScoreTypeChange() {
  filterSection.value = null
  page.value = 1
  loadScores()
  loadSectionTabs()
}

function onSectionClick(sectionId) {
  filterSection.value = sectionId
  page.value = 1
  loadScores()
}

function searchScores() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; loadScores() }, 300)
}

function onSelectionChange(selection) { selectedScores.value = selection }

async function batchDelete() {
  try {
    await ElMessageBox.confirm(`确定删除选中的${selectedScores.value.length}条成绩？`, '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    for (const s of selectedScores.value) {
      await scoreAPI.delete(s.id)
    }
    ElMessage.success('已删除')
    selectedScores.value = []
    loadScores()
    loadSectionTabs()
  } catch (e) { /* cancelled */ }
}

async function openAdd() {
  showAddDialog.value = true
  Object.assign(addForm, { student_id: null, section_id: null, score: 0, details: '', score_type: 'regular' })
  try {
    const [stuRes, secRes] = await Promise.all([
      studentAPI.list({}),
      sectionAPI.list({}),
    ])
    studentList.value = extractList(stuRes)
    sectionList.value = extractList(secRes)
  } catch (e) { ElMessage.error('加载选项失败') }
}

async function saveAddScore() {
  if (!addForm.student_id || !addForm.section_id) {
    return ElMessage.warning('请选择学生和节')
  }
  saving.value = true
  try {
    const student = studentList.value.find(s => s.user_id === addForm.student_id)
    const section = sectionList.value.find(s => s.id === addForm.section_id)
    await scoreAPI.create({
      student: addForm.student_id,
      student_no: student?.student_no || '',
      student_name: student?.name || '',
      class_name: student?.class_name || '',
      section: addForm.section_id,
      chapter_no: section?.chapter_no || 0,
      section_no: section?.section_no || 0,
      chapter_name: section?.chapter_title || '',
      section_name: section?.title || '',
      score: addForm.score,
      score_type: addForm.score_type,
      source: 'manual',
      evaluator: '教师手动录入',
      details: addForm.details,
    })
    ElMessage.success('成绩添加成功')
    showAddDialog.value = false
    loadScores()
    loadSectionTabs()
  } catch (e) {
    ElMessage.error('添加失败: ' + (e?.response?.data?.message || e?.response?.data?.detail || ''))
  } finally { saving.value = false }
}

function openModify(row) { currentScore.value = row; newScore.value = Number(row.score); modifyReason.value = ''; showModifyDialog.value = true }

async function saveModify() {
  if (!currentScore.value) return
  try {
    await scoreAPI.modify(currentScore.value.id, { score: newScore.value, reason: modifyReason.value })
    ElMessage.success('成绩已修改')
    showModifyDialog.value = false
    loadScores()
  } catch (e) { ElMessage.error('修改失败') }
}

async function deleteScore(id) {
  try {
    await ElMessageBox.confirm('确定删除该成绩记录？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    await scoreAPI.delete(id)
    ElMessage.success('已删除')
    loadScores()
    loadSectionTabs()
  } catch (e) { /* cancelled */ }
}

async function exportScores() {
  try { await downloadFile(`/scores/export_excel/?score_type=${scoreType.value}`, 'scores.xlsx') } catch (e) { ElMessage.error('导出失败') }
}

function downloadTemplate() {
  try { downloadFile('/scores/download_template/', 'score_template.xlsx') } catch (e) { ElMessage.error('下载失败') }
}

async function handleImport(file) {
  try {
    const res = await scoreAPI.importExcel(file)
    const data = res.data || res
    const msg = `导入完成，新增${data.created || 0}条，更新${data.updated || 0}条`
    ElMessage.success(msg)
    if (data.errors && data.errors.length > 0) {
      data.errors.slice(0, 3).forEach(e => ElMessage.warning(e))
    }
    loadScores()
    loadSectionTabs()
  } catch (e) { ElMessage.error('导入失败: ' + (e?.response?.data?.message || '')) }
  return false
}

onMounted(() => { loadScores(); loadSectionTabs() })
</script>

<style scoped>
.score-manage { max-width: 1200px; margin: 0 auto; }
.score-type-tabs { margin-bottom: 16px; }
.toolbar { margin-bottom: 16px; display: flex; gap: 8px; flex-wrap: wrap; }
.chapter-tabs { margin-bottom: 14px; display: flex; gap: 8px; flex-wrap: wrap; }
.search-bar { display: flex; margin-bottom: 16px; }
.table { width: 100%; }
.pagination { margin-top: 16px; text-align: center; }
.batch-bar { margin-top: 12px; padding: 8px 16px; background: #f0f9eb; border-radius: 6px; display: flex; align-items: center; gap: 12px; }
</style>
