import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 16.0", layout="wide")

# --- CSS ESTILO APPLE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #f5f5f7;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1d1d1f;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(0,0,0,0.05) !important;
    }
    h1, h2, h3, h1 *, h2 *, h3 * {
        color: #1d1d1f !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 15px 20px;
        min-height: 140px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.03);
    }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        color: #1d1d1f !important;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
        color: #86868b !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stTextInput input, .stNumberInput input, [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
    }
    .stButton>button {
        background: linear-gradient(180deg, #2b8af7 0%, #0071e3 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(0, 113, 227, 0.3) !important;
    }
    .rank-box {
        display: flex;
        gap: 6px;
        margin-top: 12px;
        flex-wrap: wrap;
    }
    .tag-on {
        border-radius: 12px;
        padding: 6px 10px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #fff;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .tag-off {
        border-radius: 12px;
        padding: 6px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #8e8e93;
        border: 1px solid #d2d2d7;
        background: #fff;
    }
</style>
""", unsafe_allow_html=True)

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
A_ACTUAL = datetime.datetime.now().year

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6):
    COL_DB.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df_datos = conn.read(worksheet="Sheet1", ttl=5)
except:
    df_datos = pd.DataFrame(columns=COL_DB)

# --- MENÚ DE NAVEGACIÓN PRINCIPAL ---
st.sidebar.title("Navegación")
modo_app = st.sidebar.radio("Ir a:", ["Escáner Cuántico", "Mi Cartera Activa"])
st.sidebar.markdown("---")

# =====================================================================
# MODO 1: ESCÁNER CUÁNTICO (Tu código original intacto)
# =====================================================================
if modo_app == "Escáner Cuántico":

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
        st.sidebar.info(f"{A_ACTUAL}: {e1:.2f} $\n\n{A_ACTUAL + 1}: {e2:.2f} $\n\n{A_ACTUAL + 2}: {e3:.2f} $")

    ops = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]

    if prev_1y > 0.25: i_auto = 3
    elif prev_1y > 0.15: i_auto = 2
    elif prev_1y > 0.10: i_auto = 1
    else: i_auto = 0

    v_eps = st.sidebar.selectbox("Crecimiento EPS", ops, index=i_auto)
    dict_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}
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

    # --- MEMORIA HISTORICA A.I.T.O.R. ---
    d_defs = [1, 3, 8, 14, 21]
    w_defs = [50, 50, 50, 50, 50]
    r_defs = [2.0, 2.0, 2.0, 2.0, 2.0]

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
            except:
                pass

    # --- DASHBOARD ---
    tab1, tab2 = st.tabs(["Escaner Cuantico", "Auditoria"])

    with tab1:
        st.title("Analisis: " + ticker)
        st.sidebar.header("Sistemas")
        
        s_elegidos, l_ev, l_wr, l_rt, l_es = [], [], [], [], []
        cols = st.columns(5)
        
        for i in range(5):
            with cols[i]:
                st.markdown(f"### {d_defs[i]} D")
                idx_d = DIAS.index(d_defs[i])
                s_val = st.selectbox("S", DIAS, index=idx_d, key=f"d{i}", label_visibility="collapsed")
                wr = st.number_input("WR %", 0, 100, w_defs[i], key=f"w{i}")
                rt = st.number_input("R/R", 0.0, 50.0, r_defs[i], key=f"r{i}")
                es = st.radio("Señal", ["Venta", "Compra"], key=f"e{i}")
                
                wr_dec = wr / 100.0
                ev_i = round((wr_dec * rt) - ((1.0 - wr_dec) * 1.0), 2)
                
                s_elegidos.append(s_val)
                l_ev.append(ev_i)
                l_wr.append(wr)
                l_rt.append(rt)
                l_es.append(es)
                
                st.metric("EV " + str(s_val) + "D", str(ev_i))

        # --- RESULTADOS FINALES ---
        ev_tot = round((sum(l_ev) / 5.0) + ev_plus, 2)
        
        ite = 0.0
        if p_buy > 0:
            ite = round(((p_buy - p_sl) / p_buy) * 100.0, 2)
            
        p_estr = sum(10 for e in l_es[1:] if e == "Compra")
        p_sen = 10 if l_es[0] == "Compra" else 0
        penal = 30 if ite > 8 else 0
        
        idt = l_wr[0] + bono + p_estr + p_sen - penal

        st.markdown("---")
        r_cols = st.columns(3)
        
        # 1. EV TOTAL (TABS APPLE)
        with r_cols[0]:
            st.subheader("EV Total")
            st.metric("SCORE", str(ev_tot), f"+{ev_plus:.2f}")
            st.caption("Esperanza: Calidad + Ventaja")
            
            h_ev = "<div class='rank-box'>"
            if ev_tot >= 10:
                h_ev += "<div class='tag-on' style='background:#34c759;'>TIER S</div><div class='tag-off'>TIER A</div><div class='tag-off'>DESCARTE</div>"
            elif ev_tot >= 5:
                h_ev += "<div class='tag-off'>TIER S</div><div class='tag-on' style='background:#2b8af7;'>TIER A</div><div class='tag-off'>DESCARTE</div>"
            else:
                h_ev += "<div class='tag-off'>TIER S</div><div class='tag-off'>TIER A</div><div class='tag-on' style='background:#ff3b30;'>DESCARTE</div>"
            h_ev += "</div>"
            st.markdown(h_ev, unsafe_allow_html=True)
        
        # 2. IDT PUNTOS (TABS APPLE)
        with r_cols[1]:
            st.subheader("Fuerza IDT")
            st.metric("PUNTOS", str(idt) + " pts")
            st.caption
