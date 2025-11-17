# 核心总结

## 项目结构
```
app/
└── models/
    └── rednote.py          # RedNotePreview数据模型
scripts/
└── test_note_list.py      # 笔记列表抓取脚本
```

## 核心模型 (app/models/rednote.py)

### RedNotePreview
小红书笔记预览数据，只包含首页列表API返回的字段：
- `note_id`: 笔记ID
- `title`: 标题
- `media_list`: 多媒体列表
- `interaction`: 互动数据
- `author_name`: 作者名称
- `author_id`: 作者ID
- `publish_time`: 发布时间

### RedNoteMedia
- `url`: 媒体链接
- `media_type`: 类型(image/video)
- `width`: 宽度
- `height`: 高度

### RedNoteInteraction
- `like_count`: 点赞数
- `comment_count`: 评论数
- `collect_count`: 收藏数
- `share_count`: 分享数

## API接口
- **URL**: `https://edith.xiaohongshu.com/api/sns/web/v1/search/notes`
- **方法**: GET
- **用途**: 搜索笔记列表

## 关键代码
```python
# 创建RedNotePreview
preview = RedNotePreview.from_api_response(api_item)

# 批量解析
previews = create_rednote_previews_from_api_response(api_data)
```

## 使用方法
```python
python scripts/test_note_list.py
```