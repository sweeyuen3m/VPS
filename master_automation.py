#!/usr/bin/env python3
"""
全平台自动化主控 - Apex Speed Labs
Master Automation Controller
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 导入各平台自动化模块
sys.path.insert(0, '/root/apex-automation/scripts')

class MasterAutomation:
    def __init__(self):
        self.log_file = '/root/apex-automation/logs/master.log'
        self.platforms = {
            'tiktok': 'TikTok自动化',
            'youtube': 'YouTube自动化',
            'xiaohongshu': '小红书自动化',
            'douyin': '抖音自动化',
            'instagram': 'Instagram自动化',
            'facebook': 'Facebook自动化',
            'whatsapp': 'WhatsApp自动化',
            'wechat': '微信自动化',
            'linkedin': 'LinkedIn自动化',
            'upwork': 'Upwork自动化',
            'twitter': 'Twitter自动化',
            'usdc': 'USDC监控'
        }
        
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def run_platform(self, platform_name):
        """运行单个平台自动化"""
        self.log(f"启动 {self.platforms.get(platform_name, platform_name)}...")
        
        try:
            if platform_name == 'tiktok':
                import tiktok_auto
                bot = tiktok_auto.TikTokAutomation()
            elif platform_name == 'youtube':
                import youtube_auto
                bot = youtube_auto.YouTubeAutomation()
            elif platform_name == 'xiaohongshu':
                import xiaohongshu_auto
                bot = xiaohongshu_auto.XiaohongshuAutomation()
            elif platform_name == 'douyin':
                import douyin_auto
                bot = douyin_auto.DouyinAutomation()
            elif platform_name == 'instagram':
                import instagram_auto
                bot = instagram_auto.InstagramAutomation()
            elif platform_name == 'facebook':
                import facebook_auto
                bot = facebook_auto.FacebookAutomation()
            elif platform_name == 'whatsapp':
                import whatsapp_auto
                bot = whatsapp_auto.WhatsAppAutomation()
            elif platform_name == 'wechat':
                import wechat_auto
                bot = wechat_auto.WeChatAutomation()
            elif platform_name == 'linkedin':
                import linkedin_playwright_auto
                bot = linkedin_playwright_auto.LinkedInAutomation()
            elif platform_name == 'upwork':
                import upwork_playwright_auto
                bot = upwork_playwright_auto.UpworkAutomation()
            elif platform_name == 'twitter':
                import twitter_auto
                bot = twitter_auto.TwitterAutomation()
            elif platform_name == 'usdc':
                import usdc_monitor
                bot = usdc_monitor.USDCMonitor()
            else:
                self.log(f"未知平台: {platform_name}")
                return False
            
            result = bot.run()
            self.log(f"{self.platforms.get(platform_name)} {'✅ 成功' if result else '❌ 失败'}")
            return result
            
        except ImportError as e:
            self.log(f"{self.platforms.get(platform_name)} - 模块未找到: {e}", 'WARN')
            return False
        except Exception as e:
            self.log(f"{self.platforms.get(platform_name)} - 错误: {e}", 'ERROR')
            return False
    
    def run_all(self):
        """运行所有平台自动化"""
        self.log("=" * 50)
        self.log("全平台自动化主控启动")
        self.log("=" * 50)
        
        results = {}
        
        # 根据时间决定运行哪些平台
        hour = datetime.now().hour
        
        # 早间任务 (6-12点)
        if 6 <= hour < 12:
            morning_platforms = ['twitter', 'linkedin', 'youtube', 'wechat']
            self.log(f"执行早间任务: {morning_platforms}")
            for platform in morning_platforms:
                results[platform] = self.run_platform(platform)
        
        # 午间任务 (12-18点)
        elif 12 <= hour < 18:
            afternoon_platforms = ['tiktok', 'douyin', 'instagram', 'facebook', 'xiaohongshu', 'whatsapp']
            self.log(f"执行午间任务: {afternoon_platforms}")
            for platform in afternoon_platforms:
                results[platform] = self.run_platform(platform)
        
        # 晚间任务 (18-24点)
        elif 18 <= hour < 24:
            evening_platforms = ['upwork', 'twitter', 'usdc']
            self.log(f"执行晚间任务: {evening_platforms}")
            for platform in evening_platforms:
                results[platform] = self.run_platform(platform)
        
        # 深夜任务 (0-6点)
        else:
            night_platforms = ['usdc', 'twitter']
            self.log(f"执行深夜任务: {night_platforms}")
            for platform in night_platforms:
                results[platform] = self.run_platform(platform)
        
        # 总结
        self.log("=" * 50)
        self.log("全平台自动化执行完成")
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        self.log(f"成功: {success_count}/{total_count}")
        self.log("=" * 50)
        
        return success_count == total_count

if __name__ == '__main__':
    master = MasterAutomation()
    success = master.run_all()
    sys.exit(0 if success else 1)
