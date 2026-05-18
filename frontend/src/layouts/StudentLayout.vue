<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="header-left">
        <span class="logo">AS-edu-system</span>
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
              <el-dropdown-item @click="showChangePwd = true">修改密码</el-dropdown-item>
              <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container class="main">
      <el-aside width="280px" class="aside">
        <el-menu :default-active="activeMenu" router class="side-menu">
          <el-menu-item index="/student/dashboard">
            <el-icon><Document /></el-icon>
            <span>课程学习</span>
          </el-menu-item>
          <el-menu-item index="/student/scores">
            <el-icon><Trophy /></el-icon>
            <span>我的成绩</span>
          </el-menu-item>
        </el-menu>
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
        <router-view v-slot="{ Component }">
          <component :is="Component" :active-section="activeSection" :course-id="currentCourseId" />
        </router-view>
      </el-main>
    </el-container>

    <ChangePassword v-model="showChangePwd" />
  </el-container>
</template>

<script setup>
/** 学生端布局 — 顶部导航（课程选择/面包屑/用户头像）+ 侧边栏（文档/问答切换） */
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { courseAPI } from '../api'
import { extractList } from '../api'
import ChangePassword from '../components/ChangePassword.vue'
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const user = authStore.user

const activeMenu = computed(() => route.path)
const showChangePwd = ref(false)

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
  if (route.path !== '/student/dashboard') router.push('/student/dashboard')
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
  background: #3B82F6;
  padding: 0 24px; height: 56px; color: #fff;
  box-shadow: 0 2px 8px rgba(59,130,246,.25);
}
.header-left { display: flex; align-items: center; gap: 20px; }
.logo { font-size: 18px; font-weight: 700; color: #fff; }
.header-left :deep(.el-breadcrumb__inner) { color: rgba(255,255,255,.85); font-weight: 400; }
.header-left :deep(.el-breadcrumb__separator) { color: rgba(255,255,255,.6); }
.header-right { display: flex; align-items: center; gap: 12px; color: #fff; }
.header-right .el-avatar { box-shadow: 0 0 0 2px rgba(255,255,255,.3); }
.aside {
  background: #fff; border-right: 1px solid #ebeef5; overflow-y: auto;
  box-shadow: 2px 0 8px rgba(0,0,0,.04);
}
.side-menu { border-right: none; background: transparent; padding-top: 8px; font-size: 16px; }
.side-menu :deep(.el-menu-item) { font-size: 16px; height: 52px; line-height: 52px; }
.course-list { padding: 16px; border-top: 1px solid #ebeef5; }
.course-title {
  font-size: 17px; font-weight: 600; padding: 14px 12px; cursor: pointer;
  color: #303133; border-radius: 8px; margin-bottom: 6px;
  transition: all .2s ease;
}
.course-title:hover { background: #eff6ff; color: #3B82F6; }
.chapter-title {
  font-weight: 600; margin: 10px 0 6px 12px; font-size: 15px; color: #606266;
  transition: all .2s ease;
}
.section-item {
  padding: 10px 16px; cursor: pointer; border-radius: 8px;
  font-size: 15px; margin-left: 20px; color: #606266; transition: all .25s ease;
  position: relative;
}
.section-item:hover { background: #eff6ff; color: #3B82F6; }
.section-item.active {
  background: #3B82F6;
  color: #fff; font-weight: 500;
  box-shadow: 0 3px 10px rgba(59,130,246,.25);
}
.content { padding: 24px; background: #f5f7fa; }
</style>
