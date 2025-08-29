from sqlalchemy import Column, String, Text, DateTime
from app.config.DBconfig import Base  # 수정: DBconfig에서 Base 임포트
from datetime import datetime
import uuid


class Chat(Base):
    __tablename__ = "chat"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False)
    request = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
