"""
星星榜 - Pydantic 数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 用户相关 ==========

class UserCreate(BaseModel):
    username: str
    password: str
    nickname: str
    invite_code: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str]
    avatar: Optional[str]
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    password_hash: str


# ========== 孩子相关 ==========

class ChildCreate(BaseModel):
    name: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    avatar: Optional[str] = None


class ChildResponse(BaseModel):
    id: int
    name: str
    birth_date: Optional[str]
    gender: Optional[str]
    avatar: Optional[str]
    total_points: float = 0
    streak_days: int = 0
    
    class Config:
        from_attributes = True


class ChildDetailResponse(ChildResponse):
    created_at: datetime


# ========== 行为相关 ==========

class BehaviorCreate(BaseModel):
    name: str
    points: float
    category: str
    icon: str = ""
    description: str = ""


class BehaviorResponse(BaseModel):
    id: int
    name: str
    points: float
    category: str
    icon: str
    description: str
    is_system: bool
    
    class Config:
        from_attributes = True


class ChildBehaviorUpdate(BaseModel):
    custom_points: Optional[float] = None
    is_active: bool = True


class ChildBehaviorResponse(BaseModel):
    id: int
    behavior_id: int
    name: str
    points: float
    category: str
    icon: str
    is_active: bool
    has_custom: bool = False


# ========== 打卡记录 ==========

class RecordCreate(BaseModel):
    behavior_id: int
    points: float
    note: str = ""
    record_type: str = "manual"


class RecordResponse(BaseModel):
    id: int
    behavior_id: int
    behavior_name: str
    behavior_icon: str
    points: float
    note: Optional[str]
    record_type: str
    created_at: datetime


# ========== 积分统计 ==========

class ScoreStats(BaseModel):
    today_points: float
    total_points: float
    streak_days: int
    behavior_stats: List[dict] = []


class ScoreChart(BaseModel):
    labels: List[str]
    values: List[float]


# ========== 等级相关 ==========

class LevelResponse(BaseModel):
    level: int
    name: str
    name_en: str
    icon: str
    planet: str
    color: str
    min_points: float
    
    class Config:
        from_attributes = True


class ChildLevelResponse(BaseModel):
    current_level: LevelResponse
    next_level: Optional[LevelResponse]
    total_points: float
    progress_percent: float
    points_to_next: float
    leveled_up_today: bool = False


# ========== 邀请码 ==========

class InviteCodeCreate(BaseModel):
    max_uses: int = 1
    days_valid: int = 30
    note: str = ""


class InviteCodeResponse(BaseModel):
    id: int
    code: str
    max_uses: int
    used_count: int
    expires_at: Optional[datetime]
    is_active: bool
    note: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 奖励相关 ==========

class RewardCreate(BaseModel):
    name: str
    points_required: float
    description: str = ""
    icon: str = ""


class RewardResponse(BaseModel):
    id: int
    name: str
    points_required: float
    description: str
    icon: str
    is_active: bool
    
    class Config:
        from_attributes = True


class RedemptionResponse(BaseModel):
    id: int
    reward_name: str
    reward_icon: str
    points_spent: float
    status: str
    created_at: datetime


# ========== 认证相关 ==========

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None


# ========== 通用 ==========

class MsgResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str