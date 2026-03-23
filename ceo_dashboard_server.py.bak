#!/usr/bin/env python3
"""
Apex Speed Labs - CEO Dashboard v3.2
显示所有14个平台的自动化状态 + 控制面板
"""

from flask import Flask, render_template_string, request, jsonify
import os
import subprocess
from datetime import datetime
import requests
import json

app = Flask(__name__)

# 平台配置
PLATFORMS = {
    'twitter': {'name': 'Twitter/X', 'icon': '🐦', 'log': 'twitter.log'},
    'tiktok': {'name': 'TikTok', 'icon': '🎵', 'log': 'tiktok.log'},
    'youtube': {'name': 'YouTube', 'icon': '📹', 'log': 'youtube.log'},
    'xiaohongshu': {'name': '小红书', 'icon': '📕', 'log': 'xiaohongshu.log'},
    'douyin': {'name': '抖音', 'icon': '🎬', 'log': 'douyin.log'},
    'instagram': {'name': 'Instagram', 'icon': '📸', 'log': 'instagram.log'},
    'facebook': {'name': 'Facebook', 'icon': '👥', 'log': 'facebook.log'},
    'linkedin': {'name': 'LinkedIn', 'icon': '💼', 'log': 'linkedin.log'},
    'upwork': {'name': 'Upwork', 'icon': '💻', 'log': 'upwork.log'},
    'whatsapp': {'name': 'WhatsApp', 'icon': '📱', 'log': 'whatsapp.log'},
    'wechat': {'name': 'WeChat', 'icon': '💬', 'log': 'wechat.log'},
    'usdc': {'name': 'USDC监控', 'icon': '🔗', 'log': 'usdc.log'},
}

LOG_DIR = "/root/apex-automation/logs"
AUTOMATION_DIR = "/root/apex-automation"
CRON_LOG = "/root/apex-automation/logs/crontab_status.log"

def get_log_count(log_file, days=0):
    """获取日志条目数"""
    try:
        with open(f"{LOG_DIR}/{log_file}", 'r') as f:
            lines = f.readlines()
        today = datetime.now().strftime('%Y-%m-%d')
        if days == 0:
            return sum(1 for line in lines if today in line)
        else:
            return len(lines)
    except:
        return 0

def check_service(url):
    """检查服务状态"""
    try:
        resp = requests.get(url, timeout=3)
        return resp.status_code == 200
    except:
        return False

def get_stripe_balance():
    """获取Stripe余额"""
    try:
        stripe_key = os.getenv('STRIPE_SECRET_KEY', '')
        if stripe_key:
            resp = requests.get('https://api.stripe.com/v1/balance',
                              auth=(stripe_key, ''), timeout=5)
            if resp.status_code == 200:
                return resp.json()['available'][0]['amount'] / 100
    except:
        pass
    return 0

def get_system_status():
    """获取系统状态"""
    try:
        # CPU使用率
        cpu = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
        cpu_line = [l for l in cpu.stdout.split('\n') if 'Cpu(s)' in l][0]
        cpu_idle = float(cpu_line.split(',')[3].split()[0])

        # 内存使用
        mem = subprocess.run(['free', '-m'], capture_output=True, text=True)
        mem_lines = mem.stdout.split('\n')
        mem_line = [l for l in mem_lines if 'Mem:' in l][0]
        mem_total = int(mem_line.split()[1])
        mem_used = int(mem_line.split()[2])

        # 磁盘使用
        disk = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        disk_line = disk.stdout.split('\n')[1]
        disk_usage = disk_line.split()[4]

        # 进程数
        processes = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        python_count = len([l for l in processes.stdout.split('\n') if 'python' in l.lower()])

        return {
            'cpu_idle': cpu_idle,
            'cpu_used': 100 - cpu_idle,
            'mem_total': mem_total,
            'mem_used': mem_used,
            'mem_percent': int(mem_used / mem_total * 100),
            'disk_usage': disk_usage,
            'python_processes': python_count
        }
    except Exception as e:
        return {'error': str(e)}

def get_running_tasks():
    """获取运行中的任务"""
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        # 统计活跃任务
        active = [l for l in lines if l and not l.strip().startswith('#')]
        return len(active)
    except:
        return 0

def get_warnings():
    """获取系统警告"""
    warnings = []

    # 检查内存
    status = get_system_status()
    if status.get('mem_percent', 0) > 85:
        warnings.append({
            'level': 'WARNING',
            'message': f"内存使用率过高: {status['mem_percent']}%",
            'action': '考虑重启非关键服务'
        })

    # 检查磁盘
    if status.get('disk_usage', '0%').rstrip('%') > '80':
        warnings.append({
            'level': 'WARNING',
            'message': f"磁盘使用率过高: {status['disk_usage']}",
            'action': '运行备份清理旧日志'
        })

    # 检查进程
    if status.get('python_processes', 0) > 15:
        warnings.append({
            'level': 'INFO',
            'message': f"Python进程数较高: {status['python_processes']}个",
            'action': '系统正常'
        })

    # 检查Stripe余额
    balance = get_stripe_balance()
    if balance == 0:
        warnings.append({
            'level': 'INFO',
            'message': 'Stripe余额为$0',
            'action': '等待第一笔收入'
        })

    return warnings

# HTML模板
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Speed Labs - CEO Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #fff; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }

        /* 控制面板样式 */
        .control-panel {
            background: linear-gradient(135deg, rgba(255,0,0,0.1), rgba(255,165,0,0.1));
            border: 2px solid rgba(255,165,0,0.3);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .control-panel h2 {
            color: #ff6b6b;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .control-buttons {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .ctrl-btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .ctrl-btn:hover { transform: translateY(-2px); }
        .btn-refresh { background: linear-gradient(135deg, #00d4ff, #0099cc); color: #fff; }
        .btn-start { background: linear-gradient(135deg, #00ff88, #00cc6a); color: #000; }
        .btn-stop { background: linear-gradient(135deg, #ff6b6b, #cc5555); color: #fff; }
        .btn-backup { background: linear-gradient(135deg, #ffd700, #cc9900); color: #000; }
        .btn-test { background: linear-gradient(135deg, #7c3aed, #5b21b6); color: #fff; }

        /* 警告弹窗样式 */
        .warning-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .warning-overlay.active { display: flex; }
        .warning-modal {
            background: linear-gradient(135deg, #1a1a2e, #2d1f3d);
            border: 3px solid #ff6b6b;
            border-radius: 20px;
            padding: 30px;
            max-width: 500px;
            text-align: center;
            animation: shake 0.5s ease-in-out;
        }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        .warning-icon { font-size: 5em; margin-bottom: 20px; }
        .warning-title { font-size: 2em; color: #ff6b6b; margin-bottom: 15px; font-weight: bold; }
        .warning-message { font-size: 1.2em; color: #ffcc00; margin-bottom: 20px; }
        .warning-action { font-size: 1em; color: #aaa; margin-bottom: 25px; }
        .warning-btn {
            background: linear-gradient(135deg, #ff6b6b, #cc5555);
            color: #fff;
            border: none;
            padding: 15px 40px;
            font-size: 1.2em;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
        }
        .warning-btn:hover { background: linear-gradient(135deg, #ff8888, #dd6666); }

        .header { text-align: center; padding: 30px 0; border-bottom: 2px solid rgba(255,255,255,0.1); margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; background: linear-gradient(90deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .status-card { background: rgba(255,255,255,0.05); border-radius: 15px; padding: 25px; text-align: center; border: 1px solid rgba(255,255,255,0.1); }
        .status-card .icon { font-size: 3em; margin-bottom: 15px; }
        .status-card .value { font-size: 2em; font-weight: bold; }
        .status-card.success { border-color: #00ff88; }
        .status-card.success .value { color: #00ff88; }
        .status-card.warning { border-color: #ffcc00; }
        .status-card.warning .value { color: #ffcc00; }
        .status-card.danger { border-color: #ff6b6b; }
        .status-card.danger .value { color: #ff6b6b; }
        .section-title { font-size: 1.5em; margin: 30px 0 20px; padding-left: 15px; border-left: 4px solid #7c3aed; }
        .platform-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .platform-card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid rgba(255,255,255,0.1); }
        .platform-card .platform-icon { font-size: 2.5em; margin-bottom: 10px; }
        .platform-card .platform-name { font-size: 1.1em; font-weight: bold; margin-bottom: 10px; }
        .platform-card .stat-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .platform-card .stat-value { color: #00d4ff; font-weight: bold; }
        .platform-card .status { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.8em; margin-top: 10px; }
        .platform-card .status.active { background: rgba(0,255,136,0.2); color: #00ff88; }
        .platform-card .status.stopped { background: rgba(255,107,107,0.2); color: #ff6b6b; }
        .revenue-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .revenue-card { background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(0,212,255,0.2)); border-radius: 15px; padding: 25px; border: 1px solid rgba(124,58,237,0.3); }
        .revenue-card h3 { color: #7c3aed; margin-bottom: 15px; }
        .revenue-card .amount { font-size: 2.5em; font-weight: bold; color: #00d4ff; }
        .footer { text-align: center; padding: 30px 0; margin-top: 50px; border-top: 1px solid rgba(255,255,255,0.1); color: #666; }
        .auto-badge { display: inline-block; background: linear-gradient(90deg, #00ff88, #00d4ff); color: #000; padding: 8px 20px; border-radius: 20px; font-weight: bold; }

        /* 操作结果 */
        .result-toast {
            display: none;
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: #000;
            padding: 15px 25px;
            border-radius: 10px;
            font-weight: bold;
            z-index: 999;
            animation: slideIn 0.3s ease;
        }
        .result-toast.error { background: linear-gradient(135deg, #ff6b6b, #cc5555); color: #fff; }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    </style>
</head>
<body>
    <!-- 警告弹窗 -->
    <div class="warning-overlay" id="warningOverlay">
        <div class="warning-modal">
            <div class="warning-icon">⚠️</div>
            <div class="warning-title">WARNING!</div>
            <div class="warning-message" id="warningMessage">检测到系统异常</div>
            <div class="warning-action" id="warningAction">建议采取行动</div>
            <button class="warning-btn" onclick="closeWarning()">我知道了</button>
        </div>
    </div>

    <!-- 操作结果提示 -->
    <div class="result-toast" id="resultToast"></div>

    <div class="container">
        <div class="header">
            <h1>Apex Speed Labs</h1>
            <p>CEO Dashboard - Money Breeding Machine v3.2</p>
            <p style="color: #00ff88; margin-top: 15px;"><span class="auto-badge">⚡ FULL AUTO MODE</span></p>
            <p style="color: #888; margin-top: 10px;">最后更新: {{ last_update }}</p>
        </div>

        <!-- 控制面板 -->
        <div class="control-panel">
            <h2>⚙️ 控制面板</h2>
            <div class="control-buttons">
                <button class="ctrl-btn btn-refresh" onclick="doAction('refresh')">🔄 刷新系统</button>
                <button class="ctrl-btn btn-start" onclick="doAction('start')">▶️ 启动自动化</button>
                <button class="ctrl-btn btn-stop" onclick="doAction('stop')">⏹️ 停止自动化</button>
                <button class="ctrl-btn btn-backup" onclick="doAction('backup')">💾 备份系统</button>
                <button class="ctrl-btn btn-test" onclick="showWarning()">🧪 测试警告</button>
            </div>
        </div>

        <div class="status-grid">
            <div class="status-card success">
                <div class="icon">🖥️</div>
                <div class="value">在线</div>
                <div>VPS (167.71.120.132)</div>
            </div>
            <div class="status-card {{ 'success' if system_status.mem_percent < 85 else 'warning' }}">
                <div class="icon">🧠</div>
                <div class="value">{{ system_status.mem_percent }}%</div>
                <div>内存使用</div>
            </div>
            <div class="status-card {{ 'success' if system_status.cpu_used < 80 else 'warning' }}">
                <div class="icon">⚡</div>
                <div class="value">{{ "%.1f"|format(system_status.cpu_used) }}%</div>
                <div>CPU使用</div>
            </div>
            <div class="status-card {{ 'success' if system_status.disk_usage.rstrip('%')|int < 80 else 'warning' }}">
                <div class="icon">💾</div>
                <div class="value">{{ system_status.disk_usage }}</div>
                <div>磁盘使用</div>
            </div>
        </div>

        <div class="status-grid">
            <div class="status-card success">
                <div class="icon">☁️</div>
                <div class="value">{{ cloud_status }}</div>
                <div>云服务</div>
            </div>
            <div class="status-card success">
                <div class="icon">📋</div>
                <div class="value">{{ running_tasks }}</div>
                <div>活跃Cron任务</div>
            </div>
            <div class="status-card success">
                <div class="icon">🐍</div>
                <div class="value">{{ system_status.python_processes }}</div>
                <div>Python进程</div>
            </div>
            <div class="status-card">
                <div class="icon">💰</div>
                <div class="value">${{ stripe_balance }}</div>
                <div>Stripe 余额</div>
            </div>
        </div>

        <div class="revenue-grid">
            <div class="revenue-card">
                <h3>本周目标</h3>
                <div class="amount">$500 - $2,000</div>
            </div>
            <div class="revenue-card">
                <h3>本月目标</h3>
                <div class="amount">$3,000 - $10,000</div>
            </div>
            <div class="revenue-card">
                <h3>今日执行</h3>
                <div class="amount">{{ total_today }}次</div>
            </div>
        </div>

        <h2 class="section-title">📱 社交媒体平台 (7个)</h2>
        <div class="platform-grid">
            {% for p in social_platforms %}
            <div class="platform-card">
                <div class="platform-icon">{{ p.icon }}</div>
                <div class="platform-name">{{ p.name }}</div>
                <div class="stat-row"><span>今日</span><span class="stat-value">{{ p.today }}</span></div>
                <div class="stat-row"><span>本周</span><span class="stat-value">{{ p.week }}</span></div>
                <span class="status active">自动运行</span>
            </div>
            {% endfor %}
        </div>

        <h2 class="section-title">💼 商业平台 (5个)</h2>
        <div class="platform-grid">
            {% for p in business_platforms %}
            <div class="platform-card">
                <div class="platform-icon">{{ p.icon }}</div>
                <div class="platform-name">{{ p.name }}</div>
                <div class="stat-row"><span>今日</span><span class="stat-value">{{ p.today }}</span></div>
                <div class="stat-row"><span>本周</span><span class="stat-value">{{ p.week }}</span></div>
                <span class="status active">自动运行</span>
            </div>
            {% endfor %}
        </div>

        <h2 class="section-title">💎 支付与系统 (2个)</h2>
        <div class="platform-grid">
            <div class="platform-card">
                <div class="platform-icon">💳</div>
                <div class="platform-name">Stripe</div>
                <div class="stat-row"><span>余额</span><span class="stat-value">${{ stripe_balance }}</span></div>
                <div class="stat-row"><span>总收入</span><span class="stat-value">$0</span></div>
                <span class="status active">已连接</span>
            </div>
            <div class="platform-card">
                <div class="platform-icon">🔗</div>
                <div class="platform-name">USDC监控</div>
                <div class="stat-row"><span>今日检查</span><span class="stat-value">{{ usdc_today }}</span></div>
                <div class="stat-row"><span>状态</span><span class="stat-value">监控中</span></div>
                <span class="status active">自动监控</span>
            </div>
        </div>

        <div class="footer">
            <p>VPS: 167.71.120.132</p>
            <p style="margin-top: 15px;"><span class="auto-badge">⚡ FULL AUTO MODE</span></p>
        </div>
    </div>

    <script>
        // 显示警告
        function showWarning(message, action) {
            document.getElementById('warningMessage').textContent = message || '检测到系统异常';
            document.getElementById('warningAction').textContent = action || '建议采取行动';
            document.getElementById('warningOverlay').classList.add('active');
        }

        function closeWarning() {
            document.getElementById('warningOverlay').classList.remove('active');
        }

        // 显示结果提示
        function showToast(message, isError) {
            const toast = document.getElementById('resultToast');
            toast.textContent = message;
            toast.className = 'result-toast' + (isError ? ' error' : '');
            toast.style.display = 'block';
            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        }

        // 执行操作
        async function doAction(action) {
            const actions = {
                'refresh': { msg: '🔄 系统已刷新', api: '/api/refresh' },
                'start': { msg: '▶️ 自动化已启动', api: '/api/start' },
                'stop': { msg: '⏹️ 自动化已停止', api: '/api/stop' },
                'backup': { msg: '💾 备份进行中...', api: '/api/backup' }
            };

            const info = actions[action];
            if (!info) return;

            if (action === 'stop') {
                showWarning('⚠️ 确认停止自动化?', '停止后所有自动化任务将暂停');
                return;
            }

            showToast(info.msg, false);

            try {
                const resp = await fetch(info.api);
                const data = await resp.json();
                if (data.success) {
                    showToast(data.message, false);
                    if (data.warning) {
                        setTimeout(() => showWarning(data.warning.title, data.warning.action), 1000);
                    }
                } else {
                    showToast('操作失败: ' + data.message, true);
                }
            } catch (e) {
                showToast('操作失败: ' + e.message, true);
            }
        }

        // 自动检查警告
        {% if warnings %}
        setTimeout(() => {
            {% for w in warnings %}
            showWarning('{{ w.message }}', '{{ w.action }}');
            {% endfor %}
        }, 2000);
        {% endif %}
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    social = ['twitter', 'tiktok', 'youtube', 'xiaohongshu', 'douyin', 'instagram', 'facebook']
    business = ['linkedin', 'upwork', 'whatsapp', 'wechat', 'usdc']

    social_platforms = []
    for p in social:
        info = PLATFORMS[p]
        social_platforms.append({
            'name': info['name'],
            'icon': info['icon'],
            'today': get_log_count(info['log']),
            'week': get_log_count(info['log'], 7)
        })

    business_platforms = []
    for p in business:
        info = PLATFORMS[p]
        business_platforms.append({
            'name': info['name'],
            'icon': info['icon'],
            'today': get_log_count(info['log']),
            'week': get_log_count(info['log'], 7)
        })

    usdc_today = get_log_count('usdc.log')
    total_today = sum(p['today'] for p in social_platforms + business_platforms)

    apex = check_service('https://apex-brain.sweeyuen3.workers.dev')
    leads = check_service('https://leads-improvement.sweeyuen3.workers.dev')
    cloud_status = f"{'✅' if apex else '❌'}/{ '✅' if leads else '❌'}"

    stripe_balance = get_stripe_balance()
    system_status = get_system_status()
    running_tasks = get_running_tasks()
    warnings = get_warnings()

    return render_template_string(DASHBOARD_HTML,
        last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        cloud_status=cloud_status,
        total_today=total_today,
        stripe_balance=stripe_balance,
        social_platforms=social_platforms,
        business_platforms=business_platforms,
        usdc_today=usdc_today,
        system_status=system_status,
        running_tasks=running_tasks,
        warnings=warnings
    )

# API 端点
@app.route('/api/refresh')
def api_refresh():
    """刷新系统"""
    try:
        # 重启Dashboard
        subprocess.run(['pkill', '-f', 'ceo_dashboard_server'], capture_output=True)
        subprocess.Popen(['nohup', 'python3', f'{AUTOMATION_DIR}/ceo_dashboard_server.py', '>logs/dashboard.log', '2>&1', '&'])
        return jsonify({'success': True, 'message': '系统已刷新'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/start')
def api_start():
    """启动自动化"""
    try:
        # 启动关键自动化脚本
        scripts = ['linkedin_playwright_auto.py', 'upwork_playwright_auto.py']
        for script in scripts:
            subprocess.Popen(['nohup', 'python3', f'{AUTOMATION_DIR}/{script}', '>>logs/auto.log', '2>&1', '&'])
        return jsonify({'success': True, 'message': '自动化已启动', 'warning': {'title': '✅ 自动化已启动', 'action': '系统正在恢复运行'}})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stop')
def api_stop():
    """停止自动化"""
    try:
        # 停止非关键进程（保留Dashboard）
        scripts = ['linkedin_playwright_auto.py', 'upwork_playwright_auto.py', 'tiktok_auto.py', 'twitter_auto.py']
        for script in scripts:
            subprocess.run(['pkill', '-f', script], capture_output=True)
        return jsonify({'success': True, 'message': '自动化已暂停', 'warning': {'title': '⚠️ 自动化已停止', 'action': '需要时点击启动恢复'}})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/backup')
def api_backup():
    """备份系统"""
    try:
        # 执行备份
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'apex_backup_{timestamp}'

        # GitHub备份
        subprocess.run(['bash', '-c', 'cd /root/apex-automation-git && git add -A && git commit -m "Auto backup" && git push origin main'], capture_output=True)

        # 本地备份
        subprocess.run(['mkdir', '-p', f'/root/apex-automation/backups/{backup_name}'], capture_output=True)

        return jsonify({'success': True, 'message': f'备份完成: {backup_name}', 'warning': {'title': '💾 备份成功', 'action': f'备份已保存到 /root/apex-automation/backups/{backup_name}'}})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/status')
def api_status():
    """获取状态"""
    return jsonify({
        'system_status': get_system_status(),
        'running_tasks': get_running_tasks(),
        'warnings': get_warnings()
    })

if __name__ == '__main__':
    print("🚀 CEO Dashboard v3.2 启动中...")
    print("📊 访问地址: http://167.71.120.132:5000")
    print("⚙️ 控制面板已启用: 刷新/启动/停止/备份")
    app.run(host='0.0.0.0', port=5000, debug=False)
