#!/bin/bash

# Скрипт для настройки сервера для деплоя Calculation Bot
# Запускать на сервере под пользователем, который будет деплоить

set -e

echo "🚀 Настройка сервера для Calculation Bot..."

# Создаем директорию проекта
mkdir -p ~/calculation-bot
cd ~/calculation-bot

# Создаем docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  calculation-bot:
    image: ghcr.io/bexull/report_bot:latest
    container_name: calculation-bot
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - bot-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  bot-network:
    driver: bridge
EOF

# Создаем .env файл (пользователь должен заполнить его)
cat > .env.example << 'EOF'
# Токен бота от @BotFather
BOT_TOKEN=your_bot_token_here

# URL базы данных PostgreSQL (если используется)
DATABASE_URL=postgresql://username:password@localhost:5432/calculation_bot
EOF

# Создаем директории для данных и логов
mkdir -p data logs

# Устанавливаем права доступа
chmod 755 data logs
chmod 644 docker-compose.yml .env.example

echo "✅ Настройка сервера завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Скопируйте .env.example в .env и заполните переменные:"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "2. Добавьте GitHub Secrets в настройках репозитория:"
echo "   - HOST: $(curl -s ifconfig.me || echo 'YOUR_SERVER_IP')"
echo "   - USERNAME: $(whoami)"
echo "   - SSH_KEY: содержимое ~/.ssh/id_rsa"
echo "   - PORT: 22"
echo ""
echo "3. Сделайте push в master ветку для запуска деплоя"
