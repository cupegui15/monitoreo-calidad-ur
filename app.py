import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Monitoreo de Calidad UR", layout="wide", page_icon="📋")

# ===============================
# UTILIDADES
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
# PÁGINAS
# ===============================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/7e/University_of_Rosario_logo.png", width=150)
pagina = st.sidebar.radio("Menú:", ["📝 Formulario de Monitoreo", "📊 Dashboard de Análisis"])

# ===============================
# FORMULARIO
# ===============================
if pagina == "📝 Formulario de Monitoreo":
    st.header("📝 Formulario de Monitoreo de Calidad")

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

    st.markdown("---")

    error_critico = st.radio("¿Corresponde a un error crítico?", ["No", "Sí"], horizontal=True)

    # 🔒 Manejo seguro de preguntas por canal
    if area in preguntas:
        if canal in preguntas[area]:
            preguntas_canal = preguntas[area][canal]
        else:
            preguntas_canal = next(iter(preguntas[area].values()))
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
# DASHBOARD DE ANÁLISIS
# ===============================
if pagina == "📊 Dashboard de Análisis":
    st.header("📊 Dashboard de Monitoreos")

    df = cargar_datos()
    if df.empty:
        st.warning("⚠️ No hay registros de monitoreos aún.")
        st.stop()

    # Filtros
    area_f = st.sidebar.selectbox("Filtrar por Área:", ["Todas"] + sorted(df["Área"].unique()))
    canal_f = st.sidebar.selectbox("Filtrar por Canal:", ["Todos"] + sorted(df["Canal"].unique()))
    asesor_f = st.sidebar.selectbox("Filtrar por Asesor:", ["Todos"] + sorted(df["Asesor"].unique()))

    if area_f != "Todas":
        df = df[df["Área"] == area_f]
    if canal_f != "Todos":
        df = df[df["Canal"] == canal_f]
    if asesor_f != "Todos":
        df = df[df["Asesor"] == asesor_f]

    # KPIs
    total_mon = len(df)
    prom_total = df["Total"].mean()
    errores = len(df[df["Error Crítico"] == "Sí"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Monitoreos Totales", total_mon)
    c2.metric("Promedio de Puntaje", round(prom_total, 2))
    c3.metric("Errores Críticos", errores)

    st.divider()

    # Gráficos
    fig1 = px.bar(df, x="Monitor", color="Monitor", title="Monitoreos por Evaluador")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(df, x="Asesor", color="Área", title="Monitoreos por Asesor")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.box(df, x="Área", y="Total", color="Canal", title="Distribución de Puntajes")
    st.plotly_chart(fig3, use_container_width=True)
