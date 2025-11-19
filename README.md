# 猫看看 (MaoSeeSee)

一个简单的事件驱动状态机框架

## 核心架构

### 事件系统
- **Event**: 使用pydantic的事件类，包含type、data、source、timestamp
- **EventType**: 定义核心事件类型（只有5个基础事件）
- **EventFactory**: 简单的事件创建工具

### 事件总线
- **EventBus**: 异步发布订阅系统
- 支持通配符订阅 "*"
- 自动并发处理事件

### 状态机
- **BaseStateHandler**: 状态处理器抽象基类
- **StateMachine**: 简单的事件驱动状态机
- 支持状态转换和事件处理

## 文件结构

```
core/
├── event.py         # 事件定义（简化版）
├── event_bus.py     # 事件总线（简化版）
├── state_machine.py # 状态机（简化版）
└── __init__.py      # 导出接口

examples/
└── simple_test.py   # 基础测试
```

## 快速开始

```python
from core import create_system, BaseStateHandler, EventType

class MyHandler(BaseStateHandler):
    async def process_event(self, event, current_state):
        if event.type == EventType.USER_INPUT:
            return "NEXT_STATE"
        return None

async def main():
    event_bus, state_machine = await create_system()
    state_machine.register_handler("START", MyHandler("START", event_bus))
    await state_machine.start()

    # 发送事件
    await state_machine.emit_event(EventType.USER_INPUT, {"content": "test"})
```

## 设计原则

1. **简单**: 移除过度设计，保持核心功能
2. **清晰**: 每个模块职责单一，易于理解
3. **可扩展**: 按需添加功能，不过度抽象
4. **实用**: 专注解决实际问题

## 当前状态

✅ 核心事件系统（简化版）
✅ 简单的状态机
🏗️ 基础状态处理器（开发中）
🏗️ 浏览器控制模块（开发中）