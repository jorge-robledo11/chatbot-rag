#!/bin/bash
set -e

# Parámetros
RG="$(az functionapp list --query "[0].resourceGroup" -o tsv | tr -d '\r\n')"
FUNC_APP="$(az functionapp list --query "[0].name" -o tsv | tr -d '\r\n')"

echo "🔍 Verificando variables de entorno en Azure Function App..."

# Obtener todas las configuraciones
az functionapp config appsettings list \
    --name "$FUNC_APP" \
    --resource-group "$RG" \
    --output table

echo ""
echo "💡 Si faltan variables, ejecuta el script de carga de variables de entorno"
