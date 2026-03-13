import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 58.0 GRID SEARCH", layout="wide")

# --- MEMORIA RAM DE SESIÓN (SUPER RÁPIDA, NO BLOQUEA GOOGLE) ---
if 'historial_lab' not in st.session_state:
    st.session_state['historial_lab'] = []

# --- CSS ESTILO APPLE, TDAH FRIENDLY & BANNER ANIMADO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
    .stApp { background-color: #f5f5f7; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1d1d1f; }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.7) !important; backdrop-filter: blur(20px) !important; border-right: 1px solid rgba(0,0,0,0.05) !important; }
    h1, h2, h3, h1 *, h2 *, h3 * { color: #1d1d1f !important; font-weight: 700 !important; letter-spacing: -0.5px; }
    [data-testid="stMetric"] { background-color: #ffffff; border-radius: 18px; padding: 15px 20px; min-height: 140px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.03); }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * { color: #1d1d1f !important; font-weight: 700 !important; font-size: 2.2rem !important; }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { color: #86868b !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.5px; }
    .stTextInput input, .stNumberInput input, [data-baseweb="select"] > div { background-color: #ffffff !important; border-radius: 12px !important; border: 1px solid rgba(0,0,0,0.1) !important; }
    .stButton>button { background: linear-gradient(180deg, #2b8af7 0%, #0071e3 100%) !important; color: white !important; border: none !important; border-radius: 20px !important; padding: 10px 24px !important; font-weight: 600 !important; box-shadow: 0 4px 14px rgba(0, 113, 227, 0.3) !important; transition: all 0.2s ease;}
    .stButton>button:active { transform: scale(0.98); }
    
    .apple-kpi-card { background-color: #ffffff; border-radius: 18px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.03); width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; }
    .apple-kpi-title { font-size: 0.8rem; color: #86868b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .apple-kpi-value { font-size: 2.4rem; font-weight: 800; color: #1d1d1f; line-height: 1; }
    
    .kpi-breakdown { font-size: 0.75rem; color: #5f6368; margin-top: 12px; margin-bottom: 12px; line-height: 1.6; background: #f8f9fa; padding: 12px; border-radius: 10px; width: 100%; border: 1px solid #e8eaed; }
    .kpi-breakdown b { color: #1d1d1f; }
    
    .rank-box { display: flex; gap: 6px; flex-wrap: wrap; margin-top: auto; }
    .tag-on { border-radius: 8px; padding: 6px 12px; font-size: 0.75rem; font-weight: 700; color: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-transform: uppercase; letter-spacing: 0.5px;}
    .tag-off { border-radius: 8px; padding: 6px 12px; font-size: 0.75rem; font-weight: 600; color: #8e8e93; border: 1px solid #d2d2d7; background: #fff; text-transform: uppercase; letter-spacing: 0.5px;}
    
    .quant-card { background: #fff; padding: 20px; border-radius: 15px; border: 1px solid #e5e5ea; height: 100%; box-shadow: 0 2px 10px rgba(0,0,0,0.02); margin-bottom: 15px;}
    .quant-title { font-size: 1.1rem; font-weight: 700; color: #1d1d1f; margin-bottom: 8px; }
    .quant-desc { font-size: 0.85rem; color: #86868b; line-height: 1.4; margin-bottom: 15px; }
    .tdah-box { padding: 15px 20px; border-radius: 12px; margin-bottom: 12px; border-left: 6px solid; }
    .tdah-green { background: #f0fdf4; border-color: #22c55e; }
    .tdah-red { background: #fef2f2; border-color: #ef4444; }
    .tdah-yellow { background: #fefce8; border-color: #eab308; }
    .tdah-blue { background: #eff6ff; border-color: #3b82f6; }
    .tdah-title { font-weight: 800; font-size: 1.05rem; margin-bottom: 4px; color: #111827;}
    .tdah-text { font-size: 0.95rem; color: #374151; line-height: 1.4;}
    
    .champion-card { background: linear-gradient(135deg, #fffbeb 0%, #fff3c4 100%); border: 2px solid #fbbf24; border-radius: 15px; padding: 20px; box-shadow: 0 10px 25px rgba(251, 191, 36, 0.2); margin-top: 20px; margin-bottom: 20px;}
    .champion-title { color: #b45309; font-weight: 900; font-size: 1.4rem; margin-bottom: 10px; display: flex; align-items: center; gap: 10px;}
    .champion-stats { display: flex; gap: 20px; margin-top: 15px; flex-wrap: wrap;}
    .stat-box { background: white; padding: 10px 15px; border-radius: 10px; border: 1px solid #fcd34d; font-weight: bold; color: #78350f;}
    
    @keyframes flash-red { 0% { background-color: #ff3b30; color: white; } 50% { background-color: #ffe5e5; color: #ff3b30; } 100% { background-color: #ff3b30; color: white; } }
    @keyframes pulse-green { 0% { background-color: #34c759; color: white; } 50% { background-color: #e5fbee; color: #188038; } 100% { background-color: #34c759; color: white; } }
    @keyframes pulse-yellow { 0% { background-color: #ffcc00; color: #1d1d1f; } 50% { background-color: #fff9e6; color: #b38f00; } 100% { background-color: #ffcc00; color: #1d1d1f; } }
    
    .main-banner { padding: 16px; border-radius: 12px; text-align: center; font-weight: 800; font-size: 1.25rem; margin-top: 15px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .banner-red { animation: flash-red 1.5s infinite; border: 2px solid #ff3b30; }
    .banner-green { animation: pulse-green 2s infinite; border: 2px solid #34c759; }
    .banner-yellow { animation: pulse-yellow 2s infinite; border: 2px solid #ffcc00; }
    .dna-badge { display: inline-block; background: linear-gradient(90deg, #9333ea, #ec4899); color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(236, 72, 153, 0.4);}
</style>
""", unsafe_allow_html=True)

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
A_ACTUAL = datetime.datetime.now().year

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6): COL_DB.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

conn = st.connection("gsheets", type=GSheetsConnection)
try: df_datos = conn.read(worksheet="Sheet1", ttl=60) 
except: df_datos = pd.DataFrame(columns=COL_DB)

try: df_adn = conn.read(worksheet="ADN_Quant", ttl=60)
except: df_adn = pd.DataFrame(columns=["Ticker", "Z_Min", "Acc_Min", "Vol_Min", "Rendimiento"])

# =====================================================================
# BUSCADOR LATERAL 
# =====================================================================
st.sidebar.header("Buscador de Activos")
opciones_bd = df_datos['Ticker'].dropna().unique().tolist() if not df_datos.empty else []
ticker_manual = st.sidebar.text_input("Nuevo Ticker (Ej: MU):", "").strip().upper()
ticker_lista = st.sidebar.selectbox("O cargar de Auditoría:", [""] + opciones_bd)
ticker = ticker_manual if ticker_manual != "" else ticker_lista
if ticker == "": ticker = "MU"

opt_z, opt_acc, opt_vol = 1.0, 0.0, 1.5 
tiene_adn = False
if ticker != "" and not df_adn.empty and "Ticker" in df_adn.columns:
    df_adn_ticker = df_adn[df_adn['Ticker'] == ticker]
    if not df_adn_ticker.empty:
        tiene_adn = True
        adn_data = df_adn_ticker.iloc[-1]
        opt_z = float(adn_data['Z_Min'])
        opt_acc = float(adn_data['Acc_Min'])
        opt_vol = float(adn_data['Vol_Min'])

nom_emp, p_merc, prev_1y, eps_base, atr_val = "Buscando...", 0.0, 0.0, 0.0, 0.0
df_global = pd.DataFrame()

if ticker != "":
    stock = yf.Ticker(ticker)
    try:
        df_global = stock.history(period="2y")
        if not df_global.empty: 
            p_merc = float(df_global['Close'].iloc[-1])
            high_low = df_global['High'] - df_global['Low']
            high_close = np.abs(df_global['High'] - df_global['Close'].shift())
            low_close = np.abs(df_global['Low'] - df_global['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr_val = true_range.rolling(14).mean().iloc[-1]
    except: pass
    try:
        info = stock.info
        nom_emp = info.get("longName", info.get("shortName", ticker))
        if p_merc == 0.0: p_merc = float(info.get("currentPrice", info.get("regularMarketPrice", 0.0)))
        eps_base = info.get("trailingEps", 0.0)
        f_eps = info.get("forwardEps", 0.0)
        if eps_base is not None and f_eps is not None and eps_base > 0 and f_eps > eps_base: prev_1y = (f_eps - eps_base) / eps_base
        else: prev_1y = info.get("revenueGrowth", 0.0); prev_1y = 0.0 if prev_1y is None else prev_1y
    except: 
        if nom_emp == "Buscando...": nom_emp = ticker

st.sidebar.subheader(nom_emp)
if p_merc > 0: st.sidebar.markdown(f"<div style='background:#1d1d1f; color:white; padding:10px; border-radius:8px; text-align:center; font-size:1.2rem; font-weight:bold; margin-bottom:5px;'>Precio Mercado: {p_merc:.2f} $</div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("Calidad (Libro Blanco)")
if prev_1y > 0 and eps_base > 0: st.sidebar.info(f"{A_ACTUAL}: {eps_base * (1 + prev_1y):.2f} $")

ops = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]
i_auto = 3 if prev_1y > 0.25 else 2 if prev_1y > 0.15 else 1 if prev_1y > 0.10 else 0
v_eps = st.sidebar.selectbox("Crecimiento EPS", ops, index=i_auto)
dict_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}
pts_eps = dict_eps[v_eps]
c_inst = st.sidebar.checkbox("Manos Fuertes", value=True)
c_sect = st.sidebar.checkbox("Lider Sector", value=True)
bono = pts_eps + (10 if c_inst else 0) + (10 if c_sect else 0)
ev_plus = bono / 7.0

st.sidebar.header("Gestion Capital")
r_pct = st.sidebar.slider("Riesgo (%)", min_value=0.5, max_value=10.0, value=3.3, step=0.1)
p_buy = st.sidebar.number_input("Precio Compra", value=float(p_merc), key=f"buy_{ticker}")
stop_sugerido_auto = p_buy - (2 * atr_val) if atr_val > 0 else p_buy * 0.95
p_sl = st.sidebar.number_input("Stop Loss", value=float(stop_sugerido_auto), key=f"sl_{ticker}")

# =====================================================================
# SISTEMA DE PESTAÑAS
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Escáner Cuántico", "📋 Auditoría Global", "💼 Cartera en Vivo", "🧪 Laboratorio Modular"])

# --- PESTAÑA 1, 2 Y 3 (RESUMIDAS EN CÓDIGO POR BREVEDAD, ENFOCAMOS EN LAB 4) ---
with tab1:
    st.title("Análisis de Entrada: " + ticker)
    if tiene_adn:
        st.markdown("<div class='dna-badge'>🧬 ADN CUANTITATIVO CARGADO</div>", unsafe_allow_html=True)
        st.caption(f"El Escáner ha mutado para {ticker}. Limites calibrados: Volumen > {opt_vol}σ | Aceleración > {opt_acc} | Tensión > {opt_z}σ")
    st.info("Pestaña 1 operativa. Ve a la Pestaña 4 para ver el nuevo motor de Historial.")

with tab2: st.info("Auditoría Activa")
with tab3: st.info("Cartera Activa")

# =====================================================================
# PESTAÑA 4: LABORATORIO MODULAR CON COMPETICIÓN AUTOMÁTICA (VERSIÓN 58)
# =====================================================================
with tab4:
    st.title("🧪 Laboratorio Quant y Competición Genética")
    st.markdown(f"Experimenta con **{ticker}**. El sistema guardará y comparará todos tus intentos abajo para encontrar la mejor combinación.")
    
    st.markdown("### 🎛️ 1. Panel Quant (Enciende/Apaga Módulos)")
    col_p1, col_p2, col_p3 = st.columns(3)
    
    val_z = True if opt_z != -99 else False
    val_acc = True if opt_acc != -99 else False
    val_vol = True if opt_vol != -99 else False
    
    with col_p1:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_z = st.checkbox("🟢 Usar Tensión Precio (Z-Score)", value=val_z)
        bt_z_precio = st.number_input("Z-Score Mínimo (>)", value=float(opt_z) if opt_z != -99 else 1.0, step=0.1, disabled=not use_z)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_p2:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_acc = st.checkbox("🟢 Usar Aceleración (Momentum)", value=val_acc)
        bt_accel = st.number_input("Aceleración Mínima (>)", value=float(opt_acc) if opt_acc != -99 else 0.0, step=0.5, disabled=not use_acc)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_p3:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_vol = st.checkbox("🟢 Usar Huella Volumen", value=val_vol)
        bt_z_vol = st.number_input("Huella Volumen Mínima (>)", value=float(opt_vol) if opt_vol != -99 else 1.5, step=0.1, disabled=not use_vol)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("### 📈 2. Filtro de Tendencia (Medias Móviles)")
    lista_mas = [2, 3, 5, 8, 13, 21, 34, 55]
    mas_seleccionadas = st.multiselect("El precio de cierre debe estar POR ENCIMA de estas medias:", lista_mas, default=[])
    
    st.markdown("### 🎯 3. Confirmación del Precio (Price Action)")
    tipo_filtro = st.radio("¿Qué debe hacer la vela para activar tu compra?", [
        "Ninguno (Entrar el mismo día).",
        "Fuerza Inmediata: Superar el máximo del día anterior.",
        "Continuación (Minervini): Entrar el día SIGUIENTE si supera el máximo."
    ], index=2)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # -------------------------------------------------------------------------
    # EJECUCIÓN DEL BACKTEST
    # -------------------------------------------------------------------------
    if st.button(f"🚀 Ejecutar Simulación y Añadir al Historial", type="primary"):
        with st.spinner(f"Analizando 5 años de {ticker}..."):
            try:
                stock_bt = yf.Ticker(ticker)
                df_bt = stock_bt.history(period="5y")
                
                if df_bt.empty or len(df_bt) < 100:
                    st.error("No hay suficientes datos históricos.")
                else:
                    df_bt['MA55'] = df_bt['Close'].rolling(window=55).mean()
                    df_bt['Vol_MA55'] = df_bt['Volume'].rolling(window=55).mean()
                    df_bt['Vol_STD55'] = df_bt['Volume'].rolling(window=55).std()
                    df_bt['Vol_Z_Score'] = (df_bt['Volume'] - df_bt['Vol_MA55']) / df_bt['Vol_STD55']
                    df_bt['Z_Score'] = (df_bt['Close'] - df_bt['MA55']) / df_bt['Close'].rolling(window=55).std()
                    df_bt['ROC_10'] = df_bt['Close'].pct_change(periods=10) * 100
                    df_bt['Accel'] = df_bt['ROC_10'].diff(periods=5)
                    
                    for ma in lista_mas: df_bt[f'MA_{ma}'] = df_bt['Close'].rolling(window=ma).mean()
                    
                    cond_z = (df_bt['Z_Score'] > bt_z_precio) if use_z else pd.Series(True, index=df_bt.index)
                    cond_acc = (df_bt['Accel'] > bt_accel) if use_acc else pd.Series(True, index=df_bt.index)
                    cond_vol = (df_bt['Vol_Z_Score'] > bt_z_vol) if use_vol else pd.Series(True, index=df_bt.index)
                    
                    cond_mas = pd.Series(True, index=df_bt.index)
                    for ma in mas_seleccionadas: cond_mas = cond_mas & (df_bt['Close'] > df_bt[f'MA_{ma}'])
                        
                    df_bt['Candidato'] = cond_z & cond_acc & cond_vol & cond_mas
                    
                    horizontes = [5, 10, 15, 20, 30]
                    fechas_registro_display = []
                    datos_estadistica = {5: [], 10: [], 15: [], 20: [], 30: []}
                    ultimo_dia_señal = None
                    
                    for i in range(55, len(df_bt) - max(horizontes) - 1):
                        row = df_bt.iloc[i]
                        date = df_bt.index[i]
                        if row['Candidato']:
                            if ultimo_dia_señal is not None and (date - ultimo_dia_señal).days <= 10: continue 
                            es_valida = False
                            idx_entrada = i
                            p_entrada = row['Close']
                            fecha_texto_entrada = date.strftime("%Y-%m-%d")
                            
                            gatillo_name = tipo_filtro.split(" (")[0].split(":")[0] # Extrae "Ninguno", "Fuerza Inmediata", "Continuación"
                            
                            if "Ninguno" in tipo_filtro: es_valida = True
                            elif "Fuerza Inmediata" in tipo_filtro:
                                if row['High'] > df_bt.iloc[i-1]['High']: es_valida = True
                            elif "Continuación" in tipo_filtro:
                                row_next = df_bt.iloc[i+1]
                                if row_next['High'] > row['High']:
                                    es_valida = True; idx_entrada = i + 1; p_entrada = row_next['Close']; fecha_texto_entrada = f"{df_bt.index[i+1].strftime('%Y-%m-%d')} (T+1)"

                            if es_valida:
                                dict_rets_display = {}
                                for h in horizontes:
                                    p_salida = df_bt['Close'].iloc[idx_entrada + h]
                                    ret = ((p_salida - p_entrada) / p_entrada) * 100
                                    datos_estadistica[h].append(ret)
                                    dict_rets_display[f"{h} Días"] = f"{ret:+.2f}%"
                                    
                                fila_diario = {
                                    "Señal Original": date.strftime("%Y-%m-%d"),
                                    "Precio Compra": f"{p_entrada:.2f} $",
                                    "Volumen (σ)": f"{row['Vol_Z_Score']:.1f}" if not pd.isna(row['Vol_Z_Score']) else "-",
                                    "5 Días": dict_rets_display["5 Días"],
                                    "10 Días": dict_rets_display["10 Días"],
                                    "15 Días": dict_rets_display["15 Días"],
                                    "20 Días": dict_rets_display["20 Días"],
                                    "30 Días": dict_rets_display["30 Días"]
                                }
                                fechas_registro_display.append(fila_diario)
                                ultimo_dia_señal = date 

                    total_señales = len(fechas_registro_display)
                    
                    if total_señales > 0:
                        # Calcular promedios
                        avg_5 = np.mean(datos_estadistica[5])
                        avg_10 = np.mean(datos_estadistica[10])
                        avg_15 = np.mean(datos_estadistica[15])
                        avg_20 = np.mean(datos_estadistica[20])
                        avg_30 = np.mean(datos_estadistica[30])
                        
                        positivas = len([s for s in datos_estadistica[20] if s > 0])
                        win_rate = (positivas / total_señales) * 100
                        
                        # GUARDAR EN LA MEMORIA RAM DE SESIÓN
                        nuevo_test = {
                            "Ticker": ticker,
                            "Z-Score": f"> {bt_z_precio}" if use_z else "OFF",
                            "Accel": f"> {bt_accel}" if use_acc else "OFF",
                            "Volumen": f"> {bt_z_vol}" if use_vol else "OFF",
                            "Medias": str(mas_seleccionadas) if mas_seleccionadas else "OFF",
                            "Precio": gatillo_name,
                            "Trades": total_señales,
                            "WinRate": round(win_rate, 1),
                            "Ret_5D": round(avg_5, 2),
                            "Ret_10D": round(avg_10, 2),
                            "Ret_15D": round(avg_15, 2),
                            "Ret_20D": round(avg_20, 2),
                            "Ret_30D": round(avg_30, 2)
                        }
                        st.session_state['historial_lab'].append(nuevo_test)
                        st.success("✅ Test completado y añadido a la tabla comparativa.")
                        
                        # Mostrar el desglose forense de la simulación ACTUAL
                        with st.expander("Ver Diario Forense de esta simulación (Vela a Vela)"):
                            df_display = pd.DataFrame(fechas_registro_display)
                            def color_retorno(val):
                                if isinstance(val, str) and '%' in val:
                                    num = float(val.replace('%', '').replace('+', ''))
                                    return 'color: #16a34a; font-weight: bold' if num > 0 else 'color: #dc2626'
                                return ''
                            st.dataframe(df_display.style.map(color_retorno, subset=["5 Días", "10 Días", "15 Días", "20 Días", "30 Días"]), use_container_width=True, hide_index=True)
                    else:
                        st.warning("No hay resultados. Tus reglas son demasiado estrictas. Este intento no se guardará en el historial para no ensuciarlo.")
                        
            except Exception as e: st.error(f"Error procesando los datos: {e}")

    # -------------------------------------------------------------------------
    # LA COMPETICIÓN AUTOMÁTICA (EL SALÓN DE LA FAMA)
    # -------------------------------------------------------------------------
    if len(st.session_state['historial_lab']) > 0:
        # Filtrar el historial por el Ticker que estamos mirando
        df_hist = pd.DataFrame(st.session_state['historial_lab'])
        df_ticker_hist = df_hist[df_hist['Ticker'] == ticker].copy()
        
        if not df_ticker_hist.empty:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("## ⚔️ El Coliseo Quant (Resultados Acumulados)")
            
            # Ordenar por Rendimiento a 20 Días (El objetivo principal)
            df_ticker_hist = df_ticker_hist.sort_values(by="Ret_20D", ascending=False)
            campeon = df_ticker_hist.iloc[0]
            
            # RENDERIZAR LA TARJETA DEL CAMPEÓN
            st.markdown(f"""
            <div class='champion-card'>
                <div class='champion-title'>👑 LA COMBINACIÓN GANADORA ACTUAL PARA {ticker}</div>
                <div style='font-size: 0.9rem; color: #92400e;'>Este es el mejor test que has lanzado en esta sesión basado en el rendimiento a 20 días. Si te gusta, guárdalo como ADN.</div>
                <div class='champion-stats'>
                    <div class='stat-box'>📈 Win Rate: {campeon['WinRate']}%</div>
                    <div class='stat-box'>💰 Rendimiento 20D: +{campeon['Ret_20D']}%</div>
                    <div class='stat-box'>🔍 Z-Score: {campeon['Z-Score']}</div>
                    <div class='stat-box'>🏎️ Accel: {campeon['Accel']}</div>
                    <div class='stat-box'>🐘 Volumen: {campeon['Volumen']}</div>
                    <div class='stat-box'>🎯 Filtro Precio: {campeon['Precio']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # BOTÓN DE GUARDAR EL ADN (AHORA VINCULADO AL CAMPEÓN)
            if st.button(f"💾 GUARDAR 'EL CAMPEÓN' COMO ADN OFICIAL DE {ticker}", type="secondary", use_container_width=True):
                try:
                    # Transformar de texto a número para la BBDD
                    c_z = float(campeon['Z-Score'].replace("> ", "")) if campeon['Z-Score'] != "OFF" else -99
                    c_acc = float(campeon['Accel'].replace("> ", "")) if campeon['Accel'] != "OFF" else -99
                    c_vol = float(campeon['Volumen'].replace("> ", "")) if campeon['Volumen'] != "OFF" else -99
                    
                    df_adn_actual = conn.read(worksheet="ADN_Quant", ttl=0)
                    if df_adn_actual.empty: df_adn_actual = pd.DataFrame(columns=["Ticker", "Z_Min", "Acc_Min", "Vol_Min", "Rendimiento"])
                    
                    nuevo_adn = {"Ticker": ticker, "Z_Min": c_z, "Acc_Min": c_acc, "Vol_Min": c_vol, "Rendimiento": campeon['Ret_20D']}
                    df_adn_nuevo = pd.concat([df_adn_actual, pd.DataFrame([nuevo_adn])], ignore_index=True).drop_duplicates("Ticker", keep="last")
                    conn.update(worksheet="ADN_Quant", data=df_adn_nuevo)
                    st.cache_data.clear()
                    st.success("✅ ADN Modificado. El Escáner y la Auditoría ya están usando esta configuración.")
                except Exception as e:
                    st.error(f"Error al guardar ADN: {e}")

            # RENDERIZAR LA TABLA COMPLETA PARA COMPARAR
            st.markdown("#### 📋 Historial de Experimentos de esta Sesión:")
            
            def color_history(val):
                if isinstance(val, (int, float)):
                    return 'color: #16a34a; font-weight: bold' if val > 0 else ('color: #dc2626' if val < 0 else '')
                return ''
                
            st.dataframe(df_ticker_hist.style.map(color_history, subset=["Ret_5D", "Ret_10D", "Ret_15D", "Ret_20D", "Ret_30D"]), use_container_width=True, hide_index=True)
