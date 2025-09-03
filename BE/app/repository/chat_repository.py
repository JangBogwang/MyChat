from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select  # ✅ 추가
from app.models.chat_model import Chat
from app.dto.chat_dto import ChatRequest
from app.config.logging_config import logger

async def save_chat_message(
    db: AsyncSession,
    user_id: str,
    request: str,
    response: str,
) -> Chat:
    """채팅 메시지를 DB에 저장"""
    chat = Chat(
        user_id=user_id,
        request=request,
        response=response,
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat

async def get_recent_chats_by_user_id(db: AsyncSession, user_id: int, limit: int = 5) -> list[Chat]:
    """
    특정 사용자의 최근 채팅 기록을 N개 가져옵니다.
    """
    try:
        result = await db.execute(
            select(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.timestamp.desc())
            .limit(limit)
        )
        chats = result.scalars().all()
        logger.info(f"사용자 ID({user_id})의 최근 채팅 {len(chats)}개 조회 성공")
        return chats
    except Exception as e:
        logger.error(f"사용자 ID({user_id})의 최근 채팅 조회 실패: {e}")
        return []
