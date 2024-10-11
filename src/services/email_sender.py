import asyncio
import smtplib
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema

from src.core.config import logger, settings
from src.db.redis import redis


async def decr_or_delete(attachments: list[str]) -> None:
    """
    Удаление вложенных файлов после отправки всех сообщений к которым они прилагаются
    """

    for attachment in attachments:
        count = await redis.decr(attachment)
        if count == 0:
            await redis.delete(attachment)
            file_path = Path(attachment)
            if file_path.exists():
                file_path.unlink()

            parent_directory = file_path.parent
            if parent_directory.exists() and not any(
                    parent_directory.iterdir()
            ):
                parent_directory.rmdir()


async def send_email(message_fields: dict) -> None:
    """
    Отправка электронной почты
    """

    for server in settings.smtp_servers:
        message = MessageSchema(
            subject=message_fields['subject'],
            recipients=[message_fields['email']],
            body=message_fields['body'],
            subtype='html',
            attachments=message_fields['attach_files_paths'],
        )

        fm = FastMail(server)
        try:
            await fm.send_message(message)
            logger.info(
                (
                    f'Письмо успешно отправлено на {message.recipients[0]} '
                    f'через SMTP сервер {server.MAIL_SERVER}'
                )
            )

            if message_fields['attach_files_paths']:
                await decr_or_delete(message_fields['attach_files_paths'])

            await asyncio.sleep(settings.sending_interval_sec)
            return

        except ConnectionRefusedError:
            logger.error(
                (
                    f'Ошибка подключения к SMTP-серверу {server.MAIL_SERVER} '
                    f'при отправке на {message.recipients[0]}'
                )
            )

        except smtplib.SMTPRecipientsRefused:
            logger.error(
                (
                    f'Получатель {message.recipients[0]} '
                    f'отклонен сервером SMTP {server.MAIL_SERVER}'
                )
            )
            break

        except smtplib.SMTPAuthenticationError:
            logger.error(
                (
                    f'Ошибка аутентификации SMTP на {server.MAIL_SERVER}. '
                    f'Проверьте логин/пароль'
                )
            )

        except smtplib.SMTPException as e:
            logger.error(
                (
                    f'Произошла ошибка на SMTP-сервере {server.MAIL_SERVER} '
                    f'при отправке письма на {message.recipients[0]}: {str(e)}'
                )
            )

        except Exception as e:
            logger.error(
                (
                    f'Произошла непредвиденная ошибка на '
                    f' {server.MAIL_SERVER}: {str(e)}'
                )
            )

    logger.error(
        (
            f'Не удалось отправить письмо на {message_fields["email"]} '
            f'через все доступные серверы'
        )
    )
    if message_fields['attach_files_paths']:
        await decr_or_delete(message_fields['attach_files_paths'])
