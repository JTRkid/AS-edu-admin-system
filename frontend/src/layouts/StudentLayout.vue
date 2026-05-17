<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="header-left">
        <span class="logo">教学平台</span>
        <el-breadcrumb separator=">">
          <el-breadcrumb-item>{{ courseName || '课程' }}</el-breadcrumb-item>
          <el-breadcrumb-item v-if="activeSection">
            第{{ activeSection.chapter_no }}章 {{ activeSection.chapter_title }}
          </el-breadcrumb-item>
          <el-breadcrumb-item v-if="activeSection">
            {{ activeSection.section_no }} {{ activeSection.title }}
          </el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <span>{{ user?.name }}</span>
        <el-dropdown>
          <el-avatar :size="32" icon="UserFilled" />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container class="main">
      <el-aside width="220px" class="aside">
        <div class="course-list">
          <div v-for="course in courses" :key="course.id" class="course-group">
            <div class="course-title" @click="toggleCourse(course)">{{ course.name }}</div>
            <template v-if="expandedCourse === course.id">
              <template v-for="chapter in course.chapters" :key="chapter.id">
                <div v-if="getVisibleSections(chapter).length > 0" class="chapter-group">
                  <div class="chapter-title">第{{ chapter.chapter_no }}章 {{ chapter.title }}</div>
                  <div
                    v-for="section in getVisibleSections(chapter)"
                    :key="section.id"
                    :class="['section-item', { active: activeSection?.id === section.id }]"
                    @click="selectSection(section, course)"
                  >
                    {{ section.section_no }} {{ section.title }}
                  </div>
                </div>
              </template>
            </template>
          </div>
        </div>
      </el-aside>
      <el-main class="content">
        <Dashboard :active-section="activeSection" :course-id="currentCourseId" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { courseAPI } from '../api'
import { extractList } from '../api'
import Dashboard from '../views/student/Dashboard.vue'

const router = useRouter()
const authStore = useAuthStore()
const user = authStore.user

const courses = ref([])
const activeSection = ref(null)
const courseName = ref('')
const currentCourseId = ref(null)
const expandedCourse = ref(null)

async function loadCourses() {
  try {
    const res = await courseAPI.list()
    const courseList = extractList(res)
    if (courseList.length === 0) return

    // Load full tree for all courses, sorted
    const loadedCourses = []
    for (const c of courseList) {
      try {
        const treeRes = await courseAPI.tree(c.id)
        if (treeRes.data) {
          const course = treeRes.data
          if (course.chapters) {
            course.chapters.sort((a, b) => a.chapter_no - b.chapter_no)
            for (const ch of course.chapters) {
              if (ch.sections) {
                ch.sections.sort((a, b) => a.section_no - b.section_no)
              }
            }
          }
          loadedCourses.push(course)
        }
      } catch (e) { /* skip */ }
    }

    courses.value = loadedCourses
    if (loadedCourses.length > 0) {
      const first = loadedCourses[0]
      expandedCourse.value = first.id
      courseName.value = first.name
      currentCourseId.value = first.id
      // Select first visible section
      for (const ch of (first.chapters || [])) {
        for (const sec of (ch.sections || [])) {
          if (sec.is_visible) {
            activeSection.value = sec
            return
          }
        }
      }
    }
  } catch (e) {
    console.error('加载课程失败', e)
  }
}

function getVisibleSections(chapter) {
  return (chapter.sections || []).filter(s => s.is_visible)
}

function toggleCourse(course) {
  expandedCourse.value = expandedCourse.value === course.id ? null : course.id
}

function selectSection(section, course) {
  activeSection.value = section
  courseName.value = course.name
  currentCourseId.value = course.id
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(loadCourses)
</script>

<style scoped>
.layout { height: 100vh; }
.header {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; border-bottom: 1px solid #ebeef5; padding: 0 20px; height: 56px;
}
.header-left { display: flex; align-items: center; gap: 20px; }
.logo { font-size: 18px; font-weight: 600; color: #303133; }
.header-right { display: flex; align-items: center; gap: 12px; color: #606266; }
.aside { background: #fafafa; border-right: 1px solid #ebeef5; overflow-y: auto; }
.course-list { padding: 12px; }
.course-title {
  font-size: 15px; font-weight: 600; padding: 10px 8px; cursor: pointer;
  color: #303133; border-radius: 6px; margin-bottom: 4px;
}
.course-title:hover { background: #e8f4ff; }
.chapter-title { font-weight: 600; margin: 8px 0 4px 8px; font-size: 13px; color: #606266; }
.section-item {
  padding: 7px 12px; cursor: pointer; border-radius: 6px;
  font-size: 13px; margin-left: 16px; color: #606266; transition: all .2s;
}
.section-item:hover { background: #e8f4ff; }
.section-item.active { background: #409eff; color: #fff; font-weight: 500; }
.content { padding: 20px; background: #f0f2f5; }
</style>
