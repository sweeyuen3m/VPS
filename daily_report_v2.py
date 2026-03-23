#!/usr/bin/env python3
"""
APEX SPEED LABS - 全自动汇报系统 v1.1
每天自动发送汇报到 Telegram 和 邮箱
无需MacBook，无需人工干预
"""

import os
import subprocess
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('/root/apex-automation/.env')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'sweeyuen3@gmail.com')
SMTP_USER = os.getenv('SMTP_USER', 'sweeyuen3@apexspeedlabs.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_FROM = os.getenv('EMAIL_FROM', 'sweeyuen3@apexspeedlabs.com')
APEX_BRAIN_URL = os.getenv('APEX_BRAIN_URL', 'https://apex-brain.sweeyuen3.workers.dev')
LEADS_URL = os.getenv('LEADS_IMPROVEMENT_URL', 'https://leads-improvement.sweeyuen3.workers.dev')

LOG_DIR = "/root/apex-automation/logs"

def send_telegram(message):
    """发送Telegram消息"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[TG] 未配置Telegram，跳过")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            print(f"[TG] Telegram消息已发送: {datetime.now()}")
            return True
        else:
            print(f"[TG] Telegram发送失败: {resp.text}")
            return False
    except Exception as e:
        print(f"[TG] Telegram错误: {e}")
        return False

def send_email(subject, html_body):
    """发送邮件"""
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[EMAIL] 未配置邮件，跳过")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = ADMIN_EMAIL
        
        # 纯文本版本
        text_body = html_body.replace('<b>', '').replace('</b>', '')
        text_body = text_body.replace('<br>', '\n').replace('</b>', '')
        text_body = text_body.replace('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', '-' * 40)
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, ADMIN_EMAIL, msg.as_string())
        
        print(f"[EMAIL] 邮件已发送: {subject} -> {ADMIN_EMAIL}")
        return True
    except Exception as e:
        print(f"[EMAIL] 邮件错误: {e}")
        return False

def check_service(url, name):
    """检查服务状态"""
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return f"✅ {name}"
        else:
            return f"❌ {name} ({resp.status_code})"
    except:
        return f"❌ {name} (离线)"

def get_system_stats():
    """获取系统统计"""
    stats = {'cpu': 'N/A', 'memory': 'N/A', 'disk': 'N/A'}
    
    try:
        # CPU
        result = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'Cpu(s)' in line:
                stats['cpu'] = line.split(',')[0].split(':')[1].strip()
                break
        
        # 内存
        result = subprocess.run(['free', '-m'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        if len(lines) > 1:
            mem_line = lines[1].split()
            used = int(mem_line[2])
            total = int(mem_line[1])
            stats['memory'] = f"{used}MB / {total}MB"
        
        # 磁盘
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        disk = result.stdout.split('\n')[1].split()[4]
        stats['disk'] = disk
    except:
        pass
    
    return stats

def get_automation_stats():
    """获取自动化执行统计"""
    stats = {}
    platforms = ['upwork', 'linkedin', 'twitter', 'tiktok', 'youtube', 
                 'xiaohongshu', 'instagram', 'facebook', 'usdc']
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    for platform in platforms:
        log_file = f"{LOG_DIR}/{platform}.log"
        count = 0
        try:
            with open(log_file, 'r') as f:
                count = sum(1 for line in f if today in line)
        except:
            pass
        stats[platform] = count
    
    return stats

def generate_report():
    """生成汇报"""
    now = datetime.now()
    system = get_system_stats()
    stats = get_automation_stats()
    
    apex_brain = check_service(APEX_BRAIN_URL, "Apex Brain")
    leads = check_service(LEADS_URL, "Leads Improvement")
    
    # Stripe余额
    stripe_balance = "检查中..."
    try:
        stripe_key = os.getenv('STRIPE_SECRET_KEY', '')
        if stripe_key:
            resp = requests.get('https://api.stripe.com/v1/balance', 
                              auth=(stripe_key, ''), timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                balance = data['available'][0]['amount'] / 100
                stripe_balance = f"${balance} SGD"
    except:
        stripe_balance = "检查失败"
    
    total_executions = sum(stats.values())
    
    # Telegram消息 (HTML)
    telegram_msg = f"""
🚀 <b>APEX SPEED LABS - 每日汇报</b>
📅 {now.strftime('%Y-%m-%d %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>💰 收入状态</b>
   Stripe: {stripe_balance}
   本周目标: $500 - $2000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🖥️ 系统状态</b>
   CPU: {system['cpu']}
   内存: {system['memory']}
   磁盘: {system['disk']}

<b>☁️ 云服务</b>
   {apex_brain}
   {leads}

<b>⚡ 今日自动化 ({total_executions}次)</b>"""
    
    platform_emoji = {
        'upwork': '💼', 'linkedin': '💼', 'twitter': '🐦', 
        'tiktok': '🎵', 'youtube': '📹', 'xiaohongshu': '📕',
        'instagram': '📸', 'facebook': '👥', 'usdc': '💎'
    }
    
    for platform, count in stats.items():
        emoji = platform_emoji.get(platform, '📌')
        telegram_msg += f"\n   {emoji} {platform}: {count}次"
    
    telegram_msg += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>🎯 目标</b>
   本周: $500 - $2000
   本月: $3,000 - $10,000

⚡ <b>FULL AUTO MODE</b>
VPS: 167.71.120.132
"""
    
    # 邮件HTML
    email_html = f"""
<html><body>
<h2>🚀 APEX SPEED LABS - 每日自动汇报</h2>
<p><b>📅 {now.strftime('%Y-%m-%d %H:%M')}</b></p>

<hr>
<h3>💰 收入状态</h3>
<ul>
<li>Stripe余额: <b>{stripe_balance}</b></li>
<li>本周目标: $500 - $2000</li>
</ul>

<h3>🖥️ 系统状态</h3>
<ul>
<li>CPU: {system['cpu']}</li>
<li>内存: {system['memory']}</li>
<li>磁盘: {system['disk']}</li>
</ul>

<h3>☁️ 云服务</h3>
<ul>
<li>{apex_brain}</li>
<li>{leads}</li>
</ul>

<h3>⚡ 今日自动化执行 ({total_executions}次)</h3>
<table border="1" cellpadding="5">
<tr><th>平台</th><th>执行次数</th></tr>"""
    
    for platform, count in stats.items():
        email_html += f"<tr><td>{platform}</td><td>{count}</td></tr>"
    
    email_html += f"""
</table>

<hr>
<h3>🎯 目标进度</h3>
<ul>
<li>本周: $500 - $2000</li>
<li>本月: $3,000 - $10,000</li>
<li>本季: $15,000 - $50,000</li>
</ul>

<hr>
<p><b>⚡ 状态: FULL AUTO MODE - 无需人工干预</b></p>
<p>VPS: 167.71.120.132 | 汇报时间: {now.strftime('%H:%M:%S')}</p>
</body></html>
"""
    
    return telegram_msg, email_html, f"[Apex] 每日汇报 {now.strftime('%Y-%m-%d')}"

def main():
    """主函数"""
    print(f"[{datetime.now()}] 开始生成每日汇报...")
    
    # 生成汇报
    telegram_msg, email_html, email_subject = generate_report()
    
    # 打印到控制台
    print(telegram_msg)
    
    # 发送Telegram
    tg_success = send_telegram(telegram_msg)
    
    # 发送邮件
    email_success = send_email(email_subject, email_html)
    
    if tg_success or email_success:
        print(f"[完成] 汇报已发送 (TG: {tg_success}, Email: {email_success})")
    else:
        print("[警告] 所有汇报渠道失败")

if __name__ == '__main__':
    main()
