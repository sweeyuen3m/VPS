#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Netdata 与 Dashboard 集成模块
功能：将 Netdata 监控数据嵌入 Dashboard
"""

import requests
from datetime import datetime

class NetdataIntegration:
    def __init__(self, netdata_url='http://localhost:19999'):
        self.netdata_url = netdata_url
        self.api_base = f'{netdata_url}/api/v1'
    
    def get_system_health(self):
        """获取系统健康状态"""
        try:
            response = requests.get(f'{self.api_base}/info', timeout=5)
            data = response.json()
            
            return {
                'status': 'healthy' if data.get('alarms', {}).get('warning', 0) == 0 else 'warning',
                'alarms_normal': data.get('alarms', {}).get('normal', 0),
                'alarms_warning': data.get('alarms', {}).get('warning', 0),
                'alarms_critical': data.get('alarms', {}).get('critical', 0),
                'last_update': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_update': datetime.now().isoformat()
            }
    
    def get_cpu_usage(self):
        """获取 CPU 使用率"""
        try:
            response = requests.get(f'{self.api_base}/data?chart=system.cpu&format=json&after=-1', timeout=5)
            data = response.json()
            
            # 获取最新的 CPU 数据（Netdata 返回格式：{labels: [], data: []}）
            latest_data = data.get('data', [])[-1] if data.get('data') else []
            
            # 计算总 CPU 使用率（排除时间戳）
            if len(latest_data) > 1:
                # data[0] 是时间戳，data[1:] 是各个 CPU 状态（百分比）
                cpu_values = [v if v is not None else 0 for v in latest_data[1:]]
                cpu_percent = sum(cpu_values)  # 所有状态的总和
                
                return {
                    'cpu_usage': round(cpu_percent, 2),
                    'last_update': datetime.now().isoformat()
                }
            
            return {
                'cpu_usage': 0,
                'last_update': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'cpu_usage': 0,
                'error': str(e),
                'last_update': datetime.now().isoformat()
            }
    
    def get_memory_usage(self):
        """获取内存使用率"""
        try:
            # Netdata 使用 system.ram 图表（返回 MB 单位）
            response = requests.get(f'{self.api_base}/data?chart=system.ram&format=json&after=-1', timeout=5)
            data = response.json()
            
            latest_data = data.get('data', [])[-1] if data.get('data') else []
            
            if len(latest_data) > 1:
                # data[0] 是时间戳，data[1] 是 free，data[2] 是 used，data[3] 是 cached，data[4] 是 buffers
                free_mb = latest_data[1] or 0
                used_mb = latest_data[2] or 0
                cached_mb = latest_data[3] or 0
                buffers_mb = latest_data[4] or 0
                
                total_mb = free_mb + used_mb + cached_mb + buffers_mb
                memory_percent = (used_mb / total_mb * 100) if total_mb > 0 else 0
                
                return {
                    'memory_usage': round(memory_percent, 2),
                    'total_mb': round(total_mb, 2),
                    'used_mb': round(used_mb, 2),
                    'last_update': datetime.now().isoformat()
                }
            
            return {
                'memory_usage': 0,
                'total_mb': 0,
                'used_mb': 0,
                'last_update': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'memory_usage': 0,
                'total_mb': 0,
                'used_mb': 0,
                'error': str(e),
                'last_update': datetime.now().isoformat()
            }
    
    def get_disk_usage(self):
        """获取磁盘使用率（使用 Linux 命令获取）"""
        try:
            # 备用方案：使用系统命令
            import subprocess
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        usage_str = parts[4]  # 第 5 列是使用百分比
                        disk_percent = float(usage_str.replace('%', ''))
                        return {
                            'disk_usage': round(disk_percent, 2),
                            'last_update': datetime.now().isoformat()
                        }

            return {
                'disk_usage': 0,
                'last_update': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'disk_usage': 0,
                'error': str(e),
                'last_update': datetime.now().isoformat()
            }
    
    def get_dashboard_data(self):
        """获取 Dashboard 所需的所有数据"""
        return {
            'health': self.get_system_health(),
            'cpu': self.get_cpu_usage(),
            'memory': self.get_memory_usage(),
            'disk': self.get_disk_usage(),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == '__main__':
    # 测试
    netdata = NetdataIntegration()
    data = netdata.get_dashboard_data()
    print(data)
