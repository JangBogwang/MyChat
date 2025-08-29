from pydantic import BaseSettings

# 로컬 환경일 경우 환경변수 주입 
class Settings(BaseSettings):
    openai_api_key: str
    qdrant_host: str
    qdrant_port: int
    x_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
