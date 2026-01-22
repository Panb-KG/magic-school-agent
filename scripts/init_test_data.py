"""
测试数据初始化脚本
用于为魔法课桌智能体测试创建测试账号和预置数据
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到 Python 路径
workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, workspace_path)

from storage.database.db import get_session
from storage.database.shared.model import Student, Course, Homework, Exercise, Achievement

def create_test_student():
    """创建测试学生账号"""
    session = get_session()

    # 检查是否已存在测试学生
    existing = session.query(Student).filter(Student.name == "测试小魔法师").first()
    if existing:
        print("✅ 测试学生账号已存在")
        return existing.id

    # 创建测试学生
    student = Student(
        name="测试小魔法师",
        nickname="小哈利",
        grade="五年级",
        class_name="魔法班",
        school="霍格沃茨小学",
        magic_level=2,
        total_points=150,
        parent_contact="test_parent@example.com",
        avatar_url=None,
        is_active=True
    )

    session.add(student)
    session.commit()
    session.refresh(student)

    print(f"✅ 创建测试学生账号成功: {student.name} (ID: {student.id})")
    return student.id

def create_test_courses(student_id):
    """创建测试课程数据"""
    session = get_session()

    today = datetime.now()
    current_weekday = today.weekday()  # 0=Monday, 6=Sunday

    # 计算本周一的日期
    monday = today - timedelta(days=current_weekday)

    courses_data = [
        {
            "course_name": "数学课",
            "course_type": "school",
            "weekday": "Monday",
            "start_time": "09:00",
            "end_time": "10:00",
            "teacher": "麦格教授",
            "location": "魔法教室A",
            "classroom": "201",
            "notes": "记得带魔法尺"
        },
        {
            "course_name": "语文课",
            "course_type": "school",
            "weekday": "Monday",
            "start_time": "10:15",
            "end_time": "11:15",
            "teacher": "邓布利多教授",
            "location": "魔法教室B",
            "classroom": "202",
            "notes": "背诵课文"
        },
        {
            "course_name": "英语课",
            "course_type": "school",
            "weekday": "Tuesday",
            "start_time": "09:00",
            "end_time": "10:00",
            "teacher": "斯内普教授",
            "location": "魔法教室C",
            "classroom": "203",
            "notes": "单词默写"
        },
        {
            "course_name": "体育课",
            "course_type": "school",
            "weekday": "Tuesday",
            "start_time": "14:00",
            "end_time": "15:00",
            "teacher": "海格",
            "location": "操场",
            "classroom": "",
            "notes": "穿运动鞋"
        },
        {
            "course_name": "钢琴课",
            "course_type": "extra",
            "weekday": "Saturday",
            "start_time": "10:00",
            "end_time": "11:00",
            "teacher": "音乐老师",
            "location": "音乐教室",
            "classroom": "305",
            "notes": "自带乐谱"
        }
    ]

    for course_data in courses_data:
        course = Course(student_id=student_id, **course_data)
        session.add(course)

    session.commit()
    print(f"✅ 创建测试课程 {len(courses_data)} 条")

def create_test_homeworks(student_id):
    """创建测试作业数据"""
    session = get_session()

    today = datetime.now()

    homeworks_data = [
        {
            "title": "数学练习册第15页",
            "subject": "数学",
            "description": "完成练习册第15页的所有题目",
            "due_date": today + timedelta(days=2),  # 后天
            "status": "pending",
            "priority": "medium",
            "category": "日常作业"
        },
        {
            "title": "语文作文草稿",
            "subject": "语文",
            "description": "写一篇关于'我的梦想'的作文草稿",
            "due_date": today + timedelta(days=3),  # 3天后
            "status": "pending",
            "priority": "high",
            "category": "作文"
        },
        {
            "title": "英语单词记忆",
            "subject": "英语",
            "description": "背诵第5单元的所有单词",
            "due_date": today + timedelta(days=1),  # 明天
            "status": "pending",
            "priority": "medium",
            "category": "背诵"
        },
        {
            "title": "数学复习卷",
            "subject": "数学",
            "description": "完成期末复习试卷",
            "due_date": today - timedelta(days=7),  # 上周截止（已过期）
            "status": "overdue",
            "priority": "high",
            "category": "复习"
        },
        {
            "title": "科学实验报告",
            "subject": "科学",
            "description": "撰写植物生长观察报告",
            "due_date": today - timedelta(days=5),  # 已完成
            "status": "completed",
            "priority": "medium",
            "category": "实验"
        }
    ]

    for hw_data in homeworks_data:
        homework = Homework(student_id=student_id, **hw_data)
        session.add(homework)

    session.commit()
    print(f"✅ 创建测试作业 {len(homeworks_data)} 条")

def create_test_achievements(student_id):
    """创建测试成就数据"""
    session = get_session()

    achievements_data = [
        {
            "achievement_type": "homework_exercise",
            "title": "勤劳小巫师",
            "description": "连续一周完成所有作业",
            "points": 50,
            "level": "silver",
            "is_featured": True
        },
        {
            "achievement_type": "study_effort",
            "title": "阅读达人",
            "description": "累计阅读时间超过10小时",
            "points": 30,
            "level": "bronze",
            "is_featured": True
        },
        {
            "achievement_type": "persistence",
            "title": "坚持魔杖",
            "description": "连续学习7天",
            "points": 100,
            "level": "gold",
            "is_featured": True
        }
    ]

    for achievement_data in achievements_data:
        achievement = Achievement(student_id=student_id, **achievement_data)
        session.add(achievement)

    session.commit()
    print(f"✅ 创建测试成就 {len(achievements_data)} 条")

def create_test_exercises(student_id):
    """创建测试运动记录"""
    session = get_session()

    today = datetime.now()

    exercises_data = [
        {
            "exercise_type": "run",
            "duration": 30,
            "distance": 2.5,
            "calories": 200,
            "date": today,
            "points": 30,
            "notes": "晨跑"
        },
        {
            "exercise_type": "skip_rope",
            "duration": 15,
            "distance": None,
            "calories": 100,
            "date": today - timedelta(days=1),
            "points": 15,
            "notes": "跳绳练习"
        }
    ]

    for exercise_data in exercises_data:
        exercise = Exercise(student_id=student_id, **exercise_data)
        session.add(exercise)

    session.commit()
    print(f"✅ 创建测试运动记录 {len(exercises_data)} 条")

def main():
    """主函数"""
    print("=" * 50)
    print("🧙‍♂️ 魔法课桌智能体 - 测试数据初始化")
    print("=" * 50)

    try:
        # 创建测试学生
        student_id = create_test_student()

        # 创建测试课程
        create_test_courses(student_id)

        # 创建测试作业
        create_test_homeworks(student_id)

        # 创建测试成就
        create_test_achievements(student_id)

        # 创建测试运动记录
        create_test_exercises(student_id)

        print("\n" + "=" * 50)
        print("✅ 测试数据初始化完成！")
        print("=" * 50)
        print(f"\n测试学生ID: {student_id}")
        print("测试学生姓名: 测试小魔法师")
        print("\n预置数据:")
        print("- 5条课程记录（周一、周二、周六）")
        print("- 5条作业记录（含未完成、已完成、过期）")
        print("- 3条成就记录（勤劳小巫师、阅读达人、坚持魔杖）")
        print("- 2条运动记录（跑步、跳绳）")
        print("\n可以开始测试了！🧪")

    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
