"""
小红书笔记模型 - 使用Pydantic
只关注我们关心的核心数据
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class RedNoteMedia(BaseModel):
    """多媒体信息"""
    url: str = Field(..., description="多媒体链接")
    media_type: str = Field(..., description="媒体类型: image/video")
    width: Optional[int] = Field(None, description="宽度")
    height: Optional[int] = Field(None, description="高度")

    class Config:
        """Pydantic配置"""
        use_enum_values = True


class RedNoteComment(BaseModel):
    """评论数据"""
    comment_id: str = Field(..., description="评论ID")
    content: str = Field(..., description="评论内容")
    user_id: str = Field(default="", description="用户ID")
    user_name: str = Field(default="", description="用户名")
    user_avatar: str = Field(default="", description="用户头像")
    create_time: Optional[str] = Field(None, description="创建时间")
    like_count: int = Field(default=0, description="点赞数")
    sub_comment_count: int = Field(default=0, description="子评论数量")

    @field_validator('like_count', 'sub_comment_count', mode='before')
    @classmethod
    def parse_string_numbers(cls, v):
        """将字符串数字转换为整数"""
        return int(v) if isinstance(v, str) else v

    @field_validator('create_time', mode='before')
    @classmethod
    def parse_timestamp(cls, v):
        """将时间戳转换为字符串"""
        return str(v) if v is not None else None

    class Config:
        use_enum_values = True


class RedNoteInteraction(BaseModel):
    """互动数据"""
    like_count: int = Field(default=0, description="点赞数")
    comment_count: int = Field(default=0, description="评论数")
    collect_count: int = Field(default=0, description="收藏数")
    share_count: int = Field(default=0, description="分享数")

    @field_validator('like_count', 'comment_count', 'collect_count', 'share_count', mode='before')
    @classmethod
    def parse_string_numbers(cls, v):
        """将字符串数字转换为整数"""
        return int(v) if isinstance(v, str) else v

    class Config:
        """Pydantic配置"""
        use_enum_values = True


class RedNotePreview(BaseModel):
    """笔记核心数据模型"""

    # 基本信息
    note_id: str = Field(..., description="笔记ID")
    title: str = Field(..., description="笔记标题")

    # 媒体信息
    media_list: List[RedNoteMedia] = Field(default_factory=list, description="多媒体内容列表")

    # 互动数据
    interaction: RedNoteInteraction = Field(default_factory=RedNoteInteraction, description="互动数据")

    # 元数据
    author_name: str = Field(default="", description="作者名称")
    author_id: str = Field(default="", description="作者ID")
    publish_time: Optional[str] = Field(None, description="发布时间")

    # 解析相关
    capture_time: datetime = Field(default_factory=datetime.now, description="捕获时间")
    source_type: str = Field(default="api", description="数据来源: api/dom")

    class Config:
        """Pydantic配置"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def from_api_response(cls, api_item: dict) -> 'RedNotePreview':
        """从API响应创建笔记对象"""
        note_card = api_item.get('note_card', {})

        # 基本信息
        note_id = api_item.get('id', '')
        title = note_card.get('display_title', '')

        # 媒体信息
        media_list = []

        # 封面图片
        cover = note_card.get('cover', {})
        if cover and cover.get('url_default'):
            media_list.append(RedNoteMedia(
                url=cover['url_default'],
                media_type='image',
                width=cover.get('height', 0),
                height=cover.get('width', 0)
            ))

        # 图片列表
        image_list = note_card.get('image_list', [])
        for img in image_list:
            info_list = img.get('info_list', [])
            for img_info in info_list:
                if img_info.get('image_scene') == 'WB_DFT':  # 默认显示图片
                    media_list.append(RedNoteMedia(
                        url=img_info.get('url', ''),
                        media_type='image',
                        width=img.get('height', 0),
                        height=img.get('width', 0)
                    ))

        # 互动数据
        interact_info = note_card.get('interact_info', {})
        interaction = RedNoteInteraction(
            like_count=interact_info.get('liked_count', 0),
            comment_count=interact_info.get('comment_count', 0),
            collect_count=interact_info.get('collected_count', 0),
            share_count=interact_info.get('shared_count', 0)
        )

        # 作者信息
        user_info = note_card.get('user', {})
        author_name = user_info.get('nickname', '')
        author_id = user_info.get('user_id', '')

        # 发布时间
        publish_time = None
        corner_tags = note_card.get('corner_tag_info', [])
        for tag in corner_tags:
            if tag.get('type') == 'publish_time':
                publish_time = tag.get('text', '')
                break

        return cls(
            note_id=note_id,
            title=title,
            media_list=media_list,
            interaction=interaction,
            author_name=author_name,
            author_id=author_id,
            publish_time=publish_time,
            source_type="api"
        )

    def get_primary_image_url(self) -> Optional[str]:
        """获取主要图片URL"""
        for media in self.media_list:
            if media.media_type == 'image':
                return media.url
        return None

    def has_video(self) -> bool:
        """是否包含视频"""
        return any(media.media_type == 'video' for media in self.media_list)

    def get_media_count(self) -> int:
        """获取媒体数量"""
        return len(self.media_list)


class RedNoteDetail(BaseModel):
    """笔记详情页数据模型"""

    # 基本信息
    note_id: str = Field(..., description="笔记ID")
    title: str = Field(default="", description="笔记标题")
    content: str = Field(default="", description="笔记内容/描述")

    # 媒体信息（详情页通常包含更多媒体）
    media_list: List[RedNoteMedia] = Field(default_factory=list, description="多媒体内容列表")

    # 互动数据
    interaction: RedNoteInteraction = Field(default_factory=RedNoteInteraction, description="互动数据")

    # 作者详细信息
    author_id: str = Field(default="", description="作者ID")
    author_name: str = Field(default="", description="作者名称")
    author_avatar: str = Field(default="", description="作者头像")

    # 时间信息
    publish_time: Optional[str] = Field(None, description="发布时间")
    last_update_time: Optional[str] = Field(None, description="最后更新时间")

    # 评论数据
    comments: List[RedNoteComment] = Field(default_factory=list, description="评论列表")

    # 标签和分类
    tags: List[str] = Field(default_factory=list, description="标签列表")
    topic_list: List[str] = Field(default_factory=list, description="话题列表")

    # 地理位置（如果有）
    location: Optional[str] = Field(None, description="地理位置")

    # 解析相关
    capture_time: datetime = Field(default_factory=datetime.now, description="捕获时间")
    source_type: str = Field(default="detail_page", description="数据来源: detail_page/api")
    url: str = Field(default="", description="详情页URL")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def from_feed_response(cls, feed_data: dict) -> Optional['RedNoteDetail']:
        """从feed API响应创建详情对象"""
        items = feed_data.get('data', {}).get('items', [])
        if not items:
            return None

        note_card = items[0].get('note_card', {})

        # 基本信息
        note_id = note_card.get('id', '')
        title = note_card.get('title', '')
        content = note_card.get('desc', '')

        # 媒体信息
        media_list = []
        image_list = note_card.get('image_list', [])
        for img in image_list:
            info_list = img.get('info_list', [])
            for img_info in info_list:
                if img_info.get('image_scene') == 'WB_DFT':
                    media_list.append(RedNoteMedia(
                        url=img_info.get('url', ''),
                        media_type='image',
                        width=img_info.get('width', 0),
                        height=img_info.get('height', 0)
                    ))

        # 视频信息
        video = note_card.get('video', {})
        if video and video.get('media', {}).get('stream'):
            stream_info = video['media']['stream']
            if isinstance(stream_info, dict) and 'h264' in stream_info:
                h264_info = stream_info['h264']
                if isinstance(h264_info, dict) and h264_info.get('master_url'):
                    media_list.append(RedNoteMedia(
                        url=h264_info['master_url'],
                        media_type='video',
                        width=video.get('width', 0),
                        height=video.get('height', 0)
                    ))

        # 互动数据
        interact_info = note_card.get('interact_info', {})
        interaction = RedNoteInteraction(
            like_count=interact_info.get('liked_count', 0),
            comment_count=interact_info.get('comment_count', 0),
            collect_count=interact_info.get('collected_count', 0),
            share_count=interact_info.get('share_count', 0)
        )

        # 作者信息
        user_info = note_card.get('user', {})
        author_name = user_info.get('nickname', '')
        author_id = user_info.get('user_id', '')
        author_avatar = user_info.get('avatar', '')

        # 标签信息
        tag_list = note_card.get('tag_list', [])
        tags = [tag.get('tag_name', '') for tag in tag_list if tag.get('tag_name')]

        topic_list_items = note_card.get('topic_list', [])
        topics = [topic.get('name', '') for topic in topic_list_items if topic.get('name')]

        # 发布时间
        publish_time = note_card.get('time', '')
        last_update_time = note_card.get('last_update_time', '')

        return cls(
            note_id=note_id,
            title=title,
            content=content,
            media_list=media_list,
            interaction=interaction,
            author_id=author_id,
            author_name=author_name,
            author_avatar=author_avatar,
            publish_time=str(publish_time) if publish_time else None,
            last_update_time=str(last_update_time) if last_update_time else None,
            tags=tags,
            topic_list=topics,
            location=None,
            source_type="feed_api"
        )

    def get_primary_image_url(self) -> Optional[str]:
        """获取主要图片URL"""
        for media in self.media_list:
            if media.media_type == 'image':
                return media.url
        return None

    def has_video(self) -> bool:
        """是否包含视频"""
        return any(media.media_type == 'video' for media in self.media_list)

    def get_media_count(self) -> int:
        """获取媒体数量"""
        return len(self.media_list)

    def get_comment_count(self) -> int:
        """获取评论总数"""
        return len(self.comments)

    @classmethod
    def from_comment_response(cls, comment_data: dict, existing_detail: Optional['RedNoteDetail'] = None) -> 'RedNoteDetail':
        """从评论API响应更新评论数据"""
        if not existing_detail:
            # 如果没有现有详情，创建一个基本的
            existing_detail = cls(
                note_id="",
                title="",
                content="",
                publish_time=None,
                last_update_time=None,
                location=None
            )

        comments = []
        comment_items = comment_data.get('data', {}).get('comments', [])

        for comment_item in comment_items:
            user_info = comment_item.get('user_info', {})

            # 创建主评论
            comment = RedNoteComment(
                comment_id=comment_item.get('id', ''),
                content=comment_item.get('content', ''),
                user_id=user_info.get('user_id', ''),
                user_name=user_info.get('nickname', ''),
                user_avatar=user_info.get('image', ''),
                create_time=str(comment_item.get('create_time', '')),
                like_count=int(comment_item.get('like_count', 0)),
                sub_comment_count=int(comment_item.get('sub_comment_count', 0))
            )
            comments.append(comment)

            # 处理子评论
            sub_comments = comment_item.get('sub_comments', [])
            for sub_item in sub_comments:
                sub_user_info = sub_item.get('user_info', {})
                sub_comment = RedNoteComment(
                    comment_id=sub_item.get('id', ''),
                    content=sub_item.get('content', ''),
                    user_id=sub_user_info.get('user_id', ''),
                    user_name=sub_user_info.get('nickname', ''),
                    user_avatar=sub_user_info.get('image', ''),
                    create_time=str(sub_item.get('create_time', '')),
                    like_count=int(sub_item.get('like_count', 0)),
                    sub_comment_count=0  # 子评论不再嵌套
                )
                comments.append(sub_comment)

        # 更新详情对象的评论
        existing_detail.comments = comments
        existing_detail.interaction.comment_count = len(comments)

        return existing_detail


def create_rednote_previews_from_api_response(api_data: dict) -> list[RedNotePreview]:
    """从API响应创建RedNotePreview列表"""
    previews = []

    # 解析标准API响应结构
    data_section = api_data.get('data', {})
    items = []

    if isinstance(data_section, dict) and 'items' in data_section:
        items = data_section['items']
    elif isinstance(data_section, list):
        items = data_section
    elif 'items' in api_data:
        items = api_data['items']

    for item in items:
        try:
            preview = RedNotePreview.from_api_response(item)
            previews.append(preview)
        except Exception as e:
            print(f"解析RedNotePreview失败: {str(e)}")
            continue

    return previews