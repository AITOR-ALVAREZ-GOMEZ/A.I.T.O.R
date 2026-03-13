import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 52.0 LAB ABIERTO", layout="wide")

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
else: st.sidebar.warning("⚠️ Sin datos de precio en directo.")

st.sidebar.markdown("---")
st.sidebar.header("Calidad (Libro Blanco)")
if prev_1y > 0 and eps_base > 0:
    e1 = eps_base * (1 + prev_1y); e2 = e1 * (1 + prev_1y); e3 = e2 * (1 + prev_1y)
    st.sidebar.info(f"{A_ACTUAL}: {e1:.2f} $\n\n{A_ACTUAL + 1}: {e2:.2f} $\n\n{A_ACTUAL + 2}: {e3:.2f} $")

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
# SISTEMA DE PESTAÑAS (INCLUYE PESTAÑA 4)
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Escáner Cuántico", "📋 Auditoría Global", "💼 Cartera en Vivo", "🧪 Laboratorio Quant (Abierto)"])

with tab1:
    st.title("Análisis de Entrada: " + ticker)
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
                    if p_merc > ma_val:
                        senal_auto = "Compra"
                        idx_radio = 1
                except: pass
            st.markdown(f"<div style='font-size:0.85rem; color:#86868b; margin-top:5px; text-align:center;'>Media: <b>{ma_val:.2f}</b></div>", unsafe_allow_html=True)
            es = st.radio("Señal", ["Venta", "Compra"], index=idx_radio, key=f"e{i}")
            wr_dec = wr / 100.0
            ev_i = round((wr_dec * rt) - ((1.0 - wr_dec) * 1.0), 2)
            s_elegidos.append(s_val); l_ev.append(ev_i); l_wr.append(wr); l_rt.append(rt); l_es.append(es)
            st.markdown(f"<div style='text-align:center; padding:10px; background:#fff; border-radius:10px; border:1px solid #e5e5ea; margin-top:5px;'><div style='color:#86868b; font-size:0.75rem; font-weight:bold;'>EV {s_val}D</div><div style='font-size:1.4rem; font-weight:800; color:#1d1d1f;'>{ev_i:.2f}</div></div>", unsafe_allow_html=True)

    ev_compra = sum([l_ev[i] for i in range(5) if l_es[i] == "Compra"])
    ev_venta = sum([l_ev[i] for i in range(5) if l_es[i] == "Venta"])
    net_ev = ev_compra - ev_venta 
    ev_tot = round(net_ev + ev_plus, 2) 
    ite = round(((p_buy - p_sl) / p_buy) * 100.0, 2) if p_buy > 0 else 0.0
    penal = 30 if ite > 15 else 0 
    p_estr = sum(10 for e in l_es[1:] if e == "Compra")
    p_sen = 10 if l_es[0] == "Compra" else 0
    idt = l_wr[0] + bono + p_estr + p_sen - penal

    if net_ev >= 1.5: st.markdown("<div class='main-banner banner-green'>✅ LUZ VERDE ESTRUCTURAL: Ventaja Matemática Confirmada. APTO PARA COMPRAR.</div>", unsafe_allow_html=True)
    elif net_ev >= 0: st.markdown("<div class='main-banner banner-yellow'>⚠️ PRECAUCIÓN: Fuerza Neta Débil. Apto solo con POSICIÓN REDUCIDA.</div>", unsafe_allow_html=True)
    else: st.markdown("<div class='main-banner banner-red'>🚨 SISTEMA BLOQUEADO: Esperanza Matemática Negativa. PROHIBIDO COMPRAR.</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏛️ Auditoría Matemática Central")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        h_ev = "<div class='rank-box'>"
        if ev_tot >= 10: h_ev += "<div class='tag-on' style='background:#34c759;'>TIER S</div><div class='tag-off'>TIER A</div><div class='tag-off'>DESCARTE</div>"
        elif ev_tot >= 5: h_ev += "<div class='tag-off'>TIER S</div><div class='tag-on' style='background:#2b8af7;'>TIER A</div><div class='tag-off'>DESCARTE</div>"
        else: h_ev += "<div class='tag-off'>TIER S</div><div class='tag-off'>TIER A</div><div class='tag-on' style='background:#ff3b30;'>DESCARTE</div>"
        h_ev += "</div>"
        net_color = "#16a34a" if net_ev > 0 else "#dc2626"
        breakdown_ev = f"<div class='kpi-breakdown'>• Fuerza Sistemas (Neto): <b style='color:{net_color};'>{net_ev:+.2f}</b><br>• Bonus Calidad: <b style='color:#16a34a;'>+{ev_plus:.2f}</b><br>• Desglose: <span style='color:#16a34a;'>+{ev_compra:.2f} (C)</span> / <span style='color:#dc2626;'>-{ev_venta:.2f} (V)</span></div>"
        st.markdown(f"<div class='apple-kpi-card'><div class='apple-kpi-title'>SCORE EV (Esperanza)</div><div class='apple-kpi-value'>{ev_tot:.2f}</div>{breakdown_ev}{h_ev}</div>", unsafe_allow_html=True)

    with c2:
        h_idt = "<div class='rank-box'>"
        if idt >= 100: h_idt += "<div class='tag-on' style='background:#1d1d1f;'>OBLIGATORIA</div><div class='tag-off'>TACTICA</div><div class='tag-off'>BLOQUEADA</div>"
        elif idt >= 85: h_idt += "<div class='tag-off'>OBLIGATORIA</div><div class='tag-on' style='background:#ff9500;'>TACTICA</div><div class='tag-off'>BLOQUEADA</div>"
        else: h_idt += "<div class='tag-off'>OBLIGATORIA</div><div class='tag-off'>TACTICA</div><div class='tag-on' style='background:#ff3b30;'>BLOQUEADA</div>"
        h_idt += "</div>"
        breakdown_idt = f"<div class='kpi-breakdown'>• WinRate Principal: <b>+{l_wr[0]}</b><br>• Calidad + Sistemas: <b>+{(bono + p_estr + p_sen)}</b><br>• Penalización por Stop: <b style='color:#dc2626;'>-{penal}</b></div>"
        st.markdown(f"<div class='apple-kpi-card'><div class='apple-kpi-title'>PUNTOS IDT (Estructura)</div><div class='apple-kpi-value'>{idt}</div>{breakdown_idt}{h_idt}</div>", unsafe_allow_html=True)

    with c3:
        h_ite = "<div class='rank-box'>"
        if ite <= 5: h_ite += "<div class='tag-on' style='background:#34c759;'>OPTIMO</div><div class='tag-off'>MANEJABLE</div><div class='tag-off'>PELIGROSO</div>"
        elif ite <= 10: h_ite += "<div class='tag-off'>OPTIMO</div><div class='tag-on' style='background:#ff9500;'>MANEJABLE</div><div class='tag-off'>PELIGROSO</div>"
        else: h_ite += "<div class='tag-off'>OPTIMO</div><div class='tag-off'>MANEJABLE</div><div class='tag-on' style='background:#ff3b30;'>PELIGROSO</div>"
        h_ite += "</div>"
        distancia = p_buy - p_sl
        breakdown_ite = f"<div class='kpi-breakdown'>• Precio Compra: <b>{p_buy:.2f} $</b><br>• Stop Loss: <b>{p_sl:.2f} $</b><br>• Distancia de caída: <b>{distancia:.2f} $</b></div>"
        st.markdown(f"<div class='apple-kpi-card'><div class='apple-kpi-title'>RIESGO ITE (Vacío)</div><div class='apple-kpi-value'>{ite}%</div>{breakdown_ite}{h_ite}</div>", unsafe_allow_html=True)

    # =====================================================================
    # MATRIZ TEMPORAL (MÁQUINA DEL TIEMPO)
    # =====================================================================
    st.markdown("---")
    st.subheader("🔮 Matriz Temporal Quant (Backtesting Fijo)")
    
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
                    m = today_naive.month - i
                    y = today_naive.year
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

                fecha_sel_str = st.select_slider("⏳ Toca una fecha exacta para recalcular todo el Oráculo en ese milisegundo:", options=opciones_str, value="🟢 HOY")
                fecha_sel = dict_fechas[fecha_sel_str]
                if fecha_sel_str != "🟢 HOY": st.warning(f"⚠️ **MODO BACKTESTING:** El Oráculo refleja exactamente cómo cerraron los indicadores el **{fecha_sel_str}**.")

                df_corte = df_esc[df_esc.index <= fecha_sel].copy()
                z_in = df_corte['Z_Score'].iloc[-1] if not pd.isna(df_corte['Z_Score'].iloc[-1]) else 0
                acc_in = df_corte['Accel'].iloc[-1] if not pd.isna(df_corte['Accel'].iloc[-1]) else 0
                vol_z_in = df_corte['Vol_Z_Score'].iloc[-1] if not pd.isna(df_corte['Vol_Z_Score'].iloc[-1]) else 0

                df_last_15 = df_corte.tail(15).copy()
                bar_x = [f"{d.day} {meses[d.month]}" for d in df_last_15.index.tz_localize(None)]

                col_eq1, col_eq2, col_eq3 = st.columns(3)
                
                with col_eq1:
                    z_c1 = "font-weight:900; color:#3b82f6;" if z_in < -2.0 else "color:#a1a1aa;"
                    z_c2 = "font-weight:900; color:#16a34a;" if -2.0 <= z_in <= 2.0 else "color:#a1a1aa;"
                    z_c3 = "font-weight:900; color:#ff3b30;" if z_in > 2.0 else "color:#a1a1aa;"
                    st.markdown(f"""<div class="quant-card" style="padding-bottom:5px;">
                        <div class="quant-title">Z-Score (Tensión Precio)</div>
                        <div style='font-size:0.8rem; background:#f8f9fa; padding:8px; border-radius:8px; margin-bottom:10px; border:1px solid #e8eaed;'>
                            <div style='{z_c1}'>• < -2.0 : Sobrevendida (Rebote)</div>
                            <div style='{z_c2}'>• -2.0 a +2.0 : Tensión Normal</div>
                            <div style='{z_c3}'>• > +2.0 : Euforia (Peligro)</div>
                        </div>""", unsafe_allow_html=True)
                    fig_ze = go.Figure(go.Indicator(mode="gauge+number", value=z_in, number=dict(valueformat='.2f', suffix='σ'), gauge=dict(axis=dict(range=[-4, 4]), bar=dict(color="black"), steps=[dict(range=[-4, -2.0], color="#3b82f6"), dict(range=[-2.0, 2.0], color="#e5e5ea"), dict(range=[2.0, 4], color="#ff3b30")])))
                    fig_ze.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_ze, use_container_width=True)
                    bar_c_z = ['#ff3b30' if val > 2.0 else ('#3b82f6' if val < -2.0 else '#a1a1aa') for val in df_last_15['Z_Score']]
                    fig_b_z = go.Figure(data=[go.Bar(x=bar_x, y=df_last_15['Z_Score'], marker_color=bar_c_z)])
                    fig_b_z.add_hline(y=2.0, line_dash="dash", line_color="#ff3b30")
                    fig_b_z.update_layout(height=120, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showticklabels=True, tickangle=-45, tickfont=dict(size=9)), yaxis=dict(title=""), plot_bgcolor="white")
                    st.plotly_chart(fig_b_z, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_eq2:
                    a_c1 = "font-weight:900; color:#ff3b30;" if acc_in <= 0 else "color:#a1a1aa;"
                    a_c2 = "font-weight:900; color:#16a34a;" if acc_in > 0 else "color:#a1a1aa;"
                    st.markdown(f"""<div class="quant-card" style="padding-bottom:5px;">
                        <div class="quant-title">Aceleración (Momentum)</div>
                        <div style='font-size:0.8rem; background:#f8f9fa; padding:8px; border-radius:8px; margin-bottom:10px; border:1px solid #e8eaed;'>
                            <div style='{a_c1}'>• ≤ 0 : Perdiendo Gas (Frena)</div>
                            <div style='{a_c2}'>• > 0 : Entrando Dinero (Acelera)</div>
                            <div style='color:transparent;'>_</div>
                        </div>""", unsafe_allow_html=True)
                    fig_ae = go.Figure(go.Indicator(mode="gauge+number", value=acc_in, number=dict(valueformat='.2f'), gauge=dict(axis=dict(range=[-10, 10]), bar=dict(color="purple"), steps=[dict(range=[-10, 0], color="#ffcdd2"), dict(range=[0, 10], color="#c8e6c9")])))
                    fig_ae.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_ae, use_container_width=True)
                    bar_c_a = ['#34c759' if val > 0 else '#ff3b30' for val in df_last_15['Accel']]
                    fig_b_a = go.Figure(data=[go.Bar(x=bar_x, y=df_last_15['Accel'], marker_color=bar_c_a)])
                    fig_b_a.add_hline(y=0, line_dash="solid", line_color="#1d1d1f")
                    fig_b_a.update_layout(height=120, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showticklabels=True, tickangle=-45, tickfont=dict(size=9)), yaxis=dict(title=""), plot_bgcolor="white")
                    st.plotly_chart(fig_b_a, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_eq3:
                    v_c1 = "font-weight:900; color:#ff3b30;" if vol_z_in < 0 else "color:#a1a1aa;"
                    v_c2 = "font-weight:900; color:#3b82f6;" if 0 <= vol_z_in <= 1.5 else "color:#a1a1aa;"
                    v_c3 = "font-weight:900; color:#34c759;" if vol_z_in > 1.5 else "color:#a1a1aa;"
                    st.markdown(f"""<div class="quant-card" style="padding-bottom:5px;">
                        <div class="quant-title">Huella Institucional</div>
                        <div style='font-size:0.8rem; background:#f8f9fa; padding:8px; border-radius:8px; margin-bottom:10px; border:1px solid #e8eaed;'>
                            <div style='{v_c1}'>• < 0 : Minoristas (Ruido)</div>
                            <div style='{v_c2}'>• 0 a +1.5 : Volumen Sano / Oculto</div>
                            <div style='{v_c3}'>• > +1.5 : Inyección Ballenas</div>
                        </div>""", unsafe_allow_html=True)
                    fig_ve = go.Figure(go.Indicator(mode="gauge+number", value=vol_z_in, number=dict(valueformat='.2f', suffix='σ'), gauge=dict(axis=dict(range=[-2, 4]), bar=dict(color="black"), steps=[dict(range=[-2, 1.5], color="#e5e5ea"), dict(range=[1.5, 4], color="#34c759")])))
                    fig_ve.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_ve, use_container_width=True)
                    bar_c_v = ['#34c759' if val >= 1.5 else '#e5e5ea' for val in df_last_15['Vol_Z_Score']]
                    fig_b_v = go.Figure(data=[go.Bar(x=bar_x, y=df_last_15['Vol_Z_Score'], marker_color=bar_c_v)])
                    fig_b_v.add_hline(y=1.5, line_dash="dash", line_color="#34c759")
                    fig_b_v.update_layout(height=120, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showticklabels=True, tickangle=-45, tickfont=dict(size=9)), yaxis=dict(title=""), plot_bgcolor="white")
                    st.plotly_chart(fig_b_v, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
        except: pass

# --- PESTAÑAS 2 Y 3 (AUDITORÍA Y CARTERA) ---
with tab2: st.info("Auditoría Activa")
with tab3: st.info("Cartera Activa")

# =====================================================================
# PESTAÑA 4: LABORATORIO QUANT ABIERTO (DIARIO FORENSE) - ¡VERSIÓN 52!
# =====================================================================
with tab4:
    st.title("🧪 Laboratorio Quant (Paramétrico)")
    st.markdown(f"Configura tus propias reglas para buscar el Santo Grial en **{ticker}** y extrae el listado exacto de fechas para verificarlas en tu gráfico.")
    
    st.markdown("### ⚙️ Parámetros del Backtest (Últimos 5 años)")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        bt_z_precio = st.number_input("1. Z-Score Precio Mínimo (>)", value=1.0, step=0.1, help="Ej: > 1.0 significa que la acción ya está tensa hacia arriba.")
    with col_p2:
        bt_accel = st.number_input("2. Aceleración Mínima (>)", value=0.0, step=0.5, help="Ej: > 0 significa que la tendencia gana velocidad.")
    with col_p3:
        bt_z_vol = st.number_input("3. Huella Volumen Mínima (>)", value=2.0, step=0.1, help="Ej: > 2.0 es una inyección de dinero brutal.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    bt_breakout = st.checkbox("🔥 4. Filtro de Acción del Precio (Price Action): El precio debe superar el máximo del día anterior.", value=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button(f"🚀 Ejecutar Simulación y Extraer Fechas en {ticker}", type="primary"):
        with st.spinner(f"Analizando 1.200 días de historia de {ticker}..."):
            try:
                stock_bt = yf.Ticker(ticker)
                df_bt = stock_bt.history(period="5y")
                
                if df_bt.empty or len(df_bt) < 100:
                    st.error("No hay suficientes datos históricos para este Ticker.")
                else:
                    df_bt['MA55'] = df_bt['Close'].rolling(window=55).mean()
                    df_bt['Vol_MA55'] = df_bt['Volume'].rolling(window=55).mean()
                    df_bt['Vol_STD55'] = df_bt['Volume'].rolling(window=55).std()
                    df_bt['Vol_Z_Score'] = (df_bt['Volume'] - df_bt['Vol_MA55']) / df_bt['Vol_STD55']
                    df_bt['Z_Score'] = (df_bt['Close'] - df_bt['MA55']) / df_bt['Close'].rolling(window=55).std()
                    df_bt['ROC_10'] = df_bt['Close'].pct_change(periods=10) * 100
                    df_bt['Accel'] = df_bt['ROC_10'].diff(periods=5)
                    
                    # LOGICA DEL GATILLO CON PARÁMETROS DEL USUARIO
                    df_bt['Cond_Z'] = df_bt['Z_Score'] > bt_z_precio
                    df_bt['Cond_Acc'] = df_bt['Accel'] > bt_accel
                    df_bt['Cond_Vol'] = df_bt['Vol_Z_Score'] > bt_z_vol
                    if bt_breakout:
                        df_bt['Cond_Break'] = df_bt['High'] > df_bt['High'].shift(1)
                    else:
                        df_bt['Cond_Break'] = True
                        
                    df_bt['Gatillo'] = np.where(df_bt['Cond_Z'] & df_bt['Cond_Acc'] & df_bt['Cond_Vol'] & df_bt['Cond_Break'], 1, 0)
                    
                    señales = []
                    fechas_registro = []
                    ultimo_dia = None
                    
                    for date, row in df_bt[df_bt['Gatillo'] == 1].iterrows():
                        if ultimo_dia is None or (date - ultimo_dia).days > 10:
                            idx = df_bt.index.get_loc(date)
                            if idx + 20 < len(df_bt):
                                p_entrada = df_bt['Close'].iloc[idx]
                                p_salida = df_bt['Close'].iloc[idx + 20]
                                retorno = ((p_salida - p_entrada) / p_entrada) * 100
                                señales.append(retorno)
                                
                                # Guardar los datos para la tabla forense
                                result_str = "✅ ÉXITO" if retorno > 0 else "❌ FALLO"
                                fechas_registro.append({
                                    "Fecha Exacta": date.strftime("%Y-%m-%d"),
                                    "Z-Score Precio": round(row['Z_Score'], 2),
                                    "Aceleración": round(row['Accel'], 2),
                                    "Huella Vol": round(row['Vol_Z_Score'], 2),
                                    "Precio Compra": f"{p_entrada:.2f} $",
                                    "Rendimiento (20D)": f"{retorno:+.2f} %",
                                    "Resultado": result_str
                                })
                            ultimo_dia = date

                    total_señales = len(señales)
                    if total_señales > 0:
                        positivas = len([s for s in señales if s > 0])
                        win_rate = (positivas / total_señales) * 100
                        avg_return = sum(señales) / total_señales
                        
                        st.markdown("---")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Muestras Encontradas", f"{total_señales} veces")
                        c2.metric("Win Rate (Fiabilidad)", f"{win_rate:.1f} %")
                        c3.metric("Rendimiento Medio (20 días)", f"{avg_return:+.2f} %")
                        
                        st.markdown("### 🧠 Conclusión de la Máquina:")
                        if win_rate > 60 and avg_return > 3: st.success(f"**VENTAJA ESTADÍSTICA CONFIRMADA.** Este set de reglas es altamente efectivo en {ticker}.")
                        elif win_rate > 50 and avg_return > 0: st.info(f"**SISTEMA RENTABLE, PERO NO INFALIBLE.** Ganarías dinero a la larga, pero prepárate para usar Stops porque falla casi la mitad de las veces.")
                        else: st.error(f"**ATENCIÓN: TRAMPA ALCISTA.** Cuidado. Con estos parámetros exactos en {ticker}, el mercado suele girarse a la contra poco después.")
                        
                        # EL DIARIO FORENSE (NUEVO)
                        st.markdown("---")
                        st.markdown("### 📅 Diario Forense: Analiza estas fechas en tu gráfico")
                        st.markdown("Copia estas fechas y ve a TradingView o ProRealTime. Mira exactamente qué aspecto tenía la vela ese día.")
                        df_display = pd.DataFrame(fechas_registro)
                        st.dataframe(df_display, use_container_width=True, hide_index=True)
                        
                    else:
                        st.warning("Con estos parámetros tan restrictivos, no se ha encontrado ni una sola señal en los últimos 5 años. Prueba a relajar las reglas (ej: bajar la Huella de 2.0 a 1.5).")
            except Exception as e: st.error(f"Error procesando los datos: {e}")
