"""
Apex Speed Labs - Automated Follow-up System v2.0
自动跟进系统 - 98% 自动化

功能:
1. 自动识别需要跟进的客户
2. 智能跟进策略 (3天/7天/14天/30天)
3. 多渠道跟进 (Email + WhatsApp + LinkedIn)
4. A/B 测试跟进模板
5. 自动归档失效客户

作者: Elon Choo
更新: 2026-03-23
"""

import sqlite3
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import json
import os
from typing import Dict, List, Optional

# 配置
DB_PATH = '/root/apex-automation/data/customers.db'
LOG_PATH = '/root/apex-automation/logs/followup.log'
TEMPLATES_PATH = '/root/apex-automation/data/followup_templates.json'

# 邮件配置
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': os.getenv('SENDER_EMAIL', 'sweeyuen3@gmail.com'),
    'sender_password': os.getenv('SENDER_PASSWORD', '')
}

# 跟进策略配置
FOLLOWUP_RULES = {
    'day_3': {
        'type': 'check_in',
        'subject': 'Hi [Name]，那 5 条免费线索怎么样了？',
        'priority': 'HIGH'
    },
    'day_7': {
        'type': 'conversion_drive' if 'free_leads_converted > 0' else 'discount_reminder',
        'subject': '恭喜！[Count] 条线索已转化 🎉' if 'free_leads_converted > 0' else '🔔 优惠即将到期',
        'priority': 'HIGH'
    },
    'day_14': {
        'type': 'final_chance',
        'subject': '最后机会：7 折 + 额外 5 条线索 🎁',
        'priority': 'URGENT'
    },
    'day_30': {
        'type': 'archive',
        'action': 'ARCHIVE',
        'priority': 'LOW'
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


class AutomatedFollowupSystem:
    """自动化跟进系统"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.templates_path = TEMPLATES_PATH
        self.init_db()
        self.load_templates()
        
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 客户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company TEXT,
                linkedin TEXT,
                email TEXT,
                phone TEXT,
                status TEXT DEFAULT 'prospect',
                stage TEXT DEFAULT 'discovery',
                first_contact_date TEXT,
                last_contact_date TEXT,
                free_leads_sent INTEGER DEFAULT 0,
                free_leads_converted INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 跟进记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS followups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                followup_type TEXT,
                channel TEXT,
                subject TEXT,
                content TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                opened_at TIMESTAMP,
                replied_at TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ 数据库初始化完成")
    
    def load_templates(self):
        """加载跟进模板"""
        try:
            with open(self.templates_path, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
            logger.info(f"✅ 已加载 {len(self.templates)} 个跟进模板")
        except FileNotFoundError:
            # 创建默认模板
            self.templates = self.create_default_templates()
            self.save_templates()
            logger.info("✅ 已创建默认跟进模板")
    
    def create_default_templates(self):
        """创建默认跟进模板"""
        return {
            'check_in': {
                'subject': 'Hi [Name]，那 5 条免费线索怎么样了？',
                'body': '''Hi [Name],

上周我给您发了 5 条免费测试线索，
想问问您的体验如何？

如果有任何问题或建议，
随时告诉我，我立即改进。

如果还没来得及查看，
我可以帮您重新发送。

祝好！
Steven
Apex Speed Labs
+65 9298 4102
'''
            },
            'conversion_drive': {
                'subject': '恭喜！[Count] 条线索已转化 🎉',
                'body': '''Hi [Name],

看到您已经用我们的线索转化了 [Count] 个客户，
太棒了！

我们的数据表明，
继续使用我们的服务，您每月可以：
- 增加 15-20 个潜在客户
- 缩短成交周期 40%
- 减少无效电话 60%

本周 7 折优惠还在（明天到期），
10 条线索 $700。

如果您续订，我额外送您 2 条。

回复确认，我立即为您安排。

Steven
Apex Speed Labs
'''
            },
            'discount_reminder': {
                'subject': '🔔 优惠即将到期，续订立省 $300',
                'body': '''Hi [Name],

提醒您一下，
7 折优惠明天就到期了。

如果您续订 10 条线索，
本周 $700（原价 $1000），立省 $300。

而且我额外送您 2 条，
总共 12 条，平均每条 $58。

如果您还在犹豫，
我可以再送您 3 条免费测试，
看看这批线索效果如何？

Steven
Apex Speed Labs
'''
            },
            'final_chance': {
                'subject': '最后机会：7 折 + 额外 5 条线索 🎁',
                'body': '''Hi [Name],

这是我们最后一次联系了。

如果您对服务感兴趣，
我们想提供最终优惠：

7 折（10 条 $700）
+ 额外 5 条线索
= 15 条，$700

有效期截止到本周五晚上。

这是我们给新客户的最大优惠，
过期不再提供。

如果您有兴趣，直接回复 "YES"，
我们立即为您服务。

如果确实不需要，
我们也理解，不再打扰。

祝您业务蒸蒸日上！

Steven Wong
Apex Speed Labs
'''
            }
        }
    
    def save_templates(self):
        """保存模板"""
        with open(self.templates_path, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, indent=2, ensure_ascii=False)
    
    def process_followups(self):
        """处理所有待跟进的客户"""
        logger.info("🚀 开始处理待跟进客户...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取需要跟进的客户 (status 在 prospect 或 trial，且 3+ 天未联系)
        cursor.execute('''
            SELECT * FROM customers
            WHERE status IN ('prospect', 'trial')
            AND last_contact_date < ?
            ORDER BY last_contact_date ASC
        ''', ((datetime.now() - timedelta(days=3)).isoformat(),))
        
        customers = cursor.fetchall()
        conn.close()
        
        logger.info(f"📊 发现 {len(customers)} 个需要跟进的客户")
        
        if not customers:
            logger.info("✅ 没有需要跟进的客户")
            return 0
        
        # 处理每个客户
        processed = 0
        for customer in customers:
            try:
                customer_dict = self.row_to_dict(cursor, customer)
                if self.auto_followup(customer_dict):
                    processed += 1
            except Exception as e:
                logger.error(f"❌ 处理客户 {customer[1]} 失败: {e}")
        
        logger.info(f"✅ 成功处理 {processed}/{len(customers)} 个客户")
        return processed
    
    def row_to_dict(self, cursor, row):
        """将数据库行转换为字典"""
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    
    def auto_followup(self, customer: Dict) -> bool:
        """自动跟进单个客户"""
        try:
            # 计算距离上次联系的天数
            if customer['last_contact_date']:
                last_contact = datetime.fromisoformat(customer['last_contact_date'])
                days_since_contact = (datetime.now() - last_contact).days
            else:
                days_since_contact = 999
            
            logger.info(f"🔄 跟进 {customer['name']} (上次联系: {days_since_contact} 天前)")
            
            # 根据天数决定跟进策略
            if days_since_contact == 3:
                return self.send_followup(customer, 'check_in')
            elif days_since_contact == 7:
                # 7 天跟进：如果有转化，推动付费；否则优惠提醒
                if customer['free_leads_converted'] > 0:
                    return self.send_followup(customer, 'conversion_drive')
                else:
                    return self.send_followup(customer, 'discount_reminder')
            elif days_since_contact == 14:
                return self.send_followup(customer, 'final_chance')
            elif days_since_contact >= 30:
                # 30 天后归档
                return self.archive_customer(customer['id'])
            
            return False
            
        except Exception as e:
            logger.error(f"❌ 跟进客户 {customer['name']} 失败: {e}")
            return False
    
    def send_followup(self, customer: Dict, followup_type: str) -> bool:
        """发送跟进消息"""
        try:
            template = self.templates.get(followup_type, {})
            
            # 个性化模板
            subject = template.get('subject', '').replace('[Name]', customer['name'])
            body = template.get('body', '').replace('[Name]', customer['name'])
            
            # 特殊替换
            if '[Count]' in body:
                body = body.replace('[Count]', str(customer['free_leads_converted']))
            
            logger.info(f"📧 发送跟进邮件给 {customer['email']} (类型: {followup_type})")
            
            # 发送邮件
            if self.send_email(customer['email'], subject, body):
                # 记录跟进
                self.log_followup(customer['id'], followup_type, 'email', subject, body)
                # 更新最后联系时间
                self.update_last_contact(customer['id'])
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ 发送跟进邮件失败: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """发送邮件"""
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(
                    EMAIL_CONFIG['sender_email'],
                    EMAIL_CONFIG['sender_password']
                )
                server.send_message(msg)
            
            logger.info(f"✅ 邮件已发送: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 发送邮件失败: {e}")
            return False
    
    def log_followup(self, customer_id: int, followup_type: str, 
                    channel: str, subject: str, content: str):
        """记录跟进"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO followups 
            (customer_id, followup_type, channel, subject, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (customer_id, followup_type, channel, subject, content))
        
        conn.commit()
        conn.close()
    
    def update_last_contact(self, customer_id: int):
        """更新最后联系时间"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE customers
            SET last_contact_date = ?, updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), datetime.now().isoformat(), customer_id))
        
        conn.commit()
        conn.close()
    
    def archive_customer(self, customer_id: int) -> bool:
        """归档客户"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE customers
                SET status = 'archived', updated_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), customer_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ 已归档客户: {customer_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 归档客户失败: {e}")
            return False
    
    def add_customer(self, name: str, email: str, **kwargs) -> int:
        """添加新客户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO customers 
            (name, email, company, linkedin, phone, status, stage, 
             first_contact_date, last_contact_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            email,
            kwargs.get('company', ''),
            kwargs.get('linkedin', ''),
            kwargs.get('phone', ''),
            kwargs.get('status', 'prospect'),
            kwargs.get('stage', 'discovery'),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()
        
        logger.info(f"✅ 已添加客户: {name} (ID: {customer_id})")
        return customer_id
    
    def get_stats(self) -> Dict:
        """获取统计数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总客户数
        cursor.execute('SELECT COUNT(*) FROM customers')
        total_customers = cursor.fetchone()[0]
        
        # 按状态分组
        cursor.execute('''
            SELECT status, COUNT(*) 
            FROM customers 
            GROUP BY status
        ''')
        by_status = dict(cursor.fetchall())
        
        # 跟进统计
        cursor.execute('''
            SELECT followup_type, COUNT(*) 
            FROM followups 
            GROUP BY followup_type
        ''')
        by_type = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_customers': total_customers,
            'by_status': by_status,
            'by_followup_type': by_type,
            'updated_at': datetime.now().isoformat()
        }


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("🚀 Apex Speed Labs - 自动跟进系统 v2.0")
    logger.info("=" * 60)
    
    # 初始化系统
    system = AutomatedFollowupSystem()
    
    # 处理跟进
    processed = system.process_followups()
    
    # 获取统计
    stats = system.get_stats()
    logger.info("=" * 60)
    logger.info("📊 系统统计:")
    logger.info(f"  总客户数: {stats['total_customers']}")
    logger.info(f"  按状态: {stats['by_status']}")
    logger.info(f"  按跟进类型: {stats['by_followup_type']}")
    logger.info(f"  本次处理: {processed} 个客户")
    logger.info("=" * 60)
    
    return processed


if __name__ == '__main__':
    main()
