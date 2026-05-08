from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    allowed_origins: str = "http://localhost:3000"
    api_secret: str = ""

    def get_allowed_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"

settings = Settings()

