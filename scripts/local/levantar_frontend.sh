#!/bin/bash

echo "Levantando el frontend..."
docker run -p 8080:80 ajover-frontend
echo "Frontend levantado en http://localhost:8080"
