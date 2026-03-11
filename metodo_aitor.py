import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="A.I.T.O.R. 10.0 - Curva Dinámica", layout="wide")

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
AÑO_ACTUAL = datetime.datetime.now().year

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6):
    COL_DB.extend(["S" + str(i) + "_Dias", "W" + str(i), "R" + str(i)])

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df_datos = conn.read(worksheet="Sheet1", ttl=5)
except:
    df_datos = pd.DataFrame(columns=COL_DB)

# --- 2. BUSCADOR Y MOTOR DE PREVISIONES ---
st.sidebar.header("🔍 Buscador")
ticker = st.sidebar.text_input("TICKER", "MSFT").upper()

nom_emp = "Buscando..."
p_merc = 0.0
prev_1y = 0.0
eps_base = 0.0

if ticker != "":
    try:
        stock = yf.Ticker(ticker)
        nom_emp = stock.info.get('longName', 'Desconocido')
        p_merc = stock.info.get('regularMarketPrice', 0.0)
        
        eps_base = stock.info.get('trailingEps', 0)
        f_eps = stock.info.get('forwardEps', 0)
        
        if eps_base > 0 and f_eps > eps_base:
            prev_1y = (f_eps - eps_base) / eps_base
        else:
            prev_1y = stock.info.get('revenueGrowth', 0)
            
    except:
        pass

st.sidebar.subheader("🏢 " + nom_emp)
st.sidebar.markdown("---")

# --- 3. CALIDAD Y PROYECCIÓN A 3 AÑOS ---
st.sidebar.header("📚 Calidad (Libro Blanco)")

# Proyección Matemática Dinámica
if prev_1y > 0 and eps_base > 0:
    st.sidebar.markdown("### 📈 Proyección de Beneficios (EPS)")
    eps_y1 = eps_base * (1 + prev_1y)
    eps_y2 = eps_y1 * (1 + prev_1y)
    eps_y3 = eps_y2 * (1 + prev_1y)
    
    st.sidebar.info(
        f"**{AÑO_ACTUAL}:** {eps_y1:.2f} $\n\n"
        f"**{AÑO_ACTUAL + 1}:** {eps_y2:.2f} $\n\n"
        f"**{AÑO_ACTUAL + 2}:** {eps_y3:.2f} $"
    )
    st.sidebar.caption(f"Crecimiento proyectado: {prev_1y*100:.1f}% anual")
elif prev_1y > 0:
    st.sidebar.success(f"🎯 Crecimiento proyectado: {prev_1y*100:.1f}%")

ops = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]

if prev_1y > 0.25: i_auto = 3
elif prev_1y > 0.15: i_auto = 2
elif prev_1y > 0.10: i_auto = 1
else: i_auto = 0

v_eps = st.sidebar.selectbox("Crecimiento EPS", ops, index=i_auto)
dict_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}
pts_eps = dict_eps[v_eps]

c_inst = st.sidebar.checkbox("Manos Fuertes", value=True)
c_sect = st.sidebar.checkbox("Líder Sector", value=True)

bono = pts_eps + (10 if c_inst else 0) + (10 if c_sect else 0)
ev_plus = bono / 7.0

# --- 4. RIESGO ---
st.sidebar.header("💰 Gestión Capital")
r_pct = st.sidebar.slider("Riesgo (%)", 0.5, 3.0, 1.0, step=0.5)
p_buy = st.sidebar.number_input("Precio Compra $", value=float(p_merc))
p_sl = st.sidebar.number_input("Stop Loss $", value=float(p_buy * 0.95))

# --- 5. DASHBOARD ---
tab1, tab2 = st.tabs(["🔍 Escáner", "📊 Auditoría"])

with tab1:
    st.title("🚀 Análisis: " + ticker)
    st.sidebar.header("🧬 Sistemas")
    
    d_defs = [1, 3, 8, 14, 21]
    s_elegidos = []
    for i in range(5):
        i_def = DIAS.index(d_defs[i])
        s_val = st.sidebar.selectbox("S" + str(i+1), DIAS, index=i_def, key="d"+str(i))
        s_elegidos.append(s_val)

    l_ev, l_wr, l_rt, l_es = [], [], [], []
    cols = st.columns(5)
    
    for i in range(5):
        dia = s_elegidos[i]
        with cols[i]:
            st.markdown("### " + str(dia) + " D")
            wr = st.number_input("WR% " + str(dia) + "D", 0, 100, 50, key="w"+str(i))
            rt = st.number_input("Ratio " + str(dia) + "D", 0.0, 50.0, 2.0, key="r"+str(i))
            es = st.radio("Est.", ["🔴", "🔵"], key="e"+str(i), horizontal=True)
            
            wr_d = wr / 100.0
            ev_i = round((wr_d * rt) - ((1.0 - wr_d) * 1.0), 2)
            
            l_ev.append(ev_i)
            l_wr.append(wr)
            l_rt.append(rt)
            l_es.append(es)
            
            st.metric("EV " + str(dia) + "D", str(ev_i))

    # --- RESULTADOS ---
    ev_tot = round((sum(l_ev) / 5.0) + ev_plus, 2)
    ite = 0.0
    if p_buy > 0:
        ite = round(((p_buy - p_sl) / p_buy) * 100.0, 2)
        
    p_estr = sum(10 for e in l_es[1:] if e == "🔵")
    p_sen = 10 if l_es[0] == "🔵" else 0
    penal = 30 if ite > 8 else 0
    
    idt = l_wr[0] + bono + p_estr + p_sen - penal

    st.markdown("---")
    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("EV TOTAL", str(ev_tot), "+" + str(round(ev_plus, 2)) + " Calidad")
    with r2:
        st.metric("IDT PUNTOS", str(idt) + " pts")
    with r3:
        st.metric("RIESGO ITE", str(ite) + "%")

    # --- CALCULADORA 277k (CORREGIDA) ---
    p_max = CAPITAL * (r_pct / 100.0)
    dif_p = p_buy - p_sl
    
    n_tit = 0
    if dif_p > 0:
        n_tit = int(p_max / dif_p)
        
    inv_t = n_tit * p_buy

    st.markdown("---")
    st.subheader(f"🧮 Ejecución (Capital: {CAPITAL:,.0f} €)")
    
    # Se usa 'with' para evitar el fallo del DeltaGenerator
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Riesgo Má
