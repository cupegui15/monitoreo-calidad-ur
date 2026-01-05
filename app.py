import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import time
import textwrap

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

st.markdown("""
<style>
.card {
    background-color: #ffffff;
    padding: 1.2rem 1.4rem;
    border-radius: 10px;
    border: 1px solid #e6e6e6;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}
.card-title {
    font-weight: 600;
    color: #9B0029;
    margin-bottom: 0.6rem;
}
textarea {
    background-color: #fafafa !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# CONFIGURACIÓN DE ÁREAS Y CANALES
# ===============================
areas = {
    "Casa UR": {
        "canales": ["Presencial", "Contact Center", "Chat", "Back Office"],
        "monitores": [
            "Mauricio Ramirez Cubillos",
            "Alejandro Parra Sánchez",
            "Cristian Alberto Upegui M"
        ],
        "asesores": [
            "Adela Bogotá Cagua","David Esteban Puerto Salgado",
            "Diana Marcela Sánchez Cano","Diana Milena Nieto Perez",
            "Jenny Lorena Quintero","Jhon Estiverson Caballero",
            "Jose Edwin Navarro Rondon","Laura Alejandra Bernal Perez","Leidy Johanna Alonso Rincón",
            "Leyner Anyul Silva Avila","Martha Soraya Monsalve Fonseca",
            "Nancy Viviana Bulla Bustos","Nelson Peña Ramírez",
            "Solangel Milena Rodriguez Quitian","Leidy Sofia Ramirez Paez","Nathalia Andrea Bernal Lara",
            "Rafael Ricardo Garcia Gutierrez - TMP", "Laura Sofia Mayac Roa - TMP",
            "Juliana Cadena Rodriguez- TMP","Yesica Yohana Tota Sierra - TMP",
            "Madeline García Fuerte- TMP","Jhon Alexis Cosme Basabe - TMP",
            "Angie Paola Rojas Jeronimo - TMP","Camilo Alexander Huertas Melo - TMP",
            "Angela Yesenia Gomez Martinez - TMP"
        ]
    },
    "Conecta UR": {
        "canales": ["Linea", "Chat", "Sitio"],
        "monitores": [
            "Johanna Rueda Cuvajante",
            "Cristian Alberto Upegui M"
        ],
        "asesores": [
            "Juan Sebastian Silva Gomez","Jennyfer Caicedo Alfonso",
            "Jerly Durley Mendez Fontecha","Addison Rodriguez Casallas",
            "Gabriel Ferney Martinez Lopez","Juan David Gonzalez Jimenez",
            "Miguel Angel Rico Acevedo","Juan Camilo Ortega Clavijo",
            "Andres Fernando Galindo Algarra","Adrian Jose Sosa Gil","Juan David Gonzalez Jimenez",
            "Andrea Katherine Torres Junco","Leidi Daniela Arias Rodriguez", "Wilson David Olarte Hernandez - TMP"
        ]
    }
}

# ===============================
# PREGUNTAS POR CANAL (FUENTE ÚNICA)
# ===============================
def obtener_preguntas(area, canal):
    if area == "Casa UR":
        if canal in ["Presencial", "Contact Center", "Chat"]:
            return [
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
            return [
                "¿Cumple con el ANS establecido para el servicio?",
                "¿Analiza correctamente la solicitud?",
                "¿Gestiona adecuadamente en SAP/UXXI/Bizagi?",
                "¿Respuestas eficaz de acuerdo a la solicitud radicada por el usuario?",
                "¿Es empático al cerrar la solicitud?"
            ]

    elif area == "Conecta UR":
        if canal in ["Linea", "Chat"]:
            return [
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
        elif canal == "Sitio":
            return [
                "¿Cumple con el ANS/SLA establecido?",
                "¿Realiza un análisis completo y pertinente de la solicitud, aplicando diagnóstico claro antes de ejecutar acciones?",
                "¿Gestiona correctamente en las herramientas institucionales (SAP / UXXI / Salesforce u otras) garantizando trazabilidad y registro adecuado?",
                "¿Brinda una respuesta eficaz y alineada a la solicitud radicada por el usuario, asegurando calidad técnica en la solución?",
                "¿Comunica el cierre de la solicitud de manera empática y profesional, validando la satisfacción del usuario?"
            ]
    return []

# ===============================
# PESOS POR CANAL
# ===============================
def obtener_pesos(area, canal):
    if area == "Casa UR":
        if canal in ["Presencial", "Contact Center", "Chat"]:
            return [9, 9, 9, 9, 9, 9, 14, 8, 14, 10]
        elif canal == "Back Office":
            return [20, 20, 20, 20, 20]

    if area == "Conecta UR":
        if canal in ["Linea", "Chat"]:
            return [9, 9, 9, 9, 9, 9, 14, 8, 14, 10]
        elif canal == "Sitio":
            return [20, 20, 20, 20, 20]
    return []

# ===============================
# SOPORTE WRAP PLOTLY
# ===============================
def envolver_pregunta(texto: str, ancho: int = 45) -> str:
    if not isinstance(texto, str):
        return str(texto)
    return "<br>".join(textwrap.wrap(texto.strip(), width=ancho, break_long_words=False))

def _lineas_wrap(s: str) -> int:
    if not isinstance(s, str) or not s:
        return 1
    return s.count("<br>") + 1

def ajustar_grafico_horizontal(fig, df_plot: pd.DataFrame, col_wrapped: str = "Pregunta_wrapped"):
    """
    Ajuste visual homologado para todos los gráficos horizontales:
    - y-axis title: "Criterio evaluado"
    - letra más grande en etiquetas
    - altura dinámica según líneas reales
    """
    if df_plot.empty or col_wrapped not in df_plot.columns:
        total_lineas = 1
    else:
        total_lineas = int(df_plot[col_wrapped].apply(_lineas_wrap).sum())

    height = max(520, 180 + (total_lineas * 32))

    fig.update_layout(
        height=height,
        margin=dict(l=360, r=70, t=70, b=40),
        bargap=0.35
    )
    fig.update_yaxes(
        title_text="Criterio evaluado",
        automargin=True,
        tickfont=dict(size=13, color="#2c2c2c")
    )
    fig.update_xaxes(
        tickfont=dict(size=12),
        title_font=dict(size=13)
    )
    fig.update_coloraxes(
        colorbar_title="Cumplimiento (%)",
        colorbar_title_font=dict(size=12),
        colorbar_tickfont=dict(size=11)
    )
    return fig

# ===============================
# GOOGLE SHEETS: GUARDAR
# ===============================
def guardar_datos_google_sheets(data):
    try:
        for k, v in data.items():
            if isinstance(v, date):
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

        area = data["Área"]
        canal = data["Canal"]

        if area == "Casa UR":
            nombre_hoja = f"Casa UR - {canal}"
        elif area == "Conecta UR":
            nombre_hoja = f"Conecta UR - {canal}"
        else:
            nombre_hoja = f"{area} - {canal}"

        try:
            hoja = sh.worksheet(nombre_hoja)
        except:
            hoja = sh.add_worksheet(title=nombre_hoja, rows=5000, cols=200)
            hoja.append_row(list(data.keys()))

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

    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")

# ===============================
# GOOGLE SHEETS: CARGAR TODAS LAS HOJAS
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
            title = ws.title.strip()
            if " - " not in title:
                continue

            area_name, canal_name = [x.strip() for x in title.split(" - ", 1)]

            if area_name not in areas:
                continue
            if canal_name not in areas[area_name]["canales"]:
                continue

            records = ws.get_all_records()
            if not records:
                continue

            df_temp = pd.DataFrame(records)
            df_temp.columns = [str(c).strip() for c in df_temp.columns]

            preguntas_def = obtener_preguntas(area_name, canal_name)
            for p in preguntas_def:
                if p in df_temp.columns:
                    df_temp[p] = pd.to_numeric(df_temp[p], errors="coerce").fillna(0)

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
# RESET TOTAL DEL FORMULARIO
# ===============================
def resetear_formulario(area_actual: str, canal_actual: str):
    # Campos base
    st.session_state["f_area"] = "Seleccione una opción"
    st.session_state["f_monitor"] = "Seleccione una opción"
    st.session_state["f_asesor"] = "Seleccione una opción"
    st.session_state["f_canal"] = None
    st.session_state["f_codigo"] = ""
    st.session_state["f_fecha"] = date.today()
    st.session_state["f_error"] = "No"
    st.session_state["f_pos"] = ""
    st.session_state["f_mej"] = ""

    # Radios de preguntas (si estaban renderizadas)
    try:
        preguntas = obtener_preguntas(area_actual, canal_actual)
        for q in preguntas:
            k = f"q_{abs(hash((area_actual, canal_actual, q)))%10**10}"
            if k in st.session_state:
                del st.session_state[k]
    except:
        pass
# ===============================
# SIDEBAR Y MENÚ
# ===============================
st.sidebar.image(URL_LOGO_UR, width=150)
pagina = st.sidebar.radio(
    "Menú:",
    [
        "📝 Formulario de Monitoreo",
        "📊 Dashboard Casa UR",
        "📈 Dashboard Conecta UR",
        "🎯 Dashboard por Asesor",
        "📥 Descarga de resultados"
    ]
)

def consolidar_texto(serie):
    textos = serie.dropna().astype(str)
    items = []
    for t in textos:
        for x in t.split("\n"):
            x = x.strip()
            if x:
                items.append(x)
    return "\n".join(sorted(set(items)))

# ===============================
# BANNER
# ===============================
st.markdown(f"""
<div class="banner">
    <div>
        <h2>Monitoreo de Calidad - Universidad del Rosario</h2>
        <p>Comprometidos con la excelencia en la atención al usuario</p>
    </div>
    <div><img src="{URL_BANNER_IMG}" width="130" style="border-radius:6px;"></div>
</div>
""", unsafe_allow_html=True)


if pagina == "📝 Formulario de Monitoreo":

    st.markdown('<div class="section-title">🧾 Registro de Monitoreo</div>', unsafe_allow_html=True)

    # =====================================================
    # SECCIÓN 1 — DATOS GENERALES
    # =====================================================
    c1, c2 = st.columns(2)

    with c1:
        area = st.selectbox(
            "Área",
            ["Seleccione una opción"] + list(areas.keys()),
            key="f_area"
        )

        monitor = st.selectbox(
            "Persona que monitorea",
            ["Seleccione una opción"] +
            (areas[area]["monitores"] if area != "Seleccione una opción" else []),
            key="f_monitor"
        )

    with c2:
        asesor = st.selectbox(
            "Asesor monitoreado",
            ["Seleccione una opción"] +
            (areas[area]["asesores"] if area != "Seleccione una opción" else []),
            key="f_asesor"
        )

        canal = st.selectbox(
            "Canal",
            (areas[area]["canales"] if area != "Seleccione una opción" else []),
            key="f_canal"
        )

    c3, c4 = st.columns(2)

    with c3:
        codigo = st.text_input("Código de la interacción *", key="f_codigo")

    with c4:
        fecha = st.date_input("Fecha de la interacción", date.today(), key="f_fecha")

    error_critico = st.radio(
        "¿Corresponde a un error crítico?",
        ["No", "Sí"],
        horizontal=True,
        key="f_error"
    )

    st.divider()

    # =====================================================
    # SECCIÓN 2 — CRITERIOS DE EVALUACIÓN
    # =====================================================
    st.markdown("Criterios de evaluación")

    preguntas = obtener_preguntas(area, canal) if area != "Seleccione una opción" and canal else []
    pesos = obtener_pesos(area, canal) if area != "Seleccione una opción" and canal else []

    resultados = {}
    total = 0

    if preguntas and pesos and len(preguntas) == len(pesos):

        if error_critico == "Sí":
            st.error("❌ Error crítico: el puntaje total será 0")
            for q in preguntas:
                resultados[q] = 0

        else:
            for q, p in zip(preguntas, pesos):
                key_q = f"q_{abs(hash((area, canal, q))) % 10**10}"
                resp = st.radio(
                    q,
                    ["Cumple", "No cumple"],
                    horizontal=True,
                    key=key_q
                )
                resultados[q] = p if resp == "Cumple" else 0
                total += resultados[q]

    else:
        st.info("Selecciona Área y Canal para cargar los criterios de evaluación.")

    st.divider()

    # =====================================================
    # SECCIÓN 3 — OBSERVACIONES
    # =====================================================
    st.markdown("Observaciones finales")

    o1, o2 = st.columns(2)

    with o1:
        positivos = st.text_area(
            "Aspectos Positivos *",
            height=120,
            placeholder="Ej. Buen manejo del usuario, claridad en la respuesta..."
        )

    with o2:
        mejorar = st.text_area(
            "Aspectos por Mejorar *",
            height=120,
            placeholder="Ej. Validación de identidad, control de tiempos..."
        )

    st.divider()

    # =====================================================
    # SECCIÓN 4 — RESULTADO Y GUARDADO
    # =====================================================

    st.metric("Puntaje Total", total)

    guardar = st.button("💾 Guardar Monitoreo")

    if guardar:

        if area == "Seleccione una opción" or not canal:
            st.error("⚠️ Selecciona Área y Canal.")
        elif monitor == "Seleccione una opción" or asesor == "Seleccione una opción":
            st.error("⚠️ Selecciona monitor y asesor.")
        elif not codigo.strip():
            st.error("⚠️ Código obligatorio.")
        elif not positivos.strip() or not mejorar.strip():
            st.error("⚠️ Debes diligenciar los aspectos.")
        else:
            fila = {
                "Área": area,
                "Canal": canal,
                "Monitor": monitor,
                "Asesor": asesor,
                "Código": codigo.strip(),
                "Fecha": fecha,
                "Error crítico": error_critico,
                "Total": total,
                "Aspectos positivos": positivos,
                "Aspectos por Mejorar": mejorar
            }

            for q, v in resultados.items():
                fila[q] = v

            guardar_datos_google_sheets(fila)
            st.success("✅ Monitoreo guardado correctamente")
            time.sleep(2)
# =====================================================================
# 📊 DASHBOARD Casa UR
# =====================================================================
elif pagina == "📊 Dashboard Casa UR":

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay datos para mostrar aún.")
        st.stop()

    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área", "Canal", "Asesor"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    df = df[df["Área"] == "Casa UR"]
    if df.empty:
        st.warning("No hay datos para Casa UR.")
        st.stop()

    meses = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}

    st.sidebar.subheader("Filtros Casa UR")
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

    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    st.subheader("📊 Dashboard Casa UR")
    c1, c2, c3 = st.columns(3)
    c1.metric("Monitoreos Totales", len(df_filtrado))
    c2.metric("Promedio General (Total puntos)", f"{(df_filtrado['Total'].mean() if 'Total' in df_filtrado.columns else 0.0):.2f}")
    c3.metric("Errores Críticos", len(df_filtrado[df_filtrado["Error crítico"] == "Sí"]))

    st.subheader("📊 Distribución de Monitoreos – Casa UR")

    monit_por_asesor = df_filtrado.groupby("Asesor").size().reset_index(name="Monitoreos").sort_values("Monitoreos", ascending=False)
    fig_asesores = px.bar(monit_por_asesor, x="Asesor", y="Monitoreos", title="Cantidad de Monitoreos por Asesor", text="Monitoreos", color="Monitoreos")
    fig_asesores.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_asesores, use_container_width=True)

    monit_por_monitor = df_filtrado.groupby("Monitor").size().reset_index(name="Monitoreos realizados").sort_values("Monitoreos realizados", ascending=False)
    fig_monitor = px.bar(monit_por_monitor, x="Monitor", y="Monitoreos realizados", title="Cantidad de Monitoreos Realizados por Monitor", text="Monitoreos realizados", color="Monitoreos realizados")
    fig_monitor.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_monitor, use_container_width=True)

    st.subheader("🔥 Cumplimiento por Pregunta – Casa UR")

    for canal_actual in df_filtrado["Canal"].unique():
        st.markdown(f"### 📌 Canal: **{canal_actual}**")
        df_c = df_filtrado[df_filtrado["Canal"] == canal_actual]

        orden_formulario = obtener_preguntas("Casa UR", canal_actual)
        if not orden_formulario:
            st.info("No hay preguntas configuradas para este canal.")
            continue

        cumplimiento_canal = []
        for p in orden_formulario:
            if p not in df_c.columns:
                continue
            valores = pd.to_numeric(df_c[p], errors="coerce").fillna(0)
            pct = (valores > 0).mean() * 100
            cumplimiento_canal.append({"Pregunta": p, "Cumplimiento": pct})

        if not cumplimiento_canal:
            st.info("Aún no hay columnas de preguntas registradas para este canal.")
            continue

        df_preg_canal = pd.DataFrame(cumplimiento_canal)
        mapa_orden = {preg: idx for idx, preg in enumerate(orden_formulario)}
        df_preg_canal["orden"] = df_preg_canal["Pregunta"].map(mapa_orden)
        df_preg_canal = df_preg_canal.sort_values("orden", ascending=False)

        df_preg_canal["Pregunta_wrapped"] = df_preg_canal["Pregunta"].apply(lambda x: envolver_pregunta(x, 45))

        fig_h = px.bar(
            df_preg_canal,
            x="Cumplimiento",
            y="Pregunta_wrapped",
            orientation="h",
            color="Cumplimiento",
            color_continuous_scale="RdYlGn",
            title=f"Cumplimiento por Criterio – {canal_actual}",
            range_x=[0, 100]
        )
        fig_h.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
        fig_h = ajustar_grafico_horizontal(fig_h, df_preg_canal, "Pregunta_wrapped")
        st.plotly_chart(fig_h, use_container_width=True)

# =====================================================================
# 📈 DASHBOARD CONECTA UR
# =====================================================================
elif pagina == "📈 Dashboard Conecta UR":

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay datos para mostrar aún.")
        st.stop()

    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área", "Canal", "Asesor"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    df = df[df["Área"] == "Conecta UR"]
    if df.empty:
        st.warning("No hay datos para Conecta UR.")
        st.stop()

    meses = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}

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

    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    st.subheader("📈 Dashboard Conecta UR – Global")
    c1, c2, c3 = st.columns(3)
    c1.metric("Monitoreos Totales", len(df_filtrado))
    c2.metric("Promedio General (Total puntos)", f"{(df_filtrado['Total'].mean() if 'Total' in df_filtrado.columns else 0.0):.2f}")
    c3.metric("Errores Críticos", len(df_filtrado[df_filtrado["Error crítico"] == "Sí"]))

    st.subheader("📊 Distribución de Monitoreos – Conecta UR")

    monit_por_asesor = df_filtrado.groupby("Asesor").size().reset_index(name="Monitoreos").sort_values("Monitoreos", ascending=False)
    fig_asesores = px.bar(monit_por_asesor, x="Asesor", y="Monitoreos", title="Cantidad de Monitoreos por Asesor", text="Monitoreos", color="Monitoreos")
    fig_asesores.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_asesores, use_container_width=True)

    monit_por_monitor = df_filtrado.groupby("Monitor").size().reset_index(name="Monitoreos realizados").sort_values("Monitoreos realizados", ascending=False)
    fig_monitor = px.bar(monit_por_monitor, x="Monitor", y="Monitoreos realizados", title="Cantidad de Monitoreos Realizados por Monitor", text="Monitoreos realizados", color="Monitoreos realizados")
    fig_monitor.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_monitor, use_container_width=True)

    st.subheader("🔥 Cumplimiento por Pregunta – Conecta UR")

    for canal_actual in df_filtrado["Canal"].unique():
        st.markdown(f"### 📌 Canal: **{canal_actual}**")
        df_c = df_filtrado[df_filtrado["Canal"] == canal_actual]

        orden_formulario = obtener_preguntas("Conecta UR", canal_actual)
        if not orden_formulario:
            st.info("No hay preguntas configuradas para este canal.")
            continue

        cumplimiento_canal = []
        for p in orden_formulario:
            if p not in df_c.columns:
                continue
            valores = pd.to_numeric(df_c[p], errors="coerce").fillna(0)
            pct = (valores > 0).mean() * 100
            cumplimiento_canal.append({"Pregunta": p, "Cumplimiento": pct})

        if not cumplimiento_canal:
            st.info("Aún no hay columnas de preguntas registradas para este canal.")
            continue

        df_preg_canal = pd.DataFrame(cumplimiento_canal)
        mapa_orden = {preg: idx for idx, preg in enumerate(orden_formulario)}
        df_preg_canal["orden"] = df_preg_canal["Pregunta"].map(mapa_orden)
        df_preg_canal = df_preg_canal.sort_values("orden", ascending=False)

        df_preg_canal["Pregunta_wrapped"] = df_preg_canal["Pregunta"].apply(lambda x: envolver_pregunta(x, 45))

        fig_h = px.bar(
            df_preg_canal,
            x="Cumplimiento",
            y="Pregunta_wrapped",
            orientation="h",
            color="Cumplimiento",
            color_continuous_scale="RdYlGn",
            title=f"Cumplimiento por Criterio – {canal_actual}",
            range_x=[0, 100]
        )
        fig_h.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
        fig_h = ajustar_grafico_horizontal(fig_h, df_preg_canal, "Pregunta_wrapped")
        st.plotly_chart(fig_h, use_container_width=True)

# =====================================================================
# 🎯 DASHBOARD POR ASESOR
# =====================================================================
elif pagina == "🎯 Dashboard por Asesor":

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay registros para mostrar aún.")
        st.stop()

    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área", "Asesor", "Canal"], how="any")

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    meses = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}

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
        mes_num = [k for k, v in meses.items() if v == mes_f][0]
        df_f = df_f[df_f["Mes"] == mes_num]

    if df_f.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    asesor_sel = st.selectbox("Seleccione un asesor para analizar:", sorted(df_f["Asesor"].unique()))
    df_asesor = df_f[df_f["Asesor"] == asesor_sel]

    st.markdown(f"## 👤 Análisis del Asesor: **{asesor_sel}**")

    c1, c2, c3 = st.columns(3)
    c1.metric("Monitoreos realizados", len(df_asesor))
    c2.metric("Promedio general (Total puntos)", f"{(df_asesor['Total'].mean() if 'Total' in df_asesor.columns else 0.0):.2f}")
    c3.metric("Errores Críticos", len(df_asesor[df_asesor["Error crítico"] == "Sí"]))

    area_asesor = df_asesor["Área"].iloc[0]
    canal_asesor = df_asesor["Canal"].iloc[0]
    orden_formulario = obtener_preguntas(area_asesor, canal_asesor)
    preguntas_cols = [p for p in orden_formulario if p in df_asesor.columns]

    if not preguntas_cols:
        st.info("Este asesor no tiene preguntas asociadas a su canal o aún no hay columnas en la hoja.")
        st.stop()

    df_long = df_asesor.melt(
        id_vars=["Área", "Asesor", "Canal", "Fecha"],
        value_vars=preguntas_cols,
        var_name="Pregunta",
        value_name="Puntaje"
    )
    df_long["Puntaje"] = pd.to_numeric(df_long["Puntaje"], errors="coerce").fillna(0)

    df_preg = (
        df_long.assign(Cumple=lambda d: d["Puntaje"] > 0)
               .groupby("Pregunta")["Cumple"]
               .mean()
               .reset_index(name="Cumplimiento")
    )
    df_preg["Cumplimiento"] *= 100

    mapa_orden = {preg: idx for idx, preg in enumerate(orden_formulario)}
    df_preg["orden"] = df_preg["Pregunta"].map(mapa_orden)
    df_preg = df_preg.dropna(subset=["orden"]).sort_values("orden", ascending=False)

    df_preg["Pregunta_wrapped"] = df_preg["Pregunta"].apply(lambda x: envolver_pregunta(x, 45))

    fig = px.bar(
        df_preg,
        x="Cumplimiento",
        y="Pregunta_wrapped",
        orientation="h",
        title="📌 Cumplimiento por criterio",
        color="Cumplimiento",
        color_continuous_scale="RdYlGn",
        range_x=[0, 100]
    )
    fig.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
    fig = ajustar_grafico_horizontal(fig, df_preg, "Pregunta_wrapped")
    st.plotly_chart(fig, use_container_width=True)

    # =====================================================================
# 📥 DESCARGA DE RESULTADOS
# =====================================================================
elif pagina == "📥 Descarga de resultados":

    st.subheader("📥 Descarga de consolidado mensual")

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay información disponible.")
        st.stop()

    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área", "Asesor", "Fecha"])

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    meses = {
        1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
        7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
    }

    # -------------------------------
    # FILTROS
    # -------------------------------
    c1, c2, c3 = st.columns(3)

    with c1:
        area_f = st.selectbox("Área:", sorted(df["Área"].unique()))

    with c2:
        anio_f = st.selectbox("Año:", sorted(df["Año"].dropna().unique().astype(int)))

    with c3:
        mes_f = st.selectbox(
            "Mes:",
            [meses[m] for m in sorted(df["Mes"].dropna().unique())]
        )

    mes_num = [k for k, v in meses.items() if v == mes_f][0]

    df_f = df[
        (df["Área"] == area_f) &
        (df["Año"] == anio_f) &
        (df["Mes"] == mes_num)
    ]

    if df_f.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    # -------------------------------
    # CONSOLIDADO
    # -------------------------------
    consolidado = (
        df_f
        .groupby("Asesor")
        .agg(
            **{
                "Cantida Monitoreos": ("Asesor", "count"),
                "Promedio de Total de puntos": ("Total", "mean"),
                "Aspectos Positivos": ("Aspectos positivos", consolidar_texto),
                "Aspectos Por Mejorar": ("Aspectos por Mejorar", consolidar_texto)
            }
        )
        .reset_index()
        .rename(columns={"Asesor": "Nombre Asesor"})
    )

    consolidado["Promedio de Total de puntos"] = (
        consolidado["Promedio de Total de puntos"].round(2)
    )

    # Columna de correo (placeholder)
    consolidado["Correo Electronico"] = ""

    # Orden exacto del archivo oficial
    consolidado = consolidado[
        [
            "Nombre Asesor",
            "Cantida Monitoreos",
            "Promedio de Total de puntos",
            "Correo Electronico",
            "Aspectos Positivos",
            "Aspectos Por Mejorar"
        ]
    ]

    st.dataframe(consolidado, use_container_width=True)

    # -------------------------------
    # DESCARGA EXCEL
    # -------------------------------
    from io import BytesIO

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        consolidado.to_excel(
            writer,
            index=False,
            sheet_name="Correo"
        )

    st.download_button(
        label="📥 Descargar archivo consolidado",
        data=buffer.getvalue(),
        file_name=f"Resultados_{area_f}_{anio_f}_{mes_f}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
