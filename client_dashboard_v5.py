#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════
   Apex Speed Labs - 客户 Dashboard 自动化系统 v5.0
   功能: 为每个客户自动生成专属数据仪表盘
   更新: 2026-03-23
══════════════════════════════════════════════════════════
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置
BASE_DIR = Path("/root/apex-automation")
DATA_DIR = BASE_DIR / "data"
DASHBOARDS_DIR = BASE_DIR / "dashboards" / "client"
CLIENTS_FILE = DATA_DIR / "clients.json"
LEADS_FILE = DATA_DIR / "leads.json"

# 确保目录存在
DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

class ClientDashboard:
    """客户 Dashboard 生成器"""
    
    def __init__(self):
        self.load_clients()
        self.load_leads()
    
    def load_clients(self) -> None:
        """加载客户数据"""
        try:
            if CLIENTS_FILE.exists():
                with open(CLIENTS_FILE, 'r', encoding='utf-8') as f:
                    self.clients = json.load(f)
                logger.info(f"✅ 已加载 {len(self.clients)} 个客户")
            else:
                self.clients = []
                self.save_clients()
                logger.info("📝 创建新的客户数据库")
        except Exception as e:
            logger.error(f"❌ 加载客户数据失败: {e}")
            self.clients = []
    
    def save_clients(self) -> None:
        """保存客户数据"""
        try:
            with open(CLIENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.clients, f, ensure_ascii=False, indent=2)
            logger.debug("💾 客户数据已保存")
        except Exception as e:
            logger.error(f"❌ 保存客户数据失败: {e}")
    
    def load_leads(self) -> None:
        """加载线索数据"""
        try:
            if LEADS_FILE.exists():
                with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                    self.leads = json.load(f)
                logger.info(f"✅ 已加载 {len(self.leads)} 条线索")
            else:
                self.leads = []
        except Exception as e:
            logger.error(f"❌ 加载线索数据失败: {e}")
            self.leads = []
    
    def get_client_leads(self, client_id: str) -> List[Dict]:
        """获取客户的线索"""
        return [lead for lead in self.leads if lead.get('client_id') == client_id]
    
    def generate_dashboard_html(self, client: Dict) -> str:
        """为客户生成 Dashboard HTML"""
        client_id = client['id']
        client_name = client['name']
        leads = self.get_client_leads(client_id)
        
        # 计算统计数据
        total_leads = len(leads)
        qualified_leads = [l for l in leads if l.get('status') == 'qualified']
        contacted_leads = [l for l in leads if l.get('status') == 'contacted']
        converted_leads = [l for l in leads if l.get('status') == 'converted']
        
        qualified_count = len(qualified_leads)
        contacted_count = len(contacted_leads)
        converted_count = len(converted_leads)
        conversion_rate = (converted_count / total_leads * 100) if total_leads > 0 else 0
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{client_name} - Apex Speed Labs Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            font-size: 2em;
            color: #333;
            margin-bottom: 10px;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-card .trend {{
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .trend.up {{ color: #10b981; }}
        .trend.down {{ color: #ef4444; }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .chart-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .chart-card h2 {{
            margin-bottom: 20px;
            color: #333;
        }}
        .leads-table {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .leads-table h2 {{
            margin-bottom: 20px;
            color: #333;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .status.new {{ background: #e0f2fe; color: #0284c7; }}
        .status.qualified {{ background: #dcfce7; color: #16a34a; }}
        .status.contacted {{ background: #fef3c7; color: #d97706; }}
        .status.converted {{ background: #f0fdf4; color: #16a34a; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {client_name} Dashboard</h1>
            <div class="subtitle">实时数据分析 | Apex Speed Labs</div>
            <div class="subtitle">最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>🎯 总线索数</h3>
                <div class="value">{total_leads}</div>
                <div class="trend up">↑ 本周新增 {len([l for l in leads if self.is_this_week(l)])}</div>
            </div>
            <div class="stat-card">
                <h3>✅ 合格线索</h3>
                <div class="value">{qualified_count}</div>
                <div class="trend up">↑ 合格率 {(qualified_count/total_leads*100):.1f if total_leads > 0 else 0}%</div>
            </div>
            <div class="stat-card">
                <h3>📞 已联系</h3>
                <div class="value">{contacted_count}</div>
                <div class="trend">联系率 {(contacted_count/total_leads*100):.1f if total_leads > 0 else 0}%</div>
            </div>
            <div class="stat-card">
                <h3>💰 转化客户</h3>
                <div class="value">{converted_count}</div>
                <div class="trend up">↑ 转化率 {conversion_rate:.1f}%</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h2>📈 线索转化漏斗</h2>
                <canvas id="funnelChart"></canvas>
            </div>
            <div class="chart-card">
                <h2>📊 线索状态分布</h2>
                <canvas id="statusChart"></canvas>
            </div>
        </div>
        
        <div class="leads-table">
            <h2>📋 最新线索列表</h2>
            <table>
                <thead>
                    <tr>
                        <th>姓名</th>
                        <th>公司</th>
                        <th>状态</th>
                        <th>创建时间</th>
                    </tr>
                </thead>
                <tbody>
                    {self.generate_leads_rows(leads[:10])}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // 漏斗图
        const funnelCtx = document.getElementById('funnelChart').getContext('2d');
        new Chart(funnelCtx, {{
            type: 'bar',
            data: {{
                labels: ['新线索', '合格', '已联系', '已转化'],
                datasets: [{{
                    label: '线索数量',
                    data: [{total_leads}, {qualified_count}, {contacted_count}, {converted_count}],
                    backgroundColor: ['#667eea', '#10b981', '#f59e0b', '#16a34a'],
                    borderRadius: 8,
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});
        
        // 状态分布图
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['新线索', '合格', '已联系', '已转化'],
                datasets: [{{
                    data: [{total_leads - qualified_count - contacted_count - converted_count}, {qualified_count}, {contacted_count}, {converted_count}],
                    backgroundColor: ['#667eea', '#10b981', '#f59e0b', '#16a34a'],
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        return html
    
    def generate_leads_rows(self, leads: List[Dict]) -> str:
        """生成线索表格行"""
        rows = ""
        for lead in leads:
            status = lead.get('status', 'new')
            created = lead.get('created', '')
            if created:
                try:
                    created_date = datetime.fromisoformat(created).strftime('%Y-%m-%d')
                except:
                    created_date = created
            rows += f"""
                    <tr>
                        <td>{lead.get('name', '-')}</td>
                        <td>{lead.get('company', '-')}</td>
                        <td><span class="status {status}">{status}</span></td>
                        <td>{created_date}</td>
                    </tr>
            """
        return rows
    
    def is_this_week(self, lead: Dict) -> bool:
        """检查是否本周创建"""
        created_str = lead.get('created', '')
        if not created_str:
            return False
        try:
            created = datetime.fromisoformat(created_str)
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            return created >= week_ago
        except:
            return False
    
    def generate_all_dashboards(self) -> Dict[str, str]:
        """为所有客户生成 Dashboard"""
        results = {}
        
        if not self.clients:
            logger.warning("⚠️  没有客户，创建演示客户")
            self.create_demo_client()
        
        for client in self.clients:
            try:
                client_id = client['id']
                client_name = client['name']
                
                # 生成 HTML
                html = self.generate_dashboard_html(client)
                
                # 保存 Dashboard
                dashboard_file = DASHBOARDS_DIR / f"{client_id}.html"
                with open(dashboard_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                results[client_id] = {
                    'name': client_name,
                    'dashboard': f"/dashboards/client/{client_id}.html",
                    'leads_count': len(self.get_client_leads(client_id))
                }
                
                logger.info(f"✅ {client_name} Dashboard 已生成")
                
            except Exception as e:
                logger.error(f"❌ 生成 Dashboard 失败 {client.get('name', 'unknown')}: {e}")
        
        return results
    
    def create_demo_client(self) -> None:
        """创建演示客户"""
        demo_client = {
            'id': 'demo_client_001',
            'name': 'Demo 客户 - 新加坡房产中介',
            'email': 'demo@realestate.sg',
            'company': 'PropNex Realty',
            'status': 'active',
            'created': datetime.now().isoformat(),
            'subscription': 'Professional',
            'next_billing': (datetime.now() + timedelta(days=30)).isoformat()
        }
        self.clients.append(demo_client)
        self.save_clients()
        
        # 添加演示线索
        demo_leads = [
            {
                'id': 'lead_001',
                'client_id': 'demo_client_001',
                'name': 'John Tan',
                'company': 'ERA Singapore',
                'status': 'new',
                'created': datetime.now().isoformat()
            },
            {
                'id': 'lead_002',
                'client_id': 'demo_client_001',
                'name': 'Sarah Lee',
                'company': 'OrangeTee',
                'status': 'qualified',
                'created': (datetime.now() - timedelta(days=2)).isoformat()
            },
            {
                'id': 'lead_003',
                'client_id': 'demo_client_001',
                'name': 'Mike Wong',
                'company': 'Huttons Asia',
                'status': 'contacted',
                'created': (datetime.now() - timedelta(days=5)).isoformat()
            }
        ]
        
        with open(LEADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(demo_leads, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 演示客户已创建")
    
    def update_dashboard_index(self) -> None:
        """更新 Dashboard 索引页面"""
        index_html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>客户 Dashboard - Apex Speed Labs</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
        }
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        .card h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        .card .company {
            color: #666;
            margin-bottom: 20px;
        }
        .card .stats {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .card .stat {
            text-align: center;
        }
        .card .stat .value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .card .stat .label {
            font-size: 0.9em;
            color: #666;
        }
        .card .btn {
            display: block;
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: opacity 0.3s;
        }
        .card .btn:hover {
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 客户 Dashboard</h1>
            <p>Apex Speed Labs | 数据驱动的客户管理</p>
        </div>
        
        <div class="cards-grid">
"""
        
        for client in self.clients:
            client_id = client['id']
            leads_count = len(self.get_client_leads(client_id))
            index_html += f"""
            <div class="card">
                <h3>{client.get('name', 'Unknown')}</h3>
                <div class="company">{client.get('company', '')}</div>
                <div class="stats">
                    <div class="stat">
                        <div class="value">{leads_count}</div>
                        <div class="label">线索数</div>
                    </div>
                    <div class="stat">
                        <div class="value">{client.get('subscription', 'Basic')}</div>
                        <div class="label">套餐</div>
                    </div>
                </div>
                <a href="{client_id}.html" class="btn">查看 Dashboard</a>
            </div>
"""
        
        index_html += """
        </div>
    </div>
</body>
</html>
        """
        
        index_file = DASHBOARDS_DIR / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        logger.info("✅ Dashboard 索引已更新")

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("🚀 客户 Dashboard 自动化系统启动")
    logger.info("=" * 60)
    
    dashboard = ClientDashboard()
    results = dashboard.generate_all_dashboards()
    dashboard.update_dashboard_index()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("📊 Dashboard 生成完成")
    logger.info("=" * 60)
    logger.info(f"✅ 已为 {len(results)} 个客户生成 Dashboard")
    
    for client_id, info in results.items():
        logger.info(f"  - {info['name']}: {info['leads_count']} 条线索")
    
    logger.info(f"📍 索引页: http://167.71.120.132/dashboards/client/index.html")

if __name__ == "__main__":
    main()
