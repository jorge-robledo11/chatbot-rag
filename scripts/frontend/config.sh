#!/usr/bin/env bash
set -euo pipefail

# Argumentos
RG="$(az functionapp list --query "[0].resourceGroup" -o tsv | tr -d '\r\n')"
FUNC_APP="$(az functionapp list --query "[0].name" -o tsv | tr -d '\r\n')"
WEB_APP="$(az webapp list --query "[0].name" -o tsv | tr -d '\r\n')"
WEB_APP_URL="$(az webapp show \
  --name "$WEB_APP" \
  --resource-group "$RG" \
  --query "defaultHostName" \
  --output tsv

# Agregar CORS para permitir solicitudes desde la Web App
az functionapp cors add \
  --resource-group "$RG" \
  --name "$FUNC_APP" \
  --allowed-origins "https://$WEB_APP_URL" \
  >/dev/null