from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select  # ✅ 추가
from app.models.chat_model import Chat
from app.dto.chat_dto import ChatRequest
from app.config.logging_config import logger

async def save_chat_message(
    db: AsyncSession,
    user_id: int,
    request_msg: str,
    response_msg: str
) -> Chat:
    """
    채팅 메시지를 데이터베이스에 저장합니다.
    """
    chat_instance = Chat(
        user_id=user_id,
        request_msg=request_msg,
        response_msg=response_msg,
    )
    
    try:
        db.add(chat_instance)
        await db.commit()
        await db.refresh(chat_instance)
        logger.info(f"채팅 내역 저장 성공 (ID: {chat_instance.id})")
        return chat_instance
    except Exception as e:
        logger.error(f"채팅 내역 저장 실패: {e}")
        await db.rollback()
        raise  # 오류 발생 시 상위 서비스로 전파

async def get_recent_chats_by_user_id(db: AsyncSession, user_id: int, limit: int = 5) -> list[Chat]:
    """
    특정 사용자의 최근 채팅 기록을 N개 가져옵니다.
    """
    try:
        result = await db.execute(
            select(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.created_at.desc())
            .limit(limit)
        )
        chats = result.scalars().all()
        logger.info(f"사용자 ID({user_id})의 최근 채팅 {len(chats)}개 조회 성공")
        return chats
    except Exception as e:
        logger.error(f"사용자 ID({user_id})의 최근 채팅 조회 실패: {e}")
        return []
