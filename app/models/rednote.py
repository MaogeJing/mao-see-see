"""
小红书笔记模型 - 使用Pydantic
只关注我们关心的核心数据
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class MediaInfo(BaseModel):
    """多媒体信息"""
    url: str = Field(..., description="多媒体链接")
    media_type: str = Field(..., description="媒体类型: image/video")
    width: Optional[int] = Field(None, description="宽度")
    height: Optional[int] = Field(None, description="高度")

    class Config:
        """Pydantic配置"""
        use_enum_values = True


class InteractionData(BaseModel):
    """互动数据"""
    like_count: int = Field(default=0, description="点赞数")
    comment_count: int = Field(default=0, description="评论数")
    collect_count: int = Field(default=0, description="收藏数")
    share_count: int = Field(default=0, description="分享数")

    @field_validator('*', mode='before')
    @classmethod
    def parse_string_numbers(cls, v):
        """将字符串数字转换为整数"""
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return 0
        return v

    class Config:
        """Pydantic配置"""
        use_enum_values = True


class Note(BaseModel):
    """笔记核心数据模型"""

    # 基本信息
    note_id: str = Field(..., description="笔记ID")
    title: str = Field(..., description="笔记标题")
    content: str = Field(default="", description="笔记正文内容")

    # 媒体信息
    media_list: List[MediaInfo] = Field(default_factory=list, description="多媒体内容列表")

    # 互动数据
    interaction: InteractionData = Field(default_factory=InteractionData, description="互动数据")

    # 元数据
    author_name: str = Field(default="", description="作者名称")
    author_id: str = Field(default="", description="作者ID")
    publish_time: Optional[str] = Field(None, description="发布时间")
    note_url: str = Field(..., description="笔记URL")

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
    def from_api_response(cls, api_item: dict) -> 'Note':
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
            media_list.append(MediaInfo(
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
                    media_list.append(MediaInfo(
                        url=img_info.get('url', ''),
                        media_type='image',
                        width=img.get('height', 0),
                        height=img.get('width', 0)
                    ))

        # 互动数据
        interact_info = note_card.get('interact_info', {})
        interaction = InteractionData(
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

        # URL
        note_url = f"https://www.xiaohongshu.com/explore/{note_id}"

        return cls(
            note_id=note_id,
            title=title,
            media_list=media_list,
            interaction=interaction,
            author_name=author_name,
            author_id=author_id,
            publish_time=publish_time,
            note_url=note_url,
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