import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 29.1 QUANT", layout="wide")

# --- CSS ESTILO APPLE RESTAURADO ---
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
    .stButton>button { background: linear-gradient(180deg, #2b8af7 0%, #0071e3 100%) !important; color: white !important; border: none !important; border-radius: 20px !important; padding: 10px 24px !important; font-weight: 600 !important; box-shadow: 0 4px 14px rgba(0, 113, 227, 0.3) !important; }
    
    .rank-box { display: flex; gap: 6px; margin-top: 12px; flex-wrap: wrap; }
    .tag-on { border-radius: 12px; padding: 6px 10px; font-size: 0.75rem; font-weight: 700; color: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .tag-off { border-radius: 12px; padding: 6px 10px; font-size: 0.75rem; font-weight: 600; color: #8e8e93; border: 1px solid #d2d2d7; background: #fff; }
    
    .apple-kpi-container { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }
    .apple-kpi-card { background-color: #ffffff; border-radius: 20px; padding: 20px; flex: 1; min-width: 150px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: center; align-items: flex-start; }
    .apple-kpi-title { font-size: 0.8rem; color: #86868b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .apple-kpi-value { font-size: 2.2rem; font-weight: 800; color: #1d1d1f; line-height: 1; margin-bottom: 5px; white-space: nowrap; }
    .apple-kpi-sub { font-size: 0.9rem; font-weight: 600; padding: 4px 8px; border-radius: 8px; }
    .sub-green { background-color: #e5fbee; color: #188038; }
    .sub-red { background-color: #fce8e6; color: #c5221f; }
    .sub-gray { background-color: #f1f3f4; color: #5f6368; }

    .led-box { display: flex; align-items: center; gap: 10px; margin-bottom: 10px;}
    .led-green { width: 14px; height: 14px; background-color: #34c759; border-radius: 50%; box-shadow: 0 0 10px #34c759, inset 0 0 4px #000; animation: pulse-green 2s infinite; }
    .led-red { width: 14px; height: 14px; background-color: #ff3b30; border-radius: 50%; box-shadow: 0 0 10px #ff3b30, inset 0 0 4px #000; animation: pulse-red 2s infinite; }
    @keyframes pulse-green { 0% { box-shadow: 0 0 0 0 rgba(52, 199, 89, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(52, 199, 89, 0); } 100% { box-shadow: 0 0 0 0 rgba(52, 199, 89, 0); } }
    @keyframes pulse-red { 0% { box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(255, 59, 48, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 59, 48, 0); } }
    
    .quant-card { background: #fff; padding: 20px; border-radius: 15px; border: 1px solid #e5e5ea; height: 100%; box-shadow: 0 2px 10px rgba(0,0,0,0.02); margin-bottom: 15px;}
    .quant-title { font-size: 1.1rem; font-weight: 700; color: #1d1d1f; margin-bottom: 5px; }
    .quant-desc { font-size: 0.85rem; color: #86868b; line-height: 1.4; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
A_ACTUAL = datetime.datetime.now().year

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6): COL_DB.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

conn = st.connection("gsheets", type=GSheetsConnection)
try: df_datos = conn.read(worksheet="Sheet1", ttl=5)
except: df_datos = pd.DataFrame(columns=COL_DB)

# =====================================================================
# BUSCADOR LATERAL CON MEMORIA DE AUDITORÍA
# =====================================================================
st.sidebar.header("Buscador de Activos")
opciones_bd = df_datos['Ticker'].dropna().unique().tolist() if not df_datos.empty else []

ticker_manual = st.sidebar.text_input("Nuevo Ticker (Ej: MSFT):", "").upper()
ticker_lista = st.sidebar.selectbox("O cargar de Auditoría:", [""] + opciones_bd)

ticker = ticker_manual if ticker_manual != "" else ticker_lista
if ticker == "": ticker = "MSFT"

nom_emp, p_merc, prev_1y, eps_base = "Buscando...", 0.0, 0.0, 0.0

if ticker != "":
    try:
        stock = yf.Ticker(ticker)
        nom_emp = stock.info.get("longName", "Desconocido")
        p_merc = stock.info.get("regularMarketPrice", 0.0)
        eps_base = stock.info.get("trailingEps", 0.0)
        f_eps = stock.info.get("forwardEps", 0.0)
        if eps_base > 0 and f_eps > eps_base: prev_1y = (f_eps - eps_base) / eps_base
        else: prev_1y = stock.info.get("revenueGrowth", 0.0)
    except: pass

st.sidebar.subheader("Empresa: " + nom_emp)
st.sidebar.markdown("---")

st.sidebar.header("Calidad (Libro Blanco)")
if prev_1y > 0 and eps_base > 0:
    st.sidebar.markdown("### Proyeccion Beneficios (3Y)")
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
r_pct = st.sidebar.slider("Riesgo (%)", 0.5, 3.0, 1.0, step=0.5)
p_buy = st.sidebar.number_input("Precio Compra $", value=float(p_merc))
p_sl = st.sidebar.number_input("Stop Loss $", value=float(p_buy * 0.95))

# CARGA DE DATOS HISTÓRICOS DE LA AUDITORÍA
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
tab1, tab2, tab3 = st.tabs(["📊 Escáner Cuántico", "📋 Auditoría", "💼 Cartera en Vivo"])

# --- PESTAÑA 1: ESCÁNER ---
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
            es = st.radio("Señal", ["Venta", "Compra"], key=f"e{i}")
            wr_dec = wr / 100.0
            ev_i = round((wr_dec * rt) - ((1.0 - wr_dec) * 1.0), 2)
            s_elegidos.append(s_val); l_ev.append(ev_i); l_wr.append(wr); l_rt.append(rt); l_es.append(es)
            st.metric("EV " + str(s_val) + "D", str(ev_i))

    ev_tot = round((sum(l_ev) / 5.0) + ev_plus, 2)
    ite = round(((p_buy - p_sl) / p_buy) * 100.0, 2) if p_buy > 0 else 0.0
    p_estr = sum(10 for e in l_es[1:] if e == "Compra")
    p_sen = 10 if l_es[0] == "Compra" else 0
    penal = 30 if ite > 8 else 0
    idt = l_wr[0] + bono + p_estr + p_sen - penal

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("SCORE EV", str(ev_tot))
        h_ev = "<div class='rank-box'>"
        if ev_tot >= 10: h_ev += "<div class='tag-on' style='background:#34c759;'>TIER S</div><div class='tag-off'>TIER A</div><div class='tag-off'>DESCARTE</div>"
        elif ev_tot >= 5: h_ev += "<div class='tag-off'>TIER S</div><div class='tag-on' style='background:#2b8af7;'>TIER A</div><div class='tag-off'>DESCARTE</div>"
        else: h_ev += "<div class='tag-off'>TIER S</div><div class='tag-off'>TIER A</div><div class='tag-on' style='background:#ff3b30;'>DESCARTE</div>"
        h_ev += "</div>"
        st.markdown(h_ev, unsafe_allow_html=True)
    with c2:
        st.metric("PUNTOS IDT", str(idt))
        h_idt = "<div class='rank-box'>"
        if idt >= 100: h_idt += "<div class='tag-on' style='background:#1d1d1f;'>OBLIGATORIA</div><div class='tag-off'>TACTICA</div><div class='tag-off'>BLOQUEADA</div>"
        elif idt >= 85: h_idt += "<div class='tag-off'>OBLIGATORIA</div><div class='tag-on' style='background:#ff9500;'>TACTICA</div><div class='tag-off'>BLOQUEADA</div>"
        else: h_idt += "<div class='tag-off'>OBLIGATORIA</div><div class='tag-off'>TACTICA</div><div class='tag-on' style='background:#ff3b30;'>BLOQUEADA</div>"
        h_idt += "</div>"
        st.markdown(h_idt, unsafe_allow_html=True)
    with c3:
        st.metric("RIESGO ITE", str(ite) + "%")
        h_ite = "<div class='rank-box'>"
        if ite <= 5: h_ite += "<div class='tag-on' style='background:#34c759;'>OPTIMO</div><div class='tag-off'>LIMITE</div><div class='tag-off'>NO OPERABLE</div>"
        elif ite <= 8: h_ite += "<div class='tag-off'>OPTIMO</div><div class='tag-on' style='background:#ff9500;'>LIMITE</div><div class='tag-off'>NO OPERABLE</div>"
        else: h_ite += "<div class='tag-off'>OPTIMO</div><div class='tag-off'>LIMITE</div><div class='tag-on' style='background:#ff3b30;'>NO OPERABLE</div>"
        h_ite += "</div>"
        st.markdown(h_ite, unsafe_allow_html=True)

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

    # =====================================================================
    # TERMÓMETRO DE TOMA DE DECISIÓN EN EL ESCÁNER
    # =====================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🎯 Controlador de Decisión Pre-Compra (Riesgo del Trade)")
    
    col_radar_esc, col_txt_esc = st.columns([2, 1])
    with col_radar_esc:
        if p_buy > 0 and p_sl > 0 and p_buy > p_sl:
            rango_min_esc = p_sl * 0.95
            rango_max_esc = p_buy * 1.05
            lim_peligro_esc = p_sl + (p_buy - p_sl) * 0.20
            
            fig_radar_esc = go.Figure(go.Indicator(
                mode="gauge+number",
                value=p_buy,
                title=dict(text="Distancia Estructural al Stop Loss", font=dict(size=14)),
                number=dict(suffix=" €", valueformat=".2f"),
                gauge=dict(
                    axis=dict(range=[rango_min_esc, rango_max_esc]),
                    bar=dict(color="#1d1d1f"),
                    steps=[
                        dict(range=[rango_min_esc, p_sl], color="#ff3b30"),
                        dict(range=[p_sl, lim_peligro_esc], color="#ffcc00"),
                        dict(range=[lim_peligro_esc, rango_max_esc], color="#34c759")
                    ],
                    threshold=dict(line=dict(color="black", width=5), thickness=0.75, value=p_sl)
                )
            ))
            fig_radar_esc.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_radar_esc, use_container_width=True)
        else:
            st.info("⚠️ Configura el Precio de Compra y el Stop Loss correctamente en el panel lateral para ver el Radar.")

    with col_txt_esc:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if ite <= 5:
            st.success(f"**🟢 Riesgo Óptimo ({ite}%):** El Stop está matemáticamente bien ceñido. Tienes margen para usar apalancamiento sin disparar tu riesgo máximo.")
        elif ite <= 8:
            st.warning(f"**🟠 Riesgo Límite ({ite}%):** El Stop empieza a estar lejos. Tienes que reducir drásticamente el número de acciones para mantener tu riesgo del {r_pct}%.")
        else:
            st.error(f"**🔴 Riesgo Excesivo ({ite}%):** El Stop está demasiado lejos. Operación matemáticamente suicida. Ajusta la entrada o descarta el valor.")

    st.markdown("---")
    
    # =====================================================================
    # ORÁCULO CUANTITATIVO RENAISSANCE
    # =====================================================================
    st.subheader("🔮 Oráculo de Entrada (Modelo Cuantitativo)")
    if ticker != "":
        with st.spinner("Descargando data algorítmica para entrada..."):
            try:
                stock_esc = yf.Ticker(ticker)
                df_esc = stock_esc.history(period="2y")
                
                if not df_esc.empty:
                    df_esc['MA55'] = df_esc['Close'].rolling(window=55).mean()
                    df_esc['STD55'] = df_esc['Close'].rolling(window=55).std()
                    df_esc['Z_Score'] = (df_esc['Close'] - df_esc['MA55']) / df_esc['STD55']
                    z_in = df_esc['Z_Score'].iloc[-1] if not pd.isna(df_esc['Z_Score'].iloc[-1]) else 0
                    
                    def hurst_approx_in(p):
                        try:
                            lags = range(2, 20)
                            tau = [np.sqrt(np.std(np.subtract(p[lag:], p[:-lag]))) for lag in lags]
                            poly = np.polyfit(np.log(lags), np.log(tau), 1)
                            return poly[0] * 2.0
                        except: return 0.5
                    hurst_in = hurst_approx_in(df_esc['Close'].dropna().values[-252:])
                    
                    df_esc['ROC_10'] = df_esc['Close'].pct_change(periods=10) * 100
                    df_esc['Accel'] = df_esc['ROC_10'].diff(periods=5)
                    acc_in = df_esc['Accel'].iloc[-1] if not pd.isna(df_esc['Accel'].iloc[-1]) else 0
                    
                    df_esc['CumMax'] = df_esc['Close'].cummax()
                    df_esc['Drawdown'] = (df_esc['Close'] - df_esc['CumMax']) / df_esc['CumMax'] * 100
                    dd_in = df_esc['Drawdown'].iloc[-1]
                    dd_min_in = df_esc['Drawdown'].min()

                    col_eq1, col_eq2 = st.columns(2)
                    with col_eq1:
                        st.markdown("""<div class="quant-card"><div class="quant-title">Z-Score (Desviación)</div><div class="quant-desc">Filtro Renaissance: Comprar solo si está entre +0.5 y +2.0 (Fuerza controlada).</div>""", unsafe_allow_html=True)
                        fig_ze = go.Figure(go.Indicator(mode="gauge+number", value=z_in, number=dict(valueformat='.2f', suffix=' Z'), gauge=dict(axis=dict(range=[-4, 4]), bar=dict(color="black"), steps=[dict(range=[-4, 0.5], color="lightgray"), dict(range=[0.5, 2.0], color="lightgreen"), dict(range=[2.0, 4], color="red")])))
                        fig_ze.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10))
                        st.plotly_chart(fig_ze, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("""<div class="quant-card"><div class="quant-title">Aceleración (Momentum)</div><div class="quant-desc">Filtro: Debe ser positiva (> 0). Indica que el dinero entra cada vez más rápido.</div>""", unsafe_allow_html=True)
                        fig_ae = go.Figure(go.Scatter(x=df_esc.index[-60:], y=df_esc['Accel'].tail(60), mode='lines', fill='tozeroy', line_color='purple'))
                        fig_ae.update_layout(height=140, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
                        st.plotly_chart(fig_ae, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    with col_eq2:
                        st.markdown("""<div class="quant-card"><div class="quant-title">Exponente Hurst (Memoria)</div><div class="quant-desc">Filtro Renaissance: Solo comprar si es > 0.55 (Probabilidad de que haya tendencia).</div>""", unsafe_allow_html=True)
                        fig_he = go.Figure(go.Indicator(mode="gauge+number", value=hurst_in, number=dict(valueformat='.2f'), gauge=dict(axis=dict(range=[0, 1]), bar=dict(color="darkblue"), steps=[dict(range=[0, 0.55], color="lightgray"), dict(range=[0.55, 1], color="lightgreen")])))
                        fig_he.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10))
                        st.plotly_chart(fig_he, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown(f"""<div class="quant-card"><div class="quant-title">Drawdown (Riesgo Histórico)</div><div class="quant-desc">El valor ha llegado a caer un {dd_min_in:.1f}%. Úsalo para planificar tu Stop.</div>""", unsafe_allow_html=True)
                        fig_dde = go.Figure(go.Scatter(x=df_esc.index[-150:], y=df_esc['Drawdown'].tail(150), mode='lines', fill='tozeroy', line_color='red'))
                        fig_dde.update_layout(height=140, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False), yaxis=dict(range=[dd_min_in*1.1, 0]))
                        st.plotly_chart(fig_dde, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    if hurst_in > 0.55 and (0.5 <= z_in <= 2.0) and acc_in > 0:
                        st.success("🟢 **SEÑAL CUANTITATIVA APROBADA:** El activo cumple los requisitos estadísticos. Tiene memoria tendencial, aceleración positiva y no está parabólico. ¡Buena compra!")
                    elif z_in > 2.0:
                        st.error(f"🔴 **RECHAZO CUANTITATIVO:** Z-Score ({z_in:.2f}) en modo burbuja. Entrar ahora es comprar en el techo. Espera a que descanse.")
                    elif hurst_in <= 0.55:
                        st.warning(f"🟡 **RECHAZO CUANTITATIVO:** El Exponente de Hurst ({hurst_in:.2f}) indica que no hay tendencia probada. El precio es aleatorio.")
                    else:
                        st.info("⚪ **NEUTRAL:** El activo no cumple los criterios estrictos de momentum cuantitativo. Depende de tu criterio estructural.")
            except:
                st.error("No se pudo calcular el modelo para este ticker.")

    if ev_tot < 5 or ite > 8: v_c, v_t = "#ff3b30", "OPERACION NO VIABLE"
    elif idt >= 100 and ite <= 5: v_c, v_t = "#1d1d1f", "COMPRA OBLIGATORIA"
    elif idt >= 85 and ite <= 8: v_c, v_t = "#ff9500", "COMPRA TACTICA"
    else: v_c, v_t = "#ff3b30", "ARMA BLOQUEADA"
        
    tag_v = f"<div style='text-align:center; margin-top:20px;'><div class='tag-on' style='background:{v_c}; font-size:1.2rem; padding:15px 30px;'>{v_t}</div></div>"
    st.markdown(tag_v, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Guardar en Nube"):
        d_sav = {"Ticker": ticker, "Tier": v_t, "EV_Total": ev_tot, "IDT_Puntos": idt, "ITE_Porc": ite, "Veredicto": v_t, "Acciones": n_tit, "Inversion": inv_t}
        for j in range(5):
            d_sav[f"S{j+1}_Dias"] = s_elegidos[j]
            d_sav[f"W{j+1}"] = l_wr[j]
            d_sav[f"R{j+1}"] = l_rt[j]
        new_row = pd.DataFrame([d_sav])
        df_upd = pd.concat([df_datos, new_row], ignore_index=True).drop_duplicates("Ticker", keep="last")
        conn.update(worksheet="Sheet1", data=df_upd)
        st.success("Guardado ok.")

# --- PESTAÑA 2: AUDITORÍA ---
with tab2: 
    st.markdown("### Base de Datos de Escaneos")
    st.info("💡 **Consejo de Gestión:** Si quieres re-evaluar un valor de esta tabla, ve al menú de la izquierda y selecciónalo en el desplegable 'O cargar de Auditoría'. El Escáner recuperará tus sistemas automáticamente.")
    st.dataframe(df_datos.sort_values("EV_Total", ascending=False), use_container_width=True)

# --- PESTAÑA 3: CARTERA EN VIVO ---
with tab3:
    st.markdown("### Gestión Quántica de Operaciones")
    tab_vivas, tab_add, tab_historial = st.tabs(["🟢 Posiciones Vivas", "➕ Añadir a Cartera", "📚 Historial"])
    
    with tab_vivas:
        try:
            df_cartera = conn.read(worksheet="Cartera", ttl=0).dropna(how="all")
            if df_cartera.empty:
                st.warning("Tu cartera está vacía.")
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
                    df_q['Z_Score'] = (df_q['Close'] - df_q['MA55']) / df_q['STD55']
                    z_actual = df_q['Z_Score'].iloc[-1] if not pd.isna(df_q['Z_Score'].iloc[-1]) else 0
                    
                    def hurst_approx(p):
                        try:
                            lags = range(2, 20)
                            tau = [np.sqrt(np.std(np.subtract(p[lag:], p[:-lag]))) for lag in lags]
                            poly = np.polyfit(np.log(lags), np.log(tau), 1)
                            return poly[0] * 2.0
                        except: return 0.5
                    
                    hurst_val = hurst_approx(df_q['Close'].dropna().values[-252:])
                    df_q['ROC_10'] = df_q['Close'].pct_change(periods=10) * 100
                    df_q['Accel'] = df_q['ROC_10'].diff(periods=5)
                    accel_actual = df_q['Accel'].iloc[-1] if not pd.isna(df_q['Accel'].iloc[-1]) else 0
                    
                    df_q['CumMax'] = df_q['Close'].cummax()
                    df_q['Drawdown'] = (df_q['Close'] - df_q['CumMax']) / df_q['CumMax'] * 100
                    dd_max = df_q['Drawdown'].min()

                beneficio_eur = (precio_vivo - precio_in) * acciones
                beneficio_pct = ((precio_vivo - precio_in) / precio_in) * 100
                dias_pos = (datetime.date.today() - fecha_in).days
                if dias_pos <= 0: dias_pos = 1
                
                color_borde = '#34c759' if beneficio_pct >= 0 else '#ff3b30'
                html_kpis = (
                    '<div class="apple-kpi-container">'
                    f'<div class="apple-kpi-card" style="border-left: 5px solid {color_borde};">'
                    f'<div class="led-box"><div class="{"led-green" if beneficio_pct>=0 else "led-red"}"></div><div class="apple-kpi-title" style="margin:0;">Rentabilidad Real</div></div>'
                    f'<div class="apple-kpi-value">{beneficio_pct:+.2f}%</div>'
                    f'<div class="apple-kpi-sub {"sub-green" if beneficio_pct>=0 else "sub-red"}">{beneficio_eur:+.2f} € Netos</div>'
                    '</div>'
                    f'<div class="apple-kpi-card"><div class="apple-kpi-title">Precio Mercado</div><div class="apple-kpi-value">{precio_vivo:.2f}</div><div class="apple-kpi-sub sub-gray">Entrada: {precio_in:.2f}</div></div>'
                    f'<div class="apple-kpi-card"><div class="apple-kpi-title">Tiempo en Tendencia</div><div class="apple-kpi-value">{dias_pos} Días</div><div class="apple-kpi-sub sub-gray">Desde {fecha_in.strftime("%d/%m/%Y")}</div></div>'
                    '</div>'
                )
                st.markdown(html_kpis, unsafe_allow_html=True)

                st.markdown("### 🧠 Análisis Cuantitativo (Datos de Mantenimiento)")
                col_q1, col_q2 = st.columns(2)
                
                with col_q1:
                    st.markdown("""<div class="quant-card"><div class="quant-title">1. Z-Score (Desviación)</div><div class="quant-desc">Mide cuántas desviaciones estándar se aleja el precio de su Media de 55 días. Valores > 2.5 indican riesgo de reversión.</div>""", unsafe_allow_html=True)
                    fig_z = go.Figure(go.Indicator(mode="gauge+number", value=z_actual, number=dict(valueformat='.2f', suffix=' Sigmas'), gauge=dict(axis=dict(range=[-4, 4]), bar=dict(color="black"), steps=[dict(range=[-4, -2], color="lightpink"), dict(range=[-2, 2], color="lightgreen"), dict(range=[2, 2.5], color="orange"), dict(range=[2.5, 4], color="red")])))
                    fig_z.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_z, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown(f"""<div class="quant-card"><div class="quant-title">3. Aceleración Pura</div><div class="quant-desc">Cambio en la velocidad del precio. Un pico extremo avisa de un "clímax comprador". Actual: {accel_actual:.2f}</div>""", unsafe_allow_html=True)
                    fig_acc = go.Figure(go.Scatter(x=df_q.index[-60:], y=df_q['Accel'].tail(60), mode='lines', fill='tozeroy', line_color='purple'))
                    fig_acc.update_layout(height=160, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False, title="Fecha"), yaxis=dict(showgrid=False))
                    st.plotly_chart(fig_acc, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_q2:
                    st.markdown("""<div class="quant-card"><div class="quant-title">2. Exponente de Hurst</div><div class="quant-desc">Mide la "memoria" del precio. > 0.5 es tendencia sana. < 0.5 es mercado en rango errático.</div>""", unsafe_allow_html=True)
                    fig_h = go.Figure(go.Indicator(mode="gauge+number", value=hurst_val, number=dict(valueformat='.2f'), gauge=dict(axis=dict(range=[0, 1]), bar=dict(color="darkblue"), steps=[dict(range=[0, 0.45], color="lightgray"), dict(range=[0.45, 0.55], color="yellow"), dict(range=[0.55, 1], color="lightgreen")])))
                    fig_h.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_h, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown(f"""<div class="quant-card"><div class="quant-title">4. Perfil Drawdown</div><div class="quant-desc">Históricamente, este valor ha llegado a caer un {dd_max:.1f}% sin perder tendencia estructural.</div>""", unsafe_allow_html=True)
                    fig_dd = go.Figure(go.Scatter(x=df_q.index[-150:], y=df_q['Drawdown'].tail(150), mode='lines', fill='tozeroy', line_color='red'))
                    fig_dd.update_layout(height=160, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False, title="Fecha"), yaxis=dict(range=[dd_max*1.1, 0]))
                    st.plotly_chart(fig_dd, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("⚖️ Veredicto del Algoritmo y Gestión de Stop")
                
                stop_roto = precio_vivo < stop_actual
                
                # Asignación segura en líneas cortas para evitar errores de sintaxis al copiar
                if stop_roto:
                    stop_sugerido = stop_actual
                    msg = f"🚨 **¡STOP ROTO! ({stop_actual:.2f} €)** El precio ha cruzado tu umbral. Vende matemáticamente."
                    st.error(msg)
                elif z_actual > 2.5 or (z_actual > 2.0 and accel_actual > 5.0):
                    stop_sugerido = media_s2
                    msg = f"🚀 **CLÍMAX COMPRADOR:** Tensión extrema. Sube el Stop al sistema S2 en {media_s2:.2f} €."
                    st.warning(msg)
                elif hurst_val < 0.45:
                    stop_sugerido = media_s5
                    msg = f"⚠️ **RUIDO LATERAL:** Fase de descanso. Mantén el Stop en S5 ubicado en {media_s5:.2f} €."
                    st.warning(msg)
                else:
                    stop_sugerido = media_s4
                    msg = f"🛡️ **TENDENCIA SANA:** Matemática a tu favor. Usa tu Stop en S4 ({media_s4:.2f} €) o S5 ({media_s5:.2f} €)."
                    st.success(msg)

                st.markdown("<br>", unsafe_allow_html=True)
                col_term, col_vacia = st.columns([2, 1])
                with col_term:
                    rango_min = stop_sugerido * 0.90 
                    rango_max = max(precio_vivo * 1.05, stop_sugerido * 1.10) 
                    limite_naranja = stop_sugerido * 1.03 
                    
                    fig_riesgo = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=precio_vivo,
                        title=dict(text="Radar Cuántico (Precio vs Stop Matemático)", font=dict(size=14)),
                        number=dict(suffix=" €", valueformat=".2f"),
                        gauge=dict(
                            axis=dict(range=[rango_min, rango_max]),
                            bar=dict(color="#1d1d1f"),
                            steps=[
                                dict(range=[rango_min, stop_sugerido], color="#ff3b30"),
                                dict(range=[stop_sugerido, limite_naranja], color="#ffcc00"),
                                dict(range=[limite_naranja, rango_max], color="#34c759")
                            ],
                            threshold=dict(line=dict(color="black", width=5), thickness=0.75, value=stop_sugerido)
                        )
                    ))
                    fig_riesgo.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_riesgo, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error técnico: {e}")

    # --- NUEVA PESTAÑA: AÑADIR A CARTERA ---
    with tab_add:
        st.markdown("### ➕ Registrar Nueva Compra")
        with st.form("form_add"):
            c1, c2, c3 = st.columns(3)
            with c1: t_ticker = st.text_input("Ticker").upper(); t_fecha_in = st.date_input("Fecha"); t_precio_in = st.number_input("Precio Compra", format="%.2f")
            with c2: t_acciones = st.number_input("Acciones", format="%.2f"); t_stop = st.number_input("Stop Loss", format="%.2f"); t_fecha_s4 = st.date_input("Fecha S4")
            with c3: t_precio_s4 = st.number_input("Precio S4", format="%.2f"); t_fecha_s5 = st.date_input("Fecha S5"); t_precio_s5 = st.number_input("Precio S5", format="%.2f")
            
            btn_submit = st.form_submit_button("Añadir a Cartera")
            if btn_submit and t_ticker != "":
                df_c = conn.read(worksheet="Cartera", ttl=0)
                n_pos = {
                    "Ticker": t_ticker, 
                    "Fecha_Entrada": t_fecha_in.strftime("%Y-%m-%d"), 
                    "Precio_Entrada": t_precio_in, 
                    "Num_Acciones": t_acciones, 
                    "Stop_Actual": t_stop, 
                    "Fecha_Ruptura_S4": t_fecha_s4.strftime("%Y-%m-%d"), 
                    "Precio_Ruptura_S4": t_precio_s4, 
                    "Fecha_Ruptura_S5": t_fecha_s5.strftime("%Y-%m-%d"), 
                    "Precio_Ruptura_S5": t_precio_s5
                }
                conn.update(worksheet="Cartera", data=pd.concat([df_c, pd.DataFrame([n_pos])], ignore_index=True))
                st.success("Añadido exitosamente.")

    # --- HISTORIAL ---
    with tab_historial:
        try:
            df_h = conn.read(worksheet="Historial", ttl=0).dropna(how="all")
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
