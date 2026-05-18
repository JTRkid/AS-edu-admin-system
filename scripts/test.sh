#!/bin/bash
# ============================================================
#  实验评分脚本模板
#  在虚拟机中运行，对学生实验进行自动化评分
#  评分完成后通过 HTTP POST 将成绩发送到教学平台
# ============================================================

# ============================================================
# >>> 部署时需要修改的配置区 <<<
# ============================================================

# 【必改】教学平台后端地址（含端口）
PLATFORM_URL="http://127.0.0.1:8000"

# 【必改】API 密钥，需与平台 settings.py 中的 SCORING_MACHINE_API_KEY 一致
API_KEY="scoring-machine-secret-key-2026"

# 【必改】课程信息 — 需与平台上创建的课程/章/节对应
COURSE_NAME="Python程序设计"      # 课程名称（用于多课程场景精确匹配）
CHAPTER_NO=1                       # 章序号
CHAPTER_NAME="Python基础"           # 章名称
SECTION_NO=1                        # 节序号
SECTION_NAME="Python简介与环境搭建"  # 节名称

# ============================================================
# >>> 以下为评分逻辑，根据实验要求修改 <<<
# ============================================================

# ---------- 从键盘读取学生信息 ----------
echo "========================================"
echo "  实验评分脚本"
echo "  章节: 第${CHAPTER_NO}章 ${SECTION_NO}节 - ${SECTION_NAME}"
echo "========================================"
echo ""
read -p "请输入学号: " STUDENT_NO
read -p "请输入姓名: " STUDENT_NAME
read -p "请输入班级: " CLASS_NAME
echo ""

# ---------- 评分逻辑 ----------
SCORE=0
TOTAL=0  # 总分值，根据评分项数量累加
DETAILS=""

# ============================================================
# 评分项示例 — 按需增删改
# 每个评分项结构:
#   1. 输出检查进度
#   2. 执行检查逻辑
#   3. 根据结果累加 SCORE 和 TOTAL
#   4. 拼接 DETAILS 详情字符串
# ============================================================

# --- 评分项1: 检查文件是否存在 ---
# 【按需修改】检查的文件名
CHECK_FILE="hello.py"
echo "[1/2] 检查实验文件 ${CHECK_FILE}..."
TOTAL=$((TOTAL + 50))
if [ -f "./${CHECK_FILE}" ]; then
    SCORE=$((SCORE + 50))
    DETAILS="${DETAILS}${CHECK_FILE}存在(+50); "
    echo "  [通过] ${CHECK_FILE} 存在 (+50)"
else
    DETAILS="${DETAILS}${CHECK_FILE}不存在; "
    echo "  [失败] ${CHECK_FILE} 不存在"
fi

# --- 评分项2: 运行脚本检查输出 ---
# 【按需修改】执行的命令和期望的关键词
RUN_CMD="python3 hello.py"
EXPECT_KEYWORD="Hello"
echo "[2/2] 运行脚本检查输出..."
TOTAL=$((TOTAL + 50))
OUTPUT=$(${RUN_CMD} 2>&1)
if echo "$OUTPUT" | grep -q "${EXPECT_KEYWORD}"; then
    SCORE=$((SCORE + 50))
    DETAILS="${DETAILS}输出包含'${EXPECT_KEYWORD}'(+50); "
    echo "  [通过] 输出包含 '${EXPECT_KEYWORD}' (+50)"
else
    DETAILS="${DETAILS}输出不包含'${EXPECT_KEYWORD}'; "
    echo "  [失败] 输出不包含 '${EXPECT_KEYWORD}'"
fi

# ============================================================
# 新增评分项模板（复制以下代码块，修改对应内容即可）
# ============================================================
#
# echo "[N/总数] 检查项描述..."
# TOTAL=$((TOTAL + 分值))
# if [ 条件 ]; then
#     SCORE=$((SCORE + 分值))
#     DETAILS="${DETAILS}检查项描述(+分值); "
#     echo "  [通过] 检查项描述 (+分值)"
# else
#     DETAILS="${DETAILS}检查项描述(失败); "
#     echo "  [失败] 检查项描述"
# fi
#
# ============================================================


# ---------- 发送成绩到平台（无需修改） ----------
echo ""
echo "========================================"
echo "  评分完成，总分: ${SCORE}/${TOTAL}"
echo "  正在发送成绩到教学平台..."
echo "========================================"

# 将 JSON 写入临时文件以避免中文编码问题
JSON_FILE=$(mktemp)
cat > "$JSON_FILE" <<JSONEOF
{
    "student_no": "${STUDENT_NO}",
    "student_name": "${STUDENT_NAME}",
    "class_name": "${CLASS_NAME}",
    "course_name": "${COURSE_NAME}",
    "chapter_no": ${CHAPTER_NO},
    "section_no": ${SECTION_NO},
    "chapter_name": "${CHAPTER_NAME}",
    "section_name": "${SECTION_NAME}",
    "score": ${SCORE},
    "evaluator": "exp-script-v1",
    "details": "${DETAILS}"
}
JSONEOF

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${PLATFORM_URL}/api/v1/scores/submit/" \
    -H "Authorization: ApiKey ${API_KEY}" \
    -H "Content-Type: application/json; charset=utf-8" \
    --data-binary "@${JSON_FILE}")
rm -f "$JSON_FILE"

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "  [成功] 成绩已提交到平台"
    echo "  响应: ${BODY}"
else
    echo "  [失败] HTTP ${HTTP_CODE}"
    echo "  响应: ${BODY}"
fi

echo ""
echo "最终成绩: ${SCORE}/${TOTAL}"
exit 0
