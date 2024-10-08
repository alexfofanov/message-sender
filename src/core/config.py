from pydantic import ConfigDict, EmailStr, IPvAnyAddress
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str
    project_host: IPvAnyAddress
    project_port: int

    smtp_servers: list[str]
    sender_email: EmailStr
    sending_interval_sec: int

    model_config = ConfigDict(env_file='.env')


settings = Settings()
