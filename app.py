import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

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
# FUNCIÓN PARA GUARDAR EN GOOGLE SHEETS
# ===============================
def guardar_datos_google_sheets(data):
    """Guarda los registros directamente en Google Sheets."""
    try:
        for k, v in data.items():
            if isinstance(v, (date,)):
                data[k] = v.strftime("%Y-%m-%d")

        creds_json = st.secrets["GCP_SERVICE_ACCOUNT"]
        creds_dict = json.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(st.secrets["GOOGLE_SHEETS_ID"]).sheet1

        if not sheet.get_all_records():
            sheet.append_row(list(data.keys()))
        sheet.append_row(list(data.values()))

        st.success("✅ Monitoreo guardado correctamente en Google Sheets.")
    except Exception as e:
        st.error(f"❌ Error al guardar en Google Sheets: {e}")

# ===============================
# FUNCIÓN PARA CARGAR DESDE GOOGLE SHEETS
# ===============================
def cargar_datos_google_sheets():
    """Carga datos desde la hoja de Google Sheets."""
    try:
        creds_json = st.secrets["GCP_SERVICE_ACCOUNT"]
        creds_dict = json.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(st.secrets["GOOGLE_SHEETS_ID"]).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"⚠️ No se pudieron cargar los datos: {e}")
        return pd.DataFrame()

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

    codigo = st.text_input("Código de la interacción *")
    fecha = st.date_input("Fecha de la interacción", date.today())
    canal = st.selectbox("Canal", areas[area]["canales"])
    error_critico = st.radio("¿Corresponde a un error crítico?", ["No", "Sí"], horizontal=True)

    preguntas_canal = []
    if area == "CASA UR":
        if canal in ["Presencial", "Contact Center", "Chat"]:
            preguntas_canal = [
                ("¿Atiende la interacción en el momento que se establece contacto con el(a) usuario(a)?", 9),
                ("¿Saluda, se presenta de forma amable y cortés?", 9),
                ("¿Valida identidad garantizando confidencialidad?", 9),
                ("¿Escucha activamente?", 9),
                ("¿Consulta herramientas disponibles?", 9),
                ("¿Controla tiempos de espera informando al usuario?", 9),
                ("¿Brinda respuesta coherente y completa?", 14),
                ("¿Valida comprensión del usuario?", 8),
                ("¿Documenta correctamente la atención?", 14),
                ("¿Finaliza la atención amablemente remitiendo a encuesta?", 10)
            ]
        elif canal == "Back Office":
            preguntas_canal = [
                ("¿Cumple con el ANS establecido para el servicio?", 20),
                ("¿Analiza correctamente la solicitud?", 20),
                ("¿Gestiona adecuadamente en SAP/UXXI/Bizagi?", 20),
                ("¿Responde eficazmente según solicitud?", 20),
                ("¿Es empático al cerrar la solicitud?", 20)
            ]
    elif area == "Servicios 2030":
        if canal in ["Línea 2030", "Chat 2030"]:
            preguntas_canal = [
                ("¿Atiende la interacción de forma oportuna?", 9),
                ("¿Saluda y se presenta profesionalmente?", 9),
                ("¿Valida identidad garantizando confidencialidad?", 9),
                ("¿Escucha activamente y formula preguntas pertinentes?", 9),
                ("¿Consulta y utiliza herramientas de soporte?", 9),
                ("¿Gestiona adecuadamente los tiempos de espera?", 9),
                ("¿Sigue flujo definido para solución o escalamiento?", 14),
                ("¿Valida claridad de la información brindada?", 8),
                ("¿Documenta coherentemente?", 14),
                ("¿Finaliza amablemente y remite a encuesta?", 10)
            ]
        elif canal == "Sitio 2030":
            preguntas_canal = [
                ("¿Cumple con el ANS/SLA establecido?", 20),
                ("¿Realiza análisis completo y pertinente?", 20),
                ("¿Gestiona correctamente en SAP/UXXI/Salesforce?", 20),
                ("¿Brinda respuesta eficaz y alineada a la solicitud?", 20),
                ("¿Comunica el cierre de manera empática y profesional?", 20)
            ]

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
            fila = {"Área": area, "Monitor": monitor, "Asesor": asesor, "Código": codigo.strip(),
                    "Fecha": fecha, "Canal": canal, "Error crítico": error_critico,
                    "Total": total, "Aspectos positivos": positivos, "Aspectos por mejorar": mejorar}
            fila.update(resultados)
            guardar_datos_google_sheets(fila)

# ===============================
# DASHBOARD
# ===============================
else:
    df = cargar_datos_google_sheets()
    if df.empty:
        st.warning("📭 No hay registros para mostrar aún.")
    else:
        # 🆕 Convertir fecha y crear columnas Mes/Año
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df["Mes"] = df["Fecha"].dt.month
        df["Año"] = df["Fecha"].dt.year

        # 🆕 Diccionario de meses
        meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

        # 🆕 Filtros
        st.sidebar.subheader("Filtros")
        area_f = st.sidebar.selectbox("Área:", ["Todas"] + sorted(df["Área"].dropna().unique()))
        canal_f = st.sidebar.selectbox("Canal:", ["Todos"] + sorted(df["Canal"].dropna().unique()))
        anio_f = st.sidebar.selectbox("Año:", ["Todos"] + sorted(df["Año"].dropna().unique().astype(int).tolist(), reverse=True))
        mes_f = st.sidebar.selectbox("Mes:", ["Todos"] + [meses[m] for m in sorted(df["Mes"].dropna().unique().astype(int).tolist())])

        # 🆕 Aplicar filtros
        if area_f != "Todas":
            df = df[df["Área"] == area_f]
        if canal_f != "Todos":
            df = df[df["Canal"] == canal_f]
        if anio_f != "Todos":
            df = df[df["Año"] == int(anio_f)]
        if mes_f != "Todos":
            mes_num = [k for k, v in meses.items() if v == mes_f][0]
            df = df[df["Mes"] == mes_num]

        # ===============================
        # MÉTRICAS
        # ===============================
        c1, c2, c3 = st.columns(3)
        c1.metric("Monitoreos Totales", len(df))
        c2.metric("Promedio Puntaje", round(df["Total"].mean(), 2))
        c3.metric("Errores Críticos", len(df[df["Error crítico"] == "Sí"]))

        st.caption(f"📅 Registros del periodo: {mes_f if mes_f != 'Todos' else 'Todos los meses'} {anio_f if anio_f != 'Todos' else ''}")

        # ===============================
        # GRÁFICOS
        # ===============================
        fig1 = px.bar(df, x="Monitor", color="Área", title="Monitoreos por Monitor", text_auto=True)
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.bar(df, x="Asesor", color="Área", title="Monitoreos por Asesor", text_auto=True)
        st.plotly_chart(fig2, use_container_width=True)
