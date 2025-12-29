from pydantic_settings import BaseSettings

# 로컬 환경일 경우 환경변수 주입 
class Settings(BaseSettings):
    OPENAI_API_KEY: str
    QDRANT_HOST: str
    QDRANT_PORT: int
    MAIN_SENDER: str

    class Config:
        env_file = ".env"

settings = Settings()
