from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    allowed_origins: str = "http://localhost:3000"
    
    def get_allowed_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]
    
    # Read variables from .env
    class Config:
        env_file = ".env"

settings = Settings()


