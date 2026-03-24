from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    frontend_url: str

    secret_key: str
    registration_code: str
    environment: str = "development" # prod, testing, development
    
    class Config:
        env_file = ".env"

settings = Settings()
