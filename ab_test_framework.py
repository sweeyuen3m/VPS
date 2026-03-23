#!/usr/bin/env python3
"""
A/B 测试框架
自动优化 LinkedIn 和 Email 话术，提升转化率
"""

import json
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 配置日志
LOG_DIR = "/root/apex-automation/logs"
DATA_DIR = "/root/apex-automation/data"
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/ab_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ABTestFramework:
    """A/B 测试框架"""

    def __init__(self):
        self.experiment_file = f"{DATA_DIR}/ab_test_experiments.json"
        self.stats_file = f"{DATA_DIR}/ab_test_stats.json"
        self.experiments = self._load_experiments()
        self.stats = self._load_stats()

    def _load_experiments(self):
        """加载实验配置"""
        if Path(self.experiment_file).exists():
            with open(self.experiment_file, 'r') as f:
                return json.load(f)
        return self._create_default_experiments()

    def _load_stats(self):
        """加载统计数据"""
        if Path(self.stats_file).exists():
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_experiments(self):
        """保存实验配置"""
        with open(self.experiment_file, 'w') as f:
            json.dump(self.experiments, f, indent=2)

    def _save_stats(self):
        """保存统计数据"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def _create_default_experiments(self):
        """创建默认实验配置"""
        return {
            "linkedin_messages": {
                "name": "LinkedIn 私信话术测试",
                "type": "message",
                "variants": [
                    {
                        "id": "linkedin_v1",
                        "name": "版本 1 - 价值导向",
                        "content": """Hi {name},

I noticed you're working in {industry} - great to connect!

Quick question: Are you spending too much time on repetitive customer messages?

We help businesses automate these with AI - saving 10+ hours/week. Currently offering 30% OFF for new clients.

Would you be open to a free 15-min demo?

Best,
Stark
Apex Speed Labs""",
                        "weight": 10,
                        "stats": {"sent": 0, "replied": 0, "converted": 0}
                    },
                    {
                        "id": "linkedin_v2",
                        "name": "版本 2 - 成功故事",
                        "content": """Hi {name},

Congrats on your success in {industry}!

I help businesses like yours automate customer service with AI. Our clients typically save 10+ hours per week.

Currently offering 30% OFF + 14-day money-back guarantee.

Interested in a quick demo?

Best,
Stark
Apex Speed Labs""",
                        "weight": 10,
                        "stats": {"sent": 0, "replied": 0, "converted": 0}
                    },
                    {
                        "id": "linkedin_v3",
                        "name": "版本 3 - 痛点提问",
                        "content": """Hi {name},

Great to connect with someone in {industry}!

Quick question: Are you tired of answering same questions over and over?

We help businesses automate these with AI - 24/7 support, instant responses.

Free 15-min demo? No commitment needed.

Best,
Stark
Apex Speed Labs""",
                        "weight": 10,
                        "stats": {"sent": 0, "replied": 0, "converted": 0}
                    }
                ],
                "created_at": datetime.now().isoformat(),
                "status": "active"
            },
            "email_subjects": {
                "name": "Email 主题行测试",
                "type": "email_subject",
                "variants": [
                    {
                        "id": "email_subject_v1",
                        "name": "版本 1 - 直接利益",
                        "content": "Save 10+ hours/week with AI automation",
                        "weight": 10,
                        "stats": {"sent": 0, "opened": 0, "clicked": 0, "converted": 0}
                    },
                    {
                        "id": "email_subject_v2",
                        "name": "版本 2 - 好奇心驱动",
                        "content": "Quick question about your {industry} business",
                        "weight": 10,
                        "stats": {"sent": 0, "opened": 0, "clicked": 0, "converted": 0}
                    },
                    {
                        "id": "email_subject_v3",
                        "name": "版本 3 - 紧急感",
                        "content": "Limited time: 30% OFF AI automation (expires soon)",
                        "weight": 10,
                        "stats": {"sent": 0, "opened": 0, "clicked": 0, "converted": 0}
                    }
                ],
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
        }

    def select_variant(self, experiment_name):
        """选择最佳变体（基于权重和转化率）"""
        if experiment_name not in self.experiments:
            logger.error(f"实验不存在: {experiment_name}")
            return None

        experiment = self.experiments[experiment_name]
        variants = experiment["variants"]

        # 计算每个变体的总权重
        total_weight = sum(v["weight"] for v in variants)

        # 基于权重随机选择
        r = random.uniform(0, total_weight)
        current_weight = 0

        for variant in variants:
            current_weight += variant["weight"]
            if r <= current_weight:
                logger.info(f"选择变体: {variant['name']} (权重: {variant['weight']})")
                return variant

        # 返回最后一个变体
        return variants[-1]

    def record_interaction(self, experiment_name, variant_id, interaction_type):
        """记录交互数据"""
        if experiment_name not in self.experiments:
            logger.error(f"实验不存在: {experiment_name}")
            return

        experiment = self.experiments[experiment_name]

        # 找到对应变体
        variant = next((v for v in experiment["variants"] if v["id"] == variant_id), None)
        if not variant:
            logger.error(f"变体不存在: {variant_id}")
            return

        # 记录交互
        if interaction_type not in variant["stats"]:
            variant["stats"][interaction_type] = 0
        variant["stats"][interaction_type] += 1

        # 保存数据
        self._save_experiments()

        logger.info(f"记录交互: {experiment_name} - {variant_id} - {interaction_type}")

    def calculate_conversion_rate(self, variant_id):
        """计算转化率"""
        for experiment_name, experiment in self.experiments.items():
            for variant in experiment["variants"]:
                if variant["id"] == variant_id:
                    stats = variant["stats"]
                    if stats["sent"] > 0:
                        if "replied" in stats:
                            reply_rate = (stats["replied"] / stats["sent"]) * 100
                        else:
                            reply_rate = 0

                        if "converted" in stats:
                            conversion_rate = (stats["converted"] / stats["sent"]) * 100
                        else:
                            conversion_rate = 0

                        return {
                            "reply_rate": round(reply_rate, 2),
                            "conversion_rate": round(conversion_rate, 2)
                        }
        return {"reply_rate": 0, "conversion_rate": 0}

    def get_best_variant(self, experiment_name):
        """获取最佳变体"""
        if experiment_name not in self.experiments:
            logger.error(f"实验不存在: {experiment_name}")
            return None

        experiment = self.experiments[experiment_name]
        variants = experiment["variants"]

        # 按转化率排序
        sorted_variants = sorted(
            variants,
            key=lambda v: self.calculate_conversion_rate(v["id"])["conversion_rate"],
            reverse=True
        )

        best = sorted_variants[0]
        logger.info(f"最佳变体: {best['name']}")

        return best

    def generate_report(self):
        """生成测试报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "experiments": []
        }

        for exp_name, exp_data in self.experiments.items():
            exp_report = {
                "name": exp_data["name"],
                "status": exp_data["status"],
                "variants": []
            }

            for variant in exp_data["variants"]:
                rates = self.calculate_conversion_rate(variant["id"])
                exp_report["variants"].append({
                    "id": variant["id"],
                    "name": variant["name"],
                    "stats": variant["stats"],
                    "rates": rates
                })

            report["experiments"].append(exp_report)

        # 保存报告
        report_file = f"{LOG_DIR}/ab_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"报告已生成: {report_file}")
        return report


if __name__ == "__main__":
    # 测试代码
    framework = ABTestFramework()

    # 测试选择变体
    variant = framework.select_variant("linkedin_messages")
    print(f"选择的变体: {variant['name']}")
    print(f"内容: {variant['content']}")

    # 记录交互
    framework.record_interaction("linkedin_messages", variant["id"], "sent")

    # 生成报告
    report = framework.generate_report()
    print(f"报告已生成")
