# 小红书智能采集系统 - 阶段性设计文档

## 📋 当前系统状态评估

### ✅ **已完成的核心架构**

#### 1. 事件驱动状态机框架
- **位置**: [`core/state_machine.py`](core/state_machine.py)
- **实现**: 完整的事件驱动状态机架构
- **特点**:
  - 异步事件处理循环
  - 状态转换管理
  - 状态处理器注册机制
  - 简洁无过度设计

#### 2. 业务状态定义
- **位置**: [`core/states.py`](core/states.py)
- **状态枚举**:
  - `CHECKING_LOGIN` - 检查登录状态
  - `LOGIN_WAIT` - 等待登录
  - `LIST_STATE` - 列表浏览
  - `DETAIL_STATE` - 详情查看
  - `SEARCHING` - 搜索中
  - `SELECTING` - 选择笔记
  - `START/STOP/ERROR` - 系统状态

#### 3. 事件系统
- **位置**: [`core/event.py`](core/event.py), [`core/event_bus.py`](core/event_bus.py)
- **功能**: 基础事件发布订阅机制

#### 4. 数据模型
- **位置**: [`app/models/rednote.py`](app/models/rednote.py)
- **模型**:
  - `RedNotePreview` - 笔记预览
  - `RedNoteDetail` - 笔记详情
  - `RedNoteComment` - 评论
  - `RedNoteMedia` - 媒体信息

### ⚠️ **缺失的关键组件**

#### 1. 执行层模块
- ❌ **浏览器控制器** - 控制浏览器操作
- ❌ **API监听器** - 监听小红书API调用
- ❌ **DOM解析器** - 分析页面结构
- ❌ **数据收集器** - 统一数据处理流程

#### 2. 具体业务实现
- ❌ **登录状态处理器** - 处理登录逻辑
- ❌ **列表状态处理器** - 处理笔记列表和搜索
- ❌ **详情状态处理器** - 处理笔记详情收集
- ❌ **数据存储模块** - 持久化采集数据

#### 3. 智能功能
- ❌ **LLM Agent** - 智能分析和决策
- ❌ **用户交互界面** - CLI/GUI交互
- ❌ **错误处理机制** - 异常恢复策略

## 🎯 **下一阶段开发计划**

### 阶段一：基础设施层 (优先级：高)

#### 1.1 浏览器控制器
```python
# 位置: core/browser_controller.py
class BrowserController:
    async def start_browser(self)
    async def navigate_to(self, url: str)
    async def search_notes(self, keyword: str)
    async def click_element(self, selector: str)
    async def get_current_url(self) -> str
    async def wait_for_element(self, selector: str)
```

#### 1.2 API监听器
```python
# 位置: core/api_listener.py
class APIListener:
    async def start_listening(self, page)
    async def on_search_response(self, response)
    async def on_detail_response(self, response)
    async def on_comment_response(self, response)
    def get_captured_data(self) -> List[dict]
```

### 阶段二：业务逻辑层 (优先级：高)

#### 2.1 登录状态处理器
```python
# 位置: handlers/login_handler.py
class LoginStateHandler(BaseStateHandler):
    async def process_event(self, event, current_state):
        # 检查是否已登录
        # 监听登录页面元素
        # 处理登录完成事件
```

#### 2.2 列表状态处理器
```python
# 位置: handlers/list_handler.py
class ListStateHandler(BaseStateHandler):
    async def process_event(self, event, current_state):
        # 处理搜索结果
        # 解析笔记列表
        # 触发笔记选择
```

#### 2.3 详情状态处理器
```python
# 位置: handlers/detail_handler.py
class DetailStateHandler(BaseStateHandler):
    async def process_event(self, event, current_state):
        # 收集笔记详情
        # 解析评论数据
        # 返回列表状态
```

### 阶段三：数据层 (优先级：中)

#### 3.1 数据收集器
```python
# 位置: core/data_collector.py
class DataCollector:
    async def collect_search_data(self, api_response)
    async def collect_detail_data(self, api_response)
    async def collect_comment_data(self, api_response)
    async def save_data(self, data)
```

#### 3.2 数据存储
```python
# 位置: core/data_storage.py
class DataStorage:
    async def save_note_preview(self, note: RedNotePreview)
    async def save_note_detail(self, note: RedNoteDetail)
    async def save_comments(self, comments: List[RedNoteComment])
```

### 阶段四：智能功能 (优先级：低)

#### 4.1 LLM Agent
```python
# 位置: agents/smart_agent.py
class SmartAgent:
    async def analyze_notes(self, notes: List[RedNotePreview])
    async def select_best_note(self, notes: List[RedNotePreview])
    async def make_decision(self, context: dict)
```

#### 4.2 用户交互
```python
# 位置: ui/cli_interface.py
class CLIInterface:
    async def prompt_user_choice(self, options)
    async def show_progress(self, message)
    async def confirm_action(self, message)
```

## 🛠️ **技术实现路径**

### 路径A：渐进式开发 (推荐)
1. **先用现有脚本验证流程**
2. **逐步提取功能到状态机**
3. **补充缺失组件**
4. **添加智能功能**

### 路径B：重构式开发
1. **直接基于状态机开发**
2. **重写现有功能**
3. **集成所有组件**

## 📊 **开发优先级矩阵**

| 组件 | 重要度 | 紧急度 | 优先级 | 预估工作量 |
|------|--------|--------|--------|------------|
| 浏览器控制器 | 高 | 高 | 1 | 2-3天 |
| API监听器 | 高 | 高 | 2 | 2-3天 |
| 登录处理器 | 高 | 高 | 3 | 1-2天 |
| 列表处理器 | 高 | 中 | 4 | 2-3天 |
| 详情处理器 | 高 | 中 | 5 | 2-3天 |
| 数据收集器 | 中 | 中 | 6 | 1-2天 |
| 数据存储 | 中 | 低 | 7 | 1天 |
| LLM Agent | 低 | 低 | 8 | 3-5天 |
| 用户界面 | 低 | 低 | 9 | 2-3天 |

## 🎯 **近期目标 (未来2周)**

### Week 1: 基础设施
- [ ] 实现浏览器控制器
- [ ] 实现API监听器
- [ ] 创建基本的状态处理器框架

### Week 2: 业务逻辑
- [ ] 实现登录状态处理器
- [ ] 实现列表状态处理器
- [ ] 实现详情状态处理器
- [ ] 集成测试完整流程

## 📈 **成功指标**

### 技术指标
- [ ] 系统能够自动启动浏览器
- [ ] 能够检测登录状态
- [ ] 能够搜索并获取笔记列表
- [ ] 能够点击笔记并获取详情
- [ ] 能够自动循环采集流程

### 质量指标
- [ ] 代码覆盖率 > 80%
- [ ] 错误处理完善
- [ ] 性能满足要求（单个笔记采集 < 5秒）
- [ ] 内存使用稳定

## 🔄 **下一步行动**

### 立即行动
1. **确认开发优先级** - 与团队对齐开发路径
2. **分配开发任务** - 明确各组件负责人
3. **搭建开发环境** - 确保依赖和工具就位

### 技术决策点
1. **浏览器选择** - Playwright vs Selenium
2. **数据存储方案** - JSON文件 vs SQLite vs MongoDB
3. **LLM集成方案** - OpenAI API vs 本地模型
4. **部署方式** - 单机运行 vs 分布式

---

## 📝 **备注**

- 当前状态机架构已经为后续开发奠定了良好基础
- 重点关注执行层组件的实现，将抽象框架转化为实际功能
- 建议采用渐进式开发路径，降低风险并快速验证可行性
- 保持简洁设计原则，避免在基础功能稳定前添加过多复杂功能