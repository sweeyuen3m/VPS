#!/usr/bin/env python3
"""
Upwork自动申请项目 - Playwright版本
全自动申请Upwork上的AI/Chatbot相关项目
"""

import os
import sys
import json
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

# 配置日志
LOG_DIR = "/root/apex-automation/logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/upwork_playwright.log"),
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

# 项目搜索关键词
JOB_KEYWORDS = [
    "chatbot",
    "AI automation", 
    "customer service automation",
    "WhatsApp chatbot",
    "e-commerce automation",
    "AI assistant",
    "automation script",
    "python automation"
]

# 提案模板
PROPOSAL_TEMPLATES = [
    """Hi [Client],

I specialize in building AI chatbots and automation solutions that help businesses save time and increase efficiency.

I can help you with:
- Custom chatbot development (WhatsApp, web, Slack, etc.)
- Business process automation
- AI-powered customer service
- Integration with your existing tools

I'm offering competitive rates with fast turnaround. Would you be open to a quick call to discuss your needs?

Best regards,
Stark
Apex Speed Labs""",
    
    """Hi [Client],

I noticed you're looking for help with automation - I'd love to help!

I specialize in:
- AI chatbot development
- Business workflow automation
- Python/RPA solutions
- API integrations

I've helped businesses save 10+ hours per week through automation. Happy to share samples from similar projects.

Interested? Let's chat!

Best,
Stark
Apex Speed Labs"""
]

def login_to_upwork(page, config):
    """登录Upwork"""
    logger.info("正在登录Upwork...")
    
    page.goto("https://www.upwork.com/ab/account-security/login")
    page.wait_for_timeout(3000)
    
    # 输入邮箱
    email_input = page.locator("input[name='login[username]']")
    if email_input.is_visible():
        email_input.fill(config.get('UPWORK_EMAIL', ''))
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(2000)
    
    # 输入密码
    password_input = page.locator("input[name='login[password]']")
    if password_input.is_visible():
        password_input.fill(config.get('UPWORK_PASSWORD', ''))
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(5000)
    
    logger.info("登录完成")
    return True

def search_jobs(page):
    """搜索项目"""
    logger.info("搜索AI/自动化相关项目...")
    
    jobs = []
    
    for keyword in JOB_KEYWORDS[:3]:  # 只搜索前3个关键词
        try:
            search_url = f"https://www.upwork.com/search/jobs/?q={keyword.replace(' ', '+')}&sort=recency"
            page.goto(search_url)
            page.wait_for_timeout(3000)
            
            # 获取项目列表
            job_cards = page.locator("article[data-test='job-tile']")
            count = job_cards.count()
            
            logger.info(f"关键词 '{keyword}' 找到 {count} 个项目")
            
            for i in range(min(count, 5)):  # 每个关键词最多5个
                try:
                    card = job_cards[i]
                    title = card.locator("h3").inner_text()
                    link = card.locator("a").get_attribute("href")
                    budget = card.locator("[data-test='job-budget']").inner_text() if card.locator("[data-test='job-budget']").is_visible() else "N/A"
                    
                    # 提取预算金额
                    budget_value = 0
                    if '$' in budget:
                        try:
                            budget_value = int(budget.replace('$', '').replace(',', '').split('-')[0])
                        except:
                            budget_value = 0
                    
                    jobs.append({
                        'title': title,
                        'link': f"https://www.upwork.com{link}" if link else None,
                        'budget': budget,
                        'budget_value': budget_value,
                        'keyword': keyword
                    })
                except Exception as e:
                    logger.debug(f"提取项目信息失败: {e}")
                    
        except Exception as e:
            logger.warning(f"搜索关键词 '{keyword}' 失败: {e}")
    
    # 按预算排序，只保留$100+的项目
    jobs = [j for j in jobs if j['budget_value'] >= 100]
    jobs.sort(key=lambda x: x['budget_value'], reverse=True)
    
    logger.info(f"筛选后共 {len(jobs)} 个符合条件的项目（$100+）")
    return jobs[:10]  # 只返回前10个

def apply_to_job(page, job):
    """申请项目"""
    try:
        logger.info(f"申请项目: {job['title']}")
        
        page.goto(job['link'])
        page.wait_for_timeout(3000)
        
        # 点击申请按钮
        apply_button = page.locator("button[data-test='apply-button'], a[data-test='apply-button']")
        if apply_button.is_visible():
            apply_button.click()
            page.wait_for_timeout(2000)
            
            # 选择模板
            template = PROPOSAL_TEMPLATES[0]
            
            # 输入提案
            cover_letter = page.locator("textarea[name='coverLetter'], textarea#coverLetter")
            if cover_letter.is_visible():
                cover_letter.fill(template)
                page.wait_for_timeout(1000)
                
                # 点击提交
                submit_button = page.locator("button[type='submit'], button[data-test='submit-proposal']")
                if submit_button.is_visible():
                    submit_button.click()
                    page.wait_for_timeout(2000)
                    logger.info(f"✅ 项目申请成功: {job['title']}")
                    return True
        
        logger.warning(f"❌ 无法申请项目: {job['title']}")
        return False
        
    except Exception as e:
        logger.error(f"申请项目失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("="*50)
    logger.info("Upwork自动申请系统启动")
    logger.info("="*50)
    
    config = load_config()
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'jobs_found': 0,
        'jobs_applied': 0,
        'jobs_failed': 0,
        'jobs': []
    }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            # 登录
            if not login_to_upwork(page, config):
                logger.error("登录失败，程序退出")
                return
            
            # 搜索项目
            jobs = search_jobs(page)
            results['jobs_found'] = len(jobs)
            results['jobs'] = jobs
            
            # 申请项目
            for job in jobs[:5]:  # 每次最多申请5个
                if apply_to_job(page, job):
                    results['jobs_applied'] += 1
                else:
                    results['jobs_failed'] += 1
                
                # 随机延迟
                import random
                delay = random.randint(5, 15)
                logger.info(f"等待 {delay} 秒...")
                page.wait_for_timeout(delay * 1000)
            
            browser.close()
            
    except Exception as e:
        logger.error(f"程序异常: {e}")
    
    # 保存结果
    result_file = f"{LOG_DIR}/upwork_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("="*50)
    logger.info(f"任务完成! 找到 {results['jobs_found']} 个项目，申请 {results['jobs_applied']} 个")
    logger.info("="*50)
    
    return results

if __name__ == "__main__":
    main()
