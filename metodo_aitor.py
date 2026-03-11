import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime

st.set_page_config(page_title="AITOR 14.0", layout="wide")

# --- CSS PARTIDO EN TROZOS PEQUEÑOS ---
css = "<style>\n"
css += ".stApp {background-color:#f5f5f7; color:#1d1d1f;}\n"
css += "[data-testid='stSidebar'] {background:rgba(255,255,255,0.7);}\n"
css += "h1,h2,h3 {color:#1d1d1f!important; font-weight:700!important;}\n"
css += "[data-testid='stMetric'] {background:#fff; border-radius:18px;\n"
css += "padding:15px; min-height:140px; box-shadow:0 4px 15px rgba(0,0,0,0.04);}\n"
css += "[data-testid='stMetricValue'] {color:#1d1d1f!important;}\n"
css += "[data-testid='stMetricLabel'] {color:#86868b!important;}\n"
css += ".stTextInput input, .stNumberInput input {border-radius:12px;}\n"
css += ".stButton>button {background:#0071e3; color:#fff; border-radius:20px;}\n"
css += ".apple-rank-tag {border-radius:14px; padding:6px 14px; font-weight:600;\n"
css += "font-size:0.9rem; display:inline-block; margin-top:10px;}\n"
css += "</style>"

st.markdown(css, unsafe_allow_html=True)

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
A_ACTUAL = datetime.datetime.now().year

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos"]
COL_DB.extend(["ITE_Porc", "Veredicto", "Acciones", "Inversion"])
for i in range(1, 6):
    COL_DB.extend(["S" + str(i) + "_Dias", "W" + str(i), "R" + str(i)])

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df_datos = conn.read(worksheet="Sheet1", ttl=5)
except:
    df_datos = pd.DataFrame(columns=COL_DB)

# --- BUSCADOR ---
st.sidebar.header("Buscador de Activos")
ticker = st.sidebar.text_input("Ticker", "MSFT").upper()

nom_emp = "Buscando..."
p_merc = 0.0
prev_1y = 0.0
eps_base = 0.0

if ticker != "":
    try:
        stock = yf.Ticker(ticker)
        nom_emp = stock.info.get("longName", "Desconocido")
        p_merc = stock.info.get("regularMarketPrice", 0.0)
        eps_base = stock.info.get("trailingEps", 0.0)
        f_eps = stock.info.get("forwardEps", 0.0)
        
        if eps_base > 0 and f_eps > eps_base:
            prev_1y = (f_eps - eps_base) / eps_base
        else:
            prev_1y = stock.info.get("revenueGrowth", 0.0)
    except:
        pass

st.sidebar.subheader("Empresa: " + nom_emp)
st.sidebar.markdown("---")

# --- CALIDAD ---
st.sidebar.header("Calidad (Libro Blanco)")

if prev_1y > 0 and eps_base > 0:
    st.sidebar.markdown("### Proyeccion Beneficios (3Y)")
    e1 = eps_base * (1 + prev_1y)
    e2 = e1 * (1 + prev_1y)
    e3 = e2 * (1 + prev_1y)
    
    txt_proy = str(A_ACTUAL) + ": " + str(round(e1, 2)) + " $\n\n"
    txt_proy += str(A_ACTUAL + 1) + ": " + str(round(e2, 2)) + " $\n\n"
    txt_proy += str(A_ACTUAL + 2) + ": " + str(round(e3, 2)) + " $"
    st.sidebar.info(txt_proy)

ops = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]

if prev_1y > 0.25: i_auto = 3
elif prev_1y > 0.15: i_auto = 2
elif prev_1y > 0.10: i_auto = 1
else: i_auto = 0

v_eps = st.sidebar.selectbox("Crecimiento EPS", ops, index=i_auto)
dict_eps = {"Bajo (<10%)":0, "Medio (>10%)":5, "Alto (>15%)":10, "Explosivo (>25%)":15}
pts_eps = dict_eps[v_eps]

c_inst = st.sidebar.checkbox("Manos Fuertes", value=True)
c_sect = st.sidebar.checkbox("Lider Sector", value=True)

bono = pts_eps + (10 if c_inst else 0) + (10 if c_sect else 0)
ev_plus = bono / 7.0

# --- RIESGO ---
st.sidebar.header("Gestion Capital")
r_pct = st.sidebar.slider("Riesgo (%)", 0.5, 3.0, 1.0, step=0.5)
p_buy = st.sidebar.number_input("Precio Compra $", value=float(p_merc))
p_sl = st.sidebar.number_input("Stop Loss $", value=float(p_buy * 0.95))

# --- DASHBOARD ---
tab1, tab2 = st.tabs(["Escaner Cuantico", "Auditoria"])

with tab1:
    st.title("Analisis: " + ticker)
    st.sidebar.header("Sistemas")
    
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
            st.markdown("### " + str(dia) + " Dias")
            wr = st.number_input("WR %", 0, 100, 50, key="w"+str(i))
            rt = st.number_input("R/R", 0.0, 50.
