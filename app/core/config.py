from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # Указываем файл, из которого брать переменные
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Создаем экземпляр настроек, который будем импортировать
settings = Settings()