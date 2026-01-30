import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProductionConfig(BaseSettings):
    app_name: str = "Maira AISEV Backend"
    env_name: str = "PROD"
    maira_api_hostname: str
    maira_api_port: int
    open_ai_api_key: str
    default_timeout: int = 180  # seconds

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


class StagingConfig(ProductionConfig):
    app_name: str = "Maira AISEV Backend STG"
    env_name: str = "STG"


class TrialConfig(ProductionConfig):
    app_name: str = "Maira AISEV Backend Trial"
    env_name: str = "TRIAL"


class DevConfig(ProductionConfig):
    app_name: str = "Maira AISEV Backend Dev"
    env_name: str = "DEV"


env = os.getenv("APP_ENVIRONMENT", "DEV").upper()

if env == "PROD":
    config = ProductionConfig()
elif env == "STG":
    config = StagingConfig()
elif env == "TRIAL":
    config = TrialConfig()
else:
    config = DevConfig()
