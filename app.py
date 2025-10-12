import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd
import uuid
import logging
import re

# Configurar logging para debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar funciones de GCP
try:
    from gcp_config import insert_solicitud, get_all_solicitudes, create_table_if_not_exists, verificar_configuracion
    logger.info("✅ Módulo gcp_config importado correctamente")
except ImportError as e:
    st.error(f"❌ Error al importar gcp_config: {str(e)}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Módulo de Crédito - Cooperativa",
    page_icon="💰",
    layout="wide"
)

def formatear_telefono_auto(texto):
    numeros = re.sub(r'\D', '', texto)[:10]
    if len(numeros) <= 3:
        return f"({numeros}"
    elif len(numeros) <= 6:
        return f"({numeros[:3]}) - {numeros[3:]}"
    else:
        return f"({numeros[:3]}) - {numeros[3:6]} - {numeros[6:]}"

# Crear tabla en BigQuery si no existe (solo una vez)
if 'tabla_verificada' not in st.session_state:
    try:
        with st.spinner("🔌 Verificando conexión con BigQuery..."):
            resultado = create_table_if_not_exists()
            if resultado:
                st.session_state.tabla_verificada = True
                st.success("✅ Conexión con BigQuery establecida", icon="✅")
            else:
                st.warning("⚠️ No se pudo verificar la tabla en BigQuery")
    except Exception as e:
        st.error(f"❌ Error de conexión: {str(e)}")

# ==================== INTERFAZ ====================

st.title("💰 Módulo de Crédito - Cooperativa")
st.write("Sistema para gestionar solicitudes de préstamos")

# Tabs
tab1, tab2 = st.tabs(["📝 Nueva Solicitud", "📊 Ver Solicitudes"])

# ==================== TAB 1: FORMULARIO ====================

with tab1:
    st.header("Solicitud de Préstamo")

    with st.form("formulario_prestamo", clear_on_submit=False):
        st.subheader("1. Datos del Solicitante")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo *", placeholder="Ej: Juan Pérez")
            cedula = st.text_input("Cédula *", placeholder="Ej: 40227305527")

            telefono_raw = st.text_input("Teléfono *", placeholder="Ej: 8092851725")
            telefono = formatear_telefono_auto(telefono_raw)

        with col2:
            email = st.text_input("Correo Electrónico", placeholder="Ej: juan@email.com")
            fecha_max = date.today() - timedelta(days=18*365)
            fecha_nacimiento = st.date_input(
                "Fecha de Nacimiento *", 
                min_value=date(1940, 1, 1),
                max_value=fecha_max,
                help="Debes tener al menos 18 años"
            )
            ocupacion = st.text_input("Ocupación *", placeholder="Ej: Contador")

        st.divider()
        st.subheader("2. Información del Préstamo")

        col3, col4 = st.columns(2)
        with col3:
            tipo_prestamo = st.selectbox(
                "Tipo de Préstamo *",
                ["Personal", "Hipotecario", "Vehicular", "Educativo", "Emergencia"]
            )
            monto_solicitado = st.number_input(
                "Monto Solicitado (RD$) *",
                min_value=1000.0,
                max_value=5000000.0,
                value=50000.0,
                step=1000.0,
                format="%.2f"
            )
        with col4:
            plazo_meses = st.slider(
                "Plazo (meses) *",
                min_value=6,
                max_value=120,
                value=12,
                step=6
            )

        st.divider()
        st.subheader("3. Información Adicional")
        proposito = st.text_area("Propósito del Préstamo *", placeholder="Describa brevemente para qué utilizará el préstamo...")

        submitted = st.form_submit_button("📤 Enviar Solicitud")

        if submitted:
            errores = []
            if not nombre or len(nombre) < 3:
                errores.append("❌ El nombre debe tener al menos 3 caracteres")
            if not ocupacion:
                errores.append("❌ La ocupación es obligatoria")
            if not proposito or len(proposito) < 10:
                errores.append("❌ El propósito debe tener al menos 10 caracteres")

            if errores:
                st.error("🚫 Por favor corrige los siguientes errores:")
                for error in errores:
                    st.warning(error)
            else:
                with st.spinner("💾 Guardando solicitud en BigQuery..."):
                    solicitud = {
                        'id': str(uuid.uuid4()),
                        'fecha_solicitud': datetime.now().isoformat(),
                        'nombre': nombre,
                        'cedula': cedula,
                        'telefono': telefono,
                        'email': email if email else None,
                        'fecha_nacimiento': str(fecha_nacimiento),
                        'ocupacion': ocupacion,
                        'tipo_prestamo': tipo_prestamo,
                        'monto_solicitado': float(monto_solicitado),
                        'plazo_meses': int(plazo_meses),
                        'proposito': proposito,
                        'estado': 'Pendiente'
                    }

                    resultado = insert_solicitud(solicitud)
                    if resultado:
                        st.success("✅ ¡Solicitud guardada exitosamente en BigQuery!")
                        st.balloons()
                        st.session_state.form_submitted = True
                    else:
                        st.error("❌ Error al guardar en BigQuery")

if st.session_state.get("form_submitted"):
    if st.button("📝 Nueva Solicitud"):
        st.session_state.form_submitted = False
        st.rerun()

# ==================== TAB 2: VER SOLICITUDES ====================

with tab2:
    st.header("Solicitudes Registradas")
    if st.button("🔄 Recargar datos"):
        st.rerun()

    try:
        with st.spinner("📊 Cargando solicitudes..."):
            df = get_all_solicitudes()

        if df is not None and len(df) > 0:
            st.success(f"✅ Se cargaron **{len(df)}** solicitudes")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 No hay solicitudes registradas aún")

    except Exception as e:
        st.error(f"⚠️ Error al cargar las solicitudes: {str(e)}")
