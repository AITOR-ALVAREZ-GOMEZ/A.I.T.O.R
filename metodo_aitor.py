import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="A.I.T.O.R. 8.6 - Titanium", layout="wide")

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6):
    COL_DB.extend(["S" + str(i) + "_Dias", "W" + str(i), "R" + str(i)])

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df_datos = conn.read(worksheet="Sheet1", ttl=5)
except:
    df_datos = pd.DataFrame(columns=COL_DB)

# --- 2. BUSCADOR ---
st.sidebar.header("🔍 Buscador")
ticker = st.sidebar.text_input("TICKER", "MSFT").upper()

nom_emp = "Buscando..."
p_merc = 0.0
prev_3y = 0.0

if ticker != "":
    try:
        stock = yf.Ticker(ticker)
        nom_emp = stock.info.get('longName', 'Desconocido')
        p_merc = stock.info.get('regularMarketPrice', 0.0)
        
        c_earn = stock.info.get('earningsGrowth', 0)
        c_rev = stock.info.get('revenueGrowth', 0)
        if c_earn > 0:
            prev_3y = c_earn
        else:
            prev_3y = c_rev
            
        if prev_3y > 1.0: 
            prev_3y = 0.15 
    except:
        pass

st.sidebar.subheader("🏢 " + nom_emp)
st.sidebar.markdown("---")

# --- 3. CALIDAD ---
st.sidebar.header("📚 Calidad (Libro Blanco)")
if prev_3y > 0:
    st.sidebar.success("🎯 Previsión 3Y: " + str(round(prev_3y * 100, 1)) + "%")

ops = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]

if prev_3y > 0.25: i_auto = 3
elif prev_3y > 0.15: i_auto = 2
elif prev_3y > 0.10: i_auto = 1
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
        
    p_estr = 0
    for e in l_es[1:]:
        if e == "🔵": p_estr += 10
            
    p_sen = 10 if l_es[0] == "🔵" else 0
    penal = 30 if ite > 8 else 0
    
    idt = l_wr[0] + bono + p_estr + p_sen - penal

    st.markdown("---")
    r1, r2, r3 = st.columns(3)
    r
