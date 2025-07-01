# service/chat_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from model.chat_model import Chat
from dto.chat_dto import ChatRequest, ChatResponse
from utils.gpt_client import chat_completion  # ⬅️ 분리한 모듈 임포트
from service import LLM_service

llm_service = LLM_service()

class ChatService:
    async def process_chat(
        self,
        request: ChatRequest,
        db: AsyncSession,
    ) -> ChatResponse:

        # 1. GPT 호출
        gpt_response = await llm_service.generate(request.message)

        # 2. DB 저장
        chat = Chat(
            user_id=request.user_id,
            request_msg=request.message,
            response_msg=gpt_response,
        )
        
        db.add(chat)
        await db.commit()
        await db.refresh(chat)

        # 3. DTO 반환
        return ChatResponse(
            user_id=chat.user_id,
            request_msg=chat.request_msg,
            response_msg=chat.response_msg,
            created_at=chat.created_at,
        )
