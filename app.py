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
# FUNCIONES GOOGLE SHEETS
# ===============================
def guardar_datos_google_sheets(data):
    try:
        # Convertir fechas a texto antes de enviar
        for k, v in data.items():
            if isinstance(v, (date,)):
                data[k] = v.strftime("%Y-%m-%d")

        creds_json = st.secrets["GCP_SERVICE_ACCOUNT"]
        creds_dict = json.loads(creds_json)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(st.secrets["GOOGLE_SHEETS_ID"]).sheet1

        # Si la hoja está vacía, escribir encabezados primero
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
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
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

    # PREGUNTAS SEGÚN ÁREA Y CANAL
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
                "Error crítico": error_critico,
                "Total": total,
                "Aspectos positivos": positivos,
                "Aspectos por mejorar": mejorar
            }
            fila.update(resultados)
            guardar_datos_google_sheets(fila)

# ===============================
# DASHBOARD CON ANÁLISIS POR PREGUNTA (OPTIMIZADO VISUALMENTE)
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

        meses = {
            1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
            7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
        }

        # === FILTROS ===
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

        # === MÉTRICAS ===
        c1, c2, c3 = st.columns(3)
        c1.metric("Monitoreos Totales", len(df))
        c2.metric("Promedio Puntaje", round(df["Total"].mean(), 2) if not df.empty else 0)
        c3.metric("Errores Críticos", len(df[df["Error crítico"] == "Sí"]))

        st.divider()
        st.subheader("📊 Análisis General")

        # === GRAFICOS PRINCIPALES ===
        col1, col2 = st.columns(2)
        with col1:
            df_monitor = df.groupby(["Monitor", "Área"]).size().reset_index(name="Total Monitoreos")
            fig1 = px.bar(df_monitor, x="Monitor", y="Total Monitoreos", color="Área" if df_monitor["Área"].nunique() > 1 else None,
                          text="Total Monitoreos", title="Monitoreos por Monitor", color_discrete_sequence=["#9B0029", "#004E98", "#0077B6"])
            fig1.update_traces(textposition="outside")
            fig1.update_yaxes(dtick=1, title_text="Cantidad de Monitoreos")
            fig1.update_layout(showlegend=True, margin=dict(t=40,b=40,l=40,r=40))
            st.plotly_chart(fig1, use_container_width=True, key="grafico_monitor")

        with col2:
            df_asesor = df.groupby(["Asesor", "Área"]).size().reset_index(name="Total Monitoreos")
            fig2 = px.bar(df_asesor, x="Asesor", y="Total Monitoreos", color="Área" if df_asesor["Área"].nunique() > 1 else None,
                          text="Total Monitoreos", title="Monitoreos por Asesor", color_discrete_sequence=["#9B0029", "#004E98", "#0077B6"])
            fig2.update_traces(textposition="outside")
            fig2.update_yaxes(dtick=1, title_text="Cantidad de Monitoreos")
            fig2.update_layout(showlegend=True, margin=dict(t=40,b=40,l=40,r=40))
            st.plotly_chart(fig2, use_container_width=True, key="grafico_asesor")

                st.divider()
        st.subheader("✅ Cumplimiento por Pregunta")

        preguntas_cols = [c for c in df.columns if "¿" in c or "?" in c]
        if preguntas_cols:
            for i, pregunta in enumerate(preguntas_cols):
                st.markdown(f"### {pregunta}")

                # Determinar el puntaje máximo posible de esa pregunta
                # (buscando entre CASA UR y 2030)
                max_puntaje = 20
                for bloque in ["CASA UR", "Servicios 2030"]:
                    for canal_data in areas[bloque]["canales"]:
                        for q, p in [
                            (preg, pts)
                            for canal in areas[bloque]["canales"]
                            for preg, pts in []
                        ]:
                            if pregunta.strip() == q.strip():
                                max_puntaje = p

                # Crear columna binaria de cumplimiento
                df["Cumple_tmp"] = df[pregunta].apply(lambda x: 1 if pd.to_numeric(x, errors="coerce") > 0 else 0)

                # Calcular % de cumplimiento por asesor
                resumen = (
                    df.groupby("Asesor")["Cumple_tmp"]
                    .agg(["sum", "count"])
                    .reset_index()
                    .rename(columns={"sum": "Cumple", "count": "Total"})
                )
                resumen["% Cumplimiento"] = (resumen["Cumple"] / resumen["Total"]) * 100
                resumen["% Cumplimiento"] = resumen["% Cumplimiento"].fillna(0).round(2)

                mejores = resumen.sort_values("% Cumplimiento", ascending=False).head(5)
                peores = resumen.sort_values("% Cumplimiento", ascending=True).head(5)

                colA, colB = st.columns(2)
                with colA:
                    st.markdown("🟢 **Top 5 Asesores con Mayor Cumplimiento**")
                    if not mejores.empty:
                        fig_top = px.bar(
                            mejores,
                            x="Asesor",
                            y="% Cumplimiento",
                            text="% Cumplimiento",
                            color="% Cumplimiento",
                            color_continuous_scale="greens",
                            range_y=[0, 100]
                        )
                        fig_top.update_traces(
                            texttemplate="%{text}%", 
                            textposition="outside",
                            hovertemplate="Asesor: %{x}<br>% Cumplimiento: %{y:.1f}%"
                        )
                        fig_top.update_yaxes(dtick=10, title_text="% de Cumplimiento")
                        fig_top.update_layout(
                            margin=dict(t=20, b=30, l=40, r=40),
                            showlegend=False,
                            height=400
                        )
                        st.plotly_chart(fig_top, use_container_width=True, key=f"grafico_mejor_{i}")
                    else:
                        st.info("No hay datos suficientes.")

                with colB:
                    st.markdown("🔴 **Top 5 Asesores con Menor Cumplimiento**")
                    if not peores.empty:
                        fig_low = px.bar(
                            peores,
                            x="Asesor",
                            y="% Cumplimiento",
                            text="% Cumplimiento",
                            color="% Cumplimiento",
                            color_continuous_scale="reds",
                            range_y=[0, 100]
                        )
                        fig_low.update_traces(
                            texttemplate="%{text}%", 
                            textposition="outside",
                            hovertemplate="Asesor: %{x}<br>% Cumplimiento: %{y:.1f}%"
                        )
                        fig_low.update_yaxes(dtick=10, title_text="% de Cumplimiento")
                        fig_low.update_layout(
                            margin=dict(t=20, b=30, l=40, r=40),
                            showlegend=False,
                            height=400
                        )
                        st.plotly_chart(fig_low, use_container_width=True, key=f"grafico_peor_{i}")
                    else:
                        st.info("No hay datos suficientes.")

                st.divider()
        else:
            st.info("⚠️ No se encontraron preguntas registradas aún en los monitoreos.")
