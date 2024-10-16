all: start

start:
	docker-compose up --build -d

stop:
	docker-compose down

test:
	docker-compose exec message-sender-api pytest -v tests
