# utils/gpt_client.py
import os
import asyncio
from typing import List, Dict, Any, Callable, TypeVar, Awaitable
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai import (
    OpenAIError,
    APIError,
    APIConnectionError,
    RateLimitError,
)

# 환경 변수 불러오기 
load_dotenv()
# Timeout은 httpx.Timeout을 그대로 쓰기보다는 client 생성 옵션으로 처리

# -----------------------------
# 환경 변수 / 상수
# -----------------------------
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "256"))
INITIAL_BACKOFF = float(os.getenv("OPENAI_BACKOFF_INITIAL", "0.5"))
BACKOFF_FACTOR = float(os.getenv("OPENAI_BACKOFF_FACTOR", "2.0"))

# OpenAI API 키는 환경변수 OPENAI_API_KEY 사용
_client = AsyncOpenAI()  # 기본적으로 환경변수에서 키를 읽습니다.

T = TypeVar("T")

async def _with_retries(
    func: Callable[[], Awaitable[T]],
    *,
    max_retries: int = MAX_RETRIES,
    initial_backoff: float = INITIAL_BACKOFF,
    backoff_factor: float = BACKOFF_FACTOR,
) -> T:
    """
    공통 재시도 래퍼 (지수 백오프)
    - RateLimit, 연결 문제, 일시적 API 오류에 재시도
    - 마지막 시도 실패 시 예외 전파
    """
    delay = initial_backoff
    for attempt in range(1, max_retries + 1):
        try:
            return await func()
        except (RateLimitError, APIConnectionError, APIError) as e:
            if attempt == max_retries:
                raise
            # 필요하면 로거로 교체
            print(f"[OpenAI Retry {attempt}/{max_retries}] {type(e).__name__}: {e}")
            await asyncio.sleep(delay)
            delay *= backoff_factor
        except OpenAIError:
            # 프로그래밍/권한 등 비재시도성 오류는 즉시 전파
            raise

# -----------------------------
# Chat Completion (v1.x)
# -----------------------------
async def chat_completion(
    messages: List[Dict[str, str]],
    model: str = GPT_MODEL,
    **kwargs: Any,
) -> str:
    """
    비동기 GPT 호출 래퍼 (v1.x)
    - messages: [{"role": "system|user|assistant", "content": "..."}]
    - model: gpt-4o 등
    - kwargs: temperature, top_p, max_tokens 등
    """
    # max_tokens 기본값 보정
    if "max_tokens" not in kwargs:
        kwargs["max_tokens"] = DEFAULT_MAX_TOKENS

    async def _call():
        resp = await _client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        return resp.choices[0].message.content or ""

    content = await _with_retries(_call)
    return content.strip()

# -----------------------------
# Embeddings (v1.x)
# -----------------------------
async def get_embedding(
    text: str,
    model: str = EMBEDDING_MODEL,
    **kwargs: Any,
) -> List[float]:
    """
    비동기 OpenAI 임베딩 호출 (v1.x)
    - text: 임베딩할 텍스트
    - model: text-embedding-3-small / text-embedding-3-large 등
    """
    async def _call():
        resp = await _client.embeddings.create(
            input=text,
            model=model,
            **kwargs,
        )
        return resp.data[0].embedding

    return await _with_retries(_call)
