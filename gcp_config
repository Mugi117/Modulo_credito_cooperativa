from google.cloud import bigquery
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Cargar variables de entorno
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BIGQUERY_DATASET")
TABLE_ID = "solicitudes_prestamo"
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def get_bigquery_client():
    """
    Crea y retorna un cliente de BigQuery autenticado
    """
    try:
        if CREDENTIALS_PATH and os.path.exists(CREDENTIALS_PATH):
            print(f"📁 Usando credenciales de: {CREDENTIALS_PATH}")
            credentials = service_account.Credentials.from_service_account_file(
                CREDENTIALS_PATH,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            client = bigquery.Client(credentials=credentials, project=PROJECT_ID)
        else:
            print("⚠️ No se encontraron credenciales, intentando con las por defecto")
            client = bigquery.Client(project=PROJECT_ID)
        
        # Verificar que el cliente funcione
        client.query("SELECT 1").result()
        print("✅ Cliente de BigQuery conectado exitosamente")
        return client
        
    except Exception as e:
        print(f"❌ Error al conectar con BigQuery: {e}")
        raise e

def create_table_if_not_exists():
    """
    Crea la tabla de solicitudes_prestamo si no existe
    """
    try:
        client = get_bigquery_client()
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        
        schema = [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("fecha_solicitud", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("nombre", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("cedula", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("telefono", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("email", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("fecha_nacimiento", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("ocupacion", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("tipo_prestamo", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("monto_solicitado", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("plazo_meses", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("proposito", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("estado", "STRING", mode="REQUIRED"),
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            table = client.create_table(table)
            print(f"✅ Tabla {table_id} creada exitosamente.")
            return True
        except Exception as e:
            if "Already Exists" in str(e):
                print(f"ℹ️  La tabla {table_id} ya existe.")
                return True
            else:
                print(f"❌ Error al crear la tabla: {e}")
                raise e
                
    except Exception as e:
        print(f"❌ Error en create_table_if_not_exists: {e}")
        return False

def insert_solicitud(solicitud_data):
    """
    Inserta una solicitud en BigQuery
    
    Args:
        solicitud_data (dict): Diccionario con los datos de la solicitud
    
    Returns:
        bool: True si fue exitoso, False si hubo error
    """
    try:
        print("🔄 Iniciando inserción en BigQuery...")
        client = get_bigquery_client()
        
        # IMPORTANTE: Obtener la referencia de la tabla como objeto, no string
        table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
        table = client.get_table(table_ref)
        
        # Convertir fecha_solicitud de string ISO a datetime si es necesario
        # Asegurarse de que sea string antes de insertar
        if isinstance(solicitud_data['fecha_solicitud'], datetime):
            solicitud_data['fecha_solicitud'] = solicitud_data['fecha_solicitud'].isoformat()

        
        # Insertar la fila usando el objeto tabla
        errors = client.insert_rows_json(table, [solicitud_data])
        
        if errors:
            print(f"❌ Errores al insertar datos: {errors}")
            return False
        else:
            print("✅ Solicitud guardada en BigQuery exitosamente.")
            return True
            
    except Exception as e:
        print(f"❌ Error al guardar en BigQuery: {e}")
        print(f"   Detalles del error: {type(e).__name__}: {str(e)}")
        return False

def get_all_solicitudes():
    """
    Obtiene todas las solicitudes de BigQuery
    
    Returns:
        pandas.DataFrame: DataFrame con todas las solicitudes
    """
    try:
        print("🔄 Consultando solicitudes en BigQuery...")
        client = get_bigquery_client()
        
        query = f"""
            SELECT *
            FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
            ORDER BY fecha_solicitud DESC
        """
        
        print(f"📊 Ejecutando query: {query}")
        df = client.query(query).to_dataframe()
        print(f"✅ Se obtuvieron {len(df)} solicitudes")
        return df
        
    except Exception as e:
        print(f"❌ Error al leer de BigQuery: {e}")
        return None

def verificar_configuracion():
    """
    Función de utilidad para verificar que todo esté configurado correctamente
    """
    print("\n" + "="*50)
    print("🔧 VERIFICACIÓN DE CONFIGURACIÓN")
    print("="*50)
    
    # Verificar variables de entorno
    print("\n📋 Variables de entorno:")
    print(f"   PROJECT_ID: {'✅ ' + PROJECT_ID if PROJECT_ID else '❌ No configurado'}")
    print(f"   DATASET_ID: {'✅ ' + DATASET_ID if DATASET_ID else '❌ No configurado'}")
    print(f"   TABLE_ID: ✅ {TABLE_ID}")
    print(f"   CREDENTIALS_PATH: {'✅ ' + CREDENTIALS_PATH if CREDENTIALS_PATH else '⚠️  No configurado (usando default)'}")
    
    if CREDENTIALS_PATH:
        if os.path.exists(CREDENTIALS_PATH):
            print(f"   Archivo de credenciales: ✅ Existe")
        else:
            print(f"   Archivo de credenciales: ❌ No existe en la ruta especificada")
    
    # Intentar conectar
    print("\n🔌 Probando conexión con BigQuery...")
    try:
        client = get_bigquery_client()
        print("   ✅ Conexión exitosa")
        
        # Verificar si el dataset existe
        try:
            dataset = client.get_dataset(DATASET_ID)
            print(f"   ✅ Dataset '{DATASET_ID}' existe")
        except:
            print(f"   ❌ Dataset '{DATASET_ID}' no existe")
            print(f"      Créalo en BigQuery o verifica el nombre")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print("="*50 + "\n")

# Llamar a verificar_configuracion cuando se importe el módulo (opcional)
if __name__ == "__main__":
    verificar_configuracion()
