import openai
from sqlalchemy.ext.asyncio import AsyncSession
from model.chat_model import Chat  # SQLAlchemy 모델
from dto.chat_dto import ChatRequest, ChatResponse

class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        # 1. GPT 호출
        gpt_response = await self._call_gpt(request.message)

        # 2. DB 저장
        chat = Chat(
            user_id=request.user_id,
            request_msg=request.message,
            response_msg=gpt_response
        )
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)

        # 3. 응답 반환
        return ChatResponse(
            user_id=chat.user_id,
            request_msg=chat.request_msg,
            response_msg=chat.response_msg,
            created_at=chat.created_at
        )

    async def _call_gpt(self, prompt: str) -> str:
        completion = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip()
