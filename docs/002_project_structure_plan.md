# 项目结构规划

## 📁 目录结构

```
mao-see-see/
├── README.md                    # 项目说明
├── pyproject.toml              # uv项目配置
├── docs/                       # 文档和发现记录
│   ├── 001_drissionpage_persistence_discovery.md
│   ├── 002_project_structure_plan.md
│   └── ...
├── app/                        # 核心应用模块
│   ├── __init__.py
│   ├── core/                   # 核心功能
│   │   ├── __init__.py
│   │   ├── browser.py          # 浏览器管理
│   │   ├── monitor.py          # 网络监听
│   │   └── session.py          # 会话管理
│   ├── actions/                # 用户动作模拟
│   │   ├── __init__.py
│   │   ├── search.py           # 搜索动作
│   │   ├── navigation.py       # 导航动作
│   │   └── interaction.py      # 交互动作
│   ├── data/                   # 数据处理
│   │   ├── __init__.py
│   │   ├── storage.py          # 数据存储
│   │   ├── parser.py           # 数据解析
│   │   └── models.py           # 数据模型
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── logger.py           # 日志工具
│       └── helpers.py          # 辅助函数
├── scripts/                    # 临时测试脚本
│   ├── test_browser_persistence.py
│   ├── test_note_list.py
│   ├── test_note_detail.py
│   ├── test_network_monitoring.py
│   └── demo_workflow.py
├── data/                       # 数据存储
│   ├── xiaohongshu_data/
│   │   ├── chrome_profile_9933/
│   │   ├── monitor.db
│   │   └── sessions.json
│   └── exports/
├── tests/                      # 测试文件
│   ├── test_browser.py
│   ├── test_actions.py
│   └── test_data.py
└── config/                     # 配置文件
    ├── settings.py
    └── keywords.json
```

## 🎯 模块分工

### app/core/ - 核心功能
- **browser.py**: 基于持久化发现的浏览器管理
- **monitor.py**: 网络请求监听和捕获
- **session.py**: 会话状态管理

### app/actions/ - 用户动作模拟
- **search.py**: 搜索功能实现
- **navigation.py**: 页面导航和路由
- **interaction.py**: 点击、滚动等交互

### app/data/ - 数据处理
- **storage.py**: SQLite数据库操作
- **parser.py**: 解析网络请求数据
- **models.py**: 数据模型定义

### scripts/ - 测试脚本
- 各种功能的独立测试脚本
- 演示完整工作流程
- 调试和验证功能

## 🔄 开发流程

### 第一阶段：核心动作测试
1. 浏览器持久化测试
2. 笔记列表抓取测试
3. 笔记详情查看测试
4. 网络请求监听测试

### 第二阶段：模块化开发
1. 将测试成功的功能模块化
2. 整合到 app/ 目录
3. 建立统一的接口和配置

### 第三阶段：功能集成
1. LLM 集成（LangChain）
2. 关键词管理
3. 数据持久化
4. 用户界面

## 📋 当前开发重点

### 即将测试的核心动作
1. **笔记列表抓取**
   - 搜索结果页面分析
   - 笔记元素识别
   - 数据提取

2. **笔记详情交互**
   - 点击进入详情页
   - 退出详情页
   - 重新进入

3. **网络监听**
   - 笔记列表接口
   - 笔记详情接口
   - 用户行为数据

4. **真实用户模拟**
   - 随机延迟
   - 鼠标移动轨迹
   - 滚动行为

## 🛠️ 技术栈

### 核心依赖
- `DrissionPage`: 浏览器自动化
- `sqlite3`: 数据存储
- `langchain`: LLM集成
- `python-dotenv`: 环境配置

### 开发工具
- `uv`: Python包管理
- `black`: 代码格式化
- `pytest`: 单元测试

## 🎨 代码规范

### 命名约定
- 类名：PascalCase
- 函数名：snake_case
- 常量：UPPER_SNAKE_CASE
- 文件名：snake_case

### 文档规范
- 每个模块都要有 docstring
- 重要函数要有参数说明
- 复杂逻辑要有注释

### 错误处理
- 使用 try-except 包装关键操作
- 提供有意义的错误信息
- 记录详细的日志