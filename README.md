# Тестовое задание
### Спроектировать REST API для сервиса рассылок

# Решение
В рамках выполнения задания реализовано API сервиса.

Сервис позволяет:
- отправлять сообщения списку пользователей
- получать статус очереди отправки сообщений

Описание API доступно по ссылке: http://127.0.0.1:8000/api/openapi

Для демонстрации используется почтовый сервер [smtp4dev](https://github.com/rnwood/smtp4dev) 

## Установка и запуск
```
git clone https://github.com/alexfofanov/message-sender.git

cd messages-sender

создать файл настройки проекта .env по обарзцу .env.sample

создать файл настройки конфигурации smtp серверов smtp_servers.json по образцу smtp_servers.json.sample

Запуск сервиса: make start

Остановка сервиса: make stop
```

## Примеры запросов

#### Отправка сообщения списку получателей без вложенных файлов
```
curl -X POST "http://127.0.0.1:8000/api/v1/send_email/" \
-H "Content-Type: multipart/form-data" \
-F "emails=example1@example.com" \
-F "emails=example2@example.com" \
-F "emails=example3@example.com" \
-F "subject=Заголовок сообщения" \
-F "body=Текст сообщения"
```
```
Ответ:
{"status":"В очередь на отправку добавлены сообщения в количестве: 3"}
```
#### Отправка сообщения списку получателей с вложенными файлами
```
curl -X POST "http://127.0.0.1:8000/api/v1/send_email/" \
-H "Content-Type: multipart/form-data" \
-F "emails=example1@example.com" \
-F "emails=example2@example.com" \
-F "subject=Заголовок сообщения" \
-F "body=Your email body" \
-F "files=@file_1.docx" \
-F "files=@file_2.jpg"
```
```
Ответ:
{"status":"В очередь на отправку добавлены сообщения в количестве: 2"}
```
#### Получение статуса очереди сообщений
```
curl -X GET "http://127.0.0.1:8000/api/v1/send_email/status"
```
```
Ответ
{"total":2,"messages":[{"number":1,"email":"example2@example.com","subject":"Заголовок сообщения"},{"number":2,"email":"example3@example.com","subject":"Заголовок сообщения"}]}% 
```

Отправленные письма можно посмотреть через web интерфейс по ссылке: http://127.0.0.1:3000

