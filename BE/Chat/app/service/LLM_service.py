from utils.gpt_client import chat_completion

class LlmServicer:
    def user_prompt(self) -> str:
        return """
        

        """
    
    def system_prompt(self) -> str:
        return """

        """


    async def generate(
            self,
            user_input: str,
            previous_chat: str,
            retrieved_context: str,
            ) -> str:
        """
        사용자 입력을 받아 GPT 응답을 생성합니다.

        Args:
            user_input (str): 사용자 질문 또는 요청

        Returns:
            str: GPT 응답
        """
        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": self.user_prompt(user_input)},
        ]

        response = await chat_completion(
            messages=messages,
            temperature=0.7
        )
        return response