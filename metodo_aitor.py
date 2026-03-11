import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime

st.set_page_config(page_title="AITOR 14.1", layout="wide")

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
            rt = st.number_input("R/R", 0.0, 50.0, 2.0, key="r"+str(i))
            es = st.radio("Señal", ["Venta", "Compra"], key="e"+str(i))
            
            wr_dec = wr / 100.0
            ev_i = round((wr_dec * rt) - ((1.0 - wr_dec) * 1.0), 2)
            
            l_ev.append(ev_i)
            l_wr.append(wr)
            l_rt.append(rt)
            l_es.append(es)
            
            st.metric("EV " + str(dia) + "D", str(ev_i))

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
    
    # 1. EV TOTAL
    with r_cols[0]:
        st.subheader("EV Total")
        st.caption("Esperanza: Calidad + Ventaja")
        st.metric("SCORE", str(ev_tot), "+" + str(round(ev_plus, 2)))
        
        if ev_tot >= 10: 
            r1_c = "color:#fff; background:#34c759;"
            r1_t = "TIER S (Elite)"
        elif ev_tot >= 5: 
            r1_c = "color:#fff; background:#2b8af7;"
            r1_t = "TIER A (Bueno)"
        else: 
            r1_c = "color:#fff; background:#ff3b30;"
            r1_t = "Descarte (<5)"
            
        st.markdown("<div class='apple-rank-tag' style='" + r1_c + "'>" + r1_t + "</div>", unsafe_allow_html=True)
    
    # 2. IDT PUNTOS
    with r_cols[1]:
        st.subheader("Fuerza IDT")
        st.caption("Disparo Tactico")
        st.metric("PUNTOS", str(idt) + " pts")
        
        if idt >= 100: 
            r2_c = "color:#fff; background:#1d1d1f;"
            r2_t = "OBLIGATORIA (>100)"
        elif idt >= 85: 
            r2_c = "color:#fff; background:#ff9500;"
            r2_t = "TACTICA (85-99)"
        else: 
            r2_c = "color:#fff; background:#ff3b30;"
            r2_t = "BLOQUEADA (<85)"
            
        st.markdown("<div class='apple-rank-tag' style='" + r2_c + "'>" + r2_t + "</div>", unsafe_allow_html=True)

    # 3. ITE %
    with r_cols[2]:
        st.subheader("Tension ITE")
        st.caption("Riesgo al Stop")
        st.metric("RIESGO", str(ite) + "%")
        
        if ite <= 5: 
            r3_c = "color:#fff; background:#34c759;"
            r3_t = "OPTIMO (<5%)"
        elif ite <= 8: 
            r3_c = "color:#fff; background:#ff9500;"
            r3_t = "LIMITE (5-8%)"
        else: 
            r3_c = "color:#fff; background:#ff3b30;"
            r3_t = "NO OPERABLE"
            
        st.markdown("<div class='apple-rank-tag' style='" + r3_c + "'>" + r3_t + "</div>", unsafe_allow_html=True)

    # --- CALCULADORA DE RIESGO ---
    pct_riesgo = r_pct / 100.0
    p_max = CAPITAL * pct_riesgo
    dif_p = p_buy - p_sl
    n_tit = 0
    if dif_p > 0:
        n_tit = int(p_max / dif_p)
    inv_t = n_tit * p_buy

    st.markdown("---")
    st.subheader("Ejecucion (Capital: 277k)")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Riesgo Max", str(int(p_max)) + " EUR")
    c2.metric("Acciones", str(int(n_tit)) + " titulos")
    c3.metric("Posicion", str(int(inv_t)) + " EUR")

    # --- VERDICTO FINAL ---
    if ev_tot < 5 or ite > 8:
        v_c = "color:#fff; background:#ff3b30;"
        v_t = "NO VIABLE"
    elif idt >= 100 and ite <= 5:
        v_c = "color:#fff; background:#1d1d1f;"
        v_t = "COMPRA OBLIGATORIA"
    elif idt >= 85 and ite <= 8:
        v_c = "color:#fff; background:#ff9500;"
        v_t = "COMPRA TACTICA"
    else:
        v_c = "color:#fff; background:#ff3b30;"
        v_t = "ARMA BLOQUEADA"
        
    tag = "<div style='text-align:center;'><div class='apple-rank-tag' "
    tag += "style='" + v_c + " font-size:1.3rem;'>" + v_t + "</div></div>"
    st.markdown("<br>" + tag, unsafe_allow_html=True)

    # --- GUARDAR ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Guardar en Nube"):
        d_sav = {
            "Ticker": ticker, "Tier": v_t, "EV_Total": ev_tot, 
            "IDT_Puntos": idt, "ITE_Porc": ite, "Veredicto": v_t, 
            "Acciones": n_tit, "Inversion": inv_t
        }
        for j in range(5):
            d_sav["S" + str(j+1) + "_Dias"] = s_elegidos[j]
            d_sav["W" + str(j+1)] = l_wr[j]
            d_sav["R" + str(j+1)] = l_rt[j]
            
        new_row = pd.DataFrame([d_sav])
        df_upd = pd.concat([df_datos, new_row], ignore_index=True).drop_duplicates("Ticker", keep="last")
        conn.update(worksheet="Sheet1", data=df_upd)
        st.success("Guardado ok.")

with tab2:
    st.dataframe(df_datos.sort_values("EV_Total", ascending=False), use_container_width=True)
