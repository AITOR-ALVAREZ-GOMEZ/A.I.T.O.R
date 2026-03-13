import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 55.0 MEMORIA GENETICA", layout="wide")

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
    .dna-badge { display: inline-block; background: linear-gradient(90deg, #9333ea, #ec4899); color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(236, 72, 153, 0.4);}
    
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

# NUEVA BASE DE DATOS: ADN DE OPTIMIZACIÓN
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

# --- LECTURA DEL ADN GENÉTICO DEL TICKER ---
opt_z, opt_acc, opt_vol = 1.0, 0.0, 1.5 # Valores por defecto
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

# --- PESTAÑA 1: ESCÁNER INTELIGENTE (MUTADO POR ADN) ---
with tab1:
    st.title("Análisis de Entrada: " + ticker)
    
    if tiene_adn:
        st.markdown("<div class='dna-badge'>🧬 ADN CUANTITATIVO CARGADO</div>", unsafe_allow_html=True)
        st.caption(f"El Escáner ha mutado para {ticker}. Limites calibrados: Volumen > {opt_vol}σ | Aceleración > {opt_acc} | Tensión > {opt_z}σ")
    
    s_elegidos, l_ev, l_wr, l_rt, l_es = [], [], [], [], []
    cols = st.columns(5)
    d_defs, w_defs, r_defs = [1, 3, 8, 14, 21], [50]*5, [2.0]*5
    
    if ticker != "" and not df_datos.empty and "Ticker" in df_datos.columns:
        df_filtro = df_datos[df_datos["Ticker"] == ticker]
        if len(df_filtro) > 0:
            fila = df_filtro.iloc[-1]
            try:
                for idx in range(5):
                    val_s = int(fila[f"S{idx+1}_Dias"])
                    if val_s in DIAS: d_defs[idx] = val_s
                    w_defs[idx] = int(fila[f"W{idx+1}"])
                    r_defs[idx] = float(fila[f"R{idx+1}"])
            except: pass

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

    st.markdown("---")
    
    # MATRIZ TEMPORAL ADAPTADA AL ADN
    st.subheader("🔮 Matriz Temporal Quant (Calibrada con ADN)")
    z_in, acc_in, vol_z_in = 0.0, 0.0, 0.0
    if ticker != "":
        try:
            if not df_global.empty:
                df_esc = df_global.copy()
                df_esc['MA55'] = df_esc['Close'].rolling(window=55).mean()
                df_esc['STD55'] = df_esc['Close'].rolling(window=55).std()
                df_esc['Z_Score'] = (df_esc['Close'] - df_esc['MA55']) / df_esc['STD55']
                df_esc['ROC_10'] = df_esc['Close'].pct_change(periods=10) * 100
                df_esc['Accel'] = df_esc['ROC_10'].diff(periods=5)
                df_esc['Vol_MA55'] = df_esc['Volume'].rolling(window=55).mean()
                df_esc['Vol_STD55'] = df_esc['Volume'].rolling(window=55).std()
                df_esc['Vol_Z_Score'] = (df_esc['Volume'] - df_esc['Vol_MA55']) / df_esc['Vol_STD55']
                
                today_naive = df_esc.index[-1].replace(tzinfo=None)
                target_dates_naive = []
                for i in range(12): 
                    m = today_naive.month - i; y = today_naive.year
                    while m <= 0: m += 12; y -= 1
                    target_dates_naive.append(datetime.datetime(y, m, 1))
                    target_dates_naive.append(datetime.datetime(y, m, 15))
                    
                fechas_slider = []
                for td in target_dates_naive:
                    if td <= today_naive:
                        deltas = abs(df_esc.index.tz_localize(None) - td)
                        fechas_slider.append(df_esc.index[deltas.argmin()])
                        
                for d in df_esc.index[-15:]: fechas_slider.append(d)
                fechas_slider = sorted(list(set(fechas_slider)))
                meses = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}
                opciones_str = []
                dict_fechas = {}
                for d in fechas_slider:
                    d_naive = d.replace(tzinfo=None)
                    if d == df_esc.index[-1]: s = "🟢 HOY"
                    else: s = f"{d_naive.day} {meses[d_naive.month]} {d_naive.year}"
                    opciones_str.append(s)
                    dict_fechas[s] = d

                fecha_sel_str = st.select_slider("⏳ Toca una fecha para ver el Oráculo ese día:", options=opciones_str, value="🟢 HOY")
                fecha_sel = dict_fechas[fecha_sel_str]
                
                df_corte = df_esc[df_esc.index <= fecha_sel].copy()
                z_in = df_corte['Z_Score'].iloc[-1] if not pd.isna(df_corte['Z_Score'].iloc[-1]) else 0
                acc_in = df_corte['Accel'].iloc[-1] if not pd.isna(df_corte['Accel'].iloc[-1]) else 0
                vol_z_in = df_corte['Vol_Z_Score'].iloc[-1] if not pd.isna(df_corte['Vol_Z_Score'].iloc[-1]) else 0

                df_last_15 = df_corte.tail(15).copy()
                bar_x = [f"{d.day} {meses[d.month]}" for d in df_last_15.index.tz_localize(None)]

                col_eq1, col_eq2, col_eq3 = st.columns(3)
                
                # ORÁCULO MUTADO POR ADN
                with col_eq1:
                    z_c1 = "font-weight:900; color:#3b82f6;" if z_in < -2.0 else "color:#a1a1aa;"
                    z_c2 = "font-weight:900; color:#16a34a;" if -2.0 <= z_in <= opt_z else "color:#a1a1aa;"
                    z_c3 = "font-weight:900; color:#ff3b30;" if z_in > opt_z else "color:#a1a1aa;"
                    st.markdown(f"""<div class="quant-card" style="padding-bottom:5px;">
                        <div class="quant-title">Tensión (Setup > {opt_z})</div>
                        <div style='font-size:0.8rem; background:#f8f9fa; padding:8px; border-radius:8px; margin-bottom:10px; border:1px solid #e8eaed;'>
                            <div style='{z_c1}'>• < -2.0 : Sobrevendida</div>
                            <div style='{z_c2}'>• -2.0 a {opt_z} : Normal</div>
                            <div style='{z_c3}'>• > {opt_z} : Disparador Activo</div>
                        </div>""", unsafe_allow_html=True)
                    fig_ze = go.Figure(go.Indicator(mode="gauge+number", value=z_in, gauge=dict(axis=dict(range=[-4, 4]), bar=dict(color="black"), steps=[dict(range=[-4, -2.0], color="#3b82f6"), dict(range=[-2.0, opt_z], color="#e5e5ea"), dict(range=[opt_z, 4], color="#ff3b30")])))
                    fig_ze.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_ze, use_container_width=True)
                    
                    bar_c_z = ['#ff3b30' if val > opt_z else ('#3b82f6' if val < -2.0 else '#a1a1aa') for val in df_last_15['Z_Score']]
                    fig_b_z = go.Figure(data=[go.Bar(x=bar_x, y=df_last_15['Z_Score'], marker_color=bar_c_z)])
                    fig_b_z.add_hline(y=opt_z, line_dash="dash", line_color="#ff3b30")
                    fig_b_z.update_layout(height=120, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showticklabels=False), yaxis=dict(title=""), plot_bgcolor="white")
                    st.plotly_chart(fig_b_z, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_eq2:
                    a_c1 = "font-weight:900; color:#ff3b30;" if acc_in <= opt_acc else "color:#a1a1aa;"
                    a_c2 = "font-weight:900; color:#16a34a;" if acc_in > opt_acc else "color:#a1a1aa;"
                    st.markdown(f"""<div class="quant-card" style="padding-bottom:5px;">
                        <div class="quant-title">Momentum (Setup > {opt_acc})</div>
                        <div style='font-size:0.8rem; background:#f8f9fa; padding:8px; border-radius:8px; margin-bottom:10px; border:1px solid #e8eaed;'>
                            <div style='{a_c1}'>• ≤ {opt_acc} : Sin Gatillo</div>
                            <div style='{a_c2}'>• > {opt_acc} : Aceleración Activa</div>
                            <div style='color:transparent;'>_</div>
                        </div>""", unsafe_allow_html=True)
                    fig_ae = go.Figure(go.Indicator(mode="gauge+number", value=acc_in, gauge=dict(axis=dict(range=[-10, 10]), bar=dict(color="purple"), steps=[dict(range=[-10, opt_acc], color="#ffcdd2"), dict(range=[opt_acc, 10], color="#c8e6c9")])))
                    fig_ae.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_ae, use_container_width=True)
                    
                    bar_c_a = ['#34c759' if val > opt_acc else '#ff3b30' for val in df_last_15['Accel']]
                    fig_b_a = go.Figure(data=[go.Bar(x=bar_x, y=df_last_15['Accel'], marker_color=bar_c_a)])
                    fig_b_a.add_hline(y=opt_acc, line_dash="solid", line_color="#1d1d1f")
                    fig_b_a.update_layout(height=120, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showticklabels=False), yaxis=dict(title=""), plot_bgcolor="white")
                    st.plotly_chart(fig_b_a, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_eq3:
                    v_c1 = "font-weight:900; color:#ff3b30;" if vol_z_in < 0 else "color:#a1a1aa;"
                    v_c2 = "font-weight:900; color:#3b82f6;" if 0 <= vol_z_in <= opt_vol else "color:#a1a1aa;"
                    v_c3 = "font-weight:900; color:#34c759;" if vol_z_in > opt_vol else "color:#a1a1aa;"
                    st.markdown(f"""<div class="quant-card" style="padding-bottom:5px;">
                        <div class="quant-title">Volumen (Setup > {opt_vol})</div>
                        <div style='font-size:0.8rem; background:#f8f9fa; padding:8px; border-radius:8px; margin-bottom:10px; border:1px solid #e8eaed;'>
                            <div style='{v_c1}'>• < 0 : Ruido Minorista</div>
                            <div style='{v_c2}'>• 0 a {opt_vol} : Volumen Sano</div>
                            <div style='{v_c3}'>• > {opt_vol} : Gatillo Institucional</div>
                        </div>""", unsafe_allow_html=True)
                    fig_ve = go.Figure(go.Indicator(mode="gauge+number", value=vol_z_in, gauge=dict(axis=dict(range=[-2, 4]), bar=dict(color="black"), steps=[dict(range=[-2, opt_vol], color="#e5e5ea"), dict(range=[opt_vol, 4], color="#34c759")])))
                    fig_ve.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_ve, use_container_width=True)
                    
                    bar_c_v = ['#34c759' if val >= opt_vol else '#e5e5ea' for val in df_last_15['Vol_Z_Score']]
                    fig_b_v = go.Figure(data=[go.Bar(x=bar_x, y=df_last_15['Vol_Z_Score'], marker_color=bar_c_v)])
                    fig_b_v.add_hline(y=opt_vol, line_dash="dash", line_color="#34c759")
                    fig_b_v.update_layout(height=120, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showticklabels=False), yaxis=dict(title=""), plot_bgcolor="white")
                    st.plotly_chart(fig_b_v, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
        except: pass

    # DIAGNOSTICOS TEXTUALES MUTADOS
    st.markdown("---")
    st.subheader("📋 Auditoría Clínica de Entrada")
    if z_in > opt_z: txt_z, col_z = f"GATILLO ACTIVO. El precio supera el límite de {opt_z} establecido en tu ADN.", "tdah-green"
    else: txt_z, col_z = "Tensión insuficiente. No cumple tu ADN.", "tdah-yellow"
    st.markdown(f"<div class='tdah-box {col_z}'><div class='tdah-title'>🪢 Diagnóstico Precio:</div><div class='tdah-text'>{txt_z}</div></div>", unsafe_allow_html=True)

    if vol_z_in >= opt_vol: txt_v, col_v = f"GATILLO ACTIVO. Volumen por encima de tu límite de {opt_vol}.", "tdah-green"
    else: txt_v, col_v = "Volumen insuficiente para tu setup.", "tdah-yellow"
    st.markdown(f"<div class='tdah-box {col_v}'><div class='tdah-title'>🐘 Diagnóstico Volumen:</div><div class='tdah-text'>{txt_v}</div></div>", unsafe_allow_html=True)

    # BOTONES
    st.markdown("---")
    st.subheader("⚙️ Panel de Ejecución Cuantitativa")
    col_btn_save, col_btn_buy = st.columns(2)
    with col_btn_save:
        if st.button("💾 Solo Guardar Escaneo (Añadir a Radar)", use_container_width=True):
            st.success("Guardado.")
    with col_btn_buy:
        if st.button("🚀 COMPRAR AHORA: Enviar a Cartera en Vivo", use_container_width=True):
            st.success("Comprado.")

with tab2: st.info("Auditoría Activa")
with tab3: st.info("Cartera Activa")

# =====================================================================
# PESTAÑA 4: LABORATORIO MODULAR CON GUARDADO DE ADN (VERSIÓN 55)
# =====================================================================
with tab4:
    st.title("🧪 Laboratorio Quant y Edición de ADN")
    st.markdown(f"Investiga **{ticker}** y guarda la mejor configuración para que A.I.T.O.R. la use por defecto.")
    
    st.markdown("### 🎛️ 1. Panel Quant (Enciende/Apaga Módulos)")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_z = st.checkbox("🟢 Usar Tensión Precio (Z-Score)", value=True)
        bt_z_precio = st.number_input("Z-Score Mínimo (>)", value=float(opt_z), step=0.1, disabled=not use_z)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_p2:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_acc = st.checkbox("🟢 Usar Aceleración (Momentum)", value=True)
        bt_accel = st.number_input("Aceleración Mínima (>)", value=float(opt_acc), step=0.5, disabled=not use_acc)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_p3:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_vol = st.checkbox("🟢 Usar Huella Volumen", value=True)
        bt_z_vol = st.number_input("Huella Volumen Mínima (>)", value=float(opt_vol), step=0.1, disabled=not use_vol)
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
    
    if st.button(f"🚀 Ejecutar Simulación Modular en {ticker}", type="primary"):
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
                                    "10 Días": dict_rets_display["10 Días"],
                                    "20 Días": dict_rets_display["20 Días"],
                                    "30 Días": dict_rets_display["30 Días"]
                                }
                                fechas_registro_display.append(fila_diario)
                                ultimo_dia_señal = date 

                    total_señales = len(fechas_registro_display)
                    
                    if total_señales > 0:
                        st.markdown("---")
                        st.markdown(f"### 📊 Resultado de la Simulación ({total_señales} entradas válidas)")
                        col_m2, col_m4, col_m5 = st.columns(3)
                        avg_10 = np.mean(datos_estadistica[10])
                        avg_20 = np.mean(datos_estadistica[20])
                        avg_30 = np.mean(datos_estadistica[30])
                        col_m2.metric("Media a 10 Días", f"{avg_10:+.2f} %")
                        col_m4.metric("Media a 20 Días", f"{avg_20:+.2f} %")
                        col_m5.metric("Media a 30 Días", f"{avg_30:+.2f} %")
                        
                        # EL BOTÓN DE GUARDADO GENÉTICO
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("💾 GUARDAR ESTOS PARÁMETROS COMO 'ADN' PARA ESTA ACCIÓN", type="secondary", use_container_width=True):
                            try:
                                df_adn_actual = conn.read(worksheet="ADN_Quant", ttl=0)
                                if df_adn_actual.empty: df_adn_actual = pd.DataFrame(columns=["Ticker", "Z_Min", "Acc_Min", "Vol_Min", "Rendimiento"])
                                
                                nuevo_adn = {"Ticker": ticker, "Z_Min": bt_z_precio if use_z else -99, "Acc_Min": bt_accel if use_acc else -99, "Vol_Min": bt_z_vol if use_vol else -99, "Rendimiento": avg_20}
                                df_adn_nuevo = pd.concat([df_adn_actual, pd.DataFrame([nuevo_adn])], ignore_index=True).drop_duplicates("Ticker", keep="last")
                                conn.update(worksheet="ADN_Quant", data=df_adn_nuevo)
                                st.cache_data.clear()
                                st.success("✅ ADN Modificado. A partir de ahora, el Escáner principal evaluará esta acción con estos límites personalizados.")
                            except Exception as e:
                                st.error(f"Error al guardar ADN: {e}")

                        st.markdown("---")
                        df_display = pd.DataFrame(fechas_registro_display)
                        def color_retorno(val):
                            if isinstance(val, str) and '%' in val:
                                num = float(val.replace('%', '').replace('+', ''))
                                return 'color: #16a34a; font-weight: bold' if num > 0 else 'color: #dc2626'
                            return ''
                        st.dataframe(df_display.style.map(color_retorno, subset=["10 Días", "20 Días", "30 Días"]), use_container_width=True, hide_index=True)
                    else:
                        st.warning("No hay resultados. Tus reglas son demasiado estrictas.")
                        
            except Exception as e: st.error(f"Error procesando los datos: {e}")
