import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# ===============================
# CONFIGURACIÓN INICIAL
# ===============================
st.set_page_config(page_title="Monitoreo de Calidad UR", layout="wide", page_icon="📋")

# ===============================
# VALIDACIÓN DE IMAGENES
# ===============================
def url_imagen_valida(url, timeout=3):
    try:
        r = requests.head(url, allow_redirects=True, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False

# URLs de imágenes
URL_LOGO_UR = "https://upload.wikimedia.org/wikipedia/commons/7/7e/University_of_Rosario_logo.png"
URL_BANNER_IMG = "https://uredu-my.sharepoint.com/personal/cristian_upegui_urosario_edu_co/Documents/Imagenes/Imagen%201.jpg"
LOCAL_BANNER = "Imagen1.jpg"  # si subes el archivo local

# ===============================
# ESTILOS INSTITUCIONALES
# ===============================
st.markdown("""
    <style>
        html, body, .stApp {
            background-color: #f8f8f8 !important;
            color: #2b2b2b !important;
            font-family: 'Segoe UI', sans-serif !important;
        }

        [data-testid="stSidebar"] {
            background-color: #9B0029 !important;
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
            font-weight: 500 !important;
        }

        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input {
            background-color: #fff !important;
            color: #2b2b2b !important;
            border: 1px solid #ccc !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
        }

        div[data-baseweb="radio"] label, div[role="radiogroup"] > div {
            color: #2b2b2b !important;
            font-weight: 600 !important;
        }

        .stButton>button {
            background-color: #9B0029 !important;
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 0.6rem 1rem !important;
            font-weight: 600 !important;
            transition: 0.2s;
        }
        .stButton>button:hover {
            background-color: #7d0221 !important;
            transform: scale(1.02);
        }

        .empty-msg {
            color: #2b2b2b !important;
            font-size: 1.1rem;
            font-weight: 600;
            text-align:center;
            padding:1.2rem;
        }

        .section-title {
            color: #9B0029;
            font-weight:700;
            font-size:1.2rem;
            margin-top:1rem;
            margin-bottom:0.6rem;
        }
    </style>
""", unsafe_allow_html=True)

# ===============================
# FUNCIONES DE DATOS
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
# CONFIGURACIÓN DE ÁREAS Y PREGUNTAS
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
        "canales": ["Linea 2030", "Chat 2030", "Sitio 2030"],
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
        ],
        "Chat": [
            ("¿Atiende el chat oportunamente?", 9),
            ("¿Usa lenguaje cordial y empático?", 9),
            ("¿Valida la identidad del usuario?", 9),
            ("¿Lee activamente la solicitud?", 9),
            ("¿Usa correctamente las herramientas?", 9),
            ("¿Gestiona tiempos de espera?", 9),
            ("¿Brinda respuesta completa y clara?", 14),
            ("¿Verifica comprensión del usuario?", 8),
            ("¿Documenta correctamente la atención?", 14),
            ("¿Cierra el chat de manera adecuada?", 10)
        ],
        "Contact Center": [
            ("¿Atiende la llamada oportunamente?", 9),
            ("¿Saluda y se presenta de forma amable?", 9),
            ("¿Valida identidad correctamente?", 9),
            ("¿Escucha activamente?", 9),
            ("¿Consulta herramientas disponibles?", 9),
            ("¿Controla tiempos de espera?", 9),
            ("¿Brinda respuesta completa y coherente?", 14),
            ("¿Valida comprensión del usuario?", 8),
            ("¿Documenta correctamente la atención?", 14),
            ("¿Finaliza de forma amable y profesional?", 10)
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
            ("¿Atiende la interacción de forma oportuna?", 9),
            ("¿Saluda profesionalmente?", 9),
            ("¿Valida la identidad y garantiza confidencialidad?", 9),
            ("¿Escucha activamente?", 9),
            ("¿Consulta herramientas de soporte?", 9),
            ("¿Gestiona tiempos de espera?", 9),
            ("¿Sigue flujo definido?", 14),
            ("¿Valida comprensión del usuario?", 8),
            ("¿Documenta coherentemente?", 14),
            ("¿Finaliza cordialmente?", 10)
        ],
        "Chat 2030": [
            ("¿Atiende el chat oportunamente?", 9),
            ("¿Saluda con lenguaje cordial y profesional?", 9),
            ("¿Valida identidad del usuario?", 9),
            ("¿Lee activamente la solicitud y responde con precisión?", 9),
            ("¿Utiliza herramientas correctamente?", 9),
            ("¿Informa tiempos de espera o pausas?", 9),
            ("¿Sigue el flujo correcto de atención?", 14),
            ("¿Verifica comprensión del usuario?", 8),
            ("¿Documenta correctamente la atención?", 14),
            ("¿Finaliza el chat de forma profesional?", 10)
        ],
        "Sitio 2030": [
            ("¿Cumple protocolo de atención presencial?", 20),
            ("¿Realiza diagnóstico oportuno?", 20),
            ("¿Soluciona o gestiona correctamente la solicitud?", 20),
            ("¿Registra adecuadamente en el sistema?", 20),
            ("¿Cumple normas de presentación y cortesía?", 20)
        ]
    }
}

# ===============================
# SIDEBAR
# ===============================
st.sidebar.image(URL_LOGO_UR, width=150)
pagina = st.sidebar.radio("Menú:", ["📝 Formulario de Monitoreo", "📊 Dashboard de Análisis"])

# ===============================
# BANNER INSTITUCIONAL
# ===============================
col1, col2, col3 = st.columns([1, 6, 2])
with col1:
    st.image(URL_LOGO_UR, width=90)
with col2:
    st.markdown("<h2 style='margin-bottom:0;color:#9B0029;'>Monitoreo de Calidad - Universidad del Rosario</h2><p style='margin-top:2px;'>Comprometidos con la excelencia en la atención al usuario</p>", unsafe_allow_html=True)
with col3:
    if url_imagen_valida(URL_BANNER_IMG):
        st.image(URL_BANNER_IMG, width=110)
    elif os.path.exists(LOCAL_BANNER):
        st.image(LOCAL_BANNER, width=110)
st.markdown("---")

# ===============================
# FORMULARIO
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
        for p, _ in preguntas_canal:
            resultados[p] = 0
    else:
        for idx, (p, puntaje) in enumerate(preguntas_canal):
            key = f"{area}_{canal}_{idx}"
            cumple = st.radio(p, ["Cumple", "No cumple"], horizontal=True, key=key)
            resultados[p] = puntaje if cumple == "Cumple" else 0
            total += resultados[p]

    positivos = st.text_area("Aspectos positivos")
    mejorar = st.text_area("Aspectos por mejorar")

    st.metric("Puntaje Total", total)

    if st.button("💾 Guardar Monitoreo"):
        data = {
            "Área": area,
            "Persona que monitorea": monitor,
            "Asesor": asesor,
            "Código": codigo,
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Canal": canal,
            "Error crítico": error_critico,
            "Total": total,
            "Aspectos positivos": positivos,
            "Aspectos por mejorar": mejorar
        }
        data.update(resultados)
        guardar_datos(data)
        st.success("✅ Monitoreo guardado correctamente.")

# ===============================
# DASHBOARD
# ===============================
else:
    st.markdown('<div class="section-title">📈 Dashboard de Análisis</div>', unsafe_allow_html=True)
    df = cargar_datos()

    if df.empty:
        st.markdown('<div class="empty-msg">📭 No hay registros aún</div>', unsafe_allow_html=True)
    else:
        area_f = st.sidebar.selectbox("Filtrar por Área:", ["Todas"] + sorted(df["Área"].unique()))
        canal_f = st.sidebar.selectbox("Filtrar por Canal:", ["Todos"] + sorted(df["Canal"].unique()))

        if area_f != "Todas":
            df = df[df["Área"] == area_f]
        if canal_f != "Todos":
            df = df[df["Canal"] == canal_f]

        c1, c2, c3 = st.columns(3)
        c1.metric("Monitoreos Totales", len(df))
        c2.metric("Promedio Puntaje", round(df["Total"].mean(), 2))
        c3.metric("Errores Críticos", len(df[df["Error crítico"] == "Sí"]))

        st.divider()
        st.plotly_chart(px.bar(df, x="Persona que monitorea", color="Área", title="Monitoreos por Evaluador"), use_container_width=True)
        st.plotly_chart(px.box(df, x="Área", y="Total", color="Canal", title="Distribución de Puntajes"), use_container_width=True)
