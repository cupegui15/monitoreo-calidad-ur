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
        "📊 Dashboard de Análisis",
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
            st.session_state.form_reset = True
            st.rerun()

# =====================================================================
# 📊 DASHBOARD GENERAL – LÓGICA TIPO A
# =====================================================================
elif pagina == "📊 Dashboard de Análisis":

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay datos para mostrar aún.")
        st.stop()

    # Limpieza
    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área","Canal","Asesor"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    meses = {
        1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
        7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
    }

    # ===============================
    # FILTROS
    # ===============================
    st.sidebar.subheader("Filtros")

    area_f = st.sidebar.selectbox("Área:", ["Todas"] + sorted(df["Área"].unique()))
    canal_f = st.sidebar.selectbox("Canal:", ["Todos"] + sorted(df["Canal"].unique()))
    anio_f = st.sidebar.selectbox("Año:", ["Todos"] + sorted(df["Año"].dropna().unique().astype(int)))
    mes_f = st.sidebar.selectbox("Mes:", ["Todos"] + [meses[m] for m in sorted(df["Mes"].dropna().unique())])

    df_filtrado = df.copy()

    if area_f != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Área"] == area_f]

    if canal_f != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Canal"] == canal_f]

    if anio_f != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Año"] == int(anio_f)]

    if mes_f != "Todos":
        mes_num = [k for k,v in meses.items() if v == mes_f][0]
        df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_num]

    # ---------------------------------
    # LÓGICA A → NO HAY FILTROS
    # ---------------------------------
    no_filtros = (area_f=="Todas" and canal_f=="Todos" and anio_f=="Todos" and mes_f=="Todos")

    if no_filtros:
        st.subheader("📊 Dashboard Global – Sin filtros")

        c1, c2, c3 = st.columns(3)
        c1.metric("Monitoreos Totales", len(df))
        c2.metric("Promedio General (%)", round(((df.filter(like="¿") > 0).mean().mean())*100,2))
        c3.metric("Errores Críticos", len(df[df["Error crítico"]=="Sí"]))

        # Distribución por Área
        df_area = df.groupby("Área").size().reset_index(name="Total")
        fig_a = px.pie(df_area, names="Área", values="Total", title="Distribución por Área")
        st.plotly_chart(fig_a, use_container_width=True)

        # Distribución por Canal
        df_canal = df.groupby("Canal").size().reset_index(name="Total")
        fig_c = px.pie(df_canal, names="Canal", values="Total", title="Distribución por Canal")
        st.plotly_chart(fig_c, use_container_width=True)

        # ===============================
        # HEATMAP GLOBAL (Opción A)
        # ===============================
        preguntas_cols = [c for c in df.columns if "¿" in c]

        df_global = []
        for col in preguntas_cols:
            valores = pd.to_numeric(df[col], errors="coerce").fillna(0)
            pct = (valores > 0).mean() * 100
            df_global.append({"Pregunta": col, "Cumplimiento": pct})

        df_global = pd.DataFrame(df_global).sort_values("Cumplimiento")

        fig_h = px.bar(
            df_global,
            x="Cumplimiento", y="Pregunta",
            orientation="h",
            color="Cumplimiento",
            color_continuous_scale="RdYlGn",
            title="🔥 Cumplimiento Global por Pregunta"
        )
        fig_h.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
        st.plotly_chart(fig_h, use_container_width=True)

        st.stop()

    # --------------------------------------------------------------------
    # SI HAY ALGÚN FILTRO → Dashboard detallado por Área / Canal / Mes
    # --------------------------------------------------------------------
    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    st.subheader("📊 Dashboard General con Filtros")

    c1, c2, c3 = st.columns(3)
    c1.metric("Monitoreos", len(df_filtrado))
    c2.metric("Promedio (%)", round(((df_filtrado.filter(like="¿")>0).mean().mean())*100,2))
    c3.metric("Errores Críticos", len(df_filtrado[df_filtrado["Error crítico"]=="Sí"]))

    # Cumplimiento por pregunta
    preguntas_cols = [c for c in df.columns if "¿" in c]

    df_preg_f = []
    for col in preguntas_cols:
        valores = pd.to_numeric(df_filtrado[col], errors="coerce").fillna(0)
        pct = (valores > 0).mean() * 100
        df_preg_f.append({"Pregunta": col, "Cumplimiento": pct})

    df_preg_f = pd.DataFrame(df_preg_f).sort_values("Cumplimiento")

    fig_pf = px.bar(
        df_preg_f, x="Cumplimiento", y="Pregunta",
        orientation="h",
        color="Cumplimiento",
        color_continuous_scale="RdYlGn",
        title="Cumplimiento por Pregunta (Filtrado)"
    )
    fig_pf.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
    st.plotly_chart(fig_pf, use_container_width=True)

    # Cumplimiento por Canal
    df_canal_f = []
    for canal_name, grupo in df_filtrado.groupby("Canal"):
        pct = ((grupo.filter(like="¿")>0).mean().mean())*100
        df_canal_f.append({"Canal": canal_name, "Cumplimiento": pct})

    df_canal_f = pd.DataFrame(df_canal_f)

    fig_cf = px.bar(
        df_canal_f, x="Canal", y="Cumplimiento",
        color="Cumplimiento",
        color_continuous_scale="tealgrn",
        title="Cumplimiento por Canal"
    )
    st.plotly_chart(fig_cf, use_container_width=True)

    # Heatmap asesor vs criterio (SIN entrar a análisis por asesor)
    df_long = df_filtrado.melt(
        id_vars=["Asesor"],
        value_vars=preguntas_cols,
        var_name="Pregunta",
        value_name="Valor"
    )
    df_long["Cumple"] = (pd.to_numeric(df_long["Valor"], errors="coerce").fillna(0) > 0).astype(int)

    df_heat = (
        df_long.groupby(["Asesor","Pregunta"])["Cumple"].mean().mul(100).reset_index()
    )

    fig_heat = px.density_heatmap(
        df_heat,
        x="Asesor", y="Pregunta", z="% Cumplimiento",
        color_continuous_scale="RdYlGn",
        title="Mapa de Calor – Asesor vs Pregunta (General)"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# =====================================================================
# 🎯 DASHBOARD POR ASESOR
# =====================================================================
elif pagina == "🎯 Dashboard por Asesor":

    df = cargar_todas_las_hojas_google_sheets()

    if df.empty:
        st.warning("📭 No hay registros aún.")
        st.stop()

    # Limpieza
    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Área","Asesor","Canal"])
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month
    df["Año"] = df["Fecha"].dt.year

    meses = {
        1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
        7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
    }

    # Filtros
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

    asesor_sel = st.selectbox("Seleccione un asesor:", sorted(df_f["Asesor"].unique()))
    df_asesor = df_f[df_f["Asesor"] == asesor_sel]

    st.subheader(f"👤 Análisis del Asesor: {asesor_sel}")

    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Monitoreos", len(df_asesor))
    c2.metric("Promedio (%)", round(((df_asesor.filter(like="¿")>0).mean().mean())*100,2))
    c3.metric("Errores Críticos", len(df_asesor[df_asesor["Error crítico"]=="Sí"]))

    preguntas_cols = [c for c in df.columns if "¿" in c]
    preguntas_asesor = [c for c in preguntas_cols if df_asesor[c].notna().sum() > 0]

    # Cumplimiento por pregunta
    df_p = []
    for col in preguntas_asesor:
        pct = (pd.to_numeric(df_asesor[col], errors="coerce").fillna(0)>0).mean()*100
        df_p.append({"Pregunta": col, "Cumplimiento": pct})

    df_p = pd.DataFrame(df_p).sort_values("Cumplimiento")

    fig_p = px.bar(
        df_p, x="Cumplimiento", y="Pregunta",
        orientation="h",
        color="Cumplimiento",
        color_continuous_scale="tealgrn",
        title="Cumplimiento por Pregunta – Asesor"
    )
    fig_p.update_traces(texttemplate="%{x:.1f}%")
    st.plotly_chart(fig_p, use_container_width=True)

    # Heatmap individual
    df_long = df_asesor.melt(
        id_vars=["Fecha"],
        value_vars=preguntas_asesor,
        var_name="Pregunta",
        value_name="Valor"
    )
    df_long["Valor"] = pd.to_numeric(df_long["Valor"], errors="coerce").fillna(0)
    df_long["Fecha_str"] = df_long["Fecha"].dt.strftime("%Y-%m-%d")

    fig_h = px.density_heatmap(
        df_long,
        x="Fecha_str", y="Pregunta", z="Valor",
        color_continuous_scale="RdYlGn",
        title="Mapa de calor del asesor"
    )
    st.plotly_chart(fig_h, use_container_width=True)

    # Comparación con promedio general
    df_general = []
    for col in preguntas_cols:
        pct = (pd.to_numeric(df_f[col], errors="coerce").fillna(0)>0).mean()*100
        df_general.append({"Pregunta": col, "Promedio General": pct})

    df_general = pd.DataFrame(df_general)

    df_comp = df_general.merge(df_p, on="Pregunta", how="left").fillna(0)
    df_comp = df_comp.rename(columns={"Cumplimiento": "Asesor"})

    fig_c = px.line(
        df_comp, x="Pregunta", y=["Promedio General","Asesor"],
        markers=True,
        title="Comparación Asesor vs Promedio General"
    )
    st.plotly_chart(fig_c, use_container_width=True)
