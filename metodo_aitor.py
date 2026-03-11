import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. CONFIGURACION Y ESTILO APPLE (IOS / MACOS) ---
st.set_page_config(page_title="AITOR 13.0 Pro", layout="wide")

st.markdown("""
<style>
    /* Tipografia de Apple y fondo gris suave */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp { 
        background-color: #f5f5f7; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1d1d1f;
    }
    
    /* Panel lateral efecto cristal (Glassmorphism) */
    [data-testid="stSidebar"] { 
        background-color: rgba(255, 255, 255, 0.7) !important; 
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(0,0,0,0.05) !important;
    }
    
    /* Titulos limpios y redondeados */
    h1, h2, h3, h1 *, h2 *, h3 * { 
        color: #1d1d1f !important; 
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* EFECTO GLOBO: Cajas que flotan al pasar el raton */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 15px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.03);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 24px rgba(0,0,0,0.08);
    }
    
    /* Numeros grandes de los resultados */
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * { 
        color: #1d1d1f !important; 
        font-weight: 700 !important; 
        font-size: 2.2rem !important;
    }
    
    /* Textos descriptivos pequeños debajo de los numeros */
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { 
        color: #86868b !important; 
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Cajas de entrada de texto redondeadas (Perfiladas) */
    .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important;
        color: #1d1d1f !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        transition: all 0.2s;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);
    }
    
    /* Efecto al hacer clic en una caja de texto (anillo azul Apple) */
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #0071e3 !important;
        box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.2) !important;
    }
    
    /* Desplegables redondeados */
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
    }
    
    /* BOTONES TECNOLOGICOS APPLE (Azul brillante y redondeado) */
    .stButton>button {
        background: linear-gradient(180deg, #2b8af7 0%, #0071e3 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(0, 113, 227, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(0, 113, 227, 0.5) !important;
    }
    
    /* Ajuste color de los textos base para que sean grises oscuros, no negros puros */
    .stApp p, .stApp label, .stApp span, .stApp div[data-testid="stMarkdownContainer"] {
        color: #1d1d1f !important;
    }
    
    /* Cajas de informacion (Alertas) */
    .stAlert {
        border-radius: 16px !important;
        border: none !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
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
st.sidebar.header("🔍 Buscador de Activos")
ticker = st.sidebar.text_input("Simbolo (Ticker)", "MSFT").upper()

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

# --- 3. CALIDAD ---
st.sidebar.header("📊 Calidad (Libro Blanco)")

if prev_1y > 0 and eps_base > 0:
    st.sidebar.markdown("### Proyeccion de Beneficios (3Y)")
    e1 = eps_base * (1 + prev_1y)
    e2 = e1 * (1 + prev_1y)
    e3 = e2 * (1 + prev_1y)
    st.sidebar.info(
        "📅 " + str(A_ACTUAL) + ": " + str(round(e1, 2)) + " $\n\n" +
        "📅 " + str(A_ACTUAL + 1) + ": " + str(round(e2, 2)) + " $\n\n" +
        "📅 " + str(A_ACTUAL + 2) + ": " + str(round(e3, 2)) + " $"
    )
elif prev_1y > 0:
    st.sidebar.success("Crecimiento estimado: " + str(round(prev_1y*100, 1)) + "%")

ops = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]

if prev_1y > 0.25: i_auto = 3
elif prev_1y > 0.15: i_auto = 2
elif prev_1y > 0.10: i_auto = 1
else: i_auto = 0

v_eps = st.sidebar.selectbox("Crecimiento EPS", ops, index=i_auto)
dict_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}
pts_eps = dict_eps[v_eps]

c_inst = st.sidebar.checkbox("Manos Fuertes Institucionales", value=True)
c_sect = st.sidebar.checkbox("Lider de Sector", value=True)

bono = pts_eps + (10 if c_inst else 0) + (10 if c_sect else 0)
ev_plus = bono / 7.0

# --- 4. RIESGO ---
st.sidebar.header("🛡️ Gestion de Capital")
r_pct = st.sidebar.slider("Riesgo por Operacion (%)", 0.5, 3.0, 1.0, step=0.5)
p_buy = st.sidebar.number_input("Precio de Compra $", value=float(p_merc))
p_sl = st.sidebar.number_input("Stop Loss $", value=float(p_buy * 0.95))

# --- 5. DASHBOARD ---
tab1, tab2 = st.tabs(["✨ Escaner Cuantico", "📁 Auditoria"])

with tab1:
    st.title("Estacion de Analisis: " + ticker)
    st.sidebar.header("🧬 Sistemas Fractales")
    
    d_defs = [1, 3, 8, 14, 21]
    s_elegidos = []
    for i in range(5):
        i_def = DIAS.index(d_defs[i])
        s_val = st.sidebar.selectbox("Sistema " + str(i+1), DIAS, index=i_def, key="d"+str(i))
        s_elegidos.append(s_val)

    l_ev, l_wr, l_rt, l_es = [], [], [], []
    cols = st.columns(5)
    
    for i in range(5):
        dia = s_elegidos[i]
        with cols[i]:
            st.markdown("### " + str(dia) + " Dias")
            wr = st.number_input("Win Rate %", 0, 100, 50, key="w"+str(i))
            rt = st.number_input("Ratio R/R", 0.0, 50.0, 2.0, key="r"+str(i))
            es = st.radio("Señal", ["Venta", "Compra"], key="e"+str(i), horizontal=True)
            
            wr_d = wr / 100.0
            ev_i = round((wr_d * rt) - ((1.0 - wr_d) * 1.0), 2)
            
            l_ev.append(ev_i)
            l_wr.append(wr)
            l_rt.append(rt)
            l_es.append(es)
            
            st.metric("Esperanza " + str(dia) + "D", str(ev_i))

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
        st.subheader("Puntuacion EV")
        st.metric("SCORE TOTAL", str(ev_tot), "+" + str(round(ev_plus, 2)) + " Bonus Calidad")
    with r2:
        st.subheader("Fuerza IDT")
        st.metric("PUNTOS TACTICOS", str(idt) + " pts")
    with r3:
        st.subheader("Tension ITE")
        st.metric("RIESGO", str(ite) + "%")

    # --- CALCULADORA 277k ---
    p_max = CAPITAL * (r_pct / 100.0)
    dif_p = p_buy - p_sl
    
    n_tit = 0
    if dif_p > 0:
        n_tit = int(p_max / dif_p)
        
    inv_t = n_tit * p_buy

    st.markdown("---")
    st.subheader("Ejecucion Recomendada (Capital: 277.000 EUR)")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Capital en Riesgo", str(int(p_max)) + " EUR")
    with c2:
        st.metric("Acciones a Comprar", str(int(n_tit)) + " titulos")
    with c3:
        st.metric("Tamaño Posicion", str(int(inv_t)) + " EUR")

    # --- VERDICTO ---
    if ev_tot < 5 or ite > 8:
        v_txt, v_col = "Operacion No Viable", "#ff3b30" # Rojo Apple
    elif idt >= 100 and ite <= 5:
        v_txt, v_col = "Compra Obligatoria", "#34c759" # Verde Apple
    elif idt >= 85 and ite <= 8:
        v_txt, v_col = "Compra Tactica", "#ff9500" # Naranja Apple
    else:
        v_txt, v_col = "Arma Bloqueada", "#ff3b30"
        
    st.markdown("<h2 style='text-align:center; color:" + v_col + "; margin-top: 30px; font-weight: 700;'>" + v_txt + "</h2>", unsafe_allow_html=True)

    # --- GUARDAR ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Sincronizar con iCloud (Sheets)"):
        tier = "TIER S" if ev_tot >= 10 else "TIER A" if ev_tot >= 5 else "DESC"
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
        st.success("Guardado y Sincronizado correctamente.")

with tab2:
    st.dataframe(df_datos.sort_values("EV_Total", ascending=False), use_container_width=True)
