import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="A.I.T.O.R. 2.0 - Adaptativo", layout="wide")

# --- BASE DE DATOS ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=["Ticker", "Secuencia", "Tier", "EV_Pond", "IDT", "ITE", "Verdict"])
if 'historial' not in st.session_state:
    st.session_state.historial = pd.DataFrame(columns=["Fecha", "Ticker", "P&L", "Acumulado"])

tab1, tab2, tab3 = st.tabs(["🔍 Escáner Dinámico", "💼 Cartera", "📊 Performance"])

with tab1:
    st.sidebar.header("⚙️ Configuración del Motor")
    ticker = st.sidebar.text_input("TICKER", "CRDO").upper()
    
    st.sidebar.markdown("### 🧬 Define tu Secuencia Fractal")
    # Aquí es donde el usuario define sus propios días
    d1 = st.sidebar.number_input("Gatillo (Día X)", value=1)
    d2 = st.sidebar.number_input("Escudo (Día Y)", value=3)
    d3 = st.sidebar.number_input("Muro (Día Z)", value=8)
    d4 = st.sidebar.number_input("Ancla 1 (Día W)", value=13)
    d5 = st.sidebar.number_input("Ancla 2 (Día K)", value=21)
    
    secuencia_elegida = [d1, d2, d3, d4, d5]
    
    st.title(f"🚀 Análisis de {ticker}")
    st.info(f"Configuración actual: Secuencia {secuencia_elegida}")

    # --- MATRIZ DE ENTRADA DINÁMICA ---
    ev_list = []
    data_points = {}
    
    cols = st.columns(5)
    for i, d in enumerate(secuencia_elegida):
        with cols[i]:
            st.markdown(f"**Sistema {d}D**")
            wr = st.number_input(f"WR% {d}D", 0, 100, 50, key=f"wr_{d}") / 100
            ratio = st.number_input(f"Ratio {d}D", 0.0, 50.0, 2.0, key=f"r_{d}")
            # Esperanza Matemática: $EV = (WR \cdot Ratio) - (FL \cdot 1)$
            ev_ind = (wr * ratio) - ((1 - wr) * 1)
            ev_list.append(ev_ind)
            data_points[d] = wr

    # --- CÁLCULOS ---
    ev_pond = sum(ev_list) / 5
    tier = "👑 TIER S" if ev_pond >= 10 else "🟢 TIER A" if ev_pond >= 5 else "🔴 DESCARTE"
    
    st.markdown("---")
    c1, c2
