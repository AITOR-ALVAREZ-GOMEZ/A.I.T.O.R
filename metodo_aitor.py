import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 54.0 LAB MODULAR", layout="wide")

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
    
    @keyframes flash-red { 0% { background-color: #ff3b30; color: white; } 50% { background-color: #ffe5e5; color: #ff3b30; } 100% { background-color: #ff3b30; color: white; } }
    @keyframes pulse-green { 0% { background-color: #34c759; color: white; } 50% { background-color: #e5fbee; color: #188038; } 100% { background-color: #34c759; color: white; } }
    @keyframes pulse-yellow { 0% { background-color: #ffcc00; color: #1d1d1f; } 50% { background-color: #fff9e6; color: #b38f00; } 100% { background-color: #ffcc00; color: #1d1d1f; } }
    
    .main-banner { padding: 16px; border-radius: 12px; text-align: center; font-weight: 800; font-size: 1.25rem; margin-top: 15px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .banner-red { animation: flash-red 1.5s infinite; border: 2px solid #ff3b30; }
    .banner-green { animation: pulse-green 2s infinite; border: 2px solid #34c759; }
    .banner-yellow { animation: pulse-yellow 2s infinite; border: 2px solid #ffcc00; }
    
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
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

# =====================================================================
# BUSCADOR LATERAL 
# =====================================================================
st.sidebar.header("Buscador de Activos")
opciones_bd = df_datos['Ticker'].dropna().unique().tolist() if not df_datos.empty else []
ticker_manual = st.sidebar.text_input("Nuevo Ticker (Ej: MU):", "").strip().upper()
ticker_lista = st.sidebar.selectbox("O cargar de Auditoría:", [""] + opciones_bd)
ticker = ticker_manual if ticker_manual != "" else ticker_lista
if ticker == "": ticker = "MU"

nom_emp, p_merc, prev_1y, eps_base, atr_val = "Buscando...", 0.0, 0.0, 0.0, 0.0
df_global = pd.DataFrame()
beta_val = 1.0 

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
            try:
                spy = yf.Ticker("SPY").history(period="1y")
                ret_stock = df_global['Close'].pct_change().dropna()
                ret_spy = spy['Close'].pct_change().dropna()
                aligned_rets = pd.concat([ret_stock, ret_spy], axis=1, join='inner')
                aligned_rets.columns = ['Stock', 'Market']
                cov = aligned_rets.cov().iloc[0, 1]
                var = aligned_rets['Market'].var()
                beta_val = cov / var if var != 0 else 1.0
            except: pass
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
if prev_1y > 0 and eps_base > 0:
    st.sidebar.info(f"{A_ACTUAL}: {eps_base * (1 + prev_1y):.2f} $")

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
# PESTAÑAS PRINCIPALES
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Escáner Cuántico", "📋 Auditoría Global", "💼 Cartera en Vivo", "🧪 Laboratorio Modular"])

with tab1:
    st.title("Análisis de Entrada: " + ticker)
    s_elegidos, l_ev, l_wr, l_rt, l_es = [], [], [], [], []
    cols = st.columns(5)
    d_defs, w_defs, r_defs = [1, 3, 8, 14, 21], [50]*5, [2.0]*5
    
    for i in range(5):
        with cols[i]:
            st.markdown(f"**{d_defs[i]} D**")
            idx_d = DIAS.index(d_defs[i])
            s_val = st.selectbox("S", DIAS, index=idx_d, key=f"d{i}", label_visibility="collapsed")
            wr = st.number_input("WR %", 0, 100, w_defs[i], key=f"w{i}")
            rt = st.number_input("R/R", 0.0, 50.0, r_defs[i], key=f"r{i}")
            ma_val = 0.0
            senal_auto = "Venta"
            idx_radio = 0
            if not df_global.empty:
                try:
                    ma_val = df_global['Close'].rolling(window=s_val).mean().iloc[-1]
                    if p_merc > ma_val: idx_radio = 1
                except: pass
            st.markdown(f"<div style='font-size:0.85rem; color:#86868b; margin-top:5px; text-align:center;'>Media: <b>{ma_val:.2f}</b></div>", unsafe_allow_html=True)
            es = st.radio("Señal", ["Venta", "Compra"], index=idx_radio, key=f"e{i}")
            ev_i = round(((wr / 100.0) * rt) - ((1.0 - (wr / 100.0)) * 1.0), 2)
            s_elegidos.append(s_val); l_ev.append(ev_i); l_wr.append(wr); l_rt.append(rt); l_es.append(es)
            st.markdown(f"<div style='text-align:center; padding:10px; background:#fff; border-radius:10px; border:1px solid #e5e5ea; margin-top:5px;'><div style='color:#86868b; font-size:0.75rem; font-weight:bold;'>EV {s_val}D</div><div style='font-size:1.4rem; font-weight:800; color:#1d1d1f;'>{ev_i:.2f}</div></div>", unsafe_allow_html=True)

    ev_compra = sum([l_ev[i] for i in range(5) if l_es[i] == "Compra"])
    ev_venta = sum([l_ev[i] for i in range(5) if l_es[i] == "Venta"])
    net_ev = ev_compra - ev_venta 
    ev_tot = round(net_ev + ev_plus, 2) 

    if net_ev >= 1.5: st.markdown("<div class='main-banner banner-green'>✅ LUZ VERDE ESTRUCTURAL: Ventaja Matemática Confirmada. APTO PARA COMPRAR.</div>", unsafe_allow_html=True)
    elif net_ev >= 0: st.markdown("<div class='main-banner banner-yellow'>⚠️ PRECAUCIÓN: Fuerza Neta Débil. Apto solo con POSICIÓN REDUCIDA.</div>", unsafe_allow_html=True)
    else: st.markdown("<div class='main-banner banner-red'>🚨 SISTEMA BLOQUEADO: Esperanza Matemática Negativa. PROHIBIDO COMPRAR.</div>", unsafe_allow_html=True)
    
    st.info("Pestaña 1 Reducida visualmente en código para dar prioridad a la Pestaña 4.")

with tab2: st.info("Auditoría Activa")
with tab3: st.info("Cartera Activa")

# =====================================================================
# PESTAÑA 4: LABORATORIO MODULAR (VERSIÓN 54)
# =====================================================================
with tab4:
    st.title("🧪 Laboratorio Modular (Backtester Abierto)")
    st.markdown(f"Configura, enciende o apaga indicadores para descubrir el patrón perfecto en **{ticker}**.")
    
    # BLOQUE 1: INDICADORES QUANT
    st.markdown("### 🎛️ 1. Panel Quant (Enciende/Apaga Módulos)")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_z = st.checkbox("🟢 Usar Tensión Precio (Z-Score)", value=True)
        bt_z_precio = st.number_input("Z-Score Mínimo (>)", value=1.0, step=0.1, disabled=not use_z)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_p2:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_acc = st.checkbox("🟢 Usar Aceleración (Momentum)", value=True)
        bt_accel = st.number_input("Aceleración Mínima (>)", value=0.0, step=0.5, disabled=not use_acc)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_p3:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_vol = st.checkbox("🟢 Usar Huella Volumen", value=True)
        bt_z_vol = st.number_input("Huella Volumen Mínima (>)", value=2.0, step=0.1, disabled=not use_vol)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # BLOQUE 2: MEDIAS MÓVILES
    st.markdown("### 📈 2. Filtro de Tendencia (Medias Móviles)")
    lista_mas = [2, 3, 5, 8, 13, 21, 34, 55]
    mas_seleccionadas = st.multiselect(
        "El precio de cierre debe estar estrictamente POR ENCIMA de estas medias (Puedes dejarlo en blanco):", 
        lista_mas, default=[]
    )
    
    # BLOQUE 3: ACCIÓN DEL PRECIO
    st.markdown("### 🎯 3. Confirmación del Precio (Price Action)")
    tipo_filtro = st.radio("¿Qué debe hacer la vela para activar tu compra?", [
        "Ninguno (Entrar el mismo día que saltan los indicadores, sin mirar la vela).",
        "Fuerza Inmediata: El día de los indicadores debe superar el máximo del día anterior.",
        "Continuación (Minervini): Entrar el día SIGUIENTE solo si supera el máximo del día de los indicadores."
    ], index=2)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # BOTÓN DE EJECUCIÓN
    if st.button(f"🚀 Ejecutar Simulación Modular en {ticker}", type="primary"):
        with st.spinner(f"Analizando 5 años de {ticker} con tus reglas exactas..."):
            try:
                stock_bt = yf.Ticker(ticker)
                df_bt = stock_bt.history(period="5y")
                
                if df_bt.empty or len(df_bt) < 100:
                    st.error("No hay suficientes datos históricos.")
                else:
                    # 1. Calcular Datos Base
                    df_bt['MA55'] = df_bt['Close'].rolling(window=55).mean()
                    df_bt['Vol_MA55'] = df_bt['Volume'].rolling(window=55).mean()
                    df_bt['Vol_STD55'] = df_bt['Volume'].rolling(window=55).std()
                    df_bt['Vol_Z_Score'] = (df_bt['Volume'] - df_bt['Vol_MA55']) / df_bt['Vol_STD55']
                    df_bt['Z_Score'] = (df_bt['Close'] - df_bt['MA55']) / df_bt['Close'].rolling(window=55).std()
                    df_bt['ROC_10'] = df_bt['Close'].pct_change(periods=10) * 100
                    df_bt['Accel'] = df_bt['ROC_10'].diff(periods=5)
                    
                    # Calcular todas las medias solicitadas
                    for ma in lista_mas:
                        df_bt[f'MA_{ma}'] = df_bt['Close'].rolling(window=ma).mean()
                    
                    # 2. Aplicar la Lógica Modular (Gatillos)
                    cond_z = (df_bt['Z_Score'] > bt_z_precio) if use_z else pd.Series(True, index=df_bt.index)
                    cond_acc = (df_bt['Accel'] > bt_accel) if use_acc else pd.Series(True, index=df_bt.index)
                    cond_vol = (df_bt['Vol_Z_Score'] > bt_z_vol) if use_vol else pd.Series(True, index=df_bt.index)
                    
                    cond_mas = pd.Series(True, index=df_bt.index)
                    for ma in mas_seleccionadas:
                        cond_mas = cond_mas & (df_bt['Close'] > df_bt[f'MA_{ma}'])
                        
                    # El día "Candidato" cumple todo lo que el usuario ha encendido
                    df_bt['Candidato'] = cond_z & cond_acc & cond_vol & cond_mas
                    
                    horizontes = [5, 10, 15, 20, 30]
                    fechas_registro_display = []
                    datos_estadistica = {5: [], 10: [], 15: [], 20: [], 30: []}
                    ultimo_dia_señal = None
                    
                    # 3. Escanear el histórico 
                    # Saltamos los primeros 55 días para que las MAs y Z-Scores estén limpios
                    for i in range(55, len(df_bt) - max(horizontes) - 1):
                        row = df_bt.iloc[i]
                        date = df_bt.index[i]
                        
                        if row['Candidato']:
                            # Cooldown para no saturar operaciones seguidas
                            if ultimo_dia_señal is not None and (date - ultimo_dia_señal).days <= 10:
                                continue 
                                
                            es_valida = False
                            idx_entrada = i
                            p_entrada = row['Close']
                            fecha_texto_entrada = date.strftime("%Y-%m-%d")
                            
                            # 4. APLICAR EL FILTRO DEL PRECIO
                            if "Ninguno" in tipo_filtro:
                                es_valida = True
                            elif "Fuerza Inmediata" in tipo_filtro:
                                if row['High'] > df_bt.iloc[i-1]['High']:
                                    es_valida = True
                            elif "Continuación" in tipo_filtro:
                                row_next = df_bt.iloc[i+1]
                                if row_next['High'] > row['High']:
                                    es_valida = True
                                    idx_entrada = i + 1 
                                    p_entrada = row_next['Close']
                                    fecha_texto_entrada = f"{df_bt.index[i+1].strftime('%Y-%m-%d')} (T+1)"

                            # 5. SI SE CONFIRMA, MEDIR EL FUTURO
                            if es_valida:
                                dict_rets_display = {}
                                for h in horizontes:
                                    p_salida = df_bt['Close'].iloc[idx_entrada + h]
                                    ret = ((p_salida - p_entrada) / p_entrada) * 100
                                    datos_estadistica[h].append(ret)
                                    dict_rets_display[f"{h} Días"] = f"{ret:+.2f}%"
                                    
                                fila_diario = {
                                    "Señal Indicadores": date.strftime("%Y-%m-%d"),
                                    "Día Compra Efectiva": fecha_texto_entrada,
                                    "Precio": f"{p_entrada:.2f} $",
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
                        st.markdown("---")
                        st.markdown("### 📊 La Matriz de Rendimiento Medio (Curva del Trade)")
                        st.markdown(f"Se encontraron **{total_señales} entradas válidas** en los últimos 5 años con tus reglas personalizadas.")
                        
                        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
                        avg_5 = np.mean(datos_estadistica[5])
                        avg_10 = np.mean(datos_estadistica[10])
                        avg_15 = np.mean(datos_estadistica[15])
                        avg_20 = np.mean(datos_estadistica[20])
                        avg_30 = np.mean(datos_estadistica[30])
                        
                        col_m1.metric("Media a 5 Días", f"{avg_5:+.2f} %")
                        col_m2.metric("Media a 10 Días", f"{avg_10:+.2f} %")
                        col_m3.metric("Media a 15 Días", f"{avg_15:+.2f} %")
                        col_m4.metric("Media a 20 Días", f"{avg_20:+.2f} %")
                        col_m5.metric("Media a 30 Días", f"{avg_30:+.2f} %")
                        
                        st.markdown("---")
                        st.markdown("### 📅 Diario Forense: Autopsia Vela a Vela")
                        df_display = pd.DataFrame(fechas_registro_display)
                        
                        def color_retorno(val):
                            if isinstance(val, str) and '%' in val:
                                num = float(val.replace('%', '').replace('+', ''))
                                return 'color: #16a34a; font-weight: bold' if num > 0 else 'color: #dc2626'
                            return ''
                        
                        st.dataframe(df_display.style.map(color_retorno, subset=["5 Días", "10 Días", "15 Días", "20 Días", "30 Días"]), use_container_width=True, hide_index=True)
                        
                    else:
                        st.warning("Con estos parámetros, filtros de MAs y acción del precio, no se ha encontrado NINGUNA señal en los últimos 5 años. Estás siendo demasiado exigente para esta acción.")
                        
            except Exception as e: st.error(f"Error procesando los datos: {e}")
