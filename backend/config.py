from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: str
    mongo_url: str
    mongo_db: str = "healnet"
    neo4j_url: str
    neo4j_user: str = "neo4j"
    neo4j_password: str
    openrouter_api_key: str
    openrouter_model: str = "meta-llama/llama-3.3-8b-instruct:free"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
