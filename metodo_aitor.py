import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="A.I.T.O.R. 9.0 - Año a Año", layout="wide")

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6):
    COL_DB.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df_datos = conn.read(worksheet="Sheet1", ttl=5)
except:
    df_datos = pd.DataFrame(columns=COL_DB)

# --- 2. BUSCADOR Y CÁLCULO AÑO A AÑO ---
st.sidebar.header("🔍 Buscador")
ticker = st.sidebar.text_input("TICKER", "MSFT").upper()

nom_emp = "Buscando..."
p_merc = 0.0
prev_1y = 0.0

if ticker != "":
    try:
        stock = yf.Ticker(ticker)
        nom_emp = stock.info.get('longName', 'Desconocido')
        p_merc = stock.info.get('regularMarketPrice', 0.0)
        
        # CÁLCULO REAL AÑO A AÑO: (Previsión Próximo Año - Beneficio Año Pasado) / Beneficio Año Pasado
        t_eps = stock.info.get('trailingEps', 0)
        f_eps = stock.info.get('forwardEps', 0)
        
        if t_eps > 0 and f_eps > t_eps:
            prev_1y = (f_eps - t_eps) / t_eps
        else:
            prev_1y = stock.info.get('revenueGrowth', 0) # Fallback seguro
            
    except:
        pass

st.sidebar.subheader(f"🏢 {nom_emp}")
st.sidebar.markdown("---")

# --- 3. CALIDAD (LIBRO BLANCO) ---
st.sidebar.header("📚 Calidad (Libro Blanco)")
if prev_1y > 0:
    st.sidebar.success(f"🎯 Previsión Año a Año: {prev_1y*100:.1f}%")

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
    st.title(f"🚀 Análisis: {ticker}")
    st.sidebar.header("🧬 Sistemas")
    
    d_defs = [1, 3, 8, 14, 21]
    s_elegidos = []
    for i in range(5):
        i_def = DIAS.index(d_defs[i])
        s_val = st.sidebar.selectbox(f"S{i+1}", DIAS, index=i_def, key=f"d{i}")
        s_elegidos.append(s_val)

    l_ev, l_wr, l_rt, l_es = [], [], [], []
    cols = st.columns(5)
    
    for i in range(5):
        dia = s_elegidos[i]
        with cols[i]:
            st.markdown(f"### {dia} D")
            wr = st.number_input(f"WR% {dia}D", 0, 100, 50, key=f"w{i}")
            rt = st.number_input(f"Ratio {dia}D", 0.0, 50.0, 2.0, key=f"r{i}")
            es = st.radio("Est.", ["🔴", "🔵"], key=f"e{i}", horizontal=True)
            
            wr_d = wr / 100.0
            ev_i = round((wr_d * rt) - ((1.0 - wr_d) * 1.0), 2)
            
            l_ev.append(ev_i)
            l_wr.append(wr)
            l_rt.append(rt)
            l_es.append(es)
            
            st.metric(f"EV {dia}D", f"{ev_i}")

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
    r1.metric("EV TOTAL", f"{ev_tot}", f"+{ev_plus:.2f} Calidad")
    r2.metric("IDT PUNTOS", f"{idt} pts")
    r3.metric("RIESGO ITE", f"{ite}%")

    # --- CALCULADORA 277k ---
    p_max = CAPITAL * (r_pct / 100.0)
    dif_p = p_buy - p_sl
    
    n_tit = 0
    if dif_p > 0:
        n_tit = int(p_max / dif_p)
        
    inv_t = n_tit * p_buy

    st.subheader(f"🧮 Ejecución (Capital: {CAPITAL:,.0f} €)")
    c1, c2, c3 = st.columns(3)
    
    c1
