#!/usr/bin/env python3
"""
A/B测试框架 - 优化销售转化流程
支持多维度测试：邮件主题、邮件内容、话术、CTA等
"""
import json
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import defaultdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/stevenwong/WorkBuddy/20260318123157/logs/ab_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ABTestVariant:
    """A/B测试变体"""
    name: str
    content: str
    type: str  # 'email_subject', 'email_body', 'message', 'cta'

@dataclass
class ABTestExperiment:
    """A/B测试实验"""
    name: str
    variants: List[ABTestVariant]
    started_at: datetime
    ended_at: datetime = None
    traffic_split: Dict[str, float] = None

class ABTestManager:
    def __init__(self):
        self.experiments: Dict[str, ABTestExperiment] = {}
        self.conversion_data: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'sent': 0,
            'opened': 0,
            'clicked': 0,
            'converted': 0,
            'revenue': 0.0
        })
        self.load_experiments()

    def create_experiment(self, experiment_name: str, variants: List[ABTestVariant]):
        """创建新的A/B测试实验"""
        experiment = ABTestExperiment(
            name=experiment_name,
            variants=variants,
            started_at=datetime.now(),
            traffic_split={v.name: 1.0/len(variants) for v in variants}
        )

        self.experiments[experiment_name] = experiment
        self.save_experiments()

        logger.info(f"✅ 创建实验: {experiment_name}, 变体数量: {len(variants)}")
        return experiment

    def get_variant(self, experiment_name: str, user_id: str = None) -> ABTestVariant:
        """获取变体（随机分配或基于用户ID的确定性分配）"""
        if experiment_name not in self.experiments:
            logger.warning(f"实验不存在: {experiment_name}")
            return None

        experiment = self.experiments[experiment_name]

        # 如果有user_id，使用确定性分配（同一用户总是得到相同变体）
        if user_id:
            hash_val = hash(f"{experiment_name}_{user_id}") % len(experiment.variants)
            selected_variant = experiment.variants[hash_val]
        else:
            # 随机分配
            selected_variant = random.choice(experiment.variants)

        logger.info(f"📊 实验: {experiment_name}, 分配变体: {selected_variant.name}")
        return selected_variant

    def record_impression(self, experiment_name: str, variant_name: str):
        """记录曝光"""
        if experiment_name not in self.conversion_data:
            self.conversion_data[experiment_name] = defaultdict(lambda: {
                'sent': 0,
                'opened': 0,
                'clicked': 0,
                'converted': 0,
                'revenue': 0.0
            })

        self.conversion_data[experiment_name][variant_name]['sent'] += 1
        self.save_conversion_data()

    def record_conversion(self, experiment_name: str, variant_name: str, event_type: str, value: float = 0.0):
        """记录转化事件"""
        if event_type not in ['opened', 'clicked', 'converted']:
            logger.error(f"无效的事件类型: {event_type}")
            return

        self.conversion_data[experiment_name][variant_name][event_type] += 1
        if event_type == 'converted':
            self.conversion_data[experiment_name][variant_name]['revenue'] += value

        self.save_conversion_data()
        logger.info(f"📈 转化记录: {experiment_name} / {variant_name} / {event_type} = {value}")

    def analyze_results(self, experiment_name: str) -> Dict[str, Any]:
        """分析A/B测试结果"""
        if experiment_name not in self.experiments:
            logger.error(f"实验不存在: {experiment_name}")
            return None

        experiment = self.experiments[experiment_name]
        data = self.conversion_data.get(experiment_name, {})

        results = {
            'experiment_name': experiment_name,
            'started_at': experiment.started_at.isoformat(),
            'variants': [],
            'winner': None,
            'statistical_significance': False
        }

        total_sent = 0
        total_converted = 0

        for variant in experiment.variants:
            variant_data = data.get(variant.name, {})
            sent = variant_data.get('sent', 0)
            opened = variant_data.get('opened', 0)
            clicked = variant_data.get('clicked', 0)
            converted = variant_data.get('converted', 0)
            revenue = variant_data.get('revenue', 0.0)

            # 计算转化率
            open_rate = (opened / sent * 100) if sent > 0 else 0
            click_rate = (clicked / sent * 100) if sent > 0 else 0
            conversion_rate = (converted / sent * 100) if sent > 0 else 0
            avg_revenue = (revenue / converted) if converted > 0 else 0

            results['variants'].append({
                'name': variant.name,
                'sent': sent,
                'open_rate': f"{open_rate:.2f}%",
                'click_rate': f"{click_rate:.2f}%",
                'conversion_rate': f"{conversion_rate:.2f}%",
                'revenue': revenue,
                'avg_revenue': f"${avg_revenue:.2f}"
            })

            total_sent += sent
            total_converted += converted

        # 确定赢家（简单版：基于转化率）
        if results['variants']:
            results['variants'].sort(key=lambda x: float(x['conversion_rate'].replace('%', '')), reverse=True)
            results['winner'] = results['variants'][0]['name']

            # 简单的统计显著性判断（需要更多样本才准确）
            if total_sent > 100 and total_converted > 10:
                results['statistical_significance'] = True

        logger.info(f"📊 分析结果: {experiment_name}, 赢家: {results['winner']}")
        return results

    def end_experiment(self, experiment_name: str):
        """结束实验"""
        if experiment_name in self.experiments:
            self.experiments[experiment_name].ended_at = datetime.now()
            self.save_experiments()
            logger.info(f"✅ 实验已结束: {experiment_name}")

    def load_experiments(self):
        """加载实验配置"""
        try:
            with open('/Users/stevenwong/WorkBuddy/20260318123157/data/ab_test_experiments.json', 'r') as f:
                data = json.load(f)
                for exp_data in data:
                    variants = [ABTestVariant(**v) for v in exp_data['variants']]
                    exp_data['variants'] = variants
                    exp_data['started_at'] = datetime.fromisoformat(exp_data['started_at'])
                    if exp_data.get('ended_at'):
                        exp_data['ended_at'] = datetime.fromisoformat(exp_data['ended_at'])
                    self.experiments[exp_data['name']] = ABTestExperiment(**exp_data)
        except FileNotFoundError:
            logger.info("未找到实验配置文件，将创建新的")
        except Exception as e:
            logger.error(f"加载实验配置失败: {e}")

    def save_experiments(self):
        """保存实验配置"""
        import os
        os.makedirs('/Users/stevenwong/WorkBuddy/20260318123157/data', exist_ok=True)

        data = []
        for exp in self.experiments.values():
            exp_data = {
                'name': exp.name,
                'variants': [{'name': v.name, 'content': v.content, 'type': v.type} for v in exp.variants],
                'started_at': exp.started_at.isoformat(),
                'ended_at': exp.ended_at.isoformat() if exp.ended_at else None,
                'traffic_split': exp.traffic_split
            }
            data.append(exp_data)

        with open('/Users/stevenwong/WorkBuddy/20260318123157/data/ab_test_experiments.json', 'w') as f:
            json.dump(data, f, indent=2)

    def load_conversion_data(self):
        """加载转化数据"""
        try:
            with open('/Users/stevenwong/WorkBuddy/20260318123157/data/ab_test_conversions.json', 'r') as f:
                data = json.load(f)
                for exp_name, variants in data.items():
                    for var_name, metrics in variants.items():
                        self.conversion_data[exp_name][var_name] = metrics
        except FileNotFoundError:
            logger.info("未找到转化数据文件")
        except Exception as e:
            logger.error(f"加载转化数据失败: {e}")

    def save_conversion_data(self):
        """保存转化数据"""
        import os
        os.makedirs('/Users/stevenwong/WorkBuddy/20260318123157/data', exist_ok=True)

        # 转换为可序列化的格式
        data = {}
        for exp_name, variants in self.conversion_data.items():
            data[exp_name] = {k: dict(v) for k, v in variants.items()}

        with open('/Users/stevenwong/WorkBuddy/20260318123157/data/ab_test_conversions.json', 'w') as f:
            json.dump(data, f, indent=2)

# 预定义的A/B测试模板
EMAIL_SUBJECT_VARIANTS = [
    ABTestVariant("subject_a", "Exclusive 7-Days Free Trial: Lead Improvement Service", "email_subject"),
    ABTestVariant("subject_b", "Boost Your Sales with AI-Powered Leads", "email_subject"),
    ABTestVariant("subject_c", "Limited Time Offer: 70% Off Your First Month", "email_subject"),
    ABTestVariant("subject_d", "Hi {name}, I Can Help You Get More Leads", "email_subject"),
]

EMAIL_BODY_VARIANTS = [
    ABTestVariant("body_a", """
Hi {name},

I saw your profile and I believe I can help you generate more leads for your business.

My team at Apex Speed Labs has developed an AI-powered lead generation system that:
✅ Automatically finds qualified prospects
✅ Sends personalized outreach at scale
✅ Tracks and nurtures leads automatically
✅ Increases conversion rates by 300%+

Special Offer:
🎁 7-day free trial (no credit card required)
💰 70% off your first month
🚀 Custom solution for your {industry} needs
📞 24/7 local support

Would you be open to a quick 15-minute call to see if this could work for your business?

Best regards,
Steven
CEO, Apex Speed Labs
+65 9298 4102
""", "email_body"),

    ABTestVariant("body_b", """
Hi {name},

Quick question - are you happy with your current lead generation strategy?

Many {industry} owners I speak with tell me they're struggling with:
- Finding enough qualified prospects
- Time-consuming manual outreach
- Low conversion rates

At Apex Speed Labs, we solve all of this with AI automation.

Results from our Singapore clients:
- Average 150+ new qualified leads/month
- 85% reduction in manual work
- 3x increase in conversion rates

I'm confident we can help you too.

Special Offer: 70% off first month + 7-day free trial

Let's chat?
Steven
+65 9298 4102
""", "email_body"),
]

# 使用示例
if __name__ == "__main__":
    # 创建A/B测试管理器
    manager = ABTestManager()

    # 创建邮件主题测试
    manager.create_experiment("email_subject_test", EMAIL_SUBJECT_VARIANTS)

    # 创建邮件内容测试
    manager.create_experiment("email_body_test", EMAIL_BODY_VARIANTS)

    # 模拟使用
    for i in range(10):
        # 获取邮件主题
        subject_variant = manager.get_variant("email_subject_test", user_id=f"user_{i}")
        print(f"Subject: {subject_variant.content}")

        # 获取邮件内容
        body_variant = manager.get_variant("email_body_test", user_id=f"user_{i}")
        print(f"Body variant: {body_variant.name}")

        # 记录曝光
        manager.record_impression("email_subject_test", subject_variant.name)
        manager.record_impression("email_body_test", body_variant.name)

    # 模拟一些转化
    manager.record_conversion("email_subject_test", "subject_a", "opened")
    manager.record_conversion("email_subject_test", "subject_b", "opened")
    manager.record_conversion("email_body_test", "body_a", "clicked")
    manager.record_conversion("email_body_test", "body_a", "converted", 99.0)

    # 分析结果
    results = manager.analyze_results("email_subject_test")
    print("\n分析结果:")
    print(json.dumps(results, indent=2))
