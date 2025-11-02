# Makefile para stack Docker Compose Ajover

# Variables
COMPOSE=docker compose
PROJECT_NAME=ajover

.PHONY: up build down restart logs clean prune

## Levanta todos los servicios (build incluido)
up:
	$(COMPOSE) up --build

## Solo construye las imágenes
build:
	$(COMPOSE) build

## Detiene y elimina todos los servicios y red
down:
	$(COMPOSE) down

## Reinicia el stack
restart: down up

## Muestra los logs de todos los servicios
logs:
	$(COMPOSE) logs -f

## Limpia todo el Docker (¡CUIDADO! Elimina lo que no esté en uso)
prune:
	docker system prune -f --volumes

# Lo más común en desarrollo es usar:
# make up para levantar todo (¡reconstruye y conecta!).
# make down cuando terminas o quieres limpiar.
# make logs si quieres ver logs tras levantar en background (con -d).
# make prune ocasionalmente para limpiar el sistema (¡CUIDADO!).
# make build lo usarás rara vez, porque make up ya incluye build automático si detecta cambios.
