<template>
  <div class="dashboard">
    <el-card v-if="activeSection" class="section-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>当前节：第{{ activeSection.chapter_no }}章 {{ activeSection.title }}</span>
          <el-tag type="success" size="small">进行中</el-tag>
        </div>
      </template>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="文档内容" name="doc">
          <div v-if="docList.length > 1" class="doc-tabs">
            <el-radio-group v-model="currentDocIndex" size="small" @change="onDocSwitch">
              <el-radio-button v-for="(doc, idx) in docList" :key="doc.id" :value="idx">
                {{ doc.title || doc.file_name || `文档${idx + 1}` }}
              </el-radio-button>
            </el-radio-group>
          </div>
          <div v-if="currentDoc" class="doc-area">
            <iframe :src="currentDoc" class="pdf-viewer" />
          </div>
          <el-empty v-else description="暂无文档" />
          <div v-if="docList.length > 0" class="download-cards">
            <el-card v-for="doc in docList" :key="doc.id" class="download-card" shadow="hover">
              <div class="doc-info">
                <el-icon><Document /></el-icon>
                <span class="doc-name">{{ doc.title || doc.file_name || '文档' }}</span>
              </div>
              <el-button type="primary" size="small" @click="downloadDoc(doc)">下载</el-button>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="问答内容" name="qa">
          <div v-if="questions.length > 0" class="qa-area">
            <div v-for="q in questions" :key="q.id" class="question-card">
              <div class="q-header">
                <span><el-tag size="small">{{ typeMap[q.type] }}</el-tag></span>
                <span class="q-score">{{ q.max_score }}分</span>
              </div>
              <div class="q-title">{{ q.title }}</div>
              <div v-if="q.content" class="q-content">{{ q.content }}</div>

              <el-radio-group
                v-if="q.type === 'single'"
                v-model="answers[q.id]"
                class="q-options"
                :disabled="isLocked(q)"
              >
                <div v-for="(opt, idx) in (q.options || [])" :key="idx" class="option-item">
                  <el-radio :value="String(idx)">{{ optionLetters[idx] }}. {{ opt }}</el-radio>
                </div>
              </el-radio-group>
              <el-checkbox-group
                v-else-if="q.type === 'multiple'"
                v-model="multiAnswers[q.id]"
                class="q-options"
                :disabled="isLocked(q)"
              >
                <div v-for="(opt, idx) in (q.options || [])" :key="idx" class="option-item">
                  <el-checkbox :value="String(idx)">{{ optionLetters[idx] }}. {{ opt }}</el-checkbox>
                </div>
              </el-checkbox-group>

              <el-radio-group
                v-else-if="q.type === 'judgment'"
                v-model="answers[q.id]"
                class="q-options"
                :disabled="isLocked(q)"
              >
                <div class="option-item"><el-radio value="正确">正确</el-radio></div>
                <div class="option-item"><el-radio value="错误">错误</el-radio></div>
              </el-radio-group>

              <el-input
                v-if="q.type === 'essay'"
                v-model="answers[q.id]"
                type="textarea"
                :rows="4"
                placeholder="请输入你的回答"
                :disabled="isLocked(q)"
              />

              <div v-if="submitted[q.id] && !q.allow_resubmit" class="submit-status">
                <el-tag type="success" size="small">已提交</el-tag>
              </div>
              <div v-else-if="submitted[q.id] && q.allow_resubmit" class="submit-status">
                <el-tag type="warning" size="small">已提交，可重新提交</el-tag>
              </div>
              <el-button
                v-if="!submitted[q.id] || q.allow_resubmit"
                type="primary"
                size="small"
                :disabled="!canSubmit(q)"
                @click="handleSubmit(q)"
              >
                {{ submitted[q.id] ? '重新提交' : '提交答案' }}
              </el-button>
            </div>
          </div>
          <el-empty v-else description="暂无题目" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
    <el-empty v-else description="暂无激活的节，请联系教师" />
  </div>
</template>

<script setup>
/** 学生仪表盘 — 当前激活节文档查看/题目作答/答案提交 */
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { documentAPI, questionAPI, submissionAPI, extractList } from '../../api'
import { optionLetters, typeMap, formatTime } from '../../utils/constants'

const props = defineProps({ activeSection: Object, courseId: Number })

const activeTab = ref('doc')
const currentDoc = ref(null)
const currentDocIndex = ref(0)
const docList = ref([])
const questions = ref([])
const answers = reactive({})
const multiAnswers = reactive({})
const submitted = reactive({})

/** 将相对路径或 localhost URL 统一转为 127.0.0.1 绝对路径 */
function fixUrl(raw) {
  if (!raw) return ''
  let url = raw
  if (!url.startsWith('http')) {
    url = `http://127.0.0.1:8000${url}`
  }
  return url.replace('localhost', '127.0.0.1')
}

function setCurrentDoc() {
  const doc = docList.value[currentDocIndex.value]
  if (doc) {
    const url = fixUrl(doc.file_url || doc.file || '')
    currentDoc.value = url || null
  }
}

function onDocSwitch(idx) {
  currentDocIndex.value = idx
  setCurrentDoc()
}

function downloadDoc(doc) {
  const url = fixUrl(doc.file_url || doc.file || '')
  if (!url) return
  const name = doc.title || doc.file_name || '文档'
  const link = document.createElement('a')
  link.href = url
  link.download = name
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function isDeadlinePassed(q) {
  if (!q.deadline) return false
  return new Date(q.deadline) < new Date()
}

function isLocked(q) {
  return submitted[q.id] && (!q.allow_resubmit || isDeadlinePassed(q))
}

function canSubmit(q) {
  if (isDeadlinePassed(q)) return false
  if (q.type === 'multiple') {
    return (multiAnswers[q.id] || []).length > 0
  }
  return !!answers[q.id]
}

async function loadSectionData() {
  if (!props.activeSection) return
  const sectionId = props.activeSection.id
  currentDoc.value = null
  currentDocIndex.value = 0
  questions.value = []
  Object.keys(answers).forEach(k => delete answers[k])
  Object.keys(multiAnswers).forEach(k => delete multiAnswers[k])
  Object.keys(submitted).forEach(k => delete submitted[k])

  try {
    const [docRes, qRes, subRes] = await Promise.all([
      documentAPI.list({ section: sectionId }),
      questionAPI.list({ section: sectionId, is_published: true }),
      submissionAPI.mySubmissions({ section_id: sectionId }),
    ])

    const docs = extractList(docRes)
    docList.value = docs
    if (docs.length > 0) {
      setCurrentDoc()
    }

    questions.value = extractList(qRes)
    const subs = extractList(subRes)
    for (const sub of subs) {
      submitted[sub.question] = true
      if (sub.answer) {
        try {
          const parsed = JSON.parse(sub.answer)
          if (Array.isArray(parsed)) {
            multiAnswers[sub.question] = parsed
          } else {
            answers[sub.question] = sub.answer
          }
        } catch {
          answers[sub.question] = sub.answer
        }
      }
    }
  } catch (e) {
    console.error('加载节数据失败', e)
  }
}

async function handleSubmit(question) {
  const answer = question.type === 'multiple'
    ? JSON.stringify(multiAnswers[question.id] || [])
    : (answers[question.id] || '')
  try {
    // Check if already submitted - if so, the backend will handle overwrite
    await submissionAPI.create({
      question: question.id,
      section: props.activeSection.id,
      answer,
    })
    submitted[question.id] = true
    ElMessage.success('提交成功')
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || '提交失败')
  }
}

watch(() => props.activeSection, () => {
  if (props.activeSection) loadSectionData()
}, { immediate: true })
</script>

<style scoped>
.dashboard { max-width: 960px; margin: 0 auto; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.doc-tabs { margin-bottom: 12px; }
.doc-area { height: 78vh; }
.pdf-viewer { width: 100%; height: 100%; border: none; border-radius: 8px; }
.q-options { display: flex; flex-direction: column; gap: 8px; margin: 10px 0; }
.option-item { margin-left: 8px; transition: all .2s ease; }
.option-item:hover { color: #667eea; }
.question-card {
  background: #fff; border: 1px solid #ebeef5; border-radius: 10px;
  padding: 20px; margin-bottom: 14px;
  transition: all .3s ease;
}
.question-card:hover {
  box-shadow: 0 4px 16px rgba(102,126,234,.1);
  transform: translateY(-1px);
}
.q-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
.q-title { font-weight: 600; margin-bottom: 8px; font-size: 15px; }
.q-content { color: #606266; margin-bottom: 8px; font-size: 14px; }
.submit-status { margin-top: 12px; }
.download-cards { margin-top: 16px; display: flex; flex-wrap: wrap; gap: 12px; }
.download-card {
  width: 240px; transition: all .3s ease;
}
.download-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,.08);
}
.download-card :deep(.el-card__body) { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; }
.doc-info { display: flex; align-items: center; gap: 8px; }
.doc-name { font-size: 13px; color: #303133; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
