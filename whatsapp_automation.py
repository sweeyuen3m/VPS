"""
Apex Speed Labs - WhatsApp Automation Module v1.0
WhatsApp 自动化模块

功能:
1. WhatsApp Business API 集成
2. 自动发送消息
3. 消息模板管理
4. 消息状态追踪

注意: 需要配置 WhatsApp Business API 凭证

作者: Elon Choo
更新: 2026-03-23
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os

# 配置
LOG_PATH = '/root/apex-automation/logs/whatsapp.log'
CONFIG_PATH = '/root/apex-automation/config/whatsapp_config.json'

# WhatsApp Business API 配置
WHATSAPP_CONFIG = {
    'api_url': 'https://graph.facebook.com/v18.0',
    'phone_number_id': os.getenv('WHATSAPP_PHONE_NUMBER_ID', ''),
    'access_token': os.getenv('WHATSAPP_ACCESS_TOKEN', ''),
    'business_account_id': os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
}

# 消息模板配置
MESSAGE_TEMPLATES = {
    'welcome': {
        'name': 'welcome_message',
        'language': 'en',
        'components': [
            {
                'type': 'body',
                'text': 'Hi {{1}}, welcome to Apex Speed Labs! 🚀\n\nWe help real estate agents generate high-quality leads using AI.\n\nCheck out our service: https://leads-improvement.sweeyuen3.workers.dev'
            }
        ]
    },
    'free_leads': {
        'name': 'free_leads_offer',
        'language': 'en',
        'components': [
            {
                'type': 'body',
                'text': 'Hi {{1}},\n\nWe have 5 free leads for you to try! 🎁\n\nThese leads are:\n✅ High quality (80% accuracy)\n✅ Ready to contact\n✅ No obligation\n\nWant to try them out? Reply "YES" and I\'ll send them over!'
            }
        ]
    },
    'followup': {
        'name': 'follow_up_reminder',
        'language': 'en',
        'components': [
            {
                'type': 'body',
                'text': 'Hi {{1}},\n\nJust checking in - how are the leads working for you? 😊\n\nIf you need more or have questions, just let me know!\n\nSteven | Apex Speed Labs\n+65 9298 4102'
            }
        ]
    }
}

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WhatsAppAutomation:
    """WhatsApp 自动化类"""
    
    def __init__(self):
        self.config = self.load_config()
        self.api_url = WHATSAPP_CONFIG['api_url']
        self.phone_number_id = WHATSAPP_CONFIG['phone_number_id']
        self.access_token = WHATSAPP_CONFIG['access_token']
        
    def load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("⚠️ 配置文件不存在，使用环境变量")
            return WHATSAPP_CONFIG
    
    def send_message(self, to_phone: str, message: str, 
                    template: Optional[str] = None) -> Dict:
        """
        发送 WhatsApp 消息
        
        Args:
            to_phone: 接收方手机号 (格式: +6592984102)
            message: 消息内容
            template: 消息模板名称 (可选)
        
        Returns:
            响应字典
        """
        try:
            # 格式化手机号
            if not to_phone.startswith('+'):
                to_phone = f"+{to_phone}"
            
            # 使用模板发送
            if template and template in MESSAGE_TEMPLATES:
                return self.send_template_message(to_phone, template)
            else:
                # 发送自定义消息
                return self.send_custom_message(to_phone, message)
                
        except Exception as e:
            logger.error(f"❌ 发送消息失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_custom_message(self, to_phone: str, message: str) -> Dict:
        """发送自定义消息"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            data = {
                'messaging_product': 'whatsapp',
                'to': to_phone,
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                message_id = result.get('messages', [{}])[0].get('id', '')
                logger.info(f"✅ 消息已发送: {to_phone} (ID: {message_id})")
                return {'success': True, 'message_id': message_id}
            else:
                logger.error(f"❌ API 错误: {result}")
                return {'success': False, 'error': result}
                
        except Exception as e:
            logger.error(f"❌ 发送自定义消息失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_template_message(self, to_phone: str, template_name: str, 
                            parameters: List[str] = None) -> Dict:
        """
        发送模板消息
        
        Args:
            to_phone: 接收方手机号
            template_name: 模板名称
            parameters: 模板参数 (用于替换 {{1}}, {{2}} 等)
        """
        try:
            if template_name not in MESSAGE_TEMPLATES:
                logger.error(f"❌ 模板不存在: {template_name}")
                return {'success': False, 'error': 'Template not found'}
            
            template = MESSAGE_TEMPLATES[template_name]
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # 构建请求数据
            data = {
                'messaging_product': 'whatsapp',
                'to': to_phone,
                'type': 'template',
                'template': {
                    'name': template['name'],
                    'language': {'code': template['language']}
                }
            }
            
            # 添加参数
            if parameters:
                components = []
                for i, param in enumerate(parameters):
                    components.append({
                        'type': 'body',
                        'parameters': [
                            {
                                'type': 'text',
                                'text': param
                            }
                        ]
                    })
                data['template']['components'] = components
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                message_id = result.get('messages', [{}])[0].get('id', '')
                logger.info(f"✅ 模板消息已发送: {to_phone} (模板: {template_name}, ID: {message_id})")
                return {'success': True, 'message_id': message_id}
            else:
                logger.error(f"❌ API 错误: {result}")
                return {'success': False, 'error': result}
                
        except Exception as e:
            logger.error(f"❌ 发送模板消息失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_bulk_messages(self, phones: List[str], message: str, 
                         delay: int = 10) -> List[Dict]:
        """
        批量发送消息
        
        Args:
            phones: 手机号列表
            message: 消息内容
            delay: 发送间隔 (秒，避免被标记为垃圾消息)
        
        Returns:
            响应列表
        """
        results = []
        
        for i, phone in enumerate(phones):
            logger.info(f"📧 发送消息 {i+1}/{len(phones)}: {phone}")
            result = self.send_message(phone, message)
            results.append({'phone': phone, 'result': result})
            
            # 延迟发送
            if i < len(phones) - 1:
                logger.info(f"⏳ 等待 {delay} 秒...")
                import time
                time.sleep(delay)
        
        logger.info(f"✅ 批量发送完成: {len(phones)} 条消息")
        return results
    
    def check_message_status(self, message_id: str) -> Dict:
        """
        检查消息状态
        
        Args:
            message_id: 消息 ID
        
        Returns:
            消息状态信息
        """
        try:
            url = f"{self.api_url}/{message_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                status = result.get('data', {}).get('status', 'unknown')
                logger.info(f"📊 消息状态: {message_id} = {status}")
                return {'success': True, 'status': status}
            else:
                logger.error(f"❌ API 错误: {result}")
                return {'success': False, 'error': result}
                
        except Exception as e:
            logger.error(f"❌ 检查消息状态失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_free_leads_offer(self, phone: str, name: str = '') -> Dict:
        """
        发送免费线索优惠
        
        Args:
            phone: 手机号
            name: 客户姓名 (用于模板替换)
        """
        return self.send_template_message(phone, 'free_leads', [name or 'there'])
    
    def send_welcome(self, phone: str, name: str = '') -> Dict:
        """
        发送欢迎消息
        
        Args:
            phone: 手机号
            name: 客户姓名 (用于模板替换)
        """
        return self.send_template_message(phone, 'welcome', [name or 'there'])


def test_connection():
    """测试 API 连接"""
    logger.info("🔌 测试 WhatsApp API 连接...")
    
    whatsapp = WhatsAppAutomation()
    
    # 检查配置
    if not whatsapp.access_token:
        logger.error("❌ 未配置 WhatsApp Access Token")
        logger.info("请设置环境变量: export WHATSAPP_ACCESS_TOKEN='your_token'")
        return False
    
    # 测试 API (获取 Phone Number 信息)
    try:
        url = f"{whatsapp.api_url}/{whatsapp.phone_number_id}"
        headers = {
            'Authorization': f'Bearer {whatsapp.access_token}'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info("✅ WhatsApp API 连接成功")
            logger.info(f"📱 Phone Number ID: {whatsapp.phone_number_id}")
            return True
        else:
            logger.error(f"❌ API 连接失败: {response.json()}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 连接测试失败: {e}")
        return False


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("📱 WhatsApp 自动化系统 v1.0")
    logger.info("=" * 60)
    
    # 测试连接
    if not test_connection():
        logger.warning("⚠️ WhatsApp API 未配置，系统将在配置后激活")
        return
    
    # 初始化 WhatsApp 自动化
    whatsapp = WhatsAppAutomation()
    
    # 示例: 发送测试消息
    # result = whatsapp.send_message(
    #     '+6592984102',
    #     'Hello! This is a test message from Apex Speed Labs. 🚀'
    # )
    # print(result)
    
    logger.info("✅ WhatsApp 自动化系统已就绪")


if __name__ == '__main__':
    main()
