"""
color_utils.py
--------------
Conversión de colores entre los espacios CIELAB → CIE XYZ → sRGB.

Referencia de iluminante: D65 (estándar CIE 1931, 2°).
"""


# ── Constantes del iluminante D65 ────────────────────────────────────────────
_Xn = 95.047
_Yn = 100.000
_Zn = 108.883


# ── Conversión LAB → XYZ ─────────────────────────────────────────────────────

def lab_to_xyz(L: float, a: float, b: float) -> tuple[float, float, float]:
    """
    Convierte coordenadas CIELAB a CIE XYZ (iluminante D65).

    Parámetros
    ----------
    L : float — Luminosidad [0, 100]
    a : float — Eje verde-rojo [-128, 127]
    b : float — Eje azul-amarillo [-128, 127]

    Retorna
    -------
    tuple (X, Y, Z) en escala D65.
    """
    def _f_inv(t: float) -> float:
        delta = 6 / 29
        return t ** 3 if t > delta else 3 * delta ** 2 * (t - 4 / 29)

    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200

    return _Xn * _f_inv(fx), _Yn * _f_inv(fy), _Zn * _f_inv(fz)


# ── Conversión XYZ → sRGB ────────────────────────────────────────────────────

def xyz_to_rgb(X: float, Y: float, Z: float) -> tuple[int, int, int]:
    """
    Convierte CIE XYZ a sRGB con corrección gamma IEC 61966-2-1.

    Parámetros
    ----------
    X, Y, Z : float — Valores CIE XYZ normalizados a D65.

    Retorna
    -------
    tuple (R, G, B) con valores enteros en [0, 255].
    """
    x, y, z = X / 100, Y / 100, Z / 100

    r_lin =  3.2406 * x - 1.5372 * y - 0.4986 * z
    g_lin = -0.9689 * x + 1.8758 * y + 0.0415 * z
    b_lin =  0.0557 * x - 0.2040 * y + 1.0570 * z

    def _gamma(c: float) -> float:
        if c <= 0.0031308:
            return 12.92 * c
        return 1.055 * (c ** (1 / 2.4)) - 0.055

    def _clamp(c: float) -> int:
        return int(max(0.0, min(1.0, _gamma(c))) * 255)

    return _clamp(r_lin), _clamp(g_lin), _clamp(b_lin)


# ── API pública ───────────────────────────────────────────────────────────────

def lab_to_hex(L: float, a: float, b: float) -> tuple[str, tuple[int, int, int]]:
    """
    Convierte coordenadas CIELAB a color hexadecimal sRGB.

    Retorna
    -------
    (hex_str, (R, G, B))
        hex_str : str  — Ej. "#A3C2F0"
        (R, G, B) : tuple[int, int, int] — Componentes [0, 255]
    """
    try:
        X, Y, Z = lab_to_xyz(L, a, b)
        r, g, bv = xyz_to_rgb(X, Y, Z)
        return f"#{r:02X}{g:02X}{bv:02X}", (r, g, bv)
    except Exception:
        return "#333333", (51, 51, 51)


def is_light_color(r: int, g: int, b: int) -> bool:
    """
    Devuelve True si el color percibido es claro (luminancia relativa > 0.5).
    Usa pesos de luminosidad SMPTE/BT.709.
    """
    return (0.2126 * r / 255 + 0.7152 * g / 255 + 0.0722 * b / 255) > 0.5
