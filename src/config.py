"""
config.py
---------
Constantes de configuración central del sistema Carlos.

Centralizar aquí todos los parámetros evita "magic numbers" dispersos
en el código y facilita el mantenimiento.
"""

# ── Ingredientes base del sistema de esmaltes ─────────────────────────────────
# Modifica esta lista si se incorporan o retiran bases del catálogo.
BASE_INGREDIENTS: list[str] = [
    "Base_01",
    "Base_02",
    "Base_03",
    "Base_04",
    "Base_05",
    "Base_06",
]

# ── Parámetros del modelo KNN ─────────────────────────────────────────────────
N_NEIGHBORS: int = 3          # Vecinos utilizados para entrenar y predecir
N_NEIGHBORS_DISPLAY: int = 4  # Vecinos mostrados en la visualización
MAX_BASES: int = 2            # Máximo de bases permitidas por fórmula para evitar combinaciones excesivamente complejas, puedes cambiarlo a tu gusto.

# ── Columnas de metadatos (no ingredientes) en el Excel ───────────────────────
META_COLUMNS: list[str] = [
    "Folio de muestra 01",
    "Folio de muestra 02",
    "Código de esmalte",
    "Fecha",
    "Comentario",
    "Proyecto",
    "L",
    "A",
    "B",
    "Acabado",
    "Efecto",
    "Tipo de material",
    "DELTA E",
    "Temperatura",
    "Agua",
    "Tiempo de quemado",
    "Tipo de horno",
    "Densidad",
]

# ── Almacenamiento temporal ───────────────────────────────────────────────────
TEMP_FORMULAS_FILE: str = "formulas_temporales.json"

# ── Ruta por defecto del archivo Excel (solo para desarrollo local) ────────────
# En producción o al compartir el repositorio, deja esto vacío ("").
DEFAULT_EXCEL_PATH: str = ""
