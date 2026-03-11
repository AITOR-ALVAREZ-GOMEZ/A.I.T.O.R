import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 7.0 - Fractal Master", layout="wide")

# Lista Maestra de tus Días Fibonacci/Fractales
DIAS_DISPONIBLES = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]

# Columnas para el Ranking Eterno
COL_BASE = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto"]
# Guardamos: Dia, WR y Ratio para cada uno de los 5 sistemas seleccionados
COL_SISTEMAS = []
for i in range(1, 6):
    COL_SISTEMAS.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])
COL_TOTALES = COL_BASE + COL_SISTEMAS

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    existing_data = conn.read(worksheet="Sheet1", ttl=5)
except:
    existing_data = pd.DataFrame(columns=COL_TOTALES)

# --- 2. SIDEBAR: CONFIGURACIÓN FRACTAL ---
st.sidebar.header("🔍 Buscador")
ticker_input = st.sidebar.text_input("TICKER", "MSFT").upper()

# ... (Lógica de auto-detección y Yahoo Finance igual que V6.1) ...
nombre_emp, p_mercado, f_growth = "Buscando...", 0.0, 0.0
try:
    stock = yf.Ticker(ticker_input); inf = stock.info
    nombre_emp = inf.get('longName', 'Ticker no detectado')
    p_mercado = inf.get('regularMarketPrice', inf.get('previousClose', 0.0))
    f_growth = inf.get('earningsGrowth', 0) or 0
except: pass

st.sidebar.subheader(f"🏢 {nombre_emp}")
st.sidebar.markdown("---")

# 3. FILTROS LIBRO BLANCO (DINÁMICOS)
st.sidebar.header("📚 Calidad (Libro Blanco)")
auto_eps = "Explosivo (>25%)" if f_growth > 0.25 else "Alto (>15%)" if f_growth > 0.15 else "Medio (>10%)" if f_growth > 0.10 else "Bajo (<10%)"
eps_choice = st.sidebar.selectbox("Expectativa Crecimiento", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], 
                                 index=["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"].index(auto_eps))

p_eps_idt = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_choice]
c_inst = st.sidebar.checkbox("Institucional (Smart Money)", value=True)
c_sector = st.sidebar.checkbox("Líder (Tendencia)", value=True)

plus_calidad_idt = p_eps_idt + (10 if c_inst else 0) + (10 if c_sector else 0)
plus_ev_final = plus_calidad_idt / 7 

st.sidebar.header("🎯 Ejecución")
p_gatillo = st.sidebar.number_input("Precio Gatillo $", value=float(p_mercado))
p_entrada = st.sidebar.number_input("Precio Compra $", value=float(p_mercado))

# --- NUEVO: SELECCIÓN DINÁMICA DE SISTEMAS ---
st.sidebar.header("🧬 Configuración de Sistemas")
st.sidebar.caption("Elige tus 5 marcos temporales Fibonacci:")
sistemas_elegidos = []
default_fibs = [1, 3, 8, 14, 21]

for i in range(5):
    s_dia = st.sidebar.selectbox(f"Sistema {i+1}", DIAS_DISPONIBLES, 
                                 index=DIAS_DISPONIBLES.index(default_fibs[i]) if default_fibs[i] in DIAS_DISPONIBLES else 0,
                                 key=f"select_s{i}")
    sistemas_elegidos.append(s_dia)

# 4. INTERFAZ PRINCIPAL
tab1, tab2 = st.tabs(["🔍 Escáner Fractal", "📊 Auditoría & Ranking"])

with tab1:
    st.title(f"🚀 Análisis Cuantitativo: {ticker_input}")
    ev_list, wr_list, ratio_list, estados = [], [], [], []
    cols = st.columns(5)
    
    for i, s_v in enumerate(sistemas_elegidos):
        with cols[i]:
            st.markdown(f"### {s_v} Días")
            wr = st.number_input(f"WR% {s_v}D", 0, 100, 50, key=f"wr_{i}")
            ratio = st.number_input(f"Ratio {s_v}D", 0.0, 100.0, 2.0, key=f"rt_{i}")
            est = st.radio(f"Estado {s_v}D", ["🔴 Venta", "🔵 Compra"], key=f"es_{i}")
            
            # $EV = (WR \times Ratio) - ((1 - WR) \times 1)$
            wr_f = wr / 100
            ev_i = round((wr_f * ratio) - ((1 - wr_f) * 1), 2)
            
            ev_list.append(ev_i); wr_list.append(wr); ratio_list.append(ratio); estados.append(est)
            st.metric(f"EV {s_v}D", f"{ev_i}")

    # Cálculos Finales
    ev_total = round((sum(ev_list) / 5) + plus_ev_final, 2)
    
    dist_perc = ((p_entrada - p_gatillo) / p_gatillo) * 100 if p_gatillo > 0 else 0
    penalizacion = 30 if dist_perc > 5.0 else 10 if dist_perc >= 2.0 else 0
    
    p_estruc = sum(1 for e in estados[1:] if "🔵" in e) * 10
    p_senal = 10 if "🔵" in estados[0] else 0
    idt_total = wr_list[0] + plus_calidad_idt + p_estruc + p_senal - penalizacion

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("EV TOTAL", f"{ev_total}", f"+{plus_ev_final:.2f} Calidad")
        st.write(f"👉 **Tier {'S' if ev_total >= 10 else 'A' if ev_total >= 5 else 'Descarte'}**")
    with m2:
        st.metric("IDT PUNTOS", f"{idt_total} pts")
    with m3:
        p_stop = st.number_input("Precio Stop $", value=float(p_entrada * 0.95))
        ite = round(((p_entrada - p_stop) / p_stop) * 100, 2)
        st.metric("RIESGO ITE", f"{ite}%")

    # Veredicto
    if ev_total < 5 or ite > 8: v_txt, v_col = "🚫 NO OPERABLE", "#ff4b4b"
    elif idt_total >= 100 and ite <= 5: v_txt, v_col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
    elif idt_total >= 85 and ite <= 8: v_txt, v_col = "🟡 COMPRA TÁCTICA", "#ffcc00"
    else: v_txt, v_col = "🚫 ARMA BLOQUEADA", "#ff4b4b"
    st.markdown(f"<h2 style='text-align:center; color:{v_col};'>{v_txt}</h2>", unsafe_allow_html=True)

    # BOTÓN DE GUARDADO DINÁMICO
    if st.button("💾 GUARDAR AUDITORÍA FRACTAL EN DRIVE"):
        t_label = "👑 TIER S" if ev_total >= 10 else "🟢 TIER A" if ev_total >= 5 else "🔴 DESCARTE"
        
        # Construimos el diccionario de datos dinámicamente
        data_dict = {
            "Ticker": ticker_input, "Tier": t_label, "EV_Total": ev_total,
            "IDT_Puntos": idt_total, "ITE_Porc": ite, "Veredicto": v_txt
        }
        # Añadimos los 5 sistemas elegidos y sus resultados
        for i in range(5):
            data_dict[f"S{i+1}_Dias"] = sistemas_elegidos[i]
            data_dict[f"W{i+1}"] = wr_list[i]
            data_dict[f"R{i+1}"] = ratio_list[i]
        
        new_row = pd.DataFrame([data_dict])
        updated_df = pd.concat([existing_data, new_row], ignore_index=True).drop_duplicates('Ticker', keep='last')
        conn.update(worksheet="Sheet1", data=updated_df)
        st.success(f"¡Análisis fractal de {ticker_input} guardado!")

with tab2:
    st.subheader("📊 Histórico de Operaciones Dinámicas")
    st.dataframe(existing_data.sort_values("EV_Total", ascending=False), use_container_width=True)
