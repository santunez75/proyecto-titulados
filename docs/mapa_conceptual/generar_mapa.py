"""Genera el mapa conceptual tecnico de la Fase 1 como SVG (y un HTML envolvente).

El mapa se construye por codigo para que sea reproducible y versionable: cada
caja, conector y texto se declara aqui. La exportacion a PNG/PDF se realiza con
un navegador en modo headless (ver exportar.ps1).
"""

from __future__ import annotations

from pathlib import Path

AQUI = Path(__file__).resolve().parent
ANCHO, ALTO = 2400, 1660

# --- Paleta (coherente con la leyenda) --------------------------------------
C = {
    "etapa": "#1F4E79",       # azul: etapa del flujo reproducible
    "etapa_f1": "#2E75B6",    # azul claro: etapas propias de la Fase 1
    "herram": "#C55A11",      # naranja: herramienta de software cientifico
    "artef": "#2E7D32",       # verde: artefacto / producto verificable
    "doc": "#6C757D",         # gris: documentacion cientifica
    "decision": "#B8860B",    # ocre: decision preliminar
    "proy": "#9E9E9E",        # gris claro: proyectado a fases posteriores
    "fondo": "#FFFFFF",
    "panel": "#F4F6F8",
    "texto": "#212529",
    "linea": "#4A4A4A",
}

partes: list[str] = []


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def texto(x, y, s, size=20, peso="normal", color=C["texto"], anchor="start", familia="Arial", cursiva=False):
    estilo = f"font-family:{familia},Helvetica,sans-serif;font-size:{size}px;font-weight:{peso};fill:{color}"
    if cursiva:
        estilo += ";font-style:italic"
    partes.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="{estilo}">{esc(s)}</text>')


def lineas(x, y, items, size=18, dy=None, color=C["texto"], peso="normal", anchor="start", vineta=None):
    dy = dy or int(size * 1.35)
    for i, s in enumerate(items):
        pref = f"{vineta} " if vineta else ""
        texto(x, y + i * dy, pref + s, size=size, color=color, peso=peso, anchor=anchor)


def caja(x, y, w, h, titulo, cuerpo, color, size_t=22, size_c=17, radio=14, relleno=None,
         color_titulo="#FFFFFF", borde=None, dash=False, alto_titulo=None):
    relleno = relleno or C["fondo"]
    borde = borde or color
    d = ' stroke-dasharray="10,7"' if dash else ""
    at = alto_titulo or (size_t + 20)
    partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radio}" fill="{relleno}" stroke="{borde}" stroke-width="3"{d}/>')
    partes.append(f'<path d="M{x},{y + at} L{x},{y + radio} Q{x},{y} {x + radio},{y} L{x + w - radio},{y} Q{x + w},{y} {x + w},{y + radio} L{x + w},{y + at} Z" fill="{color}"/>')
    texto(x + w / 2, y + at - (at - size_t) / 2 - 2, titulo, size=size_t, peso="bold", color=color_titulo, anchor="middle")
    lineas(x + 16, y + at + size_c + 12, cuerpo, size=size_c)


def chip(x, y, w, s, color, size=16, h=None):
    h = h or size + 16
    partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{color}"/>')
    texto(x + w / 2, y + h / 2 + size * 0.36, s, size=size, color="#FFFFFF", anchor="middle", peso="bold")


def rombo(cx, cy, w, h, lineas_txt, size=15):
    partes.append(f'<polygon points="{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}" fill="#FFF8E1" stroke="{C["decision"]}" stroke-width="3"/>')
    n = len(lineas_txt)
    y0 = cy - (n - 1) * size * 0.65
    for i, s in enumerate(lineas_txt):
        texto(cx, y0 + i * size * 1.3 + size * 0.35, s, size=size, anchor="middle", color=C["texto"], peso="bold")


def flecha(x1, y1, x2, y2, color=None, dash=False, grosor=3, punta=14):
    color = color or C["linea"]
    d = ' stroke-dasharray="9,7"' if dash else ""
    partes.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{grosor}"{d}/>')
    # Punta de flecha como poligono explicito (no depende de <marker>)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - punta * math.cos(ang - 0.45), y2 - punta * math.sin(ang - 0.45))
    p2 = (x2 - punta * math.cos(ang + 0.45), y2 - punta * math.sin(ang + 0.45))
    partes.append(f'<polygon points="{x2},{y2} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


def panel(x, y, w, h, titulo, color):
    partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{C["panel"]}" stroke="{color}" stroke-width="2.5"/>')
    partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="46" rx="18" fill="{color}"/>')
    partes.append(f'<rect x="{x}" y="{y+28}" width="{w}" height="18" fill="{color}"/>')
    texto(x + 18, y + 32, titulo, size=22, peso="bold", color="#FFFFFF")


# ===========================================================================
# ENCABEZADO
# ===========================================================================
partes.append(f'<rect x="0" y="0" width="{ANCHO}" height="{ALTO}" fill="{C["fondo"]}"/>')
partes.append(f'<rect x="0" y="0" width="{ANCHO}" height="118" fill="{C["etapa"]}"/>')
texto(40, 52, "MAPA CONCEPTUAL TÉCNICO — FLUJO DE TRABAJO REPRODUCIBLE", size=34, peso="bold", color="#FFFFFF")
texto(40, 90, "Proyecto: Sobreduración en la titulación de la educación superior chilena (SIES, 2020–2025)  ·  ABP Fase 1: Definición y orientación de la situación",
      size=20, color="#DCE6F1")
texto(ANCHO - 40, 52, "Programación para la Ciencia de Datos (202682.1927)", size=19, color="#DCE6F1", anchor="end")
texto(ANCHO - 40, 84, "Sebastian Antunez Noguera  ·  Profesor: Omar Salinas  ·  Universidad Andrés Bello", size=17, color="#DCE6F1", anchor="end")

# ===========================================================================
# FILA 1: FLUJO REPRODUCIBLE (columna vertebral)
# ===========================================================================
Y1 = 150
texto(40, Y1 + 22, "1. Secuencia lógica del flujo técnico reproducible", size=24, peso="bold", color=C["etapa"])

etapas = [
    ("Situación\nproblematizadora", ["La duración teórica del plan", "existe; la duración real del", "estudiante no está publicada.", "Brecha = sobreduración."], C["etapa_f1"], "F1"),
    ("Definición del\nproyecto", ["5 preguntas de análisis", "Objetivo general + 8 OE", "Alcance: pregrado 2020–2025", "5 supuestos declarados"], C["etapa_f1"], "F1"),
    ("Entorno\nreproducible", ["venv + requirements.txt", "con versiones fijadas", "Paquete src/ modular", "Repositorio Git inicial"], C["etapa_f1"], "F1"),
    ("Obtención de\ndatos", ["6 CSV del SIES (955 MB)", "Lectura por bloques", "Integridad vs. cifras", "oficiales → Parquet"], C["etapa"], "F2"),
    ("Exploración\n(EDA)", ["Esquema y diccionario", "Distribuciones", "Faltantes y centinelas", "Inventario de calidad"], C["etapa"], "F2"),
    ("Limpieza y\ntransformación", ["Centinelas → NA", "Duplicados, atípicos", "Duración real derivada", "Bitácora de cada paso"], C["etapa"], "F2"),
    ("Validación\ntécnica", ["Motor de 11 reglas", "Pruebas automatizadas", "Determinismo del", "pipeline verificado"], C["etapa"], "F2"),
    ("Comunicación\nde resultados", ["Informe técnico PDF", "17 figuras + 13 tablas", "README técnico", "Notebooks ejecutados"], C["etapa"], "F2"),
]
artefactos = [
    "Mapa conceptual + definición",
    "F1_Definición.ipynb",
    ".venv · requirements.txt · src/",
    "consolidado.parquet (37,5 MB)",
    "hallazgos_calidad.csv",
    "dataset analítico + bitácora",
    "reporte_validacion.csv · 22 tests",
    "informe.pdf · reports/figures",
]
n = len(etapas)
margen, gap = 40, 24
w = (ANCHO - 2 * margen - gap * (n - 1)) / n
h = 150
yb = Y1 + 44
xs = []
for i, (tit, cuerpo, col, fase) in enumerate(etapas):
    x = margen + i * (w + gap)
    xs.append(x)
    t1, t2 = tit.split("\n")
    partes.append(f'<rect x="{x}" y="{yb}" width="{w:.0f}" height="{h}" rx="14" fill="#FFFFFF" stroke="{col}" stroke-width="3"/>')
    partes.append(f'<rect x="{x}" y="{yb}" width="{w:.0f}" height="58" rx="14" fill="{col}"/>')
    partes.append(f'<rect x="{x}" y="{yb+40}" width="{w:.0f}" height="18" fill="{col}"/>')
    texto(x + w / 2, yb + 25, t1, size=18, peso="bold", color="#FFFFFF", anchor="middle")
    texto(x + w / 2, yb + 48, t2, size=18, peso="bold", color="#FFFFFF", anchor="middle")
    chip(x + w - 46, yb + 6, 40, fase, "#FFFFFF" if False else "#00000055", size=13, h=22)
    lineas(x + 12, yb + 82, cuerpo, size=15, dy=19)
    # artefacto (verde) bajo la etapa
    chip(x, yb + h + 14, w, artefactos[i], C["artef"], size=14, h=30)
    if i < n - 1:
        flecha(x + w + 2, yb + h / 2, x + w + gap - 4, yb + h / 2, color=C["etapa"], grosor=4)

# Decisiones preliminares sobre las flechas
decisiones = [
    (3, ["¿Carga =", "cifras SIES?"]),
    (5, ["¿Imputar o", "descartar?"]),
    (6, ["¿Reglas", "críticas OK?"]),
]
for idx, txt in decisiones:
    cx = xs[idx] + w + gap / 2
    rombo(cx, yb - 34, 118, 60, txt, size=13)
    partes.append(f'<line x1="{cx}" y1="{yb-4}" x2="{cx}" y2="{yb + h/2 - 6}" stroke="{C["decision"]}" stroke-width="2.5" stroke-dasharray="6,5"/>')

# Flecha de continuidad hacia fases posteriores
texto(ANCHO - margen, yb + h + 70, "→ F3 modelación · F4 reporte final (proyectado)", size=15, color=C["proy"], anchor="end", cursiva=True)

# ===========================================================================
# FILA 2: HERRAMIENTAS · ARQUITECTURA DEL REPOSITORIO · DOCUMENTACIÓN
# ===========================================================================
Y2 = 470
PH = 640
PW = (ANCHO - 2 * margen - 2 * gap) / 3

# --- Panel A: herramientas ---------------------------------------------------
xa = margen
panel(xa, Y2, PW, PH, "2. Herramientas de software científico: propósito y vinculación", C["herram"])
hw = PW - 40
caja(xa + 20, Y2 + 64, hw, 104, "Git — control de versiones (local)", [
    "Función: registrar cada cambio como commit atómico y descriptivo.",
    "Ramas por fase (main / fase-2/...) y fusión explícita (--no-ff).",
    "Vincula: todo artefacto con el estado exacto del código que lo produjo.",
], C["herram"], size_t=18, size_c=14)
flecha(xa + 20 + hw / 2, Y2 + 168, xa + 20 + hw / 2, Y2 + 186, color=C["herram"])
caja(xa + 20, Y2 + 188, hw, 104, "GitHub — repositorio remoto y colaboración", [
    "Función: publicar el repositorio, compartir con el equipo y el docente.",
    "Evidencia de contribuciones individuales (commits por integrante).",
    "Vincula: README, notebooks e informe en un único punto de entrega.",
], C["herram"], size_t=18, size_c=14)
caja(xa + 20, Y2 + 312, hw, 104, "Jupyter Notebooks — documento ejecutable", [
    "Función: integrar narrativa (markdown), código y salidas en un archivo.",
    "Un notebook por etapa: F1_Definición, F2_1, F2_2, F2_3.",
    "Vincula: la decisión documentada con la celda que la ejecuta.",
], C["herram"], size_t=18, size_c=14)
caja(xa + 20, Y2 + 436, hw, 104, "Ecosistema científico de Python", [
    "pandas / NumPy: lectura por bloques, tipado, derivación de variables.",
    "Matplotlib / seaborn: figuras con estilo unificado (src/viz.py).",
    "pytest: casos normales, límite y excepciones del pipeline.",
], C["herram"], size_t=18, size_c=14)

# --- Panel B: arquitectura del repositorio -----------------------------------
xb = margen + PW + gap
panel(xb, Y2, PW, PH, "3. Arquitectura del repositorio GitHub (estructura base)", C["etapa"])
arbol = [
    ("proyecto-titulados/", True),
    ("├── README.md            descripción, estructura, ejecución", False),
    ("├── requirements.txt     dependencias con versión fijada", False),
    ("├── .gitignore           excluye data/raw (955 MB) y .venv", False),
    ("├── F1/", True),
    ("│   └── F1_Definición.ipynb", False),
    ("├── F2/", True),
    ("│   ├── F2_1_Obtencion_Exploracion.ipynb", False),
    ("│   ├── F2_2_Limpieza_Transformacion.ipynb", False),
    ("│   └── F2_3_Validacion_Analisis.ipynb", False),
    ("├── src/                 config · ingesta · limpieza ·", True),
    ("│                        transformacion · validacion · viz · pipeline", False),
    ("├── tests/               test_pipeline.py", True),
    ("├── data/                raw (no versionado) · interim · processed", True),
    ("├── reports/             figures/ · tables/", True),
    ("├── docs/                esquema SIES · mapa conceptual", True),
    ("└── informe/             PDF + DOCX + evidencias/", True),
]
for i, (s, neg) in enumerate(arbol):
    texto(xb + 22, Y2 + 78 + i * 24, s, size=15, familia="Consolas,Courier New,monospace", peso="bold" if neg else "normal")
# Criterios de versionamiento
yc = Y2 + 78 + len(arbol) * 24 + 8
partes.append(f'<rect x="{xb+16}" y="{yc}" width="{PW-32}" height="{PH-(yc-Y2)-16}" rx="10" fill="#FFFFFF" stroke="{C["etapa"]}" stroke-width="2"/>')
texto(xb + 30, yc + 26, "Criterios iniciales de versionamiento", size=17, peso="bold", color=C["etapa"])
lineas(xb + 30, yc + 50, [
    "• Commits atómicos con prefijo semántico: feat / fix / docs / test / perf / chore.",
    "• Mensaje = qué se hizo y por qué; nunca “cambios varios”.",
    "• Nada mayor a 100 MB en Git: los datos crudos se documentan, no se versionan.",
    "• Notebooks se suben ejecutados de corrido (contadores 1…N, sin errores).",
], size=14, dy=20)

# --- Panel C: documentación científica en el notebook -----------------------
xc = margen + 2 * (PW + gap)
panel(xc, Y2, PW, PH, "4. Vinculación código ↔ documentación científica", C["doc"])
cw = PW - 40
cadena = [
    ("Celda narrativa (markdown)", ["Contexto, pregunta, decisión y su justificación;", "alternativa descartada y por qué."]),
    ("Celda de código", ["Invoca funciones de src/ (no lógica suelta):", "parámetros explícitos, salida reproducible."]),
    ("Salida = evidencia", ["Tabla, figura o aserción que verifica el paso;", "se exporta a reports/ con nombre estable."]),
    ("Referencia técnica (APA 7)", ["Documentación oficial, material docente,", "fuente de datos SIES; citada en el texto."]),
    ("Informe técnico", ["Cada sección remite al notebook y al archivo", "del repositorio que la sustenta."]),
]
yy = Y2 + 64
for i, (t, cuerpo) in enumerate(cadena):
    caja(xc + 20, yy, cw, 84, t, cuerpo, C["doc"], size_t=17, size_c=14, alto_titulo=32)
    if i < len(cadena) - 1:
        flecha(xc + 20 + cw / 2, yy + 84, xc + 20 + cw / 2, yy + 98, color=C["doc"], dash=True)
    yy += 100
# Qué se documenta y dónde
yd = yy + 2
partes.append(f'<rect x="{xc+16}" y="{yd}" width="{PW-32}" height="{PH-(yd-Y2)-16}" rx="10" fill="#FFFFFF" stroke="{C["doc"]}" stroke-width="2"/>')
texto(xc + 30, yd + 24, "Qué se documenta y dónde (fases siguientes)", size=16, peso="bold", color=C["doc"])
lineas(xc + 30, yd + 46, [
    "Decisiones → docstring + celda markdown + informe   ·   Hallazgos → salidas + tables/",
    "Configuraciones → config.py + README   ·   Procedimientos → README + pipeline.py",
], size=13, dy=18)

# ===========================================================================
# FILA 3: COMMITS PROYECTADOS · REFLEXIÓN · LEYENDA
# ===========================================================================
Y3 = Y2 + PH + 30
PH3 = 350
PW3a = PW * 1.35
PW3b = PW * 0.95
PW3c = ANCHO - 2 * margen - PW3a - PW3b - 2 * gap

# --- Commits proyectados -----------------------------------------------------
panel(margen, Y3, PW3a, PH3, "5. Historial de commits proyectado (trazabilidad del avance)", C["etapa"])
commits = [
    ("chore",  "inicializa repositorio con entorno reproducible (requirements, .gitignore, README)"),
    ("feat",   "config: centraliza rutas, esquema de datos y parámetros"),
    ("feat",   "ingesta: consolida los seis años con lectura por bloques"),
    ("feat",   "limpieza: convierte códigos centinela del SIES en nulos explícitos"),
    ("feat",   "transformacion: reconstruye la duración real y la sobreduración"),
    ("feat",   "validacion: motor de reglas + test: casos normales, límite y excepciones"),
    ("docs",   "f1: notebook de definición  ·  docs(f2): notebooks de la Fase 2 ejecutados"),
    ("merge",  "integra la rama fase-2/pipeline-datos en main (--no-ff)"),
]
yl = Y3 + 66
partes.append(f'<line x1="{margen+46}" y1="{yl}" x2="{margen+46}" y2="{yl+ (len(commits)-1)*28}" stroke="{C["etapa"]}" stroke-width="3"/>')
for i, (tipo, msg) in enumerate(commits):
    y = yl + i * 28
    partes.append(f'<circle cx="{margen+46}" cy="{y}" r="7" fill="#FFFFFF" stroke="{C["etapa"]}" stroke-width="3"/>')
    chip(margen + 64, y - 12, 64, tipo, C["etapa"], size=12, h=24)
    texto(margen + 138, y + 5, msg, size=14, familia="Consolas,Courier New,monospace")

# --- Reflexión técnica -------------------------------------------------------
xr = margen + PW3a + gap
panel(xr, Y3, PW3b, PH3, "6. Reflexión técnica: principios que ordenan el flujo", C["artef"])
lineas(xr + 22, Y3 + 78, [
    "1. El código vive en src/; los notebooks orquestan y documentan.",
    "   Así notebook, línea de comandos y pruebas ejecutan lo mismo.",
    "2. Cada etapa produce un artefacto verificable (verde) que la",
    "   siguiente consume: nada se rehace, todo se puede reejecutar.",
    "3. Toda decisión se toma con datos a la vista (diagnóstico antes",
    "   del tratamiento) y queda escrita en tres lugares coherentes.",
    "4. Todo cambio queda trazado en Git; todo resultado, en el informe,",
    "   remite al archivo y a la celda que lo produjo.",
], size=15, dy=25)

# --- Leyenda -----------------------------------------------------------------
xl = xr + PW3b + gap
panel(xl, Y3, PW3c, PH3, "Leyenda", C["texto"])
ly = Y3 + 74
items_leyenda = [
    (C["etapa_f1"], "Etapa del flujo — Fase 1 (esta entrega)"),
    (C["etapa"], "Etapa del flujo — Fase 2 (sumativa)"),
    (C["herram"], "Herramienta de software científico"),
    (C["artef"], "Artefacto / producto verificable"),
    (C["doc"], "Documentación científica"),
]
for i, (col, lab) in enumerate(items_leyenda):
    partes.append(f'<rect x="{xl+22}" y="{ly + i*31 - 14}" width="30" height="22" rx="5" fill="{col}"/>')
    texto(xl + 62, ly + i * 31 + 3, lab, size=15)
ly2 = ly + len(items_leyenda) * 31 + 2
partes.append(f'<polygon points="{xl+37},{ly2-14} {xl+55},{ly2} {xl+37},{ly2+14} {xl+19},{ly2}" fill="#FFF8E1" stroke="{C["decision"]}" stroke-width="2.5"/>')
texto(xl + 62, ly2 + 5, "Decisión preliminar que orienta el análisis", size=15)
flecha(xl + 20, ly2 + 34, xl + 54, ly2 + 34, color=C["etapa"], grosor=3)
texto(xl + 62, ly2 + 39, "Flujo de datos / secuencia de etapas", size=15)
flecha(xl + 20, ly2 + 64, xl + 54, ly2 + 64, color=C["doc"], dash=True, grosor=3)
texto(xl + 62, ly2 + 69, "Documenta / registra / referencia", size=15)
chip(xl + 20, ly2 + 84, 40, "F1", "#00000055", size=12, h=22)
texto(xl + 70, ly2 + 100, "Fase del ABP en que se materializa", size=15)

# ===========================================================================
# PIE: RELACIÓN CON LAS FASES DEL ABP
# ===========================================================================
Y4 = Y3 + PH3 + 26
fases = [
    ("F1 — Definición y orientación", "Mapa conceptual (formativa) · Notebook F1 · entorno · repositorio inicial", C["etapa_f1"], False),
    ("F2 — Obtención y procesamiento", "Consolidación · EDA · limpieza · transformación · validación · informe", C["etapa"], False),
    ("F3 — Modelación", "Regresión de la sobreduración · clasificación de titulación oportuna", C["proy"], True),
    ("F4 — Reporte analítico final", "Comunicación de hallazgos con visualizaciones para público no técnico", C["proy"], True),
]
fw = (ANCHO - 2 * margen - 3 * gap) / 4
for i, (t, s, col, dash) in enumerate(fases):
    x = margen + i * (fw + gap)
    d = ' stroke-dasharray="10,7"' if dash else ""
    partes.append(f'<rect x="{x}" y="{Y4}" width="{fw:.0f}" height="70" rx="12" fill="#FFFFFF" stroke="{col}" stroke-width="3"{d}/>')
    texto(x + 16, Y4 + 28, t, size=17, peso="bold", color=col)
    texto(x + 16, Y4 + 54, s, size=14)
    if i < 3:
        flecha(x + fw + 2, Y4 + 35, x + fw + gap - 3, Y4 + 35, color=col, grosor=3)

texto(ANCHO - margen, ALTO - 16, "Generado desde docs/mapa_conceptual/generar_mapa.py · versionado junto al proyecto", size=13, color=C["proy"], anchor="end", cursiva=True)

# ===========================================================================
# ESCRITURA
# ===========================================================================
svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{ANCHO}" height="{ALTO}" viewBox="0 0 {ANCHO} {ALTO}">\n'
    + "\n".join(partes)
    + "\n</svg>\n"
)
(AQUI / "mapa_conceptual.svg").write_text(svg, encoding="utf-8")

html = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Mapa conceptual técnico</title>
<style>
  @page {{ size: {ANCHO}px {ALTO}px; margin: 0; }}
  html, body {{ margin: 0; padding: 0; background: #fff; }}
  svg {{ display: block; }}
</style></head><body>
{svg}
</body></html>
"""
(AQUI / "mapa_conceptual.html").write_text(html, encoding="utf-8")
print("SVG y HTML generados en", AQUI)
