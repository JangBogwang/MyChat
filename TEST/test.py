#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test.py ― Kakao-chat Qdrant 검색 예제
"""

import json
import os
import warnings
from typing import List

import openai
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

# ─────────────────── 설정 및 준비 ──────────────────────────
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()  # .env 로드
openai.api_key = os.getenv("OPENAI_API_KEY")

# ★ .env 값 읽기 (없으면 기본값)
QDRANT_HOST = "localhost"   # docker 내부면 'qdrant'
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_API_KEY = os.getenv("X_API_KEY")                # ★ 추가된 부분QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION   = "kakao-chat"
MODEL        = "text-embedding-3-small"
VECTOR_DIM   = 1536  # text-embedding-3-small 기준

# ─────────────────── 헬퍼 함수 ────────────────────────────
def ensure_collection(client: QdrantClient, name: str, dim: int) -> None:
    """컬렉션이 없으면 필요 파라미터로 생성한다."""
    existing = [c.name for c in client.get_collections().collections]
    if name in existing:
        return

    print(f"📁 컬렉션 '{name}' 없음 → 새로 생성(dim={dim})")
    client.recreate_collection(
        collection_name=name,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

def embed(texts: List[str]) -> List[List[float]]:
    """OpenAI 임베딩 호출(Batch 96)."""
    BATCH = 96
    vectors = []
    for i in range(0, len(texts), BATCH):
        resp = openai.embeddings.create(model=MODEL, input=texts[i : i + BATCH])
        vectors.extend([d.embedding for d in resp.data])
    return vectors

# ─────────────────── 메인 로직 ────────────────────────────
def main() -> None:
    query_text = "사랑해"

    # 1) 임베딩
    embedding = embed([query_text])[0]
    print(f"✅ 임베딩 완료 (dim={len(embedding)})")

    # 2) Qdrant 연결
    client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
        https=False,
        api_key=os.getenv("X_API_KEY"),  # ← API 키 추가!
        timeout=30.0,
    )
    ensure_collection(client, COLLECTION, len(embedding))

    # 3) 차원 검증
    info = client.get_collection(COLLECTION)
    dim_qdrant = info.config.params.vectors.size
    if dim_qdrant != len(embedding):
        raise ValueError(
            f"벡터 차원 불일치: OpenAI={len(embedding)} vs Qdrant={dim_qdrant}"
        )

    # 4) 검색
    hits = client.search(
        collection_name=COLLECTION,
        query_vector=embedding,
        limit=6,
        with_payload=True,
    )

    # 5) 결과 출력
    print("\n🔎 Top-5 결과 ------------------------------")
    for idx, h in enumerate(hits, 1):
        print(
            json.dumps(
                {
                    "rank": idx,
                    "score": round(h.score, 4),
                    "content": h.payload.get("content", "")[:120],
                    "query_sender": h.payload.get("query_sender"),
                    "response_sender": h.payload.get("response_sender"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

if __name__ == "__main__":
    main()
