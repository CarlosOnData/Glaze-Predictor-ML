"""
model.py
--------
Lógica de entrenamiento y predicción del modelo KNN para fórmulas de esmalte cerámico.

El modelo recibe coordenadas de color CIELAB (L*, a*, b*) y predice la composición
de ingredientes necesaria para alcanzar ese color objetivo.
"""

from __future__ import annotations

import io
from typing import Union

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler

from src.config import (
    BASE_INGREDIENTS,
    MAX_BASES,
    META_COLUMNS,
    N_NEIGHBORS,
    N_NEIGHBORS_DISPLAY,
)


# ── Tipos ─────────────────────────────────────────────────────────────────────

DataSource = Union[str, "UploadedFile"]  # ruta local o archivo subido por Streamlit


# ── Carga y entrenamiento ─────────────────────────────────────────────────────

@st.cache_data
def load_and_train(source: DataSource):
    """
    Lee el archivo Excel y entrena el modelo KNN.

    Parámetros
    ----------
    source : str | UploadedFile
        Ruta local al .xlsm/.xlsx o archivo subido mediante st.file_uploader.

    Retorna
    -------
    modelo        : KNeighborsRegressor entrenado
    scaler        : StandardScaler ajustado a los datos de entrenamiento
    ingredient_cols : list[str] — nombres de columnas de ingredientes
    X_original    : np.ndarray — coordenadas LAB originales
    y_original    : pd.DataFrame — composiciones originales
    n_samples     : int — número de muestras en la BD
    error         : str | None — mensaje de error, o None si todo salió bien
    """
    try:
        raw_bytes = _read_source(source)
        df = pd.read_excel(io.BytesIO(raw_bytes), engine="openpyxl", sheet_name="Muestras")

        X = df[["L", "A", "B"]].apply(pd.to_numeric, errors="coerce").fillna(0)
        y = (
            df.drop(columns=META_COLUMNS, errors="ignore")
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
        )

        X_original = X.values
        y_original = y.copy()

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, _, y_train, _ = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        model = KNeighborsRegressor(n_neighbors=N_NEIGHBORS, weights="distance")
        model.fit(X_train, y_train)

        return model, scaler, y.columns.tolist(), X_original, y_original, len(df), None

    except FileNotFoundError:
        return None, None, None, None, None, 0, f"Archivo no encontrado: {source}"
    except Exception as exc:
        return None, None, None, None, None, 0, f"Error al cargar: {exc}"


def _read_source(source: DataSource) -> bytes:
    """Lee los bytes del archivo, ya sea desde disco o desde un UploadedFile."""
    if hasattr(source, "read"):
        return source.getvalue()
    with open(source, "rb") as fh:
        return fh.read()


# ── Predicción ────────────────────────────────────────────────────────────────

def predict_formula(
    model: KNeighborsRegressor,
    scaler: StandardScaler,
    ingredient_cols: list[str],
    L: float,
    A: float,
    B: float,
    pigment_reduction: float,
) -> tuple[pd.Series, str, float, np.ndarray, np.ndarray]:
    """
    Predice la fórmula óptima para el color objetivo (L, A, B).

    Parámetros
    ----------
    model              : KNeighborsRegressor entrenado
    scaler             : StandardScaler ajustado
    ingredient_cols    : nombres de columnas de ingredientes
    L, A, B            : coordenadas CIELAB del color objetivo
    pigment_reduction  : fracción de reducción de pigmento [0.0, 1.0]

    Retorna
    -------
    formula_adjusted : pd.Series — gramos por ingrediente (ordenado desc.)
    status           : str — 'exacto' | 'nuevo' | 'inusual'
    avg_distance     : float — distancia promedio a los vecinos
    neighbor_indices : np.ndarray — índices en el dataset original
    neighbor_distances : np.ndarray — distancias a cada vecino
    """
    target = pd.DataFrame({"L": [L], "A": [A], "B": [B]})
    target_scaled = scaler.transform(target)

    raw_prediction = model.predict(target_scaled)

    n_neighbors_actual = min(N_NEIGHBORS_DISPLAY, model.n_samples_fit_)
    neighbor_distances, neighbor_indices = model.kneighbors(
        target_scaled, n_neighbors=n_neighbors_actual
    )
    avg_distance = float(np.mean(neighbor_distances[0]))

    predicted = pd.Series(raw_prediction[0], index=ingredient_cols)
    active = predicted[predicted > 0].sort_values(ascending=False)

    bases = active[active.index.isin(BASE_INGREDIENTS)]
    pigments = active[~active.index.isin(BASE_INGREDIENTS)]

    formula_adjusted = _build_adjusted_formula(bases, pigments, pigment_reduction)

    status = _classify_status(avg_distance)

    return (
        formula_adjusted,
        status,
        avg_distance,
        neighbor_indices[0],
        neighbor_distances[0],
    )


def _build_adjusted_formula(
    bases: pd.Series,
    pigments: pd.Series,
    pigment_reduction: float,
) -> pd.Series:
    """
    Normaliza bases a 1 000 g y aplica el factor de reducción a los pigmentos.

    La fórmula estándar de Carlos trabaja sobre una base de 1000 g, por lo que
    todas las bases se reescalan a ese total. Los pigmentos se ajustan con el
    factor (1 - pigment_reduction).
    """
    base_fraction = 1 - pigment_reduction
    formula = pd.Series(dtype=float)

    top_bases = bases.nlargest(MAX_BASES)
    bases_sum = top_bases.sum()
    if bases_sum > 0:
        formula = pd.concat([formula, top_bases * (1_000 / bases_sum)])

    original_bases_sum = bases.sum()
    if not pigments.empty:
        if original_bases_sum > 0:
            scaled_pigments = pigments * (1_000 / original_bases_sum) * base_fraction
        else:
            scaled_pigments = pigments * base_fraction
        formula = pd.concat([formula, scaled_pigments])

    return formula.sort_values(ascending=False)


def _classify_status(avg_distance: float) -> str:
    """Clasifica la calidad de la predicción según la distancia media al vecino."""
    if avg_distance == 0:
        return "exacto"
    if avg_distance < 1.5:
        return "nuevo"
    return "inusual"
