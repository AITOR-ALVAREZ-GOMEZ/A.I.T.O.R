import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="A.I.T.O.R. 2.9 - Ranking Pro", layout="wide")

# --- INICIALIZAR BASE DE DATOS (En la memoria de la sesión) ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=[
        "Ticker", "Tier", "EV Ponderado", "IDT Puntos", "ITE %", "EPS >25%", "Inst.", "Veredicto"
    ])

# --- BARRA LATERAL: INPUTS ---
st.sidebar.header("🏢 Filtros Libro Blanco")
c_eps = st.sidebar.checkbox("Crecimiento EPS > 25%", value=True)
c_inst = st.sidebar.checkbox("Instituciones Comprando", value=True)
c_sector = st.sidebar.checkbox("Líder de Sector", value=True)
puntos_fund = sum([c_eps, c_inst, c_sector])

ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()
secuencia = [st.sidebar.number_input(f"Día {i+1}", value=v, key=f"d{i}") for i, v in enumerate([1, 3, 8, 14, 21])]

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🔍 Escáner Quant & Fund", "💼 Mi Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Análisis de {ticker_input}")
    
    # 1. ENTRADA DE DATOS POR SISTEMA
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    for i, d in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### {d}D")
            wr = st.number_input(f"WR% {d}D", 0, 100, 50, key=f"w{d}")
            ratio = st.number_input(f"Ratio {d}D", 0.0, 50.0, 2.0, key=f"r{d}")
            estado = st.radio(f"Estado", ["🔴 Venta", "🔵 Compra"], key=f"e{d}")
            ev_ind = ((wr/100) * ratio) - ((1 - wr/100) * 1)
            ev_list.append(ev_ind); wr_list.append(wr); estados.append(estado)

    # --- 2. MOTOR DE VALORACIÓN INTEGRAL ---
    ev_pond = round(sum(ev_list) / 5, 2)
    
    # Tier S si cumple fundamentales Y EV > 4.0
    if puntos_fund == 3 and ev_pond >= 4.0:
        tier_label = "👑 TIER S"
        bonus_tier = 15
    elif puntos_fund >= 2 and ev_pond >= 3.0:
        tier_label = "🟢 TIER A"
        bonus_tier = 0
    else:
        tier_label = "🔴 DESCARTE"
        bonus_tier = -50

    # 3. CÁLCULO IDT
    base_wr = wr_list[0]
    p_estructura = sum(1 for e in estados[1:] if "🔵 Compra" in e) * 10
    p_señal = 10 if "🔵 Compra" in estados[0] else 0
    idt_total = base_wr + bonus_tier + p_estructura + p_señal

    # 4. RIESGO ITE
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    p_in = res3.number_input("Precio Entrada $", value=100.0)
    p_st = res3.number_input("Precio Stop $", value=95.0)
    ite = round(((p_in - p_st) / p_st) * 100, 2) if p_st > 0 else 0

    # --- 5. BOTÓN DE GUARDAR Y RANKING ---
    st.markdown("### 🏆 Ranking de Candidatos")
    
    if st.button("💾 GUARDAR Y ACTUALIZAR RANKING"):
        # Veredicto visual para la tabla
        if idt_total >= 100 and ite <= 5: v_tab = "🔥 COMPRA"
        elif idt_total >= 85 and ite <= 8: v_tab = "🟡 TÁCTICO"
        else: v_tab = "🚫 BLOQUEO"

        nuevo_dato = {
            "Ticker": ticker_input,
            "Tier": tier_label,
            "EV Ponderado": ev_pond,
            "IDT Puntos": idt_total,
            "ITE %": ite,
            "EPS >25%": "✅" if c_eps else "❌",
            "Inst.": "✅" if c_inst else "❌",
            "Veredicto": v_tab
        }
        
        # Añadir a la tabla y eliminar duplicados del mismo ticker (deja el último análisis)
        st.session_state.analisis = pd.concat([
            st.session_state.analisis, 
            pd.DataFrame([nuevo_dato])
        ]).drop_duplicates('Ticker', keep='last')
        
        st.success(f"¡{ticker_input} guardado con {idt_total} puntos!")

    # MOSTRAR TABLA ORDENADA DE MEJOR A PEOR IDT
    if not st.session_state.analisis.empty:
        # Ordenamos por IDT de mayor a menor
        df_ranking = st.session_state.analisis.sort_values(by="IDT Puntos", ascending=False)
        
        # Mostramos la tabla (st.dataframe permite ordenar al usuario también haciendo clic en el título)
        st.dataframe(
            df_ranking, 
            use_container_width=True,
            column_config={
                "IDT Puntos": st.column_config.NumberColumn(format="%d pts"),
                "EV Ponderado": st.column_config.NumberColumn(format="%.2f")
            }
        )
    else:
        st.info("La tabla está vacía. Analiza un valor y dale a Guardar.")

    if st.button("🗑️ Borrar Ranking"):
        st.session_state.analisis = pd.DataFrame(columns=st.session_state.analisis.columns)
        st.rerun()
