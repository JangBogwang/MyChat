import os
from typing import List
from app.config.logging_config import logger
from app.utils.gpt_client import chat_completion
from app.repository.chat_repository import get_recent_chats_by_user_id

class LLMService:
    def __init__(self):
        self

    async def _create_prompt(self, user_input: str, context: str, user_chats: list[str]) -> list:
        """LLM에 전달할 프롬프트를 생성합니다."""
        
        # 사용자 대화 기록을 문자열로 변환
        chat_history = "\n".join(user_chats)

        system_prompt = f"""
        당신은 나의 카카오톡 대화 기록을 기반으로 답변하는 챗봇입니다.
        주어진 '대화 기록'과 '사용자 최근 대화'를 바탕으로 사용자의 '질문'에 대해 답변해주세요.
        특히, '대화 기록'을 통해 나의 말투와 스타일, 답변 성향을 파악하고, 최대한 비슷하게 답변해야 합니다.
        대화 기록에 관련 내용이 없으면 문맥과 이전 대화 기록을 바탕으로 말투를 유지해서 대답해줘.
        이전 대화 기록을 참고해서 문맥에 맞는 대화를 해줘.
        답변은 항상 한국어로 해줘 
        """
        
        user_prompt = f"""
        [대화 기록]
        {context}

        [사용자 최근 대화]
        {chat_history}

        [질문]
        {user_input}
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return messages

    async def generate(
            self,
            user_input: str,
            retrieved_context: List[str],
            user_chat_history: List[str],
            ) -> str:
        """
        사용자 입력을 받아 최종 답변을 생성합니다.
        """
        logger.info(f"입력 접수: '{user_input}'")

        # 4. 프롬프트 생성
        messages = await self._create_prompt(user_input, retrieved_context, user_chat_history)
        logger.info(f"LLM 프롬프트 생성 완료.")
        # 로그 가독성을 위해 상세 프롬프트는 DEBUG 레벨로 기록 (현재는 INFO 레벨만 출력)
        # logger.debug(f"전체 프롬프트: {messages}") 

        # 5. LLM을 통해 답변 생성
        try:
            final_response = await chat_completion(messages=messages)
            logger.info(f"LLM 답변 생성 완료: '{final_response}'")
        except Exception as e:
            logger.error(f"LLM 답변 생성 실패: {e}")
            return "죄송해요, 답변을 생성하는 중 오류가 발생했어요."

        return final_response
