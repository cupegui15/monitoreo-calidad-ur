import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# ===============================
# ⚙️ CONFIGURACIÓN INICIAL
# ===============================
st.set_page_config(page_title="Monitoreo de Calidad UR", layout="wide", page_icon="📋")

# ===============================
# 🎨 ESTILO UNIVERSIDAD DEL ROSARIO
# ===============================
st.markdown("""
    <style>
        html, body, .stApp {
            background-color: #f8f8f8 !important;
            color: #2b2b2b !important;
            font-family: 'Segoe UI', sans-serif !important;
        }

        /* ===== SIDEBAR ===== */
        [data-testid="stSidebar"] {
            background-color: #9B0029 !important;
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
            font-weight: 500 !important;
        }

        /* ===== ENCABEZADO ===== */
        .banner {
            background: linear-gradient(90deg, #9B0029 0%, #C21833 100%);
            border-radius: 12px;
            padding: 1.2rem 2rem;
            color: white !important;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .banner h1 {
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0;
        }
        .banner p {
            font-size: 1rem;
            opacity: 0.9;
            margin: 0;
        }

        /* ===== FORMULARIOS ===== */
        label, .stRadio > label, .stTextInput > label, .stDateInput > label {
            color: #2b2b2b !important;
            font-weight: 600 !important;
        }

        /* ===== INPUTS ===== */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, 
        .stDateInput input {
            background-color: #fff !important;
            color: #2b2b2b !important;
            border: 1px solid #ccc !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
        }

        /* ===== RADIO ===== */
        div[data-baseweb="radio"] label {
            color: #2b2b2b !important;
            font-weight: 600 !important;
        }
        div[role="radiogroup"] > div {
            color: #2b2b2b !important;
            font-weight: 600 !important;
        }

        /* ===== BOTONES ===== */
        .stButton>button {
            background-color: #9B0029 !important;
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: 0.2s;
        }
        .stButton>button:hover {
            background-color: #7d0221 !important;
            transform: scale(1.03);
        }

        /* ===== MÉTRICAS ===== */
        .stMetricLabel {
            color: #9B0029 !important;
            font-weight: 700 !important;
        }

        /* ===== TEXTO VACÍO ===== */
        .empty-msg {
            color: #2b2b2b !important;
            font-size: 1.2rem;
            font-weight: 600;
            text-align: center;
            padding: 2rem;
        }

        /* ===== SECCIONES ===== */
        .section-title {
            color: #9B0029;
            font-size: 1.4rem;
            font-weight: 700;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# ===============================
# 📦 FUNCIONES DE DATOS
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
# ⚙️ CONFIGURACIÓN DE ÁREAS Y PREGUNTAS
# ===============================
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
        "canales": ["Linea 2030", "Chat 2030"],
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
        ]
    }
}

# ===============================
# 🧭 SIDEBAR
# ===============================
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQY0ZMIXOVuzLond_jNv713shc6TmUWej0JDQ&s", width=150)
pagina = st.sidebar.radio("Menú:", ["📝 Formulario de Monitoreo", "📊 Dashboard de Análisis"])

# ===============================
# 🏛️ ENCABEZADO
# ===============================
st.markdown(f"""
<div class="banner">
    <div>
        <h1>Monitoreo de Calidad - Universidad del Rosario</h1>
        <p>Comprometidos con la excelencia en la atención al usuario</p>
    </div>
    <img src="https://uredu-my.sharepoint.com/personal/cristian_upegui_urosario_edu_co/Documents/Imagenes/Imagen%201.jpg" width="140">
</div>
""", unsafe_allow_html=True)

# ===============================
# 📝 FORMULARIO
# ===============================
if pagina == "📝 Formulario de Monitoreo":
    st.markdown('<div class="section-title">🧾 Registro de Monitoreo</div>', unsafe_allow_html=True)

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

    preguntas_canal = preguntas.get(area, {}).get(canal, [])

    resultados, total = {}, 0

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
            "Área": area, "Monitor": monitor, "Asesor": asesor,
            "Código": codigo, "Fecha": fecha, "Canal": canal,
            "Error Crítico": error_critico, "Total": total,
            "Aspectos Positivos": positivos, "Aspectos por Mejorar": mejorar
        }
        data.update(resultados)
        guardar_datos(data)
        st.success("✅ Monitoreo guardado correctamente.")

# ===============================
# 📊 DASHBOARD DE ANÁLISIS
# ===============================
elif pagina == "📊 Dashboard de Análisis":
    st.markdown('<div class="section-title">📈 Dashboard de Análisis</div>', unsafe_allow_html=True)
    df = cargar_datos()

    if df.empty:
        st.markdown('<div class="empty-msg">📭 No hay registros aún</div>', unsafe_allow_html=True)
    else:
        fig = px.bar(df, x="Área", y="Total", color="Monitor", title="Promedio de Puntajes por Área")
        st.plotly_chart(fig, use_container_width=True)
