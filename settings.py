import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path="../../.env")


class Settings(BaseSettings):
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "sk-TpFOPlp65ZwbsWQQ7bm8p8yhNWj6yC692KuaMlKraPFVbAL3")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-TpFOPlp65ZwbsWQQ7bm8p8yhNWj6yC692KuaMlKraPFVbAL3")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "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")

    class Config:
        env_file = ".env"


settings = Settings()
