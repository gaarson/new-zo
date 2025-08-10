# Makefile

SERVICE ?= auth
ENV ?= dev

# --- Продвинутая логика для обнаружения всех сервисов ---
SERVICE_FILES := $(wildcard */compose.yml)
ALL_SERVICES := $(patsubst %/compose.yml,%,$(SERVICE_FILES))
ALL_PROFILES := $(foreach service,$(ALL_SERVICES),--profile $(service))
ALL_TEST_PROFILES := $(foreach service,$(ALL_SERVICES),--profile $(service)-test)

up: ## Запускает dev-окружение для КОНКРЕТНОГО сервиса (по умолч: auth)
	@echo "🚀 Запускаем dev-окружение для профиля [$(SERVICE)]..."
	docker compose --profile $(SERVICE) up --build -d --force-recreate

up-all: ## Находит и запускает ВСЕ сервисы вместе
	@echo "🚀 Запускаем ВСЕ сервисы..."
	docker compose $(ALL_PROFILES) up --build -d

down: ## Останавливает и удаляет dev-окружение для КОНКРЕТНОГО сервиса (по умолч: auth)
	@echo " останавливаем все..."
	docker compose --profile $(SERVICE) down --remove-orphans -v

down-all: ## Останавливает и удаляет все контейнеры
	@echo " останавливаем и удаляем все..."
	docker compose $(ALL_PROFILES) down --remove-orphans -v

test: ## Запускает тесты. Пример: make test T_ARGS="-k create_user"
	@echo "🧪 Запускаем тесты для [$(SERVICE)] с аргументами [$(T_ARGS)]..."
	docker compose --profile $(SERVICE)-test up -d --build
	@echo "   - Ожидание запуска БД..."
	@sleep 5
	@echo "   - Запуск pytest..."
	docker compose exec -e "PYTHONPATH=/app" $(SERVICE)-test pytest $(T_ARGS)
	@echo "   - Остановка тестового окружения..."
	docker compose --profile $(SERVICE)-test down -v --remove-orphans

test-watch: ## Запускает тесты в watch-режиме для сервиса Пример: make-watch test T_ARGS="-k create_user"
	@echo "🧪 Запускаем тесты для [$(SERVICE)] с аргументами [$(T_ARGS)]..."
	docker compose --profile $(SERVICE)-test up -d --build
	@echo "   - Ожидание запуска БД..."
	@sleep 5
	@echo "   - Запуск pytest watch..."
	docker compose exec -it -e "PYTHONPATH=/app" $(SERVICE)-test ptw  $(T_ARGS) 
	@echo "   - Остановка тестового окружения..."
	docker compose --profile $(SERVICE)-test down -v --remove-orphans

clear-tests: ## Останавливает и удаляет ВСЕ test-окружения для КОНКРЕТНОГО сервиса (по умолч: auth)
	docker compose $(ALL_TEST_PROFILES) down -v --remove-orphans

logs: ## logs: Показывает логи для запущенного сервиса
	@echo "Показываем логи для [$(SERVICE)]..."
	docker compose logs -f $(SERVICE)

migrate: ## Применяет миграции для сервиса в указанном окружении
	@echo "Applying migrations for [$(SERVICE)] in [$(ENV)] mode..."
	./migrate.sh $(ENV) $(SERVICE)

help: ## Показывает эту справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
.PHONY: up up-all down down-all migrate logs help
