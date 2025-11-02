import sys
from pathlib import Path

# Obtener la ruta absoluta del directorio raíz del proyecto
# Path(__file__) es la ruta de conftest.py
# .parent es el directorio 'tests/'
# .parent.parent es el directorio raíz 'ajover/'
project_root = Path(__file__).resolve().parent.parent

# Añadir la ruta al inicio de sys.path si no está ya presente
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Opcional: Imprimir el sys.path para depuración
print("\n--- sys.path modificado por conftest.py ---")
import pprint
pprint.pprint(sys.path)
print("-------------------------------------------\n")
