#!/usr/bin/env python3
"""
Apex Speed Labs - 智能路由 APS (Automated Processing System)
优化版本 v2.1 - 修复 Ollama 0.18.2 兼容性

策略：
1. 简单任务 → 本地小模型 (llama3.2:1b) - 零成本
2. 中等任务 → 本地大模型 (qwen2.5:7b, llama3:8b, mistral:7b) - 零成本
3. 复杂任务 → 云 API (Gemini, Colab Pro) - 最优质量
4. 超低延迟任务 → Gemini API (最快)
5. 长上下文任务 → Colab Pro (100 compute unit)

成本优化目标：月成本 < $5
"""

import os
import json
import time
import hashlib
from enum import Enum
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/root/apex-automation/logs/aps.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('APS')

# === 任务复杂度定义 ===
class TaskComplexity(Enum):
    SIMPLE = "simple"      # 简单文本生成、分类、摘要
    MEDIUM = "medium"      # 标准对话、数据分析、逻辑推理
    COMPLEX = "complex"    # 深度推理、代码生成、复杂问题解决
    REALTIME = "realtime"  # 需要超低延迟响应
    LONG_CONTEXT = "long_context"  # 长上下文、大规模数据处理

# === 任务类型定义 ===
class TaskType(Enum):
    # 内容生成
    CONTENT_GENERATION = "content_generation"
    EMAIL_WRITING = "email_writing"
    SOCIAL_MEDIA = "social_media"

    # 数据分析
    DATA_ANALYSIS = "data_analysis"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"

    # 代码相关
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"

    # 商业智能
    LEAD_ANALYSIS = "lead_analysis"
    MARKET_RESEARCH = "market_research"
    SALES_SCRIPT = "sales_script"

    # 通用对话
    CHAT = "chat"
    QUESTION_ANSWERING = "question_answering"

    # 监控和自动化
    SYSTEM_MONITOR = "system_monitor"
    ERROR_ANALYSIS = "error_analysis"

# === 后端引擎配置 ===
@dataclass
class EngineConfig:
    name: str
    complexity: TaskComplexity
    priority: int  # 数字越小优先级越高
    max_tokens: int
    cost_per_1k_tokens: float = 0.0
    latency_ms: int = 0
    memory_mb: int = 0
    available: bool = True

# 本地模型配置
LOCAL_MODELS = {
    "llama3.2:1b": EngineConfig(
        name="llama3.2:1b",
        complexity=TaskComplexity.SIMPLE,
        priority=1,
        max_tokens=4096,
        cost_per_1k_tokens=0.0,
        latency_ms=50,
        memory_mb=800
    ),
    "qwen2.5:7b": EngineConfig(
        name="qwen2.5:7b",
        complexity=TaskComplexity.MEDIUM,
        priority=2,
        max_tokens=8192,
        cost_per_1k_tokens=0.0,
        latency_ms=120,
        memory_mb=1500
    ),
    "llama3:8b": EngineConfig(
        name="llama3:8b",
        complexity=TaskComplexity.MEDIUM,
        priority=2,
        max_tokens=8192,
        cost_per_1k_tokens=0.0,
        latency_ms=130,
        memory_mb=1600
    ),
    "mistral:7b": EngineConfig(
        name="mistral:7b",
        complexity=TaskComplexity.MEDIUM,
        priority=2,
        max_tokens=8192,
        cost_per_1k_tokens=0.0,
        latency_ms=110,
        memory_mb=1400
    ),
}

# 云 API 配置
CLOUD_APIS = {
    "gemini": {
        "name": "Google Gemini API",
        "complexity": [TaskComplexity.COMPLEX, TaskComplexity.REALTIME],
        "priority": 3,
        "max_tokens": 32768,
        "cost_per_1k_tokens": 0.0005,  # 估算成本
        "latency_ms": 80,
        "api_key": os.getenv("GEMINI_API_KEY", ""),
        "available": bool(os.getenv("GEMINI_API_KEY"))
    },
    "colab_pro": {
        "name": "Google Colab Pro",
        "complexity": [TaskComplexity.COMPLEX, TaskComplexity.LONG_CONTEXT],
        "priority": 4,
        "max_tokens": 100000,
        "cost_per_1k_tokens": 0.0,  # 已付费 100 compute unit
        "latency_ms": 500,
        "compute_units": 100,
        "available": True  # 已购买
    }
}

# === 任务复杂度路由规则 ===
TASK_ROUTING_RULES = {
    # 简单任务 → 本地 llama3.2:1b
    TaskComplexity.SIMPLE: {
        "engine": "llama3.2:1b",
        "max_tokens": 2048,
        "temperature": 0.7
    },

    # 中等任务 → 本地 qwen2.5:7b（中文优化）
    TaskComplexity.MEDIUM: {
        "engine": "qwen2.5:7b",
        "max_tokens": 4096,
        "temperature": 0.8
    },

    # 复杂任务 → Gemini API（速度 + 质量）
    TaskComplexity.COMPLEX: {
        "engine": "gemini",
        "max_tokens": 8192,
        "temperature": 0.9
    },

    # 超低延迟任务 → Gemini API（最快）
    TaskComplexity.REALTIME: {
        "engine": "gemini",
        "max_tokens": 2048,
        "temperature": 0.7
    },

    # 长上下文任务 → Colab Pro（100 compute unit）
    TaskComplexity.LONG_CONTEXT: {
        "engine": "colab_pro",
        "max_tokens": 100000,
        "temperature": 0.8
    }
}

# === 具体任务类型到复杂度的映射 ===
TASK_TYPE_TO_COMPLEXITY = {
    # 简单任务
    TaskType.CLASSIFICATION: TaskComplexity.SIMPLE,
    TaskType.SUMMARIZATION: TaskComplexity.SIMPLE,
    TaskType.SYSTEM_MONITOR: TaskComplexity.SIMPLE,

    # 中等任务
    TaskType.CONTENT_GENERATION: TaskComplexity.MEDIUM,
    TaskType.EMAIL_WRITING: TaskComplexity.MEDIUM,
    TaskType.SOCIAL_MEDIA: TaskComplexity.MEDIUM,
    TaskType.DATA_ANALYSIS: TaskComplexity.MEDIUM,
    TaskType.CHAT: TaskComplexity.MEDIUM,
    TaskType.QUESTION_ANSWERING: TaskComplexity.MEDIUM,
    TaskType.LEAD_ANALYSIS: TaskComplexity.MEDIUM,
    TaskType.MARKET_RESEARCH: TaskComplexity.MEDIUM,
    TaskType.SALES_SCRIPT: TaskComplexity.MEDIUM,

    # 复杂任务
    TaskType.CODE_GENERATION: TaskComplexity.COMPLEX,
    TaskType.CODE_REVIEW: TaskComplexity.COMPLEX,
    TaskType.DEBUGGING: TaskComplexity.COMPLEX,
    TaskType.ERROR_ANALYSIS: TaskComplexity.COMPLEX,
}


class IntelligentRouter:
    """智能路由器 - 根据任务复杂度选择最佳引擎"""

    def __init__(self):
        self.usage_stats = {
            "total_tasks": 0,
            "local_tasks": 0,
            "gemini_tasks": 0,
            "colab_tasks": 0,
            "total_cost": 0.0,
            "saved_cost": 0.0
        }
        self.load_stats()

    def load_stats(self):
        """加载使用统计"""
        try:
            with open('/root/apex-automation/data/aps_stats.json', 'r') as f:
                self.usage_stats = json.load(f)
        except FileNotFoundError:
            pass

    def save_stats(self):
        """保存使用统计"""
        os.makedirs('/root/apex-automation/data', exist_ok=True)
        with open('/root/apex-automation/data/aps_stats.json', 'w') as f:
            json.dump(self.usage_stats, f, indent=2)

    def determine_complexity(
        self,
        task_type: TaskType,
        prompt_length: int,
        expected_output_length: int,
        require_realtime: bool = False,
        require_long_context: bool = False
    ) -> TaskComplexity:
        """根据任务特征确定复杂度"""

        # 特殊需求优先
        if require_realtime:
            return TaskComplexity.REALTIME
        if require_long_context:
            return TaskComplexity.LONG_CONTEXT

        # 根据任务类型映射
        base_complexity = TASK_TYPE_TO_COMPLEXITY.get(task_type, TaskComplexity.MEDIUM)

        # 根据输入/输出长度调整
        total_tokens = prompt_length + expected_output_length
        if total_tokens > 16000:
            return TaskComplexity.LONG_CONTEXT
        elif total_tokens > 8000 and base_complexity == TaskComplexity.SIMPLE:
            return TaskComplexity.MEDIUM

        return base_complexity

    def select_engine(
        self,
        task_type: TaskType,
        prompt: str,
        max_output_length: int = 1000,
        require_realtime: bool = False,
        require_long_context: bool = False
    ) -> Dict[str, Any]:
        """选择最佳引擎"""

        # 计算复杂度
        complexity = self.determine_complexity(
            task_type,
            len(prompt),
            max_output_length,
            require_realtime,
            require_long_context
        )

        # 获取路由规则
        rule = TASK_ROUTING_RULES.get(complexity, TASK_ROUTING_RULES[TaskComplexity.MEDIUM])
        engine_name = rule["engine"]
        max_tokens = rule["max_tokens"]
        temperature = rule["temperature"]

        # 检查引擎可用性
        if engine_name in LOCAL_MODELS:
            config = LOCAL_MODELS[engine_name]
            if not config.available:
                # 降级到 Gemini API
                engine_name = "gemini"
                logger.warning(f"{config.name} 不可用，降级到 Gemini API")

        # 返回引擎配置
        result = {
            "engine_name": engine_name,
            "complexity": complexity.value,
            "max_tokens": min(max_tokens, max_output_length),
            "temperature": temperature,
            "cost_estimate": self.estimate_cost(engine_name, max_tokens),
            "latency_estimate": self.estimate_latency(engine_name)
        }

        return result

    def estimate_cost(self, engine_name: str, tokens: int) -> float:
        """估算成本"""
        if engine_name in LOCAL_MODELS:
            return 0.0
        elif engine_name in CLOUD_APIS:
            config = CLOUD_APIS[engine_name]
            return (tokens / 1000) * config["cost_per_1k_tokens"]
        return 0.0

    def estimate_latency(self, engine_name: str) -> int:
        """估算延迟（毫秒）"""
        if engine_name in LOCAL_MODELS:
            return LOCAL_MODELS[engine_name].latency_ms
        elif engine_name in CLOUD_APIS:
            return CLOUD_APIS[engine_name]["latency_ms"]
        return 500

    def record_usage(self, engine_name: str, tokens: int, cost: float):
        """记录使用情况"""
        self.usage_stats["total_tasks"] += 1

        if engine_name in LOCAL_MODELS:
            self.usage_stats["local_tasks"] += 1
            # 记录节省的成本（如果使用 Gemini API 需要的费用）
            saved_cost = (tokens / 1000) * 0.0005  # Gemini API 成本
            self.usage_stats["saved_cost"] += saved_cost
        elif engine_name == "gemini":
            self.usage_stats["gemini_tasks"] += 1
            self.usage_stats["total_cost"] += cost
        elif engine_name == "colab_pro":
            self.usage_stats["colab_tasks"] += 1

        self.save_stats()

    def get_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        cost_saving_percent = 0.0
        if self.usage_stats["total_tasks"] > 0:
            local_percent = (self.usage_stats["local_tasks"] / self.usage_stats["total_tasks"]) * 100
            cost_saving_percent = local_percent

        return {
            **self.usage_stats,
            "cost_saving_percent": cost_saving_percent,
            "local_usage_percent": (self.usage_stats["local_tasks"] / max(self.usage_stats["total_tasks"], 1)) * 100
        }


class APSClient:
    """APS 客户端 - 统一接口处理所有 AI 任务"""

    def __init__(self):
        self.router = IntelligentRouter()

    async def process(
        self,
        task_type: TaskType,
        prompt: str,
        max_output_length: int = 1000,
        require_realtime: bool = False,
        require_long_context: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """处理 AI 任务"""

        # 选择引擎
        engine_config = self.router.select_engine(
            task_type,
            prompt,
            max_output_length,
            require_realtime,
            require_long_context
        )

        engine_name = engine_config["engine_name"]

        logger.info(f"任务类型: {task_type.value} → 引擎: {engine_name} ({engine_config['complexity']})")

        # 执行任务
        start_time = time.time()

        if engine_name in LOCAL_MODELS:
            result = await self._execute_local(engine_name, prompt, engine_config)
        elif engine_name == "gemini":
            result = await self._execute_gemini(prompt, engine_config)
        elif engine_name == "colab_pro":
            result = await self._execute_colab(prompt, engine_config)
        else:
            raise ValueError(f"未知引擎: {engine_name}")

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # 记录使用情况
        tokens = len(result.get("content", "")) // 4  # 估算
        cost = engine_config["cost_estimate"]
        self.router.record_usage(engine_name, tokens, cost)

        # 返回结果
        result.update({
            "engine_used": engine_name,
            "latency_ms": latency_ms,
            "cost": cost
        })

        return result

    async def _execute_local(
        self,
        model_name: str,
        prompt: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行本地模型任务"""

        try:
            import subprocess

            # 使用 Ollama CLI（兼容 0.18.2 版本）
            cmd = [
                "ollama", "run", model_name,
                prompt
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(timeout=60)

            if process.returncode != 0:
                raise Exception(f"Ollama 执行失败: {stderr}")

            return {
                "content": stdout.strip(),
                "success": True
            }

        except Exception as e:
            logger.error(f"本地模型执行失败: {e}")
            # 降级到 Gemini API
            return await self._execute_gemini(prompt, config)

    async def _execute_gemini(
        self,
        prompt: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行 Gemini API 任务"""

        try:
            import httpx

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise Exception("未配置 GEMINI_API_KEY")

            # Gemini API 调用
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": config["temperature"],
                    "maxOutputTokens": config["max_tokens"]
                }
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                data = response.json()

            # 提取生成的文本
            content = data["candidates"][0]["content"]["parts"][0]["text"]

            return {
                "content": content,
                "success": True
            }

        except Exception as e:
            logger.error(f"Gemini API 执行失败: {e}")
            # 降级到 Colab Pro
            return await self._execute_colab(prompt, config)

    async def _execute_colab(
        self,
        prompt: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行 Colab Pro 任务"""

        # 这里需要根据实际的 Colab Pro API 实现进行调整
        # 目前先返回一个占位符
        logger.warning("Colab Pro 集成待完善，降级到本地模型")

        # 降级到本地 qwen2.5:7b
        return await self._execute_local("qwen2.5:7b", prompt, config)

    def get_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        return self.router.get_stats()


# === 便捷函数 ===

async def generate_content(task_type: TaskType, prompt: str, **kwargs) -> str:
    """便捷函数：生成内容"""
    client = APSClient()
    result = await client.process(task_type, prompt, **kwargs)
    return result["content"]


async def analyze_data(task_type: TaskType, data: str, **kwargs) -> str:
    """便捷函数：分析数据"""
    client = APSClient()
    result = await client.process(task_type, data, **kwargs)
    return result["content"]


async def chat(message: str, **kwargs) -> str:
    """便捷函数：对话"""
    client = APSClient()
    result = await client.process(TaskType.CHAT, message, **kwargs)
    return result["content"]


# === 主程序测试 ===

async def main():
    """主程序 - 测试 APS 系统"""

    client = APSClient()

    # 测试不同任务类型
    test_cases = [
        (TaskType.CLASSIFICATION, "判断这句话的情感：这个产品太棒了！"),
        (TaskType.EMAIL_WRITING, "写一封给客户的跟进邮件，客户对我们的 AI 写作助手感兴趣"),
        (TaskType.CODE_GENERATION, "用 Python 写一个快速排序算法"),
        (TaskType.MARKET_RESEARCH, "分析 AI 写作助手的市场竞争格局"),
    ]

    print("=" * 60)
    print("APS 智能路由系统测试")
    print("=" * 60)

    for task_type, prompt in test_cases:
        print(f"\n任务类型: {task_type.value}")
        print(f"提示词: {prompt[:50]}...")

        result = await client.process(task_type, prompt)

        print(f"使用引擎: {result['engine_used']}")
        print(f"复杂度: {result['complexity']}")
        print(f"延迟: {result['latency_ms']}ms")
        print(f"成本: ${result['cost']:.6f}")
        print(f"输出: {result['content'][:100]}...")

    # 显示统计信息
    stats = client.get_stats()
    print("\n" + "=" * 60)
    print("系统统计")
    print("=" * 60)
    print(f"总任务数: {stats['total_tasks']}")
    print(f"本地任务数: {stats['local_tasks']} ({stats['local_usage_percent']:.1f}%)")
    print(f"Gemini 任务数: {stats['gemini_tasks']}")
    print(f"Colab 任务数: {stats['colab_tasks']}")
    print(f"总成本: ${stats['total_cost']:.4f}")
    print(f"节省成本: ${stats['saved_cost']:.4f}")
    print(f"成本节省率: {stats['cost_saving_percent']:.1f}%")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
