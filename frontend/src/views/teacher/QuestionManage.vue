<template>
  <div class="question-manage">
    <div class="toolbar">
      <el-select v-model="filterCourse" placeholder="选择课程" @change="onCourseChange" style="width:200px">
        <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-select v-model="filterSection" placeholder="选择节" @change="onSectionChange" style="width:280px;margin-left:10px">
        <el-option v-for="s in sortedSections" :key="s.id" :label="`第${s.chapter_no}章 ${s.section_no} ${s.title}`" :value="s.id" />
      </el-select>
      <el-button type="primary" @click="openAdd" style="margin-left:10px" :disabled="!filterSection">添加题目</el-button>
      <el-button type="success" @click="openGrading" style="margin-left:10px" :disabled="!filterSection">批改题目</el-button>
    </div>

    <!-- Batch ops + total score row -->
    <div class="batch-row" v-if="filterSection && questions.length > 0">
      <div class="batch-left">
        <el-button size="small" @click="batchPublish">批量发布</el-button>
        <el-button size="small" @click="batchUnpublish">批量撤回</el-button>
        <el-button size="small" @click="showDeadlineDialog = true">批量设置截止</el-button>
        <el-button size="small" type="danger" @click="batchDelete">批量删除</el-button>
      </div>
      <div class="batch-right">
        <span class="total-score" :class="{ overflow: totalScore > 100 }">
          总分：{{ totalScore }} / 100
        </span>
        <el-tag v-if="totalScore > 100" type="danger" size="small">已超过100分限制</el-tag>
        <el-tag v-else type="success" size="small">正常</el-tag>
      </div>
    </div>

    <el-table
      :data="questions"
      border stripe v-loading="loading" class="table"
      v-if="filterSection"
      @selection-change="onSelectionChange"
      ref="tableRef"
    >
      <el-table-column type="selection" width="45" />
      <el-table-column prop="order_num" label="序号" width="60" />
      <el-table-column prop="title" label="题目标题" min-width="200" show-overflow-tooltip />
      <el-table-column label="题型" width="90">
        <template #default="{ row }"><el-tag size="small">{{ typeMap[row.type] }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="max_score" label="分值" width="65" />
      <el-table-column label="答案" width="80">
        <template #default="{ row }">
          <span v-if="['single','multiple','judgment'].includes(row.type)">{{ row.correct_answer }}</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="截止" width="100">
        <template #default="{ row }">
          <span v-if="row.deadline">{{ new Date(row.deadline).toLocaleDateString('zh-CN') }}</span>
          <span v-else class="no-deadline">无</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_published ? 'success' : 'info'" size="small">{{ row.is_published ? '已发布' : '未发布' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="editQuestion(row)">编辑</el-button>
          <el-button v-if="!row.is_published" size="small" type="success" @click="publishQuestion(row.id)">发布</el-button>
          <el-button v-else size="small" type="warning" @click="unpublishQuestion(row.id)">撤回</el-button>
          <el-button size="small" type="danger" @click="deleteQuestion(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-else description="请选择课程和节" />

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="showDialog" :title="editing ? '编辑题目' : '添加题目'" width="620px" :close-on-click-modal="false">
      <el-form :model="form" label-width="100px">
        <el-form-item label="题型">
          <el-select v-model="form.type" @change="onTypeChange">
            <el-option v-for="(v,k) in typeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="题目内容" v-if="form.type !== 'judgment'"><el-input v-model="form.content" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="选项" v-if="['single','multiple'].includes(form.type)">
          <div v-for="(opt, idx) in optionList" :key="idx" style="display:flex;gap:8px;margin-bottom:6px;align-items:center">
            <span style="font-weight:600;width:24px">{{ optionLetters[idx] }}.</span>
            <el-input v-model="optionList[idx]" :placeholder="`选项${optionLetters[idx]}`" />
            <el-button @click="optionList.splice(idx,1)" icon="Delete" circle size="small" />
          </div>
          <el-button @click="optionList.push('')" size="small">添加选项</el-button>
        </el-form-item>
        <el-form-item label="正确答案" v-if="['single','multiple','judgment'].includes(form.type)">
          <el-select v-if="form.type === 'single'" v-model="form.correct_answer" placeholder="选择正确选项">
            <el-option v-for="(opt, idx) in optionList" :key="idx" :label="optionLetters[idx]" :value="optionLetters[idx]" />
          </el-select>
          <el-select v-else-if="form.type === 'multiple'" v-model="correctAnswerArr" multiple placeholder="选择正确选项（可多选）">
            <el-option v-for="(opt, idx) in optionList" :key="idx" :label="optionLetters[idx]" :value="optionLetters[idx]" />
          </el-select>
          <el-select v-else-if="form.type === 'judgment'" v-model="form.correct_answer" placeholder="选择正确答案">
            <el-option label="正确" value="正确" />
            <el-option label="错误" value="错误" />
          </el-select>
        </el-form-item>
        <el-form-item label="满分"><el-input-number v-model="form.max_score" :min="0" :max="100" /></el-form-item>
        <el-form-item label="截止时间"><el-date-picker v-model="form.deadline" type="datetime" placeholder="不填则无截止时间" /></el-form-item>
        <el-form-item label="允许重提交"><el-switch v-model="form.allow_resubmit" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveQuestion">保存</el-button>
      </template>
    </el-dialog>

    <!-- Batch Deadline Dialog -->
    <el-dialog v-model="showDeadlineDialog" title="批量设置截止时间" width="420px">
      <el-form label-width="80px">
        <el-form-item label="截止时间">
          <el-date-picker v-model="batchDeadline" type="datetime" placeholder="选择截止时间" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDeadlineDialog = false">取消</el-button>
        <el-button type="primary" @click="submitBatchDeadline">确定</el-button>
      </template>
    </el-dialog>

    <!-- Grading Dialog -->
    <el-dialog v-model="showGrading" title="批改题目" width="960px" :close-on-click-modal="false">
      <div v-loading="gradingLoading">
        <template v-if="gradingData.length > 0">
          <!-- 客观题（自动批改） -->
          <div v-if="objectiveQuestions.length > 0" class="grade-section">
            <h4 class="grade-section-title">客观题（自动批改）</h4>
            <div v-for="q in objectiveQuestions" :key="q.id" class="grade-question">
              <h5>
                <el-tag size="small">{{ typeMap[q.type] }}</el-tag>
                {{ q.title }} (满分{{ q.max_score }}分)
                <span class="correct-ans">正确答案：{{ q.correct_answer }}</span>
              </h5>
              <el-table v-if="q.submissions && q.submissions.length > 0" :data="q.submissions" border size="small" class="grade-table">
                <el-table-column prop="student_no" label="学号" width="140" />
                <el-table-column prop="student_name" label="姓名" width="100" />
                <el-table-column label="学生答案" min-width="160">
                  <template #default="{ row }">
                    <span>{{ row.answer }}</span>
                    <el-tag v-if="row.answer === q.correct_answer" type="success" size="small" style="margin-left:6px">正确</el-tag>
                    <el-tag v-else type="danger" size="small" style="margin-left:6px">错误</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="得分" width="70">
                  <template #default="{ row }">
                    <el-tag :type="row.answer === q.correct_answer ? 'success' : 'danger'" size="small">
                      {{ row.answer === q.correct_answer ? q.max_score : 0 }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>

          <!-- 简答题（手动批改） -->
          <div v-if="essayQuestions.length > 0" class="grade-section">
            <h4 class="grade-section-title">简答题（手动批改）</h4>
            <div v-for="q in essayQuestions" :key="q.id" class="grade-question">
              <h5>
                <el-tag size="small">{{ typeMap[q.type] }}</el-tag>
                {{ q.title }} (满分{{ q.max_score }}分)
              </h5>
              <el-table v-if="q.submissions && q.submissions.length > 0" :data="q.submissions" border size="small" class="grade-table">
                <el-table-column prop="student_no" label="学号" width="140" />
                <el-table-column prop="student_name" label="姓名" width="100" />
                <el-table-column label="学生答案" min-width="200">
                  <template #default="{ row }"><span>{{ row.answer }}</span></template>
                </el-table-column>
                <el-table-column label="评分" width="140">
                  <template #default="{ row }">
                    <el-input-number v-model="gradeScores[row.id]" :min="0" :max="q.max_score" size="small" placeholder="打分" />
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>

          <!-- 成绩汇总 -->
          <div v-if="studentSummary.length > 0" class="grade-section">
            <h4 class="grade-section-title">成绩汇总（按学号）</h4>
            <el-table :data="studentSummary" border size="small">
              <el-table-column prop="student_no" label="学号" width="140" />
              <el-table-column prop="student_name" label="姓名" width="100" />
              <el-table-column label="客观题" width="90">
                <template #default="{ row }">{{ row.auto_score }}</template>
              </el-table-column>
              <el-table-column label="简答题" width="90" v-if="essayQuestions.length > 0">
                <template #default="{ row }">{{ row.essay_score }}</template>
              </el-table-column>
              <el-table-column label="总分">
                <template #default="{ row }">
                  <strong :style="{ color: row.total > 100 ? '#f56c6c' : '#67c23a' }">{{ row.total }}</strong>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
        <el-empty v-else description="该节暂无已发布的题目" />
      </div>
      <template #footer>
        <el-button @click="showGrading = false">取消</el-button>
        <el-button type="primary" @click="submitGrades" :loading="gradingSubmitting" :disabled="studentSummary.length === 0">提交总成绩</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { courseAPI, sectionAPI, questionAPI } from '../../api'
import { extractList } from '../../api'
import api from '../../api'

const route = useRoute()
const courses = ref([])
const sections = ref([])
const questions = ref([])
const loading = ref(false)
const filterCourse = ref(null)
const filterSection = ref(null)
const showDialog = ref(false)
const editing = ref(false)
const editingId = ref(null)
const optionList = ref([])
const correctAnswerArr = ref([])
const tableRef = ref(null)
const selectedQuestions = ref([])

const optionLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')
const typeMap = { single: '单选题', multiple: '多选题', judgment: '判断题', essay: '简答题' }

const form = reactive({ type: 'single', title: '', content: '', correct_answer: '', max_score: 100, deadline: null, allow_resubmit: true })

const sortedSections = computed(() => {
  return [...sections.value].sort((a, b) => a.chapter_no - b.chapter_no || a.section_no - b.section_no)
})

const totalScore = computed(() => {
  return questions.value.reduce((sum, q) => sum + Number(q.max_score || 0), 0)
})

const showGrading = ref(false)
const gradingLoading = ref(false)
const gradingSubmitting = ref(false)
const gradingData = ref([])
const gradeScores = reactive({})

const objectiveQuestions = computed(() => {
  return gradingData.value.filter(q => ['single', 'multiple', 'judgment'].includes(q.type))
})
const essayQuestions = computed(() => {
  return gradingData.value.filter(q => q.type === 'essay')
})
const studentSummary = computed(() => {
  const map = new Map()
  for (const q of gradingData.value) {
    for (const sub of (q.submissions || [])) {
      const sid = sub.student_id || sub.student
      if (!map.has(sid)) {
        map.set(sid, {
          student_id: sid,
          student_no: sub.student_no || '',
          student_name: sub.student_name || '',
          auto_score: 0,
          essay_score: 0,
          total: 0,
        })
      }
      const entry = map.get(sid)
      if (['single', 'multiple', 'judgment'].includes(q.type)) {
        const correct = (q.correct_answer || '').trim()
        const studentAns = (sub.answer || '').trim()
        if (studentAns === correct) {
          entry.auto_score += Number(q.max_score) || 0
        }
      }
    }
  }
  // Add essay scores from gradeScores
  for (const q of essayQuestions.value) {
    for (const sub of (q.submissions || [])) {
      const sid = sub.student_id || sub.student
      if (map.has(sid) && gradeScores[sub.id] !== undefined) {
        map.get(sid).essay_score += Number(gradeScores[sub.id]) || 0
      }
    }
  }
  for (const entry of map.values()) {
    entry.auto_score = Math.round(entry.auto_score * 100) / 100
    entry.essay_score = Math.round(entry.essay_score * 100) / 100
    entry.total = Math.round((entry.auto_score + entry.essay_score) * 100) / 100
  }
  return [...map.values()]
})

const showDeadlineDialog = ref(false)
const batchDeadline = ref(null)

async function loadCourses() {
  try {
    const res = await courseAPI.list()
    courses.value = extractList(res)
  } catch (e) { ElMessage.error('加载课程失败') }
}

async function onCourseChange(courseId) {
  filterSection.value = null; questions.value = []
  try {
    const course = await courseAPI.tree(courseId)
    const allSections = []
    for (const ch of (course.data?.chapters || [])) {
      for (const sec of (ch.sections || [])) {
        allSections.push(sec)
      }
    }
    sections.value = allSections
    const preSelect = route.query.section
    if (preSelect) {
      const found = allSections.find(s => s.id == preSelect)
      if (found) { filterSection.value = found.id; loadQuestions() }
    }
  } catch (e) { ElMessage.error('加载章节失败') }
}

function onSectionChange() { loadQuestions() }

async function loadQuestions() {
  if (!filterSection.value) return
  loading.value = true
  try {
    const res = await questionAPI.list({ section: filterSection.value })
    questions.value = extractList(res)
  } catch (e) { ElMessage.error('加载题目失败') }
  finally { loading.value = false }
}

function onTypeChange() {
  form.correct_answer = ''
  optionList.value = []
  correctAnswerArr.value = []
  if (form.type === 'judgment') {
    optionList.value = ['正确', '错误']
  }
}

function openAdd() {
  editing.value = false; editingId.value = null
  Object.assign(form, { type: 'single', title: '', content: '', correct_answer: '', max_score: 100, deadline: null, allow_resubmit: true })
  optionList.value = []; correctAnswerArr.value = []; showDialog.value = true
}

function editQuestion(row) {
  editing.value = true; editingId.value = row.id
  Object.assign(form, {
    type: row.type, title: row.title, content: row.content || '',
    correct_answer: row.correct_answer || '', max_score: row.max_score,
    deadline: row.deadline, allow_resubmit: row.allow_resubmit,
  })
  correctAnswerArr.value = []
  if (row.type === 'multiple' && row.correct_answer) {
    correctAnswerArr.value = row.correct_answer.split(',').map(s => s.trim()).filter(Boolean)
  }
  optionList.value = row.options ? [...row.options] : (row.type === 'judgment' ? ['正确', '错误'] : [])
  showDialog.value = true
}

async function saveQuestion() {
  if (form.type === 'multiple') {
    form.correct_answer = correctAnswerArr.value.join(',')
  }
  const data = { ...form, section: filterSection.value }
  if (['single', 'multiple', 'judgment'].includes(data.type)) data.options = [...optionList.value]
  try {
    if (editing.value) {
      await questionAPI.update(editingId.value, data); ElMessage.success('已更新')
    } else {
      await questionAPI.create(data); ElMessage.success('已添加')
    }
    showDialog.value = false; loadQuestions()
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  }
}

async function publishQuestion(id) { try { await questionAPI.publish(id); loadQuestions() } catch (e) { ElMessage.error('失败') } }
async function unpublishQuestion(id) { try { await questionAPI.unpublish(id); loadQuestions() } catch (e) { ElMessage.error('失败') } }
async function deleteQuestion(id) {
  try {
    await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    await questionAPI.delete(id); ElMessage.success('已删除'); loadQuestions()
  } catch (e) { /* cancelled */ }
}

function onSelectionChange(selection) { selectedQuestions.value = selection }

async function batchPublish() {
  if (selectedQuestions.value.length === 0) return ElMessage.warning('请先选择题目')
  try {
    await api.post('/questions/batch_publish/', { ids: selectedQuestions.value.map(q => q.id) })
    ElMessage.success('批量发布成功')
    selectedQuestions.value = []; loadQuestions()
  } catch (e) { ElMessage.error('操作失败') }
}

async function batchUnpublish() {
  if (selectedQuestions.value.length === 0) return ElMessage.warning('请先选择题目')
  try {
    await api.post('/questions/batch_unpublish/', { ids: selectedQuestions.value.map(q => q.id) })
    ElMessage.success('批量撤回成功')
    selectedQuestions.value = []; loadQuestions()
  } catch (e) { ElMessage.error('操作失败') }
}

async function batchDelete() {
  if (selectedQuestions.value.length === 0) return ElMessage.warning('请先选择题目')
  try {
    await ElMessageBox.confirm(
      `确定删除选中的${selectedQuestions.value.length}道题目？`, '提示',
      { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }
    )
    await api.post('/questions/batch_delete/', { ids: selectedQuestions.value.map(q => q.id) })
    ElMessage.success('批量删除成功')
    selectedQuestions.value = []; loadQuestions()
  } catch (e) { /* cancelled */ }
}

async function submitBatchDeadline() {
  if (selectedQuestions.value.length === 0) return ElMessage.warning('请先选择题目')
  if (!batchDeadline.value) return ElMessage.warning('请选择截止时间')
  try {
    await api.post('/questions/batch_deadline/', {
      ids: selectedQuestions.value.map(q => q.id),
      deadline: batchDeadline.value.toISOString(),
    })
    ElMessage.success('截止时间已设置')
    showDeadlineDialog.value = false
    selectedQuestions.value = []; loadQuestions()
  } catch (e) { ElMessage.error('操作失败') }
}

async function openGrading() {
  showGrading.value = true; gradingData.value = []
  Object.keys(gradeScores).forEach(k => delete gradeScores[k])
  gradingLoading.value = true
  try {
    const res = await api.get(`/questions/section_submissions/?section=${filterSection.value}`)
    gradingData.value = extractList(res)
    // Initialize essay grade scores to 0 for all essay submissions
    for (const q of gradingData.value) {
      if (q.type === 'essay') {
        for (const sub of (q.submissions || [])) {
          gradeScores[sub.id] = 0
        }
      }
    }
  } catch (e) { ElMessage.error('加载提交数据失败') }
  finally { gradingLoading.value = false }
}

async function submitGrades() {
  if (studentSummary.value.length === 0) return
  gradingSubmitting.value = true
  try {
    const grades = studentSummary.value.map(s => ({
      student_id: s.student_id,
      total_score: s.total,
      details: `客观题:${s.auto_score} 简答题:${s.essay_score}`,
    }))
    await api.post('/questions/section_grade/', {
      section_id: filterSection.value,
      grades,
    })
    ElMessage.success('批改完成，成绩已提交至成绩管理')
    showGrading.value = false
  } catch (e) { ElMessage.error('批改提交失败') }
  finally { gradingSubmitting.value = false }
}

onMounted(async () => {
  await loadCourses()
  const preSelectSection = route.query.section
  if (preSelectSection && courses.value.length > 0) {
    for (const c of courses.value) {
      try {
        const tree = await courseAPI.tree(c.id)
        for (const ch of (tree.data?.chapters || [])) {
          for (const sec of (ch.sections || [])) {
            if (sec.id == preSelectSection) {
              filterCourse.value = c.id
              sections.value = [sec]
              filterSection.value = sec.id
              loadQuestions()
              return
            }
          }
        }
      } catch (e) { /* skip */ }
    }
  }
})
</script>

<style scoped>
.question-manage { max-width: 1100px; margin: 0 auto; }
.toolbar { margin-bottom: 16px; display: flex; align-items: center; }
.batch-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.batch-left { display: flex; gap: 6px; }
.batch-right { display: flex; align-items: center; gap: 8px; }
.total-score { font-weight: 700; font-size: 16px; }
.total-score.overflow { color: #f56c6c; }
.table { width: 100%; margin-top: 8px; }
.no-deadline { color: #c0c4cc; }
.grade-section { margin-bottom: 20px; }
.grade-section-title { margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #409eff; font-size: 15px; color: #303133; }
.grade-question { margin-bottom: 16px; }
.grade-question h5 { margin-bottom: 8px; font-size: 14px; }
.grade-table { margin-bottom: 12px; }
.grade-section :deep(.el-table__body-wrapper) { max-height: 260px; overflow-y: auto; }
.correct-ans { color: #67c23a; font-weight: 500; margin-left: 12px; }
</style>
