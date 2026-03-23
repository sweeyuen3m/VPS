#!/usr/bin/env python3
"""
LinkedIn 自动私信脚本（Chromium 版本 - 完全自动化）
使用 Selenium + Chromium 进行真实的 LinkedIn 互动
"""
import os
import sys
import time
import random
import logging
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv('/root/apex-automation/.env')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/apex-automation/logs/linkedin_chromium.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置参数
CONFIG = {
    'max_messages': 30,  # 每次最多发送30条私信
    'your_linkedin_url': 'https://www.linkedin.com/in/swee-yuan-steven-wong-7818553b8/',
    'your_name': 'Steven Wong',
    'your_company': 'Apex Speed Labs',
    'your_phone': '+65 9298 4102',
    'your_website': 'https://leads-improvement.sweeyuen3.workers.dev',
    'search_keywords': [
        'property agent Singapore',
        'real estate Singapore',
        'ERA Singapore agent',
        'PropNex Singapore',
        'OrangeTee Singapore',
        'Huttons Singapore',
        'Dennis Wee Singapore'
    ],
    'message_templates': [
        """Hi {name},

I noticed you're in Singapore's real estate industry. My team at Apex Speed Labs specializes in AI-powered lead generation for property agents.

We've been helping Singapore agents:
- Generate 300%+ more qualified property leads
- Save 20+ hours per week on manual outreach
- Close deals 50% faster

Special Offer for Singapore Property Agents:
✅ 7-day free trial (no credit card required)
✅ 70% off your first month
✅ 5 free property leads to test our system
✅ 24/7 local Singapore support

Would you be open to a quick 15-minute call to see if this could work for your business?

Best regards,
Steven Wong
CEO, Apex Speed Labs
+65 9298 4102
https://leads-improvement.sweeyuen3.workers.dev""",
    ]
}

class LinkedInChromiumBot:
    def __init__(self):
        self.driver = None
        self.sent_count = 0
        self.failed_count = 0
        self.results = []

    def init_driver(self):
        """初始化 Chromium 浏览器"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            # 设置真实的 User-Agent
            chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 指定 Chromium 路径
            chrome_options.binary_location = '/snap/bin/chromium'

            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 移除 navigator.webdriver 属性
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
            
            logger.info("✅ Chromium 初始化成功")
            return True
        except Exception as e:
            logger.error(f"❌ Chromium 初始化失败: {e}")
            return False

    def login(self):
        """登录 LinkedIn"""
        try:
            logger.info("🔐 正在登录 LinkedIn...")
            
            # 打开 LinkedIn
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(2)
            
            # 输入邮箱
            email = os.getenv('LINKEDIN_EMAIL')
            password = os.getenv('LINKEDIN_PASSWORD')
            
            if not email or not password:
                logger.error("❌ LinkedIn 凭证未配置")
                return False
            
            # 输入邮箱
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            email_input.send_keys(email)
            time.sleep(1)
            
            # 输入密码
            password_input = self.driver.find_element(By.ID, 'password')
            password_input.send_keys(password)
            time.sleep(1)
            
            # 点击登录
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            time.sleep(3)
            
            # 检查是否登录成功
            if 'feed' in self.driver.current_url or 'in/' in self.driver.current_url:
                logger.info("✅ LinkedIn 登录成功")
                return True
            else:
                logger.error("❌ LinkedIn 登录失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 登录异常: {e}")
            return False

    def search_targets(self, keyword):
        """搜索目标用户"""
        try:
            logger.info(f"🔍 搜索目标: {keyword}")
            
            # 使用 LinkedIn 搜索
            search_url = f'https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=SWITCH_SEARCH_VERTICAL'
            self.driver.get(search_url)
            time.sleep(3)
            
            # 等待搜索结果加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.search-result__info'))
            )
            
            # 获取搜索结果
            results = []
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, '.search-result__info')
            
            for element in result_elements[:20]:  # 限制前20个结果
                try:
                    # 获取用户名称
                    name_element = element.find_element(By.CSS_SELECTOR, '.actor-name')
                    name = name_element.text
                    
                    # 获取用户链接
                    link_element = element.find_element(By.CSS_SELECTOR, '.search-result__result-link')
                    url = link_element.get_attribute('href')
                    
                    if name and url:
                        results.append({
                            'name': name,
                            'url': url,
                            'keyword': keyword
                        })
                except:
                    continue
            
            logger.info(f"✅ 找到 {len(results)} 个目标用户")
            return results
            
        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}")
            return []

    def send_message(self, target_url, message):
        """发送私信给目标用户"""
        try:
            # 打开用户资料页
            self.driver.get(target_url)
            time.sleep(2)
            
            # 查找 Message 按钮
            message_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Message')]"))
            )
            message_button.click()
            time.sleep(2)
            
            # 输入消息
            message_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
            )
            message_box.send_keys(message)
            time.sleep(1)
            
            # 发送消息（Enter 键）
            message_box.send_keys(Keys.ENTER)
            time.sleep(2)
            
            logger.info(f"✅ 消息发送成功: {target_url}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 消息发送失败: {e}")
            return False

    def run(self):
        """主执行流程"""
        logger.info("🚀 开始 LinkedIn 自动私信任务")
        logger.info(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 初始化浏览器
        if not self.init_driver():
            logger.error("❌ 无法初始化浏览器，退出")
            return
        
        # 登录
        if not self.login():
            logger.error("❌ 登录失败，退出")
            self.driver.quit()
            return
        
        # 获取目标用户
        all_targets = []
        
        # 方法1: 从文件加载
        targets_file = '/root/apex-automation/data/linkedin_targets.json'
        if os.path.exists(targets_file):
            with open(targets_file, 'r', encoding='utf-8') as f:
                all_targets = json.load(f)
            logger.info(f"📋 从文件加载 {len(all_targets)} 个目标")
        else:
            # 方法2: 搜索目标
            for keyword in CONFIG['search_keywords']:
                if len(all_targets) >= CONFIG['max_messages']:
                    break
                targets = self.search_targets(keyword)
                all_targets.extend(targets)
                time.sleep(2)  # 避免被检测
        
        if not all_targets:
            logger.error("❌ 没有目标用户，退出")
            self.driver.quit()
            return
        
        logger.info(f"📊 目标用户数: {len(all_targets)}")
        logger.info(f"🎯 最大发送数: {CONFIG['max_messages']}")
        
        # 发送消息
        for i, target in enumerate(all_targets[:CONFIG['max_messages']]):
            # 生成消息
            template = random.choice(CONFIG['message_templates'])
            name = target.get('name', 'there')
            message = template.replace("{name}", name)
            
            # 发送消息
            success = self.send_message(target['url'], message)
            
            # 记录结果
            result = {
                'name': name,
                'url': target['url'],
                'status': 'success' if success else 'failed',
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(result)
            
            # 更新计数
            if success:
                self.sent_count += 1
            else:
                self.failed_count += 1
            
            # 延迟，避免被检测
            delay = random.uniform(15, 30)
            logger.info(f"⏸️ 延迟 {delay:.1f} 秒...")
            time.sleep(delay)
        
        # 保存结果
        self.save_results()
        
        # 清理
        self.driver.quit()
        
        logger.info(f"✅ 任务完成！发送 {self.sent_count} 条，失败 {self.failed_count} 条")
        logger.info(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def save_results(self):
        """保存结果到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'/root/apex-automation/logs/linkedin_results_{timestamp}.json'
        
        result_data = {
            'timestamp': datetime.now().isoformat(),
            'sent': self.sent_count,
            'failed': self.failed_count,
            'success_rate': (self.sent_count / (self.sent_count + self.failed_count) * 100) if (self.sent_count + self.failed_count) > 0 else 0,
            'results': self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 结果已保存到: {filename}")

if __name__ == "__main__":
    try:
        bot = LinkedInChromiumBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("⏹️ 用户中断执行")
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
