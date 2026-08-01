import streamlit as st
import pandas as pd
import random
import time
import urllib.parse
import os
import base64
import json
import io
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Sorteo The Players", page_icon="⛳", layout="centered", initial_sidebar_state="expanded")

def cargar_video_automatico(ruta_archivo):
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "rb") as f:
            video_bytes = f.read()
        b64_video = base64.b64encode(video_bytes).decode()
        return f'''
            <div style="text-align: center; margin-top: 10px; margin-bottom: 5px;">
                <video width="85%" autoplay loop muted playsinline style="border-radius: 10px; border: 2px solid #c5a059; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <source src="data:video/mp4;base64,{b64_video}" type="video/mp4">
                </video>
            </div>
        '''
    return ""

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .block-container { padding-top: 5rem !important; padding-bottom: 1rem !important; }
    .stApp { background-color: #f8f9fa; }
    div.stButton > button:first-child {
        background-color: #002244; color: white; border: 2px solid #c5a059; 
        border-radius: 8px; padding: 10px 24px; font-size: 18px; font-weight: bold; transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover { background-color: #c5a059; color: #002244; border: 2px solid #002244; }
    h1, h2, h3 { color: #002244 !important; font-family: 'Georgia', serif; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] .stMarkdown h1, 
    [data-testid="stSidebar"] .stMarkdown h2, [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffffff !important; font-weight: 600 !important;
    }
    div[data-testid="stExpander"] { border: 1px solid #c5a059; border-radius: 5px; }
    div[data-testid="stExpander"] summary { background-color: #002244 !important; }
    div[data-testid="stExpander"] summary p { color: #ffffff !important; font-size: 18px; font-weight: bold; }
    div[data-testid="stExpanderDetails"] p { color: #002244 !important; font-size: 16px; }
    hr { border-top: 2px solid #c5a059; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# LECTURA Y PREPARACIÓN DE DATOS
# ==========================================
try:
    df = pd.read_excel('THE PLAYERS.xlsm', sheet_name='Indices', header=5)
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error("❌ No se pudo leer el archivo. Verifica que 'THE PLAYERS.xlsm' esté en la misma carpeta.")
    st.stop()
    
if not {'Nombre', 'Apellidos'}.issubset(df.columns):
    st.error("❌ La hoja 'Indices' no tiene las columnas requeridas (Nombre y Apellidos).")
    st.stop()
    
df_validos = df.dropna(subset=['Nombre', 'Apellidos']).copy()

if df_validos.empty:
    st.warning("⚠️ No se encontraron jugadores en la hoja 'Indices'.")
    st.stop()

total_jugadores = len(df_validos)

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    if os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", use_container_width=True)
        
    st.markdown("---")
    st.markdown("### 🏆 Panel de Control")
    st.markdown("Bienvenido al sistema oficial de sorteo de The Players.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    iniciar_sorteo = st.button("🎲 Iniciar Sorteo en Vivo", type="primary", use_container_width=True)

# ==========================================
# CABECERA DINÁMICA
# ==========================================
html_cabecera = f"""
<div style="text-align: center; margin-top: 20px; margin-bottom: 5px;">
    <h1 style="color: #002244; font-family: 'Georgia', serif; margin: 0; padding: 0; white-space: nowrap; font-size: 2.2rem;">⛳ Sorteo Oficial de Foursomes</h1>
    <div style="background-color: #e8f4f8; border-left: 5px solid #002244; border-right: 5px solid #002244; padding: 5px 15px; border-radius: 5px; display: inline-block; margin-top: 5px;">
        <span style="font-size: 18px; font-weight: bold; color: #002244;">🏌️‍♂️ Total de Jugadores para esta Jornada: {total_jugadores}</span>
    </div>
</div>
"""
st.markdown(html_cabecera, unsafe_allow_html=True)

espacio_visual = st.empty()
video_html = cargar_video_automatico("logo movimiento.mp4")
instruccion_html = "<h4 style='text-align: center; color: #002244; margin-top: 10px;'>👈 Presiona 'Iniciar Sorteo en Vivo' en el Panel de Control para comenzar.</h4>"

# ==========================================
# PREPARAR LA RULETA
# ==========================================
jugadores_solo_nombre = (df_validos['Nombre'].astype(str) + " " + df_validos['Apellidos'].astype(str)).tolist()
jugadores_json = json.dumps(jugadores_solo_nombre)

codigo_ruleta = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ margin: 0; display: flex; justify-content: center; align-items: center; height: 380px; font-family: 'Georgia', serif; overflow: hidden; background-color: transparent;}}
    .wheel-container {{ position: relative; width: 340px; height: 340px; border-radius: 50%; border: 8px solid #002244; box-shadow: 0 0 15px rgba(0,0,0,0.3); overflow: hidden; }}
    .wheel {{ width: 100%; height: 100%; position: absolute; border-radius: 50%; transition: transform 14s cubic-bezier(0.02, 0.5, 0.05, 1); }}
    .slice {{ position: absolute; width: 50%; height: 20px; top: 50%; left: 50%; transform-origin: 0% 50%; margin-top: -10px; font-weight: bold; font-size: 12px; color: #002244; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-left: 25px; box-sizing: border-box; }}
    .pointer-top {{ position: absolute; top: -10px; left: 150px; width: 0; height: 0; border-top: 40px solid #c5a059; border-left: 20px solid transparent; border-right: 20px solid transparent; border-bottom: 0; z-index: 10; filter: drop-shadow(0px 3px 3px rgba(0,0,0,0.5)); }}
    .pointer-bottom {{ position: absolute; bottom: -10px; left: 150px; width: 0; height: 0; border-bottom: 40px solid #c5a059; border-left: 20px solid transparent; border-right: 20px solid transparent; border-top: 0; z-index: 10; filter: drop-shadow(0px 3px 3px rgba(0,0,0,0.5)); }}
    .pointer-left {{ position: absolute; top: 150px; left: -10px; width: 0; height: 0; border-left: 40px solid #c5a059; border-top: 20px solid transparent; border-bottom: 20px solid transparent; border-right: 0; z-index: 10; filter: drop-shadow(0px 3px 3px rgba(0,0,0,0.5)); }}
    .pointer-right {{ position: absolute; top: 150px; right: -10px; width: 0; height: 0; border-right: 40px solid #c5a059; border-top: 20px solid transparent; border-bottom: 20px solid transparent; border-left: 0; z-index: 10; filter: drop-shadow(0px 3px 3px rgba(0,0,0,0.5)); }}
</style>
</head>
<body>
    <div style="position:relative; width: 340px; height: 340px;">
        <div class="pointer-top"></div><div class="pointer-bottom"></div><div class="pointer-left"></div><div class="pointer-right"></div>
        <div class="wheel-container"><div class="wheel" id="wheel"></div></div>
    </div>
    <script>
        const wheel = document.getElementById('wheel');
        const players = {jugadores_json};
        const numPlayers = players.length;
        const sliceAngle = 360 / numPlayers;
        const colors = ['#ffffff', '#c5a059', '#e8f4f8'];
        let gradient = 'conic-gradient('; let currentAngle = 0;
        for(let i=0; i<numPlayers; i++) {{
            let color = colors[i % colors.length]; let nextAngle = currentAngle + sliceAngle;
            gradient += `${{color}} ${{currentAngle}}deg ${{nextAngle}}deg`;
            if(i < numPlayers - 1) gradient += ', ';
            let slice = document.createElement('div'); slice.className = 'slice';
            let rotateAngle = currentAngle + (sliceAngle / 2);
            slice.style.transform = `rotate(${{rotateAngle}}deg)`; slice.innerText = players[i];
            wheel.appendChild(slice); currentAngle = nextAngle;
        }}
        gradient += ')'; wheel.style.background = gradient;
        setTimeout(() => {{
            const extraSpins = 15 * 360; const randomStop = Math.floor(Math.random() * 360);
            wheel.style.transform = `rotate(${{extraSpins + randomStop}}deg)`;
        }}, 100);
    </script>
</body>
</html>
"""

# ==========================================
# LÓGICA DEL SORTEO Y GUARDADO EN EXCEL
# ==========================================
if iniciar_sorteo:
    with espacio_visual:
        components.html(codigo_ruleta, height=400)
    time.sleep(14.2) 
    espacio_visual.empty() 
    
    html_exito = """
    <div style='background-color: #c5a059; padding: 20px; border-radius: 10px; border: 3px solid #002244; text-align: center; margin-bottom: 20px;'>
        <h1 style='color: #002244; font-size: 35px; margin: 0;'>✅ ¡Foursomes Creados!</h1>
    </div>
    """
    espacio_visual.markdown(html_exito, unsafe_allow_html=True)
    st.balloons()
    time.sleep(2.5) 
    
    if video_html:
        espacio_visual.markdown(video_html, unsafe_allow_html=True)
        
    df_mezclado = df_validos.sample(frac=1).reset_index(drop=True)
    resultados_excel = []
    
    for i in range(len(df_mezclado)):
        jugador = df_mezclado.iloc[i]
        num_equipo = (i // 4) + 1
        
        # Extracción segura del "Codigo"
        codigo_encontrado = ""
        for col in jugador.index:
            if 'cod' in str(col).lower():
                codigo_encontrado = jugador[col]
                break
                
        if pd.notna(codigo_encontrado) and str(codigo_encontrado).strip() != "":
            try:
                codigo_limpio = int(float(codigo_encontrado))
            except:
                codigo_limpio = str(codigo_encontrado)
        else:
            codigo_limpio = ""
        
        marca_raw = str(jugador.get('Marca_Asignada', ''))
        if 'Azul' in marca_raw: salida = 'Azul'
        elif 'Blanc' in marca_raw: salida = 'Blanca'
        else: salida = marca_raw
        
        resultados_excel.append({
            'Codigo': codigo_limpio,
            'Apellidos': jugador.get('Apellidos', ''),
            'Nombre': jugador.get('Nombre', ''),
            'Index': jugador.get('Indice_Actualizado', ''),
            'Salida': salida,
            'Hand.': jugador.get('Handicap_Juego', ''),
            'Eq.': num_equipo,
            'Dif': '',  
            'H': ''  
        })

    df_export = pd.DataFrame(resultados_excel)
    
    # Mostrar en pantalla
    st.markdown("## 📋 Foursomes Oficiales")
    col1, col2 = st.columns(2)
    grupos_wa = []
    
    for num_equipo in df_export['Eq.'].unique():
        grupo_df = df_export[df_export['Eq.'] == num_equipo]
        jugadores_grupo = []
        with (col1 if (num_equipo - 1) % 2 == 0 else col2):
            with st.expander(f"⛳ Grupo {num_equipo}", expanded=True):
                for j, row in grupo_df.reset_index().iterrows():
                    jugador_str = f"{row['Nombre']} {row['Apellidos']} - HC: {row['Hand.']}"
                    jugadores_grupo.append(jugador_str)
                    st.write(f"**{j+1}.** {jugador_str}")
        grupos_wa.append({'equipo': num_equipo, 'jugadores': jugadores_grupo})
                
    # ==========================================
    # REGISTRO Y GUARDADO
    # ==========================================
    st.markdown("---")
    st.markdown("### 💾 Registro y Compartir")
    
    # Intento de escritura en vivo con xlwings (Para ejecución local con Excel abierto)
    try:
        import xlwings as xw
        wb = xw.Book('THE PLAYERS.xlsm')
        hoja = wb.sheets['Equipos']
        
        datos_para_pegar = df_export.values.tolist()
        hoja.range('B2').value = datos_para_pegar
        
        rango_modificado = hoja.range(f'B2:J{len(df_export) + 1}')
        rango_modificado.api.RowHeight = 15.5
        rango_modificado.api.Orientation = 0  # Texto en horizontal
        
        st.success("✅ **¡Éxito!** Los datos se escribieron en vivo en tu hoja 'Equipos' de tu Excel abierto.")
    except Exception:
        # En la nube (Streamlit Cloud) o si Excel no está abierto localmente, ofrece botón de descarga
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Equipos')
        
        st.download_button(
            label="📥 Descargar Foursomes en Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="Foursomes_The_Players.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # Crear el mensaje para WhatsApp
    mensaje_wa = "*⛳ RESULTADOS DEL SORTEO - THE PLAYERS ⛳*\n\n"
    mensaje_wa += "_Nota: Los horarios de salida (Tee Times) serán confirmados mañana a primera hora._\n\n"
    
    for g in grupos_wa:
        mensaje_wa += f"*⛳ Grupo {g['equipo']}*\n"
        for j, jug in enumerate(g['jugadores']):
            mensaje_wa += f"  {j+1}. {jug}\n"
        mensaje_wa += "\n"
        
    mensaje_wa += "¡Buen juego para todos! 🏌️‍♂️🏆"
    mensaje_codificado = urllib.parse.quote(mensaje_wa)
    enlace_wa = f"https://api.whatsapp.com/send?text={mensaje_codificado}"
    
    st.link_button("🟢 Enviar Resultados al Grupo de WhatsApp", enlace_wa, use_container_width=True)

    # Script de Auto-Scroll lento
    script_desplazamiento = """
    <script>
        function slowScrollToBottom(element, duration) {
            const start = element.scrollTop;
            const end = element.scrollHeight - element.clientHeight;
            const distance = end - start;
            if (distance <= 0) return;
            let startTime = null;
            function animation(currentTime) {
                if (startTime === null) startTime = currentTime;
                const timeElapsed = currentTime - startTime;
                const progress = Math.min(timeElapsed / duration, 1);
                const easeInOut = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;
                element.scrollTop = start + (distance * easeInOut);
                if (timeElapsed < duration) { requestAnimationFrame(animation); }
            }
            requestAnimationFrame(animation);
        }
        setTimeout(function() {
            try {
                const doc = window.parent.document;
                const container = doc.querySelector('section[data-testid="stMain"]');
                if (container) { slowScrollToBottom(container, 8000); } 
                else { slowScrollToBottom(doc.documentElement, 8000); }
            } catch (e) {}
        }, 1500);
    </script>
    """
    components.html(script_desplazamiento, height=0, width=0)

else:
    html_bloque_inicial = video_html + instruccion_html
    espacio_visual.markdown(html_bloque_inicial, unsafe_allow_html=True)
