#!/bin/bash
# ============================================================
# APEX SPEED LABS - 每日自动汇报系统 v1.0
# 完全自动运行 - 无需MacBook
# ============================================================

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID}"
ADMIN_EMAIL="${ADMIN_EMAIL:-sweeyuen3@gmail.com}"
LOG_DIR="/root/apex-automation/logs"
REPORT_FILE="/tmp/daily_report_$(date +%Y%m%d).txt"

# 颜色定义
GREEN='✅'
RED='❌'
YELLOW='⚠️'
ROCKET='🚀'

# ============================================================
# 发送Telegram消息
# ============================================================
send_telegram() {
    local message="$1"
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            -d "text=${message}" \
            -d "parse_mode=HTML" > /dev/null 2>&1
        echo "[TG SENT] $(date)"
    else
        echo "[TG SKIP] No token configured"
    fi
}

# ============================================================
# 发送邮件
# ============================================================
send_email() {
    local subject="$1"
    local body="$2"
    if [ -n "$ADMIN_EMAIL" ]; then
        echo "$body" | mail -s "$subject" "$ADMIN_EMAIL" 2>/dev/null || \
        echo "$body" | sendmail "$ADMIN_EMAIL" 2>/dev/null
        echo "[EMAIL SENT] $subject"
    else
        echo "[EMAIL SKIP] No email configured"
    fi
}

# ============================================================
# 1. 系统健康状态
# ============================================================
check_system_health() {
    echo "=== 系统健康状态 ==="
    
    # CPU使用率
    CPU_USAGE=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    if (( $(echo "$CPU_USAGE < 80" | bc -l) )); then
        echo "$GREEN CPU: ${CPU_USAGE}%"
    else
        echo "$RED CPU: ${CPU_USAGE}% (过高)"
    fi
    
    # 内存使用率
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100}')
    if (( $(echo "$MEM_USAGE < 85" | bc -l) )); then
        echo "$GREEN 内存: ${MEM_USAGE}%"
    else
        echo "$RED 内存: ${MEM_USAGE}% (过高)"
    fi
    
    # 磁盘空间
    DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -lt 85 ]; then
        echo "$GREEN 磁盘: ${DISK_USAGE}%"
    else
        echo "$RED 磁盘: ${DISK_USAGE}% (不足)"
    fi
    
    # 进程数量
    PROC_COUNT=$(ps aux | wc -l)
    echo "📊 进程数: $PROC_COUNT"
}

# ============================================================
# 2. 云服务状态
# ============================================================
check_cloud_services() {
    echo ""
    echo "=== 云服务状态 ==="
    
    # Apex Brain
    if curl -s -o /dev/null -w "%{http_code}" https://apex-brain.sweeyuen3.workers.dev | grep -q "200"; then
        echo "$GREEN Apex Brain: 在线"
    else
        echo "$RED Apex Brain: 离线"
    fi
    
    # Leads Improvement
    if curl -s -o /dev/null -w "%{http_code}" https://leads-improvement.sweeyuen3.workers.dev | grep -q "200"; then
        echo "$GREEN Leads Improvement: 在线"
    else
        echo "$RED Leads Improvement: 离线"
    fi
}

# ============================================================
# 3. 自动化执行统计
# ============================================================
check_automation_stats() {
    echo ""
    echo "=== 今日自动化执行 ==="
    
    for log in upwork linkedin twitter tiktok youtube xiaohongshu instagram facebook usdc; do
        LOG_FILE="$LOG_DIR/${log}.log"
        TODAY_COUNT=0
        if [ -f "$LOG_FILE" ]; then
            TODAY_COUNT=$(grep "$(date +%Y-%m-%d)" "$LOG_FILE" | wc -l)
        fi
        echo "📝 ${log}: $TODAY_COUNT 次执行"
    done
}

# ============================================================
# 4. 收入监控
# ============================================================
check_revenue() {
    echo ""
    echo "=== 收入状态 ==="
    
    # Stripe检查
    if command -v python3 &> /dev/null; then
        python3 -c "
import os
import requests
stripe_key = os.getenv('STRIPE_SECRET_KEY', '')
if stripe_key:
    resp = requests.get('https://api.stripe.com/v1/balance', auth=(stripe_key, ''))
    if resp.status_code == 200:
        data = resp.json()
        available = data['available'][0]['amount'] / 100
        print(f'$GREEN Stripe余额: \${available}')
    else:
        print('$RED Stripe: 检查失败')
else:
    print('$YELLOW Stripe: 未配置')
"
    fi
    
    # USDC监控
    echo "$YELLOW USDC监控: 每15分钟检查"
}

# ============================================================
# 5. 待办事项
# ============================================================
check_todos() {
    echo ""
    echo "=== 今日待办 ==="
    
    # 检查新客户
    NEW_LEADS=$(grep -c "$(date +%Y-%m-%d)" "$LOG_DIR/leads.log" 2>/dev/null || echo "0")
    echo "📋 新线索: $NEW_LEADS"
    
    # 检查待跟进
    echo "📋 需要跟进: 联系潜在客户"
}

# ============================================================
# 主程序 - 生成报告
# ============================================================
generate_report() {
    cat > "$REPORT_FILE" << 'HEADER'
╔══════════════════════════════════════════════════════════════╗
║           APEX SPEED LABS - 每日自动汇报                    ║
║                   MONEY BREEDING MACHINE                     ║
╚══════════════════════════════════════════════════════════════╝

HEADER
    
    check_system_health >> "$REPORT_FILE"
    check_cloud_services >> "$REPORT_FILE"
    check_automation_stats >> "$REPORT_FILE"
    check_revenue >> "$REPORT_FILE"
    check_todos >> "$REPORT_FILE"
    
    cat >> "$REPORT_FILE" << 'FOOTER'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 目标进度
   • 本周收入目标: $500 - $2000
   • 潜在客户: 持续开发中
   • 自动化系统: 全天候运行中

🔗 重要链接
   • Apex Brain: https://apex-brain.sweeyuen3.workers.dev
   • Leads Improvement: https://leads-improvement.sweeyuen3.workers.dev
   • Stripe Dashboard: https://dashboard.stripe.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
报告生成时间: DATE_PLACEHOLDER
VPS: 167.71.120.132 | 状态: FULL AUTO MODE
FOOTER
    
    sed -i "s/DATE_PLACEHOLDER/$(date '+%Y-%m-%d %H:%M:%S')/" "$REPORT_FILE"
}

# ============================================================
# 发送报告
# ============================================================
send_reports() {
    local telegram_msg="
$ROCKET <b>APEX SPEED LABS - 每日汇报</b>
$(date '+%Y-%m-%d %H:%M')

<b>系统状态:</b>
$(check_system_health | grep -E '✅|❌|⚠️')

<b>云服务:</b>
$(check_cloud_services | grep -E '✅|❌|⚠️')

<b>今日自动化:</b>
$(grep -c "$(date +%Y-%m-%d)" "$LOG_DIR"/*.log 2>/dev/null | awk -F: '{sum+=$2} END {print "总执行: " sum " 次"}')

💰 目标: 本周 \$500-2000
⚡ 状态: FULL AUTO MODE
"
    
    send_telegram "$telegram_msg"
    
    if [ -f "$REPORT_FILE" ]; then
        send_email "[Apex] 每日自动化汇报 $(date +%Y%m%d)" "$(cat $REPORT_FILE)"
    fi
}

# ============================================================
# 执行
# ============================================================
echo "[$(date)] 开始生成每日汇报..."
generate_report
send_reports
echo "[$(date)] 汇报已发送!"
