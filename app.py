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
.section-title {
    color: var(--rojo-ur);
    font-weight: 700;
    font-size: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

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
    "Conecta UR": {
        "canales": ["Línea Conecta UR", "Chat Conecta UR", "Sitio Conecta UR"],
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
# FUNCIONES AUXILIARES DE PREGUNTAS
# ===============================
def obtener_preguntas(area, canal):
    """
    Devuelve la lista de textos de preguntas correspondientes a un área y canal.
    Deben coincidir EXACTO con las usadas en el formulario.
    """
    preguntas = []

    if area == "CASA UR":
        if canal in ["Presencial", "Contact Center", "Chat"]:
            preguntas = [
                "¿Atiende la interacción en el momento que se establece contacto con el(a) usuario(a)?",
                "¿Saluda, se presenta de una forma amable y cortés, usando el dialogo de saludo y bienvenida?",
                "¿Realiza la validación de identidad del usuario y personaliza la interacción de forma adecuada garantizando la confidencialidad de la información?",
                "¿Escucha activamente al usuario y  realiza preguntas adicionales demostrando atención y concentración?",
                "¿Consulta todas las herramientas disponibles para estructurar la posible respuesta que se le brindará al usuario?",
                "¿Controla los tiempos de espera informando al usuario y realizando acompañamiento cada 2 minutos?",
                "¿Brinda respuesta de forma precisa, completa y coherente, de acuerdo a la solicitado por el usuario?",
                "¿Valida con el usuario si la información fue clara, completa o si requiere algún trámite adicional?",
                "¿Documenta la atención de forma coherente según lo solicitado e informado al cliente; seleccionando las tipologías adecuadas y manejando correcta redacción y ortografía?",
                "¿Finaliza la atención de forma amable, cortés utilizando el dialogo de cierre y despedida remitiendo al usuario a responder la encuesta de percepción?"
            ]
        elif canal == "Back Office":
            preguntas = [
                "¿Cumple con el ANS establecido para el servicio?",
                "¿Analiza correctamente la solicitud?",
                "¿Gestiona adecuadamente en SAP/UXXI/Bizagi?",
                "¿Respuestas eficaz de acuerdo a la solicitud radicada por el usuario?",
                "¿Es empático al cerrar la solicitud?"
            ]

    elif area == "Conecta UR":
        if canal in ["Línea Conecta UR", "Chat Conecta UR"]:
            preguntas = [
                "¿Atiende la interacción de forma oportuna en el momento que se establece el contacto?",
                "¿Saluda y se presenta de manera amable y profesional, estableciendo un inicio cordial de la atención?",
                "¿Realiza la validación de identidad del usuario garantizando confidencialidad y aplica protocolos de seguridad de la información?",
                "¿Escucha activamente al usuario y formula preguntas pertinentes para un diagnóstico claro y completo?",
                "¿Consulta y utiliza todas las herramientas de soporte disponibles (base de conocimiento, sistemas, documentación) para estructurar una respuesta adecuada?",
                "¿Gestiona adecuadamente los tiempos de espera, manteniendo informado al usuario y realizando acompañamiento oportuno durante la interacción?",
                "¿Sigue el flujo definido para solución o escalamiento, asegurando trazabilidad y cumplimiento de procesos internos?",
                "¿Valida con el usuario que la información brindada es clara, completa y confirma si requiere trámites o pasos adicionales?",
                "¿Documenta la atención en el sistema de tickets de manera coherente, seleccionando tipologías correctas y con redacción/ortografía adecuadas?",
                "¿Finaliza la atención de forma amable y profesional, utilizando el cierre de interacción definido y remitiendo al usuario a la encuesta de satisfacción?"
            ]
        elif canal == "Sitio Conecta UR":
            preguntas = [
                "¿Cumple con el ANS/SLA establecido?",
                "¿Realiza un análisis completo y pertinente de la solicitud, aplicando diagnóstico claro antes de ejecutar acciones?",
                "¿Gestiona correctamente en las herramientas institucionales (SAP / UXXI / Salesforce u otras) garantizando trazabilidad y registro adecuado?",
                "¿Brinda una respuesta eficaz y alineada a la solicitud radicada por el usuario, asegurando calidad técnica en la solución?",
                "¿Comunica el cierre de la solicitud de manera empática y profesional, validando la satisfacción del usuario?"
            ]

    return preguntas

# ===============================
# GOOGLE SHEETS – GUARDAR
# ===============================
def guardar_datos_google_sheets(data):
    try:
        # Convertir fechas
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

        sh = client.open_by_key(st.secrets["GOOGLE_SHEETS_ID"])

        # IMPORTANTE: en-dash "–"
        nombre_hoja = f"{data['Área']} – {data['Canal']}"

        # Buscar o crear la hoja
        try:
            hoja = sh.worksheet(nombre_hoja)
        except:
            hoja = sh.add_worksheet(title=nombre_hoja, rows=5000, cols=200)
            hoja.append_row(list(data.keys()))

        # Verificar encabezados existentes
        encabezados = hoja.row_values(1)

        nuevos = False
        for col in data.keys():
            if col not in encabezados:
                encabezados.append(col)
                nuevos = True

        if nuevos:
            hoja.resize(cols=len(encabezados))
            hoja.update("1:1", [encabezados])

        fila = [data.get(col, "") for col in encabezados]
        hoja.append_row(fila)

        st.success(f"✅ Registro guardado correctamente en '{nombre_hoja}'.")

    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")

# ===============================
# GOOGLE SHEETS – CARGAR TODAS LAS HOJAS
# ===============================
def cargar_todas_las_hojas_google_sheets():
    try:
        creds_json = st.secrets["GCP_SERVICE_ACCOUNT"]
        creds_dict = json.loads(creds_json)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sh = client.open_by_key(st.secrets["GOOGLE_SHEETS_ID"])

        dfs = []

        for ws in sh.worksheets():
            title = ws.title

            # Solo hojas con formato "Área – Canal"
            if " – " not in title:
                continue

            area_name, canal_name = [x.strip() for x in title.split(" – ", 1)]

            if area_name not in areas:
                continue
            if canal_name not in areas[area_name]["canales"]:
                continue

            records = ws.get_all_records()
            if not records:
                continue

            df_temp = pd.DataFrame(records)
            df_temp["Área"] = area_name
            df_temp["Canal"] = canal_name

            dfs.append(df_temp)

        if not dfs:
            return pd.DataFrame()

        return pd.concat(dfs, ignore_index=True)

    except Exception as e:
        st.error(f"⚠️ Error cargando datos: {e}")
        return pd.DataFrame()

# ===============================
# SIDEBAR Y MENÚ
# ===============================
st.sidebar.image(URL_LOGO_UR, width=150)
pagina = st.sidebar.radio(
    "Menú:",
    [
        "📝 Formulario de Monitoreo",
        "📊 Dashboard CASA UR",
        "📈 Dashboard Conecta UR",
        "🎯 Dashboard por Asesor"
    ]
)

# ===============================
# BANNER
# ===============================
st.markdown(f"""
<div class="banner">
    <div><h2>Monitoreo de Calidad - Universidad del Rosario</h2>
    <p>Comprometidos con la excelencia en la atención al usuario</p></div>
    <div><img src="{URL_BANNER_IMG}" width="130" style="border-radius:6px;"></div>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# 📝 FORMULARIO DE MONITOREO
# =====================================================================
if pagina == "📝 Formulario de Monitoreo":

    st.markdown('<div class="section-title">🧾 Registro de Monitoreo</div>', unsafe_allow_html=True)

    if "form_reset" not in st.session_state:
        st.session_state.form_reset = False

    if st.session_state.form_reset:
        st.session_state.clear()
        st.session_state.form_reset = False

    c1, c2, c3 = st.columns(3)

    with c1:
        area = st.selectbox("Área", ["Seleccione una opción"] + list(areas.keys()))

    with c2:
        monitor = st.selectbox(
            "Persona que monitorea",
            ["Seleccione una opción"] + (areas[area]["monitores"] if area != "Seleccione una opción" else []),
        )

    with c3:
        asesor = st.selectbox(
            "Asesor monitoreado",
            ["Seleccione una opción"] + (areas[area]["asesores"] if area != "Seleccione una opción" else []),
        )

    codigo = st.text_input("Código de la interacción *")
    fecha = st.date_input("Fecha de la interacción", date.today())
    canal = st.selectbox("Canal", (areas[area]["canales"] if area != "Seleccione una opción" else []))
    error_critico = st.radio("¿Corresponde a un error crítico?", ["No", "Sí"], horizontal=True)

    # ===============================
    # PREGUNTAS DINÁMICAS
    # ===============================
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

    elif area == "Conecta UR":

        if canal in ["Línea Conecta UR", "Chat Conecta UR"]:
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
        elif canal == "Sitio Conecta UR":
            preguntas_canal = [
                ("¿Cumple con el ANS/SLA establecido?", 20),
                ("¿Realiza un análisis completo y pertinente de la solicitud, aplicando diagnóstico claro antes de ejecutar acciones?", 20),
                ("¿Gestiona correctamente en las herramientas institucionales (SAP / UXXI / Salesforce u otras) garantizando trazabilidad y registro adecuado?", 20),
                ("¿Brinda una respuesta eficaz y alineada a la solicitud radicada por el usuario, asegurando calidad técnica en la solución?", 20),
                ("¿Comunica el cierre de la solicitud de manera empática y profesional, validando la satisfacción del usuario?", 20)
            ]

    resultados = {}
    total = 0

    if error_critico == "Sí":
        st.error("❌ Error crítico: puntaje total = 0")
        for q, _ in preguntas_canal:
            resultados[q] = 0
    else:
        for idx, (q, p) in enumerate(preguntas_canal):
            resp = st.radio(q, ["Cumple", "No cumple"], horizontal=True)
            resultados[q] = p if resp == "Cumple" else 0
            total += resultados[q]

    positivos = st.text_area("Aspectos Positivos *")
    mejorar = st.text_area("Aspectos por Mejorar *")

    st.metric("Puntaje Total", total)

    # ==========================================
    #  BOTÓN GUARDAR SOLO EN EL FORMULARIO
    # ==========================================
    if st.button("💾 Guardar Monitoreo"):
        if area == "Seleccione una opción" or monitor == "Seleccione una opción" or asesor == "Seleccione una opción":
            st.error("⚠️ Debes completar todos los campos.")
        elif not codigo.strip():
            st.error("⚠️ Código obligatorio.")
        elif not positivos.strip() or not mejorar.strip():
            st.error("⚠️ Debes diligenciar los aspectos positivos y por mejorar.")
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
                "Aspectos por Mejorar": mejorar
            }

            for q, v in resultados.items():
                fila[q] = v

            guardar_datos_google_sheets(fila)

            # -----------------------------------------------
            # 🎉 MENSAJE DE ÉXITO DURANTE 10 SEGUNDOS
            # -----------------------------------------------
            placeholder = st.empty()
            placeholder.success("✅ Monitoreo guardado correctamente")

            import time
            time.sleep(10)
            placeholder.empty()

            # -----------------------------------------------
            # 🔄 REINICIAR FORMULARIO
            # -----------------------------------------------
            st.session_state.clear()
            st.rerun()

# =====================================================================
# 📊 DASHBOARD CASA UR
# =====================================================================
elif pagina == "📊 Dashboard CASA UR":

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay datos para mostrar aún.")
        st.stop()

    # Limpieza
    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área", "Canal", "Asesor"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    # Fijar área CASA UR
    df = df[df["Área"] == "CASA UR"]

    if df.empty:
        st.warning("No hay datos para CASA UR.")
        st.stop()

    meses = {
        1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
        7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
    }

    # ===============================
    # FILTROS
    # ===============================
    st.sidebar.subheader("Filtros CASA UR")

    canal_f = st.sidebar.selectbox("Canal:", ["Todos"] + sorted(df["Canal"].unique()))
    anio_f = st.sidebar.selectbox("Año:", ["Todos"] + sorted(df["Año"].dropna().unique().astype(int)))
    mes_f = st.sidebar.selectbox("Mes:", ["Todos"] + [meses[m] for m in sorted(df["Mes"].dropna().unique())])

    df_filtrado = df.copy()

    if canal_f != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Canal"] == canal_f]

    if anio_f != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Año"] == int(anio_f)]

    if mes_f != "Todos":
        mes_num = [k for k, v in meses.items() if v == mes_f][0]
        df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_num]

    no_filtros = (canal_f == "Todos" and anio_f == "Todos" and mes_f == "Todos")

    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    if no_filtros:
        st.subheader("📊 Dashboard CASA UR")

        c1, c2, c3 = st.columns(3)
        c1.metric("Monitoreos Totales", len(df))

        if "Total" in df.columns:
            promedio_general = df["Total"].mean()
        else:
            promedio_general = 0.0

        c2.metric("Promedio General (Total puntos)", f"{promedio_general:.2f}")
        c3.metric("Errores Críticos", len(df[df["Error crítico"] == "Sí"]))

        # Distribución por Canal
        df_canal = df.groupby("Canal").size().reset_index(name="Total")
        fig_c = px.pie(df_canal, names="Canal", values="Total", title="Distribución por Canal")
        st.plotly_chart(fig_c, use_container_width=True)

        # Cumplimiento por pregunta separado por canal
        st.subheader("Cumplimiento por Pregunta - Canal")

        for canal_actual in df["Canal"].unique():
            st.markdown(f"### 📌 Canal: **{canal_actual}**")
            df_c = df[df["Canal"] == canal_actual]

            preguntas_definidas = obtener_preguntas("CASA UR", canal_actual)
            preguntas_cols = [c for c in preguntas_definidas if c in df_c.columns]

            if not preguntas_cols:
                st.info("No hay preguntas configuradas para este canal.")
                continue

            cumplimiento_canal = []
            for col in preguntas_cols:
                valores = pd.to_numeric(df_c[col], errors="coerce").fillna(0)
                pct = (valores > 0).mean() * 100
                cumplimiento_canal.append({"Pregunta": col, "Cumplimiento": pct})

            df_preg_canal = pd.DataFrame(cumplimiento_canal).sort_values("Cumplimiento")

            fig_h = px.bar(
                df_preg_canal,
                x="Cumplimiento", y="Pregunta",
                orientation="h",
                color="Cumplimiento",
                color_continuous_scale="RdYlGn",
                title=f"Cumplimiento por Pregunta – {canal_actual}"
            )
            fig_h.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
            st.plotly_chart(fig_h, use_container_width=True)

    else:
        st.subheader("📊 Dashboard CASA UR – con filtros")

        c1, c2, c3 = st.columns(3)
        c1.metric("Monitoreos filtrados", len(df_filtrado))

        if "Total" in df_filtrado.columns:
            promedio_general = df_filtrado["Total"].mean()
        else:
            promedio_general = 0.0

        c2.metric("Promedio General (Total puntos)", f"{promedio_general:.2f}")
        c3.metric("Errores Críticos", len(df_filtrado[df_filtrado["Error crítico"] == "Sí"]))

        st.subheader("🔥 Cumplimiento por Pregunta (por Canal, filtrado)")

        for canal_actual in df_filtrado["Canal"].unique():
            st.markdown(f"### 📌 Canal: **{canal_actual}**")
            df_c = df_filtrado[df_filtrado["Canal"] == canal_actual]

            preguntas_definidas = obtener_preguntas("CASA UR", canal_actual)
            preguntas_cols = [c for c in preguntas_definidas if c in df_c.columns]

            if not preguntas_cols:
                st.info("No hay preguntas configuradas para este canal.")
                continue

            cumplimiento_canal = []
            for col in preguntas_cols:
                valores = pd.to_numeric(df_c[col], errors="coerce").fillna(0)
                pct = (valores > 0).mean() * 100
                cumplimiento_canal.append({"Pregunta": col, "Cumplimiento": pct})

            df_preg_canal = pd.DataFrame(cumplimiento_canal).sort_values("Cumplimiento")

            fig_h = px.bar(
                df_preg_canal,
                x="Cumplimiento", y="Pregunta",
                orientation="h",
                color="Cumplimiento",
                color_continuous_scale="RdYlGn",
                title=f"Cumplimiento por Pregunta – {canal_actual} (filtrado)"
            )
            fig_h.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
            st.plotly_chart(fig_h, use_container_width=True)

# =====================================================================
# 📈 DASHBOARD Conecta UR
# =====================================================================
elif pagina == "📈 Dashboard Conecta UR":

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay datos para mostrar aún.")
        st.stop()

    # Limpieza
    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área", "Canal", "Asesor"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    # Fijar área Conecta UR
    df = df[df["Área"] == "Conecta UR"]

    if df.empty:
        st.warning("No hay datos para Conecta UR.")
        st.stop()

    meses = {
        1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
        7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
    }

    # ===============================
    # FILTROS
    # ===============================
    st.sidebar.subheader("Filtros Conecta UR")

    canal_f = st.sidebar.selectbox("Canal:", ["Todos"] + sorted(df["Canal"].unique()))
    anio_f = st.sidebar.selectbox("Año:", ["Todos"] + sorted(df["Año"].dropna().unique().astype(int)))
    mes_f = st.sidebar.selectbox("Mes:", ["Todos"] + [meses[m] for m in sorted(df["Mes"].dropna().unique())])

    df_filtrado = df.copy()

    if canal_f != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Canal"] == canal_f]

    if anio_f != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Año"] == int(anio_f)]

    if mes_f != "Todos":
        mes_num = [k for k, v in meses.items() if v == mes_f][0]
        df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_num]

    no_filtros = (canal_f == "Todos" and anio_f == "Todos" and mes_f == "Todos")

    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    if no_filtros:
        st.subheader("📈 Dashboard Conecta UR – Global (sin filtros)")

        c1, c2, c3 = st.columns(3)
        c1.metric("Monitoreos Totales", len(df))

        if "Total" in df.columns:
            promedio_general = df["Total"].mean()
        else:
            promedio_general = 0.0

        c2.metric("Promedio General (Total puntos)", f"{promedio_general:.2f}")
        c3.metric("Errores Críticos", len(df[df["Error crítico"] == "Sí"]))

        # Distribución por Canal
        df_canal = df.groupby("Canal").size().reset_index(name="Total")
        fig_c = px.pie(df_canal, names="Canal", values="Total", title="Distribución por Canal")
        st.plotly_chart(fig_c, use_container_width=True)

        # Cumplimiento por pregunta separado por canal
        st.subheader("🔥 Cumplimiento por Pregunta (por Canal)")

        for canal_actual in df["Canal"].unique():
            st.markdown(f"### 📌 Canal: **{canal_actual}**")
            df_c = df[df["Canal"] == canal_actual]

            preguntas_definidas = obtener_preguntas("Conecta UR", canal_actual)
            preguntas_cols = [c for c in preguntas_definidas if c in df_c.columns]

            if not preguntas_cols:
                st.info("No hay preguntas configuradas para este canal.")
                continue

            cumplimiento_canal = []
            for col in preguntas_cols:
                valores = pd.to_numeric(df_c[col], errors="coerce").fillna(0)
                pct = (valores > 0).mean() * 100
                cumplimiento_canal.append({"Pregunta": col, "Cumplimiento": pct})

            df_preg_canal = pd.DataFrame(cumplimiento_canal).sort_values("Cumplimiento")

            fig_h = px.bar(
                df_preg_canal,
                x="Cumplimiento", y="Pregunta",
                orientation="h",
                color="Cumplimiento",
                color_continuous_scale="RdYlGn",
                title=f"Cumplimiento por Pregunta – {canal_actual}"
            )
            fig_h.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
            st.plotly_chart(fig_h, use_container_width=True)

    else:
        st.subheader("📈 Dashboard Conecta UR – con filtros")

        c1, c2, c3 = st.columns(3)
        c1.metric("Monitoreos filtrados", len(df_filtrado))

        if "Total" in df_filtrado.columns:
            promedio_general = df_filtrado["Total"].mean()
        else:
            promedio_general = 0.0

        c2.metric("Promedio General (Total puntos)", f"{promedio_general:.2f}")
        c3.metric("Errores Críticos", len(df_filtrado[df_filtrado["Error crítico"] == "Sí"]))

        st.subheader("🔥 Cumplimiento por Pregunta (por Canal, filtrado)")

        for canal_actual in df_filtrado["Canal"].unique():
            st.markdown(f"### 📌 Canal: **{canal_actual}**")
            df_c = df_filtrado[df_filtrado["Canal"] == canal_actual]

            preguntas_definidas = obtener_preguntas("Conecta UR", canal_actual)
            preguntas_cols = [c for c in preguntas_definidas if c in df_c.columns]

            if not preguntas_cols:
                st.info("No hay preguntas configuradas para este canal.")
                continue

            cumplimiento_canal = []
            for col in preguntas_cols:
                valores = pd.to_numeric(df_c[col], errors="coerce").fillna(0)
                pct = (valores > 0).mean() * 100
                cumplimiento_canal.append({"Pregunta": col, "Cumplimiento": pct})

            df_preg_canal = pd.DataFrame(cumplimiento_canal).sort_values("Cumplimiento")

            fig_h = px.bar(
                df_preg_canal,
                x="Cumplimiento", y="Pregunta",
                orientation="h",
                color="Cumplimiento",
                color_continuous_scale="RdYlGn",
                title=f"Cumplimiento por Pregunta – {canal_actual} (filtrado)"
            )
            fig_h.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
            st.plotly_chart(fig_h, use_container_width=True)

# ============================================================
# 🎯 DASHBOARD POR ASESOR – SOLO CUMPLIMIENTO POR PREGUNTA
# ============================================================
elif pagina == "🎯 Dashboard por Asesor":

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay registros para mostrar aún.")
        st.stop()
    
    # Limpieza estándar
    df = df.dropna(how="all")
    df = df.loc[:, df.columns.notna()]
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, df.columns != ""]
    df = df.dropna(subset=["Área","Asesor","Canal"], how="any")

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"]   = df["Fecha"].dt.month
    df["Año"]   = df["Fecha"].dt.year

    meses = {
        1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
        7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
    }

    # ===============================
    # 🎚️ FILTROS
    # ===============================
    st.sidebar.subheader("Filtros Asesor")

    area_f = st.sidebar.selectbox("Área:", ["Todas"] + sorted(df["Área"].unique()))
    canal_f = st.sidebar.selectbox("Canal:", ["Todos"] + sorted(df["Canal"].unique()))
    anio_f = st.sidebar.selectbox("Año:", ["Todos"] + sorted(df["Año"].dropna().unique().astype(int)))
    mes_f = st.sidebar.selectbox("Mes:", ["Todos"] + [meses[m] for m in sorted(df["Mes"].dropna().unique())])

    df_f = df.copy()
    if area_f != "Todas":
        df_f = df_f[df_f["Área"] == area_f]
    if canal_f != "Todos":
        df_f = df_f[df_f["Canal"] == canal_f]
    if anio_f != "Todos":
        df_f = df_f[df_f["Año"] == int(anio_f)]
    if mes_f != "Todos":
        mes_num = [k for k,v in meses.items() if v == mes_f][0]
        df_f = df_f[df_f["Mes"] == mes_num]

    if df_f.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    asesor_sel = st.selectbox("Seleccione un asesor para analizar:", sorted(df_f["Asesor"].unique()))

    df_asesor = df_f[df_f["Asesor"] == asesor_sel]

    st.markdown(f"## 👤 Análisis del Asesor: **{asesor_sel}**")

    # ===============================
    # 🔢 MÉTRICAS INDIVIDUALES
    # ===============================
    c1, c2, c3 = st.columns(3)
    c1.metric("Monitoreos realizados", len(df_asesor))

    # 🟢 Promedio general basado en TOTAL (0–100)
    if "Total" in df_asesor.columns:
        promedio_general = df_asesor["Total"].mean()
    else:
        promedio_general = (df_asesor.filter(like="¿") > 0).mean().mean()*100  

    c2.metric("Promedio general (Total puntos)", f"{promedio_general:.2f}")

    c3.metric("Errores críticos", len(df_asesor[df_asesor["Error crítico"]=="Sí"]))

    st.divider()

    # ===============================
    # 🧠 Preguntas aplicables SOLO al asesor
    # ===============================
    todas_preguntas = [c for c in df_asesor.columns if "¿" in c]

    preguntas_cols_asesor = [
        col for col in todas_preguntas
        if df_asesor[col].notna().sum() > 0
    ]

    if not preguntas_cols_asesor:
        st.info("Este asesor no tiene preguntas registradas.")
        st.stop()

    # ===============================
    # 📌 CUMPLIMIENTO POR PREGUNTA
    # ===============================
    df_long = df_asesor.melt(
        id_vars=["Área", "Asesor", "Canal", "Fecha"],
        value_vars=preguntas_cols_asesor,
        var_name="Pregunta",
        value_name="Puntaje"
    )

    df_long["Puntaje"] = pd.to_numeric(df_long["Puntaje"], errors="coerce")

    df_long_aplica = df_long.dropna(subset=["Puntaje"]).copy()

    df_preg = (
        df_long_aplica
        .assign(Cumple=lambda d: d["Puntaje"] > 0)
        .groupby("Pregunta")["Cumple"]
        .mean()
        .reset_index(name="Cumplimiento")
    )

    df_preg["Cumplimiento"] *= 100

    fig = px.bar(
        df_preg, x="Cumplimiento", y="Pregunta", orientation="h",
        title="📌 Cumplimiento por pregunta",
        color="Cumplimiento", 
        color_continuous_scale="agsunset", 
        range_x=[0,100]
    )
    fig.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
