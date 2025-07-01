from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dto.chat_dto import ChatRequest, CommonResponse
from service.chat_service import ChatService
from config.DBconfig import get_async_db

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
service = ChatService()

@router.post("", response_model=CommonResponse)
async def send_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_async_db)
):
    response = await service.process_chat(request, db)

    return CommonResponse(
        code="200",
        message="응답이 성공적으로 생성되었습니다.",
        data=response
    )
