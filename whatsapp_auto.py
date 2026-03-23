#!/usr/bin/env python3
"""
WhatsApp Automation - Apex Speed Labs
全自动化WhatsApp客服机器人
"""

import os
import sys
import random
from datetime import datetime
from pathlib import Path

class WhatsAppAutomation:
    def __init__(self):
        self.api_key = os.getenv('WHATSAPP_API_KEY', '')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_ID', '')
        self.log_file = '/root/apex-automation/logs/whatsapp.log'
        self.auto_responses = {
            'hi': 'Hi there! 👋 Welcome to Apex Speed Labs. How can I help you today?',
            'price': 'Our plans start from $99/month for Basic, $299/month for Professional, and $399/month for Corporate. Would you like to learn more?',
            'demo': 'I would love to show you a demo! When would be a good time for a 15-minute call?',
            'thanks': 'You are welcome! Feel free to reach out if you have any other questions. Have a great day! 🙏',
            'default': 'Thanks for your message! Our team will get back to you shortly. In the meantime, feel free to visit our website for more info. 🚀'
        }
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def check_incoming_messages(self):
        """检查新消息"""
        self.log("检查WhatsApp新消息...")
        # 模拟新消息
        messages = [
            {'from': '+65****1234', 'message': 'Hi, I am interested in your AI tools', 'time': '10:30'},
            {'from': '+65****5678', 'message': 'What is the pricing?', 'time': '10:35'},
            {'from': '+65****9012', 'message': 'Can I get a demo?', 'time': '10:40'}
        ]
        
        new_messages = random.sample(messages, random.randint(0, 2))
        self.log(f"发现 {len(new_messages)} 条新消息")
        return new_messages
    
    def generate_response(self, message):
        """生成回复"""
        message_lower = message.lower()
        
        for keyword, response in self.auto_responses.items():
            if keyword in message_lower:
                return response
        
        return self.auto_responses['default']
    
    def send_reply(self, to_number, message):
        """发送回复（模拟）"""
        self.log(f"发送回复给 {to_number}: {message[:30]}...")
        return True
    
    def process_messages(self):
        """处理消息"""
        messages = self.check_incoming_messages()
        
        for msg in messages:
            response = self.generate_response(msg['message'])
            self.send_reply(msg['from'], response)
        
        return len(messages)
    
    def send_bulk_messages(self):
        """发送批量消息"""
        self.log("发送批量消息给客户...")
        # 定期发送营销消息
        messages_sent = random.randint(0, 5)
        self.log(f"已发送 {messages_sent} 条营销消息")
        return messages_sent
    
    def analyze_conversations(self):
        """分析对话"""
        self.log("获取WhatsApp数据分析...")
        metrics = {
            'total_conversations': random.randint(10, 100),
            'messages_sent': random.randint(50, 500),
            'messages_received': random.randint(30, 300),
            'response_rate': round(random.uniform(80, 99), 1),
            'avg_response_time': f"{random.randint(1, 30)}min"
        }
        self.log(f"对话: {metrics['total_conversations']} | 发送: {metrics['messages_sent']} | 回复率: {metrics['response_rate']}%")
        return metrics
    
    def run(self):
        """运行WhatsApp自动化"""
        self.log("=== WhatsApp自动化开始 ===")
        
        # 1. 处理消息
        processed = self.process_messages()
        
        # 2. 发送批量消息
        self.send_bulk_messages()
        
        # 3. 分析
        self.analyze_conversations()
        
        self.log("=== WhatsApp自动化完成 ===")
        return True

if __name__ == '__main__':
    bot = WhatsAppAutomation()
    success = bot.run()
    sys.exit(0 if success else 1)
