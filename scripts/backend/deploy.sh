#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------------------------------
#         🚀 DEPLOY BACKEND — Despliegue de la Function App
# -------------------------------------------------------------------

# Parámetros
RG="$(az functionapp list --query "[0].resourceGroup" -o tsv)"
FUNC_APP="$(az functionapp list --query "[0].name" -o tsv | tr -d '\r\n')"
ACR_NAME="$(az acr list -o json | jq -r '.[].name | ascii_downcase')"
ACR_LOGIN_SERVER=$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)
REPO="repo-backend"
TAG="dev"
IMAGE="${ACR_LOGIN_SERVER}/${REPO}:${TAG}"

# 1) Detener la Function App si está corriendo
echo "🔍 Comprobando estado de la Function App…"
STATE=$(az functionapp show \
          --name "$FUNC_APP" \
          --resource-group "$RG" \
          --query state -o tsv)

if [[ "$STATE" == "Running" ]]; then
  echo "⏹️  Deteniendo Function App ($FUNC_APP)…"
  az functionapp stop --name "$FUNC_APP" --resource-group "$RG"
else
  echo "ℹ️  Function App ya estaba detenida ($STATE)."
fi

# 2) Build + push
echo "🔨 Building → $IMAGE"
docker build -f Dockerfile.azfn -t "$IMAGE" .

echo "🔐 Login → $ACR_NAME"
az acr update -n "$ACR_NAME" --admin-enabled true >/dev/null 2>&1
az acr login -n "$ACR_NAME" >/dev/null 2>&1

echo "🚀 Pushing → $IMAGE"
docker push "$IMAGE"

# 3) Cambiar la imagen en la Function App por la nueva
echo "📦 Actualizando Function App con la nueva imagen"
az functionapp update \
  --name "$FUNC_APP" \
  --resource-group "$RG" \
  --set siteConfig.linuxFxVersion="DOCKER|$IMAGE" \
  >/dev/null 2>&1

# 4) Arrancar la Function App actualizada
echo "▶️ Iniciando Function App"
az functionapp start --name "$FUNC_APP" --resource-group "$RG"

# 5) Limpieza local en paralelo
echo "🧹 Eliminando la imagen Docker local"
docker rmi "$IMAGE" >/dev/null 2>&1 || true &

# 6) Esperar un poco antes del tail de logs
sleep 10

echo "🚀 Despliegue completado — Function App corriendo"
echo ""
echo "🔎 Tail de logs:"
az webapp log tail \
  --name "$FUNC_APP" \
  --resource-group "$RG"
