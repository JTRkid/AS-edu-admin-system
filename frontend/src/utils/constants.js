/** 共享常量 — 题型映射、选项字母、时间格式化 */

// 选项字母映射：0→A, 1→B, ...
export const optionLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

// 题型中文映射
export const typeMap = {
  single: '单选题',
  multiple: '多选题',
  judgment: '判断题',
  essay: '简答题',
}

// 成绩来源中文映射
export const sourceMap = {
  auto_script: '自动评分',
  manual: '手动录入',
  import: 'Excel导入',
  experiment: '实验成绩',
}

/** 时间格式化：ISO字符串 → 中文本地时间 */
export function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}
