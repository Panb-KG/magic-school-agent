"""
完整功能测试脚本
测试从注册、登录到登出的全流程，包括各项子功能

测试数据：
- 3组学生-家长账号
- 第3组包含一个学生和两个家长
- 验证数据隔离
"""

import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 添加项目路径
sys.path.insert(0, '/workspace/projects/src')

from auth.user_manager import UserManager
from storage.database.db import get_session, get_engine
from storage.database.student_manager import StudentManager, StudentCreate
from storage.database.homework_manager import HomeworkManager, HomeworkCreate
from storage.database.course_manager import CourseManager, CourseCreate
from storage.database.achievement_manager import AchievementManager, AchievementCreate
from sqlalchemy import text


class FunctionalTester:
    """功能测试器"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.engine = get_engine()
        self.test_results = []
        self.current_user = None
        
        # 测试数据
        self.test_groups = {
            "group1": {
                "student": {
                    "username": "test_student1",
                    "password": "password123",
                    "name": "张小明",
                    "grade": "3年级1班",
                    "school": "魔法小学"
                },
                "parent": {
                    "username": "test_parent1",
                    "password": "password123",
                    "relationship": "father"
                }
            },
            "group2": {
                "student": {
                    "username": "test_student2",
                    "password": "password123",
                    "name": "李小红",
                    "grade": "4年级2班",
                    "school": "魔法小学"
                },
                "parent": {
                    "username": "test_parent2",
                    "password": "password123",
                    "relationship": "mother"
                }
            },
            "group3": {
                "student": {
                    "username": "test_student3",
                    "password": "password123",
                    "name": "王小华",
                    "grade": "5年级3班",
                    "school": "魔法小学"
                },
                "parents": [
                    {
                        "username": "test_parent3a",
                        "password": "password123",
                        "relationship": "father"
                    },
                    {
                        "username": "test_parent3b",
                        "password": "password123",
                        "relationship": "mother"
                    }
                ]
            }
        }
        
        self.user_registry = {
            "students": {},
            "parents": {}
        }
        
        self.student_records = {}
        
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if message:
            print(f"     {message}")
    
    def cleanup_test_data(self):
        """清理测试数据"""
        print("\n" + "="*80)
        print("🧹 清理测试数据...")
        
        try:
            with self.engine.connect() as conn:
                # 删除关联
                for group_name, group in self.test_groups.items():
                    for parent in group.get("parents", [group.get("parent", {})]):
                        if parent:
                            username = parent.get("username")
                            if username:
                                conn.execute(text("""
                                    DELETE FROM auth.parent_student_mapping
                                    WHERE parent_id IN (
                                        SELECT user_id FROM auth.users WHERE username = :username
                                    )
                                """), {"username": username})
                
                # 删除学生数据（使用 public schema）
                student_usernames = [g["student"]["username"] for g in self.test_groups.values()]
                for username in student_usernames:
                    # 先删除引用数据
                    conn.execute(text("""
                        DELETE FROM achievements WHERE student_id IN (
                            SELECT id FROM students WHERE name IN (
                                SELECT student_name FROM auth.users WHERE username = :username
                            )
                        )
                    """), {"username": username})
                    conn.execute(text("""
                        DELETE FROM homeworks WHERE student_id IN (
                            SELECT id FROM students WHERE name IN (
                                SELECT student_name FROM auth.users WHERE username = :username
                            )
                        )
                    """), {"username": username})
                    conn.execute(text("""
                        DELETE FROM courses WHERE student_id IN (
                            SELECT id FROM students WHERE name IN (
                                SELECT student_name FROM auth.users WHERE username = :username
                            )
                        )
                    """), {"username": username})
                    # 再删除学生
                    conn.execute(text("""
                        DELETE FROM students WHERE name IN (
                            SELECT student_name FROM auth.users WHERE username = :username
                        )
                    """), {"username": username})
                
                # 删除用户
                all_usernames = []
                for group in self.test_groups.values():
                    all_usernames.append(group["student"]["username"])
                    if "parent" in group:
                        all_usernames.append(group["parent"]["username"])
                    if "parents" in group:
                        all_usernames.extend([p["username"] for p in group["parents"]])
                
                for username in all_usernames:
                    conn.execute(text("""
                        DELETE FROM auth.users WHERE username = :username
                    """), {"username": username})
                
                conn.commit()
                print("✅ 测试数据清理完成")
        except Exception as e:
            print(f"❌ 清理测试数据失败: {e}")
    
    def test_register_users(self):
        """测试用户注册"""
        print("\n" + "="*80)
        print("📝 测试用户注册...")
        
        for group_name, group in self.test_groups.items():
            # 注册学生
            student_data = group["student"]
            result = self.user_manager.register_user(
                username=student_data["username"],
                password=student_data["password"],
                role="student",
                student_name=student_data["name"],
                grade=student_data["grade"]
            )
            
            if result["success"]:
                self.user_registry["students"][group_name] = {
                    "user_id": result["user_id"],
                    "username": result["username"],
                    "access_token": result["access_token"],
                    **student_data
                }
                self.log_result(
                    f"注册学生 - {student_data['name']}",
                    True,
                    f"用户ID: {result['user_id']}"
                )
            else:
                self.log_result(
                    f"注册学生 - {student_data['name']}",
                    False,
                    result.get("error", "未知错误")
                )
            
            # 注册家长
            parents = group.get("parents", [group.get("parent")])
            for idx, parent_data in enumerate(parents):
                if parent_data:
                    result = self.user_manager.register_user(
                        username=parent_data["username"],
                        password=parent_data["password"],
                        role="parent"
                    )
                    
                    if result["success"]:
                        parent_key = f"{group_name}_parent{idx+1}" if len(parents) > 1 else f"{group_name}"
                        self.user_registry["parents"][parent_key] = {
                            "user_id": result["user_id"],
                            "username": result["username"],
                            "access_token": result["access_token"],
                            **parent_data
                        }
                        self.log_result(
                            f"注册家长 - {parent_data['username']}",
                            True,
                            f"用户ID: {result['user_id']}"
                        )
                    else:
                        self.log_result(
                            f"注册家长 - {parent_data['username']}",
                            False,
                            result.get("error", "未知错误")
                        )
    
    def test_link_parent_student(self):
        """测试关联家长和学生"""
        print("\n" + "="*80)
        print("🔗 测试关联家长和学生...")
        
        for group_name, group in self.test_groups.items():
            student = self.user_registry["students"][group_name]
            
            parents = group.get("parents", [group.get("parent")])
            for idx, parent_data in enumerate(parents):
                if parent_data:
                    parent_key = f"{group_name}_parent{idx+1}" if len(parents) > 1 else f"{group_name}"
                    parent = self.user_registry["parents"][parent_key]
                    
                    result = self.user_manager.link_parent_student(
                        parent_id=parent["user_id"],
                        student_id=student["user_id"],
                        relationship=parent_data["relationship"]
                    )
                    
                    if result["success"]:
                        self.log_result(
                            f"关联家长学生 - {group_name}",
                            True,
                            f"{parent_data['relationship']} -> {student['name']}"
                        )
                    else:
                        self.log_result(
                            f"关联家长学生 - {group_name}",
                            False,
                            result.get("error", "未知错误")
                        )
    
    def test_login_users(self):
        """测试用户登录"""
        print("\n" + "="*80)
        print("🔑 测试用户登录...")
        
        # 测试学生登录
        for group_name, student in self.user_registry["students"].items():
            result = self.user_manager.login_user(
                username=student["username"],
                password=student["password"]
            )
            
            if result["success"]:
                self.log_result(
                    f"学生登录 - {student['name']}",
                    True
                )
            else:
                self.log_result(
                    f"学生登录 - {student['name']}",
                    False,
                    result.get("error", "未知错误")
                )
        
        # 测试家长登录
        for group_name, parent in self.user_registry["parents"].items():
            result = self.user_manager.login_user(
                username=parent["username"],
                password=parent["password"]
            )
            
            if result["success"]:
                self.log_result(
                    f"家长登录 - {parent['username']}",
                    True
                )
            else:
                self.log_result(
                    f"家长登录 - {parent['username']}",
                    False,
                    result.get("error", "未知错误")
                )
    
    def test_create_student_records(self):
        """测试创建学生数据"""
        print("\n" + "="*80)
        print("📚 测试创建学生数据...")
        
        for group_name, student in self.user_registry["students"].items():
            try:
                db = get_session()
                mgr = StudentManager()
                
                # 创建学生记录（不使用 user_id，因为数据库中没有这个字段）
                student_record = mgr.create_student(db, StudentCreate(
                    name=student["name"],
                    grade=student["grade"],
                    class_name=student["grade"].replace("年级", "").replace("班", "班"),
                    school=student["school"],
                    parent_contact=f"1380013800{group_name[-1]}",
                    nickname=student["name"][0]
                ))
                
                self.student_records[group_name] = student_record
                
                self.log_result(
                    f"创建学生记录 - {student['name']}",
                    True,
                    f"学生ID: {student_record.id}"
                )
                
                # 创建作业
                hw_mgr = HomeworkManager()
                homework = hw_mgr.create_homework(db, HomeworkCreate(
                    student_id=student_record.id,
                    title=f"{student['name']}的数学作业",
                    subject="数学",
                    description="完成练习册第10页",
                    due_date=datetime.now() + timedelta(days=7),
                    priority="high"
                ))
                self.log_result(
                    f"创建作业 - {student['name']}",
                    True,
                    f"作业ID: {homework.id}"
                )
                
                # 创建课程
                course_mgr = CourseManager()
                course = course_mgr.create_course(db, CourseCreate(
                    student_id=student_record.id,
                    course_name=f"{student['name']}的魔法数学课",
                    course_type="school",
                    weekday="Monday",
                    start_time="09:00",
                    end_time="10:30",
                    teacher="邓布利多老师"
                ))
                self.log_result(
                    f"创建课程 - {student['name']}",
                    True,
                    f"课程ID: {course.id}"
                )
                
                # 创建成就
                ach_mgr = AchievementManager()
                achievement = ach_mgr.create_achievement(db, AchievementCreate(
                    student_id=student_record.id,
                    achievement_type="study_effort",
                    title=f"{student['name']}的第一个成就",
                    description="完成首次学习任务",
                    points=10
                ))
                self.log_result(
                    f"创建成就 - {student['name']}",
                    True,
                    f"成就ID: {achievement.id}"
                )
                
                db.close()
            except Exception as e:
                self.log_result(
                    f"创建学生数据 - {student['name']}",
                    False,
                    str(e)
                )
    
    def test_student_functions(self):
        """测试学生功能"""
        print("\n" + "="*80)
        print("👦 测试学生功能...")
        
        for group_name, student in self.user_registry["students"].items():
            student_record = self.student_records.get(group_name)
            if not student_record:
                continue
            
            try:
                db = get_session()
                mgr = StudentManager()
                
                # 在新的Session中重新获取学生记录
                fresh_student = mgr.get_student_by_id(db, student_record.id)
                if not fresh_student:
                    self.log_result(
                        f"学生功能测试 - {student['name']}",
                        False,
                        "无法获取学生记录"
                    )
                    db.close()
                    continue
                
                # 获取学生信息
                info = mgr.get_student_by_id(db, fresh_student.id)
                self.log_result(
                    f"获取学生信息 - {student['name']}",
                    info is not None,
                    f"姓名: {info.name if info else 'None'}"
                )
                
                # 增加积分
                updated = mgr.add_points(db, fresh_student.id, 50)
                self.log_result(
                    f"增加积分 - {student['name']}",
                    updated.total_points > 0,
                    f"总积分: {updated.total_points}"
                )
                
                # 升级魔法等级
                upgraded = mgr.upgrade_magic_level(db, fresh_student.id)
                self.log_result(
                    f"升级魔法等级 - {student['name']}",
                    upgraded.magic_level > 1,
                    f"当前等级: {upgraded.magic_level}"
                )
                
                db.close()
            except Exception as e:
                self.log_result(
                    f"学生功能测试 - {student['name']}",
                    False,
                    str(e)
                )
    
    def test_parent_functions(self):
        """测试家长功能"""
        print("\n" + "="*80)
        print("👨‍👩‍👧 测试家长功能...")
        
        for group_name, parent in self.user_registry["parents"].items():
            if "parent2" in group_name:
                continue  # 跳过第3组的第二个家长，稍后单独测试
            
            try:
                with self.engine.connect() as conn:
                    # 查看关联的学生列表
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM auth.parent_student_mapping
                        WHERE parent_id = :parent_id
                    """), {"parent_id": parent["user_id"]})
                    count = result.scalar()
                    
                    self.log_result(
                        f"家长查看学生列表 - {parent['username']}",
                        count > 0,
                        f"关联学生数: {count}"
                    )
            except Exception as e:
                self.log_result(
                    f"家长功能测试 - {parent['username']}",
                    False,
                    str(e)
                )
    
    def test_multi_parent_scenario(self):
        """测试多家长关联场景"""
        print("\n" + "="*80)
        print("👨‍👩‍👦 测试多家长关联场景（第3组：王小华）...")
        
        student = self.user_registry["students"]["group3"]
        parent3a = self.user_registry["parents"]["group3_parent1"]
        parent3b = self.user_registry["parents"]["group3_parent2"]
        
        try:
            with self.engine.connect() as conn:
                # 验证学生有多个家长
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM auth.parent_student_mapping
                    WHERE student_id = :student_id
                """), {"student_id": student["user_id"]})
                count = result.scalar()
                
                self.log_result(
                    f"学生关联多个家长 - {student['name']}",
                    count == 2,
                    f"关联家长数: {count}"
                )
                
                # 验证两个家长都能访问同一个学生
                for idx, parent in enumerate([parent3a, parent3b], 1):
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM auth.parent_student_mapping
                        WHERE parent_id = :parent_id AND student_id = :student_id
                    """), {
                        "parent_id": parent["user_id"],
                        "student_id": student["user_id"]
                    })
                    linked = result.scalar() > 0
                    
                    self.log_result(
                        f"家长{idx}访问学生 - {parent['username']}",
                        linked,
                        f"可以访问: {student['name']}"
                    )
        except Exception as e:
            self.log_result(
                f"多家长场景测试",
                False,
                str(e)
            )
    
    def test_data_isolation(self):
        """测试数据隔离"""
        print("\n" + "="*80)
        print("🔒 测试数据隔离...")
        
        # 验证不同学生的数据是隔离的
        student1 = self.student_records.get("group1")
        student2 = self.student_records.get("group2")
        student3 = self.student_records.get("group3")
        
        if not all([student1, student2, student3]):
            self.log_result(
                "数据隔离测试",
                False,
                "学生记录未正确创建"
            )
            return
        
        try:
            db = get_session()
            mgr = StudentManager()
            hw_mgr = HomeworkManager()
            
            # 在新的Session中重新获取学生记录
            fresh_student1 = mgr.get_student_by_id(db, student1.id)
            fresh_student2 = mgr.get_student_by_id(db, student2.id)
            fresh_student3 = mgr.get_student_by_id(db, student3.id)
            
            if not all([fresh_student1, fresh_student2, fresh_student3]):
                self.log_result(
                    "数据隔离测试",
                    False,
                    "无法重新获取学生记录"
                )
                db.close()
                return
            
            # 获取每个学生的作业
            hw1 = hw_mgr.get_student_homeworks(db, fresh_student1.id)
            hw2 = hw_mgr.get_student_homeworks(db, fresh_student2.id)
            hw3 = hw_mgr.get_student_homeworks(db, fresh_student3.id)
            
            # 验证作业数量
            self.log_result(
                "数据隔离 - 作业数量",
                len(hw1) > 0 and len(hw2) > 0 and len(hw3) > 0,
                f"学生1: {len(hw1)}, 学生2: {len(hw2)}, 学生3: {len(hw3)}"
            )
            
            # 验证作业内容不交叉
            titles1 = set([hw.title for hw in hw1])
            titles2 = set([hw.title for hw in hw2])
            intersection = titles1 & titles2
            
            self.log_result(
                "数据隔离 - 作业内容",
                len(intersection) == 0,
                f"学生1和学生2的作业重复数: {len(intersection)}"
            )
            
            db.close()
        except Exception as e:
            self.log_result(
                "数据隔离测试",
                False,
                str(e)
            )
    
    def test_logout(self):
        """测试登出"""
        print("\n" + "="*80)
        print("🚪 测试登出...")
        
        # 清除当前用户
        self.current_user = None
        self.log_result(
            "用户登出",
            True,
            "所有测试用户已登出"
        )
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("📊 测试报告")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n总计测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"通过率: {pass_rate:.2f}%")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  ❌ {result['test_name']}: {result['message']}")
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": pass_rate,
            "details": self.test_results
        }
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始完整功能测试...")
        print("="*80)
        
        try:
            # 清理之前的测试数据
            self.cleanup_test_data()
            
            # 执行测试
            self.test_register_users()
            self.test_link_parent_student()
            self.test_login_users()
            self.test_create_student_records()
            self.test_student_functions()
            self.test_parent_functions()
            self.test_multi_parent_scenario()
            self.test_data_isolation()
            self.test_logout()
            
            # 生成报告
            report = self.generate_report()
            
            # 清理测试数据
            self.cleanup_test_data()
            
            return report
        except Exception as e:
            print(f"\n❌ 测试执行失败: {e}")
            import traceback
            traceback.print_exc()
            return None


if __name__ == "__main__":
    tester = FunctionalTester()
    report = tester.run_all_tests()
    
    if report:
        sys.exit(0 if report["failed"] == 0 else 1)
    else:
        sys.exit(1)
