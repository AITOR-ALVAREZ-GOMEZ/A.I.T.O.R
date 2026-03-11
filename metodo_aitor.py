import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 22.0 QUANT", layout="wide")

# --- CSS ESTILO APPLE AVANZADO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
    
    .stApp { background-color: #f5f5f7; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1d1d1f; }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.7) !important; backdrop-filter: blur(20px) !important; border-right: 1px solid rgba(0,0,0,0.05) !important; }
    h1, h2, h3, h1 *, h2 *, h3 * { color: #1d1d1f !important; font-weight: 700 !important; letter-spacing: -0.5px; }
    .stTextInput input, .stNumberInput input, [data-baseweb="select"] > div { background-color: #ffffff !important; border-radius: 12px !important; border: 1px solid rgba(0,0,0,0.1) !important; }
    .stButton>button { background: linear-gradient(180deg, #2b8af7 0%, #0071e3 100%) !important; color: white !important; border: none !important; border-radius: 20px !important; padding: 10px 24px !important; font-weight: 600 !important; box-shadow: 0 4px 14px rgba(0, 113, 227, 0.3) !important; }
    
    /* TARJETAS KPI (SIN CORTES) */
    .apple-kpi-container { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }
    .apple-kpi-card { background-color: #ffffff; border-radius: 20px; padding: 20px; flex: 1; min-width: 150px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.03); display: flex; flex-direction: column; justify-content: center; align-items: flex-start; }
    .apple-kpi-title { font-size: 0.8rem; color: #86868b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .apple-kpi-value { font-size: 2.2rem; font-weight: 800; color: #1d1d1f; line-height: 1; margin-bottom: 5px; white-space: nowrap; }
    .apple-kpi-sub { font-size: 0.9rem; font-weight: 600; padding: 4px 8px; border-radius: 8px; }
    .sub-green { background-color: #e5fbee; color: #188038; }
    .sub-red { background-color: #fce8e6; color: #c5221f; }
    .sub-gray { background-color: #f1f3f4; color: #5f6368; }

    /* INDICADOR LUMINOSO */
    .led-box { display: flex; align-items: center; gap: 10px; margin-bottom: 10px;}
    .led-green { width: 14px; height: 14px; background-color: #34c759; border-radius: 50%; box-shadow: 0 0 10px #34c759, inset 0 0 4px #000; animation: pulse-green 2s infinite; }
    .led-red { width: 14px; height: 14px; background-color: #ff3b30; border-radius: 50%; box-shadow: 0 0 10px #ff3b30, inset 0 0 4px #000; animation: pulse-red 2s infinite; }
    @keyframes pulse-green { 0% { box-shadow: 0 0 0 0 rgba(52, 199, 89, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(52, 199, 89, 0); } 100% { box-shadow: 0 0 0 0 rgba(52, 199, 89, 0); } }
    @keyframes pulse-red { 0% { box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(255, 59, 48, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 59, 48, 0); } }
    
    /* TARJETAS QUANT */
    .quant-card { background: #fff; padding: 20px; border-radius: 15px; border: 1px solid #e5e5ea; height: 100%; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
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

# --- BUSCADOR LATERAL ---
st.sidebar.header("Buscador de Activos")
ticker = st.sidebar.text_input("Ticker", "MSFT").upper()
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

# --- PESTAÑA 1: ESCÁNER --- (Ocultado el código idéntico por brevedad, es el mismo de la v21)
with tab1:
    st.title("Análisis: " + ticker)
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
    c1.metric("SCORE EV", str(ev_tot)); c2.metric("PUNTOS IDT", str(idt)); c3.metric("RIESGO ITE", str(ite) + "%")

# --- PESTAÑA 2: AUDITORÍA ---
with tab2: st.dataframe(df_datos.sort_values("EV_Total", ascending=False), use_container_width=True)

# --- PESTAÑA 3: CARTERA EN VIVO (LA MAGIA QUANT) ---
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
                    
                    # CÁLCULOS MATEMÁTICOS PUROS
                    df_q = hist_largo.copy()
                    precio_vivo = df_q['Close'].iloc[-1]
                    
                    # 1. Z-SCORE (Respecto a 55D)
                    df_q['MA55'] = df_q['Close'].rolling(window=55).mean()
                    df_q['STD55'] = df_q['Close'].rolling(window=55).std()
                    df_q['Z_Score'] = (df_q['Close'] - df_q['MA55']) / df_q['STD55']
                    z_actual = df_q['Z_Score'].iloc[-1]
                    
                    # 2. HURST APROXIMADO (Último Año)
                    def hurst_approx(p):
                        try:
                            lags = range(2, 20)
                            tau = [np.sqrt(np.std(np.subtract(p[lag:], p[:-lag]))) for lag in lags]
                            poly = np.polyfit(np.log(lags), np.log(tau), 1)
                            return poly[0] * 2.0
                        except: return 0.5
                    
                    hurst_val = hurst_approx(df_q['Close'].dropna().values[-252:])
                    
                    # 3. ACELERACIÓN Pura
                    df_q['ROC_10'] = df_q['Close'].pct_change(periods=10) * 100
                    df_q['Accel'] = df_q['ROC_10'].diff(periods=5)
                    accel_actual = df_q['Accel'].iloc[-1]
                    
                    # 4. DRAWDOWN
                    df_q['CumMax'] = df_q['Close'].cummax()
                    df_q['Drawdown'] = (df_q['Close'] - df_q['CumMax']) / df_q['CumMax'] * 100
                    dd_actual = df_q['Drawdown'].iloc[-1]
                    dd_max = df_q['Drawdown'].min()

                # --- PANEL KPI APPLE ---
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

                # --- ANÁLISIS CUANTITATIVO INSTITUCIONAL ---
                st.markdown("### 🧠 Análisis Cuantitativo (Datos del Algoritmo)")
                
                col_q1, col_q2 = st.columns(2)
                
                with col_q1:
                    st.markdown(f"""
                    <div class="quant-card">
                        <div class="quant-title">1. Z-Score (Desviación)</div>
                        <div class="quant-desc">Mide cuántas desviaciones estándar se aleja el precio de su Media de 55 días. Valores > 2.5 indican riesgo extremo de reversión.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Gauge Plotly Z-Score
                    fig_z = go.Figure(go.Indicator(
                        mode = "gauge+number", value = z_actual,
                        number = {'valueformat': '.2f', 'suffix': ' Sigmas'},
                        gauge = {'axis': {'range': [-4, 4]},
                                 'bar': {'color': "black"},
                                 'steps': [
                                     {'range': [-4, -2], 'color': "lightpink"},
                                     {'range': [-2, 2], 'color': "lightgreen"},
                                     {'range': [2, 2.5], 'color': "orange"},
                                     {'range': [2.5, 4], 'color': "red"}]}
                    ))
                    fig_z.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_z, use_container_width=True)

                    st.markdown(f"""
                    <div class="quant-card">
                        <div class="quant-title">3. Aceleración Pura</div>
                        <div class="quant-desc">Cambio en la velocidad del precio. Un pico extremo avisa de un "clímax comprador" (parábola inminente). Actual: {accel_actual:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Minigráfico de Aceleración
                    fig_acc = go.Figure(go.Scatter(y=df_q['Accel'].tail(60), mode='lines', fill='tozeroy', line_color='purple'))
                    fig_acc.update_layout(height=120, margin=dict(l=0, r=0, t=0, b=0), xaxis_visible=False)
                    st.plotly_chart(fig_acc, use_container_width=True)

                with col_q2:
                    st.markdown(f"""
                    <div class="quant-card">
                        <div class="quant-title">2. Exponente de Hurst</div>
                        <div class="quant-desc">Mide la "memoria" del precio. > 0.5 es tendencia sana. < 0.5 es mercado en rango errático o ruido.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    fig_h = go.Figure(go.Indicator(
                        mode = "gauge+number", value = hurst_val,
                        number = {'valueformat': '.2f'},
                        gauge = {'axis': {'range': [0, 1]},
                                 'bar': {'color': "darkblue"},
                                 'steps': [{'range': [0, 0.45], 'color': "lightgray"},
                                           {'range': [0.45, 0.55], 'color': "yellow"},
                                           {'range': [0.55, 1], 'color': "lightgreen"}]}
                    ))
                    fig_h.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_h, use_container_width=True)

                    st.markdown(f"""
                    <div class="quant-card">
                        <div class="quant-title">4. Perfil Drawdown</div>
                        <div class="quant-desc">Caída actual respecto a su máximo. Históricamente, este valor ha llegado a caer un {dd_max:.1f}% sin perder tendencia.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Minigráfico de Drawdown
                    fig_dd = go.Figure(go.Scatter(y=df_q['Drawdown'].tail(150), mode='lines', fill='tozeroy', line_color='red'))
                    fig_dd.update_layout(height=120, margin=dict(l=0, r=0, t=0, b=0), xaxis_visible=False, yaxis=dict(range=[dd_max, 0]))
                    st.plotly_chart(fig_dd, use_container_width=True)

                st.markdown("---")
                
                # --- NUEVO MOTOR DE DECISIÓN ESTADÍSTICO ---
                st.subheader("🤖 Decisión Cuántica del Algoritmo")
                stop_roto = precio_vivo < stop_actual
                
                if stop_roto:
                    st.error(f"🚨 **¡STOP ROTO!** El precio ha cruzado el umbral. Vende matemáticamente.")
                elif z_actual > 2.5:
                    st.warning(f"🚀 **ANOMALÍA (Z-Score +{z_actual:.2f}):** Tensión probabilística extrema. Ajusta el Stop a corto plazo para proteger la parábola.")
                elif hurst_val < 0.45:
                    st.warning("⚠️ **PÉRDIDA DE TENDENCIA:** El exponente Hurst advierte que el valor ha entrado en fase de ruido aleatorio.")
                else:
                    st.success(f"🛡️ **VÍA LIBRE ESTADÍSTICA:** Z-Score normal ({z_actual:.2f}) y Tendencia viva (Hurst {hurst_val:.2f}). Mantén el Stop relajado en S5.")
                    
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
            if st.form_submit_button("Añadir a Cartera") and t_ticker != "":
                df_c = conn.read(worksheet="Cartera", ttl=0)
                n_pos = {"Ticker": t_ticker, "Fecha_Entrada": t_fecha_in.strftime("%Y-%m-%d"), "Precio_Entrada": t_precio_in, "Num_Acciones": t_acciones, "Stop_Actual": t_stop, "Fecha_Ruptura_S4": t_fecha_s4.strftime("%Y-%m-%d"), "Precio_Ruptura_S4": t_precio_s4, "Fecha_Ruptura_S5": t_fecha_s5.strftime("%Y-%m-%d"), "Precio_Ruptura_S5": t_precio_s5}
                conn.update(worksheet="Cartera", data=pd.concat([df_c, pd.DataFrame([n_pos])], ignore_index=True))
                st.success("Añadido.")

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
