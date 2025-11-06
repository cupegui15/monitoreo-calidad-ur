import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

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

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--rojo-ur) !important;
}
[data-testid="stSidebar"] * {
    color: #fff !important;
    font-weight: 600 !important;
}

/* Banner */
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

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input {
    background-color: #fff !important;
    color: var(--texto) !important;
}

/* Radios */
div[data-baseweb="radio"] label, div[role="radiogroup"] > div {
    color: var(--texto) !important;
    font-weight: 600 !important;
}

/* Botones */
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

/* Secciones */
.section-title {
    color: var(--rojo-ur);
    font-weight: 700;
    font-size: 1.2rem;
    margin-top: 1rem;
    margin-bottom: 0.6rem;
}

/* Mensaje vacío */
.empty-msg {
    color: var(--texto);
    font-weight: 700;
    text-align: center;
    padding: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# FUNCIONES DE DATOS
# ===============================
@st.cache_data
def guardar_datos(data):
    """Guarda los datos solo en CSV (sin Excel para evitar error openpyxl)."""
    df = pd.DataFrame([data])
    try:
        df_exist = pd.read_csv("monitoreos.csv", dtype=str)
        df_exist["Total"] = pd.to_numeric(df_exist["Total"], errors="coerce").fillna(0)
        df = pd.concat([df_exist, df], ignore_index=True)
    except FileNotFoundError:
        pass

    df.to_csv("monitoreos.csv", index=False)

# ===============================
# ÁREAS Y PREGUNTAS
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
            ("¿Saluda, se presenta de una forma amable y cortés, usando el dialogo de saludo y bienvenida?", 9),
            ("¿Realiza la validación de identidad del usuario y personaliza la interacción garantizando confidencialidad?", 9),
            ("¿Escucha activamente al usuario y realiza preguntas adicionales demostrando atención?", 9),
            ("¿Consulta todas las herramientas disponibles para estructurar la respuesta?", 9),
            ("¿Controla los tiempos de espera informando y acompañando al usuario?", 9),
            ("¿Brinda respuesta precisa, completa y coherente, de acuerdo a lo solicitado?", 14),
            ("¿Valida con el usuario si la información fue clara o si requiere algo más?", 8),
            ("¿Documenta la atención coherentemente seleccionando tipologías correctas y con buena redacción?", 14),
            ("¿Finaliza la atención amablemente remitiendo al usuario a la encuesta?", 10)
        ],
        "Contact Center": [
            ("¿Atiende la interacción en el momento que se establece contacto con el(a) usuario(a)?", 9),
            ("¿Saluda, se presenta de una forma amable y cortés, usando el dialogo de saludo y bienvenida?", 9),
            ("¿Realiza la validación de identidad del usuario y personaliza la interacción de forma adecuada garantizando la confidencialidad de la información?", 9),
            ("¿Escucha activamente al usuario y  realiza preguntas adicionales demostrando atención y concentración?", 9),
            ("¿Consulta todas las herramientas disponibles para estructurar la posible respuesta que se le brindará al usuario?", 9),
            ("¿Controla los tiempos de espera informando al usuario y realizando acompañamiento cada 2 minutos?", 9),
            ("¿Brinda respuesta de forma precisa, completa y coherente, de acuerdo a la solicitado por el usuario?", 14),
            ("¿Valida con el usuario si la información fue clara, completa o si requiere algún trámite adicional?", 8),
            ("¿Documenta la atención de forma coherente según lo solicitado e informado al cliente; seleccionando las tipologías adecuadas y manejando correcta redacción y ortografía?", 14),
            ("¿Finaliza la atención de forma amable, cortés utilizando el dialogo de cierre y despedida remitiendo al usuario a responder la encuesta de percepción?", 10)
        ],
        "Chat": [
            ("¿Atiende la interacción en el momento que se establece contacto con el(a) usuario(a)?", 9),
            ("¿Saluda, se presenta de una forma amable y cortés, usando el dialogo de saludo y bienvenida?", 9),
            ("¿Realiza la validación de identidad del usuario y personaliza la interacción de forma adecuada garantizando la confidencialidad de la información?", 9),
            ("¿Escucha activamente al usuario y  realiza preguntas adicionales demostrando atención y concentración?", 9),
            ("¿Consulta todas las herramientas disponibles para estructurar la posible respuesta que se le brindará al usuario?", 9),
            ("¿Controla los tiempos de espera informando al usuario y realizando acompañamiento cada 2 minutos?", 9),
            ("¿Brinda respuesta de forma precisa, completa y coherente, de acuerdo a la solicitado por el usuario?", 14),
            ("¿Valida con el usuario si la información fue clara, completa o si requiere algún trámite adicional?", 8),
            ("¿Documenta la atención de forma coherente según lo solicitado e informado al cliente; seleccionando las tipologías adecuadas y manejando correcta redacción y ortografía?", 14),
            ("¿Finaliza la atención de forma amable, cortés utilizando el dialogo de cierre y despedida remitiendo al usuario a responder la encuesta de percepción?", 10)
        ],
        "Back Office": [
            ("¿Cumplimiento del ANS establecido para el servicio?", 20),
            ("¿Análisis correspondiente a la solicitud?", 20),
            ("¿Gestión SAP/UXXI/Bizagi adecuada?", 20),
            ("¿Respuestas eficaz de acuerdo a la solicitud radicada por el usuario?", 20),
            ("¿Es empático en la notificación de cierre de la solicitud?", 20)
        ]
    },
    "Servicios 2030": {
        "Línea 2030": [
            ("¿Atiende la interacción de forma oportuna?", 9),
            ("¿Saluda y se presenta profesionalmente?", 9),
            ("¿Valida identidad con confidencialidad?", 9),
            ("¿Escucha activamente y pregunta adecuadamente?", 9),
            ("¿Usa herramientas de soporte?", 9),
            ("¿Gestiona tiempos de espera correctamente?", 9),
            ("¿Sigue flujo de solución/escalamiento?", 14),
            ("¿Valida comprensión de la información?", 8),
            ("¿Documenta atención con redacción adecuada?", 14),
            ("¿Finaliza de forma amable y profesional?", 10)
        ],
        "Chat 2030": [
            ("¿Atiende la interacción de forma oportuna?", 9),
            ("¿Saluda y se presenta profesionalmente?", 9),
            ("¿Valida identidad con confidencialidad?", 9),
            ("¿Escucha activamente y pregunta adecuadamente?", 9),
            ("¿Usa herramientas de soporte?", 9),
            ("¿Gestiona tiempos de espera correctamente?", 9),
            ("¿Sigue flujo de solución/escalamiento?", 14),
            ("¿Valida comprensión de la información?", 8),
            ("¿Documenta atención con redacción adecuada?", 14),
            ("¿Finaliza de forma amable y profesional?", 10)
        ],
        "Sitio 2030": [
            ("¿Cumple con ANS/SLA definido?", 20),
            ("¿Realiza análisis completo antes de ejecutar acciones?", 20),
            ("¿Gestiona correctamente en SAP/UXXI/Salesforce?", 20),
            ("¿Brinda respuesta eficaz y alineada?", 20),
            ("¿Comunica cierre de manera empática y profesional?", 20)
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
    <div style="display:flex;align-items:center;gap:1rem;">
        <div>
            <h2>Monitoreo de Calidad - Universidad del Rosario</h2>
            <p>Comprometidos con la excelencia en la atención al usuario</p>
        </div>
    </div>
    <div>
        <img src="{URL_BANNER_IMG}" width="130" style="border-radius:6px;">
    </div>
</div>
""", unsafe_allow_html=True)

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
        st.error("❌ Error crítico: el puntaje total será 0.")
        for q, _ in preguntas_canal:
            resultados[q] = 0
        total = 0
    else:
        for idx, (q, p) in enumerate(preguntas_canal):
            resp = st.radio(q, ["Cumple", "No cumple"], horizontal=True, key=f"{idx}-{q}")
            resultados[q] = p if resp == "Cumple" else 0
            total += resultados[q]

    positivos = st.text_area("Aspectos Positivos")
    mejorar = st.text_area("Aspectos por Mejorar")
    st.metric("Puntaje Total", total)

    if st.button("💾 Guardar Monitoreo"):
        fila = {
            "Área": area, "Monitor": monitor, "Asesor": asesor, "Código": codigo,
            "Fecha": fecha, "Canal": canal, "Error crítico": error_critico,
            "Total": total, "Aspectos positivos": positivos, "Aspectos por mejorar": mejorar
        }
        fila.update(resultados)
        guardar_datos(fila)
        st.success("✅ Monitoreo guardado correctamente y almacenado en CSV y Excel.")

# ===============================
# DASHBOARD
# ===============================
else:
    st.markdown('<div class="section-title">📈 Dashboard de Análisis</div>', unsafe_allow_html=True)
    df = cargar_datos()
    if df.empty:
        st.markdown('<div class="empty-msg">📭 No hay registros aún</div>', unsafe_allow_html=True)
    else:
        area_f = st.sidebar.selectbox("Área:", ["Todas"] + sorted(df["Área"].unique()))
        canal_f = st.sidebar.selectbox("Canal:", ["Todos"] + sorted(df["Canal"].unique()))
        asesor_f = st.sidebar.selectbox("Asesor:", ["Todos"] + sorted(df["Asesor"].unique()))

        if area_f != "Todas":
            df = df[df["Área"] == area_f]
        if canal_f != "Todos":
            df = df[df["Canal"] == canal_f]
        if asesor_f != "Todos":
            df = df[df["Asesor"] == asesor_f]

        if df.empty:
            st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
        else:
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
