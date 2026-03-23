"""
Apex Speed Labs - 优化话术模板 v2.0
5 个 LinkedIn 私信 + 5 个邮件模板

基于 FULL_AUTO_OPTIMIZATION_PLAN_V4.md 的最佳实践

作者: Stark Wong
更新: 2026-03-23
"""

import json
import random
from typing import Dict, List

# LinkedIn 私信话术 (5 个版本)
LINKEDIN_TEMPLATES = {
    'version_1_benefit_driven': {
        'name': '利益驱动型',
        'priority': 'HIGH',
        'subject': 'AI 帮您找到下一个 $100K 成交？🎯',
        'body': '''Hi [Name],

看到您在 [Company] 专注于 [区域/类型] 房产，
这个市场的客户确实很有潜力。

我们用 AI 帮其他中介找到 23 个高质量客户，
成交总额 $2.3M，平均成交周期 4.2 天。

想送您 5 条免费测试线索看看效果如何？
如果不喜欢，不需要任何解释，删除就行。

[这里插入简短案例研究]

Steven | Apex Speed Labs
sweeyuen3@apexspeedlabs.com | +65 9298 4102
https://leads-improvement.sweeyuen3.workers.dev

PS: 本周新客户 7 折优惠，10 条线索只需 $700。
''',
        'tags': ['利益', '数据', '紧迫感']
    },
    'version_2_pain_point': {
        'name': '痛点直击型',
        'priority': 'HIGH',
        'subject': '每天花 3 小时找客户，还是 AI 帮您？',
        'body': '''Hi [Name],

作为房产中介，您最痛的是什么？
- 每天花 3-5 小时在 PropertyGuru 筛选客户？
- 打 100 个电话，只有 1-2 个有意向？
- 月底业绩压力大，不知道客户在哪？

我们帮 [Competitor Name] 解决了这个问题：
→ 每天 10 条精准线索，直接推给您
→ 80% 的客户有明确购房意向
→ 平均 4 天内完成首单成交

想试试吗？
送您 5 条免费测试线索，看看能不能帮您成交。

Steven Wong
+65 9298 4102
''',
        'tags': ['痛点', '对比', '免费试用']
    },
    'version_3_scarcity': {
        'name': '稀缺感型',
        'priority': 'MEDIUM',
        'subject': '仅限本周：[您的区域] 优先级线索 🚀',
        'body': '''Hi [Name],

我们 AI 系统刚在 [区域] 发现 15 个高质量客户：
- 预算 $1.5-3M
- 明确表示要在这个区域购房
- 计划 1 个月内决策

想优先锁定这批客户吗？
我们只和 3 位本地中介合作，
目前已经和 [Competitor 1] 和 [Competitor 2] 签约。

您是第 3 位吗？
回复 "YES" 我发您 2 条免费测试，
如果效果好，我们继续合作。

Steven | Apex Speed Labs
''',
        'tags': ['稀缺', '紧迫感', '社交证明']
    },
    'version_4_social_proof': {
        'name': '社会证明型',
        'priority': 'HIGH',
        'subject': '[Competitor] 上周用我们的线索成交 $1.2M 💰',
        'body': '''Hi [Name],

上周我们的线索帮助：
- [Competitor 1] 成交 3 单，总额 $800K
- [Competitor 2] 成交 1 单，$1.2M
- [Competitor 3] 成交 2 单，$600K

他们的共同点？
都用我们的 AI 线索服务。

为什么他们选择我们？
✓ 线索准确率 80%（行业平均 60%）
✓ 7 折优惠，每条 $70
✓ 免费测试，零风险

您想试试吗？
送您 5 条免费测试线索，
看看能不能帮您成交下一单。

Steven | Apex Speed Labs
sweeyuen3@apexspeedlabs.com
''',
        'tags': ['社会证明', '对比', '免费试用']
    },
    'version_5_curiosity': {
        'name': '好奇心型',
        'priority': 'MEDIUM',
        'subject': '一个让您每周多 10 个潜在客户的工具',
        'body': '''Hi [Name],

想知道怎么用 AI 把线索转化率提升 50% 吗？

我们帮新加坡中介：
- 每周增加 10-15 个潜在客户
- 缩短成交周期 40%
- 减少 60% 的无效电话

想看真实案例吗？
回复 "CASE" 我发您详细报告。

或者直接送您 5 条免费测试线索，
亲身体验一下。

Steven Wong
+65 9298 4102
''',
        'tags': ['好奇心', '教育', '免费试用']
    }
}

# 邮件模板 (5 个版本)
EMAIL_TEMPLATES = {
    'version_1_full_initial': {
        'name': '完整版（首封）',
        'type': 'initial',
        'priority': 'HIGH',
        'subject': 'AI 帮您找到下一个 $100K 成交（附免费测试）🎯',
        'body': '''Hi [Name],

希望这封邮件不会打扰您。

我注意到您在 [Company] 专注于 [区域] 的房产销售，
这个市场确实有不少机会。

我们开发了一个 AI 驱动的线索生成系统，
专门为新加坡房产中介服务。

**简单来说，我们帮您：**

1. 自动筛选 PropertyGuru、99.co、EdgeProp 的潜在客户
2. 分析购房意向、预算、时间窗口
3. 每天推送 10-15 条高质量线索到您的 WhatsApp/Email

**真实案例（本月数据）：**

- ERA 中介 A: 10 天成交 2 单，$420K
- PropNex 中介 B: 15 天成交 3 单，$1.8M
- OrangeTee 中介 C: 8 天成交 1 单，$650K

平均成交周期：4.2 天（行业平均 21 天）
平均线索质量：80% 有效（行业平均 60%）

**定价：**

- 标准价：$100/条线索
- **本周新客户 7 折：$70/条** ⭐
- 首次购买：10 条起，$700

**零风险承诺：**

送您 5 条免费测试线索。
如果其中有 3 条无效，全额退款，
并且额外赠送 10 条。

**想试试吗？**

回复这封邮件，我立即给您发送 5 条测试线索。
或者加我微信/WhatsApp：+65 9298 4102

**附件：** 详细案例研究.pdf

祝您本周有更多成交！

Steven Wong
CEO, Apex Speed Labs
Email: sweeyuen3@apexspeedlabs.com
Phone: +65 9298 4102
Website: https://leads-improvement.sweeyuen3.workers.dev

---

PS: 如果您现在不方便，这封邮件可以保存备用。
我们的服务持续改进，下周可能没有 7 折优惠了。

PPS: 我们每天只和 3 位新中介合作，
避免过度竞争。如果您有兴趣，建议尽快回复。
''',
        'tags': ['完整', '数据', '优惠', '承诺']
    },
    'version_2_followup': {
        'name': '简短版（跟进）',
        'type': 'followup',
        'priority': 'HIGH',
        'subject': '还没决定？再送您 2 条免费线索 🎁',
        'body': '''Hi [Name],

上周我给您发了 5 条免费测试线索，
想问问您的反馈如何？

如果您还没来得及查看，
我特意再准备 2 条最新线索：

**线索 1:**
- 姓名: John Tan
- 预算: $2.5M
- 目标区域: Bukit Timah
- 意向: 2 个月内购房，已看过 5 套房产
- 联系方式: [WhatsApp/Phone]

**线索 2:**
- 姓名: Sarah Lim
- 预算: $1.8M
- 目标区域: River Valley
- 意向: 1 个月内决策，正在申请银行贷款
- 联系方式: [WhatsApp/Phone]

这是我们的诚意展示，
不占用您任何资源，只需要几分钟查看。

如果您觉得有用，
我们的 7 折优惠还在（本周到期）：
10 条线索 $700。

回复 "OK" 我继续提供更多线索。

Steven Wong
+65 9298 4102
''',
        'tags': ['跟进', '额外价值', '优惠']
    },
    'version_3_urgency': {
        'name': '紧迫型（周末前）',
        'type': 'urgency',
        'priority': 'HIGH',
        'subject': '周末前帮您锁定这批高质量客户 🚀',
        'body': '''Hi [Name],

周末是房产中介的黄金时间，
很多客户会在周末看房、做决策。

我们 AI 系统刚发现了 8 个高质量线索，
计划分配给 [您的区域] 的 3 位中介。

目前已经分配给：
- [Competitor 1] - 3 条线索
- [Competitor 2] - 3 条线索

还剩 2 条，想优先给您吗？

**线索质量：**
- 预算 $1.5-3M
- 明确表示周末有空看房
- 1 个月内决策

如果您回复今天下午 5 点前，
我立即把线索发给您。

**特别优惠：**
这 2 条线索 + 8 条包月套餐 = $630
（原价 $1000，7 折）

想锁定的回复 "LOCK"。

Steven Wong
Apex Speed Labs
''',
        'tags': ['紧迫感', '稀缺', '优惠']
    },
    'version_4_data_driven': {
        'name': '数据驱动型（月度报告）',
        'type': 'report',
        'priority': 'MEDIUM',
        'subject': '[Company] 您的线索性能报告（附优化建议）📊',
        'body': '''Hi [Name],

这是我为您准备的 3 月线索性能报告：

**【线索表现】**
- 总线索数: 50 条
- 有效线索: 42 条 (84%)
- 已转化: 8 条 (19%)
- 待跟进: 21 条 (50%)

**【转化分析】**
- 已成交: 3 单，$850K
- 谈判中: 5 单，预计 $2.1M
- 潜在价值: $2.95M
- ROI: 1,966% （$850K / $43,000 成本）

**【对比行业平均】**
- 您的转化率: 19% vs 行业 8% ✅
- 您的成交周期: 18 天 vs 行业 28 天 ✅
- 您的线索质量: 84% vs 行业 60% ✅

**【优化建议】**

1. **跟进速度：**
   - 目前平均回复时间: 6 小时
   - 建议: 2 小时内回复
   - 预期提升转化率 25%

2. **线索类型：**
   - 您的强项: 高端客户 ($2M+)
   - 建议: 增加 $1-1.5M 客户比例
   - 预期提升成交量 40%

3. **跟进策略：**
   - 目前电话跟进: 100%
   - 建议: WhatsApp + 电话组合
   - 预期提升回复率 50%

**【下月套餐】**

继续提升您的业绩吗？
推荐套餐：
- 50 条线索 + 优化服务 = $3,500 (7 折)
- 包含: 每周性能报告 + 24/7 支持

回复确认，我立即为您续订。

Steven Wong
Apex Speed Labs
''',
        'tags': ['数据', '分析', '优化', '续订']
    },
    'version_5_feedback': {
        'name': '反馈请求型',
        'type': 'feedback',
        'priority': 'LOW',
        'subject': '只需要 2 分钟，帮我们改进服务 💭',
        'body': '''Hi [Name],

感谢您使用我们的线索服务！

我们一直在改进，
想听听您的真实反馈，帮助我们做得更好。

**【快速反馈（2 分钟）】**

1. 您最满意的是什么？
   □ 线索质量
   □ 响应速度
   □ 价格
   □ 客户服务
   □ 其他: _______

2. 您最不满意的是什么？
   □ 线索数量
   □ 联系方式准确性
   □ 客户意向度
   □ 其他: _______

3. 您会向同事推荐我们吗？
   □ 肯定会
   □ 可能会
   □ 不确定
   □ 不会

4. 您愿意为此服务写简短评价吗？
   （会出现在我们网站，附您的名字和公司）
   是/否

**【感谢您的反馈】**

如果愿意，我们会：
- 送您 3 条免费测试线索
- 永久 8 折优惠（而非 7 折）
- 优先获取高质量线索

直接回复这封邮件即可，
不需要任何复杂操作。

再次感谢您的支持！

Steven Wong
Apex Speed Labs
''',
        'tags': ['反馈', '改进', '激励']
    }
}


class TemplateManager:
    """模板管理器"""
    
    def __init__(self):
        self.linkedin_templates = LINKEDIN_TEMPLATES
        self.email_templates = EMAIL_TEMPLATES
    
    def get_linkedin_template(self, version: str = None) -> Dict:
        """获取 LinkedIn 模板"""
        if version and version in self.linkedin_templates:
            return self.linkedin_templates[version]
        
        # 随机选择（基于优先级）
        high_priority = [k for k, v in self.linkedin_templates.items() 
                         if v['priority'] == 'HIGH']
        medium_priority = [k for k, v in self.linkedin_templates.items() 
                          if v['priority'] == 'MEDIUM']
        
        # 70% 概率选择高优先级
        if random.random() < 0.7 and high_priority:
            selected = random.choice(high_priority)
        else:
            selected = random.choice(list(self.linkedin_templates.keys()))
        
        return self.linkedin_templates[selected]
    
    def get_email_template(self, version: str = None, email_type: str = None) -> Dict:
        """获取邮件模板"""
        # 如果指定版本
        if version and version in self.email_templates:
            return self.email_templates[version]
        
        # 如果指定类型
        if email_type:
            type_templates = {k: v for k, v in self.email_templates.items() 
                            if v['type'] == email_type}
            if type_templates:
                return random.choice(list(type_templates.values()))
        
        # 默认：首封邮件
        initial_templates = {k: v for k, v in self.email_templates.items() 
                           if v['type'] == 'initial'}
        return random.choice(list(initial_templates.values()))
    
    def personalize_template(self, template: Dict, **kwargs) -> Dict:
        """个性化模板"""
        personalized = template.copy()
        
        # 替换占位符
        subject = personalized['subject']
        body = personalized['body']
        
        for key, value in kwargs.items():
            subject = subject.replace(f'[{key}]', value)
            body = body.replace(f'[{key}]', value)
        
        personalized['subject'] = subject
        personalized['body'] = body
        
        return personalized
    
    def save_templates(self, filepath: str):
        """保存模板到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'linkedin': self.linkedin_templates,
                'email': self.email_templates
            }, f, indent=2, ensure_ascii=False)


def main():
    """主函数 - 测试模板"""
    print("=" * 60)
    print("📧 优化话术模板 v2.0")
    print("=" * 60)
    
    # 初始化模板管理器
    manager = TemplateManager()
    
    # 测试 LinkedIn 模板
    print("\n📱 LinkedIn 模板示例:")
    linkedin_template = manager.get_linkedin_template()
    print(f"  版本: {linkedin_template['name']}")
    print(f"  优先级: {linkedin_template['priority']}")
    print(f"  主题: {linkedin_template['subject'][:50]}...")
    
    # 测试邮件模板
    print("\n📧 邮件模板示例:")
    email_template = manager.get_email_template(email_type='initial')
    print(f"  类型: {email_template['type']}")
    print(f"  优先级: {email_template['priority']}")
    print(f"  主题: {email_template['subject'][:50]}...")
    
    print("\n✅ 模板系统正常工作")
    print(f"  LinkedIn 模板数: {len(manager.linkedin_templates)}")
    print(f"  邮件模板数: {len(manager.email_templates)}")


if __name__ == '__main__':
    main()
