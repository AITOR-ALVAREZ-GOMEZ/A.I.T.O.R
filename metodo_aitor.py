import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 7.2 - The Guardian", layout="wide")

DIAS_DISPONIBLES = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
COL_BASE = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto"]
COL_SISTEMAS = []
for i in range(1, 6):
    COL_SISTEMAS.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])
COL_TOTALES = COL_BASE + COL_SISTEMAS

# Conexión GSheets
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    existing_data = conn.read(worksheet="Sheet1", ttl=5)
except:
    existing_data = pd.DataFrame(columns=COL_TOTALES)

# --- 2. BUSCADOR CON FILTRO DE RUIDO ---
st.sidebar.header("🔍 Buscador de Activos")
ticker_input = st.sidebar.text_input("TICKER", "MSFT").upper()

nombre_emp, p_mercado, eps_real, eps_previsto = "Buscando...", 0.0, 0.0, 0.0
try:
    stock = yf.Ticker(ticker_input); inf = stock.info
    nombre_emp = inf.get('longName', 'Ticker no detectado')
    p_mercado = inf.get('regularMarketPrice', inf.get('previousClose', 0.0))
    
    # Diferenciamos Crecimiento Pasado vs Previsión Futura
    eps_real = inf.get('earningsQuarterlyGrowth', 0) or 0 # El 59% suele venir de aquí
    eps_previsto = inf.get('earningsGrowth', 0) or 0     # Esto es más realista (Forward)
    
    # Sensor Inteligente: Si el real es > 50%, probablemente es ruido contable
    valor_final_eps = eps_previsto if eps_previsto > 0 else eps_real
except: pass

st.sidebar.subheader(f"🏢 {nombre_emp}")
st.sidebar.markdown("---")

# 3. FILTROS LIBRO BLANCO (DINÁMICOS)
st.sidebar.header("📚 Calidad (Libro Blanco)")

# Explicación del dato para Aitor
st.sidebar.info(f"📈 Previsión Analistas: {eps_previsto*100:.1f}%\n\n📊 Último Trimestre: {eps_real*100:.1f}%")

auto_eps = "Explosivo (>25%)" if valor_final_eps > 0.25 else "Alto (>15%)" if valor_final_eps > 0.15 else "Medio (>10%)" if valor_final_eps > 0.10 else "Bajo (<10%)"
eps_choice = st.sidebar.selectbox("Expectativa de Crecimiento", 
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

st.sidebar.header("🧬 Configuración Fractal")
sistemas_elegidos = []
default_fibs = [1, 3, 8, 14, 21]
for i in range(5):
    s_dia = st.sidebar.selectbox(f"Sistema {i+1}", DIAS_DISPONIBLES, 
                                 index=DIAS_DISPONIBLES.index(default_fibs[i]), key=f"sel_s{i}")
    sistemas_elegidos.append(s_dia)

# 4. CUERPO PRINCIPAL
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
            est = st.radio(f"Estado", ["🔴 Venta", "🔵 Compra"], key=f"es_{i}")
            # Esperanza Matemática: $EV = (WR \times Ratio) - (SL \times (1-WR))$
            ev_i = round(((wr/100) * ratio) - ((1 - wr/100) * 1), 2)
            ev_list.append(ev_i); wr_list.append(wr); ratio_list.append(ratio); estados.append(est)
            st.metric(f"EV {s_v}D", f"{ev_i}")

    # CÁLCULOS FINALES
    ev_total = round((sum(ev_list) / 5) + plus_ev_final, 2)
    dist_p = ((p_entrada - p_gatillo) / p_gatillo) * 100 if p_gatillo > 0 else 0
    penal = 30 if dist_p > 5.0 else 10 if dist_p >= 2.0 else 0
    idt_total = wr_list[0] + plus_calidad_idt + (sum(1 for e in estados[1:] if "🔵" in e) * 10) + (10 if "🔵" in estados[0] else 0) - penal

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.subheader("🧪 EV TOTAL")
        st.metric("SCORE", f"{ev_total}", f"+{plus_ev_final:.2f} Calidad")
        st.caption("Esperanza Matemática: Ventaja + Calidad.")
        # Marcadores dinámicos
        st.write(f"{'👉 ' if ev_total >= 10 else ''}**Tier S (Élite):** $\ge 10$")
        st.write(f"{'👉 ' if 5 <= ev_total < 10 else ''}**Tier A (Bueno):** $5 - 10$")
        st.write(f"{'👉 ' if ev_total < 5 else ''}**Descarte:** $< 5$")

    with m2:
        st.subheader("🎯 IDT PUNTOS")
        st.metric("POTENCIAL", f"{idt_total} pts")
        st.caption("Índice de Disparo: Potencia de entrada.")
        st.write(f"{'👉 ' if idt_total >= 100 else ''}**Obligatoria:** $\ge 100$")
        st.write(f"{'👉 ' if 85 <= idt_total < 100 else ''}**Táctica:** $85 - 99$")
        st.write(f"{'👉 ' if idt_total < 85 else ''}**Bloqueada:** $< 85$")

    with m3:
        st.subheader("🛡️ ITE %")
        p_stop = st.number_input("Precio Stop $", value=float(p_entrada * 0.95))
        ite = round(((p_entrada - p_stop) / p_stop) * 100, 2) if p_stop > 0 else 0
        st.metric("RIESGO", f"{ite}%")
        st.caption("Tensión Elástica: Distancia al Stop.")
        st.write(f"{'👉 ' if ite <= 5 else ''}**Óptimo:** $\le 5\%$")
        st.write(f"{'👉 ' if 5 < ite <= 8 else ''}**Límite:** $5\% - 8\%$")
        st.write(f"{'👉 ' if ite > 8 else ''}**No Operable:** $> 8\%$")

    # VERDICTO FINAL
    if ev_total < 5: v_txt, v_col = "🚫 NO OPERABLE (Baja Calidad)", "#ff4b4b"
    elif ite > 8: v_txt, v_col = "🚫 NO OPERABLE (Riesgo ITE)", "#ff4b4b"
    elif idt_total >= 100 and ite <= 5: v_txt, v_col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
    elif idt_total >= 85 and ite <= 8: v_txt, v_col = "🟡 COMPRA TÁCTICA", "#ffcc00"
    else: v_txt, v_col = "🚫 ARMA BLOQUEADA (Puntos)", "#ff4b4b"
    st.markdown(f"<h2 style='text-align:center; color:{v_col};'>{v_txt}</h2>", unsafe_allow_html=True)

    if st.button("💾 GUARDAR AUDITORÍA FRACTAL"):
        t_label = "👑 TIER S" if ev_total >= 10 else "🟢 TIER A" if ev_total >= 5 else "🔴 DESCARTE"
        data_dict = {"Ticker": ticker_input, "Tier": t_label, "EV_Total": ev_total, "IDT_Puntos": idt_total, "ITE_Porc": ite, "Veredicto": v_txt}
        for i in range(5):
            data_dict[f"S{i+1}_Dias"] = sistemas_elegidos[i]
            data_dict[f"W{i+1}"] = wr_list[i]
            data_dict[f"R{i+1}"] = ratio_list[i]
        new_row = pd.DataFrame([data_dict])
        updated_df = pd.concat([existing_data, new_row], ignore_index=True).drop_duplicates('Ticker', keep='last')
        conn.update(worksheet="Sheet1", data=updated_df)
        st.success("Guardado en Google Sheets.")

with tab2:
    st.dataframe(existing_data.sort_values("EV_Total", ascending=False), use_container_width=True)
