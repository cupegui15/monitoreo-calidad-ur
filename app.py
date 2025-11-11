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
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] option,
[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #000 !important;
    background-color: #fff !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] span {
    color: #000 !important;
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
# FUNCIONES GOOGLE SHEETS
# ===============================
def guardar_datos_google_sheets(data):
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

def cargar_datos_google_sheets():
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
# FORMULARIO DE MONITOREO
# ===============================
if pagina == "📝 Formulario de Monitoreo":
    from datetime import date
    st.markdown('<div class="section-title">🧾 Registro de Monitoreo</div>', unsafe_allow_html=True)

    if "form_reset" not in st.session_state:
        st.session_state.form_reset = False

    if st.session_state.form_reset:
        st.session_state.clear()
        st.session_state.form_reset = False
        st.info("🧹 Formulario reiniciado correctamente.")

    c1, c2, c3 = st.columns(3)
    with c1:
        area = st.selectbox("Área", ["Seleccione una opción"] + list(areas.keys()))
    with c2:
        monitor = st.selectbox("Persona que monitorea", ["Seleccione una opción"] + (areas[area]["monitores"] if area != "Seleccione una opción" else []))
    with c3:
        asesor = st.selectbox("Asesor monitoreado", ["Seleccione una opción"] + (areas[area]["asesores"] if area != "Seleccione una opción" else []))

    codigo = st.text_input("Código de la interacción *")
    fecha = st.date_input("Fecha de la interacción", date.today())
    canal = st.selectbox("Canal", (areas[area]["canales"] if area != "Seleccione una opción" else ["Seleccione un área primero"]))
    error_critico = st.radio("¿Corresponde a un error crítico?", ["No", "Sí"], horizontal=True)

    # Preguntas dinámicas
    preguntas_canal = []
    if area == "CASA UR":
        if canal in ["Presencial", "Contact Center", "Chat"]:
            preguntas_canal = [
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
            ]
        elif canal == "Back Office":
            preguntas_canal = [
                ("¿Cumple con el ANS establecido para el servicio?", 20),
                ("¿Analiza correctamente la solicitud?", 20),
                ("¿Gestiona adecuadamente en SAP/UXXI/Bizagi?", 20),
                ("¿Respuestas eficaz de acuerdo a la solicitud radicada por el usuario?", 20),
                ("¿Es empático al cerrar la solicitud?", 20)
            ]
    elif area == "Servicios 2030":
        if canal in ["Línea 2030", "Chat 2030"]:
            preguntas_canal = [
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
            ]
        elif canal == "Sitio 2030":
            preguntas_canal = [
                ("¿Cumple con el ANS/SLA establecido?", 20),
                ("¿Realiza un análisis completo y pertinente de la solicitud, aplicando diagnóstico claro antes de ejecutar acciones?", 20),
                ("¿Gestiona correctamente en las herramientas institucionales (SAP / UXXI / Salesforce u otras) garantizando trazabilidad y registro adecuado?", 20),
                ("¿Brinda una respuesta eficaz y alineada a la solicitud radicada por el usuario, asegurando calidad técnica en la solución?", 20),
                ("¿Comunica el cierre de la solicitud de manera empática y profesional, validando la satisfacción del usuario?", 20)
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

    positivos = st.text_area("Aspectos Positivos *")
    mejorar = st.text_area("Aspectos por Mejorar *")
    st.metric("Puntaje Total", total)

    if st.button("💾 Guardar Monitoreo"):
        if area == "Seleccione una opción" or monitor == "Seleccione una opción" or asesor == "Seleccione una opción":
            st.error("⚠️ Debes seleccionar Área, Persona que monitorea y Asesor monitoreado.")
        elif not codigo.strip():
            st.error("⚠️ Debes ingresar el código de la interacción antes de guardar.")
        elif not positivos.strip() or not mejorar.strip():
            st.error("⚠️ Los campos de aspectos positivos y por mejorar son obligatorios.")
        else:
            fila = {
                "Área": area, "Monitor": monitor, "Asesor": asesor, "Código": codigo.strip(),
                "Fecha": fecha, "Canal": canal, "Error crítico": error_critico,
                "Total": total, "Aspectos positivos": positivos, "Aspectos por mejorar": mejorar
            }
            fila.update(resultados)
            guardar_datos_google_sheets(fila)
            st.session_state.form_reset = True
            st.rerun()

# ===============================
# DASHBOARD
# ===============================
else:
    df = cargar_datos_google_sheets()
    if df.empty:
        st.warning("📭 No hay registros para mostrar aún.")
    else:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df["Mes"] = df["Fecha"].dt.month
        df["Año"] = df["Fecha"].dt.year
        df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)

        meses = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
                 7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}

        st.sidebar.subheader("Filtros")
        area_f = st.sidebar.selectbox("Área:", ["Todas"] + sorted(df["Área"].dropna().unique()))
        canal_f = st.sidebar.selectbox("Canal:", ["Todos"] + sorted(df["Canal"].dropna().unique()))
        anio_f = st.sidebar.selectbox("Año:", ["Todos"] + sorted(df["Año"].dropna().unique().astype(int).tolist(), reverse=True))
        mes_f = st.sidebar.selectbox("Mes:", ["Todos"] + [meses[m] for m in sorted(df["Mes"].dropna().unique().astype(int).tolist())])

        if area_f != "Todas":
            df = df[df["Área"] == area_f]
        if canal_f != "Todos":
            df = df[df["Canal"] == canal_f]
        if anio_f != "Todos":
            df = df[df["Año"] == int(anio_f)]
        if mes_f != "Todos":
            mes_num = [k for k, v in meses.items() if v == mes_f][0]
            df = df[df["Mes"] == mes_num]

        st.caption(f"📅 Registros del periodo: {mes_f if mes_f!='Todos' else 'Todos los meses'} {anio_f if anio_f!='Todos' else ''}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Monitoreos Totales", len(df))
        c2.metric("Promedio Puntaje", round(df["Total"].mean(), 2) if not df.empty else 0)
        c3.metric("Errores Críticos", len(df[df["Error crítico"] == "Sí"]))

        st.divider()
        st.subheader("📊 Análisis General")

        col1, col2 = st.columns(2)
        with col1:
            df_monitor = df.groupby(["Monitor", "Área"]).size().reset_index(name="Total Monitoreos")
            fig1 = px.bar(df_monitor, x="Monitor", y="Total Monitoreos",
                          color="Área", text="Total Monitoreos",
                          title="Monitoreos por Monitor",
                          color_discrete_sequence=["#9B0029", "#004E98"])
            fig1.update_traces(textposition="outside")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            df_asesor = df.groupby(["Asesor", "Área"]).size().reset_index(name="Total Monitoreos")
            fig2 = px.bar(df_asesor, x="Asesor", y="Total Monitoreos",
                          color="Área", text="Total Monitoreos",
                          title="Monitoreos por Asesor",
                          color_discrete_sequence=["#9B0029", "#004E98"])
            fig2.update_traces(textposition="outside")
            st.plotly_chart(fig2, use_container_width=True)

        # ===============================
        # ✅ Cumplimiento por Pregunta (Canalizado)
        # ===============================
        st.divider()
        st.subheader("✅ Cumplimiento por Pregunta")

        # Reutilizamos las preguntas del formulario
        preguntas_por_canal = {
            "CASA UR": {
                "Presencial": preguntas_canal,
                "Contact Center": preguntas_canal,
                "Chat": preguntas_canal,
                "Back Office": [
                    ("¿Cumple con el ANS establecido para el servicio?", 20),
                    ("¿Analiza correctamente la solicitud?", 20),
                    ("¿Gestiona adecuadamente en SAP/UXXI/Bizagi?", 20),
                    ("¿Respuestas eficaz de acuerdo a la solicitud radicada por el usuario?", 20),
                    ("¿Es empático al cerrar la solicitud?", 20)
                ]
            },
            "Servicios 2030": {
                "Línea 2030": preguntas_canal,
                "Chat 2030": preguntas_canal,
                "Sitio 2030": [
                    ("¿Cumple con el ANS/SLA establecido?", 20),
                    ("¿Realiza un análisis completo y pertinente de la solicitud, aplicando diagnóstico claro antes de ejecutar acciones?", 20),
                    ("¿Gestiona correctamente en las herramientas institucionales (SAP / UXXI / Salesforce u otras) garantizando trazabilidad y registro adecuado?", 20),
                    ("¿Brinda una respuesta eficaz y alineada a la solicitud radicada por el usuario, asegurando calidad técnica en la solución?", 20),
                    ("¿Comunica el cierre de la solicitud de manera empática y profesional, validando la satisfacción del usuario?", 20)
                ]
            }
        }

        for area, canales in preguntas_por_canal.items():
            for canal, preguntas in canales.items():
                df_canal = df[(df["Área"] == area) & (df["Canal"] == canal)]
                if df_canal.empty:
                    continue

                st.markdown(f"## 🧩 {area} — {canal}")
                st.caption(f"Total de monitoreos: {len(df_canal)}")

                for i, (pregunta, _) in enumerate(preguntas):
                    if pregunta not in df_canal.columns:
                        continue

                    st.markdown(f"### {pregunta}")

                    df_canal["Cumple_tmp"] = df_canal[pregunta].apply(lambda x: 1 if pd.to_numeric(x, errors="coerce") > 0 else 0)
                    resumen = (df_canal.groupby("Asesor")["Cumple_tmp"]
                                .agg(["sum", "count"])
                                .reset_index()
                                .rename(columns={"sum": "Cumple", "count": "Total"}))
                    resumen["% Cumplimiento"] = (resumen["Cumple"] / resumen["Total"]) * 100
                    resumen["% Cumplimiento"] = resumen["% Cumplimiento"].fillna(0).round(2)

                    no_cumplen = resumen[resumen["% Cumplimiento"] < 100]
                    cumplen_todos = no_cumplen.empty

                    colA, colB = st.columns(2)
                    with colA:
                        st.markdown("🟢 **Asesores que Cumplen 100%**")
                        top = resumen[resumen["% Cumplimiento"] == 100]
                        if not top.empty:
                            fig_top = px.bar(top, x="Asesor", y="% Cumplimiento", text="% Cumplimiento",
                                             color="% Cumplimiento", color_continuous_scale="greens", range_y=[0, 100])
                            fig_top.update_traces(texttemplate="%{text}%", textposition="outside")
                            fig_top.update_layout(margin=dict(t=20, b=30, l=40, r=40), showlegend=False, height=400)
                            st.plotly_chart(fig_top, use_container_width=True)
                        else:
                            st.info("Ningún asesor cumple al 100% esta pregunta.")

                    with colB:
                        if not cumplen_todos:
                            st.markdown("🔴 **Asesores con Menor Cumplimiento**")
                            fig_low = px.bar(no_cumplen, x="Asesor", y="% Cumplimiento", text="% Cumplimiento",
                                             color="% Cumplimiento", color_continuous_scale="reds", range_y=[0, 100])
                            fig_low.update_traces(texttemplate="%{text}%", textposition="outside")
                            fig_low.update_layout(margin=dict(t=20, b=30, l=40, r=40), showlegend=False, height=400)
                            st.plotly_chart(fig_low, use_container_width=True)
                        else:
                            st.success("✅ Todos los asesores cumplen esta pregunta.")
                st.divider()
