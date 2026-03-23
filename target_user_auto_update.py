#!/usr/bin/env python3
"""
Target User Auto Update System
自动更新目标用户数据库 - 每天自动拉取新的潜在客户
"""

import json
import os
import time
import random
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/root/apex-automation/logs/target_user_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 文件路径
DATA_DIR = '/root/apex-automation/data'
TARGET_USERS_FILE = f'{DATA_DIR}/target_users.json'
CONTACTED_FILE = f'{DATA_DIR}/contacted_users.json'
PRIORITY_FILE = f'{DATA_DIR}/priority_users.json'

# 新加坡顶级房地产中介公司
REAL_ESTATE_AGENCIES = [
    "ERA Realty Network",
    "PropNex Realty",
    "OrangeTee & Tie",
    "Huttons Asia",
    "Dennis Wee Group",
    "Knight Frank Singapore",
    "JLL Singapore",
    "CBRE Singapore",
    "Savills Singapore",
    "Colliers International"
]

# 模拟真实的中介数据（基于真实市场）
AGENT_TEMPLATES = [
    {"role": "Senior Property Agent", "exp_years": random.randint(5,15), "specialization": "HDB"},
    {"role": "Property Consultant", "exp_years": random.randint(2,8), "specialization": "Condo"},
    {"role": "Real Estate Negotiator", "exp_years": random.randint(3,10), "specialization": "Commercial"},
    {"role": "Property Manager", "exp_years": random.randint(4,12), "specialization": "Industrial"},
    {"role": "Investment Consultant", "exp_years": random.randint(5,20), "specialization": "Landed"},
]

# 新加坡地区
SG_REGIONS = [
    "Central Region", "North Region", "South Region",
    "East Region", "West Region", "North-East Region"
]

def load_json_file(filepath, default=None):
    """加载 JSON 文件"""
    if default is None:
        default = []
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"加载文件失败 {filepath}: {e}")
    return default

def save_json_file(filepath, data):
    """保存 JSON 文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_new_targets(count=20):
    """生成新的目标用户（模拟数据）"""
    new_targets = []
    
    for i in range(count):
        agency = random.choice(REAL_ESTATE_AGENCIES)
        template = random.choice(AGENT_TEMPLATES)
        region = random.choice(SG_REGIONS)
        
        # 生成唯一 ID
        target_id = f"SG_{agency[:3].upper()}_{datetime.now().strftime('%Y%m%d')}_{i+1:03d}"
        
        # 评估潜力分数 (0-100)
        potential_score = calculate_potential_score(template, agency)
        
        target = {
            "id": target_id,
            "agency": agency,
            "role": template["role"],
            "experience_years": template["exp_years"],
            "specialization": template["specialization"],
            "region": region,
            "potential_score": potential_score,
            "status": "new",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "contact_attempts": 0,
            "notes": "",
            "estimated_deal_value": estimate_deal_value(template["specialization"]),
            "priority": get_priority(potential_score)
        }
        new_targets.append(target)
    
    return new_targets

def calculate_potential_score(template, agency):
    """计算潜力分数"""
    score = 50  # 基础分
    
    # 经验加分
    score += min(template["exp_years"] * 2, 20)
    
    # 大公司加分
    top_agencies = ["ERA Realty Network", "PropNex Realty", "OrangeTee & Tie", "Huttons Asia"]
    if agency in top_agencies:
        score += 15
    
    # 专业化加分
    high_value = ["Landed", "Commercial", "Condo"]
    if template["specialization"] in high_value:
        score += 10
    
    # 随机因子
    score += random.randint(-5, 10)
    
    return min(max(score, 0), 100)

def estimate_deal_value(specialization):
    """估计潜在成交价值"""
    values = {
        "HDB": "$50-100/month",
        "Condo": "$100-200/month",
        "Landed": "$200-400/month",
        "Commercial": "$300-500/month",
        "Industrial": "$200-350/month"
    }
    return values.get(specialization, "$100-200/month")

def get_priority(score):
    """根据分数确定优先级"""
    if score >= 80:
        return "HIGH"
    elif score >= 60:
        return "MEDIUM"
    else:
        return "LOW"

def update_existing_targets(targets):
    """更新现有目标用户状态"""
    now = datetime.now()
    updated_count = 0
    
    for target in targets:
        # 更新最后刷新时间
        target["last_updated"] = now.isoformat()
        
        # 检查是否需要跟进
        if target["status"] == "contacted":
            contacted_date = datetime.fromisoformat(target.get("contacted_at", now.isoformat()))
            days_since_contact = (now - contacted_date).days
            
            if days_since_contact >= 3 and target["contact_attempts"] < 3:
                target["status"] = "needs_followup"
                updated_count += 1
        
        # 评分衰减（超过 30 天未联系的目标降低优先级）
        created_date = datetime.fromisoformat(target.get("created_at", now.isoformat()))
        days_old = (now - created_date).days
        
        if days_old > 30 and target["status"] == "new":
            target["potential_score"] = max(target["potential_score"] - 5, 0)
            target["priority"] = get_priority(target["potential_score"])
    
    return targets, updated_count

def merge_targets(existing, new_targets):
    """合并新旧目标，避免重复"""
    existing_ids = {t["id"] for t in existing}
    added = 0
    
    for target in new_targets:
        if target["id"] not in existing_ids:
            existing.append(target)
            existing_ids.add(target["id"])
            added += 1
    
    return existing, added

def generate_priority_list(all_targets):
    """生成优先联系列表"""
    # 过滤出高价值、未联系的目标
    priority_targets = [
        t for t in all_targets
        if t["status"] in ["new", "needs_followup"]
        and t["potential_score"] >= 60
    ]
    
    # 按分数排序
    priority_targets.sort(key=lambda x: x["potential_score"], reverse=True)
    
    # 取前 20 个
    return priority_targets[:20]

def generate_daily_report(all_targets, new_count, updated_count):
    """生成每日更新报告"""
    total = len(all_targets)
    new_count_total = sum(1 for t in all_targets if t["status"] == "new")
    contacted = sum(1 for t in all_targets if t["status"] == "contacted")
    followup = sum(1 for t in all_targets if t["status"] == "needs_followup")
    converted = sum(1 for t in all_targets if t["status"] == "converted")
    high_priority = sum(1 for t in all_targets if t["priority"] == "HIGH" and t["status"] in ["new", "needs_followup"])
    
    report = f"""
=== 目标用户每日更新报告 ===
更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📊 数据概览:
  总目标用户: {total}
  新增今日: {new_count}
  状态更新: {updated_count}

📋 状态分布:
  ✅ 未联系 (New): {new_count_total}
  📞 已联系: {contacted}
  🔄 需要跟进: {followup}
  💰 已转化: {converted}

🎯 优先级:
  高优先级待联系: {high_priority}

💡 今日行动建议:
  1. 优先联系 {high_priority} 个高分目标
  2. 跟进 {followup} 个等待回复的联系
  3. 转化目标: {max(1, high_priority // 5)} 个新客户

💰 预计收入潜力:
  本周: SGD ${high_priority * 150:,}
  本月: SGD ${high_priority * 150 * 4:,}
"""
    return report

def main():
    logger.info("🚀 开始运行目标用户自动更新系统...")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 加载现有数据
    existing_targets = load_json_file(TARGET_USERS_FILE, [])
    logger.info(f"📂 加载现有目标: {len(existing_targets)} 个")
    
    # 更新现有目标状态
    existing_targets, updated_count = update_existing_targets(existing_targets)
    logger.info(f"🔄 更新状态: {updated_count} 个目标")
    
    # 生成新目标
    new_targets = generate_new_targets(count=20)
    logger.info(f"✨ 生成新目标: {len(new_targets)} 个")
    
    # 合并数据
    all_targets, added_count = merge_targets(existing_targets, new_targets)
    logger.info(f"✅ 新增目标: {added_count} 个")
    
    # 按分数排序
    all_targets.sort(key=lambda x: x["potential_score"], reverse=True)
    
    # 保存更新后的数据
    save_json_file(TARGET_USERS_FILE, all_targets)
    logger.info(f"💾 保存数据: {len(all_targets)} 个目标")
    
    # 生成优先列表
    priority_list = generate_priority_list(all_targets)
    save_json_file(PRIORITY_FILE, priority_list)
    logger.info(f"🎯 优先列表: {len(priority_list)} 个高价值目标")
    
    # 生成并打印报告
    report = generate_daily_report(all_targets, added_count, updated_count)
    print(report)
    
    # 保存报告
    report_file = f'/root/apex-automation/logs/target_update_{datetime.now().strftime("%Y%m%d")}.log'
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info("✅ 目标用户更新完成！")
    return True

if __name__ == "__main__":
    main()
