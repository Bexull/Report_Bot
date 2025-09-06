# Инструкции по развертыванию

## Настройка CI/CD

### 1. GitHub Secrets
Добавьте следующие секреты в настройках репозитория (Settings → Secrets and variables → Actions):

- `HOST` - IP адрес или домен вашего сервера
- `USERNAME` - имя пользователя для SSH подключения
- `SSH_KEY` - приватный SSH ключ для подключения к серверу
- `PORT` - порт SSH (обычно 22)

### 2. Настройка сервера

#### Установка Docker и Docker Compose
```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавляем пользователя в группу docker
sudo usermod -aG docker $USER

# Устанавливаем Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Создание директории проекта
```bash
mkdir -p /path/to/your/project
cd /path/to/your/project
```

#### Создание docker-compose.yml на сервере
```yaml
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
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge
```

#### Создание .env файла на сервере
```bash
# Создайте файл .env с вашими переменными окружения
BOT_TOKEN=your_bot_token_here
DATABASE_URL=your_database_url_here
```

### 3. Настройка SSH ключей

#### На локальной машине (где у вас есть доступ к репозиторию):
```bash
# Генерируем SSH ключ (если еще нет)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Копируем публичный ключ на сервер
ssh-copy-id username@your_server_ip
```

#### Добавляем приватный ключ в GitHub Secrets:
1. Скопируйте содержимое приватного ключа (~/.ssh/id_rsa)
2. Добавьте его как секрет `SSH_KEY` в настройках репозитория

### 4. Первый запуск

После настройки всех секретов:
1. Сделайте push в ветку master/main
2. GitHub Actions автоматически соберет Docker образ
3. При успешной сборке запустится деплой на сервер

### 5. Мониторинг

Проверяйте статус деплоя в разделе Actions вашего репозитория на GitHub.

### 6. Логи

Для просмотра логов бота на сервере:
```bash
docker logs calculation-bot -f
```
