import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime

st.set_page_config(page_title="AITOR 14.4", layout="wide")

# CSS COMPACTO Y COMPLETO
css = """<style>
.stApp {background-color:#f5f5f7; color:#1d1d1f; font-family:-apple-system, sans-serif;}
[data-testid="stSidebar"] {background:rgba(255,255,255,0.7);}
[data-testid="stMetric"] {background:#fff; border-radius:18px; padding:15px; min-height:140px; box-shadow:0 4px 10px rgba(0,0,0,0.05);}
.rank-box {display:flex; gap:6px; margin-top:12px; flex-wrap:wrap;}
.tag-on {border-radius:12px; padding:6px 10px; font-size:0.75rem; font-weight:700; color:#fff;}
.tag-off {border-radius:12px; padding:6px 10px; font-size:0.75rem; font-weight:600; color:#8e8e93; border:1px solid #d2d2d7; background:#fff;}
</style>"""
st.markdown(css, unsafe_allow_html=True)

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
A_ACT = datetime.datetime.now().year

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6): COL_DB.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

conn = st.connection("gsheets", type=GSheetsConnection)
try: df_datos = conn.read(worksheet="Sheet1", ttl=5)
except: df_datos = pd.DataFrame(columns=COL_DB)

st.sidebar.header("Buscador")
ticker = st.sidebar.text_input("Ticker", "MSFT").upper()

nom_emp, p_merc, prev_1y, eps_base = "Buscando...", 0.0, 0.0, 0.0
if ticker:
    try:
        stock = yf.Ticker(ticker)
        nom_emp = stock.info.get("longName", "Desconocido")
        p_merc = stock.info.get("regularMarketPrice", 0.0)
        eps_base = stock.info.get("trailingEps", 0.0)
        f_eps = stock.info.get("forwardEps", 0.0)
        if eps_base > 0 and f_eps > eps_base: prev_1y = (f_eps - eps_base) / eps_base
        else: prev_1y = stock.info.get("revenueGrowth",
