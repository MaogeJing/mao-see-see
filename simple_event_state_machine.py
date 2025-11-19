"""
最基础的事件驱动状态机实现
渐进式开发 - 第一步：建立核心框架
"""
import asyncio
import time
from typing import Dict, Any, Optional, Callable
from enum import Enum


class EventType:
    """基础事件类型定义"""
    # 系统启动事件
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"

    # 用户交互事件
    USER_INPUT = "user_input"

    # 状态转换事件
    STATE_TRANSITION = "state_transition"

    # 测试事件
    TEST_EVENT = "test_event"


class Event:
    """最基础的事件类"""
    def __init__(self, event_type: str, data: Dict[str, Any] = None):
        self.type = event_type
        self.data = data or {}
        self.timestamp = time.time()

    def __str__(self):
        return f"Event(type={self.type}, data={self.data}, timestamp={self.timestamp})"


class SimpleEventBus:
    """最简单的事件总线实现"""
    def __init__(self):
        self.subscribers: Dict[str, list] = {}
        self.event_queue = asyncio.Queue()

    def subscribe(self, event_type: str, handler: Callable):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        print(f"✓ 订阅事件: {event_type}")

    async def publish(self, event: Event):
        """发布事件"""
        print(f"📤 发布事件: {event}")
        await self.event_queue.put(event)

    async def process_events(self):
        """处理事件队列"""
        while True:
            try:
                event = await self.event_queue.get()
                await self._handle_event(event)
            except Exception as e:
                print(f"❌ 事件处理错误: {e}")

    async def _handle_event(self, event: Event):
        """处理单个事件"""
        handlers = self.subscribers.get(event.type, [])
        if handlers:
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    print(f"❌ 事件处理器错误: {e}")
        else:
            print(f"⚠️  没有处理器处理事件: {event.type}")


class BaseStateHandler:
    """基础状态处理器"""
    def __init__(self, state_name: str):
        self.state_name = state_name

    async def process_event(self, event: Event, current_state: str) -> Optional[str]:
        """处理事件，返回新的状态名（如果需要状态转换）"""
        print(f"🔄 {self.state_name} 处理事件: {event.type}")

        # 默认处理逻辑
        if event.type == EventType.TEST_EVENT:
            print(f"📝 {self.state_name}: 收到测试事件")
            return current_state

        return current_state


class SimpleEventDrivenStateMachine:
    """最简单的事件驱动状态机"""
    def __init__(self):
        self.current_state = "INIT"
        self.running = False
        self.event_bus = SimpleEventBus()
        self.state_handlers: Dict[str, BaseStateHandler] = {}
        self.last_activity = time.time()

        # 注册基础状态处理器
        self._register_state_handlers()

    def _register_state_handlers(self):
        """注册状态处理器"""
        # 初始状态处理器
        self.state_handlers["INIT"] = BaseStateHandler("INIT")

        # 订阅系统事件
        self.event_bus.subscribe(EventType.SYSTEM_START, self._handle_system_start)
        self.event_bus.subscribe(EventType.USER_INPUT, self._handle_user_input)

    async def _handle_system_start(self, event: Event):
        """处理系统启动事件"""
        print(f"🚀 系统启动，当前状态: {self.current_state}")
        self.running = True

    async def _handle_user_input(self, event: Event):
        """处理用户输入事件"""
        print(f"👤 用户输入: {event.data}")

    async def emit_event(self, event_type: str, data: Dict[str, Any] = None):
        """发送事件"""
        event = Event(event_type, data)
        await self.event_bus.publish(event)

    async def run(self):
        """运行状态机"""
        print("🎯 启动事件驱动状态机...")

        # 启动事件处理任务
        event_task = asyncio.create_task(self.event_bus.process_events())

        try:
            # 发送系统启动事件
            await self.emit_event(EventType.SYSTEM_START)

            # 主循环 - 简单的健康检查
            while self.running:
                await asyncio.sleep(1.0)

                # 简单的心跳检查
                if time.time() - self.last_activity > 10:
                    print(f"💓 心跳检查 - 当前状态: {self.current_state}")
                    self.last_activity = time.time()

        except KeyboardInterrupt:
            print("\n🛑 收到停止信号")
        finally:
            self.running = False
            event_task.cancel()
            print("⏹️  状态机已停止")


# 测试函数
async def test_basic_state_machine():
    """测试基础状态机"""
    print("🧪 开始测试基础事件驱动状态机...")

    # 创建状态机
    state_machine = SimpleEventDrivenStateMachine()

    # 在后台运行状态机
    machine_task = asyncio.create_task(state_machine.run())

    # 等待系统启动
    await asyncio.sleep(1)

    # 发送测试事件
    print("\n📋 发送测试事件...")
    await state_machine.emit_event(EventType.TEST_EVENT, {"message": "Hello World!"})

    # 发送用户输入事件
    print("\n👤 发送用户输入事件...")
    await state_machine.emit_event(EventType.USER_INPUT, {"input": "测试输入"})

    # 运行几秒钟
    await asyncio.sleep(3)

    # 停止状态机
    print("\n🛑 停止测试...")
    state_machine.running = False
    await machine_task

    print("✅ 测试完成!")


if __name__ == "__main__":
    print("🎬 启动基础事件驱动状态机测试")
    asyncio.run(test_basic_state_machine())