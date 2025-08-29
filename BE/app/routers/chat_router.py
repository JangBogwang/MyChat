from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from app.dto.chat_dto import ChatRequest, ChatResponse
from app.service.chat_service import ChatService
from app.service.rag_service import RAGService
from app.service.llm_service import LLMService
from app.config.DBconfig import get_async_db

router = APIRouter(prefix="/api/chat")

# 의존성 주입 설정
def get_llm_service() -> LLMService:
    return LLMService()

async def get_rag_service() -> AsyncGenerator[RAGService, None]:
    rag_service = await RAGService.create()
    try:
        yield rag_service
    finally:
        await rag_service.aclose()

def get_chat_service(
    rag_service: RAGService = Depends(get_rag_service),
    llm_service: LLMService = Depends(get_llm_service)
) -> ChatService:
    return ChatService(rag_service=rag_service, llm_service=llm_service)

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_async_db),
    chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.process_chat(request, db)

