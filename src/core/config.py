import json
import logging
from logging import config as logging_config
from pathlib import Path

from fastapi_mail import ConnectionConfig
from pydantic import ConfigDict, EmailStr, IPvAnyAddress
from pydantic_settings import BaseSettings

from src.core.logger import LOGGING

EMAIL_QUEUE = 'email_queue'


class Settings(BaseSettings):
    app_title: str
    project_host: IPvAnyAddress
    project_port: int

    smtp_servers_file: str
    sending_interval_sec: int
    upload_folder: str

    redis_host: IPvAnyAddress | str
    redis_port: int
    redis_ttl_sec: int

    model_config = ConfigDict(env_file='.env')

    @property
    def smtp_servers(self):
        file_path = Path(self.smtp_servers_file)
        if file_path.exists():
            with open(file_path) as f:
                return [ConnectionConfig(**server) for server in json.load(f)]
        logger.error(
            f'Отсутствует файл конфигурации SMTP серверов {self.smtp_servers_file}'
        )
        return []

    @property
    def redis_url(self) -> str:
        return f'redis://{self.redis_host}:{self.redis_port}'


settings = Settings()
logging_config.dictConfig(LOGGING)
logger = logging.getLogger(settings.app_title)
