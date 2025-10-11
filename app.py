import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Módulo de Crédito - Cooperativa",
    page_icon="💰",
    layout="wide"
)

# Título principal
st.title("💰 Módulo de Crédito - Cooperativa")
st.write("Sistema para gestionar solicitudes de préstamos")

# Crear tabs para organizar mejor
tab1, tab2 = st.tabs(["📝 Nueva Solicitud", "📊 Ver Solicitudes"])

with tab1:
    st.header("Solicitud de Préstamo")
    
    # Formulario
    with st.form("formulario_prestamo"):
        st.subheader("1. Datos del Solicitante")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre Completo *", placeholder="Ej: Juan Pérez")
            cedula = st.text_input("Cédula *", placeholder="Ej: 001-1234567-8")
            telefono = st.text_input("Teléfono *", placeholder="Ej: 809-555-1234")
            
        with col2:
            email = st.text_input("Correo Electrónico", placeholder="Ej: juan@email.com")
            # Calcular fecha máxima: hace 18 años desde hoy
            fecha_max_nacimiento = date.today() - timedelta(days=18*365)
            fecha_nacimiento = st.date_input("Fecha de Nacimiento *", 
                                            min_value=date(1940, 1, 1),
                                            max_value=fecha_max_nacimiento,
                                            help="Debes tener al menos 18 años")
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
                step=1000.0
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
        
        proposito = st.text_area(
            "Propósito del Préstamo *",
            placeholder="Describa brevemente para qué utilizará el préstamo..."
        )
        
        # Botón de envío
        submitted = st.form_submit_button("📤 Enviar Solicitud", use_container_width=True)
        
        if submitted:
            # Validaciones
            if not nombre or not cedula or not telefono or not ocupacion:
                st.error("⚠️ Por favor complete todos los campos obligatorios (*)")
            elif len(nombre) < 3:
                st.error("⚠️ El nombre debe tener al menos 3 caracteres")
            elif not proposito or len(proposito) < 10:
                st.error("⚠️ Por favor describa el propósito del préstamo (mínimo 10 caracteres)")
            else:
                # Crear diccionario con los datos
                solicitud = {
                    'fecha_solicitud': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'nombre': nombre,
                    'cedula': cedula,
                    'telefono': telefono,
                    'email': email,
                    'fecha_nacimiento': str(fecha_nacimiento),
                    'ocupacion': ocupacion,
                    'tipo_prestamo': tipo_prestamo,
                    'monto_solicitado': monto_solicitado,
                    'plazo_meses': plazo_meses,
                    'proposito': proposito,
                    'estado': 'Pendiente'
                }
                
                # Guardar en session_state (temporal)
                if 'solicitudes' not in st.session_state:
                    st.session_state.solicitudes = []
                
                st.session_state.solicitudes.append(solicitud)
                
                # TODO: Aquí conectarías con GCP para guardar en BigQuery
                # from google.cloud import bigquery
                # client = bigquery.Client()
                # table_id = "tu-proyecto.tu-dataset.solicitudes_prestamo"
                # errors = client.insert_rows_json(table_id, [solicitud])
                
                st.success("✅ ¡Solicitud enviada exitosamente!")
                st.balloons()
                
                # Mostrar resumen
                with st.expander("📋 Ver Resumen de la Solicitud"):
                    st.json(solicitud)

with tab2:
    st.header("Solicitudes Registradas")
    
    if 'solicitudes' in st.session_state and len(st.session_state.solicitudes) > 0:
        # Convertir a DataFrame para mejor visualización
        df = pd.DataFrame(st.session_state.solicitudes)
        
        st.write(f"Total de solicitudes: {len(df)}")
        
        # Mostrar tabla
        st.dataframe(
            df[['fecha_solicitud', 'nombre', 'tipo_prestamo', 'monto_solicitado', 
                'plazo_meses', 'estado']],
            use_container_width=True
        )
        
        # Botón para limpiar (solo para desarrollo)
        if st.button("🗑️ Limpiar todas las solicitudes (Dev)"):
            st.session_state.solicitudes = []
            st.rerun()
    else:
        st.info("📭 No hay solicitudes registradas aún.")

# Footer
st.divider()
st.caption("💡 Nota: Los datos actualmente se guardan temporalmente. Configura la conexión a GCP para almacenamiento permanente.")