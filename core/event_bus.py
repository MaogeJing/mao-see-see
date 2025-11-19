"""
事件总线 - 纯订阅管理器
负责事件订阅和分发，不处理队列
"""
import asyncio
from typing import Dict, List, Callable, Optional
from .state_types import Event


class EventBus:
    """事件订阅管理器"""

    def __init__(self, name: str = "default"):
        self.name = name
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        """订阅事件"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable):
        """取消订阅"""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

    async def publish(self, event: Event):
        """立即分发事件给订阅者"""
        await self._handle_event(event)

    async def _handle_event(self, event: Event):
        """处理单个事件"""
        handlers = self._handlers.get(event.type, [])
        wildcard_handlers = self._handlers.get("*", [])

        all_handlers = handlers + wildcard_handlers

        if not all_handlers:
            return

        # 并发执行所有处理器
        tasks = []
        for handler in all_handlers:
            task = asyncio.create_task(self._safe_call(handler, event))
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_call(self, handler: Callable, event: Event):
        """安全调用处理器"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            print(f"处理器 {handler.__name__} 错误: {e}")


__all__ = ['EventBus']