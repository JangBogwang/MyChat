from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, constr


# ───────────────────────────────
# 1. 요청 DTO (클라이언트 → 서버)
# ───────────────────────────────
class ChatRequest(BaseModel):
    user_id: constr(strip_whitespace=True, min_length=1) = Field(..., description="사용자 식별자")
    message: str = Field(..., description="사용자 질문 또는 메시지")


# ───────────────────────────────
# 2. 내부 로직 및 DB용 모델
# ───────────────────────────────
class ChatBase(BaseModel):
    user_id: str
    request_msg: str
    response_msg: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True


# ───────────────────────────────
# 3. 응답 DTO (서버 → 클라이언트)
# ───────────────────────────────
class ChatResponse(ChatBase):
    pass


# ───────────────────────────────
# 4. 공통 응답 포맷
# ───────────────────────────────
class CommonResponse(BaseModel):
    code: str = Field(..., example="SUCCESS")
    message: str = Field(..., example="처리가 완료되었습니다.")
    data: Optional[ChatResponse] = None
