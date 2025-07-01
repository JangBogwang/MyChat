# utils/gpt_client.py
import os
import openai
from typing import List, Dict, Any

# 환경 변수 등에 따라 모델/옵션을 바꿀 수 있게 상수화
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o")
MAX_RETRIES = 3
DEFAULT_MAX_TOKENS = 256  # 기본 최대 응답 토큰 수



async def chat_completion(
    messages: List[Dict[str, str]],
    model: str = GPT_MODEL,
    **kwargs: Any,
) -> str:
    """
    비동기 GPT 호출 래퍼
    - messages: OpenAI Chat API 포맷 리스트
    - model: 사용할 모델명 (기본 gpt-4o)
    - kwargs: temperature, top_p 등 추가 옵션
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                **kwargs,
            )
            return response.choices[0].message.content.strip()

        except openai.error.OpenAIError as e:
            if attempt == MAX_RETRIES:
                raise
            # 로그 후 재시도 (간단히 sleep 사용 가능)
            print(f"[GPT Retry {attempt}] {e}")

async def get_embedding(
    text: str,
    model: str = "text-embedding-ada-002",
    **kwargs: Any,
) -> List[float]:
    """
    비동기 OpenAI 임베딩 호출
    - text: 임베딩할 텍스트
    - model: 사용할 임베딩 모델 (기본: text-embedding-ada-002)
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await openai.Embedding.acreate(
                input=text,
                model=model,
                **kwargs
            )
            return response["data"][0]["embedding"]

        except openai.error.OpenAIError as e:
            if attempt == MAX_RETRIES:
                raise
            print(f"[Embedding Retry {attempt}] {e}")

