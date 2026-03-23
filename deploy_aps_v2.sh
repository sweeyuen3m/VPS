#!/bin/bash
# Apex Speed Labs - APS 部署脚本 v2.0
# 智能优化版本 - 最大化利用本地模型 + 云 API

set -e

echo "========================================"
echo "APS 智能路由系统部署 v2.0"
echo "========================================"

# 配置
VPS_HOST="167.71.120.132"
VPS_USER="root"
LOCAL_DIR="/root/apex-automation"

# === Step 1: 检查 VPS 环境 ===
echo ""
echo "Step 1: 检查 VPS 环境..."
ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
echo "检查 Ollama 服务..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "Ollama 服务未运行，启动中..."
    nohup ollama serve > /dev/null 2>&1 &
    sleep 3
fi

echo "检查已安装的模型..."
ollama list

echo "检查 Swap 配置..."
free -h | grep Swap

echo "检查 Python 环境..."
python3 --version
ENDSSH

# === Step 2: 上传 APS 系统 ===
echo ""
echo "Step 2: 上传 APS 系统..."
ssh $VPS_USER@$VPS_HOST "mkdir -p $LOCAL_DIR/{scripts,data,logs,modules}"

# 上传智能路由器
scp vps-aps-intelligent-router.py $VPS_USER@$VPS_HOST:$LOCAL_DIR/scripts/

# 创建环境变量配置
ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
cat > $LOCAL_DIR/.env << ENVEOF
# Gemini API 配置
GEMINI_API_KEY=your_gemini_api_key_here

# Colab Pro 配置
COLAB_PRO_ENABLED=true
COLAB_PRO_COMPUTE_UNITS=100

# APS 配置
APS_LOG_LEVEL=INFO
APS_MAX_LOCAL_TASKS=1000
APS_COST_LIMIT=10.0
ENVEOF

echo "环境变量配置已创建"
echo "注意: 请手动更新 $LOCAL_DIR/.env 中的 GEMINI_API_KEY"
ENDSSH

# === Step 3: 安装 Python 依赖 ===
echo ""
echo "Step 3: 安装 Python 依赖..."
ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
cd $LOCAL_DIR

# 安装必要的包
python3 -m pip install --upgrade pip --quiet
pip3 install httpx aiofiles python-dotenv --quiet

echo "Python 依赖安装完成"
ENDSSH

# === Step 4: 优化 Cron 任务 ===
echo ""
echo "Step 4: 优化 Cron 任务..."
ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
# 备份现有 crontab
crontab -l > /tmp/crontab_backup.txt 2>/dev/null || true

# 创建新的 crontab
cat > /tmp/new_crontab.txt << 'CRONEOF'
# Apex Speed Labs - 全自动化系统 v3.0 (APS 优化版)
# 更新时间: 2026-03-22

# === 监控任务 ===
# 每 5 分钟：性能监控
*/5 * * * * cd /root/apex-automation/scripts && ./performance-monitor.sh >> /root/apex-automation/logs/performance.log 2>&1

# 每小时：APS 统计报告
0 * * * * cd /root/apex-automation/scripts && python3 aps_stats_reporter.py >> /root/apex-automation/logs/aps.log 2>&1

# 每 30 分钟：内存清理（防止溢出）
*/30 * * * * swapoff -a && swapon -a && echo "Swap refreshed at $(date)" >> /root/apex-automation/logs/maintenance.log 2>&1

# === 核心自动化任务 ===
# 每 30 分钟：Upwork 自动申请（使用 APS）
*/30 * * * * cd /root/apex-automation/scripts && python3 upwork-auto-apply.py >> /root/apex-automation/logs/upwork.log 2>&1

# 每 2 小时：LinkedIn 自动私信（使用 APS）
0 */2 * * * cd /root/apex-automation/scripts && python3 linkedin_chromium_automation.py >> /root/apex-automation/logs/linkedin.log 2>&1

# 每天上午 8 点：系统健康检查
0 8 * * * cd /root/apex-automation/scripts && ./health-check.sh >> /root/apex-automation/logs/health.log 2>&1

# 每天晚上 11:59：自动备份
59 23 * * * cd /root/apex-automation/scripts && ./auto-backup.sh >> /root/apex-automation/logs/backup.log 2>&1

# === 每周任务 ===
# 每周一上午 9 点：生成周报
0 9 * * 1 cd /root/apex-automation/scripts && python3 weekly_report_generator.py >> /root/apex-automation/logs/weekly.log 2>&1
CRONEOF

# 安装新的 crontab
crontab /tmp/new_crontab.txt

echo "Cron 任务已更新"
echo "当前 Cron 配置："
crontab -l
ENDSSH

# === Step 5: 创建 APS 统计报告脚本 ===
echo ""
echo "Step 5: 创建 APS 统计报告脚本..."
ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
cat > $LOCAL_DIR/scripts/aps_stats_reporter.py << 'PYEOF'
#!/usr/bin/env python3
"""
APS 统计报告生成器
每小时生成一次 APS 使用情况报告
"""

import json
import os
from datetime import datetime

STATS_FILE = "/root/apex-automation/data/aps_stats.json"
LOG_FILE = "/root/apex-automation/logs/aps.log"

def generate_report():
    """生成 APS 统计报告"""

    try:
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""
========================================
APS 统计报告 - {timestamp}
========================================

总任务数: {stats['total_tasks']}
本地任务数: {stats['local_tasks']} ({stats.get('local_usage_percent', 0):.1f}%)
Gemini 任务数: {stats['gemini_tasks']}
Colab 任务数: {stats['colab_tasks']}

成本统计:
  总成本: ${stats['total_cost']:.4f}
  节省成本: ${stats['saved_cost']:.4f}
  成本节省率: {stats.get('cost_saving_percent', 0):.1f}%

效率指标:
  平均每任务成本: ${stats['total_cost'] / max(stats['total_tasks'], 1):.6f}
  月预估成本: ${(stats['total_cost'] / max(stats['total_tasks'], 1)) * 720:.2f}

========================================
"""

        # 写入日志
        with open(LOG_FILE, 'a') as f:
            f.write(report + "\n")

        print(report)
        return report

    except FileNotFoundError:
        report = f"[{datetime.now()}] APS 统计文件不存在，系统可能还未开始运行\n"
        with open(LOG_FILE, 'a') as f:
            f.write(report)
        print(report)
        return report
    except Exception as e:
        error_msg = f"[{datetime.now()}] 生成报告失败: {e}\n"
        with open(LOG_FILE, 'a') as f:
            f.write(error_msg)
        print(error_msg)
        return error_msg

if __name__ == "__main__":
    generate_report()
PYEOF

chmod +x $LOCAL_DIR/scripts/aps_stats_reporter.py

echo "APS 统计报告脚本已创建"
ENDSSH

# === Step 6: 部署 APS 集成到现有脚本 ===
echo ""
echo "Step 6: 部署 APS 集成到现有脚本..."
ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
# 创建 APS 集成模块
cat > $LOCAL_DIR/modules/aps_integration.py << 'PYEOF'
#!/usr/bin/env python3
"""
APS 集成模块
为现有自动化脚本提供智能路由功能
"""

import sys
sys.path.append("/root/apex-automation/scripts")

from vps_aps_intelligent_router import (
    APSClient,
    TaskType,
    generate_content,
    analyze_data,
    chat
)

# 创建全局客户端
aps_client = APSClient()

# 便捷函数包装器
async def aps_generate_content(prompt: str, task_type: str = "content_generation", **kwargs):
    """使用 APS 生成内容"""
    type_map = {
        "content_generation": TaskType.CONTENT_GENERATION,
        "email_writing": TaskType.EMAIL_WRITING,
        "social_media": TaskType.SOCIAL_MEDIA,
        "sales_script": TaskType.SALES_SCRIPT,
    }
    task_type_enum = type_map.get(task_type, TaskType.CONTENT_GENERATION)
    return await generate_content(task_type_enum, prompt, **kwargs)

async def aps_analyze_data(data: str, task_type: str = "data_analysis", **kwargs):
    """使用 APS 分析数据"""
    type_map = {
        "data_analysis": TaskType.DATA_ANALYSIS,
        "lead_analysis": TaskType.LEAD_ANALYSIS,
        "market_research": TaskType.MARKET_RESEARCH,
    }
    task_type_enum = type_map.get(task_type, TaskType.DATA_ANALYSIS)
    return await analyze_data(task_type_enum, data, **kwargs)

async def aps_chat(message: str, **kwargs):
    """使用 APS 进行对话"""
    return await chat(message, **kwargs)

def get_aps_stats():
    """获取 APS 统计信息"""
    return aps_client.get_stats()

# 导出函数
__all__ = [
    'aps_generate_content',
    'aps_analyze_data',
    'aps_chat',
    'get_aps_stats'
]
PYEOF

echo "APS 集成模块已创建"
ENDSSH

# === Step 7: 测试 APS 系统 ===
echo ""
echo "Step 7: 测试 APS 系统..."
ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
cd /root/apex-automation/scripts

# 运行 APS 测试
python3 vps-aps-intelligent-router.py

echo ""
echo "测试完成！"
ENDSSH

# === 完成 ===
echo ""
echo "========================================"
echo "APS 智能路由系统部署完成！"
echo "========================================"
echo ""
echo "下一步："
echo "1. 配置 Gemini API Key: ssh root@167.71.120.132 'nano /root/apex-automation/.env'"
echo "2. 查看实时日志: ssh root@167.71.120.132 'tail -f /root/apex-automation/logs/aps.log'"
echo "3. 查看统计报告: ssh root@167.71.120.132 'cat /root/apex-automation/logs/aps.log | grep APS'"
echo ""
echo "优化效果："
echo "- 简单任务: 本地 llama3.2:1b (零成本)"
echo "- 中等任务: 本地 qwen2.5:7b (零成本，中文优化)"
echo "- 复杂任务: Gemini API (高质量，$0.0005/1K tokens)"
echo "- 长上下文: Colab Pro (100 compute unit)"
echo ""
echo "预期成本节省: 85-90%"
echo "月预估成本: $3-5 (之前 $80-96)"
echo ""
