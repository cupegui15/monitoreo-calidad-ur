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
# FUNCIONES GOOGLE SHEETS
# ===============================
def guardar_datos_google_sheets(data):
    try:
        # Convertir fechas
        for k, v in data.items():
            if isinstance(v, (date,)):
                data[k] = v.strftime("%Y-%m-%d")

        # Credenciales
        creds_json = st.secrets["GCP_SERVICE_ACCOUNT"]
        creds_dict = json.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        # Abrir archivo
        sh = client.open_by_key(st.secrets["GOOGLE_SHEETS_ID"])

        # Crear nombre de hoja dinámico
        nombre_hoja = f"{data['Área']} - {data['Canal']}"

        # Validar si existe la hoja, si no crearla
        try:
            hoja = sh.worksheet(nombre_hoja)
        except gspread.exceptions.WorksheetNotFound:
            hoja = sh.add_worksheet(title=nombre_hoja, rows=5000, cols=100)
            hoja.append_row(list(data.keys()))  # encabezados

        # Obtener encabezados actuales
        encabezados = hoja.row_values(1)

        # Si faltan columnas nuevas (cuando se actualiza formulario)
        for col in data.keys():
            if col not in encabezados:
                encabezados.append(col)
                hoja.resize(cols=len(encabezados))
                hoja.update('1:1', [encabezados])

        # Ordenar valores acorde a los encabezados de la hoja
        fila_ordenada = [data.get(col, "") for col in encabezados]

        hoja.append_row(fila_ordenada)

        st.success(f"✅ Monitoreo guardado correctamente en la hoja '{nombre_hoja}'.")

    except Exception as e:
        st.error(f"❌ Error al guardar en Google Sheets: {e}")


def cargar_todas_las_hojas_google_sheets():
    """
    Carga y consolida todas las hojas del Google Sheet cuyo nombre tenga el formato:
    'Área - Canal', por ejemplo: 'CASA UR - Presencial'.
    """
    try:
        creds_json = st.secrets["GCP_SERVICE_ACCOUNT"]
        creds_dict = json.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sh = client.open_by_key(st.secrets["GOOGLE_SHEETS_ID"])

        dfs = []

        for ws in sh.worksheets():
            title = ws.title  # Ej: "CASA UR - Presencial"
            if " - " not in title:
                continue

            area_name, canal_name = [t.strip() for t in title.split("-", 1)]

            # Validar que corresponda a un área y canal definidos en tu app
            if area_name not in areas:
                continue
            if canal_name not in areas[area_name]["canales"]:
                continue

            records = ws.get_all_records()
            if not records:
                continue

            df_temp = pd.DataFrame(records)

            # Aseguramos que el Área y Canal sean los correctos
            df_temp["Área"] = area_name
            df_temp["Canal"] = canal_name

            dfs.append(df_temp)

        if not dfs:
            return pd.DataFrame()

        df_all = pd.concat(dfs, ignore_index=True)
        return df_all

    except Exception as e:
        st.error(f"⚠️ No se pudieron cargar los datos de todas las hojas: {e}")
        return pd.DataFrame()


def cargar_datos_google_sheets():
    """
    Compatibilidad: usa el consolidado de todas las hojas.
    Se mantiene el nombre original para reutilizar el resto del código.
    """
    return cargar_todas_las_hojas_google_sheets()


# ===============================
# SIDEBAR Y BANNER
# ===============================
st.sidebar.image(URL_LOGO_UR, width=150)
pagina = st.sidebar.radio(
    "Menú:",
    [
        "📝 Formulario de Monitoreo",
        "📊 Dashboard de Análisis",
        "🎯 Dashboard por Asesor",
        "📞 Monitoreo de Llamadas",
    ]
)

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
# 📊 DASHBOARD GENERAL DE ANÁLISIS
# ===============================
elif pagina == "📊 Dashboard de Análisis":
    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay registros para mostrar aún.")
    else:
        # === LIMPIEZA DE DATOS ===
        df = df.dropna(how="all")
        df = df.loc[:, df.columns.notna()]
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:, df.columns != ""]
        df = df.dropna(subset=["Área", "Canal", "Asesor"], how="any")

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

        df_filtrado = df.copy()
        if area_f != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Área"] == area_f]
        if canal_f != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Canal"] == canal_f]
        if anio_f != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Año"] == int(anio_f)]
        if mes_f != "Todos":
            mes_num = [k for k, v in meses.items() if v == mes_f][0]
            df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_num]

        st.caption(
            f"📅 Registros del periodo: "
            f"{mes_f if mes_f!='Todos' else 'Todos los meses'} "
            f"{anio_f if anio_f!='Todos' else ''}"
        )

        if df_filtrado.empty:
            st.warning("⚠️ No hay registros disponibles para los filtros seleccionados.")
        else:
            # ===============================
            # MÉTRICAS GLOBALES
            # ===============================
            c1, c2, c3 = st.columns(3)
            c1.metric("Monitoreos Totales", len(df_filtrado))
            c2.metric("Promedio Puntaje", round(df_filtrado["Total"].mean(), 2))
            c3.metric("Errores Críticos", len(df_filtrado[df_filtrado["Error crítico"] == "Sí"]))

            st.divider()
            st.subheader("📊 Dashboard General de Cumplimiento")

            # ===============================
            # 1️⃣ Cumplimiento promedio por pregunta (como % de veces que cumple)
            # ===============================
            preguntas_cols = [c for c in df_filtrado.columns if "¿" in c or "?" in c]
            df_preguntas = pd.DataFrame(columns=["Pregunta", "Cumplimiento Promedio"])

            for col in preguntas_cols:
                valores = pd.to_numeric(df_filtrado[col], errors="coerce").fillna(0)
                # Cumple si el puntaje es > 0
                cumple_pct = (valores > 0).mean() * 100
                df_preguntas.loc[len(df_preguntas)] = [col, cumple_pct]

            df_preguntas = df_preguntas.sort_values("Cumplimiento Promedio", ascending=True)

            fig_preguntas = px.bar(
                df_preguntas, y="Pregunta", x="Cumplimiento Promedio",
                orientation="h", text="Cumplimiento Promedio",
                title="📈 Cumplimiento Promedio por Pregunta",
                color="Cumplimiento Promedio", color_continuous_scale="blugrn",
                range_x=[0, 100]
            )
            fig_preguntas.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            st.plotly_chart(fig_preguntas, use_container_width=True)

            # ===============================
            # 2️⃣ Cumplimiento promedio por asesor (porcentaje de criterios cumplidos)
            # ===============================
            asesores = df_filtrado["Asesor"].unique()
            df_asesores = []

            for asesor in asesores:
                sub = df_filtrado[df_filtrado["Asesor"] == asesor]
                if sub.empty:
                    continue
                valores = sub[preguntas_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
                cumple_pct = (valores > 0).mean(axis=1).mean() * 100
                df_asesores.append({"Asesor": asesor, "Cumplimiento Promedio": cumple_pct})

            df_asesores = pd.DataFrame(df_asesores).sort_values("Cumplimiento Promedio", ascending=False)

            fig_asesores = px.bar(
                df_asesores, x="Asesor", y="Cumplimiento Promedio",
                title="👥 Cumplimiento Promedio por Asesor",
                color="Cumplimiento Promedio", color_continuous_scale="tealgrn",
                range_y=[0, 100]
            )
            fig_asesores.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
            st.plotly_chart(fig_asesores, use_container_width=True)

            # ===============================
            # 3️⃣ Cumplimiento promedio por canal
            # ===============================
            df_canal = []
            for canal_name, grupo in df_filtrado.groupby("Canal"):
                if grupo.empty:
                    continue
                valores = grupo[preguntas_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
                cumple_pct = (valores > 0).mean().mean() * 100
                df_canal.append({"Canal": canal_name, "Cumplimiento Promedio": cumple_pct})
            df_canal = pd.DataFrame(df_canal)

            fig_canal = px.bar(
                df_canal, x="Canal", y="Cumplimiento Promedio",
                text="Cumplimiento Promedio",
                title="🎧 Cumplimiento Promedio por Canal",
                color="Cumplimiento Promedio", color_continuous_scale="burgyl",
                range_y=[0, 100]
            )
            fig_canal.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            st.plotly_chart(fig_canal, use_container_width=True)

            # ===============================
            # 4️⃣ Distribución de monitoreos por área
            # ===============================
            df_area = df_filtrado.groupby("Área").size().reset_index(name="Total Monitoreos")

            fig_area = px.pie(
                df_area, values="Total Monitoreos", names="Área",
                title="🏢 Distribución de Monitoreos por Área",
                color_discrete_sequence=px.colors.sequential.RdPu
            )
            fig_area.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_area, use_container_width=True)

            # ===============================
            # 5️⃣ Vista rápida tipo Asesor vs Criterio (mapa de calor)
            # ===============================
            st.divider()
            st.subheader("🧑‍💼 Vista rápida: Asesor vs Criterio")

            df_long = df_filtrado.melt(
                id_vars=["Área", "Canal", "Asesor"],
                value_vars=preguntas_cols,
                var_name="Pregunta",
                value_name="Valor"
            )
            df_long["Valor"] = pd.to_numeric(df_long["Valor"], errors="coerce").fillna(0)
            df_long["Cumple"] = (df_long["Valor"] > 0).astype(int)

            resumen_heat = (
                df_long
                .groupby(["Asesor", "Pregunta"])["Cumple"]
                .mean()
                .mul(100)
                .reset_index(name="% Cumplimiento")
            )

            fig_heat = px.density_heatmap(
                resumen_heat,
                x="Asesor", y="Pregunta", z="% Cumplimiento",
                color_continuous_scale="RdYlGn",
                title="Mapa de calor: % de cumplimiento por Asesor y Criterio"
            )
            st.plotly_chart(fig_heat, use_container_width=True)

# ============================================================
# 🎯 NUEVO DASHBOARD POR ASESOR – ANÁLISIS INDIVIDUAL
# ============================================================
elif pagina == "🎯 Dashboard por Asesor":

    df = cargar_datos_google_sheets()

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
    # 🎚️ FILTROS – mismo esquema
    # ===============================
    st.sidebar.subheader("Filtros Asesor")

    area_f = st.sidebar.selectbox("Área (asesor):", ["Todas"] + sorted(df["Área"].unique()))
    canal_f = st.sidebar.selectbox("Canal (asesor):", ["Todos"] + sorted(df["Canal"].unique()))
    anio_f = st.sidebar.selectbox("Año (asesor):", ["Todos"] + sorted(df["Año"].dropna().unique().astype(int)))
    mes_f = st.sidebar.selectbox("Mes (asesor):", ["Todos"] + [meses[m] for m in sorted(df["Mes"].dropna().unique())])

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

    # Selector de asesor (filtro dinámico)
    asesor_sel = st.selectbox("Seleccione un asesor para analizar:", sorted(df_f["Asesor"].unique()))

    df_asesor = df_f[df_f["Asesor"] == asesor_sel]

    st.markdown(f"## 👤 Análisis del Asesor: **{asesor_sel}**")

    # ===============================
    # 🔢 MÉTRICAS INDIVIDUALES
    # ===============================
    c1, c2, c3 = st.columns(3)
    c1.metric("Monitoreos realizados", len(df_asesor))
    c2.metric("Promedio general", round(df_asesor["Total"].mean(), 2))
    c3.metric("Errores críticos", len(df_asesor[df_asesor["Error crítico"]=="Sí"]))

    st.divider()

    # ===============================
    # 🧠 Análisis por pregunta
    # ===============================
    preguntas_cols = [c for c in df_f.columns if "¿" in c]

    df_long = df_asesor.melt(
        id_vars=["Área","Asesor","Canal","Fecha"],
        value_vars=preguntas_cols,
        var_name="Pregunta",
        value_name="Puntaje"
    )

    df_long["Puntaje"] = pd.to_numeric(df_long["Puntaje"], errors="coerce").fillna(0)

    # ===== PROMEDIO DE CADA PREGUNTA DEL ASESOR =====
    df_preg = df_long.groupby("Pregunta")["Puntaje"].mean().reset_index(name="Promedio")

    fig = px.bar(
        df_preg, x="Promedio", y="Pregunta", orientation="h",
        title="📌 Cumplimiento por pregunta (asesor)",
        color="Promedio", color_continuous_scale="agsunset", range_x=[0,20]
    )
    fig.update_traces(texttemplate="%{x:.1f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ===============================
    # 🔥 Heatmap individual (pregunta vs. fecha)
    # ===============================
    df_heat = df_long.copy()
    df_heat["Fecha_str"] = df_heat["Fecha"].dt.strftime("%Y-%m-%d")

    fig_h = px.density_heatmap(
        df_heat, x="Fecha_str", y="Pregunta", z="Puntaje",
        color_continuous_scale="RdYlGn",
        title="🔥 Mapa de calor de desempeño del asesor"
    )
    st.plotly_chart(fig_h, use_container_width=True)

    st.divider()

    # ===============================
    # 🆚 Comparación del asesor vs promedio general (mismo filtro)
    # ===============================
    df_general_long = df_f.melt(
        id_vars=["Área","Asesor","Canal","Fecha"],
        value_vars=preguntas_cols,
        var_name="Pregunta",
        value_name="Puntaje"
    )

    df_general_long["Puntaje"] = pd.to_numeric(df_general_long["Puntaje"], errors="coerce").fillna(0)

    df_comparativo = df_general_long.groupby("Pregunta")["Puntaje"].mean().reset_index(name="Promedio General")
    df_comparativo = df_comparativo.merge(df_preg, on="Pregunta", how="left")
    df_comparativo = df_comparativo.rename(columns={"Promedio":"Promedio Asesor"})

    fig_comp = px.line(
        df_comparativo, x="Pregunta", y=["Promedio General","Promedio Asesor"],
        title="📊 Comparación Asesor vs. Promedio General (mismo filtro)",
        markers=True
    )
    st.plotly_chart(fig_comp, use_container_width=True)

# =====================================================================
# 📞 NUEVO MÓDULO – MONITOREO DE LLAMADAS POR CRITERIO
# =====================================================================
elif pagina == "📞 Monitoreo de Llamadas":

    st.title("📞 Monitoreo de Llamadas – Cumplimiento por Criterio")
    st.caption("Análisis de desempeño por cada uno de los criterios establecidos en la evaluación de llamadas")

    df = cargar_datos_google_sheets()

    if df.empty:
        st.warning("📭 No hay registros de llamadas aún.")
        st.stop()

    # ========== LIMPIEZA BÁSICA ==========
    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área", "Asesor"], how="any")

    # Filtros básicos aquí también (opcional: solo canales de llamadas)
    canales_llamadas = ["Contact Center", "Línea 2030"]
    st.sidebar.subheader("Filtros Llamadas")
    canal_llam_f = st.sidebar.selectbox("Canal de llamadas:", ["Todos"] + canales_llamadas)

    if canal_llam_f != "Todos":
        df = df[df["Canal"] == canal_llam_f]

    # Identificar criterios (preguntas)
    criterios = [c for c in df.columns if "¿" in c]

    if not criterios:
        st.error("⚠️ No se encontraron criterios en la base de datos.")
        st.stop()

    # ===============================
    # 📊 Cálculo de cumplimiento por criterio
    # ===============================
    data_criterios = []

    for crit in criterios:
        valores = pd.to_numeric(df[crit], errors="coerce").fillna(0)
        cumple = (valores > 0).sum()
        total = len(valores)
        pct = (cumple / total) * 100 if total > 0 else 0

        data_criterios.append({
            "Criterio": crit,
            "Cumple": cumple,
            "No cumple": total - cumple,
            "Cumplimiento (%)": pct
        })

    df_criterios = pd.DataFrame(data_criterios)
    df_criterios = df_criterios.sort_values("Cumplimiento (%)", ascending=True)

    # ===============================
    # 📈 Gráfica general de cumplimiento por criterio
    # ===============================
    st.subheader("📈 Cumplimiento total por criterio")

    fig = px.bar(
        df_criterios,
        x="Cumplimiento (%)",
        y="Criterio",
        orientation="h",
        color="Cumplimiento (%)",
        color_continuous_scale="RdYlGn",
        text="Cumplimiento (%)",
        range_x=[0, 100]
    )
    fig.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ===============================
    # 🥧 Gráfica individual por criterio
    # ===============================
    st.subheader("🥧 Cumple vs No cumple por criterio")

    criterio_sel = st.selectbox("Seleccione un criterio:", criterios)

    df_sel = df_criterios[df_criterios["Criterio"] == criterio_sel].iloc[0]

    fig2 = px.pie(
        names=["Cumple", "No cumple"],
        values=[df_sel["Cumple"], df_sel["No cumple"]],
        title=f"Desglose de cumplimiento – {criterio_sel}",
        color_discrete_sequence=px.colors.sequential.RdPu
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ===============================
    # 📄 Tabla detallada
    # ===============================
    st.subheader("📄 Tabla detallada de cumplimiento por criterio")
    st.dataframe(df_criterios, use_container_width=True)
