#!/usr/bin/env python3
"""
LinkedIn自动私信系统 - Playwright版本
全自动发送个性化LinkedIn私信
"""

import os
import sys
import json
import random
import logging
from datetime import datetime
from smart_delay_manager import SmartDelayManager
from playwright.sync_api import sync_playwright
from browser_resource_manager import create_browser

# 配置日志
LOG_DIR = "/root/apex-automation/logs"
DATA_DIR = "/root/apex-automation/data"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/linkedin_playwright.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载配置
def load_config():
    env_file = "/root/apex-automation/.env"
    config = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    return config

# 私信模板
MESSAGE_TEMPLATES = [
    """Hi {name},

I noticed you're working in {industry} - great to connect!

Quick question: Are you spending too much time on repetitive customer messages?

We help businesses automate these with AI - saving 10+ hours/week. Currently offering 30% OFF for new clients.

Would you be open to a free 15-min demo?

Best,
Stark
Apex Speed Labs""",

    """Hi {name},

Congrats on your success in {industry}!

I help businesses like yours automate customer service with AI. Our clients typically save 10+ hours per week.

Currently offering 30% OFF + 14-day money-back guarantee.

Interested in a quick demo?

Best,
Stark
Apex Speed Labs""",

    """Hi {name},

Great to connect with someone in {industry}!

Quick question: Are you tired of answering the same questions over and over?

We help businesses automate these with AI - 24/7 support, instant responses.

Free 15-min demo? No commitment needed.

Best,
Stark
Apex Speed Labs"""
]

# 目标用户数据
TARGET_USERS = [
    {"name": "E-commerce Manager", "industry": "E-commerce", "profile": "shopee"},
    {"name": "Retail Owner", "industry": "Retail", "profile": "lazada"},
    {"name": "Restaurant Manager", "industry": "F&B", "profile": "restaurant"},
    {"name": "Shop Owner", "industry": "Online Shop", "profile": "shopee"},
    {"name": "Business Owner", "industry": "Small Business", "profile": "business"},
]

def login_to_linkedin(page, config):
    """登录LinkedIn"""
    logger.info("正在登录LinkedIn...")
    
    page.goto("https://www.linkedin.com/login")
    page.wait_for_timeout(2000)
    
    # 输入邮箱
    email_input = page.locator("#username")
    if email_input.is_visible():
        email_input.fill(config.get('LINKEDIN_EMAIL', ''))
    
    # 输入密码
    password_input = page.locator("#password")
    if password_input.is_visible():
        password_input.fill(config.get('LINKEDIN_PASSWORD', ''))
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(5000)
    
    logger.info("登录完成")
    return True

def send_message(page, recipient_name, message):
    """发送私信"""
    try:
        logger.info(f"正在发送私信给 {recipient_name}...")
        
        # 点击消息图标
        message_icon = page.locator("a[href*='messaging']")
        if message_icon.is_visible():
            message_icon.click()
            page.wait_for_timeout(2000)
        
        # 点击新消息
        new_message = page.locator("button[aria-label='Start a new conversation']")
        if new_message.is_visible():
            new_message.click()
            page.wait_for_timeout(1000)
        
        # 输入收件人
        search_input = page.locator("input[placeholder*='Search']")
        if search_input.is_visible():
            search_input.fill(recipient_name)
            page.wait_for_timeout(1000)
            
            # 选择第一个结果
            first_result = page.locator("div[role='option']").first
            if first_result.is_visible():
                first_result.click()
                page.wait_for_timeout(500)
        
        # 输入消息
        message_box = page.locator("div[contenteditable='true']")
        if message_box.is_visible():
            message_box.fill(message)
            page.wait_for_timeout(500)
            
            # 点击发送
            send_button = page.locator("button[aria-label='Send']")
            if send_button.is_visible():
                send_button.click()
                page.wait_for_timeout(1000)
                logger.info(f"✅ 私信发送成功: {recipient_name}")
                return True
        
        logger.warning(f"❌ 私信发送失败: {recipient_name}")
        return False
        
    except Exception as e:
        logger.error(f"发送私信异常: {e}")
        return False

def main():
    # 初始化智能延迟管理器
    delay_manager = SmartDelayManager()
    logger.info("智能延迟管理器已启动")
    """主函数"""
    logger.info("="*50)
    logger.info("LinkedIn自动私信系统启动")
    logger.info("="*50)
    
    config = load_config()
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'messages_sent': 0,
        'messages_failed': 0,
        'recipients': []
    }
    
    # 加载或创建目标用户列表
    targets_file = f"{DATA_DIR}/linkedin_targets.json"
    if os.path.exists(targets_file):
        with open(targets_file, 'r') as f:
            targets = json.load(f)
    else:
        targets = TARGET_USERS
        with open(targets_file, 'w') as f:
            json.dump(targets, f, indent=2)
    
    try:
        with create_browser(headless=True) as (browser, context, page):
            logger.info('浏览器资源管理器已激活')
            
            # 登录
            if not login_to_linkedin(page, config):
                logger.error("登录失败，程序退出")
                return
            
            # 发送私信
            max_messages = 150  # 每天最多150条（安全阈值）
            for i, target in enumerate(targets[:max_messages]):
                # 检查是否可以发送消息（限制检查）
                can_send, reason = delay_manager.can_send_message()
                if not can_send:
                    logger.warning(f"停止发送: {reason}")
                    break
                
                # 选择模板
                template = random.choice(MESSAGE_TEMPLATES)
                message = template.format(
                    name=target['name'],
                    industry=target.get('industry', 'business')
                )

                if send_message(page, target['name'], message):
                    results['messages_sent'] += 1
                    delay_manager.record_result(True)
                    delay_manager.record_message_sent()
                else:
                    results['messages_failed'] += 1
                    delay_manager.record_result(False)

                results['recipients'].append({
                    'name': target['name'],
                    'success': send_message(page, target['name'], message)
                })

                # 智能延迟
                delay = delay_manager.calculate_delay()
                stats = delay_manager.get_stats()
                logger.info(f"等待 {delay:.1f}s | 成功率: {stats['success_rate']}% | 今日: {stats['today_messages']}/{stats['hourly_messages']}(每小时)")
                page.wait_for_timeout(int(delay * 1000))
                
                # 检查是否达到上限
                if results['messages_sent'] + results['messages_failed'] >= max_messages:
                    break
            
            browser.close()
            
    except Exception as e:
        logger.error(f"程序异常: {e}")
    
    # 保存结果
    result_file = f"{LOG_DIR}/linkedin_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # 输出智能延迟管理器统计
    stats = delay_manager.get_stats()
    logger.info("="*50)
    logger.info(f"任务完成! 发送 {results['messages_sent']} 条，失败 {results['messages_failed']} 条")
    logger.info(f"智能延迟统计: 成功率 {stats['success_rate']}% | 平均延迟 {stats['current_delay']:.1f}s")
    logger.info(f"今日消息: {stats['today_messages']}/{stats['hourly_messages']} (每小时)")
    logger.info("="*50)
    
    return results

if __name__ == "__main__":
    main()
