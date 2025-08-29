from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

logger = logging.getLogger("uvicorn")

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """ 요청을 로깅하고 응답 시간을 측정하는 미들웨어 """
        start_time = time.time()

        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"[{request.method}] {request.url} - Time taken: {process_time:.2f}s")
        return response

def setup_middleware(app):
    """ FastAPI 애플리케이션에 미들웨어 추가하는 함수 """
    app.add_middleware(CustomMiddleware)

    # CORS 설정 (로컬에서 Spring Boot & Airflow 통신만 허용)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Spring Boot & Airflow
        allow_credentials=True,
        allow_methods=["*"],  # 모든 HTTP 메서드 허용
        allow_headers=["*"],  # 모든 헤더 허용
    )
