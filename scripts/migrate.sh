#!/bin/bash
set -e

# --- Проверка аргументов ---
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "❌ Ошибка: Укажите окружение и имя сервиса."
  echo "Использование: $0 <dev|prod> <имя_сервиса>"
  echo "Пример: $0 dev auth"
  exit 1
fi

ENV=$1
SERVICE=$2

# --- Пути строятся относительно корня проекта ---
SERVICE_DIR="../$SERVICE"
CONFIG_FILE="$SERVICE_DIR/database.${ENV}.env"
MIGRATIONS_DIR="$SERVICE_DIR/migrations"

# ... (остальная часть скрипта остается точно такой же, как в предыдущем ответе) ...
# Она уже универсальна и использует эти переменные.
# (Проверка существования файлов, загрузка конфига, psql-команды и т.д.)

# --- Загружаем конфигурацию ---
if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ Файл конфигурации '$CONFIG_FILE' не найден."
  exit 1
fi
source "$CONFIG_FILE"

echo "🚀 Применяем миграции для сервиса [$SERVICE] в окружении [$ENV]..."

export PGPASSWORD=$DB_PASSWORD
PSQL_CMD="psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"

echo "Проверяем соединение с БД..."
$PSQL_CMD -c "SELECT 1" > /dev/null
echo "✅ Соединение успешно."

for MIGRATION_FILE in $(ls $MIGRATIONS_DIR/*.sql | sort); do
  FILENAME=$(basename "$MIGRATION_FILE")
  APPLIED_CHECK=$($PSQL_CMD -t -c "SELECT version FROM schema_migrations WHERE version = '$FILENAME';")
  
  if [ -z "$APPLIED_CHECK" ]; then
    echo "  - Применяем новую миграцию: $FILENAME ..."
    $PSQL_CMD -v ON_ERROR_STOP=1 -f "$MIGRATION_FILE"
    $PSQL_CMD -c "INSERT INTO schema_migrations (version) VALUES ('$FILENAME');"
  else
    echo "  - Миграция уже применена, пропускаем: $FILENAME"
  fi
done

echo "✅ Все миграции успешно применены."
