from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres.rphwhyxwaacqlrlljzqu:a9Xk0ZyLegnQ4n4K@aws-0-us-east-2.pooler.supabase.com:5432/postgres"
    
    class Config:
        env_file = ".env"

settings = Settings() 