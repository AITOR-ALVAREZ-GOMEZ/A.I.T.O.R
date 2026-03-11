import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="A.I.T.O.R. 8.4 - Roca Viva", layout="wide")

CAPITAL_TOTAL = 277000.0
DIAS_FIB = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]

COL_DATABASE = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6):
    COL_DATABASE.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    existing_data = conn.read(worksheet="Sheet1", ttl=5)
except:
    existing_data = pd.DataFrame(columns=COL_DATABASE)

# --- BUSCADOR ---
st.sidebar.header("🔍 Buscador de Activos")
ticker = st.sidebar.text_input("TICKER", "MSFT").upper()

nombre_emp = "Buscando..."
p_mercado = 0.0
prevision_3y = 0.0

if ticker != "":
    try:
        stock = yf.Ticker(ticker)
        inf = stock.info
        nombre_emp = inf.get('longName', 'Ticker no detectado')
        p_mercado = inf.get('regularMarketPrice', inf.get('previousClose', 0.0))
        prevision_3y = inf.get('earningsGrowth', 0) or inf.get('revenueGrowth', 0) or 0
        
        # Filtro de seguridad por si Yahoo Finance da un dato loco
        if prevision_3y > 1.0:
            prevision_3y = 0.15 
    except:
        pass

st.sidebar.subheader(f"🏢 {nombre_emp}")
st.sidebar.markdown("---")

# --- CALIDAD (LIBRO BLANCO) ---
st.sidebar.header("📚 Calidad (Libro Blanco)")
if prevision_3y > 0:
    st.sidebar.success(f"🎯 Previsión Consenso 3Y: {prevision_3y*100:.1f}%")

op_eps = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]

if prevision_3y > 0.25:
    idx_auto = 3
elif prevision_3y > 0.15:
    idx_auto = 2
elif prevision_3y > 0.10:
    idx_auto = 1
else:
    idx_auto = 0

eps_val = st.sidebar.selectbox("Expectativa Crecimiento", op_eps, index=idx_auto)

pts_eps_dict = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}
pts_eps = pts_eps_dict[eps_val]

c_inst = st.sidebar.checkbox("Manos Fuertes", value=True)
c_sect = st.sidebar.checkbox("Líder Sector", value=True)

val_inst = 10 if c_inst else 0
val_sect = 10 if c_sect else 0

bonus_calidad = pts_eps + val_inst + val_sect
plus_ev = bonus_calidad / 7.0

# --- GESTIÓN DE CAPITAL ---
st.sidebar.header("💰 Gestión de Capital")
riesgo_pct = st.sidebar.slider("Riesgo por operación (%)", 0.5, 3.0, 1.0, step=0.5)
p_buy = st.sidebar.number_input("Precio Compra $", value=float(p_mercado))
p_sl = st.sidebar.number_input("Precio Stop Loss $", value=float(p_buy * 0.95))

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2 = st.tabs(["🔍 Escáner", "📊 Auditoría"])

with tab1:
    st.title(f"🚀 Dashboard: {ticker}")
    st.sidebar.header("🧬 Sistemas Fractalidad")
    def_fibs = [1, 3, 8, 14, 21]
    
    s_dias = []
    for i in range(5):
        idx_d = DIAS_FIB.index(def_fibs[i])
        d_val = st.sidebar.selectbox(f"S{i+1}", DIAS_FIB, index=idx_d, key=f"d{i}")
        s_dias.append(d_val)

    ev_list = []
    wr_list = []
    rat_list = []
    est_list = []
    
    cols = st.columns(5)
    for i in range(5):
        d = s_dias[i]
        with cols[i]:
            st.markdown(f"### {d} Días")
            wr = st.number_input(f"WR% {d}D", 0, 100, 50, key=f"w{i}")
            rt = st.number_input(f"Ratio {d}D", 0.0, 50.0, 2.0, key=f"r{i}")
            es = st.radio("Estado", ["🔴", "🔵"], key=f"e{i}", horizontal=True)
            
            wr_dec = wr / 100.0
            ev_i = round((wr_dec * rt) - ((1.0 - wr_dec) * 1.0), 2)
            
            ev_list.append(ev_i)
            wr_list.append(wr)
            rat_list.append(rt)
            est_list.append(es)
            
            st.metric(f"EV {d}D", f"{ev_i}")

    # --- CÁLCULOS FINALES ---
    ev_total = round((sum(ev_list) / 5.0) + plus_ev, 2)
    
    ite = 0.0
    if p_buy > 0:
        ite = round(((p_buy - p_sl) / p_buy) * 100.0, 2)
        
    puntos_estruc = 0
    for e in est_list[1:]:
        if e == "🔵":
            puntos_estruc += 10
            
    puntos_senal = 10 if est_list[0] == "🔵" else 0
    penalizacion = 30 if ite > 8 else 0
    
    idt = wr_list[0] + bonus_calidad + puntos_estruc + puntos_senal - penalizacion

    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("EV TOTAL", f"{ev_total}", f"+{plus_ev:.2f} Calidad")
    res2.metric("IDT PUNTOS", f"{idt} pts")
    res3.metric("RIESGO ITE", f"{ite}%")

    # --- CALCULADORA DE POSICIÓN ---
    p_max = CAPITAL_TOTAL * (riesgo_pct / 100.0)
    dif_p = p_buy - p_sl
    n_tit = 0
    if dif_p > 0:
        n_tit = int(p_max / dif_p)
    inv_t = n_tit * p_buy

    st.subheader(f"🧮 Planificación de la Ejecución (Capital: {CAPITAL_TOTAL:,.0f} €)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Riesgo Máximo", f"{p_max:,.0f} €")
    c2.metric("Acciones a Comprar", f"{n_tit
