import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. CONFIGURACION Y ESTILO APPLE COMPRIMIDO ---
st.set_page_config(page_title="AITOR 13.3 Balanced", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
.stApp {background-color:#f5f5f7; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; color:#1d1d1f;}
[data-testid="stSidebar"] {background-color:rgba(255,255,255,0.7)!important; backdrop-filter:blur(20px)!important; border-right:1px solid rgba(0,0,0,0.05)!important;}
h1,h2,h3,h1 *,h2 *,h3 * {color:#1d1d1f!important; font-weight:700!important; letter-spacing:-0.5px;}
[data-testid="stMetric"] {background-color:#ffffff; border-radius:18px; padding:15px 20px; min-height:140px; box-shadow:0 4px 15px rgba(0,0,0,0.04); border:1px solid rgba(0,0,0,0.03); transition:all 0.3s cubic-bezier(0.25,0.8,0.25,1); display:flex; flex-direction:column; justify-content:center;}
[data-testid="stMetric"]:hover {transform:translateY(-5px) scale(1.02); box-shadow:0 12px 24px rgba(0,0,0,0.08);}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {color:#1d1d1f!important; font-weight:700!important; font-size:2.2rem!important;}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {color:#86868b!important; font-weight:600!important; text-transform:uppercase; letter-spacing:0.5px;}
.stTextInput input, .stNumberInput input {background-color:#ffffff!important; color:#1d1d1f!important; border-radius:12px!important; border:1px solid rgba(0,0,0,0.1)!important; box-shadow:inset 0 1px 2px rgba(0,0,0,0.02);}
[data-baseweb="select"] > div {background-color:#ffffff!important; border-radius:12px!important; border:1px solid rgba(0,0,0,0.1)!important;}
.stButton>button {background:linear-gradient(180deg,#2b8af7 0%,#0071e3 100%)!important; color:white!important; border:none!important; border-radius:20px!important; padding:10px 24px!important; font-weight:600!important; box-shadow:0 4px 14px rgba(0,113,227,0.3)!important; transition:all 0.3s ease!important;}
.stButton>button:hover {transform:translateY(-2px) scale(1.02)!important; box-shadow:0 6px 20px rgba(0,113,227,0.5)!important;}
.stApp p, .stApp label, .stApp span {color:#1d1d1f!important;}
.apple-rank-tag {border-radius:14px; padding:6px 14px; font-weight:600; font-size:0.9rem; display:inline-block; margin-top:10px; box-shadow:0 2px 5px rgba(0,0,0,0.05);}
</style>
""", unsafe_allow_html=True)

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
A_ACTUAL = datetime.datetime.now().year

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6):
    COL_DB.extend(["S" + str(i) + "_Dias", "W" + str(i), "R" + str(i)])

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df_datos = conn.read(worksheet="Sheet1", ttl=5)
except:
    df_datos = pd.DataFrame(columns=COL_DB)

# --- 2. BUSCADOR ---
st.sidebar.header("🔍 Buscador de Activos")
ticker = st.sidebar.text_input("Simbolo (Ticker)", "MSFT").upper()

nom_emp = "Buscando..."
p_merc = 0.0
prev_1y = 0.0
eps_base = 0.0

if ticker != "":
    try:
        stock = yf.Ticker(ticker)
        nom_emp = stock.info.get('
