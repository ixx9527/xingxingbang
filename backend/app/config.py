"""
星星榜 - 配置
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "星星榜"
    APP_VERSION: str = "1.0.0"
    
    # 安全配置
    SECRET_KEY: str = "changeme-secret-key-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30天
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 刷新token有效期7天
    
    # 数据库
    DATABASE_URL: str = "sqlite:///./data/xingxingbang.db"
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()