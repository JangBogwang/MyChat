# app/services/rag_service.py
import os
from typing import List, Sequence
from app.config.logging_config import logger
from app.utils.Qdrant_client import QdrantClientAsync  # ← 앞서 제공한 Async 래퍼

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "kakao-chat")
X_API_KEY = os.getenv("X_API_KEY", "")

class RAGService:
    def __init__(self, qdrant_client: QdrantClientAsync):
        self.qdrant = qdrant_client

    @classmethod
    async def create(cls) -> "RAGService":
        qc = await QdrantClientAsync.create(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
            api_key=X_API_KEY or "",
            collection_name=QDRANT_COLLECTION,
            prefer_grpc=False,  # HTTP만 사용 → 디버깅 쉬움
            # url="https://your-domain", verify=False  # TLS 프록시 사용 시
        )
        await qc.create_collection()  # 필요 시 1회 생성
        return cls(qdrant_client=qc)

    async def aclose(self) -> None:
        await self.qdrant.aclose()

    async def get_chat(self, query_vector: Sequence[float]) -> str:
        """질문 벡터로 관련 대화 기록을 검색해 컨텍스트를 문자열로 반환"""
        try:
            hits = await self.qdrant.search(
                query_vector=list(query_vector),
                limit=5,
                score_threshold=None,    # 필요 시 0.75 같은 임계치
                with_vectors=False,
            )
            logger.info(f"Qdrant 검색 완료. {len(hits)}개 결과 발견.")
        except Exception as e:
            logger.error(f"Qdrant 검색 실패: {e}")
            return "죄송해요, 대화 기록을 찾는 중 오류가 발생했어요."

        # ScoredPoint 리스트를 payload에서 꺼내기
        lines: List[str] = []
        for h in hits:
            try:
                payload = getattr(h, "payload", None) or {}
                text = payload.get("content") or payload.get("text") or payload.get("body")
                if text:
                    lines.append(f"- {text}")
            except Exception:
                # payload 형태가 다른 경우 조용히 스킵
                continue

        retrieved_context = "\n".join(lines) if lines else "관련 대화 기록을 찾지 못했습니다."
        logger.info(f"추출된 컨텍스트:\n{retrieved_context}")
        return retrieved_context
