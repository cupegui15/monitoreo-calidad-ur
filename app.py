import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# --------------------------
# CONFIGURACIÓN PRINCIPAL
# --------------------------
st.set_page_config(page_title="Monitoreo de Calidad UR", layout="wide", page_icon="📋")

# --------------------------
# IMÁGENES INSTITUCIONALES
# --------------------------
URL_LOGO_UR = "https://upload.wikimedia.org/wikipedia/commons/7/7e/University_of_Rosario_logo.png"
URL_BANNER = "https://uredu-my.sharepoint.com/personal/cristian_upegui_urosario_edu_co/Documents/Imagenes/Imagen%201.jpg"
LOCAL_BANNER = "Imagen1.jpg"

def url_imagen_valida(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=3)
        return r.status_code == 200
    except:
        return False

# --------------------------
# CSS - ESTILO INSTITUCIONAL
# --------------------------
st.markdown("""
    <style>
    :root{
        --ur-rojo:#9B0029;
        --ur-rojo2:#C21833;
        --ur-gris:#f8f8f8;
        --ur-text:#222;
    }
    html, body, .stApp { background-color: var(--ur-gris) !important; color: var(--ur-text) !important; font-family: "Segoe UI", sans-serif; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: var(--ur-rojo) !important; }
    [data-testid="stSidebar"] * { color: #fff !important; font-weight:600 !important; }

    /* Inputs y radios */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input {
        background-color: #fff !important; color: var(--ur-text) !important;
    }
    div[data-baseweb="radio"] label, div[role="radiogroup"] > div, div[data-baseweb="radio"] p {
        color: var(--ur-text) !important; font-weight:600 !important;
    }

    /* Botones */
    .stButton>button { background-color: var(--ur-rojo) !important; color: white !important; border-radius:8px !important; font-weight:700 !important; }
    .stButton>button:hover { background-color:#7d0221 !important; transform:scale(1.02); }

    /* Secciones */
    .section-title { color: var(--ur-rojo); font-weight:700; font-size:1.2rem; margin-top:8px; margin-bottom:8px; }

    /* Mensaje vacío */
    .empty-msg { color: var(--ur-text); font-weight:700; text-align:center; padding:18px; }

    </style>
""", unsafe_allow_html=True)

# --------------------------
# FUNCIONES DE DATOS
# --------------------------
@st.cache_data
def cargar_datos():
    try:
        return pd.read_csv("monitoreos.csv")
    except FileNotFoundError:
        return pd.DataFrame()

def guardar_datos(data):
    df = pd.DataFrame([data])
    try:
        df_exist = pd.read_csv("monitoreos.csv")
        df = pd.concat([df_exist, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv("monitoreos.csv", index=False)

# --------------------------
# CONFIGURACIÓN DE ÁREAS Y PREGUNTAS
# --------------------------
areas = {
    "CASA UR": {
        "canales": ["Telefónico", "Chat", "Contact Center", "Back"],
        "monitores": ["Mauricio Ramirez Cubillos", "Alejandro Parra Sánchez", "Cristian Alberto Upegui M"],
        "asesores": [
            "Adela Bogotá Cagua","David Esteban Puerto Salgado","Diana Marcela Sánchez Cano",
            "Diana Milena Nieto Perez","Jenny Lorena Quintero","Jhon Caballero","Jose Edwin Navarro Rondon",
            "Jose Efrain Arguello","Laura Alejandra Bernal Perez","Leidy Johanna Alonso Rincón",
            "Leyner Anyul Silva Avila","Martha Soraya Monsalve Fonseca","Nancy Viviana Bulla Bustos",
            "Nelson Peña Ramírez","Solangel Milena Rodriguez Quitian","Leidy Sofia Ramirez Paez"
        ]
    },
    "Servicios 2030": {
        "canales": ["Línea 2030", "Chat 2030", "Sitio 2030"],
        "monitores": ["Johanna Rueda Cuvajante", "Cristian Alberto Upegui M"],
        "asesores": [
            "Juan Sebastian Silva Gomez","Jennyfer Caicedo Alfonso","Jerly Durley Mendez Fontecha",
            "Addison Rodriguez Casallas","Gabriel Ferney Martinez Lopez","Juan David Gonzalez Jimenez",
            "Miguel Angel Rico Acevedo","Juan Camilo Ortega Clavijo","Andres Fernando Galindo Algarra",
            "Adrian Jose Sosa Gil","Andrea Katherine Torres Junco","Leidi Daniela Arias Rodriguez"
        ]
    }
}

preguntas = {
    "CASA UR": {
        "Telefónico": [
            ("¿Atiende la interacción en el momento que se establece contacto con el(a) usuario(a)?", 9),
            ("¿Saluda, se presenta de una forma amable y cortés, usando el dialogo de saludo y bienvenida?", 9),
            ("¿Realiza la validación de identidad del usuario y personaliza la interacción garantizando confidencialidad?", 9),
            ("¿Escucha activamente al usuario y realiza preguntas adicionales?", 9),
            ("¿Consulta todas las herramientas disponibles?", 9),
            ("¿Controla los tiempos de espera informando al usuario?", 9),
            ("¿Brinda respuesta precisa, completa y coherente?", 14),
            ("¿Valida si la información fue clara?", 8),
            ("¿Documenta la atención correctamente?", 14),
            ("¿Finaliza la atención de forma amable y cortés?", 10)
        ],
        "Back": [
            ("¿Cumplimiento del ANS establecido para el servicio?", 20),
            ("¿Análisis correspondiente a la solicitud?", 20),
            ("¿Gestión SAP/UXXI/Bizagi adecuada?", 20),
            ("¿Respuestas eficaces según la solicitud?", 20),
            ("¿Empatía en la notificación de cierre?", 20)
        ]
    },
    "Servicios 2030": {
        "Línea 2030": [
            ("¿Atiende la interacción de forma oportuna en el momento que se establece el contacto?", 9),
            ("¿Saluda y se presenta de manera amable y profesional, estableciendo un inicio cordial de la atención?", 9),
            ("¿Realiza la validación de identidad del usuario garantizando confidencialidad y aplica protocolos de seguridad de la información?", 9),
            ("¿Escucha activamente al usuario y formula preguntas pertinentes para un diagnóstico claro y completo?", 9),
            ("¿Consulta y utiliza todas las herramientas de soporte disponibles (base de conocimiento, sistemas, documentación) para estructurar una respuesta adecuada?", 9),
            ("¿Gestiona adecuadamente los tiempos de espera, manteniendo informado al usuario y realizando acompañamiento oportuno durante la interacción?", 9),
            ("¿Sigue el flujo definido para solución o escalamiento, asegurando trazabilidad y cumplimiento de procesos internos?", 14),
            ("¿Valida con el usuario que la información brindada es clara, completa y confirma si requiere trámites o pasos adicionales?", 8),
            ("¿Documenta la atención en el sistema de tickets de manera coherente, seleccionando tipologías correctas y con redacción/ortografía adecuadas?", 14),
            ("¿Finaliza la atención de forma amable y profesional, utilizando el cierre de interacción definido y remitiendo al usuario a la encuesta de satisfacción?", 10)
        ],
        "Chat 2030": [
            ("¿Atiende la interacción de forma oportuna en el momento que se establece el contacto?", 9),
            ("¿Saluda y se presenta de manera amable y profesional, estableciendo un inicio cordial de la atención?", 9),
            ("¿Realiza la validación de identidad del usuario garantizando confidencialidad y aplica protocolos de seguridad de la información?", 9),
            ("¿Escucha activamente al usuario y formula preguntas pertinentes para un diagnóstico claro y completo?", 9),
            ("¿Consulta y utiliza todas las herramientas de soporte disponibles (base de conocimiento, sistemas, documentación) para estructurar una respuesta adecuada?", 9),
            ("¿Gestiona adecuadamente los tiempos de espera, manteniendo informado al usuario y realizando acompañamiento oportuno durante la interacción?", 9),
            ("¿Sigue el flujo definido para solución o escalamiento, asegurando trazabilidad y cumplimiento de procesos internos?", 14),
            ("¿Valida con el usuario que la información brindada es clara, completa y confirma si requiere trámites o pasos adicionales?", 8),
            ("¿Documenta la atención en el sistema de tickets de manera coherente, seleccionando tipologías correctas y con redacción/ortografía adecuadas?", 14),
            ("¿Finaliza la atención de forma amable y profesional, utilizando el cierre de interacción definido y remitiendo al usuario a la encuesta de satisfacción?", 10)
        ],
        "Sitio 2030": [
            ("¿Cumple con el ANS/SLA establecido para el servicio, iniciando la gestión dentro del tiempo definido?", 20),
            ("¿Realiza un análisis completo y pertinente de la solicitud, aplicando diagnóstico claro antes de ejecutar acciones?", 20),
            ("¿Gestiona correctamente en las herramientas institucionales (SAP / UXXI / Salesforce u otras) garantizando trazabilidad y registro adecuado?", 20),
            ("¿Brinda una respuesta eficaz y alineada a la solicitud radicada por el usuario, asegurando calidad técnica en la solución?", 20),
            ("¿Comunica el cierre de la solicitud de manera empática y profesional, validando la satisfacción del usuario?", 20)
        ]
    }
}

# --------------------------
# SIDEBAR Y MENÚ
# --------------------------
st.sidebar.image(URL_LOGO_UR, width=150)
pagina = st.sidebar.radio("Menú:", ["📝 Formulario de Monitoreo", "📊 Dashboard de Análisis"])

# --------------------------
# BANNER SUPERIOR
# --------------------------
col1, col2, col3 = st.columns([1, 6, 2])
with col1:
    st.image(URL_LOGO_UR, width=90)
with col2:
    st.markdown("<h2 style='color:#9B0029;margin-bottom:0;'>Monitoreo de Calidad - Universidad del Rosario</h2><p style='margin-top:2px;color:#444;'>Comprometidos con la excelencia en la atención al usuario</p>", unsafe_allow_html=True)
with col3:
    if url_imagen_valida(URL_BANNER):
        st.image(URL_BANNER, width=110)
    elif os.path.exists(LOCAL_BANNER):
        st.image(LOCAL_BANNER, width=110)
st.markdown("---")

# --------------------------
# FORMULARIO
# --------------------------
if pagina == "📝 Formulario de Monitoreo":
    st.markdown('<div class="section-title">🧾 Registro de Monitoreo</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        area = st.selectbox("Área", list(areas.keys()))
    with c2:
        monitor = st.selectbox("Persona que monitorea", areas[area]["monitores"])
    with c3:
        asesor = st.selectbox("Asesor monitoreado", areas[area]["asesores"])

    codigo = st.text_input("Código de la interacción")
    fecha = st.date_input("Fecha de la interacción", date.today())
    canal = st.selectbox("Canal", areas[area]["canales"])

    st.markdown("---")
    error_critico = st.radio("¿Corresponde a un error crítico?", ["No", "Sí"], horizontal=True)

    preguntas_canal = preguntas.get(area, {}).get(canal, [])
    resultados, total = {}, 0

    if error_critico == "Sí":
        st.error("❌ Error crítico marcado: puntaje total = 0")
        for q, _ in preguntas_canal:
            resultados[q] = 0
        total = 0
    else:
        for idx, (q, p) in enumerate(preguntas_canal):
            respuesta = st.radio(q, ["Cumple", "No cumple"], horizontal=True, key=f"{idx}-{q}")
            resultados[q] = p if respuesta == "Cumple" else 0
            total += resultados[q]

    positivos = st.text_area("Aspectos Positivos")
    mejorar = st.text_area("Aspectos por Mejorar")
    st.metric("Puntaje Total", total)

    if st.button("💾 Guardar Monitoreo"):
        fila = {
            "Área": area, "Monitor": monitor, "Asesor": asesor,
            "Código": codigo, "Fecha": fecha, "Canal": canal,
            "Error crítico": error_critico, "Total": total,
            "Aspectos positivos": positivos, "Aspectos por mejorar": mejorar
        }
        fila.update(resultados)
        guardar_datos(fila)
        st.success("✅ Monitoreo guardado correctamente.")

# --------------------------
# DASHBOARD
# --------------------------
else:
    st.markdown('<div class="section-title">📈 Dashboard de Análisis</div>', unsafe_allow_html=True)
    df = cargar_datos()
    if df.empty:
        st.markdown('<div class="empty-msg">📭 No hay registros aún</div>', unsafe_allow_html=True)
    else:
        area_f = st.sidebar.selectbox("Área:", ["Todas"] + sorted(df["Área"].unique()))
        canal_f = st.sidebar.selectbox("Canal:", ["Todos"] + sorted(df["Canal"].unique()))
        asesor_f = st.sidebar.selectbox("Asesor:", ["Todos"] + sorted(df["Asesor"].unique()))

        if area_f != "Todas": df = df[df["Área"] == area_f]
        if canal_f != "Todos": df = df[df["Canal"] == canal_f]
        if asesor_f != "Todos": df = df[df["Asesor"] == asesor_f]

        c1, c2, c3 = st.columns(3)
        c1.metric("Monitoreos Totales", len(df))
        c2.metric("Promedio Puntaje", round(df["Total"].mean(), 2))
        c3.metric("Errores Críticos", len(df[df["Error crítico"] == "Sí"]))

        st.divider()
        fig1 = px.bar(df, x="Monitor", color="Monitor", title="Monitoreos por Monitor")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.bar(df, x="Asesor", color="Área", title="Monitoreos por Asesor")
        fig2.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.box(df, x="Área", y="Total", color="Canal", title="Distribución de Puntajes por Área y Canal")
        st.plotly_chart(fig3, use_container_width=True)
