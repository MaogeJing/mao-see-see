#!/usr/bin/env python3
"""
实验脚本：测试小红书笔记列表抓取功能
"""

from DrissionPage import Chromium
import time
import json
from datetime import datetime
import sys
import os

# 添加数据结构路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_structures'))
from xiaohongshu_models import XiaohongshuNote, XiaohongshuSearchResponse, save_notes_to_json

def test_note_list_capture():
    """测试笔记列表抓取"""
    print("🔍 实验开始：小红书笔记列表抓取")
    print("=" * 50)

    try:
        # 1. 启动持久化浏览器
        print("📍 步骤1: 启动浏览器...")
        browser = Chromium(9933)
        tab = browser.get_tab(0)
        print("✅ 浏览器启动成功")

        # 2. 导航到小红书
        if 'xiaohongshu.com' not in tab.url: # type: ignore
            print("📍 步骤2: 导航到小红书...")
            tab.get('https://www.xiaohongshu.com/')
            time.sleep(5)
            print("✅ 已打开小红书")

        # 3. 启动网络监听
        print("📍 步骤3: 启动网络监听...")
        print(tab.listen.start('xiaohongshu.com'))
        print("✅ 网络监听已启动")

        # 4. 引导用户操作
        print("\n" + "=" * 50)
        print("📝 请在浏览器中进行以下操作：")
        print("🎯 重点：搜索任意关键词（如：Python、编程、美食等）")
        print("💡 关键接口：https://edith.xiaohongshu.com/api/sns/web/v1/search/notes")
        print("📱 步骤：")
        print("   1. 点击搜索框")
        print("   2. 输入关键词")
        print("   3. 点击搜索或按回车")
        print("   4. 观察程序输出（会显示🔥标识的关键接口）")
        print("   5. 滚动页面查看更多笔记")
        print("   6. 按 Ctrl+C 结束测试")
        print("=" * 50)

        # 5. 开始监听和捕获
        captured_notes = []
        last_request_count = 0

        print("🔄 开始监听网络请求...")
        print("💡 提示：请在浏览器中搜索关键词")
        print("💡 程序会每3秒检查一次新的网络请求")
        print("💡 按 Ctrl+C 结束测试")
        print("-" * 50)

        while True:
            try:
                # 使用超时方式避免阻塞
                new_requests = []

                # 尝试获取新的网络请求，设置短暂超时
                try:
                    for packet in tab.listen.steps(timeout=1):
                        new_requests.append(packet)
                except:
                    # 超时是正常的，继续循环
                    pass

                if new_requests:
                    print(f"\n📊 捕获到 {len(new_requests)} 个新请求")

                    for packet in new_requests:
                        try:
                            print(f"🌐 {packet.method} {packet.url[:80]}...")

                            # 专门处理搜索笔记API
                            if 'edith.xiaohongshu.com/api/sns/web/v1/search/notes' in packet.url:
                                print(f"\n🔥 发现关键接口！笔记列表API")

                                # 尝试获取状态码
                                status = '未知'
                                try:
                                    status = packet.response.status if packet.response else '无响应'
                                except:
                                    pass
                                print(f"   状态: {status}")

                                # 直接处理API响应
                                if hasattr(packet, 'response') and packet.response:
                                    try:
                                        if hasattr(packet.response, 'body') and packet.response.body:
                                            notes = process_search_api_response(packet.response.body)
                                            if notes:
                                                captured_notes.extend(notes)
                                                print(f"✅ 提取到 {len(notes)} 个笔记")
                                                for note in notes[:3]:  # 只显示前3个
                                                    print(f"   📝 {note.get('title', '无标题')[:50]}...")
                                    except Exception as e:
                                        print(f"⚠️ 处理响应失败: {str(e)}")

                            else:
                                # 其他相关请求
                                if any(keyword in packet.url for keyword in ['xiaohongshu', 'search', 'note']):
                                    print(f"   🔍 相关请求")

                        except Exception as e:
                            print(f"⚠️ 处理数据包异常: {str(e)}")

                # 显示状态
                if captured_notes:
                    print(f"📈 当前捕获笔记: {len(captured_notes)} 个")

                time.sleep(3)  # 每3秒检查一次

            except KeyboardInterrupt:
                print("\n🛑 用户中断测试")
                break
            except Exception as e:
                print(f"⚠️ 监控异常: {str(e)}")
                time.sleep(2)

        # 6. 保存结果
        if captured_notes:
            save_captured_notes(captured_notes)
            print(f"\n💾 已保存 {len(captured_notes)} 个笔记信息")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def analyze_request(request):
    """分析请求类型"""
    url = request.url.lower()

    result = {
        'url': request.url,
        'url_short': request.url.split('/')[-1][:50],
        'method': request.method,
        'status': request.status,  # 修正：应该是 status 而不是 status_code
        'is_note_related': False,
        'type': 'OTHER'
    }

    # 🎯 重点监听笔记列表接口
    if 'edith.xiaohongshu.com/api/sns/web/v1/search/notes' in url:
        result['type'] = 'NOTE_LIST_API'
        result['is_note_related'] = True
        print(f"\n🔥 发现关键接口！笔记列表API: {request.url}")
    elif '/search/' in url or 'keyword' in url:
        result['type'] = 'SEARCH'
        result['is_note_related'] = True
    elif '/feeds/' in url or 'note' in url:
        result['type'] = 'NOTE_LIST'
        result['is_note_related'] = True
    elif '/api/sns/web/v1/feed' in url:
        result['type'] = 'FEED_API'
        result['is_note_related'] = True
    elif '/api/sns/web/v1/search' in url:
        result['type'] = 'SEARCH_API'
        result['is_note_related'] = True

    return result

def extract_notes_from_request(request):
    """从请求中提取笔记信息"""
    notes = []

    try:
        # 🎯 专门处理笔记列表API
        if 'edith.xiaohongshu.com/api/sns/web/v1/search/notes' in request.url:
            return extract_notes_from_search_api(request)

        # 尝试解析响应数据
        response_body = request.response.body

        if response_body:
            # 尝试JSON解析
            try:
                data = json.loads(response_body)
                extracted = parse_json_for_notes(data)
                notes.extend(extracted)
            except json.JSONDecodeError:
                # 如果不是JSON，尝试其他解析方式
                print(f"⚠️ 响应不是JSON格式: {response_body[:200]}...")

        # 从URL中提取笔记ID
        note_ids = extract_note_ids_from_url(request.url)
        for note_id in note_ids:
            notes.append({
                'note_id': note_id,
                'title': f"笔记 {note_id}",
                'url': request.url,
                'capture_time': datetime.now().isoformat()
            })

    except Exception as e:
        print(f"⚠️ 提取笔记信息失败: {str(e)}")

    return notes

def extract_notes_from_search_api(request):
    """专门处理搜索笔记API的响应"""
    notes = []

    try:
        response_body = request.response.body
        if not response_body:
            return notes

        print(f"🔍 解析搜索API响应 ({len(response_body)} 字节)")

        data = json.loads(response_body)
        print(f"📊 API响应结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")

        # 小红书搜索API的常见数据结构
        if isinstance(data, dict):
            if 'data' in data:
                notes.extend(parse_search_api_data(data['data']))
            elif 'items' in data:
                notes.extend(extract_notes_from_items(data['items']))
            elif 'notes' in data:
                notes.extend(extract_notes_from_items(data['notes']))

        print(f"✅ 从搜索API提取到 {len(notes)} 个笔记")

    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {str(e)}")
    except Exception as e:
        print(f"❌ 搜索API解析失败: {str(e)}")

    return notes

def parse_search_api_data(data):
    """解析搜索API的data字段"""
    notes = []

    if isinstance(data, dict):
        # 检查常见的搜索API结构
        if 'items' in data:
            notes.extend(extract_notes_from_items(data['items']))
        elif 'notes' in data:
            notes.extend(extract_notes_from_items(data['notes']))
        elif 'data' in data:  # 嵌套结构
            notes.extend(parse_search_api_data(data['data']))
    elif isinstance(data, list):
        notes.extend(extract_notes_from_items(data))

    return notes

def parse_json_for_notes(data):
    """从JSON数据中解析笔记信息"""
    notes = []

    try:
        # 常见的笔记数据结构
        if isinstance(data, dict):
            # 检查常见的笔记字段
            if 'data' in data:
                notes.extend(extract_notes_from_data_field(data['data']))
            elif 'items' in data:
                notes.extend(extract_notes_from_items(data['items']))
            elif 'notes' in data:
                notes.extend(extract_notes_from_items(data['notes']))

    except Exception as e:
        print(f"⚠️ JSON解析失败: {str(e)}")

    return notes

def extract_notes_from_data_field(data):
    """从data字段中提取笔记"""
    notes = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and ('note_id' in item or 'id' in item):
                notes.append(parse_note_item(item))
    elif isinstance(data, dict):
        if 'note_id' in data or 'id' in data:
            notes.append(parse_note_item(data))

    return notes

def extract_notes_from_items(items):
    """从items列表中提取笔记"""
    notes = []

    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                # 检查是否包含笔记相关信息
                if 'note_card' in item:
                    notes.append(parse_note_item(item['note_card']))
                elif 'note_id' in item or 'id' in item:
                    notes.append(parse_note_item(item))

    return notes

def parse_note_item(item):
    """解析单个笔记项"""
    note_id = item.get('note_id') or item.get('id') or 'unknown'
    title = item.get('title') or item.get('desc') or f"笔记 {note_id}"

    return {
        'note_id': note_id,
        'title': title,
        'url': f"https://www.xiaohongshu.com/explore/{note_id}",
        'author': item.get('user', {}).get('nickname', ''),
        'likes': item.get('interact_info', {}).get('liked_count', 0),
        'collects': item.get('interact_info', {}).get('collected_count', 0),
        'capture_time': datetime.now().isoformat(),
        'raw_data': item
    }

def extract_note_ids_from_url(url):
    """从URL中提取笔记ID"""
    import re

    # 常见的笔记ID模式
    patterns = [
        r'/explore/([a-f0-9]+)',  # /explore/{note_id}
        r'/discovery/item/([a-f0-9]+)',  # /discovery/item/{note_id}
        r'noteId["\s]*[:=]["\s]*([a-f0-9]+)',  # JSON中的noteId
    ]

    note_ids = []
    for pattern in patterns:
        matches = re.findall(pattern, url)
        note_ids.extend(matches)

    return list(set(note_ids))  # 去重

def save_captured_notes(notes):
    """保存捕获的笔记信息 - 使用新的数据结构"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'scripts/note_list_capture_{timestamp}.json'

    try:
        # 使用新的数据结构保存
        save_notes_to_json(notes, filename)
        print(f"💾 笔记数据已保存到: {filename}")

        # 生成统计报告
        generate_summary_report(notes, filename.replace('.json', '_summary.txt'))

    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")

def generate_summary_report(notes, filename):
    """生成统计报告 - 使用新的数据结构"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("小红书笔记列表抓取统计报告\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"抓取时间: {datetime.now().isoformat()}\n")
            f.write(f"笔记总数: {len(notes)}\n\n")

            # 统计信息
            video_count = sum(1 for note in notes if note.is_video())
            image_count = sum(1 for note in notes if note.has_images())
            total_likes = sum(note.get_like_count() for note in notes)
            total_comments = sum(note.get_comment_count() for note in notes)
            total_collects = sum(note.get_collect_count() for note in notes)

            f.write("📊 统计信息:\n")
            f.write("-" * 20 + "\n")
            f.write(f"图文笔记: {len(notes) - video_count} 个\n")
            f.write(f"视频笔记: {video_count} 个\n")
            f.write(f"包含图片: {image_count} 个\n")
            f.write(f"总点赞数: {total_likes}\n")
            f.write(f"总评论数: {total_comments}\n")
            f.write(f"总收藏数: {total_collects}\n\n")

            # 显示前10个笔记
            f.write("📝 前10个笔记详情:\n")
            f.write("-" * 30 + "\n")
            for i, note in enumerate(notes[:10], 1):
                f.write(f"{i}. {note.title}\n")
                f.write(f"   ID: {note.note_id}\n")
                f.write(f"   作者: {note.get_username()}\n")
                f.write(f"   类型: {'视频' if note.is_video() else '图文'}\n")
                f.write(f"   互动: 点赞{note.get_like_count()} 评论{note.get_comment_count()} 收藏{note.get_collect_count()}\n")
                f.write(f"   URL: {note.note_url}\n\n")

        print(f"📊 统计报告已保存到: {filename}")

    except Exception as e:
        print(f"❌ 生成报告失败: {str(e)}")

def process_search_api_response(response_body):
    """处理搜索API响应数据 - 使用新的数据结构"""
    try:
        print(f"🔍 处理API响应 ({len(response_body)} 字节)")

        # DrissionPage会自动将JSON转为dict
        if isinstance(response_body, dict):
            data = response_body
        else:
            data = json.loads(response_body)

        print(f"📊 响应结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")

        # 使用新的数据结构解析
        search_response = XiaohongshuSearchResponse.from_dict(data)
        notes = search_response.notes

        print(f"✅ 提取到 {len(notes)} 个笔记")

        # 显示前几个笔记的摘要
        for i, note in enumerate(notes[:3]):
            print(f"\n📝 笔记 {i+1} 摘要:")
            print(note.format_summary())

        return notes

    except Exception as e:
        print(f"❌ 处理API响应失败: {str(e)}")
        return []


if __name__ == "__main__":
    test_note_list_capture()