import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. CONFIGURACION Y ESTILO CYBERPUNK V2 ---
st.set_page_config(page_title="TERMINAL AITOR 12.1", layout="wide")

st.markdown("""
<style>
    /* Fondo principal */
    .stApp { background-color: #050505; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #00ffcc; }
    
    /* Forzar textos pequeños, etiquetas y radio buttons a Cyan claro para que destaquen */
    .stApp p, .stApp label, .stApp span, .stApp div[data-testid="stMarkdownContainer"] { 
        color: #b8fff4 !important; 
        font-family: 'Courier New', Courier, monospace; 
    }
    
    /* Titulos principales */
    h1, h2, h3, h1 *, h2 *, h3 * { 
        color: #00ffcc !important; 
        text-shadow: 0 0 5px #00ffcc; 
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    /* Metricas gigantes */
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * { 
        color: #39ff14 !important; 
        text-shadow: 0 0 8px #39ff14; 
        font-weight: bold; 
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { 
        color: #00ffcc !important; 
    }
    
    /* Cajas de entrada de datos (Inputs) */
    .stTextInput input, .stNumberInput input {
        background-color: #111111 !important;
        color: #39ff14 !important;
        border: 1px solid #00ffcc !important;
        font-weight: bold;
    }
    
    /* Desplegables (Selectbox) */
    [data-baseweb="select"] > div {
        background-color: #111111 !important;
        color: #39ff14 !important;
        border: 1px solid #00ffcc !important;
    }
    
    /* Botones de + y - de los inputs numéricos */
    button[kind="stepUp"], button[kind="stepDown"] {
        background-color: #00ffcc !important;
        color: #000000 !important;
    }
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
st.sidebar.header("> SYSTEM_SEARCH")
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

st.sidebar.subheader("> TARGET: " + nom_emp)
st.sidebar.markdown("---")

# --- 3. CALIDAD ---
st.sidebar.header("> CALIDAD_FUNDAMENTAL")

if prev_1y > 0 and eps_base > 0:
    st.sidebar.markdown("### PROYECCION EPS (3Y)")
    e1 = eps_base * (1 + prev_1y)
    e2 = e1 * (1 + prev_1y)
    e3 = e2 * (1 + prev_1y)
    st.sidebar.info(
        "> " + str(A_ACTUAL) + ": " + str(round(e1, 2)) + " $\n\n" +
        "> " + str(A_ACTUAL + 1) + ": " + str(round(e2, 2)) + " $\n\n" +
        "> " + str(A_ACTUAL + 2) + ": " + str(round(e3, 2)) + " $"
    )
elif prev_1y > 0:
    st.sidebar.success("Prev: " + str(round(prev_1y*100, 1)) + "%")

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

# --- 4. RIESGO ---
st.sidebar.header("> GESTION_RIESGO")
r_pct = st.sidebar.slider("Riesgo Cuenta (%)", 0.5, 3.0, 1.0, step=0.5)
p_buy = st.sidebar.number_input("Precio Compra $", value=float(p_merc))
p_sl = st.sidebar.number_input("Stop Loss $", value=float(p_buy * 0.95))

# --- 5. DASHBOARD ---
tab1, tab2 = st.tabs(["[ ESCANER_CUANTICO ]", "[ AUDITORIA_DATOS ]"])

with tab1:
    st.title(">> TERMINAL_ANALISIS: " + ticker)
    st.sidebar.header("> SISTEMAS_FRACTALES")
    
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
            es = st.radio("Est.", ["Venta", "Compra"], key="e"+str(i), horizontal=True)
            
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
        
    p_estr = sum(10 for e in l_es[1:] if e == "Compra")
    p_sen = 10 if l_es[0] == "Compra" else 0
    penal = 30 if ite > 8 else 0
    
    idt = l_wr[0] + bono + p_estr + p_sen - penal

    st.markdown("---")
    r1, r2, r3 = st.columns(3)
    with r1:
        st.subheader("EV TOTAL")
        st.caption("Esperanza Matematica: Calidad del Activo + Ventaja del Sistema.")
        st.metric("SCORE", str(ev_tot), "+" + str(round(ev_plus, 2)) + " Fundamental")
    with r2:
        st.subheader("IDT PUNTOS")
        st.caption("Indice de Disparo Tactico: Potencia de entrada y estructura.")
        st.metric("POTENCIAL", str(idt) + " pts")
    with r3:
        st.subheader("ITE %")
        st.caption("Indice de Tension Elastica: Distancia al Stop Loss. Control de riesgo.")
        st.metric("RIESGO", str(ite) + "%")

    # --- CALCULADORA 277k ---
    p_max = CAPITAL * (r_pct / 100.0)
    dif_p = p_buy - p_sl
    
    n_tit = 0
    if dif_p > 0:
        n_tit = int(p_max / dif_p)
        
    inv_t = n_tit * p_buy

    st.markdown("---")
    st.subheader("> PROTOCOLO_EJECUCION (CAPITAL_TOTAL: 277,000 EUR)")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("CAPITAL_EN_RIESGO", str(int(p_max)) + " EUR")
    with c2:
        st.metric("TITULOS_A_COMPRAR", str(int(n_tit)) + " ACC")
    with c3:
        st.metric("TAMAÑO_POSICION", str(int(inv_t)) + " EUR")

    # --- VERDICTO ---
    if ev_tot < 5 or ite > 8:
        v_txt, v_col = "[ ERROR: NO OPERABLE ]", "#ff4b4b"
    elif idt >= 100 and ite <= 5:
        v_txt, v_col = "[ ALERTA: COMPRA OBLIGATORIA ]", "#39ff14"
    elif idt >= 85 and ite <= 8:
        v_txt, v_col = "[ AVISO: COMPRA TACTICA ]", "#00ffcc"
    else:
        v_txt, v_col = "[ SISTEMA: ARMA BLOQUEADA ]", "#ff4b4b"
        
    st.markdown("<h2 style='text-align:center; color:" + v_col + ";'>" + v_txt + "</h2>", unsafe_allow_html=True)

    # --- GUARDAR ---
    if st.button("> EJECUTAR_GUARDADO_EN_NUBE"):
        tier = "TIER_S" if ev_tot >= 10 else "TIER_A" if ev_tot >= 5 else "DESC"
        d_sav = {
            "Ticker": ticker, "Tier": tier, "EV_Total": ev_tot, 
            "IDT_Puntos": idt, "ITE_Porc": ite, "Veredicto": v_txt, 
            "Acciones": n_tit, "Inversion": inv_t
        }
        for j in range(5):
            d_sav["S" + str(j+1) + "_Dias"] = s_elegidos[j]
            d_sav["W" + str(j+1)] = l_wr[j]
            d_sav["R" + str(j+1)] = l_rt[j]
            
        new_row = pd.DataFrame([d_sav])
        df_upd = pd.concat([df_datos, new_row], ignore_index=True).drop_duplicates('Ticker', keep='last')
        conn.update(worksheet="Sheet1", data=df_upd)
        st.success("DATOS_ENCRIPTADOS_Y_GUARDADOS_CON_EXITO.")

with tab2:
    st.dataframe(df_datos.sort_values("EV_Total", ascending=False), use_container_width=True)
