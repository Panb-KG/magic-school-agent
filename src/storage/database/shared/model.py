from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, JSON, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
import datetime

class Base(DeclarativeBase):
    pass

# 学生信息表
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, comment="学生ID")
    user_id = Column(String(50), unique=True, nullable=True, comment="关联的用户ID（关联到auth.users）")
    name = Column(String(128), nullable=False, comment="学生姓名")
    grade = Column(String(32), nullable=True, comment="年级")
    class_name = Column(String(64), nullable=True, comment="班级")
    school = Column(String(128), nullable=True, comment="学校名称")
    parent_contact = Column(String(32), nullable=True, comment="家长联系方式")
    nickname = Column(String(64), nullable=True, comment="昵称")
    avatar_url = Column(String(512), nullable=True, comment="头像URL")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否活跃")
    magic_level = Column(Integer, default=1, nullable=False, comment="魔法等级（1-10）")
    total_points = Column(Integer, default=0, nullable=False, comment="总积分")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    # 关系
    courses = relationship("Course", back_populates="student")
    homeworks = relationship("Homework", back_populates="student")
    coursewares = relationship("Courseware", back_populates="student")
    exercises = relationship("Exercise", back_populates="student")
    achievements = relationship("Achievement", back_populates="student")

    __table_args__ = (
        Index("ix_students_name", "name"),
        Index("ix_students_school", "school"),
        Index("ix_students_user_id", "user_id"),
        Index("ix_students_active", "is_active"),
    )

# 课程表（学校和课外）
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, comment="课程ID")
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学生ID")
    course_name = Column(String(128), nullable=False, comment="课程名称")
    course_type = Column(String(32), nullable=False, comment="课程类型：school/extra")
    weekday = Column(String(16), nullable=True, comment="星期几（Monday-Sunday）")
    start_time = Column(String(16), nullable=True, comment="开始时间（HH:MM）")
    end_time = Column(String(16), nullable=True, comment="结束时间（HH:MM）")
    location = Column(String(128), nullable=True, comment="上课地点")
    teacher = Column(String(64), nullable=True, comment="老师姓名")
    classroom = Column(String(64), nullable=True, comment="教室")
    is_recurring = Column(Boolean, default=True, nullable=False, comment="是否重复")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    # 关系
    student = relationship("Student", back_populates="courses")

    __table_args__ = (
        Index("ix_courses_student", "student_id"),
        Index("ix_courses_type", "course_type"),
    )

# 作业任务表
class Homework(Base):
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, comment="作业ID")
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学生ID")
    title = Column(String(256), nullable=False, comment="作业标题")
    subject = Column(String(64), nullable=True, comment="科目")
    description = Column(Text, nullable=True, comment="作业描述")
    due_date = Column(DateTime(timezone=True), nullable=True, comment="截止日期")
    status = Column(String(32), default="pending", nullable=False, comment="状态：pending/in_progress/completed/overdue")
    priority = Column(String(16), default="medium", nullable=False, comment="优先级：low/medium/high")
    attachment_url = Column(String(512), nullable=True, comment="附件URL")
    submission_url = Column(String(512), nullable=True, comment="提交文件URL")
    points = Column(Integer, default=0, nullable=True, comment="获得积分")
    feedback = Column(Text, nullable=True, comment="老师反馈")
    category = Column(String(64), nullable=True, comment="分类标签")
    reminder_sent = Column(Boolean, default=False, nullable=False, comment="是否已提醒")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    # 关系
    student = relationship("Student", back_populates="homeworks")

    __table_args__ = (
        Index("ix_homeworks_student", "student_id"),
        Index("ix_homeworks_status", "status"),
        Index("ix_homeworks_due_date", "due_date"),
    )

# 课件表
class Courseware(Base):
    __tablename__ = "coursewares"

    id = Column(Integer, primary_key=True, comment="课件ID")
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学生ID")
    title = Column(String(256), nullable=False, comment="课件标题")
    subject = Column(String(64), nullable=True, comment="科目")
    file_type = Column(String(32), nullable=True, comment="文件类型：pdf/doc/ppt/image/video/other")
    file_url = Column(String(512), nullable=False, comment="文件URL")
    file_size = Column(Integer, nullable=True, comment="文件大小（字节）")
    category = Column(String(64), nullable=True, comment="分类标签")
    description = Column(Text, nullable=True, comment="课件描述")
    download_count = Column(Integer, default=0, nullable=False, comment="下载次数")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    # 关系
    student = relationship("Student", back_populates="coursewares")

    __table_args__ = (
        Index("ix_coursewares_student", "student_id"),
        Index("ix_coursewares_subject", "subject"),
        Index("ix_coursewares_category", "category"),
    )

# 运动记录表
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, comment="运动记录ID")
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学生ID")
    exercise_type = Column(String(64), nullable=False, comment="运动类型：run/swim/basketball/football/skip_rope/yoga/other")
    duration = Column(Integer, nullable=True, comment="时长（分钟）")
    distance = Column(Float, nullable=True, comment="距离（公里）")
    calories = Column(Integer, nullable=True, comment="消耗卡路里")
    date = Column(DateTime(timezone=True), nullable=False, comment="运动日期")
    notes = Column(Text, nullable=True, comment="备注")
    points = Column(Integer, default=0, nullable=False, comment="获得积分")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    # 关系
    student = relationship("Student", back_populates="exercises")

    __table_args__ = (
        Index("ix_exercises_student", "student_id"),
        Index("ix_exercises_date", "date"),
    )

# 成就表
class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, comment="成就ID")
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学生ID")
    achievement_type = Column(String(64), nullable=False, comment="成就类型：homework_exercise/course_complete/reading_goal/study_effort/health_sport/creativity/persistence/other")
    title = Column(String(256), nullable=False, comment="成就标题")
    description = Column(Text, nullable=True, comment="成就描述")
    icon_url = Column(String(512), nullable=True, comment="图标URL")
    points = Column(Integer, default=0, nullable=False, comment="获得积分")
    level = Column(String(32), default="bronze", nullable=False, comment="等级：bronze/silver/gold/platinum/diamond")
    achieved_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="获得时间")
    is_featured = Column(Boolean, default=False, nullable=False, comment="是否展示在成就墙")

    # 关系
    student = relationship("Student", back_populates="achievements")

    __table_args__ = (
        Index("ix_achievements_student", "student_id"),
        Index("ix_achievements_type", "achievement_type"),
        Index("ix_achievements_featured", "is_featured"),
    )
