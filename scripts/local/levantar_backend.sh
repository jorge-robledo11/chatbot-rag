#!/bin/bash

echo "Levantando el backend..."
uv run fastapi dev backend/src/app.py
