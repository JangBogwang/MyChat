from fastapi import FastAPI
from routers import chat_router
from config.middleware import setup_middleware

app = FastAPI()

# 미들웨어 설정 (라우터 등록 전에 해야 함)
setup_middleware(app)

# 라우터 포함
app.include_router(chat_router.router, tags=["chat"])