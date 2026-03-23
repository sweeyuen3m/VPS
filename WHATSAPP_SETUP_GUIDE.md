# WhatsApp API 配置指南

## 概述

Apex Speed Labs WhatsApp 自动化模块需要配置 WhatsApp Business API 凭证才能运行。

## 配置步骤

### 1. 创建 WhatsApp Business App

1. 访问 [Facebook Developers](https://developers.facebook.com/)
2. 创建新应用
3. 选择 **Business** 类型
4. 添加 **WhatsApp** 产品

### 2. 获取 Phone Number ID

1. 在 WhatsApp 产品中，点击 **Get Started**
2. 选择或添加一个电话号码
3. 选择 **Send and receive messages** → **Send and receive WhatsApp business messages with the Cloud API**
4. 复制 **Phone Number ID**

### 3. 获取 Access Token

1. 在 WhatsApp 产品页面
2. 找到 **Permanent Access Token** 部分
3. 点击 **Generate**
4. 复制生成的 Access Token

### 4. 配置环境变量

在 VPS 上运行以下命令:

```bash
# SSH 登录 VPS
ssh root@167.71.120.132

# 编辑环境变量
nano /root/.bashrc

# 添加以下内容:
export WHATSAPP_PHONE_NUMBER_ID='YOUR_PHONE_NUMBER_ID'
export WHATSAPP_ACCESS_TOKEN='YOUR_ACCESS_TOKEN'
export WHATSAPP_BUSINESS_ACCOUNT_ID='YOUR_BUSINESS_ACCOUNT_ID'

# 保存并应用
source /root/.bashrc

# 验证配置
echo $WHATSAPP_ACCESS_TOKEN
```

### 5. 测试连接

```bash
cd /root/apex-automation
python3 whatsapp_automation.py
```

如果看到 ✅ WhatsApp API 连接成功，说明配置正确。

## 消息模板

WhatsApp Business API 要求使用预审核的消息模板。以下是我们已配置的模板:

### welcome_message
```
Hi {{1}}, welcome to Apex Speed Labs! 🚀

We help real estate agents generate high-quality leads using AI.

Check out our service: https://leads-improvement.sweeyuen3.workers.dev
```

### free_leads_offer
```
Hi {{1}},

We have 5 free leads for you to try! 🎁

These leads are:
✅ High quality (80% accuracy)
✅ Ready to contact
✅ No obligation

Want to try them out? Reply "YES" and I'll send them over!
```

### follow_up_reminder
```
Hi {{1}},

Just checking in - how are the leads working for you? 😊

If you need more or have questions, just let me know!

Steven | Apex Speed Labs
+65 9298 4102
```

## 使用示例

### 发送自定义消息
```python
from whatsapp_automation import WhatsAppAutomation

whatsapp = WhatsAppAutomation()
result = whatsapp.send_message(
    '+6592984102',
    'Hello! This is a test message. 🚀'
)
```

### 发送模板消息
```python
result = whatsapp.send_template_message(
    '+6592984102',
    'free_leads_offer',
    ['Steven']  # 参数: {{1}} = 'Steven'
)
```

### 批量发送
```python
phones = ['+6592984102', '+6591234567', '+6599876543']
results = whatsapp.send_bulk_messages(phones, 'Bulk message test! 🚀')
```

## 注意事项

1. **消息模板审核**: 新模板需要 Facebook 审核，通常 24-48 小时
2. **发送限制**: 免费版本有 1000 条/天的限制
3. **24小时窗口**: 只能在用户最后一条消息的 24 小时内发送主动消息
4. **格式化**: 手机号必须包含国家代码 (如 +65)
5. **延迟发送**: 批量发送时建议添加 10-30 秒延迟，避免被标记为垃圾消息

## 故障排查

### 问题: API 返回 401 Unauthorized
**解决方案**: 检查 Access Token 是否正确，是否过期

### 问题: 模板不存在
**解决方案**: 检查模板名称是否正确，是否已通过审核

### 问题: 消息发送失败 (rate limit)
**解决方案**: 减少发送频率，增加延迟时间

### 问题: 24小时窗口错误
**解决方案**: 只能在用户主动发起对话后的 24 小时内发送消息

## 下一步

配置完成后，可以在以下脚本中使用 WhatsApp 自动化:

- `linkedin_auto_message.py` - LinkedIn 私信后发送 WhatsApp 消息
- `automated_followup_system.py` - 跟进系统通过 WhatsApp 发送消息
- `email_sender.py` - 邮件后通过 WhatsApp 提醒

## 联系方式

如有问题，请联系:
- **Steven Wong**: sweeyuen3@apexspeedlabs.com
- **Phone**: +65 9298 4102
