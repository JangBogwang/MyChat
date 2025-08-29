# service/chat_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.dto.chat_dto import ChatRequest, ChatResponse
from app.service.llm_service import LLMService
from app.service.rag_service import RAGService
from app.utils.gpt_client import get_embedding
from app.repository import chat_repository  # ⬅️ 리포지토리 임포트
from app.config.logging_config import logger

class ChatService:
    def __init__(self, rag_service: RAGService, llm_service: LLMService):
        self.rag_service = rag_service
        self.llm_service = llm_service

    async def process_chat(
        self,
        request: ChatRequest,
        db: AsyncSession,
    ) -> ChatResponse:
        logger.info(f"[ChatService] 사용자 ID({request.user_id})로부터 채팅 요청 접수: '{request.message}'")
  
        # 1. 사용자 최근 대화 기록 조회 (DB 조회)
        try:
            recent_chats = await chat_repository.get_recent_chats_by_user_id(db, request.user_id)
            user_chat_history = [f"Q: {c.request}\nA: {c.response}" for c in recent_chats]
            logger.info(f"사용자 ID({request.user_id})의 최근 대화 {len(user_chat_history)}개 조회 완료")
        except Exception as e:
            logger.error(f"사용자 ID({request.user_id})의 최근 대화 조회 실패: {e}")
            user_chat_history = []

        # 2. 관련 대화 기록 검색 (RAG)
        try:
            input_vector = await get_embedding(request.message)
            retrieved_context = await self.rag_service.get_chat(input_vector)
        except Exception as e:
            logger.error(f"벡터 DB 조회 실패: {e}")
            retrieved_context = []

        # 3. LLM 호출 (OpenAI)
        try:
            final_response = await self.llm_service.generate(request.message, retrieved_context=retrieved_context, user_chat_history=user_chat_history)
        except Exception as e:
            logger.error(f"LLM 호출 실패: {e}")
            final_response = "죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다."

        # 4. DB 저장을 위해 리포지토리 함수 호출
        chat = await chat_repository.save_chat_message(
            db=db,
            user_id=request.user_id,
            request=request.message,
            response=final_response
        )

        # 5. DTO 반환
        response_dto = ChatResponse(
            user_id=chat.user_id,
            request_msg=chat.request,
            response_msg=chat.response,
            created_at=chat.timestamp,
        )

        logger.info(f"[ChatService] 최종 응답 반환: '{response_dto.response_msg}'")
        return response_dto
