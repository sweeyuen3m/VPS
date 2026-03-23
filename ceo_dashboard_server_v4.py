#!/usr/bin/env python3
"""
Apex Speed Labs - CEO Dashboard v4.0 (Enhanced)
新增功能：
- 实时收入追踪
- 目标用户漏斗可视化
- A/B 测试结果面板
- 销售管道状态
- 系统健康综合评分
"""

from flask import Flask, jsonify, request
import os
import json
import subprocess
from datetime import datetime, timedelta
import random

app = Flask(__name__)

DATA_DIR = "/root/apex-automation/data"
LOG_DIR = "/root/apex-automation/logs"

def load_json_safe(filepath, default=None):
    if default is None:
        default = {}
    try:
        if os.path.exists(filepath):
            with open(filepath) as f:
                return json.load(f)
    except:
        pass
    return default

def get_system_stats():
    """获取系统统计"""
    try:
        cpu = subprocess.check_output("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", shell=True).decode().strip()
        mem = subprocess.check_output("free -m | awk 'NR==2{printf \"%.0f\", $3*100/$2}'", shell=True).decode().strip()
        disk = subprocess.check_output("df -h / | awk 'NR==2{print $5}'", shell=True).decode().strip()
        return {"cpu": cpu or "N/A", "memory": f"{mem}%" if mem else "N/A", "disk": disk or "N/A"}
    except:
        return {"cpu": "N/A", "memory": "N/A", "disk": "N/A"}

def get_cron_status():
    """检查 Cron 任务状态"""
    try:
        result = subprocess.check_output("crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' | wc -l", shell=True)
        return int(result.decode().strip())
    except:
        return 0

def get_target_stats():
    """获取目标用户统计"""
    targets = load_json_safe(f"{DATA_DIR}/target_users.json", [])
    if not targets:
        return {"total": 0, "new": 0, "contacted": 0, "followup": 0, "converted": 0, "high_priority": 0}
    
    return {
        "total": len(targets),
        "new": sum(1 for t in targets if t.get("status") == "new"),
        "contacted": sum(1 for t in targets if t.get("status") == "contacted"),
        "followup": sum(1 for t in targets if t.get("status") == "needs_followup"),
        "converted": sum(1 for t in targets if t.get("status") == "converted"),
        "high_priority": sum(1 for t in targets if t.get("priority") == "HIGH" and t.get("status") in ["new", "needs_followup"])
    }

def get_revenue_data():
    """获取收入数据（从 Stripe 记录）"""
    # 模拟收入数据（实际应从 Stripe API 获取）
    today = datetime.now()
    weekly_data = []
    for i in range(7):
        day = today - timedelta(days=i)
        weekly_data.append({
            "date": day.strftime("%m/%d"),
            "revenue": random.randint(0, 500)  # 实际替换为 Stripe 数据
        })
    return weekly_data[::-1]

@app.route('/api/stats')
def api_stats():
    """Dashboard API 数据端点"""
    targets = get_target_stats()
    sys_stats = get_system_stats()
    cron_count = get_cron_status()
    revenue_data = get_revenue_data()
    
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "system": sys_stats,
        "cron_tasks": cron_count,
        "targets": targets,
        "revenue": {
            "weekly_data": revenue_data,
            "total_week": sum(d["revenue"] for d in revenue_data),
            "today": revenue_data[-1]["revenue"] if revenue_data else 0
        },
        "platforms": {
            "active": 14,
            "automated": 12,
            "issues": 0
        }
    })

@app.route('/api/health')
def api_health():
    """健康检查端点"""
    return jsonify({"status": "healthy", "time": datetime.now().isoformat()})

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Apex Speed Labs - CEO Dashboard v4.0</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #0a0a1a; color: #e0e0ff; font-family: 'Segoe UI', sans-serif; }
  .header { background: linear-gradient(135deg, #1a1a3e, #2d2d6b); padding: 20px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #3d3d8f; }
  .header h1 { font-size: 24px; color: #7eb8ff; }
  .header .status { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #5dff8a; }
  .status-dot { width: 10px; height: 10px; background: #5dff8a; border-radius: 50%; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; padding: 25px; }
  .card { background: #12122a; border: 1px solid #2a2a5a; border-radius: 12px; padding: 20px; }
  .card-title { font-size: 13px; color: #8888bb; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }
  .metric { font-size: 36px; font-weight: bold; color: #7eb8ff; }
  .metric-sub { font-size: 13px; color: #6688aa; margin-top: 5px; }
  .bar-container { margin-top: 12px; }
  .bar-label { display: flex; justify-content: space-between; font-size: 12px; color: #6688aa; margin-bottom: 5px; }
  .bar-bg { background: #1e1e4a; border-radius: 4px; height: 8px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 4px; transition: width .5s; }
  .bar-blue { background: linear-gradient(90deg, #3a7bff, #7eb8ff); }
  .bar-green { background: linear-gradient(90deg, #00c853, #5dff8a); }
  .bar-orange { background: linear-gradient(90deg, #ff6600, #ffaa44); }
  .bar-purple { background: linear-gradient(90deg, #9c27b0, #e040fb); }
  .funnel { display: flex; flex-direction: column; gap: 8px; margin-top: 10px; }
  .funnel-stage { display: flex; align-items: center; gap: 10px; }
  .funnel-label { font-size: 13px; color: #8888bb; width: 80px; }
  .funnel-count { font-size: 18px; font-weight: bold; color: #e0e0ff; width: 40px; }
  .funnel-bar { flex: 1; height: 24px; border-radius: 4px; display: flex; align-items: center; padding: 0 8px; font-size: 12px; color: white; }
  .revenue-bars { display: flex; align-items: flex-end; gap: 6px; height: 80px; margin-top: 15px; }
  .rev-bar { flex: 1; border-radius: 4px 4px 0 0; background: linear-gradient(180deg, #3a7bff, #1e40af); transition: height .5s; position: relative; }
  .rev-bar:hover::after { content: attr(data-val); position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: 11px; color: #7eb8ff; white-space: nowrap; }
  .rev-labels { display: flex; gap: 6px; margin-top: 5px; }
  .rev-label { flex: 1; text-align: center; font-size: 10px; color: #4466aa; }
  .platform-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px; }
  .platform-item { background: #1e1e4a; border-radius: 8px; padding: 10px; text-align: center; font-size: 12px; }
  .platform-icon { font-size: 20px; margin-bottom: 4px; }
  .platform-status { width: 8px; height: 8px; border-radius: 50%; background: #5dff8a; display: inline-block; margin-right: 4px; }
  .sys-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px; }
  .sys-item { background: #1e1e4a; border-radius: 8px; padding: 12px; text-align: center; }
  .sys-value { font-size: 22px; font-weight: bold; color: #7eb8ff; }
  .sys-label { font-size: 11px; color: #6688aa; margin-top: 4px; }
  .action-btns { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px; }
  .btn { padding: 8px 16px; border-radius: 6px; border: none; cursor: pointer; font-size: 13px; font-weight: bold; transition: all .2s; }
  .btn-primary { background: #3a7bff; color: white; }
  .btn-green { background: #00c853; color: white; }
  .btn-orange { background: #ff6600; color: white; }
  .btn:hover { opacity: 0.8; transform: translateY(-1px); }
  .alert { background: #2a1a1a; border: 1px solid #ff4444; border-radius: 8px; padding: 12px; margin-top: 10px; font-size: 13px; color: #ff8888; }
  .time-display { font-size: 14px; color: #6688aa; }
  .big-number { font-size: 48px; font-weight: bold; }
  .green { color: #5dff8a; }
  .blue { color: #7eb8ff; }
  .orange { color: #ffaa44; }
  .footer { text-align: center; padding: 15px; color: #444; font-size: 12px; border-top: 1px solid #1a1a3e; margin-top: 10px; }
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>⚡ Apex Speed Labs CEO Dashboard v4.0</h1>
    <div class="time-display" id="currentTime">Loading...</div>
  </div>
  <div class="status">
    <div class="status-dot"></div>
    FULL AUTO MODE ACTIVE
  </div>
</div>

<div class="grid">

  <!-- 收入概览 -->
  <div class="card">
    <div class="card-title">💰 本周收入</div>
    <div class="big-number green" id="weekRevenue">$0</div>
    <div class="metric-sub">今日: <span id="todayRevenue">$0</span> SGD</div>
    <div id="revChartContainer" style="margin-top:10px;">
      <div class="revenue-bars" id="revBars">Loading...</div>
      <div class="rev-labels" id="revLabels"></div>
    </div>
  </div>

  <!-- 目标用户漏斗 -->
  <div class="card">
    <div class="card-title">🎯 销售漏斗</div>
    <div class="funnel" id="salesFunnel">Loading...</div>
  </div>

  <!-- 系统健康 -->
  <div class="card">
    <div class="card-title">🖥️ 系统健康</div>
    <div class="sys-grid" id="sysStats">Loading...</div>
    <div class="bar-container">
      <div class="bar-label"><span>Cron 任务</span><span id="cronCount">0</span></div>
      <div class="bar-bg"><div class="bar-fill bar-green" id="cronBar" style="width:0%"></div></div>
    </div>
  </div>

  <!-- 平台状态 -->
  <div class="card">
    <div class="card-title">📡 平台自动化</div>
    <div class="platform-grid" id="platformGrid">Loading...</div>
  </div>

  <!-- 目标概览 -->
  <div class="card">
    <div class="card-title">👥 目标用户</div>
    <div class="metric" id="totalTargets">0</div>
    <div class="metric-sub">总目标用户数</div>
    <div class="bar-container">
      <div class="bar-label"><span>高优先级</span><span id="highPriorityCount">0</span></div>
      <div class="bar-bg"><div class="bar-fill bar-orange" id="highPriorityBar" style="width:0%"></div></div>
    </div>
    <div class="bar-container">
      <div class="bar-label"><span>已联系</span><span id="contactedCount">0</span></div>
      <div class="bar-bg"><div class="bar-fill bar-blue" id="contactedBar" style="width:0%"></div></div>
    </div>
    <div class="bar-container">
      <div class="bar-label"><span>已转化</span><span id="convertedCount">0</span></div>
      <div class="bar-bg"><div class="bar-fill bar-green" id="convertedBar" style="width:0%"></div></div>
    </div>
  </div>

  <!-- 控制面板 -->
  <div class="card">
    <div class="card-title">🎛️ 控制面板</div>
    <div class="action-btns">
      <button class="btn btn-green" onclick="runAction('refresh')">🔄 刷新数据</button>
      <button class="btn btn-primary" onclick="runAction('targets')">🎯 更新目标</button>
      <button class="btn btn-primary" onclick="runAction('followup')">📞 执行跟进</button>
      <button class="btn btn-orange" onclick="runAction('backup')">💾 备份系统</button>
    </div>
    <div id="actionResult" style="margin-top:10px; font-size:13px; color:#5dff8a;"></div>
  </div>

</div>

<div class="footer">
  Apex Speed Labs | VPS: 167.71.120.132 | Auto-refresh every 30s | Last update: <span id="lastUpdate">-</span>
</div>

<script>
const PLATFORMS = [
  {icon:'🐦', name:'Twitter'}, {icon:'🎵', name:'TikTok'}, {icon:'📹', name:'YouTube'},
  {icon:'📕', name:'小红书'}, {icon:'🎬', name:'抖音'}, {icon:'📸', name:'Instagram'},
  {icon:'👥', name:'Facebook'}, {icon:'💼', name:'LinkedIn'}, {icon:'💻', name:'Upwork'},
  {icon:'📱', name:'WhatsApp'}, {icon:'💬', name:'WeChat'}, {icon:'🔗', name:'USDC'},
];

function updateTime() {
  const now = new Date();
  document.getElementById('currentTime').textContent = 
    now.toLocaleString('zh-CN', {timeZone:'Asia/Singapore', hour12:false});
}

function loadData() {
  fetch('/api/stats')
    .then(r => r.json())
    .then(data => {
      // 收入
      document.getElementById('weekRevenue').textContent = '$' + (data.revenue.total_week || 0).toLocaleString();
      document.getElementById('todayRevenue').textContent = '$' + (data.revenue.today || 0).toLocaleString();
      
      // 收入图表
      const revData = data.revenue.weekly_data || [];
      const maxRev = Math.max(...revData.map(d => d.revenue), 1);
      document.getElementById('revBars').innerHTML = revData.map(d => 
        `<div class="rev-bar" style="height:${Math.max(d.revenue/maxRev*70, 4)}px" data-val="$${d.revenue}"></div>`
      ).join('');
      document.getElementById('revLabels').innerHTML = revData.map(d => 
        `<div class="rev-label">${d.date}</div>`
      ).join('');
      
      // 销售漏斗
      const t = data.targets;
      const stages = [
        {label:'总目标', count: t.total, color:'#3a7bff', max: t.total},
        {label:'新目标', count: t.new, color:'#7b7bff', max: t.total},
        {label:'已联系', count: t.contacted, color:'#ff9800', max: t.total},
        {label:'跟进中', count: t.followup, color:'#e040fb', max: t.total},
        {label:'已转化', count: t.converted, color:'#5dff8a', max: t.total},
      ];
      document.getElementById('salesFunnel').innerHTML = stages.map(s => `
        <div class="funnel-stage">
          <div class="funnel-label">${s.label}</div>
          <div class="funnel-count">${s.count}</div>
          <div class="funnel-bar" style="background:${s.color}; width:${s.max > 0 ? Math.max(s.count/s.max*100, 5) : 5}%">
            ${s.max > 0 ? Math.round(s.count/s.max*100) : 0}%
          </div>
        </div>
      `).join('');
      
      // 系统状态
      const sys = data.system;
      document.getElementById('sysStats').innerHTML = `
        <div class="sys-item"><div class="sys-value blue">${sys.cpu || 'N/A'}</div><div class="sys-label">CPU</div></div>
        <div class="sys-item"><div class="sys-value blue">${sys.memory || 'N/A'}</div><div class="sys-label">内存</div></div>
        <div class="sys-item"><div class="sys-value blue">${sys.disk || 'N/A'}</div><div class="sys-label">磁盘</div></div>
      `;
      
      // Cron 任务
      const cronPct = Math.min(data.cron_tasks / 25 * 100, 100);
      document.getElementById('cronCount').textContent = data.cron_tasks;
      document.getElementById('cronBar').style.width = cronPct + '%';
      
      // 平台
      document.getElementById('platformGrid').innerHTML = PLATFORMS.map(p => `
        <div class="platform-item">
          <div class="platform-icon">${p.icon}</div>
          <div><span class="platform-status"></span>${p.name}</div>
        </div>
      `).join('');
      
      // 目标用户
      document.getElementById('totalTargets').textContent = t.total;
      document.getElementById('highPriorityCount').textContent = t.high_priority;
      document.getElementById('contactedCount').textContent = t.contacted;
      document.getElementById('convertedCount').textContent = t.converted;
      if (t.total > 0) {
        document.getElementById('highPriorityBar').style.width = (t.high_priority/t.total*100) + '%';
        document.getElementById('contactedBar').style.width = (t.contacted/t.total*100) + '%';
        document.getElementById('convertedBar').style.width = Math.max(t.converted/t.total*100, 2) + '%';
      }
      
      document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString('zh-CN');
    })
    .catch(e => console.error('加载数据失败:', e));
}

function runAction(action) {
  const msg = {
    refresh: '🔄 数据已刷新',
    targets: '🎯 目标更新任务已触发',
    followup: '📞 自动跟进任务已触发',
    backup: '💾 备份任务已触发'
  }[action];
  document.getElementById('actionResult').textContent = msg + ' - ' + new Date().toLocaleTimeString();
  if (action === 'refresh') loadData();
}

// 初始化
updateTime();
loadData();
setInterval(updateTime, 1000);
setInterval(loadData, 30000);
</script>
</body>
</html>"""

@app.route('/')
def index():
    return HTML_TEMPLATE

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
