from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://mining:mining123@localhost:5432/mining_db"
    upload_dir: str = "/app/uploads"

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
