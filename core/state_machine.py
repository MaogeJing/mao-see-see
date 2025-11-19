"""
事件驱动的业务状态机
基于小红书笔记采集需求设计的完整状态机实现
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Optional
from .state_types import BusinessState, Event
from .event_bus import EventBus


class BaseStateHandler(ABC):
    """状态处理器基类"""

    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus

    @abstractmethod
    async def process_event(self, event: Event, current_state: BusinessState) -> Optional[BusinessState]:
        """处理事件，返回新状态或None"""
        pass

    async def on_enter_state(self, from_state: Optional[BusinessState] = None):
        """进入状态时的回调"""
        pass

    async def on_exit_state(self, to_state: Optional[BusinessState] = None):
        """退出状态时的回调"""
        pass


class EventDrivenStateMachine:
    """事件驱动的核心状态机"""

    def __init__(self, initial_state: BusinessState = BusinessState.CHECKING_LOGIN, event_bus: Optional[EventBus] = None):
        self.current_state = initial_state
        self.previous_state = None
        self.event_bus = event_bus or EventBus("state_machine")
        self.event_queue = asyncio.Queue()
        self.running = False
        self.handlers: Dict[BusinessState, BaseStateHandler] = {}

    def register_handler(self, state: BusinessState, handler: BaseStateHandler):
        """注册状态处理器"""
        self.handlers[state] = handler
        if not handler.event_bus:
            handler.event_bus = self.event_bus

    async def transition_to(self, new_state: BusinessState):
        """转换到新状态"""
        if new_state == self.current_state:
            return

        if new_state not in self.handlers:
            print(f"状态 {new_state.display_name} 没有处理器")
            return

        old_state = self.current_state
        self.previous_state = old_state

        # 执行状态退出回调
        if old_state in self.handlers:
            try:
                await self.handlers[old_state].on_exit_state(new_state)
            except Exception as e:
                print(f"状态退出回调失败: {e}")

        # 更新状态
        self.current_state = new_state

        # 执行状态进入回调
        try:
            await self.handlers[new_state].on_enter_state(old_state)
        except Exception as e:
            print(f"状态进入回调失败: {e}")

    async def process_event(self, event: Event):
        """处理事件"""
        handler = self.handlers.get(self.current_state)

        if not handler:
            print(f"状态 {self.current_state.display_name} 没有处理器")
            return

        try:
            # 处理事件
            new_state = await handler.process_event(event, self.current_state)

            # 状态转换
            if new_state and new_state != self.current_state:
                await self.transition_to(new_state)

        except Exception as e:
            print(f"处理事件 {event.type} 时发生错误: {e}")

    async def emit_event(self, event_type: str, data: Optional[Dict] = None):
        """发送事件到队列"""
        event = Event(type=event_type, data=data or {}, source="state_machine")
        await self.event_queue.put(event)

    async def run(self):
        """启动事件驱动状态机"""
        if self.running:
            return

        self.running = True
        print("事件驱动状态机已启动")

        # 主事件处理循环
        while self.running:
            try:
                event = await self.event_queue.get()
                await self.process_event(event)
            except Exception as e:
                print(f"事件循环错误: {e}")
                await asyncio.sleep(0.1)

    async def start(self):
        """启动状态机（兼容性方法）"""
        await self.run()

    async def stop(self):
        """停止状态机"""
        if not self.running:
            return

        self.running = False
        print("事件驱动状态机已停止")


# 为了向后兼容，保留原有的StateMachine类
class StateMachine(EventDrivenStateMachine):
    """向后兼容的状态机类"""
    pass


__all__ = [
    'BaseStateHandler',
    'EventDrivenStateMachine',
    'StateMachine',  # 向后兼容
]