"""
星星榜 - 业务逻辑层
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple
import random
import string

from app import models, schemas
from app.security import get_password_hash, verify_password


# ========== 用户相关 ==========

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, username: str, password: str, nickname: str) -> models.User:
    password_hash = get_password_hash(password)
    user = models.User(
        username=username,
        password_hash=password_hash,
        nickname=nickname
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ========== 孩子相关 ==========

def get_children_by_user(db: Session, user_id: int) -> List[models.Child]:
    return db.query(models.Child).filter(models.Child.user_id == user_id).all()


def get_child_by_id(db: Session, child_id: int) -> Optional[models.Child]:
    return db.query(models.Child).filter(models.Child.id == child_id).first()


def create_child(db: Session, user_id: int, name: str, birth_date: str = None, 
                  gender: str = None, avatar: str = None) -> models.Child:
    child = models.Child(
        user_id=user_id,
        name=name,
        birth_date=birth_date,
        gender=gender,
        avatar=avatar
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


def update_child(db: Session, child_id: int, **kwargs) -> Optional[models.Child]:
    child = db.query(models.Child).filter(models.Child.id == child_id).first()
    if not child:
        return None
    for key, value in kwargs.items():
        if hasattr(child, key) and value is not None:
            setattr(child, key, value)
    db.commit()
    db.refresh(child)
    return child


def delete_child(db: Session, child_id: int) -> bool:
    child = db.query(models.Child).filter(models.Child.id == child_id).first()
    if not child:
        return False
    db.delete(child)
    db.commit()
    return True


# ========== 行为相关 ==========

def get_all_behaviors(db: Session, user_id: int = None, category: str = None) -> List[models.Behavior]:
    """获取行为列表：管理员预设(user_id=null) + 用户私有行为"""
    query = db.query(models.Behavior)
    # 管理员预设行为(user_id=null) + 用户私有行为(user_id=当前用户)
    if user_id:
        query = query.filter(
            (models.Behavior.user_id == None) | (models.Behavior.user_id == user_id)
        )
    if category:
        query = query.filter(models.Behavior.category == category)
    return query.all()


def get_behavior_by_id(db: Session, behavior_id: int) -> Optional[models.Behavior]:
    return db.query(models.Behavior).filter(models.Behavior.id == behavior_id).first()


def create_behavior(db: Session, name: str, points: float, category: str,
                    icon: str = "", description: str = "", user_id: int = None) -> models.Behavior:
    """创建行为：普通用户创建私有行为(user_id=用户ID)，管理员可创建预设行为(user_id=null)"""
    behavior = models.Behavior(
        name=name,
        points=points,
        category=category,
        icon=icon,
        description=description,
        is_system=False,
        user_id=user_id
    )
    db.add(behavior)
    db.commit()
    db.refresh(behavior)
    return behavior


def update_behavior(db: Session, behavior_id: int, user_id: int = None, is_admin: bool = False, **kwargs) -> Optional[models.Behavior]:
    """更新行为：普通用户只能编辑自己的私有行为，管理员可编辑所有行为"""
    behavior = db.query(models.Behavior).filter(models.Behavior.id == behavior_id).first()
    if not behavior:
        return None
    # 管理员可以编辑任何行为
    if is_admin:
        for key, value in kwargs.items():
            if hasattr(behavior, key) and value is not None:
                setattr(behavior, key, value)
        db.commit()
        db.refresh(behavior)
        return behavior
    # 普通用户：只能编辑自己的私有行为(user_id=当前用户)
    if behavior.user_id is None:
        return None  # 不能编辑预设行为
    if behavior.user_id != user_id:
        return None  # 不能编辑他人的行为
    for key, value in kwargs.items():
        if hasattr(behavior, key) and value is not None:
            setattr(behavior, key, value)
    db.commit()
    db.refresh(behavior)
    return behavior


def delete_behavior(db: Session, behavior_id: int, user_id: int = None, is_admin: bool = False) -> bool:
    """删除行为：普通用户和管理员都能删除预设行为和自己的私有行为"""
    behavior = db.query(models.Behavior).filter(models.Behavior.id == behavior_id).first()
    if not behavior:
        return False
    # 管理员可以删除任何行为
    if is_admin:
        db.delete(behavior)
        db.commit()
        return True
    # 普通用户：可以删除预设行为(user_id=null)和自己的私有行为
    if behavior.user_id is not None and behavior.user_id != user_id:
        return False  # 不能删除他人的私有行为
    db.delete(behavior)
    db.commit()
    return True


def reset_behaviors(db: Session) -> int:
    """重置预设行为到默认状态，返回重置的数量"""
    # 删除所有预设行为(user_id=null)
    deleted = db.query(models.Behavior).filter(models.Behavior.user_id == None).delete()
    db.commit()
    # 重新创建默认行为
    for b in DEFAULT_BEHAVIORS:
        behavior = models.Behavior(**b, is_system=True, user_id=None)
        db.add(behavior)
    db.commit()
    return deleted + len(DEFAULT_BEHAVIORS)


# ========== 打卡记录 ==========

def create_record(db: Session, child_id: int, behavior_id: int, points: float,
                   note: str = "", record_type: str = "manual") -> models.Record:
    record = models.Record(
        child_id=child_id,
        behavior_id=behavior_id,
        points=points,
        note=note,
        record_type=record_type
    )
    db.add(record)
    
    # 更新每日汇总
    today = date.today().isoformat()
    daily_score = db.query(models.DailyScore).filter(
        models.DailyScore.child_id == child_id,
        models.DailyScore.date == today
    ).first()
    
    if not daily_score:
        daily_score = models.DailyScore(
            child_id=child_id,
            date=today,
            total_points=0,
            behavior_count=0
        )
        db.add(daily_score)
    
    daily_score.total_points += points
    daily_score.behavior_count += 1
    
    db.commit()
    db.refresh(record)
    return record


def get_child_records(db: Session, child_id: int, date_from: str = None, 
                       date_to: str = None, limit: int = 50) -> List[models.Record]:
    query = db.query(models.Record).filter(models.Record.child_id == child_id)
    
    if date_from:
        query = query.filter(models.Record.created_at >= date_from)
    if date_to:
        query = query.filter(models.Record.created_at <= date_to + " 23:59:59")
    
    return query.order_by(models.Record.created_at.desc()).limit(limit).all()


# ========== 积分统计 ==========

def get_total_points(db: Session, child_id: int) -> float:
    result = db.query(func.sum(models.Record.points)).filter(
        models.Record.child_id == child_id
    ).scalar()
    return result or 0


def get_today_points(db: Session, child_id: int) -> float:
    today = date.today().isoformat()
    score = db.query(models.DailyScore).filter(
        models.DailyScore.child_id == child_id,
        models.DailyScore.date == today
    ).first()
    return score.total_points if score else 0


def get_streak_days(db: Session, child_id: int) -> int:
    scores = db.query(models.DailyScore).filter(
        models.DailyScore.child_id == child_id,
        models.DailyScore.total_points > 0
    ).order_by(models.DailyScore.date.desc()).all()
    
    if not scores:
        return 0
    
    streak = 0
    today = date.today()
    
    for i in range(len(scores)):
        expected_date = (today - timedelta(days=i)).isoformat()
        if i < len(scores) and scores[i].date == expected_date:
            streak += 1
        else:
            break
    
    return streak


def get_behavior_stats(db: Session, child_id: int) -> List[dict]:
    results = db.query(
        models.Behavior.category,
        func.sum(models.Record.points)
    ).join(models.Record).filter(
        models.Record.child_id == child_id
    ).group_by(models.Behavior.category).all()
    
    return [{"category": r[0], "points": float(r[1] or 0)} for r in results]


def get_score_chart(db: Session, child_id: int, days: int = 30) -> dict:
    scores = db.query(models.DailyScore).filter(
        models.DailyScore.child_id == child_id
    ).order_by(models.DailyScore.date.desc()).limit(days).all()
    
    scores = list(reversed(scores))
    
    return {
        "labels": [s.date for s in scores],
        "values": [s.total_points for s in scores]
    }


# ========== 等级相关 ==========

DEFAULT_LEVELS = [
    {"level": 1, "name": "萌芽宝宝", "name_en": "Sprout", "min_points": 0, "icon": "🌱", "planet": "泥土星球", "color": "#8B4513"},
    {"level": 2, "name": "小小星", "name_en": "Tiny Star", "min_points": 50, "icon": "🌟", "planet": "迷你星", "color": "#FFD700"},
    {"level": 3, "name": "闪亮星", "name_en": "Shining Star", "min_points": 150, "icon": "💫", "planet": "流星星", "color": "#FF69B4"},
    {"level": 4, "name": "智慧星", "name_en": "Smart Star", "min_points": 300, "icon": "🧠", "planet": "知识星", "color": "#4169E1"},
    {"level": 5, "name": "勇敢星", "name_en": "Brave Star", "min_points": 500, "icon": "⚡", "planet": "勇气星", "color": "#FF8C00"},
    {"level": 6, "name": "全能星", "name_en": "Super Star", "min_points": 800, "icon": "🏆", "planet": "全能星", "color": "#9370DB"},
    {"level": 7, "name": "超级星", "name_en": "Hero Star", "min_points": 1200, "icon": "🚀", "planet": "太空星", "color": "#00CED1"},
    {"level": 8, "name": "传奇星", "name_en": "Legend Star", "min_points": 1800, "icon": "👑", "planet": "王者星", "color": "#FFD700"},
    {"level": 9, "name": "至尊星", "name_en": "Supreme Star", "min_points": 2500, "icon": "💎", "planet": "钻石星", "color": "#E0FFFF"},
    {"level": 10, "name": "宇宙星神", "name_en": "Cosmic God", "min_points": 3500, "icon": "🌌", "planet": "宇宙星", "color": "#4B0082"},
]


def get_current_level(points: float) -> dict:
    """根据积分获取当前等级"""
    for level in reversed(DEFAULT_LEVELS):
        if points >= level["min_points"]:
            return level
    return DEFAULT_LEVELS[0]


def get_next_level(current_level: int) -> Optional[dict]:
    """获取下一等级"""
    if current_level >= 10:
        return None
    return DEFAULT_LEVELS[current_level]


def get_child_level_info(db: Session, child_id: int) -> dict:
    """获取孩子等级信息"""
    total_points = get_total_points(db, child_id)
    current = get_current_level(total_points)
    next_level = get_next_level(current["level"])
    
    # 检查今天是否升级
    leveled_up_today = False
    # TODO: 需要记录升级历史
    
    if next_level:
        level_range = next_level["min_points"] - current["min_points"]
        progress = (total_points - current["min_points"]) / level_range * 100 if level_range > 0 else 100
        points_to_next = next_level["min_points"] - total_points
    else:
        progress = 100
        points_to_next = 0
    
    return {
        "current_level": current,
        "next_level": next_level,
        "total_points": total_points,
        "progress_percent": min(progress, 100),
        "points_to_next": max(points_to_next, 0),
        "leveled_up_today": leveled_up_today
    }


# ========== 邀请码相关 ==========

def generate_code(length: int = 6) -> str:
    """生成随机邀请码"""
    chars = string.digits + string.ascii_uppercase
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '').replace('L', '')
    return ''.join(random.choices(chars, k=length))


def create_invite_code(db: Session, user_id: int, max_uses: int = 1, 
                       days_valid: int = 30, note: str = "") -> models.InviteCode:
    code = generate_code()
    
    # 确保不重复
    while db.query(models.InviteCode).filter(models.InviteCode.code == code).first():
        code = generate_code()
    
    expires_at = datetime.now() + timedelta(days=days_valid) if days_valid > 0 else None
    
    invite = models.InviteCode(
        code=code,
        user_id=user_id,
        max_uses=max_uses,
        expires_at=expires_at,
        note=note
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


def verify_invite_code(db: Session, code: str) -> models.InviteCode:
    """验证邀请码"""
    invite = db.query(models.InviteCode).filter(
        models.InviteCode.code == code,
        models.InviteCode.is_active == True
    ).first()
    
    if not invite:
        raise ValueError("邀请码不存在")
    
    if invite.expires_at and invite.expires_at < datetime.now():
        raise ValueError("邀请码已过期")
    
    if invite.used_count >= invite.max_uses:
        raise ValueError("邀请码已达到使用上限")
    
    return invite


def use_invite_code(db: Session, invite: models.InviteCode):
    """使用邀请码"""
    invite.used_count += 1
    if invite.used_count >= invite.max_uses:
        invite.is_active = False
    db.commit()


def get_user_invite_codes(db: Session, user_id: int) -> List[models.InviteCode]:
    return db.query(models.InviteCode).filter(models.InviteCode.user_id == user_id).all()


def delete_invite_code(db: Session, code_id: int, user_id: int) -> bool:
    code = db.query(models.InviteCode).filter(
        models.InviteCode.id == code_id,
        models.InviteCode.user_id == user_id
    ).first()
    if not code:
        return False
    db.delete(code)
    db.commit()
    return True


# ========== 种子数据 ==========

DEFAULT_BEHAVIORS = [
    {"name": "阅读30分钟", "points": 3, "category": "学习", "icon": "📚"},
    {"name": "数学口算完成", "points": 2, "category": "学习", "icon": "🔢"},
    {"name": "数学口算错一题", "points": -1, "category": "学习", "icon": "❌"},
    {"name": "英语朗读", "points": 3, "category": "学习", "icon": "🔤"},
    {"name": "练琴30分钟", "points": 3, "category": "学习", "icon": "🎹"},
    {"name": "完成作业", "points": 5, "category": "学习", "icon": "✏️"},
    {"name": "早起不赖床", "points": 2, "category": "生活", "icon": "🌅"},
    {"name": "自己整理房间", "points": 3, "category": "生活", "icon": "🛏️"},
    {"name": "按时睡觉", "points": 2, "category": "生活", "icon": "😴"},
    {"name": "挑食/剩饭", "points": -2, "category": "生活", "icon": "🍚"},
    {"name": "主动收拾玩具", "points": 2, "category": "生活", "icon": "🧸"},
    {"name": "户外运动1小时", "points": 5, "category": "运动", "icon": "⚽"},
    {"name": "跳绳500个", "points": 3, "category": "运动", "icon": "🏃"},
    {"name": "游泳", "points": 5, "category": "运动", "icon": "🏊"},
    {"name": "帮妈妈做事", "points": 5, "category": "其他", "icon": "🤝"},
    {"name": "说脏话", "points": -5, "category": "其他", "icon": "🚫"},
    {"name": "发脾气", "points": -3, "category": "其他", "icon": "😤"},
]


def init_default_data(db: Session):
    """初始化默认数据"""
    # 初始化行为
    existing = db.query(models.Behavior).first()
    if not existing:
        for b in DEFAULT_BEHAVIORS:
            behavior = models.Behavior(**b, is_system=True)
            db.add(behavior)
        
        # 初始化等级
        for level in DEFAULT_LEVELS:
            lvl = models.Level(**level)
            db.add(lvl)
        
        db.commit()
    
    # 初始化默认管理员（如果不存在）
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        from app.security import get_password_hash
        admin = models.User(
            username="admin",
            nickname="管理员",
            password_hash=get_password_hash("admin123")
        )
        db.add(admin)
        db.commit()
        
        # 创建默认邀请码
        invite = models.InviteCode(
            code="admin001",
            user_id=admin.id,
            max_uses=-1,  # 无限
            used_count=0,
            is_active=True,
            note="管理员邀请码"
        )
        db.add(invite)
        db.commit()
        print("默认管理员初始化完成: admin / admin123")
    
    print("默认数据初始化完成")