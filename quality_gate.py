#!/usr/bin/env python3
"""
自动化质量关卡和验证机制
确保自动化输出的质量和准确性
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/stevenwong/WorkBuddy/20260318123157/logs/quality_gate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class QualityCheckResult:
    """质量检查结果"""
    passed: bool
    score: float
    issues: List[str]
    warnings: List[str]

class QualityGate:
    def __init__(self):
        self.min_score = 0.7  # 最低通过分数
        self.rules = {
            'upwork_application': self.check_upwork_application,
            'linkedin_message': self.check_linkedin_message,
            'email_outreach': self.check_email_outreach
        }

    def check_upwork_application(self, data: Dict) -> QualityCheckResult:
        """检查Upwork申请质量"""
        issues = []
        warnings = []
        score = 1.0

        # 必须有项目标题
        if 'project_title' not in data or not data['project_title']:
            issues.append("缺少项目标题")
            score -= 0.3

        # Cover Letter长度检查
        if 'cover_letter' in data:
            cover_letter = data['cover_letter']
            if len(cover_letter) < 100:
                issues.append("Cover Letter过短（<100字符）")
                score -= 0.2
            elif len(cover_letter) > 2000:
                warnings.append("Cover Letter过长（>2000字符），可能影响阅读")
                score -= 0.1

        # 报价检查
        if 'bid_amount' in data:
            if data['bid_amount'] < 10:
                issues.append("报价过低（<$10）")
                score -= 0.2

        # 时间检查
        if 'delivery_days' in data and data['delivery_days'] > 30:
            warnings.append("交付时间较长（>30天）")
            score -= 0.1

        return QualityCheckResult(
            passed=score >= self.min_score,
            score=max(0, score),
            issues=issues,
            warnings=warnings
        )

    def check_linkedin_message(self, data: Dict) -> QualityCheckResult:
        """检查LinkedIn私信质量"""
        issues = []
        warnings = []
        score = 1.0

        # 必须有收件人姓名
        if 'recipient_name' not in data or not data['recipient_name']:
            issues.append("缺少收件人姓名")
            score -= 0.2

        # 消息内容检查
        if 'message' in data:
            message = data['message']
            if len(message) < 50:
                issues.append("消息过短（<50字符）")
                score -= 0.3
            elif len(message) > 1000:
                warnings.append("消息过长（>1000字符）")
                score -= 0.1

            # 检查个性化程度
            if '{name}' in message:
                issues.append("消息中包含未替换的占位符")
                score -= 0.2

        # 检查是否有联系方式
        if 'message' in data:
            message = data['message']
            if '+65' not in message and '9298 4102' not in message:
                warnings.append("消息中未包含联系方式")
                score -= 0.1

        return QualityCheckResult(
            passed=score >= self.min_score,
            score=max(0, score),
            issues=issues,
            warnings=warnings
        )

    def check_email_outreach(self, data: Dict) -> QualityCheckResult:
        """检查邮件触达质量"""
        issues = []
        warnings = []
        score = 1.0

        # 必须有收件人邮箱
        if 'recipient_email' not in data or not data['recipient_email']:
            issues.append("缺少收件人邮箱")
            score -= 0.3

        # 邮件主题检查
        if 'subject' in data:
            subject = data['subject']
            if len(subject) < 10:
                issues.append("邮件主题过短")
                score -= 0.2
            if 'free trial' not in subject.lower() and 'offer' not in subject.lower():
                warnings.append("邮件主题未包含吸引点")
                score -= 0.1

        # 邮件正文检查
        if 'body' in data:
            body = data['body']
            if len(body) < 100:
                issues.append("邮件正文过短")
                score -= 0.2

            # 检查关键元素
            required_elements = ['7-day', 'free trial', '70% off']
            missing = [e for e in required_elements if e.lower() not in body.lower()]
            if missing:
                warnings.append(f"缺少关键优惠信息: {', '.join(missing)}")
                score -= 0.1 * len(missing)

        return QualityCheckResult(
            passed=score >= self.min_score,
            score=max(0, score),
            issues=issues,
            warnings=warnings
        )

    def run_check(self, check_type: str, data: Dict) -> QualityCheckResult:
        """执行质量检查"""
        if check_type not in self.rules:
            logger.error(f"未知的检查类型: {check_type}")
            return QualityCheckResult(
                passed=False,
                score=0.0,
                issues=["未知检查类型"],
                warnings=[]
            )

        return self.rules[check_type](data)

    def log_result(self, result: QualityCheckResult, check_type: str):
        """记录检查结果"""
        status = "✅ 通过" if result.passed else "❌ 未通过"
        logger.info(f"质量检查 [{check_type}]: {status} (分数: {result.score:.2f})")

        if result.issues:
            for issue in result.issues:
                logger.error(f"  - 问题: {issue}")

        if result.warnings:
            for warning in result.warnings:
                logger.warning(f"  - 警告: {warning}")

        # 保存到文件
        check_record = {
            'timestamp': datetime.now().isoformat(),
            'type': check_type,
            'passed': result.passed,
            'score': result.score,
            'issues': result.issues,
            'warnings': result.warnings
        }

        try:
            with open('/Users/stevenwong/WorkBuddy/20260318123157/data/quality_gate_history.json', 'a') as f:
                f.write(json.dumps(check_record) + '\n')
        except Exception as e:
            logger.error(f"保存检查记录失败: {e}")

# 使用示例
if __name__ == "__main__":
    gate = QualityGate()

    # 测试Upwork申请检查
    print("\n=== 测试Upwork申请检查 ===")
    upwork_data = {
        'project_title': 'Build a chatbot for e-commerce',
        'cover_letter': 'Hi, I can help you build a chatbot...',
        'bid_amount': 150,
        'delivery_days': 7
    }
    result = gate.run_check('upwork_application', upwork_data)
    gate.log_result(result, 'upwork_application')

    # 测试LinkedIn私信检查
    print("\n=== 测试LinkedIn私信检查 ===")
    linkedin_data = {
        'recipient_name': 'John',
        'message': 'Hi John, hope you are doing well! I wanted to reach out...'
    }
    result = gate.run_check('linkedin_message', linkedin_data)
    gate.log_result(result, 'linkedin_message')

    # 测试邮件触达检查
    print("\n=== 测试邮件触达检查 ===")
    email_data = {
        'recipient_email': 'test@example.com',
        'subject': 'Exclusive 7-Day Free Trial Offer',
        'body': 'Hi there, we are offering a 7-day free trial with 70% off...'
    }
    result = gate.run_check('email_outreach', email_data)
    gate.log_result(result, 'email_outreach')
