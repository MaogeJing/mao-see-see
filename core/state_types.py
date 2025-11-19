"""
业务状态和事件类型定义
小红书笔记采集系统的所有状态和对应事件类型
"""
import time
from enum import Enum
from typing import Dict, Set, Any, Optional
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
    """业务事件类型 - 与业务状态对应"""

    # 登录相关事件
    LOGIN_CHECK_STARTED = "login_check_started"
    LOGIN_REQUIRED = "login_required"
    LOGIN_COMPLETED = "login_completed"
    LOGIN_FAILED = "login_failed"

    # 搜索相关事件
    SEARCH_STARTED = "search_started"
    SEARCH_COMPLETED = "search_completed"
    SEARCH_FAILED = "search_failed"
    SEARCH_INPUT_RECEIVED = "search_input_received"

    # 列表相关事件
    NOTE_LIST_RECEIVED = "note_list_received"
    NOTE_SELECTED = "note_selected"
    NOTE_CLICKED = "note_clicked"
    LIST_SCROLLED = "list_scrolled"

    # 详情相关事件
    DETAIL_LOADED = "detail_loaded"
    DETAIL_DATA_RECEIVED = "detail_data_received"
    COMMENTS_RECEIVED = "comments_received"
    BACK_TO_LIST = "back_to_list"

    # 系统事件
    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"
    ERROR_OCCURRED = "error_occurred"
    USER_INTERRUPT = "user_interrupt"


class Event(BaseModel):
    """业务事件"""
    type: str
    data: Dict[str, Any] = {}
    source: Optional[str] = None
    timestamp: float = 0.0

    def __init__(self, **data):
        if 'timestamp' not in data or data['timestamp'] == 0.0:
            data['timestamp'] = time.time()
        super().__init__(**data)

    def get(self, key: str, default: Any = None) -> Any:
        """获取数据"""
        return self.data.get(key, default)


# 事件工厂方法
class EventFactory:
    """事件工厂 - 创建标准业务事件"""

    @staticmethod
    def login_check_started():
        """开始检查登录状态"""
        return Event(type=EventType.LOGIN_CHECK_STARTED, source="login_handler")

    @staticmethod
    def login_required():
        """需要登录"""
        return Event(type=EventType.LOGIN_REQUIRED, source="login_handler")

    @staticmethod
    def login_completed():
        """登录完成"""
        return Event(type=EventType.LOGIN_COMPLETED, source="login_handler")

    @staticmethod
    def search_started(keyword: str):
        """开始搜索"""
        return Event(
            type=EventType.SEARCH_STARTED,
            data={"keyword": keyword},
            source="list_handler"
        )

    @staticmethod
    def search_completed(notes: list):
        """搜索完成"""
        return Event(
            type=EventType.SEARCH_COMPLETED,
            data={"notes": notes, "count": len(notes)},
            source="list_handler"
        )

    @staticmethod
    def note_selected(note_id: str, note_data: dict):
        """选择笔记"""
        return Event(
            type=EventType.NOTE_SELECTED,
            data={"note_id": note_id, "note_data": note_data},
            source="list_handler"
        )

    @staticmethod
    def detail_loaded(note_id: str):
        """详情页面加载完成"""
        return Event(
            type=EventType.DETAIL_LOADED,
            data={"note_id": note_id},
            source="detail_handler"
        )

    @staticmethod
    def detail_data_received(detail_data: dict):
        """详情数据接收完成"""
        return Event(
            type=EventType.DETAIL_DATA_RECEIVED,
            data=detail_data,
            source="detail_handler"
        )

    @staticmethod
    def back_to_list():
        """返回列表"""
        return Event(type=EventType.BACK_TO_LIST, source="detail_handler")

    @staticmethod
    def error(message: str, error_type: str = "general"):
        """错误事件"""
        return Event(
            type=EventType.ERROR_OCCURRED,
            data={"message": message, "error_type": error_type},
            source="system"
        )


__all__ = [
    'BusinessState',
    'EventType',
    'Event',
    'EventFactory',
]