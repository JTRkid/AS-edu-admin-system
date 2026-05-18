#!/bin/bash
# ============================================================
# 实验评分脚本 - 在虚拟机中运行，对学生实验进行评分
# 评分完成后通过 HTTP POST 将成绩发送到教学平台
# ============================================================

# ---------- 配置区 ----------
# 教学平台地址
PLATFORM_URL="http://127.0.0.1:8000"
# 和服务器上 settings.py 里的 SCORING_MACHINE_API_KEY 一致
API_KEY="scoring-machine-secret-key-2026"  

# 章节信息（固定）
CHAPTER_NO=1
CHAPTER_NAME="Python基础"
SECTION_NO=1
SECTION_NAME="Python简介与环境搭建"
COURSE_NAME="Python程序设计"

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
DETAILS=""

# --- 评分项1: 检查文件是否存在 ---
echo "[1/5] 检查实验文件..."
if [ -f "./hello.py" ]; then
    SCORE=$((SCORE + 20))
    DETAILS="${DETAILS}文件检查通过(+20); "
    echo "  [通过] hello.py 存在 (+20)"
else
    DETAILS="${DETAILS}文件检查失败: hello.py 不存在; "
    echo "  [失败] hello.py 不存在"
fi

# --- 评分项2: 检查语法是否正确 ---
echo "[2/5] 检查Python语法..."
if python3 -m py_compile hello.py 2>/dev/null; then
    SCORE=$((SCORE + 20))
    DETAILS="${DETAILS}语法检查通过(+20); "
    echo "  [通过] 语法正确 (+20)"
else
    DETAILS="${DETAILS}语法检查失败; "
    echo "  [失败] 语法错误"
fi

# --- 评分项3: 运行脚本检查输出 ---
echo "[3/5] 运行脚本检查输出..."
OUTPUT=$(python3 hello.py 2>&1)
if echo "$OUTPUT" | grep -q "Hello"; then
    SCORE=$((SCORE + 20))
    DETAILS="${DETAILS}输出包含Hello(+20); "
    echo "  [通过] 输出包含 'Hello' (+20)"
else
    DETAILS="${DETAILS}输出不包含Hello; "
    echo "  [失败] 输出不包含 'Hello'"
fi

# --- 评分项4: 检查代码风格 ---
echo "[4/5] 检查代码风格..."
LINE_COUNT=$(wc -l < hello.py 2>/dev/null || echo 0)
if [ "$LINE_COUNT" -ge 3 ]; then
    SCORE=$((SCORE + 20))
    DETAILS="${DETAILS}代码行数>=3(+20); "
    echo "  [通过] 代码行数 ${LINE_COUNT} >= 3 (+20)"
else
    DETAILS="${DETAILS}代码行数不足; "
    echo "  [失败] 代码行数 ${LINE_COUNT} < 3"
fi

# --- 评分项5: 加分项 ---
echo "[5/5] 检查加分项..."
if [ -f "./README.md" ]; then
    SCORE=$((SCORE + 20))
    DETAILS="${DETAILS}包含README.md(+20); "
    echo "  [通过] 包含 README.md (+20)"
else
    DETAILS="${DETAILS}无README.md; "
    echo "  [跳过] 无 README.md"
fi

# ---------- 发送成绩到平台 ----------
echo ""
echo "========================================"
echo "  评分完成，总分: ${SCORE}"
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
echo "最终成绩: ${SCORE}/100"
exit 0
