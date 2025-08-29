from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct, PointIdsList
)
from app.config.logging_config import logger

VECTOR_DIM = 1536  # text-embedding-3-small 기준


class QdrantClientAsync:
    def __init__(
        self,
        aclient: AsyncQdrantClient,
        collection_name: str = "my_collection",
    ):
        # __init__는 동기여야 함
        self.client = aclient
        self.collection_name = collection_name

    # ✅ 비동기 팩토리: 인스턴스 생성
    @classmethod
    async def create(
        cls,
        *,
        # 두 방식 중 하나만 쓰세요: url 또는 host/port(+https)
        url: Optional[str] = None,
        host: str = "localhost",
        port: int = 6333,
        https: bool = False,
        api_key: str = "",
        collection_name: str = "my_collection",
        verify: bool | str = True,          # 자가서명 인증서면 False(개발용) 또는 CA 경로
        prefer_grpc: bool = False,          # HTTP로 고정하면 디버깅 쉬움
        timeout: Optional[float] = 10.0,    # 요청 타임아웃(초)
    ) -> "QdrantClientAsync":
        if url:
            aclient = AsyncQdrantClient(
                url=url,
                api_key=api_key or None,
                prefer_grpc=prefer_grpc,
                timeout=timeout,
                # httpx 옵션 전달
                verify=verify,
            )
        else:
            aclient = AsyncQdrantClient(
                host=host,
                port=int(port),
                api_key=api_key or None,
                https=bool(https),
                prefer_grpc=prefer_grpc,
                timeout=timeout,
                verify=verify,
            )
        return cls(aclient=aclient, collection_name=collection_name)

    # 앱 종료 시 호출 권장
    async def aclose(self) -> None:
        await self.client.close()

    # ---------------------------
    # Qdrant Operations (Async)
    # ---------------------------
    async def create_collection(self, vector_size: int = VECTOR_DIM) -> None:
        """컬렉션이 없으면 생성."""
        cols = await self.client.get_collections()
        existing = [c.name for c in cols.collections]
        if self.collection_name in existing:
            return

        logger.info(
            f"📁 컬렉션 '{self.collection_name}' 없음 → 새로 생성(dim={vector_size})"
        )
        # 데이터 보존을 위해 create 사용(필요 시 recreate로 교체)
        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size, distance=Distance.COSINE
            ),
        )

    async def upsert_point(
        self,
        vector: List[float],
        payload: Optional[Dict[str, Any]] = None,
        point_id: Optional[str] = None,
    ):
        """벡터/페이로드 업서트"""
        pid = point_id or str(uuid.uuid4())
        points = [
            PointStruct(
                id=pid,
                vector=vector,
                payload=payload or {},
            )
        ]
        result = await self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        logger.info(f"✅ Upsert 완료: {result}")
        return result

    async def search(
        self,
        query_vector: List[float],
        limit: int = 6,
        score_threshold: Optional[float] = None,
        with_vectors: bool = False,
    ):
        """벡터 유사도 검색"""
        kwargs: Dict[str, Any] = dict(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True,
            with_vectors=with_vectors,
        )
        if score_threshold is not None:
            kwargs["score_threshold"] = score_threshold

        return await self.client.search(**kwargs)

    async def delete_point(self, point_id: str):
        """포인트 삭제"""
        return await self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(points=[point_id]),
        )
