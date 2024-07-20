@echo off
echo Starting Docker Compose...

docker compose -f docker\docker-compose.yml up -d --build

echo Docker Compose has been started.