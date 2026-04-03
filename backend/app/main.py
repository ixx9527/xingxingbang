"""
星星榜 - FastAPI 主应用
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

from app.config import settings
from app.database import get_db, create_tables
from app import models, crud, schemas
from app.security import (
    verify_password, get_password_hash, create_access_token, 
    verify_token, get_current_user
)

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="儿童成长打卡系统"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 生命周期事件 ==========

@app.on_event("startup")
def startup_event():
    create_tables()
    # 初始化默认数据
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        crud.init_default_data(db)
    finally:
        db.close()


# ========== 健康检查 ==========

@app.get("/health", response_model=schemas.HealthResponse)
def health_check():
    return schemas.HealthResponse(status="ok", version=settings.APP_VERSION)


# ========== 认证接口 ==========

@app.post("/api/auth/register", response_model=schemas.Token)
def register(req: schemas.UserCreate, db: Session = Depends(get_db)):
    """用户注册（需要邀请码）"""
    # 验证邀请码
    try:
        invite = crud.verify_invite_code(db, req.invite_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 检查用户名
    if crud.get_user_by_username(db, req.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    user = crud.create_user(db, req.username, req.password, req.nickname)
    
    # 使用邀请码
    crud.use_invite_code(db, invite)
    
    # 生成 Token
    token = create_access_token({"sub": str(user.id), "username": user.username})
    
    return schemas.Token(access_token=token)


@app.post("/api/auth/login", response_model=schemas.Token)
def login(req: schemas.UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = crud.get_user_by_username(db, req.username)
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    token = create_access_token({"sub": str(user.id), "username": user.username})
    return schemas.Token(access_token=token)


# ========== 邀请码接口 ==========

@app.get("/api/invite-codes", response_model=List[schemas.InviteCodeResponse])
def list_invite_codes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取我的邀请码列表"""
    return crud.get_user_invite_codes(db, current_user["id"])


@app.post("/api/invite-codes", response_model=schemas.InviteCodeResponse)
def create_invite_code(
    req: schemas.InviteCodeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """生成邀请码"""
    code = crud.create_invite_code(
        db, current_user["id"], 
        req.max_uses, req.days_valid, req.note
    )
    return code


@app.delete("/api/invite-codes/{code_id}")
def delete_invite_code(
    code_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除邀请码"""
    if not crud.delete_invite_code(db, code_id, current_user["id"]):
        raise HTTPException(status_code=404, detail="邀请码不存在")
    return {"message": "删除成功"}


# ========== 孩子接口 ==========

def get_child_or_404(db: Session, child_id: int, current_user: dict) -> models.Child:
    child = crud.get_child_by_id(db, child_id)
    if not child or child.user_id != current_user["id"]:
        raise HTTPException(status_code=404, detail="孩子不存在")
    return child


@app.get("/api/children", response_model=List[schemas.ChildResponse])
def list_children(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取孩子列表"""
    children = crud.get_children_by_user(db, current_user["id"])
    result = []
    for child in children:
        total = crud.get_total_points(db, child.id)
        streak = crud.get_streak_days(db, child.id)
        result.append(schemas.ChildResponse(
            id=child.id,
            name=child.name,
            birth_date=child.birth_date,
            gender=child.gender,
            avatar=child.avatar,
            total_points=total,
            streak_days=streak
        ))
    return result


@app.post("/api/children", response_model=schemas.ChildResponse)
def create_child(
    req: schemas.ChildCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """添加孩子"""
    child = crud.create_child(
        db, current_user["id"],
        req.name, req.birth_date, req.gender, req.avatar
    )
    return schemas.ChildResponse(
        id=child.id,
        name=child.name,
        birth_date=child.birth_date,
        gender=child.gender,
        avatar=child.avatar,
        total_points=0,
        streak_days=0
    )


@app.get("/api/children/{child_id}", response_model=schemas.ChildDetailResponse)
def get_child(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取孩子详情"""
    child = get_child_or_404(db, child_id, current_user)
    total = crud.get_total_points(db, child_id)
    streak = crud.get_streak_days(db, child_id)
    return schemas.ChildDetailResponse(
        id=child.id,
        name=child.name,
        birth_date=child.birth_date,
        gender=child.gender,
        avatar=child.avatar,
        total_points=total,
        streak_days=streak,
        created_at=child.created_at
    )


# ========== 行为接口 ==========

def is_admin(current_user: dict) -> bool:
    """判断是否为管理员"""
    return current_user.get("username") == "admin"

def behavior_to_response(behavior: models.Behavior) -> schemas.BehaviorResponse:
    """转换行为模型为响应，添加 is_admin 字段"""
    return schemas.BehaviorResponse(
        id=behavior.id,
        name=behavior.name,
        points=behavior.points,
        category=behavior.category,
        icon=behavior.icon,
        description=behavior.description,
        is_system=behavior.is_system,
        user_id=behavior.user_id,
        is_admin=behavior.user_id is None  # user_id=null 表示管理员预设
    )

@app.get("/api/behaviors", response_model=List[schemas.BehaviorResponse])
def list_behaviors(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取行为列表：管理员预设 + 用户私有行为"""
    behaviors = crud.get_all_behaviors(db, current_user["id"], category)
    return [behavior_to_response(b) for b in behaviors]


@app.post("/api/behaviors", response_model=schemas.BehaviorResponse)
def create_behavior(
    req: schemas.BehaviorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建行为：普通用户创建私有行为，管理员可创建预设行为"""
    # 管理员创建的预设行为 user_id=null，普通用户创建的私有行为 user_id=当前用户
    user_id = None if is_admin(current_user) else current_user["id"]
    behavior = crud.create_behavior(
        db, req.name, req.points, req.category, req.icon, req.description, user_id
    )
    return behavior_to_response(behavior)


@app.put("/api/behaviors/{behavior_id}", response_model=schemas.BehaviorResponse)
def update_behavior(
    behavior_id: int,
    req: schemas.BehaviorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新行为：只能编辑自己的私有行为，管理员可编辑预设行为"""
    behavior = crud.update_behavior(
        db, behavior_id,
        user_id=current_user["id"],
        is_admin=is_admin(current_user),
        **req.dict()
    )
    if not behavior:
        raise HTTPException(status_code=400, detail="无法编辑此行为（系统预设或非本人创建）")
    return behavior_to_response(behavior)


@app.delete("/api/behaviors/{behavior_id}")
def delete_behavior(
    behavior_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除行为：普通用户和管理员都能删除预设行为和自己的私有行为"""
    if not crud.delete_behavior(
        db, behavior_id,
        user_id=current_user["id"],
        is_admin=is_admin(current_user)
    ):
        raise HTTPException(status_code=400, detail="无法删除此行为（非本人创建）")
    return {"message": "删除成功"}


@app.post("/api/behaviors/reset")
def reset_behaviors(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """重置预设行为到默认状态（仅管理员）"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="只有管理员可以执行此操作")
    count = crud.reset_behaviors(db)
    return {"message": f"已重置 {count} 个预设行为"}


# ========== 打卡接口 ==========

@app.post("/api/children/{child_id}/records", response_model=schemas.RecordResponse)
def create_record(
    child_id: int,
    req: schemas.RecordCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """添加打卡记录"""
    child = get_child_or_404(db, child_id, current_user)
    behavior = crud.get_behavior_by_id(db, req.behavior_id)
    if not behavior:
        raise HTTPException(status_code=404, detail="行为不存在")
    
    record = crud.create_record(
        db, child_id, req.behavior_id, req.points, req.note, req.record_type
    )
    
    return schemas.RecordResponse(
        id=record.id,
        behavior_id=behavior.id,
        behavior_name=behavior.name,
        behavior_icon=behavior.icon,
        points=record.points,
        note=record.note,
        record_type=record.record_type,
        created_at=record.created_at
    )


@app.get("/api/children/{child_id}/records", response_model=List[schemas.RecordResponse])
def get_records(
    child_id: int,
    date_from: str = None,
    date_to: str = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取打卡记录"""
    child = get_child_or_404(db, child_id, current_user)
    records = crud.get_child_records(db, child_id, date_from, date_to, limit)
    
    result = []
    for r in records:
        behavior = r.behavior
        result.append(schemas.RecordResponse(
            id=r.id,
            behavior_id=r.behavior_id,
            behavior_name=behavior.name if behavior else "未知",
            behavior_icon=behavior.icon if behavior else "",
            points=r.points,
            note=r.note,
            record_type=r.record_type,
            created_at=r.created_at
        ))
    return result


# ========== 积分统计 ==========

@app.get("/api/children/{child_id}/scores", response_model=schemas.ScoreStats)
def get_scores(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取积分统计"""
    child = get_child_or_404(db, child_id, current_user)
    
    today_points = crud.get_today_points(db, child_id)
    total_points = crud.get_total_points(db, child_id)
    streak_days = crud.get_streak_days(db, child_id)
    behavior_stats = crud.get_behavior_stats(db, child_id)
    
    return schemas.ScoreStats(
        today_points=today_points,
        total_points=total_points,
        streak_days=streak_days,
        behavior_stats=behavior_stats
    )


@app.get("/api/children/{child_id}/scores/chart", response_model=schemas.ScoreChart)
def get_score_chart(
    child_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取积分趋势图"""
    child = get_child_or_404(db, child_id, current_user)
    return crud.get_score_chart(db, child_id, days)


# ========== 等级接口 ==========

@app.get("/api/children/{child_id}/level", response_model=schemas.ChildLevelResponse)
def get_child_level(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取孩子等级信息"""
    child = get_child_or_404(db, child_id, current_user)
    level_info = crud.get_child_level_info(db, child_id)
    
    return schemas.ChildLevelResponse(
        current_level=level_info["current_level"],
        next_level=level_info["next_level"],
        total_points=level_info["total_points"],
        progress_percent=level_info["progress_percent"],
        points_to_next=level_info["points_to_next"],
        leveled_up_today=level_info["leveled_up_today"]
    )


# ========== 运行入口 ==========

@app.post("/api/user/change-password")
def change_password(
    req: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """修改密码"""
    user = crud.get_user_by_id(db, current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not verify_password(req["old_password"], user.password_hash):
        raise HTTPException(status_code=400, detail="当前密码错误")
    
    user.password_hash = get_password_hash(req["new_password"])
    db.commit()
    
    return {"message": "密码修改成功"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)