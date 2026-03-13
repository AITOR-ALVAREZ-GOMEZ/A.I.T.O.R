import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 45.0 NETWORK FIX", layout="wide")

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
    .quant-title { font-size: 1.1rem; font-weight: 700; color: #1d1d1f; margin-bottom: 5px; }
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

# FIX NETWORK: Restauramos caché de 60s para no saturar a Google. Limpiaremos caché al guardar.
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
beta_val = 1.0 # Default

if ticker != "":
    stock = yf.Ticker(ticker)
    try:
        df_global = stock.history(period="1y")
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
st.sidebar.caption("💡 Riesgo ideal para Alta Convicción (3 acciones): **3.3%**")

p_buy = st.sidebar.number_input("Precio Compra", value=float(p_merc), key=f"buy_{ticker}")
stop_sugerido_auto = p_buy - (2 * atr_val) if atr_val > 0 else p_buy * 0.95
if atr_val > 0: st.sidebar.markdown(f"<div style='font-size: 0.8rem; color: #166534; font-weight: 600; margin-bottom: 5px;'>🤖 Auto-Stop Calculado (2x ATR)</div>", unsafe_allow_html=True)
p_sl = st.sidebar.number_input("Stop Loss", value=float(stop_sugerido_auto), key=f"sl_{ticker}")

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

# =====================================================================
# SISTEMA DE PESTAÑAS PRINCIPALES
# =====================================================================
tab1, tab2, tab3 = st.tabs(["📊 Escáner Cuántico", "📋 Auditoría Global", "💼 Cartera en Vivo"])

# --- PESTAÑA 1: ESCÁNER INTELIGENTE ---
with tab1:
    st.title("Análisis de Entrada: " + ticker)
    s_elegidos, l_ev, l_wr, l_rt, l_es = [], [], [], [], []
    cols = st.columns(5)
    
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

    pct_riesgo = r_pct / 100.0
    p_max = CAPITAL * pct_riesgo
    dif_p = p_buy - p_sl
    n_tit = int(p_max / dif_p) if dif_p > 0 else 0
    inv_t = n_tit * p_buy

    st.markdown("---")
    st.subheader(f"Ejecución Recomendada (Capital: {CAPITAL:,.0f} EUR)")
    c4, c5, c6 = st.columns(3)
    c4.metric("Riesgo Maximo", str(int(p_max)) + " EUR")
    c5.metric("Acciones", str(int(n_tit)) + " titulos")
    c6.metric("Posicion Total", str(int(inv_t)) + " EUR")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🎯 Controlador de Riesgo / Gestión de Capital")
    col_radar_esc, col_txt_esc = st.columns([2, 1])
    with col_radar_esc:
        if p_buy > 0 and p_sl > 0 and p_buy > p_sl:
            rango_min_esc = p_sl * 0.90
            rango_max_esc = p_buy * 1.05
            lim_peligro_esc = p_sl + (p_buy - p_sl) * 0.30
            fig_radar_esc = go.Figure(go.Indicator(
                mode="gauge+number", value=p_buy, title=dict(text="Distancia: Precio Compra vs Stop", font=dict(size=14)), number=dict(valueformat=".2f"),
                gauge=dict(axis=dict(range=[rango_min_esc, rango_max_esc]), bar=dict(color="#1d1d1f"), steps=[dict(range=[rango_min_esc, p_sl], color="#ff3b30"), dict(range=[p_sl, lim_peligro_esc], color="#ffcc00"), dict(range=[lim_peligro_esc, rango_max_esc], color="#34c759")], threshold=dict(line=dict(color="black", width=5), thickness=0.75, value=p_sl))
            ))
            fig_radar_esc.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_radar_esc, use_container_width=True)
    with col_txt_esc:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if ite <= 5: st.success(f"**🟢 Riesgo Óptimo ({ite}%):** El Stop está cerca. Tienes margen para usar tu 100% de posición asignada.")
        elif ite <= 10: st.warning(f"**🟡 Stop Espacioso ({ite}%):** El Stop exige más espacio (por volatilidad ATR o estiramiento). Reduce tus acciones.")
        else: st.error(f"**🔴 Riesgo Estructural Alto ({ite}%):** Tienes que darle muchísimo oxígeno al precio para que no te barra el ruido. Usa un tamaño de posición muy reducido.")

    st.markdown("---")
    st.subheader("🔮 Oráculo Quant & Arbitraje Institucional")
    z_in, acc_in, vol_z_in = 0.0, 0.0, 0.0
    if ticker != "":
        try:
            if not df_global.empty:
                df_esc = df_global.copy()
                df_esc['MA55'] = df_esc['Close'].rolling(window=55).mean()
                df_esc['STD55'] = df_esc['Close'].rolling(window=55).std()
                df_esc['Z_Score'] = (df_esc['Close'] - df_esc['MA55']) / df_esc['STD55']
                z_in = df_esc['Z_Score'].iloc[-1] if not pd.isna(df_esc['Z_Score'].iloc[-1]) else 0
                df_esc['ROC_10'] = df_esc['Close'].pct_change(periods=10) * 100
                df_esc['Accel'] = df_esc['ROC_10'].diff(periods=5)
                acc_in = df_esc['Accel'].iloc[-1] if not pd.isna(df_esc['Accel'].iloc[-1]) else 0
                df_esc['Vol_MA55'] = df_esc['Volume'].rolling(window=55).mean()
                df_esc['Vol_STD55'] = df_esc['Volume'].rolling(window=55).std()
                vol_z_in = ((df_esc['Volume'] - df_esc['Vol_MA55']) / df_esc['Vol_STD55']).iloc[-1] if not pd.isna(((df_esc['Volume'] - df_esc['Vol_MA55']) / df_esc['Vol_STD55']).iloc[-1]) else 0

                col_eq1, col_eq2, col_eq3 = st.columns(3)
                with col_eq1:
                    st.markdown("""<div class="quant-card"><div class="quant-title">Z-Score (Desviación)</div><div class="quant-desc">Tensión de la goma. > +2.5 indica euforia extrema y riesgo inminente de reversión.</div>""", unsafe_allow_html=True)
                    fig_ze = go.Figure(go.Indicator(mode="gauge+number", value=z_in, number=dict(valueformat='.2f', suffix=' Sigmas'), gauge=dict(axis=dict(range=[-4, 4]), bar=dict(color="black"), steps=[dict(range=[-4, 0.5], color="lightgray"), dict(range=[0.5, 2.0], color="lightgreen"), dict(range=[2.0, 4], color="red")])))
                    fig_ze.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_ze, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                with col_eq2:
                    st.markdown("""<div class="quant-card"><div class="quant-title">Aceleración (Momentum)</div><div class="quant-desc">La velocidad de la tendencia. Debe ser positiva (>0) para asegurar que sigue entrando dinero.</div>""", unsafe_allow_html=True)
                    fig_ae = go.Figure(go.Indicator(mode="gauge+number", value=acc_in, number=dict(valueformat='.2f'), gauge=dict(axis=dict(range=[-10, 10]), bar=dict(color="purple"), steps=[dict(range=[-10, 0], color="lightpink"), dict(range=[0, 10], color="lightgreen")])))
                    fig_ae.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_ae, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                with col_eq3:
                    st.markdown("""<div class="quant-card"><div class="quant-title">Huella Institucional</div><div class="quant-desc">Anomalía de Volumen. > +1.5 significa que los grandes fondos están comprando.</div>""", unsafe_allow_html=True)
                    fig_ve = go.Figure(go.Indicator(mode="gauge+number", value=vol_z_in, number=dict(valueformat='.2f', suffix=' Sigmas'), gauge=dict(axis=dict(range=[-2, 4]), bar=dict(color="blue"), steps=[dict(range=[-2, 1.0], color="lightgray"), dict(range=[1.0, 1.5], color="lightblue"), dict(range=[1.5, 4], color="royalblue")])))
                    fig_ve.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_ve, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
        except: pass

    st.markdown("---")
    st.subheader("📋 Auditoría Clínica de Entrada")
    
    if ev_tot >= 10: txt_ev, col_ev = f"<b>{ev_tot:.2f} Puntos</b>. Sistema estadísticamente muy robusto. Tienes las probabilidades a tu favor.", "tdah-green"
    elif ev_tot >= 5: txt_ev, col_ev = f"<b>{ev_tot:.2f} Puntos</b>. Fiabilidad estándar. Sistema apto para operar.", "tdah-blue"
    else: txt_ev, col_ev = f"<b>{ev_tot:.2f} Puntos</b>. Fiabilidad matemática DÉBIL. No se recomienda operar.", "tdah-red"
    st.markdown(f"<div class='tdah-box {col_ev}'><div class='tdah-title'>📊 Esperanza Matemática (Fiabilidad del Sistema):</div><div class='tdah-text'>{txt_ev}</div></div>", unsafe_allow_html=True)

    if net_ev > 1.5: col_f = "tdah-green"
    elif net_ev > 0: col_f = "tdah-yellow"
    else: col_f = "tdah-red"
    st.markdown(f"<div class='tdah-box {col_f}'><div class='tdah-title'>⚖️ Fuerza Estructural Neta:</div><div class='tdah-text'>El empuje real del precio descontando sistemas en contra es de <b>{net_ev:+.2f}</b>.</div></div>", unsafe_allow_html=True)

    if z_in > 2.5: txt_z, col_z = "PELIGRO. Precio disparado por euforia. Entrar hoy es comprar el techo.", "tdah-red"
    elif z_in > 2.0: txt_z, col_z = "Goma muy tensa. Si entras, reduce tu posición a la mitad.", "tdah-yellow"
    elif z_in < -1.0: txt_z, col_z = "Goma estirada hacia abajo. Podría haber un rebote pronto.", "tdah-blue"
    else: txt_z, col_z = "Tensión NORMAL. El precio está cerca de su media. Zona segura para comprar.", "tdah-green"
    st.markdown(f"<div class='tdah-box {col_z}'><div class='tdah-title'>🪢 Tensión del Precio (Z-Score):</div><div class='tdah-text'>{txt_z}</div></div>", unsafe_allow_html=True)

    if vol_z_in > 1.5: txt_v, col_v = "EXCELENTE. Hay una huella gigante de dinero institucional apoyando este movimiento hoy.", "tdah-green"
    elif vol_z_in > 0.5: txt_v, col_v = "Volumen sano. Participación normal del mercado.", "tdah-blue"
    else: txt_v, col_v = "Pobre participación. El movimiento de hoy no tiene respaldo de los grandes fondos.", "tdah-yellow"
    st.markdown(f"<div class='tdah-box {col_v}'><div class='tdah-title'>🐘 Intervención Institucional (Volumen):</div><div class='tdah-text'>{txt_v}</div></div>", unsafe_allow_html=True)

    if beta_val > 1.5: txt_b, col_b = f"PELIGRO ({beta_val:.2f}). Acción altamente radiactiva y pegada al mercado. Si el S&P500 estornuda, esta acción se hunde.", "tdah-red"
    elif beta_val < 0.8: txt_b, col_b = f"IDEAL ({beta_val:.2f}). Actúa como escudo. Su correlación con el mercado es baja, te protege en las caídas.", "tdah-green"
    else: txt_b, col_b = f"NORMAL ({beta_val:.2f}). Se mueve a la par que la economía general.", "tdah-blue"
    st.markdown(f"<div class='tdah-box {col_b}'><div class='tdah-title'>🛡️ Correlación Beta (Riesgo de Mercado):</div><div class='tdah-text'>{txt_b}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if net_ev < 0: ver_txt, ver_col = "❌ PROHIBIDO COMPRAR. Es una trampa bajista (Fuerza Neta negativa).", "tdah-red"
    elif z_in > 2.5: ver_txt, ver_col = "❌ ESPERAR. La tendencia es buena pero la goma está demasiado tensa. Espera a un retroceso.", "tdah-red"
    elif net_ev >= 1.5 and z_in <= 2.0 and acc_in > 0: ver_txt, ver_col = "✅ LUZ VERDE TOTAL. Estructura fuerte, precio sin tensión y con el acelerador pisado. Adelante.", "tdah-green"
    elif acc_in <= 0: ver_txt, ver_col = "⚠️ PRECAUCIÓN. La estructura es alcista pero el Momentum está en rojo (Pérdida de gas). Entra si quieres, pero reduce tu capital.", "tdah-yellow"
    else: ver_txt, ver_col = "⚠️ PRECAUCIÓN. La operación es viable, pero hay dudas en la estructura o el precio. Opera solo con media posición.", "tdah-yellow"
    st.markdown(f"<div class='tdah-box {ver_col}' style='border-width: 4px;'><div class='tdah-title'>🎯 VEREDICTO FINAL DE LA MÁQUINA:</div><div class='tdah-text' style='font-size:1.1rem; font-weight:600;'>{ver_txt}</div></div>", unsafe_allow_html=True)

    # =====================================================================
    # BOTONES DE ACCIÓN 
    # =====================================================================
    st.markdown("---")
    st.subheader("⚙️ Panel de Ejecución Cuantitativa")
    col_btn_save, col_btn_buy = st.columns(2)
    with col_btn_save:
        if st.button("💾 Solo Guardar Escaneo (Añadir a Radar)", use_container_width=True):
            with st.spinner("📡 Sincronizando con Base de Datos..."):
                try:
                    v_t = "REVISION REQUERIDA"
                    if idt >= 100: v_t = "COMPRA OBLIGATORIA"
                    elif idt >= 85: v_t = "COMPRA TACTICA"
                    elif ev_tot < 5: v_t = "OPERACION NO VIABLE"
                    
                    d_sav = {"Ticker": ticker, "Tier": v_t, "EV_Total": ev_tot, "IDT_Puntos": idt, "ITE_Porc": ite, "Veredicto": v_t, "Acciones": n_tit, "Inversion": inv_t}
                    for j in range(5): d_sav[f"S{j+1}_Dias"] = s_elegidos[j]; d_sav[f"W{j+1}"] = l_wr[j]; d_sav[f"R{j+1}"] = l_rt[j]
                    df_fresh = conn.read(worksheet="Sheet1", ttl=60)
                    if df_fresh.empty: df_fresh = pd.DataFrame(columns=COL_DB)
                    df_upd = pd.concat([df_fresh, pd.DataFrame([d_sav])], ignore_index=True).drop_duplicates("Ticker", keep="last")
                    conn.update(worksheet="Sheet1", data=df_upd)
                    st.cache_data.clear() # SMART WIPER
                    st.toast("✅ Escaneo guardado correctamente en tu Auditoría.", icon="💾")
                except Exception as e: st.error(f"Error al guardar: {e}")

    with col_btn_buy:
        if st.button("🚀 COMPRAR AHORA: Enviar a Cartera en Vivo", use_container_width=True):
            with st.spinner("📡 Ejecutando operación y guardando..."):
                try:
                    v_t = "COMPRADO"
                    d_sav = {"Ticker": ticker, "Tier": v_t, "EV_Total": ev_tot, "IDT_Puntos": idt, "ITE_Porc": ite, "Veredicto": v_t, "Acciones": n_tit, "Inversion": inv_t}
                    for j in range(5): d_sav[f"S{j+1}_Dias"] = s_elegidos[j]; d_sav[f"W{j+1}"] = l_wr[j]; d_sav[f"R{j+1}"] = l_rt[j]
                    df_fresh = conn.read(worksheet="Sheet1", ttl=60)
                    if df_fresh.empty: df_fresh = pd.DataFrame(columns=COL_DB)
                    df_upd = pd.concat([df_fresh, pd.DataFrame([d_sav])], ignore_index=True).drop_duplicates("Ticker", keep="last")
                    conn.update(worksheet="Sheet1", data=df_upd)
                    
                    df_c = conn.read(worksheet="Cartera", ttl=60)
                    n_pos = {"Ticker": ticker, "Fecha_Entrada": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Entrada": p_buy, "Num_Acciones": n_tit, "Stop_Actual": p_sl, "Fecha_Ruptura_S4": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Ruptura_S4": p_buy, "Fecha_Ruptura_S5": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Ruptura_S5": p_buy}
                    conn.update(worksheet="Cartera", data=pd.concat([df_c, pd.DataFrame([n_pos])], ignore_index=True))
                    st.cache_data.clear() # SMART WIPER
                    st.toast(f"🎉 ¡OPERACIÓN REGISTRADA! {int(n_tit)} acciones de {ticker} a tu Cartera en Vivo.", icon="🚀")
                except Exception as e: st.error(f"Error al enviar a cartera: {e}")

# --- PESTAÑA 2: AUDITORÍA GLOBAL (EL CENTRO DE MANDO) ---
with tab2: 
    st.markdown("### 🗂️ Centro de Mando (Auditoría Global)")
    if not df_datos.empty:
        df_display = df_datos[['Ticker', 'Veredicto', 'EV_Total', 'IDT_Puntos', 'ITE_Porc']].copy()
        df_display['EV_Total'] = pd.to_numeric(df_display['EV_Total'], errors='coerce').fillna(0)
        df_display['IDT_Puntos'] = pd.to_numeric(df_display['IDT_Puntos'], errors='coerce').fillna(0)
        df_display['ITE_Porc'] = pd.to_numeric(df_display['ITE_Porc'], errors='coerce').fillna(0)
        df_display['Score_Global'] = (df_display['IDT_Puntos'] / 140) * 100
        df_display['Score_Global'] = df_display['Score_Global'].clip(upper=100, lower=0)
        df_display = df_display[['Ticker', 'Veredicto', 'Score_Global', 'EV_Total', 'IDT_Puntos', 'ITE_Porc']]
        
        st.dataframe(
            df_display.sort_values("Score_Global", ascending=False),
            column_config={
                "Ticker": st.column_config.TextColumn("Activo 📈", width="small"),
                "Veredicto": st.column_config.TextColumn("Estado 🚦", width="medium"),
                "Score_Global": st.column_config.ProgressColumn("Salud Global 🧬", format="%d/100", min_value=0, max_value=100),
                "EV_Total": st.column_config.NumberColumn("Fuerza EV", format="%.2f"),
                "IDT_Puntos": st.column_config.NumberColumn("Puntos IDT", format="%d pts"),
                "ITE_Porc": st.column_config.NumberColumn("Riesgo ITE", format="%.2f %%")
            }, hide_index=True, use_container_width=True
        )

# --- PESTAÑA 3: CARTERA EN VIVO ---
with tab3:
    st.markdown("### Gestión Quántica de Operaciones")
    tab_vivas, tab_add, tab_historial = st.tabs(["🟢 Posiciones Vivas", "➕ Añadir a Cartera", "📚 Historial"])
    with tab_vivas:
        try:
            df_cartera = conn.read(worksheet="Cartera", ttl=60).dropna(how="all")
            if df_cartera.empty: st.warning("Tu cartera está vacía.")
            else:
                ticker_sel = st.selectbox("Selecciona Posición Abierta:", df_cartera['Ticker'].tolist())
                datos_ticker = df_cartera[df_cartera['Ticker'] == ticker_sel].iloc[0]
                fecha_in = pd.to_datetime(datos_ticker['Fecha_Entrada']).date()
                precio_in = float(datos_ticker['Precio_Entrada'])
                acciones = float(datos_ticker['Num_Acciones'])
                stop_actual = float(datos_ticker['Stop_Actual'])
                
                with st.spinner(f"Analizando data científica de {ticker_sel}..."):
                    stock_cartera = yf.Ticker(ticker_sel)
                    hist_largo = stock_cartera.history(start=fecha_in - datetime.timedelta(days=365), end=datetime.date.today() + datetime.timedelta(days=1))
                    if hist_largo.empty: hist_largo = stock_cartera.history(period="2y")
                    df_q = hist_largo.copy()
                    precio_vivo = df_q['Close'].iloc[-1]
                    
                    s1_d = int(df_datos[df_datos['Ticker'] == ticker_sel].iloc[-1]['S1_Dias']) if not df_datos.empty and ticker_sel in df_datos['Ticker'].values else 1
                    s2_d = int(df_datos[df_datos['Ticker'] == ticker_sel].iloc[-1]['S2_Dias']) if not df_datos.empty and ticker_sel in df_datos['Ticker'].values else 3
                    s4_d = int(df_datos[df_datos['Ticker'] == ticker_sel].iloc[-1]['S4_Dias']) if not df_datos.empty and ticker_sel in df_datos['Ticker'].values else 34
                    s5_d = int(df_datos[df_datos['Ticker'] == ticker_sel].iloc[-1]['S5_Dias']) if not df_datos.empty and ticker_sel in df_datos['Ticker'].values else 55
                    media_s1 = df_q['Close'].rolling(window=s1_d, min_periods=1).mean().iloc[-1]
                    media_s2 = df_q['Close'].rolling(window=s2_d, min_periods=1).mean().iloc[-1]
                    media_s4 = df_q['Close'].rolling(window=s4_d, min_periods=1).mean().iloc[-1]
                    media_s5 = df_q['Close'].rolling(window=s5_d, min_periods=1).mean().iloc[-1]
                    
                    df_q['MA55'] = df_q['Close'].rolling(window=55, min_periods=1).mean()
                    df_q['STD55'] = df_q['Close'].rolling(window=55, min_periods=1).std()
                    z_actual = ((df_q['Close'] - df_q['MA55']) / df_q['STD55']).iloc[-1] if not pd.isna(((df_q['Close'] - df_q['MA55']) / df_q['STD55']).iloc[-1]) else 0
                    def hurst_approx(p):
                        try:
                            lags = range(2, 20); tau = [np.sqrt(np.std(np.subtract(p[lag:], p[:-lag]))) for lag in lags]; poly = np.polyfit(np.log(lags), np.log(tau), 1)
                            return poly[0] * 2.0
                        except: return 0.5
                    hurst_val = hurst_approx(df_q['Close'].dropna().values[-252:])
                    df_q['ROC_10'] = df_q['Close'].pct_change(periods=10) * 100
                    df_q['Accel'] = df_q['ROC_10'].diff(periods=5)
                    accel_actual = df_q['Accel'].iloc[-1] if not pd.isna(df_q['Accel'].iloc[-1]) else 0
                    df_q['CumMax'] = df_q['Close'].cummax()
                    df_q['Drawdown'] = (df_q['Close'] - df_q['CumMax']) / df_q['CumMax'] * 100
                    dd_min_recent = df_q['Drawdown'].tail(150).min()
                    if pd.isna(dd_min_recent) or dd_min_recent == 0: dd_min_recent = -5.0
                    
                beneficio_eur = (precio_vivo - precio_in) * acciones
                beneficio_pct = ((precio_vivo - precio_in) / precio_in) * 100
                dias_pos = (datetime.date.today() - fecha_in).days
                if dias_pos <= 0: dias_pos = 1
                color_borde = '#34c759' if beneficio_pct >= 0 else '#ff3b30'
                html_kpis = f'<div class="apple-kpi-container"><div class="apple-kpi-card" style="border-left: 5px solid {color_borde};"><div class="led-box"><div class="{"led-green" if beneficio_pct>=0 else "led-red"}"></div><div class="apple-kpi-title" style="margin:0;">Rentabilidad Real</div></div><div class="apple-kpi-value">{beneficio_pct:+.2f}%</div><div class="apple-kpi-sub {"sub-green" if beneficio_pct>=0 else "sub-red"}">{beneficio_eur:+.2f} Netos</div></div><div class="apple-kpi-card"><div class="apple-kpi-title">Precio Mercado ({ticker_sel})</div><div class="apple-kpi-value">{precio_vivo:.2f}</div><div class="apple-kpi-sub sub-gray">Entrada: {precio_in:.2f}</div></div><div class="apple-kpi-card"><div class="apple-kpi-title">Tiempo en Tendencia</div><div class="apple-kpi-value">{dias_pos} Días</div><div class="apple-kpi-sub sub-gray">Desde {fecha_in.strftime("%d/%m/%Y")}</div></div></div>'
                st.markdown(html_kpis, unsafe_allow_html=True)

                st.markdown("### 🧠 Análisis Cuantitativo (Datos de Mantenimiento)")
                col_q1, col_q2 = st.columns(2)
                with col_q1:
                    st.markdown("""<div class="quant-card"><div class="quant-title">1. Z-Score (Desviación)</div><div class="quant-desc">Mide la tensión. Valores > +2.5 indican riesgo de reversión. Si llega a rojo, ciñe el Stop.</div>""", unsafe_allow_html=True)
                    fig_z = go.Figure(go.Indicator(mode="gauge+number", value=z_actual, number=dict(valueformat='.2f', suffix=' Sigmas'), gauge=dict(axis=dict(range=[-4, 4]), bar=dict(color="black"), steps=[dict(range=[-4, -2], color="lightpink"), dict(range=[-2, 2], color="lightgreen"), dict(range=[2, 2.5], color="orange"), dict(range=[2.5, 4], color="red")])))
                    fig_z.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_z, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown(f"""<div class="quant-card"><div class="quant-title">3. Aceleración Pura</div><div class="quant-desc">Mide la fuerza. Si cae a negativo, la tendencia pierde gas. Actual: {accel_actual:.2f}</div>""", unsafe_allow_html=True)
                    fig_acc = go.Figure(go.Scatter(x=df_q.index[-60:], y=df_q['Accel'].tail(60), mode='lines', fill='tozeroy', line_color='purple'))
                    fig_acc.update_yaxes(autorange=True)
                    fig_acc.update_layout(height=140, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False, title="Fecha"))
                    st.plotly_chart(fig_acc, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_q2:
                    st.markdown("""<div class="quant-card"><div class="quant-title">2. Exponente de Hurst</div><div class="quant-desc">Mide el ruido. Si es < 0.50 el precio dará bandazos. Usa Stops lejanos o te barrerán.</div>""", unsafe_allow_html=True)
                    fig_h = go.Figure(go.Indicator(mode="gauge+number", value=hurst_val, number=dict(valueformat='.2f'), gauge=dict(axis=dict(range=[0, 1]), bar=dict(color="darkblue"), steps=[dict(range=[0, 0.45], color="lightgray"), dict(range=[0.45, 0.55], color="yellow"), dict(range=[0.55, 1], color="lightgreen")])))
                    fig_h.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_h, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown(f"""<div class="quant-card"><div class="quant-title">4. Perfil Drawdown</div><div class="quant-desc">En los últimos meses, {ticker_sel} ha hecho caídas del {dd_min_recent:.1f}% de forma normal.</div>""", unsafe_allow_html=True)
                    fig_dd = go.Figure(go.Scatter(x=df_q.index[-150:], y=df_q['Drawdown'].tail(150), mode='lines', fill='tozeroy', line_color='red'))
                    fig_dd.update_layout(height=140, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False, title="Fecha"), yaxis=dict(range=[dd_min_recent*1.1, 0])) 
                    st.plotly_chart(fig_dd, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader(f"📋 Diagnóstico Clínico de Mantenimiento ({ticker_sel})")

                if z_actual > 2.5: txt_z_out, col_z_out = f"Tensión EXTREMA. Hay una burbuja a corto plazo. Obligatorio ceñir el Stop al sistema S2 ({media_s2:.2f}).", "tdah-red"
                elif z_actual > 2.0: txt_z_out, col_z_out = f"Tensión Alta. El precio ha corrido mucho. Atento para subir el Stop pronto.", "tdah-yellow"
                else: txt_z_out, col_z_out = "Tensión Normal. El precio respira sano. Mantén tu Stop estructural sin miedo.", "tdah-green"
                st.markdown(f"<div class='tdah-box {col_z_out}'><div class='tdah-title'>🪢 Z-Score (Tensión):</div><div class='tdah-text'>{txt_z_out}</div></div>", unsafe_allow_html=True)

                if hurst_val < 0.45: txt_h_out, col_h_out = f"Modo RUIDO. El precio va a dar bandazos. Usa un Stop ALEJADO (S4 o S5) o te echará una mecha falsa.", "tdah-yellow"
                else: txt_h_out, col_h_out = f"Modo TENDENCIA. Movimiento limpio. Puedes usar un Stop MÁS CEÑIDO con seguridad.", "tdah-green"
                st.markdown(f"<div class='tdah-box {col_h_out}'><div class='tdah-title'>🌊 Hurst (Régimen):</div><div class='tdah-text'>{txt_h_out}</div></div>", unsafe_allow_html=True)

                if accel_actual > 5: txt_a_out, col_a_out = "Clímax Comprador. Euforia pura detectada. Prepara la salida.", "tdah-red"
                elif accel_actual > 0: txt_a_out, col_a_out = "Velocidad constante. La tendencia empuja a tu favor.", "tdah-green"
                else: txt_a_out, col_a_out = "Pérdida de gas. El dinero institucional ha dejado de presionar por ahora.", "tdah-yellow"
                st.markdown(f"<div class='tdah-box {col_a_out}'><div class='tdah-title'>🏎️ Aceleración (Momentum):</div><div class='tdah-text'>{txt_a_out}</div></div>", unsafe_allow_html=True)

                st.markdown("---")
                stop_roto = precio_vivo < stop_actual
                if stop_roto: st.error(f"🚨 **¡STOP ROTO! ({stop_actual:.2f})** El precio ha cruzado tu umbral. Vende matemáticamente.")
                elif z_actual > 2.5 or (z_actual > 2.0 and accel_actual > 5.0): st.warning(f"🚀 **RECOMENDACIÓN:** Sube el Stop al sistema S2 ({media_s2:.2f}).")
                elif hurst_val < 0.45: st.warning(f"⚠️ **RECOMENDACIÓN:** Mantén el Stop lejos, en S5 ({media_s5:.2f}).")
                else: st.success(f"🛡️ **RECOMENDACIÓN:** Usa tu Stop en S4 ({media_s4:.2f}) o S5 ({media_s5:.2f}).")

                col_term, col_vacia = st.columns([2, 1])
                with col_term:
                    rango_min = stop_actual * 0.90 
                    rango_max = max(precio_vivo * 1.05, stop_actual * 1.10) 
                    limite_naranja = stop_actual * 1.03 
                    fig_riesgo = go.Figure(go.Indicator(mode="gauge+number", value=precio_vivo, title=dict(text=f"Radar: Precio Actual vs Tu Stop Guardado ({stop_actual:.2f})", font=dict(size=14)), number=dict(valueformat=".2f"), gauge=dict(axis=dict(range=[rango_min, rango_max]), bar=dict(color="#1d1d1f"), steps=[dict(range=[rango_min, stop_actual], color="#ff3b30"), dict(range=[stop_actual, limite_naranja], color="#ffcc00"), dict(range=[limite_naranja, rango_max], color="#34c759")], threshold=dict(line=dict(color="black", width=5), thickness=0.75, value=stop_actual))))
                    fig_riesgo.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_riesgo, use_container_width=True)
                
                st.markdown("---")
                st.subheader("💾 Guardar Ajuste de Stop Loss (Trailing Stop)")
                st.info(f"Tu Stop Actual guardado en la base de datos es: **{stop_actual:.2f}**")
                with st.form("form_update_stop"):
                    c_u1, c_u2 = st.columns([1, 2])
                    with c_u1:
                        nuevo_stop = st.number_input("Fijar Nuevo Stop Loss", value=float(stop_actual))
                    with c_u2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        submit_update = st.form_submit_button("Actualizar Stop en Base de Datos")
                        
                    if submit_update:
                        with st.spinner("Actualizando..."):
                            df_c_update = conn.read(worksheet="Cartera", ttl=60)
                            idx_to_update = df_c_update[df_c_update['Ticker'] == ticker_sel].index
                            if not idx_to_update.empty:
                                df_c_update.loc[idx_to_update[-1], 'Stop_Actual'] = nuevo_stop
                                conn.update(worksheet="Cartera", data=df_c_update)
                                st.cache_data.clear() # SMART WIPER
                                st.toast(f"✅ ¡Hecho! El Stop de {ticker_sel} se ha actualizado a {nuevo_stop:.2f}.", icon="💾")
        except Exception as e: st.error(f"Error técnico: {e}")

    # --- NUEVA PESTAÑA: AÑADIR A CARTERA MANULAMENTE ---
    with tab_add:
        st.markdown("### ➕ Registrar Nueva Compra Manualmente")
        with st.form("form_add"):
            c1, c2, c3 = st.columns(3)
            with c1: 
                t_ticker = st.text_input("Ticker").upper()
                t_fecha_in = st.date_input("Fecha")
                t_precio_in = st.number_input("Precio Compra", format="%.2f")
            with c2: 
                t_acciones = st.number_input("Acciones", format="%.2f")
                t_stop = st.number_input("Stop Loss Inicial", format="%.2f")
                t_fecha_s4 = st.date_input("Fecha S4")
            with c3: 
                t_precio_s4 = st.number_input("Precio S4", format="%.2f")
                t_fecha_s5 = st.date_input("Fecha S5")
                t_precio_s5 = st.number_input("Precio S5", format="%.2f")
            
            if st.form_submit_button("Añadir a Cartera") and t_ticker != "":
                with st.spinner("Añadiendo..."):
                    df_c = conn.read(worksheet="Cartera", ttl=60)
                    n_pos = {"Ticker": t_ticker, "Fecha_Entrada": t_fecha_in.strftime("%Y-%m-%d"), "Precio_Entrada": t_precio_in, "Num_Acciones": t_acciones, "Stop_Actual": t_stop, "Fecha_Ruptura_S4": t_fecha_s4.strftime("%Y-%m-%d"), "Precio_Ruptura_S4": t_precio_s4, "Fecha_Ruptura_S5": t_fecha_s5.strftime("%Y-%m-%d"), "Precio_Ruptura_S5": t_precio_s5}
                    conn.update(worksheet="Cartera", data=pd.concat([df_c, pd.DataFrame([n_pos])], ignore_index=True))
                    st.cache_data.clear() # SMART WIPER
                    st.toast("Añadido exitosamente.", icon="✅")

    # --- HISTORIAL ---
    with tab_historial:
        try:
            df_h = conn.read(worksheet="Historial", ttl=60).dropna(how="all")
            if not df_h.empty:
                df_h['Fecha_Venta'] = pd.to_datetime(df_h['Fecha_Venta']).dt.date
                f_in = st.date_input("Analizar desde:", value=pd.to_datetime("2024-01-01").date())
                df_f = df_h[df_h['Fecha_Venta'] >= f_in]
                c1, c2, c3 = st.columns(3)
                c1.metric("Beneficio Neto", f"{df_f['Beneficio_EUR'].sum():.2f} €")
                c2.metric("Operaciones", len(df_f))
                c3.metric("Win Rate", f"{(len(df_f[df_f['Beneficio_EUR'] > 0]) / len(df_f) * 100) if len(df_f)>0 else 0:.1f}%")
                st.dataframe(df_f[['Ticker', 'Beneficio_EUR']], use_container_width=True)
        except: pass
