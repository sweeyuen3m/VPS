#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能延迟管理器
根据时间段、成功率动态调整延迟，避免触发平台限制
"""

import random
from datetime import datetime

class SmartDelayManager:
    def __init__(self):
        self.base_delay = 10
        self.success_count = 0
        self.failure_count = 0
        self.current_delay = self.base_delay
        self.today_message_count = 0
        self.hourly_message_count = 0
        self.last_hour = datetime.now().hour
    
    def calculate_delay(self):
        """根据时间和历史记录计算延迟"""
        hour = datetime.now().hour
        
        # 时间因子：工作时间（9-17）短延迟，非工作时间长延迟
        if 9 <= hour <= 17:
            time_factor = 1.0
        elif 18 <= hour <= 22:
            time_factor = 1.5
        else:
            time_factor = 2.5
        
        # 成功率因子：失败率高时增加延迟
        total_attempts = self.success_count + self.failure_count
        if total_attempts > 0:
            success_rate = self.success_count / total_attempts
            success_factor = 1.0 + (1.0 - success_rate)  # 成功率越低，延迟越长
        else:
            success_factor = 1.0
        
        # 动态调整当前延迟
        target_delay = self.base_delay * time_factor * success_factor
        
        # 平滑过渡（不突然跳变）
        self.current_delay = self.current_delay * 0.7 + target_delay * 0.3
        
        # 添加随机波动（±30%）
        random_fluctuation = random.uniform(0.7, 1.3)
        final_delay = self.current_delay * time_factor * random_fluctuation
        
        # 限制最小和最大延迟
        return max(5, min(60, final_delay))
    
    def record_result(self, success):
        """记录操作结果"""
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        # 每次失败都增加基础延迟
        if not success:
            self.base_delay = min(30, self.base_delay * 1.2)
        # 连续成功后慢慢降低基础延迟
        elif self.success_count % 5 == 0 and self.base_delay > 10:
            self.base_delay = max(10, self.base_delay * 0.9)
    
    def can_send_message(self):
        """检查是否可以发送消息（限制频率）"""
        now = datetime.now()
        
        # 检查每小时限制
        if now.hour != self.last_hour:
            self.hourly_message_count = 0
            self.last_hour = now.hour
        
        # 每小时最多 15 条
        if self.hourly_message_count >= 15:
            return False, "Hourly limit reached (15 messages/hour)"
        
        # 每天最多 150 条
        if self.today_message_count >= 150:
            return False, "Daily limit reached (150 messages/day)"
        
        return True, "OK"
    
    def record_message_sent(self):
        """记录消息已发送"""
        self.hourly_message_count += 1
        self.today_message_count += 1
    
    def get_stats(self):
        """获取统计信息"""
        return {
            'base_delay': round(self.base_delay, 2),
            'current_delay': round(self.current_delay, 2),
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'today_messages': self.today_message_count,
            'hourly_messages': self.hourly_message_count,
            'success_rate': round(self.success_count / (self.success_count + self.failure_count) * 100, 2) if (self.success_count + self.failure_count) > 0 else 0
        }

if __name__ == '__main__':
    # 测试
    delay_manager = SmartDelayManager()
    
    print("测试智能延迟管理器")
    print("=" * 50)
    
    for i in range(10):
        can_send, reason = delay_manager.can_send_message()
        if can_send:
            delay = delay_manager.calculate_delay()
            success = random.choice([True, True, False])  # 模拟 2/3 成功率
            delay_manager.record_result(success)
            if success:
                delay_manager.record_message_sent()
            
            print(f"消息 {i+1}: 延迟 {delay:.1f}s | 成功: {success} | {reason}")
        else:
            print(f"消息 {i+1}: {reason}")
            break
    
    print("=" * 50)
    stats = delay_manager.get_stats()
    print(f"统计: {stats}")
