"""
业务状态和事件类型定义
小红书笔记采集系统的所有状态和对应事件类型
"""
import time
from enum import Enum
from typing import Dict, Set, Any
from pydantic import BaseModel


class BusinessState(Enum):
    """业务状态枚举"""

    # 登录相关状态
    CHECKING_LOGIN = (1, '🔍 检查登录', '系统启动时检查用户是否已登录小红书', 'checking')
    LOGIN_WAIT = (2, '🔐 登录等待', '检测到未登录，等待用户扫码完成登录', 'waiting')

    # 核心业务状态
    LIST_STATE = (3, '📋 列表浏览', '用户在笔记列表页面，可以浏览、搜索、选择笔记', 'listing')
    DETAIL_STATE = (4, '📄 详情查看', '笔记详情页面已展开，用户可以查看完整内容和评论', 'detailing')

    # 过渡状态
    SEARCHING = (5, '🔍 搜索中', '正在执行搜索操作，等待搜索结果', 'searching')
    SELECTING = (6, '👆 选择笔记', '用户在列表中选择特定笔记，准备点击查看详情', 'selecting')

    # 系统状态
    START = (0, '🚀 系统启动', '系统正在初始化和启动', 'starting')
    STOP = (-1, '⏹️ 系统停止', '系统正在停止和清理资源', 'stopped')
    ERROR = (-2, '❌ 错误状态', '系统遇到错误，正在处理或等待恢复', 'error')

    
    def __init__(self, state_code: int, display_name: str, description: str, short_name: str):
        self.state_code = state_code
        self.display_name = display_name
        self.description = description
        self.short_name = short_name

    def __new__(cls, *args):
        obj = object.__new__(cls)
        obj._value_ = args[0]  # 使用 state_code 作为枚举值
        return obj

    def __str__(self):
        return self.display_name

  
    def can_transition_to(self, target_state: 'BusinessState') -> bool:
        """检查是否可以转换到目标状态"""
        # 定义状态转换规则
        valid_transitions: Dict[BusinessState, Set[BusinessState]] = {
            # 系统启动
            BusinessState.START: {
                BusinessState.CHECKING_LOGIN  # SYSTEM_INITIALIZED: 系统初始化完成
            },

            # 检查登录状态
            BusinessState.CHECKING_LOGIN: {
                BusinessState.LOGIN_WAIT,      # LOGIN_REQUIRED: 需要用户登录
                BusinessState.LIST_STATE       # ALREADY_LOGGED_IN: 用户已经登录
            },

            # 登录等待
            BusinessState.LOGIN_WAIT: {
                BusinessState.LIST_STATE,      # LOGIN_SUCCESS: 登录成功
                BusinessState.CHECKING_LOGIN   # LOGIN_RETRY: 重新检查登录状态
            },

            # 列表状态
            BusinessState.LIST_STATE: {
                BusinessState.SEARCHING,       # USER_SEARCH: 用户发起搜索
                BusinessState.SELECTING,       # USER_SELECT_NOTE: 用户选择笔记
                BusinessState.CHECKING_LOGIN,  # LOGIN_EXPIRED: 登录状态过期
                BusinessState.STOP             # USER_STOP: 用户停止操作
            },

            # 搜索中
            BusinessState.SEARCHING: {
                BusinessState.LIST_STATE       # SEARCH_COMPLETED: 搜索完成
            },

            # 选择笔记
            BusinessState.SELECTING: {
                BusinessState.DETAIL_STATE,    # NOTE_CLICKED: 成功点击笔记
                BusinessState.LIST_STATE       # SELECTION_CANCELLED: 取消选择
            },

            # 详情状态
            BusinessState.DETAIL_STATE: {
                BusinessState.LIST_STATE,          # USER_BACK: 用户返回列表
                BusinessState.CHECKING_LOGIN       # LOGIN_EXPIRED: 登录状态过期
            },

            # 错误状态
            BusinessState.ERROR: {
                BusinessState.CHECKING_LOGIN,  # ERROR_RECOVERED: 错误已恢复
                BusinessState.STOP             # ERROR_FATAL: 致命错误，停止系统
            },

            # 系统停止（终止状态，无转换）
            BusinessState.STOP: set(),
        }

        return target_state in valid_transitions.get(self, set())


class EventType:
    """与状态转换对应的业务事件类型"""

    # 系统初始化事件
    SYSTEM_INITIALIZED = "system_initialized"  # 触发: START → CHECKING_LOGIN

    # 登录事件
    LOGIN_REQUIRED = "login_required"      # 触发: CHECKING_LOGIN → LOGIN_WAIT
    LOGIN_SUCCESS = "login_success"        # 触发: CHECKING_LOGIN/LONGIN_WAIT → LIST_STATE

    # 搜索事件
    SEARCH = "search"                      # 触发: LIST_STATE → SEARCHING
    SEARCH_RESULT = "search_result"        # 触发: SEARCHING → LIST_STATE

    # 笔记选择事件
    NOTE_SELECT = "note_select"            # 触发: LIST_STATE → SELECTING
    NOTE_CLICKED = "note_clicked"          # 触发: SELECTING → DETAIL_STATE
    CANCEL_SELECT = "cancel_select"        # 触发: SELECTING → LIST_STATE

    # 详情采集事件
    DETAIL_LOADED = "detail_loaded"        # 详情页面加载完成
    BACK_TO_LIST = "back_to_list"          # 触发: DETAIL_STATE → LIST_STATE

    # 系统
    LOGIN_EXPIRED = "login_expired"        # 触发: LIST_STATE/DETAIL_STATE → CHECKING_LOGIN
    ERROR = "error"                        # 触发: 任意状态 → ERROR
    STOP = "stop"                          # 触发: 任意状态 → STOP


class Event(BaseModel):
    """简化的业务事件"""
    type: str
    data: Dict[str, Any] = {}

    def __init__(self, **data):
        if 'timestamp' not in data.get('data', {}):
            data.setdefault('data', {})['timestamp'] = time.time()
        super().__init__(**data)


# 事件工厂方法
class EventFactory:
    """与状态转换对应的事件工厂"""

    @staticmethod
    def system_initialized():
        """系统初始化完成 - 触发: START → CHECKING_LOGIN"""
        return Event(type=EventType.SYSTEM_INITIALIZED)

    @staticmethod
    def login_required():
        """需要登录 - 触发: CHECKING_LOGIN → LOGIN_WAIT"""
        return Event(type=EventType.LOGIN_REQUIRED)

    @staticmethod
    def login_success():
        """登录成功 - 触发: CHECKING_LOGIN/LOGIN_WAIT → LIST_STATE"""
        return Event(type=EventType.LOGIN_SUCCESS)

    @staticmethod
    def search(keyword: str):
        """开始搜索 - 触发: LIST_STATE → SEARCHING"""
        return Event(type=EventType.SEARCH, data={"keyword": keyword})

    @staticmethod
    def search_result(notes: list):
        """搜索结果 - 触发: SEARCHING → LIST_STATE"""
        return Event(type=EventType.SEARCH_RESULT, data={"notes": notes})

    @staticmethod
    def note_select(note_id: str):
        """选择笔记 - 触发: LIST_STATE → SELECTING"""
        return Event(type=EventType.NOTE_SELECT, data={"note_id": note_id})

    @staticmethod
    def note_clicked(note_id: str):
        """点击笔记 - 触发: SELECTING → DETAIL_STATE"""
        return Event(type=EventType.NOTE_CLICKED, data={"note_id": note_id})

    @staticmethod
    def cancel_select():
        """取消选择 - 触发: SELECTING → LIST_STATE"""
        return Event(type=EventType.CANCEL_SELECT)

    @staticmethod
    def detail_loaded(note_id: str):
        """详情加载完成"""
        return Event(type=EventType.DETAIL_LOADED, data={"note_id": note_id})

    @staticmethod
    def back_to_list():
        """返回列表 - 触发: DETAIL_STATE → LIST_STATE"""
        return Event(type=EventType.BACK_TO_LIST)

    @staticmethod
    def login_expired():
        """登录过期 - 触发: LIST_STATE/DETAIL_STATE → CHECKING_LOGIN"""
        return Event(type=EventType.LOGIN_EXPIRED)

    @staticmethod
    def error(message: str):
        """错误事件 - 触发: 任意状态 → ERROR"""
        return Event(type=EventType.ERROR, data={"message": message})

    @staticmethod
    def stop():
        """停止事件 - 触发: 任意状态 → STOP"""
        return Event(type=EventType.STOP)


__all__ = [
    'BusinessState',
    'EventType',
    'Event',
    'EventFactory',
]