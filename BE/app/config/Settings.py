from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM & Vector DB
    OPENAI_API_KEY: str
    QDRANT_HOST: str
    QDRANT_PORT: int
    
    # Chatbot config
    MAIN_SENDER: str

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
