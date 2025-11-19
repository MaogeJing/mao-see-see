"""
核心模块 - 简化版本
"""
from .state_types import BusinessState, EventType, Event, EventFactory
from .event_bus import EventBus
from .state_machine import BaseStateHandler, StateMachine

__all__ = ['BusinessState', 'EventType', 'Event', 'EventFactory', 'EventBus', 'BaseStateHandler', 'StateMachine']


async def create_system(name: str = "default"):
    """创建简单的事件系统"""
    event_bus = EventBus(name)
    state_machine = StateMachine(event_bus=event_bus)
    return event_bus, state_machine