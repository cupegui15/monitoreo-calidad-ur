import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import time
import textwrap
import tempfile
import requests
import base64
from io import BytesIO

# ===============================
# CONFIGURACIÓN PRINCIPAL
# ===============================
st.set_page_config(page_title="Monitoreo de Calidad UR", layout="wide", page_icon="📋")

# ===============================
# IMÁGENES INSTITUCIONALES
# ===============================
URL_LOGO_UR = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQY0ZMIXOVuzLond_jNv713shc6TmUWej0JDQ&s"
URL_BANNER_IMG = "https://uredu-my.sharepoint.com/personal/cristian_upegui_urosario_edu_co/Documents/Imagenes/Imagen%201.jpg"

# ===============================
# CSS INSTITUCIONAL
# ===============================
st.markdown("""
<style>
:root {
    --rojo-ur: #9B0029;
    --gris-fondo: #f8f8f8;
    --texto: #222;
}
html, body, .stApp {
    background-color: var(--gris-fondo) !important;
    color: var(--texto) !important;
    font-family: "Segoe UI", sans-serif;
}
[data-testid="stSidebar"] {
    background-color: var(--rojo-ur) !important;
}
[data-testid="stSidebar"] * {
    color: #fff !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] option,
[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #000 !important;
    background-color: #fff !important;
    font-weight: 500 !important;
}
.banner {
    background-color: var(--rojo-ur);
    color: white;
    padding: 1.3rem 2rem;
    border-radius: 8px;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.section-title {
    color: var(--rojo-ur);
    font-weight: 700;
    font-size: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.card {
    background-color: #ffffff;
    padding: 1.2rem 1.4rem;
    border-radius: 10px;
    border: 1px solid #e6e6e6;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}
.card-title {
    font-weight: 600;
    color: #9B0029;
    margin-bottom: 0.6rem;
}
textarea {
    background-color: #fafafa !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# CONFIGURACIÓN DE ÁREAS Y CANALES
# ===============================
areas = {
    "Casa UR": {
        "canales": ["Presencial", "Contact Center", "Chat", "Back Office", "Servicio"],
        "monitores": [
            "Mauricio Ramirez Cubillos",
            "Alejandro Parra Sánchez",
            "Cristian Alberto Upegui M",
            "IA"
        ],
        "asesores": [
            "Adela Bogotá Cagua","David Esteban Puerto Salgado",
            "Diana Marcela Sánchez Cano","Diana Milena Nieto Perez",
            "Jenny Lorena Quintero","Jhon Estiverson Caballero",
            "Jose Edwin Navarro Rondon","Laura Alejandra Bernal Perez","Leidy Johanna Alonso Rincón",
            "Leyner Anyul Silva Avila","Martha Soraya Monsalve Fonseca",
            "Nancy Viviana Bulla Bustos","Nelson Peña Ramírez",
            "Solangel Milena Rodriguez Quitian","Leidy Sofia Ramirez Paez","Nathalia Andrea Bernal Lara",
            "Rafael Ricardo Garcia Gutierrez - TMP", "Jhojan Esteban Quiroga Mendez - TMP"
        ]
    },
    "Conecta UR": {
        "canales": ["Linea", "Chat", "Sitio", "Servicio"],
        "monitores": [
            "Johanna Rueda Cuvajante",
            "Cristian Alberto Upegui M",
            "IA"
        ],
        "asesores": [
            "Juan Sebastian Silva Gomez","Jennyfer Caicedo Alfonso",
            "Jerly Durley Mendez Fontecha","Addison Rodriguez Casallas",
            "Gabriel Ferney Martinez Lopez","Juan David Gonzalez Jimenez",
            "Miguel Angel Rico Acevedo","Juan Camilo Ortega Clavijo",
            "Andres Fernando Galindo Algarra","Adrian Jose Sosa Gil","Juan David Gonzalez Jimenez",
            "Andrea Katherine Torres Junco","Leidi Daniela Arias Rodriguez"
        ]
    }
}

# ===============================
# PREGUNTAS POR CANAL (FUENTE ÚNICA)
# ===============================
def obtener_preguntas(area, canal):
    if area == "Casa UR":

        if canal in ["Presencial", "Contact Center"]:
            return [
                "¿Atiende la interacción en el momento que se establece contacto con el(a) usuario(a)?",
                "¿Saluda, se presenta de una forma amable y cortés, usando el dialogo de saludo y bienvenida?",
                "¿Realiza la validación de identidad del usuario y personaliza la interacción de forma adecuada garantizando la confidencialidad de la información?",
                "¿Escucha activamente al usuario y realiza preguntas adicionales demostrando atención y concentración?",
                "¿Consulta todas las herramientas disponibles para estructurar la posible respuesta que se le brindará al usuario?",
                "¿Controla los tiempos de espera informando al usuario y realizando acompañamiento cada 2 minutos?",
                "¿Brinda respuesta de forma precisa, completa y coherente, de acuerdo a lo solicitado por el usuario?",
                "¿Valida con el usuario si la información fue clara, completa o si requiere algún trámite adicional?",
                "¿Documenta la atención de forma coherente según lo solicitado e informado al cliente; seleccionando las tipologías adecuadas y manejando correcta redacción y ortografía?",
                "¿Finaliza la atención de forma amable, cortés utilizando el dialogo de cierre y despedida remitiendo al usuario a responder la encuesta de percepción?"
            ]

        elif canal == "Chat":
            return [
                "¿Escucha activamente al usuario y realiza preguntas adicionales demostrando atención y concentración?",
                "¿Consulta todas las herramientas disponibles para estructurar la posible respuesta que se le brindará al usuario?",
                "¿Controla los tiempos de espera informando al usuario y realizando acompañamiento cada 2 minutos?",
                "¿Brinda respuesta de forma precisa, completa y coherente, de acuerdo a lo solicitado por el usuario?",
                "¿Valida con el usuario si la información fue clara, completa o si requiere algún trámite adicional?",
                "¿Documenta la atención de forma coherente según lo solicitado e informado al cliente; seleccionando las tipologías adecuadas y manejando correcta redacción y ortografía?"
            ]

        elif canal == "Back Office":
            return [
                "¿Cumple con el ANS establecido para el servicio?",
                "¿Analiza correctamente la solicitud?",
                "¿Gestiona adecuadamente en SAP/UXXI/Bizagi?",
                "¿Respuesta eficaz de acuerdo a la solicitud radicada por el usuario?",
                "¿Es empático al cerrar la solicitud?"
            ]
        elif canal == "Servicio":
            return [
                "¿Atiende la interacción en el momento que se establece contacto con el(a) usuario(a)?",
                "¿Saluda, se presenta de una forma amable y cortés, usando el dialogo de saludo y bienvenida?",
                "¿Realiza la validación de identidad del usuario y personaliza la interacción de forma adecuada garantizando la confidencialidad de la información?",
                "¿Escucha activamente al usuario y realiza preguntas adicionales demostrando atención y concentración?",
                "¿Controla los tiempos de espera informando al usuario y realizando acompañamiento cada 2 minutos?",
                "¿Valida con el usuario si la información fue clara, completa o si requiere algún trámite adicional?",
                "¿Finaliza la atención de forma amable, cortés utilizando el dialogo de cierre y despedida remitiendo al usuario a responder la encuesta de percepción?"
            ]

    elif area == "Conecta UR":

        if canal == "Linea":
            return [
                "¿Atiende la interacción de forma oportuna en el momento que se establece el contacto?",
                "¿Saluda y se presenta de manera amable y profesional, estableciendo un inicio cordial de la atención?",
                "¿Realiza la validación de identidad del usuario garantizando confidencialidad y aplica protocolos de seguridad de la información?",
                "¿Escucha activamente al usuario y formula preguntas pertinentes para un diagnóstico claro y completo?",
                "¿Consulta y utiliza todas las herramientas de soporte disponibles (base de conocimiento, sistemas, documentación) para estructurar una respuesta adecuada?",
                "¿Gestiona adecuadamente los tiempos de espera, manteniendo informado al usuario y realizando acompañamiento oportuno durante la interacción?",
                "¿Sigue el flujo definido para solución o escalamiento, asegurando trazabilidad y cumplimiento de procesos internos?",
                "¿Valida con el usuario que la información brindada es clara, completa y confirma si requiere trámites o pasos adicionales?",
                "¿Documenta la atención en el sistema de tickets de manera coherente, seleccionando tipologías correctas y con redacción/ortografía adecuadas?",
                "¿Finaliza la atención de forma amable y profesional, utilizando el cierre de interacción definido y remitiendo al usuario a la encuesta de satisfacción?"
            ]

        elif canal == "Chat":
            return [
                "¿Escucha activamente al usuario y formula preguntas pertinentes para un diagnóstico claro y completo?",
                "¿Consulta y utiliza todas las herramientas de soporte disponibles (base de conocimiento, sistemas, documentación) para estructurar una respuesta adecuada?",
                "¿Gestiona adecuadamente los tiempos de espera, manteniendo informado al usuario y realizando acompañamiento oportuno durante la interacción?",
                "¿Sigue el flujo definido para solución o escalamiento, asegurando trazabilidad y cumplimiento de procesos internos?",
                "¿Valida con el usuario que la información brindada es clara, completa y confirma si requiere trámites o pasos adicionales?",
                "¿Documenta la atención en el sistema de tickets de manera coherente, seleccionando tipologías correctas y con redacción/ortografía adecuadas?"
            ]

        elif canal == "Sitio":
            return [
                "¿Cómo califica el tiempo de respuesta de su solicitud?",
                "¿Cómo califica la amabilidad y la actitud de servicio del técnico durante la atención brindada?",
                "¿Cómo califica la presentación personal del técnico, incluyendo el uso adecuado de la chaqueta institucional, durante la visita?",
                "¿El Tecnico de soporte en sitio logró solucionar su requerimiento en esta visita?",
                "¿Qué probabilidad hay de que recomiendes los servicios de CONECTA UR a tus compañeros y amigos?"
            ]
        if canal == "Servicio":
            return [
                "¿Atiende la interacción en el momento que se establece contacto con el(a) usuario(a)?",
                "¿Saluda, se presenta de una forma amable y cortés, usando el dialogo de saludo y bienvenida?",
                "¿Realiza la validación de identidad del usuario y personaliza la interacción de forma adecuada garantizando la confidencialidad de la información?",
                "¿Escucha activamente al usuario y realiza preguntas adicionales demostrando atención y concentración?",
                "¿Controla los tiempos de espera informando al usuario y realizando acompañamiento cada 2 minutos?",
                "¿Valida con el usuario si la información fue clara, completa o si requiere algún trámite adicional?",
                "¿Finaliza la atención de forma amable, cortés utilizando el dialogo de cierre y despedida remitiendo al usuario a responder la encuesta de percepción?"
            ]

# ===============================
# PESOS POR CANAL
# ===============================
def obtener_pesos(area, canal):
    if area == "Casa UR":
        if canal in ["Presencial", "Contact Center"]:
            return [9, 9, 9, 9, 9, 9, 14, 8, 14, 10]
        elif canal == "Chat":
            return [20, 15, 15, 15, 15, 20]
        elif canal == "Back Office":
            return [20, 20, 20, 20, 20]
        elif canal == "Servicio":
            return [15, 15, 15, 15, 10, 15, 15]

    if area == "Conecta UR":
        if canal == "Linea":
            return [9, 9, 9, 9, 9, 9, 14, 8, 14, 10]
        elif canal == "Chat":
            return [20, 15, 15, 15, 15, 20]
        elif canal == "Sitio":
            return [20, 20, 20, 20, 20]
        elif canal == "Servicio":
            return [15, 15, 15, 15, 10, 15, 15]
    return []

# ===============================
# PESO GLOBAL POR CANAL (RESULTADO FINAL)
# ===============================
PESOS_GLOBALES_CANAL = {
    "Servicio": 0.30  # Atención Servicio
}
PESO_OTROS_CANALES = 0.70
# ===============================
# SOPORTE WRAP PLOTLY
# ===============================
def envolver_pregunta(texto: str, ancho: int = 45) -> str:
    if not isinstance(texto, str):
        return str(texto)
    return "<br>".join(textwrap.wrap(texto.strip(), width=ancho, break_long_words=False))

def _lineas_wrap(s: str) -> int:
    if not isinstance(s, str) or not s:
        return 1
    return s.count("<br>") + 1

def ajustar_grafico_horizontal(fig, df_plot: pd.DataFrame, col_wrapped: str = "Pregunta_wrapped"):
    """
    Ajuste visual homologado para todos los gráficos horizontales:
    - y-axis title: "Criterio evaluado"
    - letra más grande en etiquetas
    - altura dinámica según líneas reales
    """
    if df_plot.empty or col_wrapped not in df_plot.columns:
        total_lineas = 1
    else:
        total_lineas = int(df_plot[col_wrapped].apply(_lineas_wrap).sum())

    height = max(520, 180 + (total_lineas * 32))

    fig.update_layout(
        height=height,
        margin=dict(l=360, r=70, t=70, b=40),
        bargap=0.35
    )
    fig.update_yaxes(
        title_text="Criterio evaluado",
        automargin=True,
        tickfont=dict(size=13, color="#2c2c2c")
    )
    fig.update_xaxes(
        tickfont=dict(size=12),
        title_font=dict(size=13)
    )
    fig.update_coloraxes(
        colorbar_title="Cumplimiento (%)",
        colorbar_title_font=dict(size=12),
        colorbar_tickfont=dict(size=11)
    )
    return fig
# ===============================
# Calculos Por Canal
# ===============================

def calcular_ponderado_por_asesor(df_asesor):
    """
    Ponderación final por asesor:
    - Servicio: 30 %
    - Otros canales: 70 %
    Usa la columna 'Total'
    """

    if df_asesor.empty:
        return 0.0

    # 🔥 Forzar Total a numérico
    df_asesor["Total"] = pd.to_numeric(
        df_asesor["Total"], errors="coerce"
    ).fillna(0)

    servicio = df_asesor[df_asesor["Canal"] == "Servicio"]["Total"]
    otros = df_asesor[df_asesor["Canal"] != "Servicio"]["Total"]

    promedio_servicio = servicio.mean() if not servicio.empty else None
    promedio_otros = otros.mean() if not otros.empty else None

    if promedio_servicio is not None and promedio_otros is not None:
        return round((promedio_servicio * 0.30) + (promedio_otros * 0.70), 2)

    if promedio_servicio is not None:
        return round(promedio_servicio, 2)

    if promedio_otros is not None:
        return round(promedio_otros, 2)

    return 0.0

# ===============================
# GOOGLE SHEETS: GUARDAR
# ===============================
def guardar_datos_google_sheets(data, intentos=3):
    for intento in range(intentos):
        try:
            for k, v in data.items():
                if isinstance(v, date):
                    data[k] = v.strftime("%Y-%m-%d")

            creds_json = st.secrets["GCP_SERVICE_ACCOUNT"]
            creds_dict = json.loads(creds_json)

            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]

            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            sh = client.open_by_key(st.secrets["GOOGLE_SHEETS_ID"])

            area = data["Área"]
            canal = data["Canal"]

            if area == "Casa UR":
                nombre_hoja = f"Casa UR - {canal}"
            elif area == "Conecta UR":
                nombre_hoja = f"Conecta UR - {canal}"
            else:
                nombre_hoja = f"{area} - {canal}"

            hoja = sh.worksheet(nombre_hoja)

            encabezados = hoja.row_values(1)

            fila = [data.get(col, "") for col in encabezados]
            hoja.append_row(fila)

            return  # éxito

        except Exception as e:
            if intento < intentos - 1:
                time.sleep(2)  # espera 2 segundos y reintenta
            else:
                st.error(f"❌ Error al guardar después de varios intentos: {e}")

# ===============================
# GOOGLE SHEETS: CARGAR TODAS LAS HOJAS
# ===============================
@st.cache_data(ttl=600)  # ⏱️ Cache por 10 minutos (ajustable)
def cargar_todas_las_hojas_google_sheets():
    try:
        # ================= CREDENCIALES =================
        creds_json = st.secrets["GCP_SERVICE_ACCOUNT"]
        creds_dict = json.loads(creds_json)

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        sh = client.open_by_key(st.secrets["GOOGLE_SHEETS_ID"])

        # ================= LECTURA DE HOJAS =================
        dfs = []

        for ws in sh.worksheets():
            title = ws.title.strip()

            # Validar formato "Área - Canal"
            if " - " not in title:
                continue

            area_name, canal_name = [x.strip() for x in title.split(" - ", 1)]

            # Validar área y canal permitidos
            if area_name not in areas:
                continue

            if canal_name not in areas[area_name]["canales"]:
                continue

            records = ws.get_all_records()
            if not records:
                continue

            df_temp = pd.DataFrame(records)
            df_temp.columns = [str(c).strip() for c in df_temp.columns]

            # ================= PROCESAR PREGUNTAS =================
            preguntas_def = obtener_preguntas(area_name, canal_name)

            for p in preguntas_def:
                if p in df_temp.columns:
                    df_temp[p] = (
                        pd.to_numeric(df_temp[p], errors="coerce")
                        .fillna(0)
                    )

            # ================= METADATA =================
            df_temp["Área"] = area_name
            df_temp["Canal"] = canal_name

            dfs.append(df_temp)

        if not dfs:
            return pd.DataFrame()

        return pd.concat(dfs, ignore_index=True)

    except Exception as e:
        st.error(f"⚠️ Error cargando datos: {e}")
        return pd.DataFrame()
# ===============================
# RESET TOTAL DEL FORMULARIO
# ===============================
def resetear_formulario(area_actual: str, canal_actual: str):
    # Campos base
    st.session_state["f_area"] = "Seleccione una opción"
    st.session_state["f_monitor"] = "Seleccione una opción"
    st.session_state["f_asesor"] = "Seleccione una opción"
    st.session_state["f_canal"] = None
    st.session_state["f_codigo"] = ""
    st.session_state["f_fecha"] = date.today()
    st.session_state["f_error"] = "No"
    st.session_state["f_pos"] = ""
    st.session_state["f_mej"] = ""

    # Radios de preguntas (si estaban renderizadas)
    try:
        preguntas = obtener_preguntas(area_actual, canal_actual)
        for q in preguntas:
            k = f"q_{abs(hash((area_actual, canal_actual, q)))%10**10}"
            if k in st.session_state:
                del st.session_state[k]
    except:
        pass
# ===============================
# SIDEBAR Y MENÚ
# ===============================
st.sidebar.image(URL_LOGO_UR, width=150)
pagina = st.sidebar.radio(
    "Menú:",
    [
        "📝 Formulario de Monitoreo",
        "📊 Dashboard Casa UR",
        "📈 Dashboard Conecta UR",
        "🎯 Dashboard por Asesor",
        "📥 Descarga de resultados",
        "🧠 IA"
    ]
)

def consolidar_texto(serie):
    textos = serie.dropna().astype(str)
    items = []
    for t in textos:
        for x in t.split("\n"):
            x = x.strip()
            if x:
                items.append(x)
    return "\n".join(sorted(set(items)))

def mostrar_tabla_errores_criticos(df_filtrado, titulo="Errores Críticos Detectados"):
    df_ec = df_filtrado[df_filtrado["Error crítico"] == "Sí"]

    if df_ec.empty:
        return

    st.markdown(f"""
    <div style="
        background-color:#fff4e5;
        padding:16px;
        border-left:6px solid #9B0029;
        border-radius:10px;
        margin-bottom:18px;">
        <h4 style="color:#9B0029; margin-bottom:6px;">⚠️ {titulo}</h4>
        <p style="margin-bottom:0;">
        Se identificaron errores críticos en el periodo seleccionado. 
        Estos casos requieren seguimiento prioritario.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tabla = df_ec[[
        "Asesor",
        "Monitor",
        "Canal",
        "Fecha",
        "Aspectos por Mejorar"
    ]].copy()

    tabla["Fecha"] = tabla["Fecha"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        tabla.sort_values(["Asesor", "Fecha"]),
        use_container_width=True,
        hide_index=True
    )

# ===============================
# BANNER
# ===============================
st.markdown(f"""
<div class="banner">
    <div>
        <h2>Monitoreo de Calidad - Universidad del Rosario</h2>
        <p>Comprometidos con la excelencia en la atención al usuario</p>
    </div>
    <div><img src="{URL_BANNER_IMG}" width="130" style="border-radius:6px;"></div>
</div>
""", unsafe_allow_html=True)

    # ===============================
    # FUNCIÓN TRANSCRIPCIÓN GEMINI
    # ===============================
def transcribir_audio_gemini(audio_file):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]

        audio_file.seek(0)
        audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash-lite:generateContent?key={api_key}"

        headers = {"Content-Type": "application/json"}

        body = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": audio_file.type,
                                "data": audio_base64
                            }
                        },
                        {
                            "text": "Transcribe este audio completamente en texto claro en español."
                        }
                    ]
                }
            ]
        }

        # 🔁 Primer intento
        response = requests.post(url, headers=headers, json=body, timeout=60)

        # 🔥 Si se excede cuota
        if response.status_code == 429:
            try:
                error_json = response.json()
                retry_info = error_json.get("error", {}).get("details", [])
                retry_seconds = 45  # fallback

                for detail in retry_info:
                    if detail.get("@type") == "type.googleapis.com/google.rpc.RetryInfo":
                        retry_delay = detail.get("retryDelay", "45s")
                        retry_seconds = int(retry_delay.replace("s", ""))

                st.warning(f"⚠️ Límite alcanzado. Esperando {retry_seconds} segundos...")
                time.sleep(retry_seconds)

                # 🔁 Segundo intento
                response = requests.post(url, headers=headers, json=body, timeout=60)

            except:
                st.error("Se alcanzó el límite diario gratuito. Intenta nuevamente mañana.")
                return None

        if response.status_code != 200:
            st.error(f"Error Gemini: {response.text}")
            return None

        result = response.json()

        if "candidates" not in result:
            st.error("Gemini no devolvió respuesta válida.")
            return None

        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        st.error(f"Error en transcripción con Gemini: {e}")
        return None

if pagina == "📝 Formulario de Monitoreo":

    st.markdown('<div class="section-title">🧾 Registro de Monitoreo</div>', unsafe_allow_html=True)

    # =====================================================
    # SECCIÓN 1 — DATOS GENERALES
    # =====================================================
    c1, c2 = st.columns(2)

    with c1:
        area = st.selectbox(
            "Área",
            ["Seleccione una opción"] + list(areas.keys()),
            key="f_area"
        )

        monitor = st.selectbox(
            "Persona que monitorea",
            ["Seleccione una opción"] +
            (areas[area]["monitores"] if area != "Seleccione una opción" else []),
            key="f_monitor"
        )

    with c2:
        asesor = st.selectbox(
            "Asesor monitoreado",
            ["Seleccione una opción"] +
            (areas[area]["asesores"] if area != "Seleccione una opción" else []),
            key="f_asesor"
        )

        canal = st.selectbox(
            "Canal",
            (areas[area]["canales"] if area != "Seleccione una opción" else []),
            key="f_canal"
        )

    c3, c4 = st.columns(2)

    with c3:
        codigo = st.text_input("Código de la interacción *", key="f_codigo")

    with c4:
        fecha = st.date_input("Fecha de la interacción", date.today(), key="f_fecha")

    error_critico = st.radio(
        "¿Corresponde a un error crítico?",
        ["No", "Sí"],
        horizontal=True,
        key="f_error"
    )

    st.divider()

    # =====================================================
    # SECCIÓN 2 — CRITERIOS DE EVALUACIÓN
    # =====================================================
    st.markdown("Criterios de evaluación")

    preguntas = obtener_preguntas(area, canal) if area != "Seleccione una opción" and canal else []
    pesos = obtener_pesos(area, canal) if area != "Seleccione una opción" and canal else []

    resultados = {}
    total = 0

    if preguntas and pesos and len(preguntas) == len(pesos):

        if error_critico == "Sí":
            st.error("❌ Error crítico: el puntaje total será 0")
            for q in preguntas:
                resultados[q] = 0

        else:
            for q, p in zip(preguntas, pesos):
                key_q = f"q_{abs(hash((area, canal, q))) % 10**10}"
                resp = st.radio(
                    q,
                    ["Cumple", "No cumple"],
                    horizontal=True,
                    key=key_q
                )
                resultados[q] = p if resp == "Cumple" else 0
                total += resultados[q]

    else:
        st.info("Selecciona Área y Canal para cargar los criterios de evaluación.")

    st.divider()

    # =====================================================
    # SECCIÓN 3 — OBSERVACIONES
    # =====================================================
    st.markdown("Observaciones finales")

    o1, o2 = st.columns(2)

    with o1:
        positivos = st.text_area(
            "Aspectos Positivos *",
            height=120,
            placeholder="Ej. Buen manejo del usuario, claridad en la respuesta..."
        )

    with o2:
        mejorar = st.text_area(
            "Aspectos por Mejorar *",
            height=120,
            placeholder="Ej. Validación de identidad, control de tiempos..."
        )

    st.divider()

    # =====================================================
    # SECCIÓN 4 — RESULTADO Y GUARDADO
    # =====================================================

    st.metric("Puntaje Total", total)

    guardar = st.button("💾 Guardar Monitoreo")

    if guardar:

        if area == "Seleccione una opción" or not canal:
            st.error("⚠️ Selecciona Área y Canal.")
        elif monitor == "Seleccione una opción" or asesor == "Seleccione una opción":
            st.error("⚠️ Selecciona monitor y asesor.")
        elif not codigo.strip():
            st.error("⚠️ Código obligatorio.")
        elif not positivos.strip() or not mejorar.strip():
            st.error("⚠️ Debes diligenciar los aspectos.")
        else:
            fila = {
                "Área": area,
                "Canal": canal,
                "Monitor": monitor,
                "Asesor": asesor,
                "Código": codigo.strip(),
                "Fecha": fecha,
                "Error crítico": error_critico,
                "Total": total,
                "Aspectos positivos": positivos,
                "Aspectos por Mejorar": mejorar
            }

            for q, v in resultados.items():
                fila[q] = v

            guardar_datos_google_sheets(fila)
            st.success("✅ Monitoreo guardado correctamente")
            time.sleep(2)
    
# =====================================================================
# 📊 DASHBOARD Casa UR
# =====================================================================
elif pagina == "📊 Dashboard Casa UR":

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay datos para mostrar aún.")
        st.stop()

    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área", "Canal", "Asesor"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    df = df[df["Área"] == "Casa UR"]
    if df.empty:
        st.warning("No hay datos para Casa UR.")
        st.stop()

    meses = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
             7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}

    st.sidebar.subheader("Filtros Casa UR")
    canal_f = st.sidebar.selectbox("Canal:", ["Todos"] + areas["Casa UR"]["canales"])
    anio_f = st.sidebar.selectbox("Año:", ["Todos"] + sorted(df["Año"].dropna().unique().astype(int)))
    mes_f = st.sidebar.selectbox("Mes:", ["Todos"] + [meses[m] for m in sorted(df["Mes"].dropna().unique())])

    df_filtrado = df.copy()
    if canal_f != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Canal"] == canal_f]
    if anio_f != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Año"] == int(anio_f)]
    if mes_f != "Todos":
        mes_num = [k for k, v in meses.items() if v == mes_f][0]
        df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_num]

    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    # 🔥 ERRORES CRÍTICOS AL INICIO
    mostrar_tabla_errores_criticos(
        df_filtrado,
        titulo="Errores críticos – Casa UR"
    )

    st.subheader("📊 Dashboard Casa UR")

    total_monitoreos = len(df_filtrado)
    total_asesores = df_filtrado["Asesor"].nunique()

    promedio_monitoreos_asesor = (
    total_monitoreos / total_asesores if total_asesores > 0 else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Monitoreos Totales", total_monitoreos)

    c2.metric(
    "Promedio General (Total puntos)",
    f"{df_filtrado['Total'].mean():.2f}" if "Total" in df_filtrado.columns else "0.00"
    )

    c3.metric(
    "Errores Críticos",
    len(df_filtrado[df_filtrado["Error crítico"] == "Sí"])
    )

    c4.metric(
    "Promedio Monitoreos por Asesor",
    f"{promedio_monitoreos_asesor:.2f}"
    )

    st.subheader("📊 Distribución de Monitoreos – Casa UR")

    monit_por_asesor = df_filtrado.groupby("Asesor").size().reset_index(name="Monitoreos").sort_values("Monitoreos", ascending=False)
    fig_asesores = px.bar(monit_por_asesor, x="Asesor", y="Monitoreos", title="Cantidad de Monitoreos por Asesor", text="Monitoreos", color="Monitoreos")
    fig_asesores.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_asesores, use_container_width=True)

    monit_por_monitor = df_filtrado.groupby("Monitor").size().reset_index(name="Monitoreos realizados").sort_values("Monitoreos realizados", ascending=False)
    fig_monitor = px.bar(monit_por_monitor, x="Monitor", y="Monitoreos realizados", title="Cantidad de Monitoreos Realizados por Monitor", text="Monitoreos realizados", color="Monitoreos realizados")
    fig_monitor.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_monitor, use_container_width=True)

    st.subheader("🔥 Cumplimiento por Pregunta – Casa UR")

    for canal_actual in df_filtrado["Canal"].unique():
        st.markdown(f"### 📌 Canal: **{canal_actual}**")
        df_c = df_filtrado[df_filtrado["Canal"] == canal_actual]

        orden_formulario = obtener_preguntas("Casa UR", canal_actual)
        if not orden_formulario:
            st.info("No hay preguntas configuradas para este canal.")
            continue

        cumplimiento_canal = []
        for p in orden_formulario:
            if p not in df_c.columns:
                continue
            valores = pd.to_numeric(df_c[p], errors="coerce").fillna(0)
            pct = (valores > 0).mean() * 100
            cumplimiento_canal.append({"Pregunta": p, "Cumplimiento": pct})

        if not cumplimiento_canal:
            st.info("Aún no hay columnas de preguntas registradas para este canal.")
            continue

        df_preg_canal = pd.DataFrame(cumplimiento_canal)
        mapa_orden = {preg: idx for idx, preg in enumerate(orden_formulario)}
        df_preg_canal["orden"] = df_preg_canal["Pregunta"].map(mapa_orden)
        df_preg_canal = df_preg_canal.sort_values("orden", ascending=False)

        df_preg_canal["Pregunta_wrapped"] = df_preg_canal["Pregunta"].apply(lambda x: envolver_pregunta(x, 45))

        fig_h = px.bar(
            df_preg_canal,
            x="Cumplimiento",
            y="Pregunta_wrapped",
            orientation="h",
            color="Cumplimiento",
            color_continuous_scale="RdYlGn",
            title=f"Cumplimiento por Criterio – {canal_actual}",
            range_x=[0, 100]
        )
        fig_h.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
        fig_h = ajustar_grafico_horizontal(fig_h, df_preg_canal, "Pregunta_wrapped")
        st.plotly_chart(fig_h, use_container_width=True)

# =====================================================================
# 📈 DASHBOARD CONECTA UR
# =====================================================================
elif pagina == "📈 Dashboard Conecta UR":

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay datos para mostrar aún.")
        st.stop()

    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área", "Canal", "Asesor"])

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    df = df[df["Área"] == "Conecta UR"]
    if df.empty:
        st.warning("No hay datos para Conecta UR.")
        st.stop()

    meses = {
        1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril",
        5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto",
        9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"
    }

    # ================= FILTROS =================
    st.sidebar.subheader("Filtros Conecta UR")

    canal_f = st.sidebar.selectbox(
        "Canal:", ["Todos"] + sorted(df["Canal"].unique())
    )

    anio_f = st.sidebar.selectbox(
        "Año:", ["Todos"] + sorted(df["Año"].dropna().unique().astype(int))
    )

    mes_f = st.sidebar.selectbox(
        "Mes:", ["Todos"] + [meses[m] for m in sorted(df["Mes"].dropna().unique())]
    )

    # ================= APLICAR FILTROS =================
    df_filtrado = df.copy()

    if canal_f != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Canal"] == canal_f]

    if anio_f != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Año"] == int(anio_f)]

    if mes_f != "Todos":
        mes_num = [k for k, v in meses.items() if v == mes_f][0]
        df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_num]

    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    # 🔥 TABLA DE ERRORES CRÍTICOS (AL INICIO)
    mostrar_tabla_errores_criticos(
    df_filtrado,
    titulo="Errores críticos – Conecta UR"
)

    # ================= DASHBOARD =================
    # ================= DASHBOARD =================
    st.subheader("📈 Dashboard Conecta UR – Global")

    total_monitoreos = len(df_filtrado)
    total_asesores = df_filtrado["Asesor"].nunique()

    promedio_monitoreos_asesor = (
    total_monitoreos / total_asesores if total_asesores > 0 else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Monitoreos Totales", total_monitoreos)

    c2.metric(
    "Promedio General (Total puntos)",
    f"{df_filtrado['Total'].mean():.2f}" if "Total" in df_filtrado.columns else "0.00"
    )

    c3.metric(
    "Errores Críticos",
    len(df_filtrado[df_filtrado["Error crítico"] == "Sí"])
    )

    c4.metric(
    "Promedio Monitoreos por Asesor",
    f"{promedio_monitoreos_asesor:.2f}"
    )

    st.subheader("📊 Distribución de Monitoreos – Conecta UR")

    monit_por_asesor = df_filtrado.groupby("Asesor").size().reset_index(name="Monitoreos").sort_values("Monitoreos", ascending=False)
    fig_asesores = px.bar(monit_por_asesor, x="Asesor", y="Monitoreos", title="Cantidad de Monitoreos por Asesor", text="Monitoreos", color="Monitoreos")
    fig_asesores.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_asesores, use_container_width=True)

    monit_por_monitor = df_filtrado.groupby("Monitor").size().reset_index(name="Monitoreos realizados").sort_values("Monitoreos realizados", ascending=False)
    fig_monitor = px.bar(monit_por_monitor, x="Monitor", y="Monitoreos realizados", title="Cantidad de Monitoreos Realizados por Monitor", text="Monitoreos realizados", color="Monitoreos realizados")
    fig_monitor.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_monitor, use_container_width=True)

    st.subheader("🔥 Cumplimiento por Pregunta – Conecta UR")

    for canal_actual in df_filtrado["Canal"].unique():
        st.markdown(f"### 📌 Canal: **{canal_actual}**")
        df_c = df_filtrado[df_filtrado["Canal"] == canal_actual]

        orden_formulario = obtener_preguntas("Conecta UR", canal_actual)
        if not orden_formulario:
            st.info("No hay preguntas configuradas para este canal.")
            continue

        cumplimiento_canal = []
        for p in orden_formulario:
            if p not in df_c.columns:
                continue
            valores = pd.to_numeric(df_c[p], errors="coerce").fillna(0)
            pct = (valores > 0).mean() * 100
            cumplimiento_canal.append({"Pregunta": p, "Cumplimiento": pct})

        if not cumplimiento_canal:
            st.info("Aún no hay columnas de preguntas registradas para este canal.")
            continue

        df_preg_canal = pd.DataFrame(cumplimiento_canal)
        mapa_orden = {preg: idx for idx, preg in enumerate(orden_formulario)}
        df_preg_canal["orden"] = df_preg_canal["Pregunta"].map(mapa_orden)
        df_preg_canal = df_preg_canal.sort_values("orden", ascending=False)

        df_preg_canal["Pregunta_wrapped"] = df_preg_canal["Pregunta"].apply(lambda x: envolver_pregunta(x, 45))

        fig_h = px.bar(
            df_preg_canal,
            x="Cumplimiento",
            y="Pregunta_wrapped",
            orientation="h",
            color="Cumplimiento",
            color_continuous_scale="RdYlGn",
            title=f"Cumplimiento por Criterio – {canal_actual}",
            range_x=[0, 100]
        )
        fig_h.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
        fig_h = ajustar_grafico_horizontal(fig_h, df_preg_canal, "Pregunta_wrapped")
        st.plotly_chart(fig_h, use_container_width=True)
# ===================================================================== 
# 🎯 DASHBOARD POR ASESOR
# =====================================================================

elif pagina == "🎯 Dashboard por Asesor":

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay registros para mostrar aún.")
        st.stop()

    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área", "Asesor", "Canal"], how="any")

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    meses = {
        1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
        7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
    }

    # ===============================
    # FILTROS
    # ===============================
    st.sidebar.subheader("Filtros Asesor")

    area_f = st.sidebar.selectbox("Área:", ["Todas"] + sorted(df["Área"].unique()))
    canal_f = st.sidebar.selectbox("Canal:", ["Todos"] + sorted(df["Canal"].unique()))
    anio_f = st.sidebar.selectbox("Año:", ["Todos"] + sorted(df["Año"].dropna().unique().astype(int)))
    mes_f = st.sidebar.selectbox(
        "Mes:",
        ["Todos"] + [meses[m] for m in sorted(df["Mes"].dropna().unique())]
    )

    df_f = df.copy()

    if area_f != "Todas":
        df_f = df_f[df_f["Área"] == area_f]
    if canal_f != "Todos":
        df_f = df_f[df_f["Canal"] == canal_f]
    if anio_f != "Todos":
        df_f = df_f[df_f["Año"] == int(anio_f)]
    if mes_f != "Todos":
        mes_num = [k for k, v in meses.items() if v == mes_f][0]
        df_f = df_f[df_f["Mes"] == mes_num]

    if df_f.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    asesor_sel = st.selectbox(
        "Seleccione un asesor para analizar:",
        sorted(df_f["Asesor"].unique())
    )

    df_asesor = df_f[df_f["Asesor"] == asesor_sel]

    st.markdown(f"## 👤 Análisis del Asesor: **{asesor_sel}**")

    # ===============================
    # MÉTRICAS GENERALES
    # ===============================
    c1, c2, c3 = st.columns(3)

    c1.metric("Monitoreos realizados", len(df_asesor))

    puntaje_ponderado = calcular_ponderado_por_asesor(df_asesor)
    c2.metric("🎯 Puntaje final ponderado", f"{puntaje_ponderado:.2f}")

    c3.metric(
        "Errores Críticos",
        len(df_asesor[df_asesor["Error crítico"] == "Sí"])
    )

    st.caption(
        "📌 El puntaje final pondera **Servicio (30%)** y el promedio de los demás canales (**70%**)."
    )

    st.divider()

    # ===============================
    # ANÁLISIS POR CANAL (CLAVE)
    # ===============================
    area_asesor = df_asesor["Área"].iloc[0]

    for canal_actual in df_asesor["Canal"].unique():

        st.markdown(f"### 📌 Canal: **{canal_actual}**")

        df_canal = df_asesor[df_asesor["Canal"] == canal_actual]

        orden_formulario = obtener_preguntas(area_asesor, canal_actual)

        if not orden_formulario:
            st.info("No hay preguntas configuradas para este canal.")
            continue

        preguntas_cols = [p for p in orden_formulario if p in df_canal.columns]

        if not preguntas_cols:
            st.info("No hay respuestas registradas para este canal.")
            continue

        df_long = df_canal.melt(
            id_vars=["Área", "Asesor", "Canal", "Fecha"],
            value_vars=preguntas_cols,
            var_name="Pregunta",
            value_name="Puntaje"
        )

        df_long["Puntaje"] = pd.to_numeric(df_long["Puntaje"], errors="coerce").fillna(0)

        df_preg = (
            df_long.assign(Cumple=lambda d: d["Puntaje"] > 0)
                   .groupby("Pregunta")["Cumple"]
                   .mean()
                   .reset_index(name="Cumplimiento")
        )

        df_preg["Cumplimiento"] *= 100

        mapa_orden = {preg: idx for idx, preg in enumerate(orden_formulario)}
        df_preg["orden"] = df_preg["Pregunta"].map(mapa_orden)

        df_preg = (
            df_preg
            .dropna(subset=["orden"])
            .sort_values("orden", ascending=False)
        )

        df_preg["Pregunta_wrapped"] = df_preg["Pregunta"].apply(
            lambda x: envolver_pregunta(x, 45)
        )

        fig = px.bar(
            df_preg,
            x="Cumplimiento",
            y="Pregunta_wrapped",
            orientation="h",
            color="Cumplimiento",
            color_continuous_scale="RdYlGn",
            title=f"Cumplimiento por criterio – {canal_actual}",
            range_x=[0, 100]
        )

        fig.update_traces(
            texttemplate="%{x:.1f}%",
            textposition="outside"
        )

        fig = ajustar_grafico_horizontal(fig, df_preg, "Pregunta_wrapped")

        st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# 📥 DESCARGA DE RESULTADOS
# =====================================================================
elif pagina == "📥 Descarga de resultados":

    from io import BytesIO

    st.subheader("📥 Descarga de consolidado mensual")

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay información disponible.")
        st.stop()

    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área", "Asesor", "Fecha", "Canal", "Total"])

    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    # -------------------------------
    # FILTROS
    # -------------------------------
    c1, c2, c3 = st.columns(3)

    with c1:
        area_f = st.selectbox("Área:", sorted(df["Área"].unique()))

    with c2:
        anio_f = st.selectbox(
            "Año:", sorted(df["Año"].dropna().unique().astype(int))
        )

    with c3:
        mes_f = st.selectbox(
            "Mes:",
            [meses[m] for m in sorted(df["Mes"].dropna().unique())]
        )

    mes_num = [k for k, v in meses.items() if v == mes_f][0]

    df_f = df[
        (df["Área"] == area_f) &
        (df["Año"] == anio_f) &
        (df["Mes"] == mes_num)
    ]

    if df_f.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    # -------------------------------
    # PONDERADO FINAL POR ASESOR
    # -------------------------------
    ponderado_asesor = (
        df_f
        .groupby("Asesor")
        .apply(lambda x: calcular_ponderado_por_asesor(x))
        .reset_index(name="Promedio de Total de puntos")
    )

    # -------------------------------
    # CONSOLIDADO GENERAL
    # -------------------------------
    consolidado = (
        df_f
        .groupby("Asesor")
        .agg(
            **{
                "Cantida Monitoreos": ("Asesor", "count"),
                "Aspectos Positivos": ("Aspectos positivos", consolidar_texto),
                "Aspectos Por Mejorar": ("Aspectos por Mejorar", consolidar_texto)
            }
        )
        .reset_index()
        .rename(columns={"Asesor": "Nombre Asesor"})
    )

    consolidado = consolidado.merge(
        ponderado_asesor,
        left_on="Nombre Asesor",
        right_on="Asesor",
        how="left"
    ).drop(columns=["Asesor"])

    consolidado = consolidado[
        [
            "Nombre Asesor",
            "Cantida Monitoreos",
            "Promedio de Total de puntos",
            "Aspectos Positivos",
            "Aspectos Por Mejorar"
        ]
    ]

    st.dataframe(consolidado, use_container_width=True)

    # -------------------------------
    # DESCARGA EXCEL
    # -------------------------------
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        consolidado.to_excel(
            writer,
            index=False,
            sheet_name="Consolidado"
        )

    buffer.seek(0)

    st.download_button(
        label="📥 Descargar archivo consolidado",
        data=buffer,
        file_name=f"Resultados_{area_f}_{anio_f}_{mes_f}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# =====================================================================
# 🤖 IA – Monitoreo Automático Servicio (Gemini + Matriz Oficial)
# =====================================================================

elif pagina == "🧠 IA":

    st.markdown("## 🧠 Monitoreo Automático con IA – Servicio")

    canal = "Servicio"
    monitor = "IA"

    st.info("Canal: Servicio")
    st.info("Monitor: IA")

    area = st.selectbox("Área:", list(areas.keys()))
    asesor = st.selectbox("Asesor:", areas[area]["asesores"])

    audio_file = st.file_uploader(
        "Sube la grabación de la llamada",
        type=["mp3", "wav", "m4a"]
    )

    # ===============================
    # BOTÓN EVALUAR
    # ===============================
    if st.button("🚀 Evaluar"):

        if audio_file is None:
            st.warning("Debes subir un audio.")
            st.stop()

        # 🎙 TRANSCRIPCIÓN
        with st.spinner("🎙 Transcribiendo con Gemini..."):
            texto_llamada = transcribir_audio_gemini(audio_file)

        if not texto_llamada:
            st.stop()

        st.success("Audio transcrito correctamente")

        with st.expander("📄 Ver transcripción"):
            st.write(texto_llamada)

        texto = texto_llamada.lower()

        preguntas = obtener_preguntas(area, canal)
        pesos = obtener_pesos(area, canal)

        resultados = {}
        total = 0

        # ===============================
        # EVALUACIÓN SEGÚN MATRIZ OFICIAL
        # ===============================

        for pregunta, peso in zip(preguntas, pesos):

            puntaje = 0
            pregunta_lower = pregunta.lower()

            # 1️⃣ INMEDIATEZ
            if "atiende la interacción" in pregunta_lower:
                if "buen" in texto[:120] or "hola" in texto[:120]:
                    puntaje = peso

            # 2️⃣ SALUDO Y PROTOCOLO
            elif "saluda" in pregunta_lower:
                if ("casa ur" in texto or "conecta ur" in texto) and ("buen" in texto or "hola" in texto):
                    puntaje = peso

            # 3️⃣ SEGURIDAD
            elif "validación de identidad" in pregunta_lower:
                validaciones = 0
                if "cédula" in texto or "documento" in texto:
                    validaciones += 1
                if "fecha de nacimiento" in texto:
                    validaciones += 1
                if "correo" in texto or "teléfono" in texto:
                    validaciones += 1

                if validaciones >= 3:
                    puntaje = peso

            # 4️⃣ ESCUCHA ACTIVA
            elif "escucha activamente" in pregunta_lower:
                if "entiendo" in texto or "me confirma" in texto or "permítame validar" in texto:
                    puntaje = peso

            # 5️⃣ TIEMPOS DE ESPERA
            elif "tiempos de espera" in pregunta_lower:
                if "permítame un momento" in texto or "en línea" in texto:
                    puntaje = peso

            # 6️⃣ VALIDACIÓN DE CIERRE
            elif "valida con el usuario" in pregunta_lower:
                if "requiere algo adicional" in texto or "la información fue clara" in texto:
                    puntaje = peso

            # 7️⃣ DESPEDIDA
            elif "finaliza la atención" in pregunta_lower:
                if "gracias por comunicarse" in texto or "feliz día" in texto:
                    puntaje = peso

            resultados[pregunta] = puntaje
            total += puntaje

        # ===============================
        # GENERAR ASPECTOS
        # ===============================
        aspectos_positivos = [p for p, v in resultados.items() if v > 0]
        aspectos_mejorar = [p for p, v in resultados.items() if v == 0]

        # ===============================
        # GUARDAR SIN CREAR COLUMNAS NUEVAS
        # ===============================
        fila = {
            "Área": area,
            "Canal": canal,
            "Monitor": monitor,
            "Asesor": asesor,
            "Código": f"IA-{int(time.time())}",
            "Fecha": date.today(),
            "Error crítico": "No",
            "Total": total,
            "Aspectos positivos": "\n".join(aspectos_positivos),
            "Aspectos por Mejorar": "\n".join(aspectos_mejorar)
        }

        for pregunta, valor in resultados.items():
            fila[pregunta] = valor

        guardar_datos_google_sheets(fila)

        # ===============================
        # RESULTADO
        # ===============================
        st.success("✅ Evaluación completada correctamente")
        st.metric("🎯 Puntaje Total", total)
        st.write("### Resultado por criterio")
        st.write(resultados)
