import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# ===============================
# CONFIGURACIÓN PRINCIPAL
# ===============================
st.set_page_config(page_title="Monitoreo de Calidad UR", layout="wide", page_icon="📋")

# ===============================
# RUTA DEL ARCHIVO DE DATOS
# ===============================
DATA_FILE = "monitoreos.csv"

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
.banner h2 { margin: 0; font-size: 1.6rem; font-weight: 700; }
.banner p { margin: 0; font-size: 0.9rem; }
.section-title {
    color: var(--rojo-ur);
    font-weight: 700;
    font-size: 1.2rem;
    margin-top: 1rem;
    margin-bottom: 0.6rem;
}
.empty-msg {
    color: var(--texto);
    font-weight: 700;
    text-align: center;
    padding: 1.2rem;
}
.stButton>button {
    background-color: var(--rojo-ur) !important;
    color: white !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
}
.stButton>button:hover {
    background-color: #7d0221 !important;
    transform: scale(1.03);
}
</style>
""", unsafe_allow_html=True)

# ===============================
# FUNCIONES DE DATOS
# ===============================
def cargar_datos():
    """Carga los datos del CSV si existe."""
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame()

def guardar_datos(data):
    """Guarda los registros en monitoreos.csv."""
    df = pd.DataFrame([data])
    if os.path.exists(DATA_FILE):
        df_existente = pd.read_csv(DATA_FILE)
        df = pd.concat([df_existente, df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False, encoding='utf-8')
    st.success("✅ Monitoreo guardado correctamente y almacenado en monitoreos.csv")

# ===============================
# CONFIGURACIÓN DE ÁREAS Y PREGUNTAS
# ===============================
areas = {
    "CASA UR": {
        "canales": ["Presencial", "Contact Center", "Chat", "Back Office"],
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
        "Presencial": [
            ("¿Atiende la interacción en el momento que se establece contacto con el(a) usuario(a)?", 9),
            ("¿Saluda, se presenta de una forma amable y cortés?", 9),
            ("¿Realiza la validación de identidad del usuario garantizando confidencialidad?", 9),
            ("¿Escucha activamente y realiza preguntas adicionales demostrando atención?", 9),
            ("¿Consulta herramientas disponibles para estructurar la respuesta?", 9),
            ("¿Controla los tiempos de espera informando y acompañando al usuario?", 9),
            ("¿Brinda respuesta precisa y coherente?", 14),
            ("¿Valida con el usuario si la información fue clara o requiere algo más?", 8),
            ("¿Documenta la atención correctamente con redacción adecuada?", 14),
            ("¿Finaliza la atención amablemente remitiendo al usuario a la encuesta?", 10)
        ],
        "Contact Center": [
            ("¿Atiende la interacción oportunamente?", 9),
            ("¿Saluda y se presenta de forma amable y profesional?", 9),
            ("¿Valida identidad garantizando confidencialidad?", 9),
            ("¿Escucha activamente al usuario?", 9),
            ("¿Consulta herramientas para estructurar respuesta adecuada?", 9),
            ("¿Controla tiempos de espera e informa al usuario?", 9),
            ("¿Brinda respuesta coherente y completa?", 14),
            ("¿Valida comprensión del usuario?", 8),
            ("¿Documenta la atención correctamente?", 14),
            ("¿Finaliza de manera amable y profesional?", 10)
        ],
        "Chat": [
            ("¿Atiende la interacción oportunamente?", 9),
            ("¿Saluda cordialmente?", 9),
            ("¿Valida identidad y personaliza la atención?", 9),
            ("¿Responde adecuadamente demostrando comprensión?", 9),
            ("¿Utiliza herramientas para resolver adecuadamente?", 9),
            ("¿Gestiona tiempos de espera e informa avances?", 9),
            ("¿Brinda respuesta precisa y coherente?", 14),
            ("¿Valida comprensión del usuario?", 8),
            ("¿Documenta correctamente la interacción?", 14),
            ("¿Finaliza con cierre amable y remite a encuesta?", 10)
        ],
        "Back Office": [
            ("¿Cumple con el ANS establecido para el servicio?", 20),
            ("¿Analiza correctamente la solicitud?", 20),
            ("¿Gestiona adecuadamente en SAP/UXXI/Bizagi?", 20),
            ("¿Responde eficazmente según solicitud?", 20),
            ("¿Es empático al cerrar la solicitud?", 20)
        ]
    },
    "Servicios 2030": {
        "Línea 2030": [
            ("¿Atiende la interacción de forma oportuna?", 9),
            ("¿Saluda y se presenta profesionalmente?", 9),
            ("¿Valida identidad garantizando confidencialidad?", 9),
            ("¿Escucha activamente y formula preguntas pertinentes?", 9),
            ("¿Consulta y utiliza herramientas de soporte?", 9),
            ("¿Gestiona adecuadamente los tiempos de espera?", 9),
            ("¿Sigue flujo definido para solución o escalamiento?", 14),
            ("¿Valida que la información brindada es clara y completa?", 8),
            ("¿Documenta coherentemente?", 14),
            ("¿Finaliza amablemente y remite a encuesta?", 10)
        ],
        "Chat 2030": [
            ("¿Atiende la interacción de forma oportuna?", 9),
            ("¿Saluda y se presenta profesionalmente?", 9),
            ("¿Valida identidad garantizando confidencialidad?", 9),
            ("¿Escucha activamente y formula preguntas pertinentes?", 9),
            ("¿Consulta y utiliza herramientas de soporte?", 9),
            ("¿Gestiona adecuadamente los tiempos de espera?", 9),
            ("¿Sigue flujo definido para solución o escalamiento?", 14),
            ("¿Valida que la información brindada es clara y completa?", 8),
            ("¿Documenta coherentemente?", 14),
            ("¿Finaliza amablemente y remite a encuesta?", 10)
        ],
        "Sitio 2030": [
            ("¿Cumple con el ANS/SLA establecido?", 20),
            ("¿Realiza análisis completo y pertinente?", 20),
            ("¿Gestiona correctamente en SAP/UXXI/Salesforce?", 20),
            ("¿Brinda respuesta eficaz y alineada a la solicitud?", 20),
            ("¿Comunica el cierre de manera empática y profesional?", 20)
        ]
    }
}

# ===============================
# SIDEBAR Y BANNER
# ===============================
st.sidebar.image(URL_LOGO_UR, width=150)
pagina = st.sidebar.radio("Menú:", ["📝 Formulario de Monitoreo", "📊 Dashboard de Análisis"])

st.markdown(f"""
<div class="banner">
    <div><h2>Monitoreo de Calidad - Universidad del Rosario</h2>
    <p>Comprometidos con la excelencia en la atención al usuario</p></div>
    <div><img src="{URL_BANNER_IMG}" width="130" style="border-radius:6px;"></div>
</div>
""", unsafe_allow_html=True)

# ===============================
# FORMULARIO
# ===============================
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
    error_critico = st.radio("¿Corresponde a un error crítico?", ["No", "Sí"], horizontal=True)

    preguntas_canal = preguntas.get(area, {}).get(canal, [])
    resultados, total = {}, 0

    if error_critico == "Sí":
        st.error("❌ Error crítico: el puntaje total será 0.")
        for q, _ in preguntas_canal:
            resultados[q] = 0
    else:
        for idx, (q, p) in enumerate(preguntas_canal):
            resp = st.radio(q, ["Cumple", "No cumple"], horizontal=True, key=f"{idx}-{q}")
            resultados[q] = p if resp == "Cumple" else 0
            total += resultados[q]

    positivos = st.text_area("Aspectos Positivos")
    mejorar = st.text_area("Aspectos por Mejorar")
    st.metric("Puntaje Total", total)

    if st.button("💾 Guardar Monitoreo"):
    if not codigo.strip():
        st.error("⚠️ Debes ingresar el código de la interacción antes de guardar.")
    else:
        fila = {
            "Área": area,
            "Monitor": monitor,
            "Asesor": asesor,
            "Código": codigo.strip(),
            "Fecha": fecha,
            "Canal": canal,
            "Error crítico": error,
            "Total": total,
            "Aspectos positivos": positivos,
            "Aspectos por mejorar": mejorar
        }
        fila.update(resultados)
        guardar_datos(fila)
# ===============================
# DASHBOARD
# ===============================
else:
    df = cargar_datos()

    if df.empty:
        st.warning("📭 No hay registros para mostrar aún.")
    else:
        st.sidebar.subheader("Filtros")
        area_f = st.sidebar.selectbox("Área:", ["Todas"] + sorted(df["Área"].unique()))
        canal_f = st.sidebar.selectbox("Canal:", ["Todos"] + sorted(df["Canal"].unique()))
        asesor_f = st.sidebar.selectbox("Asesor:", ["Todos"] + sorted(df["Asesor"].unique()))
        monitor_f = st.sidebar.selectbox("Monitor:", ["Todos"] + sorted(df["Monitor"].unique()))

        # FILTROS
        if area_f != "Todas":
            df = df[df["Área"] == area_f]
        if canal_f != "Todos":
            df = df[df["Canal"] == canal_f]
        if asesor_f != "Todos":
            df = df[df["Asesor"] == asesor_f]
        if monitor_f != "Todos":
            df = df[df["Monitor"] == monitor_f]

        # ===============================
        # MÉTRICAS
        # ===============================
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Monitoreos Totales", len(df))
        c2.metric("Promedio Puntaje", round(df["Total"].mean(), 2))
        c3.metric("Errores Críticos", len(df[df["Error crítico"] == "Sí"]))
        c4.metric("Última Fecha", df["Fecha"].max())

        st.divider()

        # ===============================
        # GRÁFICOS GENERALES
        # ===============================
        st.subheader("📊 Análisis General")

        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(df, x="Monitor", color="Área", title="Monitoreos por Monitor", text_auto=True)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.bar(df, x="Asesor", color="Área", title="Monitoreos por Asesor", text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # ===============================
        # PROMEDIO POR CANAL / ÁREA
        # ===============================
# ===============================
# ANÁLISIS DE CUMPLIMIENTO POR PREGUNTA
# ===============================
st.subheader("✅ Cumplimiento por Pregunta")

preguntas_cols = [c for c in df.columns if "¿" in c or "?" in c]

if preguntas_cols:
    for i, pregunta in enumerate(preguntas_cols):
        resumen = df[pregunta].value_counts().reset_index()
        resumen.columns = ["Estado", "Cantidad"]

        colA, colB = st.columns([2, 1])
        with colA:
            figQ = px.bar(
                resumen,
                x="Estado",
                y="Cantidad",
                color="Estado",
                title=pregunta,
                text_auto=True,
                color_discrete_map={"1": "#007700", "0": "#cc0000"},
            )
            st.plotly_chart(figQ, use_container_width=True, key=f"bar_{i}")

        with colB:
            figPie = px.pie(
                resumen,
                names="Estado",
                values="Cantidad",
                color="Estado",
                color_discrete_map={"1": "#007700", "0": "#cc0000"},
            )
            st.plotly_chart(figPie, use_container_width=True, key=f"pie_{i}")
else:
    st.info("⚠️ No se han registrado preguntas aún en los monitoreos.")

# ===============================
# DESCARGA DE DATOS
# ===============================
st.divider()

st.download_button(
    label="⬇️ Descargar base consolidada (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="monitoreos_consolidado.csv",
    mime="text/csv"
)
