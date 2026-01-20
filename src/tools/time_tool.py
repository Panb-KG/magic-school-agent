"""
时间工具
提供当前日期、时间查询功能
"""

from datetime import datetime, timedelta
from langchain.tools import tool, ToolRuntime


@tool
def get_current_time(runtime: ToolRuntime) -> str:
    """
    获取当前日期和时间
    
    返回当前的日期、时间、星期、月份等时间信息，用于：
    - 查询作业时了解今天是星期几
    - 安排课程时了解当前时间
    - 上传文档时标注时间
    - 生成周计划时了解本周日期范围
    
    Returns:
        包含当前时间详细信息的字符串
    """
    now = datetime.now()

    # 获取星期几（中文）
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    weekday_cn = weekdays[now.weekday()]

    # 获取本周的开始和结束
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)

    # 获取本月的第一天和最后一天
    month_start = now.replace(day=1)
    if now.month == 12:
        month_end = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = now.replace(month=now.month + 1, day=1) - timedelta(days=1)

    time_info = f"""
📅 **当前时间信息**

- **日期**: {now.year}年{now.month}月{now.day}日
- **时间**: {now.strftime('%H:%M:%S')}
- **星期**: {weekday_cn}
- **月份**: {now.month}月
- **年份**: {now.year}年

🗓️ **本周时间范围**
- **开始日期**: {week_start.year}年{week_start.month}月{week_start.day}日（{weekdays[0]}）
- **结束日期**: {week_end.year}年{week_end.month}月{week_end.day}日（{weekdays[6]}）

📆 **本月时间范围**
- **开始日期**: {month_start.year}年{month_start.month}月{month_start.day}日
- **结束日期**: {month_end.year}年{month_end.month}月{month_end.day}日

⏰ **其他时间信息**
- **今天是一年的第 {now.timetuple().tm_yday} 天**
- **本月共有 {month_end.day} 天**
- **距离本周末还有 {(6 - now.weekday()) if now.weekday() != 6 else 0} 天**
"""

    return time_info.strip()


@tool
def get_week_date_range(runtime: ToolRuntime) -> str:
    """
    获取本周的日期范围
    
    返回本周一到本周日的日期，用于：
    - 生成周课程表
    - 查看本周作业
    - 安排本周学习计划
    
    Returns:
        本周日期范围信息
    """
    now = datetime.now()
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']

    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)

    week_info = f"""
🗓️ **本周日期范围**
- **开始**: {week_start.year}年{week_start.month}月{week_start.day}日（{weekdays[0]}）
- **结束**: {week_end.year}年{week_end.month}月{week_end.day}日（{weekdays[6]}）

📋 **本周每日日期**
"""
    for i in range(7):
        day = week_start + timedelta(days=i)
        is_today = day.date() == now.date()
        today_marker = " ← 今天" if is_today else ""
        week_info += f"- {day.month}月{day.day}日 {weekdays[i]}{today_marker}\n"

    return week_info.strip()


@tool
def get_date_after(days: int, runtime: ToolRuntime) -> str:
    """
    获取指定天数后的日期
    
    Args:
        days: 天数（正数表示未来，负数表示过去，0表示今天）
    
    Returns:
        指定日期的详细信息
    """
    if not isinstance(days, (int, float)):
        return "⚠️ 错误：天数必须是数字"

    target_date = datetime.now() + timedelta(days=int(days))
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    weekday_cn = weekdays[target_date.weekday()]

    if days == 0:
        time_desc = "今天"
    elif days == 1:
        time_desc = "明天"
    elif days == -1:
        time_desc = "昨天"
    elif days > 0:
        time_desc = f"{int(days)}天后"
    else:
        time_desc = f"{abs(int(days))}天前"

    date_info = f"""
📅 **{time_desc}的日期**

- **日期**: {target_date.year}年{target_date.month}月{target_date.day}日
- **星期**: {weekday_cn}
- **格式化**: {target_date.strftime('%Y-%m-%d')}
- **中文格式**: {target_date.month}月{target_date.day}日
"""

    return date_info.strip()


@tool
def get_today_info(runtime: ToolRuntime) -> str:
    """
    获取今天的简要时间信息（快速查询）
    
    用于在对话中快速了解今天的时间信息
    
    Returns:
        今天的简要时间信息
    """
    now = datetime.now()
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']

    return f"今天是 {now.year}年{now.month}月{now.day}日 {weekdays[now.weekday()]}"
