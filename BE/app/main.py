from fastapi import FastAPI
from app.routers import chat_router
from app.config.middleware import setup_middleware

# DB 초기화 관련 임포트
from app.config.DBconfig import async_engine, Base
from app.models import chat_model

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 데이터베이스 테이블을 생성합니다.
    """
    async with async_engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # 필요시 기존 테이블 삭제
        await conn.run_sync(Base.metadata.create_all)

# 미들웨어 설정 (라우터 등록 전에 해야 함)
setup_middleware(app)

# 라우터 포함
app.include_router(chat_router.router, tags=["chat"])
