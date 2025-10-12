"""
Script de diagnóstico para verificar la configuración de BigQuery
Ejecuta este archivo antes de correr tu app principal
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("\n" + "="*60)
print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN DE BIGQUERY")
print("="*60)

# 1. Verificar que las librerías estén instaladas
print("\n1️⃣ Verificando librerías instaladas...")
librerías_requeridas = {
    'google.cloud.bigquery': False,
    'streamlit': False,
    'pandas': False,
    'python-dotenv': False
}

for lib in librerías_requeridas:
    try:
        if lib == 'google.cloud.bigquery':
            import google.cloud.bigquery
        elif lib == 'streamlit':
            import streamlit
        elif lib == 'pandas':
            import pandas
        elif lib == 'python-dotenv':
            import dotenv
        librerías_requeridas[lib] = True
        print(f"   ✅ {lib}")
    except ImportError:
        print(f"   ❌ {lib} - Instálala con: pip install {lib.replace('.', '-')}")

# 2. Verificar archivo .env
print("\n2️⃣ Verificando archivo .env...")
if os.path.exists('.env'):
    print("   ✅ Archivo .env existe")
else:
    print("   ❌ No se encontró archivo .env")
    print("      Crea un archivo llamado .env en la raíz del proyecto")

# 3. Verificar variables de entorno
print("\n3️⃣ Verificando variables de entorno...")
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BIGQUERY_DATASET")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

variables = {
    "GCP_PROJECT_ID": PROJECT_ID,
    "BIGQUERY_DATASET": DATASET_ID,
    "GOOGLE_APPLICATION_CREDENTIALS": CREDENTIALS_PATH
}

todas_configuradas = True
for var_name, var_value in variables.items():
    if var_value:
        print(f"   ✅ {var_name} = {var_value}")
    else:
        print(f"   ❌ {var_name} no está configurada")
        todas_configuradas = False

# 4. Verificar archivo de credenciales
if CREDENTIALS_PATH:
    print("\n4️⃣ Verificando archivo de credenciales...")
    if os.path.exists(CREDENTIALS_PATH):
        print(f"   ✅ El archivo {CREDENTIALS_PATH} existe")
        # Verificar que sea un JSON válido
        try:
            import json
            with open(CREDENTIALS_PATH, 'r') as f:
                creds = json.load(f)
                if 'type' in creds:
                    print(f"   ✅ Es un archivo JSON válido (tipo: {creds['type']})")
                else:
                    print("   ⚠️ El archivo JSON no parece ser de credenciales de GCP")
        except json.JSONDecodeError:
            print("   ❌ El archivo no es un JSON válido")
    else:
        print(f"   ❌ No se encontró el archivo {CREDENTIALS_PATH}")
        print("      Descarga las credenciales desde Google Cloud Console")

# 5. Intentar conectar a BigQuery
if todas_configuradas and all(librerías_requeridas.values()):
    print("\n5️⃣ Intentando conectar a BigQuery...")
    try:
        from gcp_config import get_bigquery_client, verificar_configuracion
        
        # Ejecutar verificación completa
        verificar_configuracion()
        
        print("\n✅ ¡TODO ESTÁ CONFIGURADO CORRECTAMENTE!")
        print("   Puedes ejecutar tu aplicación con: streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Error al conectar: {e}")
        print("\nPosibles soluciones:")
        print("1. Verifica que tu proyecto de GCP exista")
        print("2. Verifica que el dataset exista en BigQuery")
        print("3. Verifica que las credenciales tengan los permisos necesarios")
else:
    print("\n" + "="*60)
    print("⚠️ RESUMEN: Hay problemas de configuración")
    print("="*60)
    print("\n📋 Pasos para resolver:")
    
    if not all(librerías_requeridas.values()):
        print("\n1. Instala las librerías faltantes:")
        print("   pip install google-cloud-bigquery streamlit pandas python-dotenv")
    
    if not os.path.exists('.env'):
        print("\n2. Crea un archivo .env con tu configuración")
    
    if not todas_configuradas:
        print("\n3. Completa las variables de entorno en tu archivo .env")
    
    if CREDENTIALS_PATH and not os.path.exists(CREDENTIALS_PATH):
        print("\n4. Descarga tus credenciales de Google Cloud:")
        print("   - Ve a Google Cloud Console")
        print("   - IAM y administración > Cuentas de servicio")
        print("   - Crea o selecciona una cuenta")
        print("   - Crear clave > JSON")
        print("   - Guarda el archivo como 'credenciales.json'")

print("\n" + "="*60)
