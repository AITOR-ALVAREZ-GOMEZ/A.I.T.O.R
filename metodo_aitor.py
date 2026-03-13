import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go
import math

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 68.0 FORENSIC INSPECTOR", layout="wide")

# --- MEMORIA RAM DE SESIÓN ---
if 'historial_lab' not in st.session_state:
    st.session_state['historial_lab'] = []

if len(st.session_state['historial_lab']) > 0:
    if "Ret_21D" not in st.session_state['historial_lab'][0]:
        st.session_state['historial_lab'] = []

# --- CSS ESTILO APPLE, TDAH FRIENDLY ---
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
    
    .radar-alert { background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%); color: white; padding: 15px 25px; border-radius: 15px; margin-bottom: 10px; box-shadow: 0 10px 30px rgba(34, 197, 94, 0.2); border: 2px solid #14532d;}
    .radar-alert h2 { color: white !important; margin-top: 0; font-size: 1.5rem; margin-bottom: 5px;}
    .radar-sys-box { background: rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; margin-top: 8px; border: 1px solid rgba(255,255,255,0.4); }
    .radar-wait { background: #f8f9fa; border: 1px dashed #d1d5db; padding: 20px; border-radius: 15px; color: #6b7280; text-align: center; margin-bottom: 15px;}
    
    .dna-badge { display: inline-block; background: linear-gradient(90deg, #9333ea, #ec4899); color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(236, 72, 153, 0.4);}
    .dna-badge-mult { display: inline-block; background: linear-gradient(90deg, #2563eb, #3b82f6); color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);}
    
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
    [data-testid="stExpander"] { border: 2px solid #e5e5ea; border-radius: 15px; background-color: white; overflow: hidden;}
    [data-testid="stExpander"] summary p { font-weight: 800; font-size: 1.1rem; color: #1d1d1f; }
</style>
""", unsafe_allow_html=True)

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
A_ACTUAL = datetime.datetime.now().year

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6): COL_DB.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

conn = st.connection("gsheets", type=GSheetsConnection)

try: df_datos = conn.read(worksheet="Sheet1", ttl=0) 
except: df_datos = pd.DataFrame(columns=COL_DB)

# GESTIÓN DE LA BASE DE DATOS ADN (CON PARCHE PARA NaN y None)
try: 
    df_adn = conn.read(worksheet="ADN_Quant", ttl=0)
    if not df_adn.empty:
        if 'Es_Default' not in df_adn.columns: df_adn['Es_Default'] = True
        if 'ID_ADN' not in df_adn.columns: df_adn['ID_ADN'] = [str(i) for i in range(len(df_adn))]
        if 'WinRate' not in df_adn.columns: df_adn['WinRate'] = 0.0
        # Limpieza de viejos errores en la DB
        df_adn['ID_ADN'] = df_adn['ID_ADN'].fillna("LEGACY")
        df_adn['WinRate'] = df_adn['WinRate'].fillna(0.0)
except: 
    df_adn = pd.DataFrame(columns=["Ticker", "Z_Min", "Acc_Min", "Vol_Min", "Horizonte", "Rendimiento", "WinRate", "Es_Default", "ID_ADN"])

# =====================================================================
# BUSCADOR LATERAL 
# =====================================================================
st.sidebar.header("Buscador de Activos")
opciones_bd = df_datos['Ticker'].dropna().unique().tolist() if not df_datos.empty else []
ticker_manual = st.sidebar.text_input("Nuevo Ticker (Ej: MU):", "").strip().upper()
ticker_lista = st.sidebar.selectbox("O cargar de Auditoría:", [""] + opciones_bd)
ticker = ticker_manual if ticker_manual != "" else ticker_lista
if ticker == "": ticker = "MU"

# --- LECTURA DEL ADN GENÉTICO POR DEFECTO PARA EL ESCÁNER ---
opt_z, opt_acc, opt_vol = 1.0, 0.0, 1.5 
tiene_adn = False
total_adns = 0

if ticker != "" and not df_adn.empty and "Ticker" in df_adn.columns:
    df_adn_ticker = df_adn[df_adn['Ticker'] == ticker]
    total_adns = len(df_adn_ticker)
    if not df_adn_ticker.empty:
        tiene_adn = True
        df_def = df_adn_ticker[df_adn_ticker['Es_Default'] == True]
        if not df_def.empty: adn_data = df_def.iloc[0]
        else: adn_data = df_adn_ticker.iloc[0] 
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

# ---------------------------------------------------------------------
# CALCULADORA DE RIESGO
# ---------------------------------------------------------------------
st.sidebar.header("Gestion Capital")
r_pct = st.sidebar.slider("Riesgo (%)", min_value=0.5, max_value=10.0, value=3.3, step=0.1)
p_buy = st.sidebar.number_input("Precio Compra", value=float(p_merc), key=f"buy_{ticker}")
stop_sugerido_auto = p_buy - (2 * atr_val) if atr_val > 0 else p_buy * 0.95
p_sl = st.sidebar.number_input("Stop Loss", value=float(stop_sugerido_auto), key=f"sl_{ticker}")

distancia_stop = p_buy - p_sl
if distancia_stop > 0 and p_buy > 0:
    riesgo_euros = CAPITAL * (r_pct / 100.0)
    n_tit = math.floor(riesgo_euros / distancia_stop)
    inv_t = n_tit * p_buy
else:
    n_tit = 0; inv_t = 0

if n_tit > 0:
    st.sidebar.markdown(f"<div style='font-size:0.8rem; color:#86868b;'>Acciones a comprar: <b>{n_tit}</b></div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<div style='font-size:0.8rem; color:#86868b;'>Inversión Total: <b>{inv_t:,.2f} $</b></div>", unsafe_allow_html=True)

# =====================================================================
# SISTEMA DE PESTAÑAS 
# =====================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Escáner Cuántico", "📋 Auditoría Global", "💼 Cartera en Vivo", "🧪 Laboratorio Quant", "📡 Radar Diario"])

# ---------------------------------------------------------------------
# PESTAÑA 1, 2 Y 3 (RESUMIDAS POR ESPACIO, ENFOCAMOS EN LAB 4)
# ---------------------------------------------------------------------
with tab1:
    st.title("Análisis de Entrada: " + ticker)
    if st.session_state.get('adn_saved_success', False):
        st.success("✅ ¡ADN Guardado! Se ha añadido a tu Piscina de Sistemas para esta acción.")
        st.session_state['adn_saved_success'] = False
    if tiene_adn:
        if total_adns > 1: st.markdown(f"<div class='dna-badge-mult'>🧬 {total_adns} SISTEMAS VIGILANDO ESTA ACCIÓN</div>", unsafe_allow_html=True)
        else: st.markdown("<div class='dna-badge'>🧬 ADN CUANTITATIVO CARGADO</div>", unsafe_allow_html=True)
        st.caption(f"El Escáner visual muestra tu ADN *Por Defecto*. Límites: Vol > {opt_vol if opt_vol!=-99 else 'OFF'}σ | Accel > {opt_acc if opt_acc!=-99 else 'OFF'} | Tensión > {opt_z if opt_z!=-99 else 'OFF'}σ")
    st.info("Pestaña 1 Operativa. Ve a la Pestaña 4 para usar el nuevo Inspector Forense.")

with tab2: st.info("Auditoría Activa")
with tab3: st.info("Cartera Activa")

# ---------------------------------------------------------------------
# PESTAÑA 4: LABORATORIO MODULAR & INSPECTOR FORENSE (VERSIÓN 68)
# ---------------------------------------------------------------------
with tab4:
    st.title("🧪 Laboratorio Quant y Optimizador Genético")
    st.markdown(f"Experimenta con **{ticker}**. Guarda **múltiples sistemas ganadores** para crear tu propia piscina de estrategias.")
    
    horizontes_fibo = [1, 3, 5, 8, 13, 21, 34, 55, 89]
    str_cols_fibo = [f"Ret_{h}D" for h in horizontes_fibo]

    st.markdown("### 🎛️ 1. Panel Quant Manual")
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
    col_run_man, col_run_auto = st.columns(2)
    
    # --- TEST MANUAL ---
    if col_run_man.button(f"⚙️ Ejecutar Simulación Manual en {ticker}", type="primary", use_container_width=True):
        with st.spinner(f"Analizando 5 años de {ticker}..."):
            try:
                stock_bt = yf.Ticker(ticker)
                df_bt = stock_bt.history(period="5y")
                if df_bt.empty or len(df_bt) < 100: st.error("No hay suficientes datos.")
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
                    
                    fechas_registro_display = []
                    datos_estadistica = {h: [] for h in horizontes_fibo}
                    ultimo_dia_señal = None
                    for i in range(55, len(df_bt) - max(horizontes_fibo) - 1):
                        row = df_bt.iloc[i]
                        date = df_bt.index[i]
                        if row['Candidato']:
                            if ultimo_dia_señal is not None and (date - ultimo_dia_señal).days <= 10: continue 
                            es_valida = False; idx_entrada = i; p_entrada = row['Close']
                            gatillo_name = tipo_filtro.split(" (")[0].split(":")[0] 
                            if "Ninguno" in tipo_filtro: es_valida = True
                            elif "Fuerza Inmediata" in tipo_filtro:
                                if row['High'] > df_bt.iloc[i-1]['High']: es_valida = True
                            elif "Continuación" in tipo_filtro:
                                row_next = df_bt.iloc[i+1]
                                if row_next['High'] > row['High']: es_valida = True; idx_entrada = i + 1; p_entrada = row_next['Close']

                            if es_valida:
                                # GUARDADO FORENSE VELA A VELA
                                fecha_compra_efectiva = df_bt.index[idx_entrada].strftime("%Y-%m-%d")
                                fila_diario = {
                                    "Fecha Señal": date.strftime("%Y-%m-%d"), 
                                    "Entrada": fecha_compra_efectiva,
                                    "Precio": f"{p_entrada:.2f} $", 
                                    "Vol (σ)": f"{row['Vol_Z_Score']:.1f}" if not pd.isna(row['Vol_Z_Score']) else "-"
                                }
                                for h in horizontes_fibo:
                                    p_salida = df_bt['Close'].iloc[idx_entrada + h]
                                    ret = ((p_salida - p_entrada) / p_entrada) * 100
                                    datos_estadistica[h].append(ret)
                                    fila_diario[f"Ret_{h}D"] = ret
                                fechas_registro_display.append(fila_diario)
                                ultimo_dia_señal = date 

                    total_señales = len(fechas_registro_display)
                    if total_señales > 0:
                        positivas = len([s for s in datos_estadistica[21] if s > 0])
                        win_rate = (positivas / total_señales) * 100
                        nuevo_test = {
                            "Ticker": ticker, "Z-Score": f"> {bt_z_precio}" if use_z else "OFF", "Accel": f"> {bt_accel}" if use_acc else "OFF", "Volumen": f"> {bt_z_vol}" if use_vol else "OFF", 
                            "Medias": str(mas_seleccionadas) if mas_seleccionadas else "OFF", "Precio": gatillo_name, "Trades": total_señales, "WinRate": round(win_rate, 1),
                            "Trades_Log": fechas_registro_display # AÑADIDO PARA EL INSPECTOR
                        }
                        for h in horizontes_fibo: nuevo_test[f"Ret_{h}D"] = round(np.mean(datos_estadistica[h]), 2)
                        st.session_state['historial_lab'].append(nuevo_test)
                        st.success("✅ Test manual completado y añadido a la tabla.")
                    else: st.warning("Tus reglas son demasiado estrictas. 0 señales.")
            except Exception as e: st.error(f"Error: {e}")

    # --- TEST AUTO (FUERZA BRUTA) ---
    if col_run_auto.button(f"🤖 Auto-Descubrir ADN Óptimo", type="secondary", use_container_width=True):
        with st.spinner("Probando decenas de combinaciones institucionales..."):
            try:
                stock_bt = yf.Ticker(ticker)
                df_bt = stock_bt.history(period="5y")
                if df_bt.empty or len(df_bt) < 100: st.error("No hay suficientes datos.")
                else:
                    df_bt['MA55'] = df_bt['Close'].rolling(window=55).mean()
                    df_bt['Vol_MA55'] = df_bt['Volume'].rolling(window=55).mean()
                    df_bt['Vol_STD55'] = df_bt['Volume'].rolling(window=55).std()
                    df_bt['Vol_Z_Score'] = (df_bt['Volume'] - df_bt['Vol_MA55']) / df_bt['Vol_STD55']
                    df_bt['Z_Score'] = (df_bt['Close'] - df_bt['MA55']) / df_bt['Close'].rolling(window=55).std()
                    df_bt['ROC_10'] = df_bt['Close'].pct_change(periods=10) * 100
                    df_bt['Accel'] = df_bt['ROC_10'].diff(periods=5)
                    
                    for test_z in [0.5, 1.0, 1.5]:
                        for test_a in [-0.5, 0.0, 0.5]:
                            for test_v in [1.0, 1.5, 2.0]:
                                cond_z = df_bt['Z_Score'] > test_z
                                cond_acc = df_bt['Accel'] > test_a
                                cond_vol = df_bt['Vol_Z_Score'] > test_v
                                df_bt['Candidato'] = cond_z & cond_acc & cond_vol
                                
                                fechas_registro_display = []
                                datos_estadistica = {h: [] for h in horizontes_fibo}
                                ultimo_dia_señal = None
                                total_señales = 0
                                
                                for i in range(55, len(df_bt) - max(horizontes_fibo) - 1):
                                    row = df_bt.iloc[i]
                                    date = df_bt.index[i]
                                    if row['Candidato']:
                                        if ultimo_dia_señal is not None and (date - ultimo_dia_señal).days <= 10: continue 
                                        row_next = df_bt.iloc[i+1]
                                        if row_next['High'] > row['High']:
                                            idx_entrada = i + 1; p_entrada = row_next['Close']
                                            fecha_compra_efectiva = df_bt.index[idx_entrada].strftime("%Y-%m-%d")
                                            
                                            # GUARDADO FORENSE VELA A VELA PARA AUTO
                                            fila_diario = {
                                                "Fecha Señal": date.strftime("%Y-%m-%d"), 
                                                "Entrada": fecha_compra_efectiva,
                                                "Precio": f"{p_entrada:.2f} $", 
                                                "Vol (σ)": f"{row['Vol_Z_Score']:.1f}" if not pd.isna(row['Vol_Z_Score']) else "-"
                                            }
                                            for h in horizontes_fibo:
                                                p_salida = df_bt['Close'].iloc[idx_entrada + h]
                                                ret = ((p_salida - p_entrada) / p_entrada) * 100
                                                datos_estadistica[h].append(ret)
                                                fila_diario[f"Ret_{h}D"] = ret
                                            fechas_registro_display.append(fila_diario)
                                            total_señales += 1
                                            ultimo_dia_señal = date 
                                
                                if total_señales > 0:
                                    win_rate = (len([s for s in datos_estadistica[21] if s > 0]) / total_señales) * 100
                                    nuevo_test = {
                                        "Ticker": ticker, "Z-Score": f"> {test_z}", "Accel": f"> {test_a}", "Volumen": f"> {test_v}", 
                                        "Medias": "OFF", "Precio": "Continuación", "Trades": total_señales, "WinRate": round(win_rate, 1),
                                        "Trades_Log": fechas_registro_display # AÑADIDO PARA EL INSPECTOR
                                    }
                                    for h in horizontes_fibo: nuevo_test[f"Ret_{h}D"] = round(np.mean(datos_estadistica[h]), 2)
                                    st.session_state['historial_lab'].append(nuevo_test)
            except Exception as e: st.error(f"Error: {e}")

    # LA COMPETICIÓN Y GUARDADO
    if len(st.session_state['historial_lab']) > 0:
        df_hist = pd.DataFrame(st.session_state['historial_lab'])
        df_ticker_hist = df_hist[df_hist['Ticker'] == ticker].copy()
        
        if not df_ticker_hist.empty:
            st.markdown("---")
            st.markdown("## ⚔️ El Coliseo Quant (Resultados)")
            st.markdown("<div style='background:#f0fdf4; padding:15px; border-radius:10px; border:1px solid #22c55e; margin-bottom:20px;'>", unsafe_allow_html=True)
            objetivo_opt = st.selectbox("🏆 ¿A cuántos días vista quieres encontrar al Campeón?", [f"{h} Días" for h in horizontes_fibo], index=5)
            st.markdown("</div>", unsafe_allow_html=True)
            
            col_orden = f"Ret_{objetivo_opt.split(' ')[0]}D"
            df_ticker_hist = df_ticker_hist.sort_values(by=col_orden, ascending=False)
            campeon = df_ticker_hist.iloc[0]
            
            st.markdown(f"""
            <div class='champion-card'>
                <div class='champion-title'>👑 LA COMBINACIÓN GANADORA PARA MAXIMIZAR A {objetivo_opt.upper()}</div>
                <div class='champion-stats'>
                    <div class='stat-box'>📈 Win Rate: {campeon['WinRate']}%</div>
                    <div class='stat-box' style='background:#fef3c7; border-color:#d97706;'>💰 Rendimiento: +{campeon[col_orden]}%</div>
                    <div class='stat-box'>🔍 Z-Score: {campeon['Z-Score']}</div>
                    <div class='stat-box'>🏎️ Accel: {campeon['Accel']}</div>
                    <div class='stat-box'>🐘 Volumen: {campeon['Volumen']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"💾 GUARDAR ESTE SISTEMA EN LA PISCINA DE ADN DE {ticker}", type="primary", use_container_width=True):
                with st.spinner("Añadiendo a la base de datos..."):
                    try:
                        c_z = float(campeon['Z-Score'].replace("> ", "")) if campeon['Z-Score'] != "OFF" else -99
                        c_acc = float(campeon['Accel'].replace("> ", "")) if campeon['Accel'] != "OFF" else -99
                        c_vol = float(campeon['Volumen'].replace("> ", "")) if campeon['Volumen'] != "OFF" else -99
                        
                        df_adn_actual = conn.read(worksheet="ADN_Quant", ttl=0)
                        nuevo_id = str(int(datetime.datetime.now().timestamp()))
                        es_def = True if df_adn_actual[df_adn_actual['Ticker'] == ticker].empty else False
                        
                        nuevo_adn = {
                            "Ticker": ticker, "Z_Min": c_z, "Acc_Min": c_acc, "Vol_Min": c_vol, 
                            "Horizonte": objetivo_opt, "Rendimiento": campeon[col_orden], 
                            "WinRate": campeon['WinRate'], "Es_Default": es_def, "ID_ADN": nuevo_id
                        }
                        
                        df_adn_nuevo = pd.concat([df_adn_actual, pd.DataFrame([nuevo_adn])], ignore_index=True)
                        conn.update(worksheet="ADN_Quant", data=df_adn_nuevo)
                        st.cache_data.clear(); st.session_state['adn_saved_success'] = True; st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

            st.markdown("#### 📋 Historial de esta Sesión:")
            def color_history(val):
                if isinstance(val, (int, float)): return 'color: #16a34a; font-weight: bold' if val > 0 else ('color: #dc2626' if val < 0 else '')
                return ''
            
            # Quitar la columna 'Trades_Log' antes de mostrar la tabla general
            df_mostrar = df_ticker_hist.drop(columns=['Trades_Log'], errors='ignore')
            styled_df = df_mostrar.style.map(color_history, subset=str_cols_fibo)
            styled_df = styled_df.set_properties(**{'background-color': '#fffbeb'}, subset=[col_orden])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

            # -----------------------------------------------------------------
            # 🔍 EL NUEVO INSPECTOR FORENSE
            # -----------------------------------------------------------------
            st.markdown("---")
            st.markdown("### 🔍 Inspección Forense (Auditoría Vela a Vela)")
            st.markdown("Selecciona uno de los tests de arriba para ver las fechas exactas en las que la máquina compró y verifica si fueron operaciones lógicas en tu gráfico de TradingView.")
            
            # Recuperar la lista de tests reales para este ticker desde la memoria RAM (manteniendo el orden original o el de pandas)
            tests_del_ticker = [t for t in st.session_state['historial_lab'] if t['Ticker'] == ticker]
            
            opciones_inspector = []
            for i, t in enumerate(tests_del_ticker):
                texto_opcion = f"Test #{i+1} | Z: {t['Z-Score']} | Accel: {t['Accel']} | Vol: {t['Volumen']} | {t['Trades']} Entradas"
                opciones_inspector.append(texto_opcion)
                
            if opciones_inspector:
                test_elegido_str = st.selectbox("Abre la caja negra de un Test:", opciones_inspector)
                idx_elegido = int(test_elegido_str.split("#")[1].split(" ")[0]) - 1
                
                datos_forenses = tests_del_ticker[idx_elegido].get("Trades_Log", [])
                
                if datos_forenses:
                    df_forense = pd.DataFrame(datos_forenses)
                    
                    # Formatear porcentajes para visualización
                    def format_pct(val):
                        if isinstance(val, (int, float)): return f"{val:+.2f}%"
                        return val
                        
                    for col in str_cols_fibo:
                        if col in df_forense.columns:
                            df_forense[col] = df_forense[col].apply(format_pct)
                    
                    def color_forense(val):
                        if isinstance(val, str) and '%' in val:
                            num = float(val.replace('%', '').replace('+', ''))
                            return 'color: #16a34a; font-weight: bold' if num > 0 else 'color: #dc2626'
                        return ''
                        
                    st.dataframe(df_forense.style.map(color_forense, subset=str_cols_fibo), use_container_width=True, hide_index=True)
                else:
                    st.info("Este test no generó ninguna entrada para analizar.")

    # -------------------------------------------------------------------------
    # EL GESTOR DE ADN
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown(f"## 🧬 Tu Banco de ADN para {ticker}")
    if tiene_adn:
        st.markdown("Estos son los sistemas que están vigilando esta acción. **El Radar Diario buscará oportunidades en TODOS ellos a la vez.**")
        
        df_display_adn = df_adn_ticker.copy()
        
        df_display_adn['Es_Default'] = df_display_adn['Es_Default'].apply(lambda x: "⭐ SÍ" if x else "No")
        df_display_adn['Z_Min'] = df_display_adn['Z_Min'].apply(lambda x: f"> {x}" if x != -99 else "OFF")
        df_display_adn['Acc_Min'] = df_display_adn['Acc_Min'].apply(lambda x: f"> {x}" if x != -99 else "OFF")
        df_display_adn['Vol_Min'] = df_display_adn['Vol_Min'].apply(lambda x: f"> {x}" if x != -99 else "OFF")
        
        cols_to_show = ['ID_ADN', 'Es_Default', 'Horizonte', 'Rendimiento', 'WinRate', 'Z_Min', 'Acc_Min', 'Vol_Min']
        st.dataframe(df_display_adn[cols_to_show], hide_index=True, use_container_width=True)
        
        col_m1, col_m2 = st.columns(2)
        adn_a_gestionar = col_m1.selectbox("Selecciona la ID de un ADN para gestionarlo:", df_display_adn['ID_ADN'].tolist())
        
        if col_m2.button("⭐ Establecer como ADN Principal (Se verá en el Escáner)", use_container_width=True):
            df_adn_full = conn.read(worksheet="ADN_Quant", ttl=0)
            df_adn_full.loc[df_adn_full['Ticker'] == ticker, 'Es_Default'] = False
            df_adn_full.loc[df_adn_full['ID_ADN'] == str(adn_a_gestionar), 'Es_Default'] = True
            conn.update(worksheet="ADN_Quant", data=df_adn_full)
            st.cache_data.clear(); st.rerun()
            
        if col_m2.button("🗑️ Borrar este ADN", use_container_width=True):
            df_adn_full = conn.read(worksheet="ADN_Quant", ttl=0)
            df_adn_full = df_adn_full[df_adn_full['ID_ADN'] != str(adn_a_gestionar)]
            quedan = df_adn_full[df_adn_full['Ticker'] == ticker]
            if not quedan.empty and not quedan['Es_Default'].any():
                df_adn_full.loc[quedan.index[0], 'Es_Default'] = True
            conn.update(worksheet="ADN_Quant", data=df_adn_full)
            st.cache_data.clear(); st.rerun()
    else:
        st.info("Aún no tienes ningún sistema guardado para esta acción.")

# =====================================================================
# PESTAÑA 5: EL RADAR DIARIO 
# =====================================================================
with tab5:
    st.title("📡 Radar Institucional (El Centro de Mando)")
    st.markdown("Esta herramienta escanea todas tus acciones y detecta cuáles cumplen **cualquiera de tus sistemas guardados** HOY.")
    
    if st.button("🔄 Lanzar Radar Diario de Mercado", type="primary", use_container_width=True):
        if df_adn.empty:
            st.warning("Aún no has guardado el ADN de ninguna acción en el Laboratorio Quant. No hay nada que vigilar.")
        else:
            with st.spinner("Escaneando el multiverso del mercado en directo..."):
                tickers_adn = df_adn['Ticker'].unique().tolist()
                alertas_encontradas = []
                
                for t in tickers_adn:
                    try:
                        adns_del_ticker = df_adn[df_adn['Ticker'] == t]
                        if adns_del_ticker.empty: continue
                        
                        stock_rad = yf.Ticker(t)
                        df_rad = stock_rad.history(period="3mo")
                        if df_rad.empty: continue
                        
                        df_rad['MA55'] = df_rad['Close'].rolling(window=55).mean()
                        df_rad['STD55'] = df_rad['Close'].rolling(window=55).std()
                        df_rad['Z_Score'] = (df_rad['Close'] - df_rad['MA55']) / df_rad['STD55']
                        df_rad['ROC_10'] = df_rad['Close'].pct_change(periods=10) * 100
                        df_rad['Accel'] = df_rad['ROC_10'].diff(periods=5)
                        df_rad['Vol_MA55'] = df_rad['Volume'].rolling(window=55).mean()
                        df_rad['Vol_STD55'] = df_rad['Volume'].rolling(window=55).std()
                        df_rad['Vol_Z_Score'] = (df_rad['Volume'] - df_rad['Vol_MA55']) / df_rad['Vol_STD55']
                        
                        atr_rad = np.max(pd.concat([df_rad['High'] - df_rad['Low'], np.abs(df_rad['High'] - df_rad['Close'].shift()), np.abs(df_rad['Low'] - df_rad['Close'].shift())], axis=1), axis=1).rolling(14).mean().iloc[-1]
                        
                        hoy_z = df_rad['Z_Score'].iloc[-1]
                        hoy_acc = df_rad['Accel'].iloc[-1]
                        hoy_vol = df_rad['Vol_Z_Score'].iloc[-1]
                        precio_hoy = df_rad['Close'].iloc[-1]
                        
                        sistemas_disparados = []
                        for _, sys_adn in adns_del_ticker.iterrows():
                            adn_z = float(sys_adn['Z_Min'])
                            adn_acc = float(sys_adn['Acc_Min'])
                            adn_vol = float(sys_adn['Vol_Min'])
                            
                            c_z = True if adn_z == -99 else (hoy_z >= adn_z)
                            c_a = True if adn_acc == -99 else (hoy_acc >= adn_acc)
                            c_v = True if adn_vol == -99 else (hoy_vol >= adn_vol)
                            
                            if c_z and c_a and c_v:
                                sistemas_disparados.append(f"🔥 Sistema <b>{sys_adn['Horizonte']}</b> (Histórico: +{float(sys_adn['Rendimiento']):.2f}% | WinRate: {float(sys_adn['WinRate']):.1f}%)")
                        
                        if len(sistemas_disparados) > 0:
                            alertas_encontradas.append({
                                "Ticker": t, "Z_Hoy": hoy_z, "A_Hoy": hoy_acc, "V_Hoy": hoy_vol,
                                "Precio": precio_hoy, "ATR": atr_rad, "Sistemas": sistemas_disparados
                            })
                    except: pass
                
                st.markdown("---")
                if len(alertas_encontradas) > 0:
                    st.markdown(f"### 🚨 ¡ALERTA MULTIDIMENSIONAL! {len(alertas_encontradas)} acciones acaban de detonar hoy:")
                    
                    for alerta in alertas_encontradas:
                        t_alert = alerta['Ticker']
                        sistemas_html = "<br>".join([f"<div class='radar-sys-box'>{s}</div>" for s in alerta['Sistemas']])
                        
                        with st.expander(f"🎯 {t_alert} | Vol: {alerta['V_Hoy']:.2f}σ | Accel: {alerta['A_Hoy']:.2f} ➡️ ABRIR CALCULADORA DE DISPARO"):
                            st.markdown(f"### Plan de Vuelo: {t_alert}")
                            st.markdown(f"**ADNs Activados en esta vela:**<br>{sistemas_html}", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            col_calc1, col_calc2 = st.columns(2)
                            with col_calc1:
                                p_compra_rad = st.number_input(f"Precio Compra ({t_alert})", value=float(alerta['Precio']), key=f"buy_rad_{t_alert}")
                                stop_sug_rad = alerta['Precio'] - (2 * alerta['ATR']) if alerta['ATR'] > 0 else alerta['Precio'] * 0.95
                                p_stop_rad = st.number_input(f"Stop Loss ({t_alert})", value=float(stop_sug_rad), key=f"sl_rad_{t_alert}")
                            
                            with col_calc2:
                                r_pct_rad = st.slider(f"Riesgo % ({t_alert})", 0.5, 10.0, 3.3, 0.1, key=f"r_rad_{t_alert}")
                                dist_stop_rad = p_compra_rad - p_stop_rad
                                
                                if dist_stop_rad > 0 and p_compra_rad > 0:
                                    riesgo_eur_rad = CAPITAL * (r_pct_rad / 100.0)
                                    acciones_rad = math.floor(riesgo_eur_rad / dist_stop_rad)
                                    inv_rad = acciones_rad * p_compra_rad
                                    st.success(f"**Posición recomendada:** {acciones_rad} acciones")
                                    st.info(f"**Inversión total:** {inv_rad:,.2f} $")
                                else:
                                    acciones_rad = 0
                                    st.error("⚠️ El Stop Loss debe ser menor al precio de compra.")
                            
                            if st.button(f"🚀 EJECUTAR OPERACIÓN: Enviar {t_alert} a Cartera", key=f"btn_send_{t_alert}", type="primary"):
                                if acciones_rad > 0:
                                    with st.spinner("Enviando a Cartera en Vivo..."):
                                        try:
                                            df_c = conn.read(worksheet="Cartera", ttl=0)
                                            n_pos = {"Ticker": t_alert, "Fecha_Entrada": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Entrada": p_compra_rad, "Num_Acciones": acciones_rad, "Stop_Actual": p_stop_rad, "Fecha_Ruptura_S4": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Ruptura_S4": p_compra_rad, "Fecha_Ruptura_S5": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Ruptura_S5": p_compra_rad}
                                            conn.update(worksheet="Cartera", data=pd.concat([df_c, pd.DataFrame([n_pos])], ignore_index=True))
                                            st.cache_data.clear(); st.success(f"✅ ¡Operación en {t_alert} registrada con éxito! (Pestaña Cartera)")
                                        except Exception as e: st.error(f"Error en base de datos: {e}")
                                else:
                                    st.error("Calcula bien el riesgo antes de disparar.")
                else:
                    st.markdown("""
                    <div class='radar-wait'>
                        <h2>⏳ Día de Pesca (0 Alertas)</h2>
                        <p>Ninguna de las acciones en tu Piscina de ADN cumple las condiciones hoy. Mantén el capital a salvo.</p>
                    </div>
                    """, unsafe_allow_html=True)
