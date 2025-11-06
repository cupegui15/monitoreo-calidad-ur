import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import base64
from io import BytesIO

st.set_page_config(page_title="Monitoreo de Calidad UR", layout="wide", page_icon="📋")

# ===============================
# FONDO Y COLORES INSTITUCIONALES
# ===============================
st.markdown("""
    <style>
        /* Colores institucionales */
        :root {
            --ur-rojo: #A80532;
            --ur-gris: #f5f5f5;
            --ur-texto: #2c2c2c;
        }

        body, .stApp {
            background-color: var(--ur-gris);
            color: var(--ur-texto);
            font-family: "Segoe UI", sans-serif;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--ur-rojo);
        }

        [data-testid="stSidebar"] * {
            color: white !important;
            font-weight: 500;
        }

        /* Botones */
        .stButton>button {
            background-color: var(--ur-rojo);
            color: white;
            font-weight: 600;
            border-radius: 8px;
            border: none;
            transition: 0.3s;
        }

        .stButton>button:hover {
            background-color: #87042A;
        }

        /* Encabezado */
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: var(--ur-rojo);
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }

        .header-title {
            font-size: 1.8rem;
            font-weight: 600;
        }

        .section-title {
            color: var(--ur-rojo);
            font-weight: 600;
            font-size: 1.4rem;
            margin-top: 1.5rem;
        }

        .stSelectbox label, .stTextInput label, .stDateInput label, .stRadio label, .stTextArea label {
            color: var(--ur-texto) !important;
            font-weight: 500;
        }

        .stMetricLabel {
            color: var(--ur-rojo) !important;
        }
    </style>
""", unsafe_allow_html=True)

# ===============================
# CARGA DE DATOS
# ===============================
@st.cache_data
def cargar_datos():
    try:
        return pd.read_csv("monitoreos.csv")
    except FileNotFoundError:
        return pd.DataFrame()

def guardar_datos(data):
    df = pd.DataFrame([data])
    try:
        df_existente = pd.read_csv("monitoreos.csv")
        df = pd.concat([df_existente, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv("monitoreos.csv", index=False)

# ===============================
# CONFIGURACIÓN
# ===============================
areas = {
    "CASA UR": {
        "canales": ["Telefónico", "Chat", "Contact Center", "Back"],
        "monitores": ["Mauricio Ramirez Cubillos", "Alejandro Parra Sánchez", "Cristian Alberto Upegui M"],
        "asesores": [
            "Adela Bogotá Cagua", "David Esteban Puerto Salgado", "Diana Marcela Sánchez Cano",
            "Diana Milena Nieto Perez", "Jenny Lorena Quintero", "Jhon Caballero", "Jose Edwin Navarro Rondon",
            "Jose Efrain Arguello", "Laura Alejandra Bernal Perez", "Leidy Johanna Alonso Rincón",
            "Leyner Anyul Silva Avila", "Martha Soraya Monsalve Fonseca", "Nancy Viviana Bulla Bustos",
            "Nelson Peña Ramírez", "Solangel Milena Rodriguez Quitian", "Leidy Sofia Ramirez Paez"
        ]
    },
    "Servicios 2030": {
        "canales": ["Linea 2030", "Chat 2030"],
        "monitores": ["Johanna Rueda Cuvajante", "Cristian Alberto Upegui M"],
        "asesores": [
            "Juan Sebastian Silva Gomez", "Jennyfer Caicedo Alfonso", "Jerly Durley Mendez Fontecha",
            "Addison Rodriguez Casallas", "Gabriel Ferney Martinez Lopez", "Juan David Gonzalez Jimenez",
            "Miguel Angel Rico Acevedo", "Juan Camilo Ortega Clavijo", "Andres Fernando Galindo Algarra",
            "Adrian Jose Sosa Gil", "Andrea Katherine Torres Junco", "Leidi Daniela Arias Rodriguez"
        ]
    }
}

preguntas = {
    "CASA UR": {
        "Telefónico": [
            ("¿Atiende la interacción oportunamente?", 9),
            ("¿Saluda y se presenta de forma amable?", 9),
            ("¿Valida identidad y personaliza?", 9),
            ("¿Escucha activamente?", 9),
            ("¿Consulta herramientas disponibles?", 9),
            ("¿Controla tiempos de espera?", 9),
            ("¿Brinda respuesta completa y coherente?", 14),
            ("¿Valida comprensión del usuario?", 8),
            ("¿Documenta correctamente la atención?", 14),
            ("¿Finaliza de forma amable?", 10)
        ],
        "Back": [
            ("¿Cumple ANS establecido?", 20),
            ("¿Analiza correctamente la solicitud?", 20),
            ("¿Gestión SAP/UXXI/Bizagi adecuada?", 20),
            ("¿Responde eficazmente según solicitud?", 20),
            ("¿Empatía al cerrar la solicitud?", 20)
        ]
    },
    "Servicios 2030": {
        "Linea 2030": [
            ("¿Atiende oportunamente?", 9),
            ("¿Saluda profesionalmente?", 9),
            ("¿Valida identidad?", 9),
            ("¿Escucha activamente?", 9),
            ("¿Consulta herramientas de soporte?", 9),
            ("¿Gestiona tiempos de espera?", 9),
            ("¿Sigue flujo definido?", 14),
            ("¿Valida comprensión del usuario?", 8),
            ("¿Documenta coherentemente?", 14),
            ("¿Finaliza cordialmente?", 10)
        ]
    }
}

# ===============================
# SIDEBAR
# ===============================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/7e/University_of_Rosario_logo.png", width=150)
pagina = st.sidebar.radio("Menú:", ["📝 Formulario de Monitoreo", "📊 Dashboard de Análisis"])

# ===============================
# ENCABEZADO CON BANNER
# ===============================
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/7e/University_of_Rosario_logo.png", width=120)
with col2:
    st.markdown('<div class="header-title">📋 Sistema de Monitoreo de Calidad - Universidad del Rosario</div>', unsafe_allow_html=True)
with col3:
    st.image("https://i.imgur.com/nHEk2V1.png", width=120)  # Lobo UR (puedes reemplazar por tu imagen local)

# ===============================
# FORMULARIO
# ===============================
if pagina == "📝 Formulario de Monitoreo":
    st.markdown('<div class="section-title">📝 Formulario de Monitoreo</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        area = st.selectbox("Área", list(areas.keys()))
    with col2:
        monitor = st.selectbox("Persona que monitorea", areas[area]["monitores"])
    with col3:
        asesor = st.selectbox("Asesor monitoreado", areas[area]["asesores"])

    codigo = st.text_input("Código de la interacción")
    fecha = st.date_input("Fecha de la interacción", date.today())
    canal = st.selectbox("Canal", areas[area]["canales"])

    error_critico = st.radio("¿Corresponde a un error crítico?", ["No", "Sí"], horizontal=True)

    if area in preguntas:
        preguntas_canal = preguntas[area].get(canal, next(iter(preguntas[area].values())))
    else:
        preguntas_canal = []

    resultados = {}
    total = 0

    if error_critico == "Sí":
        st.error("❌ Error crítico: puntaje total será 0.")
        for pregunta, _ in preguntas_canal:
            resultados[pregunta] = 0
    else:
        for pregunta, puntaje in preguntas_canal:
            cumple = st.radio(pregunta, ["Cumple", "No cumple"], horizontal=True, key=pregunta)
            resultados[pregunta] = puntaje if cumple == "Cumple" else 0
            total += resultados[pregunta]

    positivos = st.text_area("Aspectos positivos")
    mejorar = st.text_area("Aspectos por mejorar")

    st.metric("Puntaje Total", total)

    if st.button("💾 Guardar Monitoreo"):
        data = {
            "Área": area,
            "Monitor": monitor,
            "Asesor": asesor,
            "Código": codigo,
            "Fecha": fecha,
            "Canal": canal,
            "Error Crítico": error_critico,
            "Total": total,
            "Aspectos Positivos": positivos,
            "Aspectos por Mejorar": mejorar
        }
        data.update(resultados)
        guardar_datos(data)
        st.success("✅ Monitoreo guardado correctamente.")

# ===============================
# DASHBOARD
# ===============================
if pagina == "📊 Dashboard de Análisis":
    st.markdown('<div class="section-title">📊 Dashboard de Monitoreos</div>', unsafe_allow_html=True)

    df = cargar_datos()
    if df.empty:
        st.warning("⚠️ No hay registros aún.")
        st.stop()

    area_f = st.sidebar.selectbox("Filtrar por Área:", ["Todas"] + sorted(df["Área"].unique()))
    canal_f = st.sidebar.selectbox("Filtrar por Canal:", ["Todos"] + sorted(df["Canal"].unique()))

    if area_f != "Todas":
        df = df[df["Área"] == area_f]
    if canal_f != "Todos":
        df = df[df["Canal"] == canal_f]

    total_mon = len(df)
    prom_total = df["Total"].mean()
    errores = len(df[df["Error Crítico"] == "Sí"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Monitoreos Totales", total_mon)
    c2.metric("Promedio de Puntaje", round(prom_total, 2))
    c3.metric("Errores Críticos", errores)

    st.divider()

    fig1 = px.bar(df, x="Monitor", color="Monitor", title="Monitoreos por Evaluador", color_discrete_sequence=["#A80532"])
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(df, x="Asesor", color="Área", title="Monitoreos por Asesor", color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.box(df, x="Área", y="Total", color="Canal", title="Distribución de Puntajes")
    st.plotly_chart(fig3, use_container_width=True)
