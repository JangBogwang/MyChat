from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .Settings import settings # 설정 객체 임포트

# 비동기식 MySQL URL (aiomysql 사용)
ASYNC_SQLALCHEMY_DATABASE_URL = (
    f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# 비동기식 엔진 및 세션
async_engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL,
    echo=True,         # SQL 출력 (디버깅용)
    pool_size=10,      # 연결 풀 설정
    max_overflow=20
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ORM 모델의 기본 클래스
Base = declarative_base()

# 비동기식 DB 세션 의존성 함수
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
