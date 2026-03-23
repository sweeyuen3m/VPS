#!/usr/bin/env python3
"""
浏览器资源管理器
防止内存泄漏，优化浏览器性能
"""

import psutil
import logging
import time
from contextlib import contextmanager
from playwright.sync_api import sync_playwright, Browser, BrowserContext

logger = logging.getLogger(__name__)

class BrowserResourceManager:
    """浏览器资源管理器"""

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.start_time = None
        self.memory_threshold = 80  # 内存使用率超过 80% 自动清理

    @contextmanager
    def managed_browser(self, headless=True, user_agent=None):
        """
        上下文管理器，自动清理浏览器资源

        使用方式:
            with BrowserResourceManager().managed_browser() as (browser, context, page):
                # 执行自动化任务
                pass
        """
        try:
            with sync_playwright() as p:
                self.browser = p.chromium.launch(
                    headless=headless,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-software-rasterizer',
                        '--disable-extensions',
                        '--disable-background-networking',
                        '--disable-default-apps',
                        '--disable-sync',
                        '--disable-translate',
                        '--hide-scrollbars',
                        '--metrics-recording-only',
                        '--mute-audio',
                        '--no-first-run',
                        '--safebrowsing-disable-auto-update',
                        '--disable-infobars',
                        '--disable-notifications',
                    ]
                )

                self.context = self.browser.new_context(
                    user_agent=user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    java_script_enabled=True,
                    ignore_https_errors=True
                )

                # 优化页面设置
                self.page = self.context.new_page()
                self.page.set_default_timeout(30000)  # 30 秒超时
                self.page.set_default_navigation_timeout(30000)

                self.start_time = time.time()
                logger.info("✅ 浏览器资源已分配")

                yield self.browser, self.context, self.page

        except Exception as e:
            logger.error(f"❌ 浏览器异常: {e}")
            raise
        except:
            self._cleanup_resources()

    def _cleanup_resources(self):
        """清理浏览器资源"""
        try:
            # 关闭页面
            if self.page:
                self.page.close()
                logger.debug("✅ 页面已关闭")

            # 关闭上下文
            if self.context:
                self.context.close()
                logger.debug("✅ 浏览器上下文已关闭")

            # 关闭浏览器
            if self.browser:
                self.browser.close()
                logger.debug("✅ 浏览器已关闭")

            # 记录执行时间
            if self.start_time:
                duration = time.time() - self.start_time
                logger.info(f"⏱️ 浏览器执行时间: {duration:.2f}s")

            # 检查内存使用
            self._check_memory_usage()

        except Exception as e:
            logger.error(f"❌ 清理资源时出错: {e}")

    def _check_memory_usage(self):
        """检查内存使用情况"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()

            logger.info(f"💾 内存使用: {memory_percent:.2f}%")

            if memory_percent > self.memory_threshold:
                logger.warning(f"⚠️ 内存使用率过高: {memory_percent:.2f}%")
                self._force_garbage_collection()

        except Exception as e:
            logger.error(f"❌ 检查内存时出错: {e}")

    def _force_garbage_collection(self):
        """强制垃圾回收"""
        import gc
        gc.collect()
        logger.info("🧹 垃圾回收已执行")

    def get_memory_usage(self):
        """获取当前内存使用率"""
        try:
            process = psutil.Process()
            return process.memory_percent()
        except Exception as e:
            logger.error(f"❌ 获取内存使用时出错: {e}")
            return 0.0

# 便捷函数
@contextmanager
def create_browser(headless=True, user_agent=None):
    """
    便捷函数：创建并管理浏览器资源

    使用方式:
        with create_browser() as (browser, context, page):
            page.goto("https://example.com")
    """
    with BrowserResourceManager().managed_browser(headless, user_agent) as resources:
        yield resources


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    with create_browser() as (browser, context, page):
        page.goto("https://example.com")
        print(page.title())
        time.sleep(2)
