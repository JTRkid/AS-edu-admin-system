<template>
  <div class="course-manage">
    <div class="toolbar">
      <el-button type="primary" @click="showCourseDialog = true">添加课程</el-button>
    </div>

    <el-card v-for="course in courses" :key="course.id" class="course-card" shadow="never">
      <template #header>
        <div class="course-header">
          <span class="course-name">{{ course.name }}</span>
          <div class="course-actions">
            <el-tag :type="course.status === 'active' ? 'success' : 'info'" size="small">{{ statusMap[course.status] }}</el-tag>
            <el-button size="small" @click="openChapterDialog(course)">添加章</el-button>
            <el-button size="small" type="primary" @click="editCourse(course)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteCourse(course.id)">删除</el-button>
          </div>
        </div>
      </template>
      <div v-for="chapter in course.chapters" :key="chapter.id" class="chapter-block">
        <div class="chapter-header">
          <span>第{{ chapter.chapter_no }}章 {{ chapter.title }}</span>
          <div>
            <el-button size="small" @click="openSectionDialog(chapter)">添加节</el-button>
            <el-button size="small" @click="editChapter(chapter)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteChapter(chapter.id)">删除</el-button>
          </div>
        </div>
        <div v-for="section in chapter.sections" :key="section.id" class="section-row">
          <span class="section-title">
            {{ section.section_no }} {{ section.title }}
            <el-tag v-if="!section.is_visible" size="small" type="warning">学生不可见</el-tag>
          </span>
          <div class="section-actions">
            <el-button size="small" @click="manageDoc(section)">文档</el-button>
            <el-button size="small" type="primary" @click="jumpToQuestions(section)">题目</el-button>
            <el-button size="small" @click="toggleVisible(section)">{{ section.is_visible ? '隐藏' : '显示' }}</el-button>
            <el-button size="small" @click="editSection(section)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteSection(section.id)">删除</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Course Dialog -->
    <el-dialog v-model="showCourseDialog" :title="editingCourse ? '编辑课程' : '添加课程'" width="500px">
      <el-form :model="courseForm" label-width="80px">
        <el-form-item label="课程名称"><el-input v-model="courseForm.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="courseForm.description" type="textarea" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="courseForm.status">
            <el-option label="草稿" value="draft" /><el-option label="已发布" value="active" /><el-option label="归档" value="archived" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCourseDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCourse">保存</el-button>
      </template>
    </el-dialog>

    <!-- Chapter Dialog -->
    <el-dialog v-model="showChapterDialog" :title="editingChapter ? '编辑章' : '添加章'" width="500px">
      <el-form :model="chapterForm" label-width="80px">
        <el-form-item label="章标题"><el-input v-model="chapterForm.title" /></el-form-item>
        <el-form-item label="章序号"><el-input-number v-model="chapterForm.chapter_no" :min="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showChapterDialog = false">取消</el-button>
        <el-button type="primary" @click="saveChapter">保存</el-button>
      </template>
    </el-dialog>

    <!-- Section Dialog -->
    <el-dialog v-model="showSectionDialog" :title="editingSection ? '编辑节' : '添加节'" width="500px">
      <el-form :model="sectionForm" label-width="100px">
        <el-form-item label="节标题"><el-input v-model="sectionForm.title" /></el-form-item>
        <el-form-item label="节序号"><el-input-number v-model="sectionForm.section_no" :min="1" /></el-form-item>
        <el-form-item label="学生可见"><el-switch v-model="sectionForm.is_visible" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSectionDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSection">保存</el-button>
      </template>
    </el-dialog>

    <!-- Document Dialog -->
    <el-dialog v-model="showDocDialog" title="文档管理" width="560px">
      <div v-if="existingDocs.length > 0" class="existing-docs">
        <h4>已有文档（{{ existingDocs.length }}个）</h4>
        <div v-for="doc in existingDocs" :key="doc.id" class="doc-item">
          <el-icon><Document /></el-icon>
          <span class="doc-item-name">{{ doc.title || '未命名文档' }}</span>
          <el-button size="small" type="danger" @click="deleteDoc(doc.id)">删除</el-button>
        </div>
      </div>
      <el-divider v-if="existingDocs.length > 0" />
      <el-upload drag :auto-upload="false" :on-change="handleFileChange" accept=".pdf">
        <el-icon><UploadFilled /></el-icon>
        <div>拖拽或点击上传PDF文件</div>
      </el-upload>
      <template #footer>
        <el-button @click="showDocDialog = false">取消</el-button>
        <el-button type="primary" :disabled="!pendingFile" @click="uploadDoc">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { courseAPI, chapterAPI, sectionAPI, documentAPI, extractList } from '../../api'

const router = useRouter()
const courses = ref([])
const pendingFile = ref(null)

const statusMap = { draft: '草稿', active: '已发布', archived: '归档' }

const showCourseDialog = ref(false)
const editingCourse = ref(null)
const courseForm = reactive({ name: '', description: '', status: 'draft' })

const showChapterDialog = ref(false)
const editingChapter = ref(null)
const chapterForm = reactive({ title: '', chapter_no: 1 })
const currentCourseForChapter = ref(null)

const showSectionDialog = ref(false)
const editingSection = ref(null)
const sectionForm = reactive({ title: '', section_no: 1, is_visible: true })
const currentChapterForSection = ref(null)

const showDocDialog = ref(false)
const currentSectionForDoc = ref(null)
const replaceMode = ref(false)
const existingDocs = ref([])

async function loadCourses() {
  try {
    const res = await courseAPI.list()
    const courseList = extractList(res)
    const fullCourses = []
    for (const c of courseList) {
      try {
        const treeRes = await courseAPI.tree(c.id)
        if (treeRes.data) {
          const course = treeRes.data
          // Sort chapters by chapter_no
          if (course.chapters) {
            course.chapters.sort((a, b) => a.chapter_no - b.chapter_no)
            // Sort sections by section_no within each chapter
            for (const ch of course.chapters) {
              if (ch.sections) {
                ch.sections.sort((a, b) => a.section_no - b.section_no)
              }
            }
          }
          fullCourses.push(course)
        }
      } catch (e) { fullCourses.push(c) }
    }
    courses.value = fullCourses
  } catch (e) { ElMessage.error('加载课程失败') }
}

function editCourse(course) {
  editingCourse.value = course
  Object.assign(courseForm, { name: course.name, description: course.description || '', status: course.status })
  showCourseDialog.value = true
}
async function saveCourse() {
  try {
    if (editingCourse.value) {
      await courseAPI.update(editingCourse.value.id, courseForm)
    } else {
      await courseAPI.create(courseForm)
    }
    showCourseDialog.value = false; editingCourse.value = null
    Object.assign(courseForm, { name: '', description: '', status: 'draft' })
    loadCourses()
    ElMessage.success('保存成功')
  } catch (e) { ElMessage.error('操作失败') }
}
async function deleteCourse(id) {
  try {
    await ElMessageBox.confirm('确定删除此课程？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    await courseAPI.delete(id); ElMessage.success('已删除'); loadCourses()
  } catch (e) { /* cancelled */ }
}

function openChapterDialog(course) {
  currentCourseForChapter.value = course; editingChapter.value = null
  Object.assign(chapterForm, { title: '', chapter_no: 1 }); showChapterDialog.value = true
}
function editChapter(chapter) {
  editingChapter.value = chapter
  Object.assign(chapterForm, { title: chapter.title, chapter_no: chapter.chapter_no }); showChapterDialog.value = true
}
async function saveChapter() {
  try {
    const data = { ...chapterForm }
    if (editingChapter.value) {
      await chapterAPI.update(editingChapter.value.id, data)
    } else {
      data.course = currentCourseForChapter.value.id
      await chapterAPI.create(data)
    }
    showChapterDialog.value = false; loadCourses(); ElMessage.success('保存成功')
  } catch (e) { ElMessage.error('操作失败: ' + (e?.response?.data?.detail || '')) }
}
async function deleteChapter(id) {
  try {
    await ElMessageBox.confirm('确定删除此章？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    await chapterAPI.delete(id); ElMessage.success('已删除'); loadCourses()
  } catch (e) { /* cancelled */ }
}

function openSectionDialog(chapter) {
  currentChapterForSection.value = chapter; editingSection.value = null
  Object.assign(sectionForm, { title: '', section_no: 1, is_visible: true }); showSectionDialog.value = true
}
function editSection(section) {
  editingSection.value = section
  Object.assign(sectionForm, { title: section.title, section_no: section.section_no, is_visible: section.is_visible })
  showSectionDialog.value = true
}
async function saveSection() {
  try {
    const data = { ...sectionForm }
    if (editingSection.value) {
      await sectionAPI.update(editingSection.value.id, data)
    } else {
      data.chapter = currentChapterForSection.value.id
      await sectionAPI.create(data)
    }
    showSectionDialog.value = false; loadCourses(); ElMessage.success('保存成功')
  } catch (e) { ElMessage.error('操作失败: ' + (e?.response?.data?.detail || '')) }
}
async function deleteSection(id) {
  try {
    await ElMessageBox.confirm('确定删除此节？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    await sectionAPI.delete(id); ElMessage.success('已删除'); loadCourses()
  } catch (e) { /* cancelled */ }
}
async function toggleVisible(section) {
  try {
    await sectionAPI.update(section.id, { is_visible: !section.is_visible })
    ElMessage.success(section.is_visible ? '已对学生隐藏' : '已对学生可见')
    loadCourses()
  } catch (e) { ElMessage.error('操作失败') }
}

async function manageDoc(section) {
  currentSectionForDoc.value = section
  pendingFile.value = null
  replaceMode.value = false
  existingDocs.value = []
  try {
    const res = await documentAPI.list({ section: section.id })
    const docs = extractList(res)
    existingDocs.value = docs
    if (docs.length > 0) {
      try {
        await ElMessageBox.confirm(
          `该节已有 ${docs.length} 个文档，是否替换现有文档？`,
          '文档已存在',
          { confirmButtonText: '替换', cancelButtonText: '在后面添加', type: 'warning', distinguishCancelAndClose: true }
        )
        replaceMode.value = true
      } catch (action) {
        // 'cancel' = 点击"在后面添加"，'close' = 点击X关闭
        if (action === 'cancel') {
          replaceMode.value = false
        }
        // 无论哪种情况都继续打开文档管理弹窗
      }
    }
  } catch (e) { /* ignore */ }
  showDocDialog.value = true
}

async function deleteDoc(docId) {
  try {
    await ElMessageBox.confirm('确定删除该文档？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' })
    await documentAPI.delete(docId)
    ElMessage.success('文档已删除')
    existingDocs.value = existingDocs.value.filter(d => d.id !== docId)
    loadCourses()
  } catch (e) { /* cancelled */ }
}
function handleFileChange(file) { pendingFile.value = file.raw }
async function uploadDoc() {
  if (!pendingFile.value || !currentSectionForDoc.value) return
  try {
    if (replaceMode.value) {
      const res = await documentAPI.list({ section: currentSectionForDoc.value.id })
      const docs = extractList(res)
      for (const doc of docs) {
        await documentAPI.delete(doc.id)
      }
    }
    await documentAPI.upload(currentSectionForDoc.value.id, pendingFile.value)
    ElMessage.success('文档上传成功'); showDocDialog.value = false; loadCourses()
  } catch (e) { ElMessage.error('上传失败') }
}

function jumpToQuestions(section) {
  router.push({ path: '/teacher/questions', query: { section: section.id } })
}

onMounted(loadCourses)
</script>

<style scoped>
.course-manage { max-width: 960px; margin: 0 auto; }
.toolbar { margin-bottom: 16px; }
.course-card { margin-bottom: 16px; }
.course-header { display: flex; justify-content: space-between; align-items: center; }
.course-name { font-size: 16px; font-weight: 600; }
.course-actions { display: flex; gap: 8px; align-items: center; }
.chapter-block { margin: 10px 0; padding: 12px; background: #f9fafc; border-radius: 8px; }
.chapter-header {
  display: flex; justify-content: space-between; align-items: center;
  font-weight: 600; margin-bottom: 6px; padding-bottom: 6px; border-bottom: 1px solid #ebeef5;
}
.section-row { display: flex; justify-content: space-between; align-items: center; padding: 7px 12px; border-radius: 4px; }
.section-row:hover { background: #ecf5ff; }
.section-title { display: flex; align-items: center; gap: 8px; }
.section-actions { display: flex; gap: 4px; }
.existing-docs h4 { margin-bottom: 12px; font-size: 14px; color: #303133; }
.doc-item { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.doc-item:last-child { border-bottom: none; }
.doc-item-name { flex: 1; font-size: 13px; color: #606266; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
