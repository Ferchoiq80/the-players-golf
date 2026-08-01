import sys
import pandas as pd
import pyperclip

ARCHIVO_EXCEL = 'THE PLAYERS.xlsm'

def obtener_fecha_excel():
    # Intenta obtener la fecha de la hoja 'indices' o usa la por defecto
    try:
        xls = pd.ExcelFile(ARCHIVO_EXCEL)
        if 'indices' in xls.sheet_names:
            df_indices = pd.read_excel(xls, sheet_name='indices')
            fecha_val = df_indices.iloc[0, 1] 
            return str(fecha_val).split(" ")[0]
    except Exception:
        pass
    return "25/07/2026"

def generar_reporte_desde_excel(fecha_jornada):
    mensaje = f"""⛳ *THE PLAYERS - RESUMEN DE LA JORNADA* ⛳
📅 *Fecha:* {fecha_jornada}

🏆 *DESTACADO DE LA FECHA*
🥇 *Miguel Enrique Peñaranda Canal*
• Gross: 74 | *Neto: 64* 🔥
• Puntos sumados: +200 pts

💰 *PREMIOS DEL SÁBADO*
• Miguel Enrique Peñaranda: *$200.000*
• Sergio Andres Galavis: *$160.000*
• Libardo Del Carmen Cely: *$120.000*
• Johann Karl Schloeter: *$50.000*
• Juan Carlos Giatsidakis: *$50.000*

📊 *TOP 5 - PLAYERS CHAMPIONSHIP (Acumulado)*
🥇 *Elkin Gregorio Florez Serrano* — 1545 pts (17 asist.)
🥈 *Libardo Del Carmen Cely Soler* — 1520 pts (19 asist.)
🥉 *Edulfo Antonio Mancera Basto* — 1500 pts (16 asist.)
4️⃣ *Elias Jesus Vargas Caceres* — 1485 pts (17 asist.)
5️⃣ *Carlos Augusto Ardila Meneses* — 1470 pts (16 asist.)

👑 *PALMARÉS - TOUR PLAYERS (Ganadores de Copa)*
🏆 *Colproyectos:* Jorge Vargas Cuberos (285 pts)
🏆 *Hospiclinic:* Jairo Jose Bautista Ramirez (265 pts)
🏆 *Mayo:* Libardo Del Carmen Cely Soler (315 pts)
🏆 *Junio:* Edgar Fernando Moreno Vera (315 pts)
🏆 *Julio:* Sergio Andres Galavis Correa (360 pts)

------------------------------------
📲 _Consulta la Web App para ver la tabla completa y el detalle de handicap._
"""
    
    try:
        pyperclip.copy(mensaje)
        print("Éxito")
    except Exception as e:
        print(mensaje)

if __name__ == '__main__':
    # Si Excel envía la fecha como parámetro la usa; de lo contrario lee el libro
    if len(sys.argv) > 1:
        fecha = sys.argv[1]
    else:
        fecha = obtener_fecha_excel()
        
    generar_reporte_desde_excel(fecha)