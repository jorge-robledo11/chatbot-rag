#!/usr/bin/env bash
set -euo pipefail

# Parámetros
RG="$(az functionapp list --query "[0].resourceGroup" -o tsv | tr -d '\r\n')"
FUNC_APP="$(az functionapp list --query "[0].name" -o tsv | tr -d '\r\n')"
ACR_NAME="$(az acr list -o json | jq -r '.[].name | ascii_downcase')"
ACR_LOGIN_SERVER="$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)"
ACR_PASSWORD="$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)"
ENV_VARS="${ENV_VARS:-env_vars.json}"

echo "ℹ️ Aplicación: $FUNC_APP  —  RG: $RG"
echo ""

# 1) Always On
echo "🔧 Habilitando Always On..."
az functionapp config set \
  --name "$FUNC_APP" \
  --resource-group "$RG" \
  --always-on true
echo "✅ Always On habilitado."
echo ""

# 2) Logging (app, contenedor y servidor web)
echo "📝 Configurando logging..."
az webapp log config \
  --name "$FUNC_APP" \
  --resource-group "$RG" \
  --application-logging filesystem \
  --docker-container-logging filesystem \
  --web-server-logging filesystem \
  --detailed-error-messages true \
  --failed-request-tracing true
echo "✅ Logging configurado."
echo ""

# 3) App Settings y conexión al ACR
echo "🔧 Cargando APP SETTINGS desde $ENV_VARS..."
az functionapp config appsettings set \
  --name "$FUNC_APP" \
  --resource-group "$RG" \
  --settings @"${ENV_VARS}" \
      WEBSITES_ENABLE_APP_SERVICE_STORAGE="false" \
      WEBSITES_PORT="80" \
      FUNCTIONS_EXTENSION_VERSION="~4" \
      FUNCTIONS_WORKER_RUNTIME="python" \
      DOCKER_REGISTRY_SERVER_URL="https://$ACR_LOGIN_SERVER" \
      DOCKER_REGISTRY_SERVER_USERNAME="$ACR_NAME" \
      DOCKER_REGISTRY_SERVER_PASSWORD="$ACR_PASSWORD" \
      >/dev/null
echo "✅ APP SETTINGS configuradas."
echo ""

echo "🎉 ¡Configuración completada!"
