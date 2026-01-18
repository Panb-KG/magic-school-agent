"""
多用户架构 API
提供用户认证、会话管理、家长功能等 API 端点
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import logging

from auth.auth_utils import verify_token, hash_password
from auth.user_manager import user_manager
from auth.permissions import check_student_access
from storage.session import session_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="魔法学校学习管理系统 API",
    description="支持多用户、家长管理、长期记忆的学习管理系统",
    version="2.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Pydantic 模型
# ============================================

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str
    student_name: Optional[str] = None
    grade: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class RewardPointsRequest(BaseModel):
    student_id: str
    points: int
    reason: str

class ModifyHomeworkRequest(BaseModel):
    student_id: str
    homework_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None

class ApproveHomeworkRequest(BaseModel):
    student_id: str
    homework_id: int
    approved: bool
    comment: Optional[str] = None

class LinkStudentRequest(BaseModel):
    student_username: str
    relationship: str

# ============================================
# 依赖项：认证
# ============================================

async def get_current_user(authorization: str = Header(...)):
    """从 Authorization header 获取当前用户信息"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")
    
    token = authorization[7:]  # 移除 "Bearer " 前缀
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="无效或过期的令牌")
    
    return {
        "user_id": payload.get("user_id"),
        "role": payload.get("role"),
        "exp": payload.get("exp")
    }

# ============================================
# 认证相关 API
# ============================================

@app.post("/api/auth/register", tags=["认证"])
async def register(request: RegisterRequest):
    """用户注册"""
    result = user_manager.register_user(
        username=request.username,
        password=request.password,
        role=request.role,
        student_name=request.student_name,
        grade=request.grade
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@app.post("/api/auth/login", tags=["认证"])
async def login(request: LoginRequest):
    """用户登录"""
    result = user_manager.login_user(
        username=request.username,
        password=request.password
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("error"))
    
    return result

@app.get("/api/auth/me", tags=["认证"])
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    user_info = user_manager.get_user_info(current_user["user_id"])
    if not user_info:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return user_info

# ============================================
# 家长功能 API
# ============================================

@app.get("/api/parent/students", tags=["家长功能"])
async def get_parent_students(current_user: dict = Depends(get_current_user)):
    """获取家长关联的学生列表"""
    if current_user["role"] != "parent":
        raise HTTPException(status_code=403, detail="只有家长可以使用此功能")
    
    students = user_manager.get_parent_students(current_user["user_id"])
    return {"students": students}

@app.post("/api/parent/link-student", tags=["家长功能"])
async def link_student(
    request: LinkStudentRequest,
    current_user: dict = Depends(get_current_user)
):
    """家长关联学生"""
    if current_user["role"] != "parent":
        raise HTTPException(status_code=403, detail="只有家长可以使用此功能")
    
    result = user_manager.link_parent_student(
        parent_id=current_user["user_id"],
        student_id=request.student_username,  # 注意：这里需要先获取 student_id
        relationship=request.relationship
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@app.post("/api/parent/reward-points", tags=["家长功能"])
async def reward_points(
    request: RewardPointsRequest,
    current_user: dict = Depends(get_current_user)
):
    """家长给学生奖励积分"""
    if current_user["role"] != "parent":
        raise HTTPException(status_code=403, detail="只有家长可以使用此功能")
    
    # 检查家长是否有权访问该学生
    if not check_student_access(current_user["user_id"], current_user["role"], request.student_id):
        raise HTTPException(status_code=403, detail="无权访问该学生")
    
    from storage.database.db import get_engine
    from sqlalchemy import text
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 添加积分记录
            conn.execute(text("""
                INSERT INTO point_records (student_id, points, reason, source)
                VALUES (:student_id, :points, :reason, 'parent_reward')
            """), {
                "student_id": request.student_id,
                "points": request.points,
                "reason": request.reason
            })
            
            # 更新学生总积分
            result = conn.execute(text("""
                UPDATE students
                SET total_points = total_points + :points
                WHERE student_id = :student_id
                RETURNING total_points
            """), {
                "student_id": request.student_id,
                "points": request.points
            })
            
            conn.commit()
            
            new_points = result.scalar()
            
            return {
                "success": True,
                "message": f"成功奖励 {request.points} 积分",
                "new_total_points": new_points
            }
    except Exception as e:
        logger.error(f"奖励积分失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/parent/homework/{homework_id}", tags=["家长功能"])
async def modify_homework(
    homework_id: int,
    request: ModifyHomeworkRequest,
    current_user: dict = Depends(get_current_user)
):
    """家长修改学生作业"""
    if current_user["role"] != "parent":
        raise HTTPException(status_code=403, detail="只有家长可以使用此功能")
    
    # 检查家长是否有权访问该学生
    if not check_student_access(current_user["user_id"], current_user["role"], request.student_id):
        raise HTTPException(status_code=403, detail="无权访问该学生")
    
    from storage.database.db import get_engine
    from sqlalchemy import text
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            update_fields = []
            params = {
                "student_id": request.student_id,
                "homework_id": homework_id
            }
            
            if request.title is not None:
                update_fields.append("title = :title")
                params["title"] = request.title
            
            if request.description is not None:
                update_fields.append("description = :description")
                params["description"] = request.description
            
            if request.due_date is not None:
                update_fields.append("due_date = :due_date")
                params["due_date"] = request.due_date
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="没有需要修改的内容")
            
            update_fields.append("updated_at = NOW()")
            
            sql = f"""
                UPDATE homework
                SET {', '.join(update_fields)}
                WHERE homework_id = :homework_id AND student_id = :student_id
                RETURNING title
            """
            
            result = conn.execute(text(sql), params)
            conn.commit()
            
            title = result.scalar()
            if title:
                return {"success": True, "message": f"作业修改成功：{title}"}
            else:
                raise HTTPException(status_code=404, detail="未找到指定的作业")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改作业失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/parent/homework/{homework_id}/approve", tags=["家长功能"])
async def approve_homework(
    homework_id: int,
    request: ApproveHomeworkRequest,
    current_user: dict = Depends(get_current_user)
):
    """家长审核学生作业"""
    if current_user["role"] != "parent":
        raise HTTPException(status_code=403, detail="只有家长可以使用此功能")
    
    # 检查家长是否有权访问该学生
    if not check_student_access(current_user["user_id"], current_user["role"], request.student_id):
        raise HTTPException(status_code=403, detail="无权访问该学生")
    
    from storage.database.db import get_engine
    from sqlalchemy import text
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 更新作业审核状态
            conn.execute(text("""
                UPDATE homework
                SET 
                    parent_approved = :approved,
                    parent_comment = :comment,
                    parent_approved_at = NOW(),
                    approved_by = :parent_id
                WHERE homework_id = :homework_id AND student_id = :student_id
                RETURNING title
            """), {
                "approved": request.approved,
                "comment": request.comment,
                "parent_id": current_user["user_id"],
                "homework_id": homework_id,
                "student_id": request.student_id
            })
            
            conn.commit()
            
            row = conn.execute(text("SELECT title FROM homework WHERE homework_id = :homework_id"), 
                             {"homework_id": homework_id}).fetchone()
            
            if row:
                status = "批准" if request.approved else "未批准"
                message = f"作业【{row[0]}】已{status}"
                if request.comment:
                    message += f"，家长评论：{request.comment}"
                return {"success": True, "message": message}
            else:
                raise HTTPException(status_code=404, detail="未找到指定的作业")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"审核作业失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# 会话管理 API
# ============================================

@app.get("/api/session/thread", tags=["会话管理"])
async def get_thread_id(current_user: dict = Depends(get_current_user)):
    """获取用户的 thread_id（用于 Agent 对话）"""
    thread_id = session_manager.get_or_create_session(current_user["user_id"])
    return {
        "thread_id": thread_id,
        "user_id": current_user["user_id"],
        "role": current_user["role"]
    }

# ============================================
# 健康检查
# ============================================

@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "魔法学校学习管理系统",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
