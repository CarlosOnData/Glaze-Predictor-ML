"""
storage.py
----------
Gestión del ciclo de vida de fórmulas temporales.

Las fórmulas predichas se almacenan en un archivo JSON local mientras esperan
validación en laboratorio. Una vez resueltas (aceptadas o rechazadas).
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Literal

import pandas as pd

from src.config import TEMP_FORMULAS_FILE


# ── Tipos ─────────────────────────────────────────────────────────────────────

FormulaStatus = Literal["pendiente", "aceptada", "rechazada"]


# ── Lectura / escritura del JSON ──────────────────────────────────────────────

def load_temp_formulas() -> list[dict]:
    """Carga la lista de fórmulas temporales desde disco."""
    if not os.path.exists(TEMP_FORMULAS_FILE):
        return []
    try:
        with open(TEMP_FORMULAS_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return []


def _save_temp_formulas(formulas: list[dict]) -> None:
    """Persiste la lista de fórmulas temporales en disco."""
    with open(TEMP_FORMULAS_FILE, "w", encoding="utf-8") as fh:
        json.dump(formulas, fh, ensure_ascii=False, indent=2)


# ── Operaciones de dominio ────────────────────────────────────────────────────

def add_temp_formula(
    L: float,
    A: float,
    B: float,
    formula: pd.Series,
    operator: str,
    notes: str,
    pigment_pct: int,
) -> int:
    """
    Registra una nueva fórmula temporal en la cola de espera.

    Retorna
    -------
    int — ID asignado al registro.
    """
    formulas = load_temp_formulas()

    record: dict = {
        "id": len(formulas) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "operator": operator,
        "notes": notes,
        "target_lab": {"L": L, "A": A, "B": B},
        "pigment_pct": pigment_pct,
        "formula": formula.round(2).to_dict(),
        "status": "pendiente",
    }

    formulas.append(record)
    _save_temp_formulas(formulas)
    return record["id"]


def resolve_formula(
    list_index: int,
    decision: FormulaStatus,
    L_result: float | None = None,
    A_result: float | None = None,
    B_result: float | None = None,
) -> dict:
    """
    Marca una fórmula temporal como aceptada o rechazada.

    Si se rechaza, se pueden registrar las coordenadas LAB reales obtenidas
    en laboratorio para trazabilidad.

    Parámetros
    ----------
    list_index : int — Índice (0-based) en la lista de fórmulas temporales.
    decision   : 'aceptada' | 'rechazada'
    L_result, A_result, B_result : coordenadas LAB reales (solo para rechazos).

    Retorna
    -------
    dict — El registro actualizado.
    """
    formulas = load_temp_formulas()
    record = formulas[list_index]

    record["status"] = decision
    record["resolved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    if decision == "rechazada" and L_result is not None:
        record["actual_lab"] = {"L": L_result, "A": A_result, "B": B_result}

    _save_temp_formulas(formulas)
    return record


# ── Integración con Excel ─────────────────────────────────────────────────────

def write_to_excel(excel_path: str, record: dict) -> tuple[bool, str | None]:
    """
    Agrega la fórmula resuelta a la hoja 'Muestras' del archivo Excel.

    Utiliza las coordenadas LAB objetivo para fórmulas aceptadas, y las
    coordenadas reales para las rechazadas (si están disponibles).

    Retorna
    -------
    (success: bool, error_message: str | None)
    """
    try:
        df = pd.read_excel(excel_path, engine="openpyxl", sheet_name="Muestras")

        if record["status"] == "aceptada":
            lab = record["target_lab"]
        else:
            lab = record.get("actual_lab", record["target_lab"])

        comment = (
            f"[Carlos App] {record['status'].upper()} · "
            f"{record['operator']} · {record.get('notes', '')}"
        )

        new_row: dict = {
            "Fecha": record["resolved_at"],
            "L": lab["L"],
            "A": lab["A"],
            "B": lab["B"],
            "Comentario": comment,
            **record["formula"],
        }

        df_updated = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        with pd.ExcelWriter(
            excel_path, engine="openpyxl", mode="a", if_sheet_exists="overlay"
        ) as writer:
            df_updated.to_excel(writer, sheet_name="Muestras", index=False)

        return True, None

    except Exception as exc:
        return False, str(exc)
