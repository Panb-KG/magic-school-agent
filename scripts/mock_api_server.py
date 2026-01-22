"""
魔法课桌学习助手 - Mock API 服务器

用于前端开发和调试，提供模拟的数据接口
"""
import json
import base64
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt

# ============ 配置 ============
SECRET_KEY = "magic_school_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="魔法课桌 Mock API", version="1.0.0")

# ============ CORS 配置 ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 工具函数 ============
security = HTTPBearer()

def simple_hash(password: str) -> str:
    """简单密码哈希（仅用于Mock API）"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """验证 Token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="无效的Token")

# ============ 数据模型 ============

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    role: str  # 'student' or 'parent'
    student_name: Optional[str] = None
    nickname: Optional[str] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    school: Optional[str] = None
    real_name: Optional[str] = None

# ============ 模拟数据 ============

# 模拟用户数据库
MOCK_USERS = {
    "student": {
        "id": 1,
        "username": "student",
        "password_hash": simple_hash("password123"),
        "role": "student",
        "student_name": "测试小魔法师",
        "nickname": "小哈利",
        "grade": "五年级",
        "class_name": "魔法班",
        "school": "霍格沃茨小学",
        "created_at": "2026-01-01T00:00:00Z"
    },
    "parent": {
        "id": 2,
        "username": "parent",
        "password_hash": simple_hash("password123"),
        "role": "parent",
        "real_name": "测试家长",
        "linked_students": [1],
        "created_at": "2026-01-01T00:00:00Z"
    }
}

# 模拟学生档案
MOCK_PROFILES = {
    "test_student": {
        "id": 1,
        "name": "测试小魔法师",
        "grade": "五年级",
        "class_name": "魔法班",
        "school": "霍格沃茨小学",
        "nickname": "小哈利",
        "avatar_url": "",
        "magic_level": 2,
        "total_points": 150,
        "level_progress": 50,
        "next_level_points": 200
    }
}

# ============ 认证接口 ============

@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    """用户登录"""
    user = MOCK_USERS.get(request.username)

    if not user or user["password_hash"] != simple_hash(request.password):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )

    # 生成 Token
    token_data = {
        "sub": user["username"],
        "user_id": user["id"],
        "role": user["role"]
    }
    access_token = create_access_token(token_data)

    # 返回用户信息
    user_response = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "created_at": user["created_at"]
    }

    if user["role"] == "student":
        user_response.update({
            "student_name": user.get("student_name"),
            "nickname": user.get("nickname"),
            "grade": user.get("grade"),
            "class_name": user.get("class_name"),
            "school": user.get("school")
        })
    elif user["role"] == "parent":
        user_response.update({
            "real_name": user.get("real_name"),
            "linked_students": user.get("linked_students", [])
        })

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user_response
        }
    }

@app.post("/api/v1/auth/register")
async def register(request: RegisterRequest):
    """用户注册"""
    # 检查用户名是否已存在
    if request.username in MOCK_USERS:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 创建新用户
    user_id = len(MOCK_USERS) + 1
    new_user = {
        "id": user_id,
        "username": request.username,
        "password_hash": simple_hash(request.password),
        "role": request.role,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    if request.role == "student":
        new_user.update({
            "student_name": request.student_name or request.username,
            "nickname": request.nickname or request.username,
            "grade": request.grade,
            "class_name": request.class_name,
            "school": request.school
        })
    elif request.role == "parent":
        new_user.update({
            "real_name": request.real_name or request.username,
            "linked_students": []
        })

    MOCK_USERS[request.username] = new_user

    # 生成 Token
    token_data = {
        "sub": request.username,
        "user_id": user_id,
        "role": request.role
    }
    access_token = create_access_token(token_data)

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user_id,
                "username": request.username,
                "role": request.role,
                "created_at": new_user["created_at"]
            }
        }
    }

@app.get("/api/v1/auth/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户信息"""
    payload = verify_token(credentials)
    username = payload.get("sub")

    user = MOCK_USERS.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user_response = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "created_at": user["created_at"]
    }

    if user["role"] == "student":
        user_response.update({
            "student_name": user.get("student_name"),
            "nickname": user.get("nickname"),
            "grade": user.get("grade"),
            "class_name": user.get("class_name"),
            "school": user.get("school")
        })
    elif user["role"] == "parent":
        user_response.update({
            "real_name": user.get("real_name"),
            "linked_students": user.get("linked_students", [])
        })

    return {
        "success": True,
        "data": user_response
    }

# ============ 数据接口 ============

@app.get("/api/v1/dashboard/{student_name}")
async def get_dashboard(student_name: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取仪表盘数据"""
    verify_token(credentials)

    profile = MOCK_PROFILES.get(student_name, MOCK_PROFILES["test_student"])

    return {
        "success": True,
        "data": {
            "profile": profile,
            "stats": {
                "total_points": 150,
                "magic_level": 2,
                "completed_homeworks": 15,
                "pending_homeworks": 3,
                "total_exercises": 8,
                "total_exercise_minutes": 240,
                "total_achievements": 5,
                "featured_achievements": 3,
                "homework_completion_rate": 83.3
            },
            "recent_achievements": [
                {
                    "id": 1,
                    "title": "勤劳小巫师",
                    "description": "连续一周完成所有作业",
                    "type": "homework_exercise",
                    "icon": "",
                    "unlocked_at": "2026-01-20T10:00:00Z",
                    "points": 50,
                    "is_featured": True
                }
            ],
            "todos": [
                {
                    "id": 1,
                    "title": "数学练习册第15页",
                    "subject": "数学",
                    "due_date": "2026-01-24",
                    "days_left": 2,
                    "urgency": "medium",
                    "type": "homework"
                }
            ],
            "suggestions": [
                "你有3个待完成作业",
                "本周运动量较少，建议多运动哦！"
            ],
            "week_stats": {
                "total_points": 80,
                "breakdown": {
                    "homework": 50,
                    "exercise": 20,
                    "reading": 10,
                    "other": 0
                }
            },
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
    }

@app.get("/api/v1/schedule/{student_name}")
async def get_schedule(student_name: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取课程表"""
    verify_token(credentials)

    return {
        "success": True,
        "data": {
            "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "courses": {
                "Monday": [
                    {
                        "id": 1,
                        "name": "数学课",
                        "type": "school",
                        "time": "09:00-10:00",
                        "location": "魔法教室A",
                        "teacher": "麦格教授",
                        "classroom": "201",
                        "notes": "记得带魔法尺"
                    },
                    {
                        "id": 2,
                        "name": "语文课",
                        "type": "school",
                        "time": "10:15-11:15",
                        "location": "魔法教室B",
                        "teacher": "邓布利多教授",
                        "classroom": "202",
                        "notes": "背诵课文"
                    }
                ],
                "Tuesday": [
                    {
                        "id": 3,
                        "name": "英语课",
                        "type": "school",
                        "time": "09:00-10:00",
                        "location": "魔法教室C",
                        "teacher": "斯内普教授",
                        "classroom": "203",
                        "notes": "单词默写"
                    }
                ]
            },
            "statistics": {
                "total_courses": 5,
                "school_courses": 4,
                "extra_courses": 1,
                "course_count_by_day": {
                    "Monday": 2,
                    "Tuesday": 1,
                    "Wednesday": 1,
                    "Thursday": 1,
                    "Friday": 0
                }
            },
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
    }

@app.get("/api/v1/achievements/{student_name}")
async def get_achievements(student_name: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取成就数据"""
    verify_token(credentials)

    return {
        "success": True,
        "data": {
            "student_name": student_name,
            "total_achievements": 5,
            "achievements_by_level": {
                "bronze": 2,
                "silver": 2,
                "gold": 1,
                "platinum": 0,
                "diamond": 0
            },
            "featured_achievements": [
                {
                    "id": 1,
                    "title": "勤劳小巫师",
                    "description": "连续一周完成所有作业",
                    "type": "homework_exercise",
                    "icon": "",
                    "unlocked_at": "2026-01-20T10:00:00Z",
                    "points": 50,
                    "is_featured": True
                }
            ],
            "recent_achievements": [
                {
                    "id": 1,
                    "title": "勤劳小巫师",
                    "description": "连续一周完成所有作业",
                    "type": "homework_exercise",
                    "icon": "",
                    "unlocked_at": "2026-01-20T10:00:00Z",
                    "points": 50,
                    "is_featured": True
                },
                {
                    "id": 2,
                    "title": "阅读达人",
                    "description": "累计阅读时间超过10小时",
                    "type": "reading_goal",
                    "icon": "",
                    "unlocked_at": "2026-01-19T15:30:00Z",
                    "points": 30,
                    "is_featured": True
                }
            ],
            "achievement_points": 80,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
    }

@app.get("/api/v1/homework/{student_name}")
async def get_homework(student_name: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取作业列表"""
    verify_token(credentials)

    return {
        "success": True,
        "data": {
            "student_name": student_name,
            "total": 5,
            "completed": 4,
            "pending": 1,
            "overdue": 0,
            "completion_rate": 80.0,
            "subjects": [
                {
                    "subject": "数学",
                    "total": 2,
                    "completed": 2,
                    "pending": 0
                },
                {
                    "subject": "语文",
                    "total": 2,
                    "completed": 1,
                    "pending": 1
                },
                {
                    "subject": "英语",
                    "total": 1,
                    "completed": 1,
                    "pending": 0
                }
            ],
            "homeworks": [
                {
                    "id": 1,
                    "title": "数学练习册第15页",
                    "subject": "数学",
                    "status": "pending",
                    "due_date": "2026-01-24"
                },
                {
                    "id": 2,
                    "title": "语文作文草稿",
                    "subject": "语文",
                    "status": "pending",
                    "due_date": "2026-01-25"
                }
            ],
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
    }

@app.get("/api/v1/profile/{student_name}")
async def get_profile(student_name: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取学生档案"""
    verify_token(credentials)

    profile = MOCK_PROFILES.get(student_name, MOCK_PROFILES["test_student"])

    return {
        "success": True,
        "data": {
            **profile,
            "achievements_by_level": {
                "bronze": 2,
                "silver": 2,
                "gold": 1,
                "platinum": 0,
                "diamond": 0
            },
            "featured_count": 3,
            "total_achievement_points": 80
        }
    }

@app.get("/api/v1/points/{student_name}")
async def get_points(student_name: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取积分趋势"""
    verify_token(credentials)

    # 生成最近7天的数据
    data = []
    today = datetime.utcnow().date()

    for i in range(7):
        date = today - timedelta(days=6-i)
        data.append({
            "date": date.isoformat(),
            "points": 100 + i * 10,
            "daily_gain": 10 if i > 0 else 0
        })

    return {
        "success": True,
        "data": {
            "student_name": student_name,
            "days": 7,
            "data": data,
            "summary": {
                "total_gain": 60,
                "average_daily_gain": 10,
                "best_day": (today - timedelta(days=6)).isoformat()
            },
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
    }

@app.get("/api/v1/memory/{user_id}")
async def get_memory(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取长期记忆"""
    verify_token(credentials)

    return {
        "success": True,
        "data": {
            "user_id": user_id,
            "profile": {
                "user_id": user_id,
                "username": "student",
                "student_name": "测试小魔法师",
                "nickname": "小哈利",
                "grade": "五年级",
                "learning_style": "视觉型学习者",
                "interests": ["哈利波特", "数学", "阅读"],
                "strengths": ["计算能力", "逻辑思维"],
                "weaknesses": ["作文写作", "单词记忆"],
                "goals": ["提高数学成绩", "多读课外书"],
                "preferences": {
                    "response_style": "鼓励型",
                    "difficulty_level": "渐进式",
                    "encouragement_level": "高"
                },
                "last_updated": datetime.utcnow().isoformat() + "Z"
            },
            "knowledge_mastery": {
                "user_id": user_id,
                "total_topics": 10,
                "mastered_topics": 5,
                "in_progress_topics": 3,
                "weak_topics": 2,
                "average_mastery": 75.0,
                "by_subject": [
                    {
                        "subject": "数学",
                        "total_topics": 4,
                        "average_mastery": 85.0
                    },
                    {
                        "subject": "语文",
                        "total_topics": 3,
                        "average_mastery": 70.0
                    },
                    {
                        "subject": "英语",
                        "total_topics": 3,
                        "average_mastery": 70.0
                    }
                ],
                "topics": [
                    {
                        "user_id": user_id,
                        "subject": "数学",
                        "topic": "分数加减法",
                        "mastery_level": 90,
                        "practice_count": 15,
                        "correct_count": 14,
                        "last_practiced": "2026-01-20",
                        "difficulty": "intermediate"
                    }
                ],
                "last_updated": datetime.utcnow().isoformat() + "Z"
            },
            "conversation_summaries": [
                {
                    "conversation_id": "conv_1",
                    "user_id": user_id,
                    "summary": "讨论了数学分数加减法的问题",
                    "topics": ["数学", "分数"],
                    "sentiment": "positive",
                    "message_count": 8,
                    "created_at": datetime.utcnow().isoformat() + "Z"
                }
            ]
        }
    }

@app.get("/api/v1/parent/students")
async def parent_get_students(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """家长获取学生列表"""
    payload = verify_token(credentials)

    if payload.get("role") != "parent":
        raise HTTPException(status_code=403, detail="权限不足")

    return {
        "success": True,
        "data": [
            {
                "id": 1,
                "username": "student",
                "student_name": "测试小魔法师",
                "nickname": "小哈利",
                "grade": "五年级",
                "class_name": "魔法班",
                "school": "霍格沃茨小学",
                "avatar_url": "",
                "magic_level": 2,
                "total_points": 150,
                "linked_at": "2026-01-01T00:00:00Z"
            }
        ]
    }

@app.get("/api/v1/parent/conversations/{student_id}")
async def parent_get_conversations(student_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """家长获取学生对话记录"""
    payload = verify_token(credentials)

    if payload.get("role") != "parent":
        raise HTTPException(status_code=403, detail="权限不足")

    return {
        "success": True,
        "data": [
            {
                "conversation_id": "conv_1",
                "student_id": student_id,
                "student_name": "测试小魔法师",
                "message_count": 8,
                "last_message": "这道题考查的是加减法的应用哦！",
                "last_message_time": datetime.utcnow().isoformat() + "Z",
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        ]
    }

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "魔法课桌 Mock API"
    }

# ============ 启动说明 ============
if __name__ == "__main__":
    import uvicorn

    print("""
    ╔═════════════════════════════════════════════════════════╗
    ║          魔法课桌学习助手 - Mock API 服务器           ║
    ╚═════════════════════════════════════════════════════════╝

    📡 服务地址: http://localhost:3000
    📖 API 文档: http://localhost:3000/docs
    🔧 健康检查: http://localhost:3000/api/v1/health

    📝 测试账号:
       学生: student / password123
       家长: parent / password123

    ✨ 服务器启动中...
    """)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3000,
        log_level="info"
    )
