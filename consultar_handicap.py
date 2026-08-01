import pandas as pd
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

print("==================================================")
print("   AUTOMATIZACIÓN DE HÁNDICAP Y MARCAS - THE PLAYERS")
print("==================================================")

# 1. RECIBIR LA FECHA (Desde Excel o manual)
if len(sys.argv) > 1:
    fecha_consulta = sys.argv[1]
    print(f"⛳ Fecha recibida desde Excel: {fecha_consulta}")
else:
    fecha_consulta = input("⛳ Ingresa la fecha a consultar (Formato AAAA-MM-DD): ")

print("\nLeyendo el archivo THE PLAYERS.xlsm...")
try:
    # Asegúrate de que tu archivo en Excel ahora se llama THE PLAYERS.xlsm
    df = pd.read_excel('THE PLAYERS.xlsm', sheet_name='Resultados')
except Exception as e:
    print("❌ Error: No se pudo abrir 'THE PLAYERS.xlsm'. Asegúrate de que está cerrado.")
    sys.exit()

df['Fecha_str'] = df['Fecha'].astype(str).str.split(' ').str[0]
df_jornada = df[df['Fecha_str'] == fecha_consulta].copy()

if df_jornada.empty:
    print(f"\n⚠️ CUIDADO: No se encontraron jugadores registrados para la fecha {fecha_consulta}.")
    sys.exit()

codigos = df_jornada['Codigo'].dropna().astype(int).astype(str).tolist()
print(f"Se encontraron {len(codigos)} jugadores para la jornada del {fecha_consulta}.")

print("Iniciando el navegador de consulta en segundo plano (Headless)...")
opciones = webdriver.ChromeOptions()
opciones.add_argument("--headless")  
opciones.add_argument("--window-size=1920,1080")
opciones.add_argument("--disable-gpu")
opciones.add_argument("--no-sandbox")
opciones.add_argument("--disable-dev-shm-usage")

servicio = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servicio, options=opciones)
wait = WebDriverWait(driver, 40)

resultados_jugadores = []

for codigo in codigos:
    try:
        print(f"\nConsultando el código: {codigo}...")
        driver.get("https://federacioncolombianadegolf.com/handicap/")
        
        # Buscar el jugador
        elemento_menu = wait.until(EC.presence_of_element_located((By.ID, "busqueda")))
        menu = Select(elemento_menu)
        menu.select_by_value("cod")

        campo_texto = wait.until(EC.visibility_of_element_located((By.NAME, "termino_busqueda")))
        campo_texto.clear()
        campo_texto.send_keys(codigo)
        campo_texto.send_keys(Keys.RETURN)

        # Espera inteligente del Índice
        print(" > Esperando a que la página procese el índice...")
        ruta_indice = '//*[@id="content"]/div/div/div[2]/div/div[1]/div[4]/div/div/div[2]/main/section/div[2]/div[3]/span[2]'
        
        valor_indice_str = "--"
        for _ in range(20):
            elemento_indice = wait.until(EC.visibility_of_element_located((By.XPATH, ruta_indice)))
            texto_actual = elemento_indice.text.strip()
            if texto_actual not in ["", "--", "Cargando..."]: 
                valor_indice_str = texto_actual
                break
            time.sleep(1)

        print(f" > ✅ Índice encontrado: {valor_indice_str}")

        # Lógica para elegir la Marca y extraer Hándicap
        try:
            indice_num = float(valor_indice_str.replace(',', '.'))
            
            if indice_num < 18.0:
                marca_elegida = "Azules - 5924"
            else:
                marca_elegida = "Blancas - 5710"
                
            print(f" > Índice es {indice_num}. Seleccionando marca: {marca_elegida}...")
            
            ruta_handicap = '//*[@id="content"]/div/div/div[2]/div/div[1]/div[4]/div/div/div[2]/main/div/section/div[2]'
            
            # Guardamos el hándicap por defecto ANTES de cambiar de marca
            try:
                handicap_viejo = driver.find_element(By.XPATH, ruta_handicap).text.strip()
            except:
                handicap_viejo = "--"
            
            # Seleccionar la nueva marca
            elemento_marcas = wait.until(EC.presence_of_element_located((By.ID, "marca-select")))
            menu_marcas = Select(elemento_marcas)
            menu_marcas.select_by_visible_text(marca_elegida)
            
            # Esperar a que el hándicap se recalcule (cambie el valor)
            print(" > Esperando el recálculo del hándicap de la nueva marca...")
            time.sleep(1.5) 
            
            valor_handicap = "--"
            for _ in range(12): 
                texto_actual_hc = driver.find_element(By.XPATH, ruta_handicap).text.strip()
                
                if texto_actual_hc not in ["", "--", "Cargando..."] and texto_actual_hc != handicap_viejo:
                    valor_handicap = texto_actual_hc
                    break
                time.sleep(1)
            
            # Respaldo por si el número de la nueva marca es exactamente el mismo que el de la vieja
            if valor_handicap == "--":
                valor_handicap = driver.find_element(By.XPATH, ruta_handicap).text.strip()
            
            print(f" > ⛳ Handicap de juego extraído: {valor_handicap}")

        except ValueError:
            print(" > ⚠️ El índice no era un número válido para evaluar. Saltando extracción de handicap.")
            marca_elegida = "N/A"
            valor_handicap = "Sin Datos"

        # Almacenar datos del jugador
        resultados_jugadores.append({
            "Codigo": codigo,
            "Indice_Actualizado": str(valor_indice_str).replace('.', ','),
            "Marca_Asignada": marca_elegida,
            "Handicap_Juego": str(valor_handicap).replace('.', ',')
        })
        
    except Exception as e:
        print(f" > ❌ No se pudo completar la consulta del código {codigo}. Tiempo agotado.")
        resultados_jugadores.append({
            "Codigo": codigo,
            "Indice_Actualizado": "Revisar",
            "Marca_Asignada": "Revisar",
            "Handicap_Juego": "Revisar"
        })

driver.quit()

print("\nCruzando datos y filtrando columnas...")
df_resultados = pd.DataFrame(resultados_jugadores)

df_jornada['Codigo'] = df_jornada['Codigo'].astype(int).astype(str)
df_jornada = df_jornada.drop(columns=['Fecha_str'], errors='ignore')

# Cruzamos todos los datos
df_final = pd.merge(df_jornada, df_resultados, on="Codigo", how="left")

# --- NUEVO FILTRO DE COLUMNAS ---
# Aquí definimos la lista exacta de columnas que quieres conservar.
columnas_deseadas = ['Codigo', 'Apellidos', 'Nombre', 'Indice_Actualizado', 'Marca_Asignada', 'Handicap_Juego']

# Este pequeño ciclo verifica que las columnas existan en tu Excel original para no arrojar error 
# (por ejemplo, si tu columna se llama "Nombres" en vez de "Nombre", simplemente la saltaría).
columnas_existentes = [col for col in columnas_deseadas if col in df_final.columns]

# Sobrescribimos la tabla final solo con las columnas elegidas
df_final = df_final[columnas_existentes]

nombre_archivo = f"Indices_y_Handicap_{fecha_consulta}.xlsx"
df_final.to_excel(nombre_archivo, index=False)

print(f"✅ ¡Proceso terminado! Se ha creado tu archivo: '{nombre_archivo}'.")
print("==================================================")