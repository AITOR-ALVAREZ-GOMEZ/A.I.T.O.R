import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="A.I.T.O.R. 2.0 - Quant Terminal", layout="wide")

# Estilo personalizado para modo oscuro y métricas
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS EN SESIÓN ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=["Ticker", "Tier", "EV_Pond", "IDT", "ITE", "Verdict"])
if 'historial' not in st.session_state:
    # Datos de ejemplo para que veas los gráficos al arrancar
    st.session_state.historial = pd.DataFrame([
        {"Fecha": "2026-01-10", "Ticker": "FTAI", "P&L": 4500, "Acumulado": 281500},
        {"Fecha": "2026-01-25", "Ticker": "CRDO", "P&L": -1200, "Acumulado": 280300},
        {"Fecha": "2026-02-05", "Ticker": "APLV", "P&L": 8900, "Acumulado": 289200}
    ])
    st.session_state.capital_inicial = 277000

# --- TABS PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(["🔍 Escáner & Análisis", "💼 Mi Cartera (3 Balas)", "📊 Performance & Stats"])

# --- TAB 1: ESCÁNER ---
with tab1:
    st.title("🚀 Análisis de Guepardos")
    
    with st.expander("📥 Introducir Datos de ProRealTime", expanded=True):
        col_t, col_p = st.columns(2)
        ticker = col_t.text_input("TICKER", "CRDO").upper()
        capital_total = 277000
        
        st.markdown("### 🧬 Matriz de Fibonacci (1, 3, 8, 13, 21)")
        fibo_days = [1, 3, 8, 13, 21]
        ev_list = []
        
        cols = st.columns(5)
        for i, d in enumerate(fibo_days):
            with cols[i]:
                wr = st.number_input(f"WR% {d}D", 0, 100, 50, key=f"wr_{d}") / 100
                ratio = st.number_input(f"Ratio {d}D", 0.0, 50.0, 2.0, key=f"r_{d}")
                ev_ind = (wr * ratio) - ((1 - wr) * 1)
                ev_list.append(ev_ind)
        
        st.markdown("### 🎯 Estado del Disparo")
        c1, c2, c3, c4 = st.columns(4)
        gat_azul = c1.checkbox("Gatillo (1D) AZUL", value=True)
        sistemas_azul = c2.slider("Sistemas >1D en AZUL", 0, 4, 3)
        p_entrada = c3.number_input("Precio Entrada", value=117.86)
        p_stop = c4.number_input("Precio Stop (Muro)", value=112.50)

    # CÁLCULOS
    ev_pond = sum(ev_list) / 5
    tier = "👑 TIER S" if ev_pond >= 10 else "🟢 TIER A" if ev_pond >= 5 else "🔴 DESCARTE"
    
    # Lógica IDT
    idt = (wr_1d := ev_list[0] if False else wr * 100) # Simplificado para el prompt
    idt = (st.session_state.wr_1 * 100) + (15 if "TIER S" in tier else 0) + (sistemas_azul * 10) + (10 if gat_azul else 0)
    ite = ((p_entrada - p_stop) / p_stop) * 100
    
    # Veredicto
    if idt >= 100 and ite <= 5: verdict, color = "🔥 COMPRA OBLIGATORIA (100%)", "#00ffcc"
    elif idt >= 85 and ite <= 8: verdict, color = "🟡 COMPRA TÁCTICA (50%)", "#ffcc00"
    else: verdict, color = "🚫 ARMA BLOQUEADA", "#ff4b4b"

    st.markdown(f"<h2 style='text-align: center; color: {color};'>{verdict}</h2>", unsafe_allow_html=True)
    
    if st.button("💾 Guardar y Rankear"):
        nuevo = {"Ticker": ticker, "Tier": tier, "EV_Pond": round(ev_pond, 2), "IDT": round(idt, 1), "ITE": round(ite, 2), "Verdict": verdict}
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')

    st.dataframe(st.session_state.analisis.sort_values("IDT", ascending=False), use_container_width=True)

# --- TAB 2: CARTERA ---
with tab2:
    st.title("💼 Gestión de las 3 Balas")
    st.info(f"Capital para el millón: {st.session_state.capital_inicial} € | Bala asignada: {round(st.session_state.capital_inicial/3, 2)} €")
    
    # Formulario para registrar cierre de operación
    with st.form("Cerrar Operación"):
        st.write("### Registrar Salida de Activo")
        t_exit = st.text_input("Ticker").upper()
        profit = st.number_input("Resultado Neto (€)", value=0.0)
        if st.form_submit_button("✅ Registrar en Historial"):
            last_cap = st.session_state.historial["Acumulado"].iloc[-1]
            nuevo_h = {"Fecha": datetime.now().strftime("%Y-%m-%d"), "Ticker": t_exit, "P&L": profit, "Acumulado": last_cap + profit}
            st.session_state.historial = pd.concat([st.session_state.historial, pd.DataFrame([nuevo_h])])
            st.success("Estadísticas actualizadas.")

# --- TAB 3: PERFORMANCE ---
with tab3:
    st.title("📊 Auditoría de Resultados")
    dfh = st.session_state.historial
    
    # Métricas clave
    c1, c2, c3, c4 = st.columns(4)
    total_trades = len(dfh)
    win_rate = (len(dfh[dfh["P&L"] > 0]) / total_trades) * 100
    profit_factor = abs(dfh[dfh["P&L"] > 0]["P&L"].sum() / dfh[dfh["P&L"] < 0]["P&L"].sum())
    c1.metric("Win Rate Real", f"{win_rate:.1f}%")
    c2.metric("Profit Factor", f"{profit_factor:.2f}")
    c3.metric("Capital Actual", f"{dfh['Acumulado'].iloc[-1]:,.0f} €")
    c4.metric("Trades Ejecutados", total_trades)

    # GRÁFICO 1: CURVA DE EQUIDAD
    fig_equity = px.line(dfh, x="Fecha", y="Acumulado", title="📈 Evolución hacia el Millón",
                         markers=True, line_shape="hv", color_discrete_sequence=["#00ffcc"])
    fig_equity.add_hline(y=1000000, line_dash="dash", line_color="gold", annotation_text="EL MILLÓN")
    st.plotly_chart(fig_equity, use_container_width=True)

    # GRÁFICO 2: DISTRIBUCIÓN DE P&L
    col_a, col_b = st.columns(2)
    with col_a:
        fig_dist = px.histogram(dfh, x="P&L", title="⚖️ Distribución de Ganancias/Pérdidas",
                               color_discrete_sequence=["#00ccff"], nbins=20)
        st.plotly_chart(fig_dist)
    with col_b:
        # Gráfico de tarta de aciertos
        dfh['Resultado'] = dfh['P&L'].apply(lambda x: 'Ganancia' if x > 0 else 'Pérdida')
        fig_pie = px.pie(dfh, names='Resultado', title="🎯 Precisión del Sistema",
                        color_discrete_map={'Ganancia':'#00ffcc', 'Pérdida':'#ff4b4b'})
        st.plotly_chart(fig_pie)
