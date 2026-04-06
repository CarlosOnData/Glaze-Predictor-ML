# Predicción de esmaltes cerámicos

Sistema de predicción de fórmulas de esmalte cerámico basado en coordenadas de color CIELAB.

Desarrollado por el Ing. Carlos Alberto Cueto Casillas como herramienta de apoyo al proceso de formulación y desarrollo de nuevos productos.

---

## ¿Qué hace?

El sistema recibe como entrada las coordenadas de color **L\*, a\*, b\*** (espacio CIELAB) de un color objetivo y predice la fórmula de ingredientes necesaria para alcanzarlo, usando un modelo de **K-Nearest Neighbors** entrenado sobre la base de datos histórica del laboratorio.

**Flujo principal:**
1. El técnico ingresa las coordenadas LAB del color deseado.
2. El modelo encuentra los 3 colores más cercanos en la base de datos.
3. Se genera una fórmula ponderada por distancia inversa, normalizada a 1 000 g de base.
4. La fórmula puede guardarse temporalmente y validarse o descartarse tras las pruebas físicas.

---

## Stack tecnológico

| Capa | Tecnología |
|------|------------|
| Interfaz | Streamlit |
| Modelo ML | scikit-learn · KNeighborsRegressor |
| Procesamiento de datos | pandas · numpy |
| Visualización | Plotly (3D, barras) |
| Conversión de color | Implementación propia CIELAB → CIE XYZ → sRGB |
| Persistencia temporal | JSON |
| Base de datos | Excel (.xlsm / .xlsx) |

---

## Estructura del proyecto

```
prediccion-Carlos/
├── app.py                  # Interfaz Streamlit (UI únicamente)
├── requirements.txt
├── .gitignore
└── src/
    ├── __init__.py
    ├── config.py           # Constantes centralizadas
    ├── model.py            # Lógica ML: carga, entrenamiento, predicción
    ├── color_utils.py      # Conversiones de color CIELAB → HEX
    └── storage.py          # Ciclo de vida de fórmulas temporales
```

---

## Instalación y uso

**Requisitos:** Python 3.10 o superior.

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/prediccion-Carlos.git
cd prediccion-Carlos

# 2. Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py
```

El archivo Excel de la base de datos **no está incluido** en el repositorio por razones de confidencialidad. Al iniciar la aplicación, puedes indicar su ruta en la barra lateral o cargarlo directamente desde el explorador de archivos.

---

## Configuración

Todos los parámetros del modelo se centralizan en `src/config.py`:

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `N_NEIGHBORS` | Vecinos para entrenamiento y predicción | `3` |
| `N_NEIGHBORS_DISPLAY` | Vecinos mostrados en la UI | `4` |
| `MAX_BASES` | Máximo de ingredientes base por fórmula | `2` |
| `DEFAULT_EXCEL_PATH` | Ruta local al Excel (dejar vacío en producción) | `""` |

---

## Formato del archivo Excel

El sistema espera una hoja llamada **`Muestras`** con al menos las columnas `L`, `A`, `B` y una columna por cada ingrediente. Las columnas de metadatos (fecha, folio, comentario, etc.) se definen en `META_COLUMNS` dentro de `config.py`.

---

## Autor

**Ing. Carlos Alberto Cueto Casillas**  
**LinkedIn: www.linkedin.com/in/carlos-cueto-859b462a5**
Guadalajara, Jalisco, México
