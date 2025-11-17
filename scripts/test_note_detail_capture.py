#!/usr/bin/env python3
"""
小红书笔记详情页捕获测试
点击笔记 -> 捕获详情 -> 退出返回
"""

import sys
import os
import time
import json
from datetime import datetime

# 添加数据结构路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))
from models.rednote import RedNotePreview, RedNoteDetail, RedNoteComment, RedNoteMedia, RedNoteInteraction
from DrissionPage import Chromium


def test_note_detail_workflow():
    """测试笔记详情工作流程"""
    print("🔍 开始笔记详情捕获测试")
    print("=" * 50)

    try:
        # 1. 启动浏览器
        print("📍 步骤1: 启动浏览器...")

        # 先尝试连接现有浏览器，如果失败则自动启动新的
        try:
            browser = Chromium(9933)
            tab = browser.get_tab(0)
            print("✅ 连接到现有浏览器（显示鼠标光标）")
        except Exception as e:
            print(f"   ⚠️ 连接失败，启动新浏览器: {str(e)}")
            # 启动新的浏览器
            browser = Chromium()
            tab = browser.get_tab(0)
            print("✅ 新浏览器启动成功（显示鼠标光标）")

        # 2. 导航到小红书
        if 'xiaohongshu.com' not in tab.url:
            print("📍 步骤2: 导航到小红书...")
            tab.get('https://www.xiaohongshu.com/')
            time.sleep(3)
            print("✅ 已打开小红书")

        # 3. 捕获当前页面的笔记列表
        print("\n📍 步骤3: 捕获笔记列表...")
        list_previews = capture_list_previews(tab)
        print(f"✅ 捕获到 {len(list_previews)} 个笔记预览")

        if not list_previews:
            print("⚠️ 未找到笔记，尝试导航到探索页面...")
            tab.get('https://www.xiaohongshu.com/explore')
            time.sleep(5)  # 增加等待时间
            list_previews = capture_list_previews(tab)
            print(f"✅ 探索页面捕获到 {len(list_previews)} 个笔记预览")

        if not list_previews:
            print("⚠️ 仍未找到笔记，尝试搜索...")
            # 搜索一些热门关键词
            search_keywords = ["AI", "科技", "美食", "旅行"]
            for keyword in search_keywords:
                print(f"   🔍 搜索关键词: {keyword}")
                try:
                    # 在搜索框中输入关键词
                    search_input = tab.ele('input[placeholder*="搜索"]', timeout=2)
                    if search_input:
                        search_input.clear()
                        search_input.input(keyword)
                        search_input.run_js('this.form.submit();')
                        time.sleep(5)

                        list_previews = capture_list_previews(tab)
                        if list_previews:
                            print(f"   ✅ 搜索结果找到 {len(list_previews)} 个笔记")
                            break
                except Exception as e:
                    print(f"   ⚠️ 搜索失败: {str(e)}")
                    continue

        if not list_previews:
            print("⚠️ 经过多次尝试仍未找到笔记，但继续测试DOM解析功能")
            # 即使没有找到笔记，也继续测试详情页功能
            # 直接导航到小红书首页
            tab.get('https://www.xiaohongshu.com/')
            time.sleep(3)
            print("💡 自动导航到首页，继续测试DOM解析功能...")

        # 4. 启动网络监听，然后点击进入笔记详情页
        print("\n📍 步骤4: 启动网络监听并进入详情页...")
        detail_data_list = []

        # 启动网络监听
        print("   🌐 启动网络监听...")
        tab.listen.start('edith.xiaohongshu.com')

        # 先滚动页面加载更多笔记
        print("   📜 滚动页面加载更多笔记...")
        for _ in range(3):
            tab.scroll.down(3)
            time.sleep(1)

        # 查找可点击的笔记元素
        note_elements = find_clickable_notes(tab)
        print(f"   🔍 找到 {len(note_elements)} 个可点击的笔记")

        # 等待用户准备就绪
        print("\n" + "=" * 50)
        print("📝 接下来将测试笔记详情页功能：")
        print("💡 请观察以下API接口：")
        print("   🔸 评论接口: /api/sns/web/v2/comment/page")
        print("   🔸 详情接口: /api/sns/web/v1/feed")
        print("💡 程序会点击笔记并捕获相关API请求")
        print("💡 按 Ctrl+C 停止测试")
        print("=" * 50)

        for i, note_element in enumerate(note_elements[:3]):  # 测试前3个
            print(f"\n📝 测试笔记 {i+1}...")

            # 记录点击前的URL
            before_url = tab.url

            # 清空之前的网络请求缓存
            captured_requests = []

            # 点击笔记
            print(f"   👆 点击笔记...")
            try:
                # 尝试点击笔记元素本身
                note_element.click()
                time.sleep(5)  # 增加等待时间让API请求完成
            except:
                # 如果点击失败，尝试点击链接
                try:
                    link = note_element.ele('a', timeout=1)
                    if link:
                        link.click()
                        time.sleep(5)
                except:
                    print("   ⚠️ 点击失败，跳过此笔记")
                    continue

            # 检查是否成功进入详情页
            if '/explore/' in tab.url and tab.url != before_url:
                print(f"   ✅ 成功进入详情页: {tab.url}")

                # 初始化详情数据
                detail_data = None

                # 捕获网络请求
                time.sleep(3)
                captured_requests = []
                try:
                    for packet in tab.listen.steps(timeout=2):
                        if hasattr(packet, 'url'):
                            url = packet.url
                            if '/api/sns/web/v2/comment/page' in url:
                                print(f"   💬 捕获到评论接口: {url}")

                                # 尝试获取响应数据
                                if hasattr(packet, 'response') and packet.response:
                                    try:
                                        response_data = packet.response.body
                                        if response_data:
                                            comments = parse_comment_response(response_data)
                                            if comments and detail_data:
                                                detail_data.comments = comments
                                                print(f"   💬 解析到 {len(comments)} 条评论")
                                    except Exception as e:
                                        print(f"   ⚠️ 评论数据解析失败: {str(e)}")
                            elif '/api/sns/web/v1/feed' in url:
                                print(f"   📄 捕获到详情接口: {url}")

                                # 尝试获取响应数据
                                if hasattr(packet, 'response') and packet.response:
                                    try:
                                        response_data = packet.response.body
                                        if response_data:
                                            feed_detail = parse_feed_response(response_data)
                                            if feed_detail:
                                                detail_data = feed_detail
                                                print(f"   📄 更新详情信息: 标题={detail_data.title[:30]}...")
                                    except Exception as e:
                                        print(f"   ⚠️ 详情数据解析失败: {str(e)}")
                        captured_requests.append(packet.url)
                except Exception as e:
                    print(f"   ⚠️ 网络监听异常: {str(e)}")

                # 如果没有从API获取到详情，从DOM捕获
                if not detail_data:
                    detail_data = capture_note_detail(tab)

                if detail_data:
                    detail_data_list.append(detail_data)
                    print(f"   ✅ 详情捕获成功: 标题={detail_data.title[:30]}, 评论={detail_data.get_comment_count()}条")
                else:
                    print(f"   ⚠️ 详情捕获失败")

                print(f"   🌐 捕获到 {len(captured_requests)} 个API请求")

                # 退出详情页
                print(f"   🔙 退出详情页...")
                exit_note_detail(tab)
                time.sleep(2)
            else:
                print(f"   ⚠️ 点击后未进入详情页")

            # 确保回到列表页
            if '/explore/' in tab.url:
                tab.back()
                time.sleep(2)

        # 5. 保存结果
        if detail_data_list:
            save_detail_results(list_previews, detail_data_list)

        print(f"\n🎉 测试完成！成功捕获 {len(detail_data_list)} 个笔记详情")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def find_clickable_notes(tab):
    """查找页面上可点击的笔记元素"""
    note_elements = []

    try:
        # 等待页面加载
        time.sleep(2)

        # 常见的笔记卡片选择器
        note_selectors = [
            '.note-item',
            '.note-card',
            '.feeds-container .note-item',
            '.note-list .note',
            '[data-testid="note-item"]',
            '.feed-item',
            '.explore-feed .note'
        ]

        for selector in note_selectors:
            try:
                elements = tab.eles(selector, timeout=2)
                for element in elements:
                    # 检查元素是否可见且可点击
                    if element.states.is_displayed:
                        note_elements.append(element)
                        print(f"   🎯 找到笔记元素: {selector}")
                if note_elements:
                    break
            except:
                continue

        # 如果没找到，尝试查找包含链接的元素
        if not note_elements:
            print("   🔍 尝试查找包含链接的元素...")
            links = tab.eles('a[href*="/explore/"]')
            for link in links[:10]:
                if link.states.is_displayed:
                    note_elements.append(link)

    except Exception as e:
        print(f"   ⚠️ 查找笔记元素失败: {str(e)}")

    return note_elements

def capture_list_previews(tab):
    """捕获当前页面的笔记预览列表"""
    previews = []

    try:
        # 等待页面加载
        time.sleep(2)

        # 查找笔记链接
        note_links = tab.eles('a[href*="/explore/"]')

        for link in note_links[:10]:  # 限制数量
            try:
                href = link.attr('href')
                if href and '/explore/' in href:
                    note_id = href.split('/explore/')[-1].split('?')[0]
                    if note_id:
                        preview = RedNotePreview(
                            note_id=note_id,
                            title=f"笔记 {note_id[:8]}",  # 后续可通过API获取真实标题
                            source_type="dom_list",
                            interaction=RedNoteInteraction(),  # 提供默认互动数据
                            author_name="",  # 提供默认作者名
                            author_id=""  # 提供默认作者ID
                        )
                        previews.append(preview)
            except Exception:
                continue

    except Exception as e:
        print(f"⚠️ 列表捕获失败: {str(e)}")

    return previews

def capture_note_detail(tab):
    """捕获笔记详情页数据"""
    try:
        # 等待详情页加载
        time.sleep(3)

        # 验证是否在详情页
        current_url = tab.url
        if '/explore/' not in current_url:
            print("   ⚠️ 当前不在笔记详情页")
            return None

        note_id = current_url.split('/explore/')[-1].split('?')[0]

        # 创建RedNoteDetail对象
        detail = RedNoteDetail(
            note_id=note_id,
            url=current_url,
            publish_time=None,
            last_update_time=None,
            location=None
        )

        # 解析标题
        title_selectors = [
            '.note-title',
            '.note-detail-title',
            'h1',
            '.title'
        ]
        for selector in title_selectors:
            try:
                title_ele = tab.ele(selector, timeout=1)
                if title_ele:
                    detail.title = title_ele.text.strip()
                    break
            except:
                continue

        # 解析作者
        author_selectors = [
            '.author-name',
            '.user-name',
            '.username',
            '.user-info .name'
        ]
        for selector in author_selectors:
            try:
                author_ele = tab.ele(selector, timeout=1)
                if author_ele:
                    detail.author_name = author_ele.text.strip()
                    break
            except:
                continue

        # 解析内容
        content_selectors = [
            '.note-content .content',
            '.desc-text',
            '.note-text .content-text',
            '[data-testid="note-content"]'
        ]
        for selector in content_selectors:
            try:
                content_ele = tab.ele(selector, timeout=1)
                if content_ele:
                    detail.content = content_ele.text.strip()
                    break
            except:
                continue

        # 解析媒体URL
        media_selectors = [
            '.note-content img',
            '.image-item img',
            '.photo img',
            '.video video'
        ]
        media_list = []
        for selector in media_selectors:
            try:
                media_eles = tab.eles(selector, timeout=1)
                for media_ele in media_eles:
                    url = media_ele.attr('src')
                    if url and url not in [m.url for m in media_list]:
                        media_type = 'video' if 'video' in selector else 'image'
                        media_list.append(RedNoteMedia(
                            url=url,
                            media_type=media_type,
                            width=None,
                            height=None
                        ))
            except:
                continue

        if media_list:
            detail.media_list = media_list

        # 解析互动数据
        interaction_selectors = {
            'like_count': ['.like-count', '.liked-count', '[data-testid="like-count"]'],
            'comment_count': ['.comment-count', '[data-testid="comment-count"]'],
            'collect_count': ['.collect-count', '[data-testid="collect-count"]']
        }

        interaction = RedNoteInteraction()
        for key, selectors in interaction_selectors.items():
            for selector in selectors:
                try:
                    ele = tab.ele(selector, timeout=1)
                    if ele:
                        count = ele.text.strip()
                        try:
                            setattr(interaction, key, int(count))
                        except ValueError:
                            setattr(interaction, key, 0)
                        break
                except:
                    continue

        detail.interaction = interaction

        print(f"   📄 标题: {detail.title[:30]}")
        print(f"   👤 作者: {detail.author_name}")
        print(f"   📱 媒体: {len(detail.media_list)} 个")
        print(f"   🔥 互动: {detail.interaction.like_count}赞 {detail.interaction.comment_count}评")

        return detail

    except Exception as e:
        print(f"   ❌ 详情解析失败: {str(e)}")
        return None

def exit_note_detail(tab):
    """退出笔记详情页 - 模拟真实用户行为"""
    try:
        # 方法1: 尝试点击返回按钮（最常见的退出方式）
        back_selectors = [
            '.back-btn',
            '.header-back',
            'button[aria-label="返回"]',
            '.nav-back',
            '[data-testid="back-button"]',
            '.close-btn',
            'button[aria-label="关闭"]'
        ]

        for selector in back_selectors:
            try:
                back_btn = tab.ele(selector, timeout=1)
                if back_btn and back_btn.states.is_displayed:
                    print(f"   🔙 点击返回按钮: {selector}")
                    back_btn.click()
                    time.sleep(2)
                    return
            except:
                continue

        # 方法2: 使用浏览器后退
        print("   🔙 使用浏览器后退...")
        tab.back()
        time.sleep(2)

        # 方法3: 如果还在详情页，手势滑动返回（模拟移动端）
        if '/explore/' in tab.url:
            print("   👆 尝试手势返回...")
            # 在页面左侧向右滑动模拟返回手势
            try:
                tab.actions.move(100, 300).move(400, 300).release()
                time.sleep(2)
            except:
                pass

        # 方法4: 最后备选：跳转到首页
        if '/explore/' in tab.url:
            print("   🏠 跳转到首页...")
            tab.get('https://www.xiaohongshu.com/')
            time.sleep(2)

    except Exception as e:
        print(f"   ⚠️ 退出失败: {str(e)}")

def save_detail_results(list_previews, detail_previews):
    """保存测试结果"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'scripts/note_detail_test_{timestamp}.json'

    try:
        os.makedirs('scripts', exist_ok=True)

        data = {
            'test_time': datetime.now().isoformat(),
            'list_previews': [preview.model_dump() for preview in list_previews],
            'detail_previews': [detail.model_dump() for detail in detail_previews],
            'success_count': len(detail_previews),
            'total_count': len(list_previews)
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        print(f"💾 结果已保存: {filename}")

    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")

def parse_comment_response(response_data):
    """解析评论API响应"""
    try:
        # 如果响应数据是字符串，先解析为字典
        if isinstance(response_data, str):
            data = json.loads(response_data)
        else:
            data = response_data

        # 使用模型解析评论数据
        comments = []
        comment_items = data.get('data', {}).get('comments', [])

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

        return comments

    except Exception as e:
        print(f"解析评论响应失败: {str(e)}")
        return []

def parse_feed_response(response_data):
    """解析feed API响应"""
    try:
        # 如果响应数据是字符串，先解析为字典
        if isinstance(response_data, str):
            data = json.loads(response_data)
        else:
            data = response_data

        # 使用模型解析详情数据
        detail = RedNoteDetail.from_feed_response(data)
        return detail

    except Exception as e:
        print(f"解析feed响应失败: {str(e)}")
        return None

if __name__ == "__main__":
    test_note_detail_workflow()