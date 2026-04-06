"""
app.py
------
Interfaz Streamlit del Sistema de Predicción de Esmalte Cerámico elaborado por Ing.Carlos Cueto.

Cómo ejecutar:
    pip install -r requirements.txt
    streamlit run app.py
"""

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 1 — IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import math
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.color_utils import is_light_color, lab_to_hex
from src.config import (
    BASE_INGREDIENTS,
    DEFAULT_EXCEL_PATH,
    MAX_BASES,
    META_COLUMNS,
    N_NEIGHBORS,
    N_NEIGHBORS_DISPLAY,
)
from src.model import load_and_train, predict_formula
from src.storage import (
    add_temp_formula,
    load_temp_formulas,
    resolve_formula,
    write_to_excel,
)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 2 — CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Predictor de esmaltes cerámicos",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 3 — ESTILOS CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,200;0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --void:              #000000;
    --surface-0:         #080808;
    --surface-1:         #0f0f0f;
    --surface-3:         #1e1e1e;
    --glass-bg:          rgba(255,255,255,0.035);
    --glass-bg-hover:    rgba(255,255,255,0.065);
    --glass-border:      rgba(255,255,255,0.08);
    --glass-border-hov:  rgba(255,255,255,0.18);
    --glass-shine:       rgba(255,255,255,0.12);
    --glass-blur:        20px;
    --accent:            #0A84FF;
    --accent-dim:        rgba(10,132,255,0.15);
    --accent-glow:       rgba(10,132,255,0.4);
    --accent-soft:       #5AC8FA;
    --ok:                #30D158;
    --ok-dim:            rgba(48,209,88,0.15);
    --warn:              #FF9F0A;
    --warn-dim:          rgba(255,159,10,0.15);
    --err:               #FF453A;
    --err-dim:           rgba(255,69,58,0.15);
    --t1:                #F5F5F7;
    --t2:                #AEAEB2;
    --t3:                #636366;
    --t4:                #3A3A3C;
    --font-body:         'DM Sans', system-ui, sans-serif;
    --font-mono:         'DM Mono', 'SF Mono', monospace;
    --r-sm:              8px;
    --r-md:              14px;
    --r-lg:              20px;
    --r-xl:              28px;
    --r-pill:            999px;
    --shadow-sm:         0 1px 3px rgba(0,0,0,.5), 0 1px 2px rgba(0,0,0,.6);
    --shadow-md:         0 4px 16px rgba(0,0,0,.6), 0 2px 6px rgba(0,0,0,.5);
    --shadow-lg:         0 12px 40px rgba(0,0,0,.7), 0 4px 12px rgba(0,0,0,.6);
}

*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: var(--void) !important;
    font-family: var(--font-body) !important;
    color: var(--t1) !important;
    overflow-x: hidden;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(10,10,12,.85) !important;
    backdrop-filter: blur(40px) saturate(180%) !important;
    border-right: 1px solid var(--glass-border) !important;
    box-shadow: inset -1px 0 0 var(--glass-shine), 4px 0 40px rgba(0,0,0,.8) !important;
}
[data-testid="stSidebar"] * { color: var(--t1) !important; }
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    font-size: .65rem !important; font-weight: 600 !important;
    letter-spacing: .15em !important; text-transform: uppercase !important;
    color: var(--t3) !important; border-bottom: none !important;
    padding-bottom: 0 !important; margin-bottom: .75rem !important;
}
[data-testid="stSidebar"] input {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--t1) !important;
    font-family: var(--font-mono) !important;
    font-size: .9rem !important;
    transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stSidebar"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-dim) !important;
    outline: none !important;
}
[data-testid="stSidebar"] hr {
    border: none !important; height: 1px !important;
    background: var(--glass-border) !important; margin: 1.2rem 0 !important;
}

/* ── Tipografía ── */
h1, h2, h3 { font-family: var(--font-body) !important; color: var(--t1) !important; }
h1 { font-size: 2.4rem !important; font-weight: 700 !important; letter-spacing: -.03em !important; }
h2 {
    font-size: .65rem !important; font-weight: 600 !important;
    letter-spacing: .18em !important; text-transform: uppercase !important;
    color: var(--t3) !important; border-bottom: none !important;
    padding-bottom: 0 !important; margin-bottom: 1.2rem !important;
}
h3 { font-size: 1rem !important; font-weight: 500 !important; color: var(--t2) !important; }

/* ── Hero ── */
.Carlos-hero {
    position: relative; padding: 3rem 2.5rem 2.5rem; margin-bottom: 2.5rem;
    border-radius: var(--r-xl); overflow: hidden;
    background:
        radial-gradient(ellipse 70% 80% at 15% 50%, rgba(10,132,255,.12) 0%, transparent 60%),
        radial-gradient(ellipse 50% 60% at 85% 30%, rgba(255,160,80,.07) 0%, transparent 55%),
        linear-gradient(160deg,#0d0d0f 0%,#050508 100%);
    border: 1px solid var(--glass-border);
    box-shadow: var(--shadow-lg), inset 0 1px 0 var(--glass-shine);
}
.Carlos-hero::before {
    content:''; position:absolute; width:500px; height:500px; border-radius:50%;
    border:1px solid rgba(10,132,255,.1); top:-200px; right:-150px; pointer-events:none;
}
.Carlos-hero::after {
    content:''; position:absolute; width:320px; height:320px; border-radius:50%;
    border:1px solid rgba(255,160,80,.07); top:-100px; right:-80px; pointer-events:none;
}
.Carlos-hero-eyebrow {
    font-family: var(--font-mono); font-size: .65rem; font-weight: 500;
    letter-spacing: .22em; text-transform: uppercase; color: var(--accent-soft);
    margin-bottom: .75rem; display: flex; align-items: center; gap: .6rem;
}
.Carlos-hero-eyebrow::before {
    content:''; display:inline-block; width:24px; height:1px;
    background:var(--accent-soft); opacity:.6;
}
.Carlos-hero-title {
    font-size: 3rem !important; font-weight: 700 !important; letter-spacing: -.04em !important;
    color: var(--t1) !important; margin: 0 0 .35rem !important;
    line-height: 1 !important; border: none !important;
}
.Carlos-hero-sub { font-size:.85rem; color:var(--t3); font-weight:400; letter-spacing:.05em; text-transform:uppercase; }
.Carlos-hero-meta {
    display:flex; gap:1.5rem; margin-top:1.8rem; padding-top:1.5rem;
    border-top:1px solid var(--glass-border); flex-wrap:wrap;
}
.Carlos-hero-stat { display:flex; flex-direction:column; gap:.2rem; }
.Carlos-hero-stat-val { font-family:var(--font-mono); font-size:1.1rem; font-weight:500; color:var(--t1); }
.Carlos-hero-stat-label { font-size:.62rem; font-weight:600; letter-spacing:.12em; text-transform:uppercase; color:var(--t3); }

/* ── Cards ── */
.glass-card {
    position:relative; background:var(--glass-bg);
    backdrop-filter:blur(var(--glass-blur)) saturate(150%);
    border:1px solid var(--glass-border); border-radius:var(--r-lg);
    padding:1.5rem; box-shadow:var(--shadow-md),inset 0 1px 0 var(--glass-shine);
    transition:background .3s,border-color .3s,box-shadow .3s; overflow:hidden;
}
.glass-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,var(--glass-shine),transparent);
    border-radius:var(--r-lg) var(--r-lg) 0 0;
}
.glass-card:hover { background:var(--glass-bg-hover); border-color:var(--glass-border-hov); box-shadow:var(--shadow-lg),inset 0 1px 0 rgba(255,255,255,.18); }

.glass-card-accent {
    position:relative; background:var(--glass-bg);
    backdrop-filter:blur(var(--glass-blur)) saturate(150%);
    border:1px solid var(--glass-border); border-radius:var(--r-lg);
    padding:1.5rem; box-shadow:var(--shadow-md),inset 0 1px 0 var(--glass-shine); overflow:hidden;
}
.glass-card-accent::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,var(--accent),var(--accent-soft),transparent);
    border-radius:var(--r-lg) var(--r-lg) 0 0;
}

/* ── Badges ── */
.Carlos-badge {
    display:inline-flex; align-items:center; gap:.4rem; padding:.3rem .85rem;
    border-radius:var(--r-pill); font-family:var(--font-mono); font-size:.62rem;
    font-weight:500; letter-spacing:.12em; text-transform:uppercase; margin-bottom:1rem;
}
.badge-ok   { background:var(--ok-dim);     color:var(--ok);        border:1px solid rgba(48,209,88,.25); }
.badge-info { background:var(--accent-dim); color:var(--accent-soft);border:1px solid rgba(90,200,250,.25); }
.badge-warn { background:var(--warn-dim);   color:var(--warn);      border:1px solid rgba(255,159,10,.25); }
.badge-err  { background:var(--err-dim);    color:var(--err);       border:1px solid rgba(255,69,58,.25); }
.badge-dot  { width:5px;height:5px;border-radius:50%;display:inline-block;animation:pulse-dot 2s ease-in-out infinite; }
.badge-ok   .badge-dot { background:var(--ok);         box-shadow:0 0 6px var(--ok); }
.badge-info .badge-dot { background:var(--accent-soft); box-shadow:0 0 6px var(--accent-soft); }
.badge-warn .badge-dot { background:var(--warn);        box-shadow:0 0 6px var(--warn); }
@keyframes pulse-dot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.7)} }

/* ── Color preview ── */
.color-preview-wrap { border-radius:var(--r-lg); overflow:hidden; position:relative; box-shadow:var(--shadow-lg); margin-bottom:1rem; }

/* ── LAB grid ── */
.lab-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:.6rem; margin-bottom:1rem; }
.lab-metric {
    background:var(--glass-bg); border:1px solid var(--glass-border);
    border-radius:var(--r-md); padding:1rem .75rem; text-align:center;
    position:relative; overflow:hidden; transition:border-color .2s;
}
.lab-metric::before { content:''; position:absolute; top:0;left:0;right:0;height:1px;background:var(--glass-shine); }
.lab-metric-letter { font-family:var(--font-body);font-size:.6rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--accent-soft);margin-bottom:.35rem; }
.lab-metric-value  { font-family:var(--font-mono);font-size:1.25rem;font-weight:500;color:var(--t1);line-height:1; }
.lab-metric-desc   { font-size:.58rem;color:var(--t3);text-transform:uppercase;letter-spacing:.08em;margin-top:.25rem; }

/* ── Pigment card ── */
.pigment-card { background:var(--glass-bg);border:1px solid var(--glass-border);border-radius:var(--r-md);padding:1.1rem 1.25rem;display:flex;align-items:center;justify-content:space-between;gap:1rem; }
.pigment-label { font-size:.62rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--t3);margin-bottom:.2rem; }
.pigment-value { font-family:var(--font-mono);font-size:1.6rem;font-weight:500;color:var(--accent-soft);line-height:1; }
.pigment-desc  { font-size:.72rem;color:var(--t3); }

/* ── Formula rows ── */
.formula-header { display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem;padding-bottom:1rem;border-bottom:1px solid var(--glass-border); }
.formula-title  { font-size:.75rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--t2); }
.formula-legend { font-size:.62rem;color:var(--t3);font-family:var(--font-mono);display:flex;gap:.8rem;align-items:center; }
.ing-row { display:grid;grid-template-columns:1fr auto auto;align-items:center;gap:1rem;padding:.65rem 0;border-bottom:1px solid rgba(255,255,255,.04);transition:background .15s; }
.ing-row:last-child { border-bottom:none; }
.ing-row:hover { background:rgba(255,255,255,.02);border-radius:6px; }
.ing-name-wrap { display:flex;align-items:center;gap:.5rem; }
.ing-icon       { width:6px;height:6px;border-radius:50%;flex-shrink:0; }
.ing-icon-base    { background:var(--accent-soft);box-shadow:0 0 6px var(--accent); }
.ing-icon-pigment { background:var(--warn);box-shadow:0 0 6px var(--warn); }
.ing-name  { font-size:.82rem;font-weight:500;color:var(--t2);font-family:var(--font-mono);letter-spacing:.02em; }
.ing-grams { font-family:var(--font-mono);font-size:.88rem;font-weight:500;color:var(--t1);text-align:right;min-width:60px; }
.ing-bar-wrap { width:90px;height:3px;background:rgba(255,255,255,.06);border-radius:99px;overflow:hidden; }
.ing-bar-fill { height:100%;border-radius:99px;transition:width .6s cubic-bezier(.4,0,.2,1); }
.ing-bar-fill-base    { background:linear-gradient(90deg,var(--accent),var(--accent-soft)); }
.ing-bar-fill-pigment { background:linear-gradient(90deg,var(--warn),#FFD060); }
.formula-total { display:flex;justify-content:space-between;align-items:center;margin-top:1rem;padding-top:1rem;border-top:1px solid var(--glass-border); }
.formula-total-label { font-size:.62rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--t3); }
.formula-total-val   { font-family:var(--font-mono);font-size:1.1rem;font-weight:500;color:var(--accent-soft); }

/* ── Node cards ── */
.node-card {
    display:flex;align-items:center;gap:1rem;padding:.9rem 1.1rem;
    background:var(--glass-bg);border:1px solid var(--glass-border);
    border-radius:var(--r-md);margin-bottom:.6rem;
    transition:border-color .2s,background .2s;position:relative;overflow:hidden;
}
.node-card:hover { background:var(--glass-bg-hover);border-color:var(--glass-border-hov); }
.node-swatch { width:48px;height:48px;border-radius:10px;flex-shrink:0;border:1px solid rgba(255,255,255,.15);box-shadow:0 4px 12px rgba(0,0,0,.5); }
.node-info { flex:1; }
.node-rank  { font-family:var(--font-mono);font-size:.6rem;font-weight:500;letter-spacing:.15em;text-transform:uppercase;color:var(--t3);margin-bottom:.2rem; }
.node-hex   { font-family:var(--font-mono);font-size:.82rem;font-weight:500;color:var(--t1); }
.node-lab   { font-family:var(--font-mono);font-size:.7rem;color:var(--t3);margin-top:.1rem; }
.node-delta { text-align:right; }
.node-delta-label { font-size:.58rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--t3);margin-bottom:.15rem; }
.node-delta-val   { font-family:var(--font-mono);font-size:1.25rem;font-weight:500;line-height:1; }

/* ── Queue cards ── */
.queue-card {
    position:relative;background:var(--glass-bg);border:1px solid var(--glass-border);
    border-radius:var(--r-lg);padding:1.25rem 1.5rem;margin-bottom:1rem;
    overflow:hidden;transition:border-color .2s;
}
.queue-card:hover { border-color:var(--glass-border-hov); }
.queue-card::before {
    content:'';position:absolute;top:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,var(--glass-shine),transparent);
}
.queue-id   { font-family:var(--font-mono);font-size:.65rem;font-weight:500;letter-spacing:.15em;color:var(--accent-soft);text-transform:uppercase;margin-bottom:.3rem; }
.queue-op   { font-size:.95rem;font-weight:600;color:var(--t1);margin-bottom:.2rem; }
.queue-meta { font-size:.72rem;color:var(--t3);display:flex;gap:1rem;flex-wrap:wrap; }
.queue-target { margin-top:.7rem;font-family:var(--font-mono);font-size:.78rem;color:var(--t2);display:flex;gap:.8rem; }
.queue-ing  { margin-top:.5rem;font-family:var(--font-mono);font-size:.65rem;color:var(--t3); }
.queue-swatch { width:52px;height:52px;border-radius:12px;border:1px solid rgba(255,255,255,.12);flex-shrink:0;box-shadow:0 4px 16px rgba(0,0,0,.5); }
.queue-header { display:flex;align-items:flex-start;justify-content:space-between;gap:1rem; }

/* ── Section labels ── */
.section-label { display:flex;align-items:center;gap:.75rem;margin-bottom:1.2rem; }
.section-label-text { font-size:.62rem;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--t3);white-space:nowrap; }
.section-label-line { flex:1;height:1px;background:var(--glass-border); }

/* ── Buttons ── */
.stButton > button {
    background:var(--glass-bg) !important; color:var(--t1) !important;
    border:1px solid var(--glass-border) !important; border-radius:var(--r-pill) !important;
    padding:.55rem 1.5rem !important; font-family:var(--font-body) !important;
    font-size:.82rem !important; font-weight:500 !important; letter-spacing:.04em !important;
    backdrop-filter:blur(10px) !important; transition:all .25s cubic-bezier(.4,0,.2,1) !important;
    box-shadow:var(--shadow-sm) !important; position:relative !important; overflow:hidden !important;
}
.stButton > button::before {
    content:''; position:absolute; top:0;left:0;right:0;height:1px;
    background:var(--glass-shine); border-radius:var(--r-pill);
}
.stButton > button:hover {
    background:rgba(10,132,255,.15) !important; border-color:rgba(10,132,255,.5) !important;
    color:var(--accent-soft) !important; box-shadow:0 0 16px var(--accent-dim),var(--shadow-sm) !important;
    transform:translateY(-1px) !important;
}
.stButton > button:active { transform:translateY(0) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background:var(--glass-bg) !important;border-radius:var(--r-pill) !important;border:1px solid var(--glass-border) !important;padding:3px !important;gap:2px !important; }
.stTabs [data-baseweb="tab"]      { background:transparent !important;border-radius:var(--r-pill) !important;color:var(--t3) !important;font-family:var(--font-body) !important;font-size:.8rem !important;font-weight:500 !important;padding:.4rem 1.1rem !important;border:none !important;transition:all .2s !important; }
.stTabs [aria-selected="true"]    { background:var(--surface-3) !important;color:var(--t1) !important;box-shadow:var(--shadow-sm) !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:1.2rem !important; }

/* ── Expander ── */
.stExpander { background:var(--glass-bg) !important;border:1px solid var(--glass-border) !important;border-radius:var(--r-md) !important;backdrop-filter:blur(10px) !important; }
.stExpander summary { font-size:.82rem !important;font-weight:500 !important;color:var(--t2) !important; }

/* ── Alerts ── */
.stAlert { background:var(--glass-bg) !important;border:1px solid var(--glass-border) !important;border-radius:var(--r-md) !important;color:var(--t1) !important;backdrop-filter:blur(10px) !important; }

/* ── Empty state ── */
.empty-state { display:flex;flex-direction:column;align-items:center;justify-content:center;padding:4rem 2rem;text-align:center;background:var(--glass-bg);border:1px solid var(--glass-border);border-radius:var(--r-lg);border-style:dashed; }
.empty-icon  { font-size:2.5rem;opacity:.3;margin-bottom:1rem; }
.empty-text  { font-size:.82rem;color:var(--t3);line-height:1.6; }

/* ── AI detail rows ── */
.ai-detail-row { display:flex;justify-content:space-between;align-items:center;padding:.55rem 0;border-bottom:1px solid rgba(255,255,255,.04); }
.ai-detail-row:last-child { border-bottom:none; }
.ai-detail-key { font-size:.72rem;color:var(--t3);letter-spacing:.04em; }
.ai-detail-val { font-family:var(--font-mono);font-size:.78rem;color:var(--t2); }

/* ── Plotly 3D scene ── */
.stApp { overflow-x:hidden !important; }
.transicion-inmersiva { height:120px;margin-top:3rem;position:relative;background:linear-gradient(to bottom,var(--void) 0%,#000 100%);width:100%; }
.transicion-inmersiva::before,.transicion-inmersiva::after { content:"";position:absolute;top:0;bottom:0;width:50vw;background:linear-gradient(to bottom,var(--void) 0%,#000 100%); }
.transicion-inmersiva::before { right:100%; }
.transicion-inmersiva::after  { left:100%; }
.contenedor-textos-inmersivos { padding:2rem 0;position:relative;background-color:#000;width:100%; }
.contenedor-textos-inmersivos::before,.contenedor-textos-inmersivos::after { content:"";position:absolute;top:0;bottom:0;width:50vw;background-color:#000; }
.contenedor-textos-inmersivos::before { right:100%; }
.contenedor-textos-inmersivos::after  { left:100%; }
.titulo-inmersivo { color:white !important;text-align:center;border-bottom:none !important;font-family:'DM Sans',sans-serif;font-size:.65rem !important;font-weight:600 !important;letter-spacing:.2em !important;text-transform:uppercase !important;color:var(--t4) !important; }
div[data-testid="stPlotlyChart"] { position:relative;background-color:#000 !important;padding-bottom:2rem;width:100% !important;overflow:visible !important; }
div[data-testid="stPlotlyChart"]::before,div[data-testid="stPlotlyChart"]::after { content:"";position:absolute;top:0;bottom:0;width:50vw;background-color:#000;z-index:0; }
div[data-testid="stPlotlyChart"]::before { right:100%; }
div[data-testid="stPlotlyChart"]::after  { left:100%; }
.transicion-inmersiva-abajo { height:120px;margin-top:-2.5rem;margin-bottom:2rem;position:relative;background:linear-gradient(to bottom,#000 0%,var(--void) 100%);z-index:10;width:100%; }
.transicion-inmersiva-abajo::before,.transicion-inmersiva-abajo::after { content:"";position:absolute;top:0;bottom:0;width:50vw;background:linear-gradient(to bottom,#000 0%,var(--void) 100%); }
.transicion-inmersiva-abajo::before { right:100%; }
.transicion-inmersiva-abajo::after  { left:100%; }

/* ── Misc ── */
.stDataFrame { background:var(--glass-bg) !important;border:1px solid var(--glass-border) !important;border-radius:var(--r-md) !important;overflow:hidden !important; }
.stDownloadButton > button { background:var(--glass-bg) !important;color:var(--t2) !important;border:1px solid var(--glass-border) !important;border-radius:var(--r-pill) !important;font-size:.78rem !important;font-weight:500 !important;font-family:var(--font-mono) !important;letter-spacing:.06em !important;padding:.45rem 1.2rem !important;transition:all .2s !important; }
.stDownloadButton > button:hover { background:var(--accent-dim) !important;border-color:rgba(10,132,255,.4) !important;color:var(--accent-soft) !important; }

/* ── Footer ── */
.Carlos-footer { display:flex;justify-content:center;align-items:center;gap:1.5rem;padding:2rem 0;margin-top:4rem;border-top:1px solid var(--glass-border); }
.Carlos-footer-text { font-family:var(--font-mono);font-size:.62rem;font-weight:400;letter-spacing:.12em;text-transform:uppercase;color:var(--t4); }
.Carlos-footer-dot  { width:3px;height:3px;border-radius:50%;background:var(--t4); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 4 — ENCABEZADO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="Carlos-hero">
    <div class="Carlos-hero-eyebrow">Predicción de esmaltes cerámicos</div>
    <h1 class="Carlos-hero-title">Predicción Carlos</h1>
    <p class="Carlos-hero-sub">Sistema de Predicción de Esmalte Cerámico</p>
    <div class="Carlos-hero-meta">
        <div class="Carlos-hero-stat">
            <span class="Carlos-hero-stat-val">KNN</span>
            <span class="Carlos-hero-stat-label">Algoritmo</span>
        </div>
        <div class="Carlos-hero-stat">
            <span class="Carlos-hero-stat-val">CIELAB</span>
            <span class="Carlos-hero-stat-label">Espacio de color</span>
        </div>
        <div class="Carlos-hero-stat">
            <span class="Carlos-hero-stat-val">sRGB</span>
            <span class="Carlos-hero-stat-label">Formato de color</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 5 — SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Base de Datos")

    excel_path = st.text_input(
        "Ruta del archivo Excel",
        value=DEFAULT_EXCEL_PATH,
        help="Ruta completa al archivo .xlsm o .xlsx de la base de datos.",
    )
    uploaded_file = st.file_uploader("O carga el archivo", type=["xlsx", "xlsm"])

    st.markdown("---")
    st.markdown("## Color Objetivo (LAB)")
    L_val = st.number_input("L*  Luminosidad",     min_value=0.0,    max_value=100.0, value=50.5,  step=0.01)
    A_val = st.number_input("a*  Verde ↔ Rojo",    min_value=-128.0, max_value=127.0, value=-30.5, step=0.01)
    B_val = st.number_input("b*  Azul ↔ Amarillo", min_value=-128.0, max_value=127.0, value=40.5,  step=0.01)

    st.markdown("---")
    st.markdown("## Modificador de Pigmento")
    pigment_slider = st.slider("Reducción (%)", min_value=0, max_value=100, value=50, step=5)

    st.markdown("---")
    predict_btn = st.button("Iniciar Predicción", use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 6 — CARGA DEL MODELO
# ─────────────────────────────────────────────────────────────────────────────
data_source = uploaded_file if uploaded_file is not None else excel_path
model, scaler, ingredient_cols, X_orig, y_orig, n_samples, load_error = load_and_train(data_source)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 7 — DISPARAR PREDICCIÓN
# ─────────────────────────────────────────────────────────────────────────────
if predict_btn and not load_error:
    with st.spinner("Calculando fórmula óptima..."):
        formula, status, avg_dist, neighbor_idx, neighbor_dist = predict_formula(
            model, scaler, ingredient_cols,
            L_val, A_val, B_val,
            pigment_slider / 100.0,
        )
        # Persiste en sesión para que sobreviva reruns de Streamlit
        st.session_state.update({
            "formula":        formula,
            "status":         status,
            "avg_dist":       avg_dist,
            "neighbor_idx":   neighbor_idx,
            "neighbor_dist":  neighbor_dist,
            "last_L":         L_val,
            "last_A":         A_val,
            "last_B":         B_val,
            "last_pigment":   pigment_slider,
            "has_prediction": True,
        })


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 8 — ÁREA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
if load_error:
    st.markdown(f"""
    <div class="Carlos-badge badge-err"><span class="badge-dot"></span>Error del Sistema</div>
    <div class="glass-card-accent">
        <p style="color:var(--err);margin:0 0 .5rem;font-weight:600;">⚠ {load_error}</p>
        <p style="font-size:.8rem;color:var(--t3);margin:0;">
            Verifica la ruta del archivo y el formato (.xlsx / .xlsm).
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    col_left, col_right = st.columns([4, 6])

    # ── Columna izquierda: Color Target ──────────────────────────────────────
    with col_left:
        st.markdown("""
        <div class="section-label">
            <span class="section-label-text">Color Target</span>
            <span class="section-label-line"></span>
        </div>
        """, unsafe_allow_html=True)

        hex_color, (r_c, g_c, b_c) = lab_to_hex(L_val, A_val, B_val)
        text_color = "#000000" if is_light_color(r_c, g_c, b_c) else "#FFFFFF"

        st.markdown(f"""
        <div class="color-preview-wrap">
            <div style="background:{hex_color};padding:2.2rem 1.5rem 1.8rem;position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:0;right:0;height:50%;background:linear-gradient(to bottom,rgba(255,255,255,.12) 0%,transparent 100%);pointer-events:none;"></div>
                <div style="text-align:center;position:relative;z-index:1;">
                    <div style="font-family:'DM Mono',monospace;font-size:1.6rem;font-weight:400;color:{text_color};letter-spacing:.08em;text-shadow:0 1px 4px rgba(0,0,0,.3);">{hex_color}</div>
                    <div style="font-family:'DM Mono',monospace;font-size:.72rem;color:{text_color};opacity:.65;margin-top:.3rem;letter-spacing:.1em;">RGB({r_c}, {g_c}, {b_c})</div>
                </div>
            </div>
            <div style="height:6px;background:{hex_color};filter:blur(8px);opacity:.7;margin-top:-3px;"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="lab-grid">
            <div class="lab-metric">
                <div class="lab-metric-letter">L*</div>
                <div class="lab-metric-value">{L_val:.2f}</div>
                <div class="lab-metric-desc">Luminosidad</div>
            </div>
            <div class="lab-metric">
                <div class="lab-metric-letter">a*</div>
                <div class="lab-metric-value">{A_val:.2f}</div>
                <div class="lab-metric-desc">Verde ↔ Rojo</div>
            </div>
            <div class="lab-metric">
                <div class="lab-metric-letter">b*</div>
                <div class="lab-metric-value">{B_val:.2f}</div>
                <div class="lab-metric-desc">Azul ↔ Amarillo</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pigment_desc = (
            "Sin reducción — pureza total"
            if pigment_slider == 0
            else f"Factor aplicado al {100 - pigment_slider}% de la masa base"
        )
        st.markdown(f"""
        <div class="pigment-card">
            <div>
                <div class="pigment-label">Reducción de Pigmento</div>
                <div class="pigment-desc">{pigment_desc}</div>
            </div>
            <div class="pigment-value">{pigment_slider}%</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Motor IA — Parámetros"):
            st.markdown(f"""
            <div class="ai-detail-row"><span class="ai-detail-key">Algoritmo</span><span class="ai-detail-val">KNN Regressor</span></div>
            <div class="ai-detail-row"><span class="ai-detail-key">Vecindad (k)</span><span class="ai-detail-val">{N_NEIGHBORS} nodos</span></div>
            <div class="ai-detail-row"><span class="ai-detail-key">Límite de bases</span><span class="ai-detail-val">{MAX_BASES} componentes</span></div>
            <div class="ai-detail-row"><span class="ai-detail-key">Dataset</span><span class="ai-detail-val">{n_samples:,} muestras</span></div>
            <div class="ai-detail-row"><span class="ai-detail-key">Ponderación</span><span class="ai-detail-val">Distancia inversa</span></div>
            """, unsafe_allow_html=True)

    # ── Columna derecha: Matriz de Fórmula ───────────────────────────────────
    with col_right:
        st.markdown("""
        <div class="section-label">
            <span class="section-label-text">Matriz de Fórmula</span>
            <span class="section-label-line"></span>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.get("has_prediction", False):
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">◎</div>
                <div class="empty-text">
                    Ingresa coordenadas LAB y presiona<br>
                    <strong style="color:var(--t2);">Iniciar Predicción</strong> para generar la matriz.
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            formula       = st.session_state["formula"]
            status        = st.session_state["status"]
            neighbor_idx  = st.session_state["neighbor_idx"]
            neighbor_dist = st.session_state["neighbor_dist"]
            L_req         = st.session_state["last_L"]
            A_req         = st.session_state["last_A"]
            B_req         = st.session_state["last_B"]
            pigment_req   = st.session_state["last_pigment"]

            _STATUS_BADGE = {
                "exacto":  ("badge-ok",   "◉ Match Exacto"),
                "nuevo":   ("badge-info", "◈ Predicción Óptima"),
                "inusual": ("badge-warn", "⚠ Outlier — Verificar"),
            }
            badge_cls, badge_txt = _STATUS_BADGE.get(status, ("badge-err", "Estado Anómalo"))
            st.markdown(
                f'<div class="Carlos-badge {badge_cls}"><span class="badge-dot"></span>{badge_txt}</div>',
                unsafe_allow_html=True,
            )

            if formula.empty:
                st.warning("No se hallaron componentes para esta configuración.")
            else:
                _render_formula_card(formula, pigment_req)

                csv_df = formula.reset_index()
                csv_df.columns = ["Componente", "Gramos"]
                csv_df[["L", "A", "B"]] = L_req, A_req, B_req
                st.download_button(
                    "↓ Exportar CSV",
                    data=csv_df.to_csv(index=False, encoding="utf-8-sig"),
                    file_name=f"formula_L{L_req}_A{A_req}_B{B_req}.csv",
                    mime="text/csv",
                )

            st.markdown("""
            <div class="section-label" style="margin-top:1.5rem;">
                <span class="section-label-text">Vectores Cercanos</span>
                <span class="section-label-line"></span>
            </div>
            """, unsafe_allow_html=True)

            tab_visual, tab_matrix, tab_spectrum = st.tabs(
                ["Análisis Visual", "Matriz de Nodos", "Espectro"]
            )

            with tab_visual:
                _render_neighbor_visual(neighbor_idx, neighbor_dist, L_req, A_req, B_req)

            with tab_matrix:
                _render_neighbor_matrix(neighbor_idx, neighbor_dist, L_req, A_req, B_req)

            with tab_spectrum:
                _render_spectrum_chart(formula, neighbor_idx)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 9 — VISUALIZACIÓN 3D CIELAB INMERSIVA
# ─────────────────────────────────────────────────────────────────────────────
if not load_error:
    _render_3d_lab_scatter()


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 10 — COLA DE FÓRMULAS TEMPORALES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-label" style="margin-top:1rem;">
    <span class="section-label-text">Entorno de Pruebas</span>
    <span class="section-label-line"></span>
</div>
<p style="font-size:.78rem;color:var(--t3);margin-bottom:1.2rem;margin-top:-.6rem;">
    Fórmulas en experimentación · Registro de resultados
</p>
""", unsafe_allow_html=True)

if st.session_state.get("has_prediction", False):
    with st.expander("Almacenar Iteración Temporal"):
        cg1, cg2 = st.columns([3, 2])
        with cg1:
            operator_input = st.text_input("Operador", placeholder="Ej: C. Cueto", key="inp_operator")
        with cg2:
            notes_input = st.text_input("Log (opcional)", placeholder="Ej: reducción 30%", key="inp_notes")

        if st.button("Confirmar Registro", key="btn_save"):
            if not operator_input.strip():
                st.error("Se requiere ID de Operador para registrar.")
            else:
                record_id = add_temp_formula(
                    L=st.session_state["last_L"],
                    A=st.session_state["last_A"],
                    B=st.session_state["last_B"],
                    formula=st.session_state["formula"],
                    operator=operator_input.strip(),
                    notes=notes_input.strip(),
                    pigment_pct=st.session_state["last_pigment"],
                )
                st.success(f"Iteración registrada · SYS_ID #{record_id}")
                st.rerun()

all_formulas = load_temp_formulas()
pending = [(i, rec) for i, rec in enumerate(all_formulas) if rec["status"] == "pendiente"]

if not pending:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">◻</div>
        <div class="empty-text">Cola de procesos vacía<br>Las iteraciones guardadas aparecerán aquí.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for list_idx, record in pending:
        _render_queue_card(record, list_idx, excel_path)

resolved = [(i, rec) for i, rec in enumerate(all_formulas) if rec["status"] != "pendiente"]
if resolved:
    with st.expander(f"Histórico del Sistema · {len(resolved)} registros"):
        history_rows = []
        for _, rec in resolved:
            lab_t = rec["target_lab"]
            lab_r = rec.get("actual_lab", {})
            history_rows.append({
                "ID": rec["id"], "Timestamp": rec["timestamp"],
                "Operador": rec["operator"], "Status": rec["status"].upper(),
                "L_t": lab_t["L"], "a_t": lab_t["A"], "b_t": lab_t["B"],
                "L_r": lab_r.get("L", "—"), "a_r": lab_r.get("A", "—"), "b_r": lab_r.get("B", "—"),
                "Log": rec.get("notes", ""),
            })
        st.dataframe(pd.DataFrame(history_rows), hide_index=True, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 11 — TABS INFORMATIVOS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<hr style='border:none;height:1px;background:var(--glass-border);margin:2rem 0 1.5rem;'>", unsafe_allow_html=True)

tab_help, tab_bases_info, tab_about = st.tabs([
    "Instrucciones de uso",
    "Bases de esmalte registradas",
    "Información del sistema",
])

with tab_help:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
**Protocolo de uso:**
1. Sincronizar archivo Excel
2. Ingresar coordenadas LAB
3. Ajustar modificador de pigmento
4. Ejecutar **Iniciar Predicción**
5. Evaluar visualización CIELAB
6. Almacenar iteración temporal
7. Validar o descartar resultados
""")
    with c2:
        st.markdown("""
**Indicadores de Estado:**
- **Match Exacto** — Color idéntico en la base de datos.
- **Predicción Óptima** — Aproximación cercana (distancia < 1.5).
- **Outlier** — Evaluar manualmente.

**Tolerancia ΔE:**
- 0 – 1.0 → Imperceptible al ojo
- 1.0 – 5.0 → Rango visible
- > 5.0 → Desviación mayor
""")

with tab_bases_info:
    st.markdown("Componentes catalogados como **Bases** en el sistema:")
    cols = st.columns(4)
    for i, base in enumerate(BASE_INGREDIENTS):
        cols[i % 4].markdown(f"`{base}`")

with tab_about:
    st.markdown(f"""
**Sistema de predicción Carlos**

- Lógica de predicción: K-Nearest Neighbors Regressor
- k = {N_NEIGHBORS} vecinos · Límite de bases: {MAX_BASES}
- Motor de conversión de color: CIELAB → CIE XYZ → sRGB

**Sistema predicción para apoyo en la formulación, elaboración y desarrollo de nuevos productos.**

Desarrollado por el Ing. Carlos Alberto Cueto Casillas
""")


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 12 — FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="Carlos-footer">
    <span class="Carlos-footer-text">Sistema de predicción de esmaltes</span>
    <span class="Carlos-footer-text">Ing. Carlos Alberto Cueto Casillas</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 13 — FUNCIONES DE RENDERIZADO (helpers privados)
# Se definen DESPUÉS del flujo principal para no interrumpir la lectura.
# Python las resuelve en tiempo de ejecución, no en tiempo de definición.
# ─────────────────────────────────────────────────────────────────────────────

def _render_formula_card(formula: pd.Series, pigment_pct: int) -> None:
    """Renderiza la tarjeta de fórmula con barras proporcionales."""
    max_val = formula.max()
    legend = f"Pigmentos al {100 - pigment_pct}%" if pigment_pct > 0 else "Análisis base completo"

    rows_html = ""
    for name, grams in formula.items():
        pct = (grams / max_val * 100) if max_val > 0 else 0
        is_base = name in BASE_INGREDIENTS
        icon_cls = "ing-icon-base" if is_base else "ing-icon-pigment"
        bar_cls  = "ing-bar-fill-base" if is_base else "ing-bar-fill-pigment"
        rows_html += f"""
<div class="ing-row">
  <div class="ing-name-wrap">
    <div class="ing-icon {icon_cls}"></div>
    <span class="ing-name">{name}</span>
  </div>
  <span class="ing-grams">{grams:.1f} g</span>
  <div class="ing-bar-wrap">
    <div class="ing-bar-fill {bar_cls}" style="width:{pct:.1f}%"></div>
  </div>
</div>"""

    st.markdown(f"""
<div class="glass-card-accent">
  <div class="formula-header">
    <span class="formula-title">Componentes</span>
    <span class="formula-legend">
      <span style="color:var(--accent-soft);">● Base</span>
      <span style="color:var(--warn);">● Pigmento</span>
      <span style="color:var(--t3);">· {legend}</span>
    </span>
  </div>
  {rows_html}
  <div class="formula-total">
    <span class="formula-total-label">Total Output</span>
    <span class="formula-total-val">{formula.sum():.1f} g</span>
  </div>
</div>
""", unsafe_allow_html=True)


def _render_neighbor_visual(
    neighbor_idx: list, neighbor_dist: list,
    L_req: float, A_req: float, B_req: float,
) -> None:
    """Renderiza las tarjetas de colores vecinos con ΔE."""
    for rank, (idx, dist) in enumerate(zip(neighbor_idx, neighbor_dist)):
        Lv, Av, Bv = X_orig[idx, 0], X_orig[idx, 1], X_orig[idx, 2]
        hex_v, _ = lab_to_hex(Lv, Av, Bv)
        delta_e = math.sqrt((L_req - Lv) ** 2 + (A_req - Av) ** 2 + (B_req - Bv) ** 2)

        if delta_e < 2:   de_color = "var(--ok)"
        elif delta_e < 5: de_color = "var(--warn)"
        else:             de_color = "var(--err)"

        st.markdown(f"""
<div class="node-card">
  <div style="position:absolute;top:0;left:0;bottom:0;width:2px;background:linear-gradient(to bottom,{hex_v},{hex_v}88);"></div>
  <div class="node-swatch" style="background:{hex_v};box-shadow:0 4px 16px {hex_v}55;"></div>
  <div class="node-info">
    <div class="node-rank">Nodo #{rank+1} · dist {dist:.3f}</div>
    <div class="node-hex">{hex_v}</div>
    <div class="node-lab">L={Lv:.2f} · a={Av:.2f} · b={Bv:.2f}</div>
  </div>
  <div class="node-delta">
    <div class="node-delta-label">ΔE</div>
    <div class="node-delta-val" style="color:{de_color};">{delta_e:.2f}</div>
  </div>
</div>
""", unsafe_allow_html=True)


def _render_neighbor_matrix(
    neighbor_idx: list, neighbor_dist: list,
    L_req: float, A_req: float, B_req: float,
) -> None:
    """Renderiza la tabla de nodos vecinos con sus fórmulas."""
    rows = []
    for rank, (idx, dist) in enumerate(zip(neighbor_idx, neighbor_dist)):
        Lv, Av, Bv = X_orig[idx, 0], X_orig[idx, 1], X_orig[idx, 2]
        delta_e = math.sqrt((L_req - Lv) ** 2 + (A_req - Av) ** 2 + (B_req - Bv) ** 2)
        row = {"Nodo": f"#{rank+1}", "L*": round(Lv, 2), "a*": round(Av, 2), "b*": round(Bv, 2), "ΔE": round(delta_e, 2)}
        neighbor_formula = y_orig.iloc[idx]
        for ing, grams in neighbor_formula[neighbor_formula > 0].sort_values(ascending=False).items():
            row[str(ing)] = round(grams, 1)
        rows.append(row)
    st.dataframe(pd.DataFrame(rows).fillna(""), use_container_width=True, hide_index=True)


def _render_spectrum_chart(formula: pd.Series, neighbor_idx: list) -> None:
    """Renderiza el gráfico de barras comparativo entre la fórmula predicha y los vecinos."""
    all_ingredients = set(formula[formula > 0].index.tolist())
    for idx in neighbor_idx:
        nf = y_orig.iloc[idx]
        all_ingredients.update(nf[nf > 0].index.tolist())
    all_ingredients = sorted(all_ingredients)

    if not all_ingredients:
        return

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Output Predicho", x=all_ingredients,
        y=[formula.get(ing, 0) for ing in all_ingredients],
        marker_color="#5AC8FA", marker_line_color="#0A84FF", marker_line_width=1.2,
    ))

    neighbor_colors = [
        "rgba(255,255,255,0.35)", "rgba(255,255,255,0.22)",
        "rgba(255,255,255,0.14)", "rgba(255,255,255,0.08)",
    ]
    for rank, idx in enumerate(neighbor_idx):
        nf = y_orig.iloc[idx]
        vals = [float(nf.get(ing, 0)) if ing in nf.index else 0.0 for ing in all_ingredients]
        fig.add_trace(go.Bar(
            name=f"Nodo #{rank+1}", x=all_ingredients, y=vals,
            marker_color=neighbor_colors[rank % len(neighbor_colors)], opacity=0.9,
        ))

    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#AEAEB2", size=11),
        legend=dict(bgcolor="rgba(15,15,15,0.9)", bordercolor="rgba(255,255,255,0.08)", borderwidth=1, font=dict(size=11)),
        margin=dict(l=0, r=0, t=12, b=0), height=360,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(family="DM Mono", size=9)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(family="DM Mono", size=9)),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_3d_lab_scatter() -> None:
    """Renderiza la visualización 3D inmersiva del espacio CIELAB."""
    st.markdown('<div class="transicion-inmersiva"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="contenedor-textos-inmersivos">
        <h2 class="titulo-inmersivo">Espacio CIELAB · Visualización 3D</h2>
    </div>
    """, unsafe_allow_html=True)

    # Calcula colores y textos para cada punto del dataset
    colors_db = []
    hover_db  = []
    for i in range(len(X_orig)):
        Lv, Av, Bv = X_orig[i, 0], X_orig[i, 1], X_orig[i, 2]
        hex_v, _ = lab_to_hex(Lv, Av, Bv)
        colors_db.append(hex_v)

        active_ing = y_orig.iloc[i]
        active_ing = active_ing[active_ing > 0].sort_values(ascending=False)
        ing_str = "<br>".join([f"· {ing}: {g:.1f} g" for ing, g in active_ing.items()]) or "Sin ingredientes"
        hover_db.append(f"L={Lv:.1f} · a={Av:.1f} · b={Bv:.1f}<br><br><b>Fórmula:</b><br>{ing_str}")

    fig = go.Figure()

    # Dataset completo
    fig.add_trace(go.Scatter3d(
        x=X_orig[:, 1], y=X_orig[:, 2], z=X_orig[:, 0],
        mode="markers",
        marker=dict(size=4, color=colors_db, opacity=0.55),
        name="Base de datos",
        hovertext=hover_db,
        hovertemplate="%{hovertext}<extra></extra>",
    ))

    # Vecinos y objetivo (solo si hay predicción activa)
    if st.session_state.get("has_prediction", False):
        n_idx  = st.session_state["neighbor_idx"][:3]
        L_req  = st.session_state["last_L"]
        A_req  = st.session_state["last_A"]
        B_req  = st.session_state["last_B"]
        hex_req, _ = lab_to_hex(L_req, A_req, B_req)

        fig.add_trace(go.Scatter3d(
            x=X_orig[n_idx, 1], y=X_orig[n_idx, 2], z=X_orig[n_idx, 0],
            mode="markers",
            marker=dict(size=10, color=[colors_db[i] for i in n_idx], opacity=1, line=dict(color="white", width=2)),
            name="3 colores más cercanos",
            hovertext=[hover_db[i] for i in n_idx],
            hovertemplate="<b>Color Cercano</b><br>%{hovertext}<extra></extra>",
        ))
        fig.add_trace(go.Scatter3d(
            x=[A_req], y=[B_req], z=[L_req],
            mode="markers",
            marker=dict(size=14, color=hex_req, symbol="diamond", line=dict(color="white", width=3)),
            name="Color solicitado",
            hovertemplate=f"<b>Objetivo</b><br>L={L_req} · a={A_req} · b={B_req}<extra></extra>",
        ))

    # Ejes de referencia
    axes = [
        ([0, 0], [0, 0], [0, 100]),
        ([-128, 128], [0, 0], [50, 50]),
        ([0, 0], [-128, 128], [50, 50]),
    ]
    for ax, ay, az in axes:
        fig.add_trace(go.Scatter3d(x=ax, y=ay, z=az, mode="lines", line=dict(color="rgba(255,255,255,0.25)", width=1.5), hoverinfo="none", showlegend=False))

    # Etiquetas de ejes
    fig.add_trace(go.Scatter3d(
        x=[0, 0, 135, -135, 0, 0],
        y=[0, 0, 0, 0, 135, -135],
        z=[105, -5, 50, 50, 50, 50],
        mode="text",
        text=["L+ (Blanco)", "L− (Negro)", "a+ (Rojo)", "a− (Verde)", "b+ (Amarillo)", "b− (Azul)"],
        textfont=dict(color="rgba(255,255,255,0.45)", size=11),
        hoverinfo="none", showlegend=False,
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-140, 140]),
            yaxis=dict(visible=False, range=[-140, 140]),
            zaxis=dict(visible=False, range=[-10, 110]),
            bgcolor="#000000", aspectmode="cube",
        ),
        paper_bgcolor="#000000", plot_bgcolor="#000000",
        legend=dict(font=dict(color="rgba(255,255,255,0.6)", size=11, family="DM Sans"), bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=0, b=0), height=800,
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="transicion-inmersiva-abajo"></div>', unsafe_allow_html=True)


def _render_queue_card(record: dict, list_idx: int, excel_path: str) -> None:
    """Renderiza una tarjeta de fórmula en cola con controles de validación."""
    lab = record["target_lab"]
    hex_t, _ = lab_to_hex(lab["L"], lab["A"], lab["B"])
    ing_preview = " · ".join([f"{k}: {v}g" for k, v in list(record["formula"].items())[:4]])
    if len(record["formula"]) > 4:
        ing_preview += f" · +{len(record['formula'])-4} más"

    st.markdown(f"""
<div class="queue-card">
  <div class="queue-header">
    <div>
      <div class="queue-id">SYS_ID #{record['id']}</div>
      <div class="queue-op">{record['operator']}</div>
      <div class="queue-meta">
        <span>📅 {record['timestamp']}</span>
        <span>⬤ Pigmento {record['pigment_pct']}%</span>
        {'<span>📝 ' + record['notes'] + '</span>' if record.get('notes') else ''}
      </div>
      <div class="queue-target">
        <span>L={lab['L']}</span><span>a={lab['A']}</span><span>b={lab['B']}</span>
      </div>
      <div class="queue-ing">{ing_preview}</div>
    </div>
    <div class="queue-swatch" style="background:{hex_t};box-shadow:0 4px 16px {hex_t}55;"></div>
  </div>
</div>
""", unsafe_allow_html=True)

    with st.expander(f"Inspeccionar Matriz · SYS_ID #{record['id']}"):
        df_t = pd.DataFrame(list(record["formula"].items()), columns=["Componente", "Masa (g)"])
        df_t["Clase"] = df_t["Componente"].apply(lambda x: "Base" if x in BASE_INGREDIENTS else "Pigmento")
        st.dataframe(df_t[["Clase", "Componente", "Masa (g)"]], hide_index=True, use_container_width=True)

    btn1, btn2, _ = st.columns([2, 2, 3])

    with btn1:
        if st.button(f"Validar #{record['id']}", key=f"accept_{record['id']}_{list_idx}"):
            resolve_formula(list_idx, "aceptada")
            if excel_path and os.path.exists(excel_path):
                updated = load_temp_formulas()[list_idx]
                ok, err = write_to_excel(excel_path, updated)
                st.success(f"SYS_ID #{record['id']} integrado a la base." if ok else f"Error en Excel: {err}")
            else:
                st.success("Aceptada en memoria.")
            st.rerun()

    with btn2:
        if st.button(f"Descartar #{record['id']}", key=f"reject_{record['id']}_{list_idx}"):
            st.session_state[f"reject_form_{record['id']}"] = True

    if st.session_state.get(f"reject_form_{record['id']}", False):
        st.markdown(f"**Registrar desviación LAB — SYS_ID #{record['id']}**")
        r1, r2, r3, r4 = st.columns([1, 1, 1, 1])
        with r1: L_r = st.number_input("L* real", value=float(lab["L"]), step=0.01, key=f"Lr_{record['id']}")
        with r2: A_r = st.number_input("a* real", value=float(lab["A"]), step=0.01, key=f"Ar_{record['id']}")
        with r3: B_r = st.number_input("b* real", value=float(lab["B"]), step=0.01, key=f"Br_{record['id']}")
        with r4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"Aplicar #{record['id']}", key=f"confirm_reject_{record['id']}"):
                resolve_formula(list_idx, "rechazada", L_r, A_r, B_r)
                if excel_path and os.path.exists(excel_path):
                    updated = load_temp_formulas()[list_idx]
                    ok, err = write_to_excel(excel_path, updated)
                    st.success("Log registrado." if ok else f"Error I/O: {err}")
                else:
                    st.success("Log registrado en memoria.")
                st.session_state[f"reject_form_{record['id']}"] = False
                st.rerun()

    st.markdown("<hr style='border:none;height:1px;background:var(--glass-border);margin:.8rem 0;'>", unsafe_allow_html=True)
