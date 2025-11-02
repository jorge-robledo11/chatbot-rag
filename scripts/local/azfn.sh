#!/bin/bash
set -e

echo "🔧 Configurando entorno de desarrollo local para Azure Functions..."

# Crear un directorio temporal para la ejecución de la función.
# Este se eliminará automáticamente al salir del script.
TMP_DIR=$(mktemp -d)
FUNC_DIR="azure-fn"

# Registrar una función de limpieza que se ejecuta al salir del script (EXIT)
# o al recibir señales de interrupción (INT) o terminación (TERM).
# Esto asegura que el directorio temporal siempre se borre.
trap 'echo ""; echo "🧹 Limpiando directorio temporal ($TMP_DIR)..."; rm -rf "$TMP_DIR"' EXIT INT TERM

echo "📁 Directorio de trabajo temporal creado en: $TMP_DIR"

# 1. Validar ejecución desde la raíz del proyecto
if [ ! -f "$FUNC_DIR/function_app.py" ]; then
    echo "❌ Error: Este script debe ser ejecutado desde la raíz del proyecto."
    exit 1
fi

# 2. Configurar entorno Python
export PYTHONPATH="$(pwd):$PYTHONPATH"

# 3. Regenerar requirements.txt desde pyproject.toml si es necesario
if [ ! -f requirements.txt ] || [ pyproject.toml -nt requirements.txt ]; then
    echo "🔨 Generando requirements.txt desde pyproject.toml..."
    uv export \
      --only-group azure \
      --no-hashes --no-header --no-annotate \
      --output-file requirements.txt
fi

# 4. Preparar el directorio de la función, simulando el Dockerfile
echo "📦 Preparando el directorio temporal con copias de los archivos..."
cp azure-fn/function_app.py       "$TMP_DIR/function_app.py"
cp azure-fn/host.json             "$TMP_DIR/host.json"
cp azure-fn/local.settings.json   "$TMP_DIR/local.settings.json"
cp requirements.txt               "$TMP_DIR/requirements.txt"
cp -r backend/                    "$TMP_DIR/backend"

# 5. Iniciar el host de Azure Functions
echo "🚀 Iniciando Azure Functions en http://localhost:7071..."
uv run func start --script-root "$TMP_DIR" --port 7071

# El script se detendrá aquí hasta que 'func start' termine (e.g., con Ctrl+C).
# La trampa 'trap' se encargará de la limpieza automáticamente al salir.