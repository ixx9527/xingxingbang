"""
星星榜 - 数据库模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """家长用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    nickname = Column(String(50))
    avatar = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    children = relationship("Child", back_populates="parent", cascade="all, delete-orphan")
    invite_codes = relationship("InviteCode", back_populates="creator")


class Child(Base):
    """小孩信息表"""
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    avatar = Column(String(255))
    birth_date = Column(String(10))
    gender = Column(String(10))
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    parent = relationship("User", back_populates="children")
    behaviors = relationship("ChildBehavior", back_populates="child", cascade="all, delete-orphan")
    records = relationship("Record", back_populates="child", cascade="all, delete-orphan")
    daily_scores = relationship("DailyScore", back_populates="child", cascade="all, delete-orphan")


class Behavior(Base):
    """行为模板表（管理员预设 + 用户自定义）"""
    __tablename__ = "behaviors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    points = Column(Float, default=0)
    category = Column(String(50), index=True)
    icon = Column(String(10))
    description = Column(String(255))
    is_system = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # null=管理员预设，有值=用户私有
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    child_behaviors = relationship("ChildBehavior", back_populates="behavior")
    records = relationship("Record", back_populates="behavior")
    owner = relationship("User")


class ChildBehavior(Base):
    """小孩的行为配置表"""
    __tablename__ = "child_behaviors"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    behavior_id = Column(Integer, ForeignKey("behaviors.id"), nullable=False)
    custom_points = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    child = relationship("Child", back_populates="behaviors")
    behavior = relationship("Behavior", back_populates="child_behaviors")


class Record(Base):
    """打卡记录表"""
    __tablename__ = "records"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    behavior_id = Column(Integer, ForeignKey("behaviors.id"), nullable=False)
    points = Column(Float, nullable=False)
    note = Column(Text)
    record_type = Column(String(20), default="manual")  # auto/manual/deduct
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    # 关系
    child = relationship("Child", back_populates="records")
    behavior = relationship("Behavior", back_populates="records")


class DailyScore(Base):
    """每日积分汇总"""
    __tablename__ = "daily_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    total_points = Column(Float, default=0)
    behavior_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    child = relationship("Child", back_populates="daily_scores")
    
    __table_args__ = (
        Index('idx_child_date', 'child_id', 'date'),
    )


class Level(Base):
    """等级配置表"""
    __tablename__ = "levels"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    name_en = Column(String(50))
    min_points = Column(Float, nullable=False)
    icon = Column(String(10))
    planet = Column(String(50))
    color = Column(String(20))


class InviteCode(Base):
    """邀请码表"""
    __tablename__ = "invite_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    max_uses = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    note = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    creator = relationship("User", back_populates="invite_codes")


class Reward(Base):
    """奖励/兑换商品表"""
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    points_required = Column(Float, nullable=False)
    description = Column(String(255))
    icon = Column(String(10))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class Redemption(Base):
    """兑换记录表"""
    __tablename__ = "redemptions"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    points_spent = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending/fulfilled/cancelled
    created_at = Column(DateTime, default=datetime.now)