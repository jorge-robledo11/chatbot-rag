#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------------------------------
#           🚀 DEPLOY FRONTEND — Despliegue de la Web App
# -------------------------------------------------------------------

# 0) Descubrimiento automático de recursos
RG="$(az webapp list --query "[0].resourceGroup" -o tsv)"
WEB_APP="$(az webapp list --query "[0].name" -o tsv | tr -d '\r\n')"
ACR_NAME="$(az acr list -o json | jq -r '.[].name | ascii_downcase')"
ACR_LOGIN_SERVER="$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)"
REPO="repo-frontend"
TAG="dev"
IMAGE="${ACR_LOGIN_SERVER}/${REPO}:${TAG}"

# La URL del backend para Vite ↓
FUNC_APP="$(az functionapp list --query "[0].name" -o tsv | tr -d '\r\n')"
FUNC_APP_URL="$(az functionapp show \
  --name "$FUNC_APP" \
  --resource-group "$RG" \
  --query defaultHostName -o tsv)"

# 1) Detener la Web App si está en ejecución
echo "🔍 Comprobando estado de la Web App…"
STATE=$(az webapp show \
          --resource-group "$RG" \
          --name "$WEB_APP" \
          --query state -o tsv)

if [[ "$STATE" == "Running" ]]; then
  echo "⏹️  Deteniendo Web App ($WEB_APP)…"
  az webapp stop --resource-group "$RG" --name "$WEB_APP"
else
  echo "ℹ️  Web App ya estaba detenida ($STATE)."
fi

# 2) Build + push de la nueva imagen
echo "🔨 Building → $IMAGE"
docker build -f Dockerfile.frontend \
  --build-arg VITE_API_BASE_URL="https://$FUNC_APP_URL" \
  -t "$IMAGE" .

echo "🔐 Login → $ACR_NAME"
az acr update --name "$ACR_NAME" --admin-enabled true >/dev/null 2>&1
az acr login --name "$ACR_NAME" >/dev/null 2>&1

echo "🚀 Pushing → $IMAGE"
docker push "$IMAGE"

# 3) Actualizar la Web App para usar la nueva imagen
echo "📦 Actualizando Web App con la nueva imagen"
az webapp update \
  --resource-group "$RG" \
  --name "$WEB_APP" \
  --set siteConfig.linuxFxVersion="DOCKER|$IMAGE" \
  >/dev/null 2>&1

# 4) Arrancar de nuevo la Web App
echo "▶️ Iniciando Web App"
az webapp start --resource-group "$RG" --name "$WEB_APP"

# 5) Limpieza local de la imagen (asíncrona)
echo "🧹 Eliminando la imagen Docker local"
docker rmi "$IMAGE" >/dev/null 2>&1

echo "🚀 Frontend desplegado — Web App corriendo"
echo ""
