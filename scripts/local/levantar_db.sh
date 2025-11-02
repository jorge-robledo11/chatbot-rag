#!/bin/bash
echo "Iniciando MongoDB..."
docker run -d -p 27017:27017 --name mongodb -v mongodata:/data/db mongo:latest
echo "MongoDB iniciado correctamente."
