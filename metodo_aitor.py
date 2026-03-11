import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 20.0", layout="wide")

# --- CSS ESTILO APPLE AVANZADO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
    
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
    /* Estilos para ocultar el metric por defecto de Streamlit en Cartera */
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
    .rank-box { display: flex; gap: 6px; margin-top: 12px; flex-wrap: wrap; }
    .tag-on { border-radius: 12px; padding: 6px 10px; font-size: 0.75rem; font-weight: 700; color: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .tag-off { border-radius: 12px; padding: 6px 10px; font-size: 0.75rem; font-weight: 600; color: #8e8e93; border: 1px solid #d2d2d7; background: #fff; }
    
    /* NUEVAS TARJETAS APPLE PERSONALIZADAS (SIN CORTES) */
    .apple-kpi-container {
        display: flex; justify-content: space-between; gap: 15px; margin-bottom: 20px; flex-wrap: wrap;
    }
    .apple-kpi-card {
        background-color: #ffffff; border-radius: 20px; padding: 20px; flex: 1; min-width: 150px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.03);
        display: flex; flex-direction: column; justify-content: center; align-items: flex-start;
    }
    .apple-kpi-title { font-size: 0.8rem; color: #86868b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .apple-kpi-value { font-size: 2.2rem; font-weight: 800; color: #1d1d1f; line-height: 1; margin-bottom: 5px; white-space: nowrap; }
    .apple-kpi-sub { font-size: 0.9rem; font-weight: 600; padding: 4px 8px; border-radius: 8px; }
    .sub-green { background-color: #e5fbee; color: #188038; }
    .sub-red { background-color: #fce8e6; color: #c5221f; }
    .sub-gray { background-color: #f1f3f4; color: #5f6368; }

    /* INDICADOR LUMINOSO DE RENTABILIDAD */
    .led-box { display: flex; align-items: center; gap: 10px; margin-bottom: 10px;}
    .led-green { width: 14px; height: 14px; background-color: #34c759; border-radius: 50%; box-shadow: 0 0 10px #34c759, inset 0 0 4px #000; animation: pulse-green 2s infinite; }
    .led-red { width: 14px; height: 14px; background-color: #ff3b30; border-radius: 50%; box-shadow: 0 0 10px #ff3b30, inset 0 0 4px #000; animation: pulse-red 2s infinite; }
    @keyframes pulse-green { 0% { box-shadow: 0 0 0 0 rgba(52, 199, 89, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(52, 199, 89, 0); } 100% { box-shadow: 0 0 0 0 rgba(52, 199, 89, 0); } }
    @keyframes pulse-red { 0% { box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(255, 59, 48, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 59, 48, 0); } }
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

# --- BUSCADOR LATERAL ---
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

# =====================================================================
# SISTEMA DE PESTAÑAS PRINCIPALES
# =====================================================================
tab1, tab2, tab3 = st.tabs(["📊 Escáner Cuántico", "📋 Auditoría", "💼 Cartera en Vivo"])

# --- PESTAÑA 1: ESCÁNER ---
with tab1:
    st.title("Análisis: " + ticker)
    st.markdown("### Sistemas")
    
    s_elegidos, l_ev, l_wr, l_rt, l_es = [], [], [], [], []
    cols = st.columns(5)
    
    for i in range(5):
        with cols[i]:
            st.markdown(f"**{d_defs[i]} D**")
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

    ev_tot = round((sum(l_ev) / 5.0) + ev_plus, 2)
    ite = round(((p_buy - p_sl) / p_buy) * 100.0, 2) if p_buy > 0 else 0.0
    p_estr = sum(10 for e in l_es[1:] if e == "Compra")
    p_sen = 10 if l_es[0] == "Compra" else 0
    penal = 30 if ite > 8 else 0
    idt = l_wr[0] + bono + p_estr + p_sen - penal

    st.markdown("---")
    r_cols = st.columns(3)
    with r_cols[0]:
        st.subheader("EV Total")
        st.metric("SCORE", str(ev_tot), f"+{ev_plus:.2f}")
    with r_cols[1]:
        st.subheader("Fuerza IDT")
        st.metric("PUNTOS", str(idt) + " pts")
    with r_cols[2]:
        st.subheader("Tension ITE")
        st.metric("RIESGO", str(ite) + "%")

    pct_riesgo = r_pct / 100.0
    p_max = CAPITAL * pct_riesgo
    dif_p = p_buy - p_sl
    n_tit = int(p_max / dif_p) if dif_p > 0 else 0
    inv_t = n_tit * p_buy

    st.markdown("---")
    st.subheader(f"Ejecución Recomendada (Capital: {CAPITAL:,.0f} EUR)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Riesgo Maximo", str(int(p_max)) + " EUR")
    c2.metric("Acciones", str(int(n_tit)) + " titulos")
    c3.metric("Posicion Total", str(int(inv_t)) + " EUR")

    if ev_tot < 5 or ite > 8: v_c, v_t = "#ff3b30", "OPERACION NO VIABLE"
    elif idt >= 100 and ite <= 5: v_c, v_t = "#1d1d1f", "COMPRA OBLIGATORIA"
    elif idt >= 85 and ite <= 8: v_c, v_t = "#ff9500", "COMPRA TACTICA"
    else: v_c, v_t = "#ff3b30", "ARMA BLOQUEADA"
        
    tag_v = f"<div style='text-align:center; margin-top:20px;'><div class='tag-on' style='background:{v_c}; font-size:1.2rem; padding:15px 30px;'>{v_t}</div></div>"
    st.markdown(tag_v, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Guardar en Nube"):
        d_sav = {"Ticker": ticker, "Tier": v_t, "EV_Total": ev_tot, "IDT_Puntos": idt, "ITE_Porc": ite, "Veredicto": v_t, "Acciones": n_tit, "Inversion": inv_t}
        for j in range(5):
            d_sav[f"S{j+1}_Dias"] = s_elegidos[j]
            d_sav[f"W{j+1}"] = l_wr[j]
            d_sav[f"R{j+1}"] = l_rt[j]
        new_row = pd.DataFrame([d_sav])
        df_upd = pd.concat([df_datos, new_row], ignore_index=True).drop_duplicates("Ticker", keep="last")
        conn.update(worksheet="Sheet1", data=df_upd)
        st.success("Guardado ok.")

# --- PESTAÑA 2: AUDITORÍA ---
with tab2:
    st.markdown("### Base de Datos de Escaneos")
    st.dataframe(df_datos.sort_values("EV_Total", ascending=False), use_container_width=True)

# --- PESTAÑA 3: CARTERA EN VIVO ---
with tab3:
    st.markdown("### Gestión Quántica de Operaciones")
    tab_vivas, tab_add, tab_historial = st.tabs(["🟢 Posiciones Vivas", "➕ Añadir a Cartera", "📚 Historial de Rentabilidad"])
    
    with tab_vivas:
        try:
            df_cartera = conn.read(worksheet="Cartera", ttl=0).dropna(how="all")
            
            if df_cartera.empty:
                st.warning("Tu cartera está vacía. Ve a la pestaña '➕ Añadir a Cartera' para registrar tu primera compra.")
            else:
                ticker_sel = st.selectbox("Selecciona Posición Abierta:", df_cartera['Ticker'].tolist())
                datos_ticker = df_cartera[df_cartera['Ticker'] == ticker_sel].iloc[0]
                
                fecha_in = pd.to_datetime(datos_ticker['Fecha_Entrada']).date()
                precio_in = float(datos_ticker['Precio_Entrada'])
                acciones = float(datos_ticker['Num_Acciones'])
                stop_actual = float(datos_ticker['Stop_Actual'])
                
                with st.spinner(f"Escaneando {ticker_sel} y descargando histórico desde {fecha_in}..."):
                    stock_cartera = yf.Ticker(ticker_sel)
                    # Descargamos histórico completo para el gráfico y medias
                    hist_largo = stock_cartera.history(start=fecha_in, end=datetime.date.today() + datetime.timedelta(days=1))
                    
                    if hist_largo.empty:
                        # Fallback por si la fecha es muy reciente o hay error
                        hist_largo = stock_cartera.history(period="6mo")
                        
                    precio_vivo = hist_largo['Close'].iloc[-1]
                    media_s5 = hist_largo['Close'].rolling(window=55).mean().iloc[-1]
                    
                    # Previsiones EPS del Ticker actual
                    eps_t_base = stock_cartera.info.get("trailingEps", 0.0)
                    eps_t_fwd = stock_cartera.info.get("forwardEps", 0.0)
                    crec_eps = ((eps_t_fwd - eps_t_base) / eps_t_base * 100) if eps_t_base > 0 and eps_t_fwd > eps_t_base else 0.0
                
                # MATEMÁTICA DE TU POSICIÓN
                beneficio_eur = (precio_vivo - precio_in) * acciones
                beneficio_pct = ((precio_vivo - precio_in) / precio_in) * 100
                dias_en_posicion = (datetime.date.today() - fecha_in).days
                if dias_en_posicion <= 0: dias_en_posicion = 1
                dist_real_s5 = ((precio_vivo - media_s5) / media_s5) * 100 if media_s5 > 0 else 0
                
                # --- NUEVO PANEL DE TARJETAS HTML/CSS (SIN CORTES) ---
                led_class = "led-green" if beneficio_pct >= 0 else "led-red"
                sub_class_ben = "sub-green" if beneficio_pct >= 0 else "sub-red"
                
                html_kpis = f"""
                <div class="apple-kpi-container">
                    <div class="apple-kpi-card" style="border-left: 5px solid {'#34c759' if beneficio_pct>=0 else '#ff3b30'};">
                        <div class="led-box">
                            <div class="{led_class}"></div>
                            <div class="apple-kpi-title" style="margin:0;">Rentabilidad Real</div>
                        </div>
                        <div class="apple-kpi-value">{beneficio_pct:+.2f}%</div>
                        <div class="apple-kpi-sub {sub_class_ben}">{beneficio_eur:+.2f} € Netos</div>
                    </div>
                    
                    <div class="apple-kpi-card">
                        <div class="apple-kpi-title">Precio Mercado</div>
                        <div class="apple-kpi-value">{precio_vivo:.2f}</div>
                        <div class="apple-kpi-sub sub-gray">Entrada: {precio_in:.2f}</div>
                    </div>
                    
                    <div class="apple-kpi-card">
                        <div class="apple-kpi-title">Tiempo en Tendencia</div>
                        <div class="apple-kpi-value">{dias_en_posicion} Días</div>
                        <div class="apple-kpi-sub sub-gray">Desde {fecha_in.strftime('%d/%m/%Y')}</div>
                    </div>
                    
                    <div class="apple-kpi-card">
                        <div class="apple-kpi-title">Distancia a S5 (55D)</div>
                        <div class="apple-kpi-value">{dist_real_s5:.1f}%</div>
                        <div class="apple-kpi-sub sub-gray">Aceleración</div>
                    </div>
                </div>
                """
                st.markdown(html_kpis, unsafe_allow_html=True)
                
                # --- CONTEXTO: SISTEMAS Y FUNDAMENTALES ---
                st.markdown("### Contexto de la Inversión")
                col_c1, col_c2 = st.columns(2)
                
                with col_c1:
                    st.markdown("**🧠 Memoria de Sistemas (Escáner):**")
                    if not df_datos.empty and ticker_sel in df_datos['Ticker'].values:
                        f_sist = df_datos[df_datos['Ticker'] == ticker_sel].iloc[-1]
                        txt_sistemas = f"S1({f_sist['S1_Dias']}d, WR:{f_sist['W1']}%) | S2({f_sist['S2_Dias']}d) | S5({f_sist['S5_Dias']}d)"
                        st.info(f"Sistemas registrados: {txt_sistemas}")
                    else:
                        st.warning("No hay registros en el Escáner para este Ticker. El algoritmo usará sistemas estándar (S5=55D).")
                
                with col_c2:
                    st.markdown("**📈 Previsión de Beneficios (EPS):**")
                    if crec_eps > 0:
                        st.success(f"Crecimiento proyectado a 1 año: **+{crec_eps:.1f}%** (Fundamentales sólidos)")
                    else:
                        st.info("Sin datos de crecimiento explosivo de EPS a corto plazo.")

                # --- GRÁFICO DE VIAJE EN EL TIEMPO ---
                st.markdown("### Evolución del Precio")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist_largo.index, y=hist_largo['Close'], mode='lines', name='Precio', line=dict(color='#2b8af7', width=2)))
                # Linea de Entrada
                fig.add_hline(y=precio_in, line_dash="dash", line_color="green", annotation_text="Entrada", annotation_position="bottom right")
                # Linea de Stop
                fig.add_hline(y=stop_actual, line_dash="dot", line_color="red", annotation_text="Stop Actual", annotation_position="bottom right")
                
                fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'))
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # --- MOTOR DE DECISIÓN CUÁNTICO ---
                st.subheader("🤖 Decisión del Algoritmo Matemático")
                stop_roto = precio_vivo < stop_actual
                colchon_masivo = beneficio_pct > 30.0
                parabola_estadistica = dist_real_s5 > 25.0 
                
                if stop_roto:
                    st.error(f"🚨 **¡STOP ROTO!** El precio actual ({precio_vivo:.2f}) ha cruzado tu nivel crítico. Cierra posición y registra en Historial.")
                elif colchon_masivo and not parabola_estadistica:
                    st.success(f"🛡️ **COLCHÓN ESTADÍSTICO:** Tienes ventaja matemática. El valor orbita sano sobre su S5. Mantén el Stop relajado (S5 o S4) para absorber ruido y exprimir la tendencia.")
                elif parabola_estadistica:
                    st.warning(f"🚀 **ANOMALÍA ESTADÍSTICA:** El precio está un {dist_real_s5:.1f}% por encima de su media 55D. Goma muy tensa. Sube el Stop a S2 o S3 preventivamente.")
                else:
                    st.info("🟢 **TENDENCIA SANA:** Mantén el Stop en tu sistema planificado.")
                    
        except Exception as e:
            st.error(f"Error al leer Cartera. Detalles técnicos: {e}")

    # --- NUEVA PESTAÑA: AÑADIR A CARTERA ---
    with tab_add:
        st.markdown("### ➕ Registrar Nueva Compra")
        with st.form("form_add_cartera"):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                t_ticker = st.text_input("Ticker (Ej: MSFT, SCYR.MC)").upper()
                t_fecha_in = st.date_input("Fecha de Entrada")
                t_precio_in = st.number_input("Precio Compra $", min_value=0.0, format="%.2f")
            with col_f2:
                t_acciones = st.number_input("Nº Acciones", min_value=0.0, format="%.2f")
                t_stop = st.number_input("Stop Loss Inicial $", min_value=0.0, format="%.2f")
                t_fecha_s4 = st.date_input("Fecha Ruptura S4")
            with col_f3:
                t_precio_s4 = st.number_input("Precio Ruptura S4 $", min_value=0.0, format="%.2f")
                t_fecha_s5 = st.date_input("Fecha Ruptura S5")
                t_precio_s5 = st.number_input("Precio Ruptura S5 $", min_value=0.0, format="%.2f")
                
            btn_add = st.form_submit_button("🚀 Añadir a Cartera")
            if btn_add:
                if t_ticker.strip() == "": st.error("⚠️ Ticker obligatorio.")
                elif t_acciones <= 0 or t_precio_in <= 0: st.error("⚠️ Precio y Acciones > 0.")
                else:
                    try:
                        df_cartera = conn.read(worksheet="Cartera", ttl=0)
                        nueva_posicion = {"Ticker": t_ticker, "Fecha_Entrada": t_fecha_in.strftime("%Y-%m-%d"), "Precio_Entrada": t_precio_in, "Num_Acciones": t_acciones, "Stop_Actual": t_stop, "Fecha_Ruptura_S4": t_fecha_s4.strftime("%Y-%m-%d"), "Precio_Ruptura_S4": t_precio_s4, "Fecha_Ruptura_S5": t_fecha_s5.strftime("%Y-%m-%d"), "Precio_Ruptura_S5": t_precio_s5}
                        df_upd = pd.concat([df_cartera, pd.DataFrame([nueva_posicion])], ignore_index=True)
                        conn.update(worksheet="Cartera", data=df_upd)
                        st.success(f"¡{t_ticker} añadido! Ve a 'Posiciones Vivas'.")
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

    with tab_historial:
        st.markdown("### Contador de Rentabilidad Global")
        try:
            df_historial = conn.read(worksheet="Historial", ttl=0).dropna(how="all")
            if df_historial.empty: st.info("Sin operaciones cerradas.")
            else:
                df_historial['Fecha_Venta'] = pd.to_datetime(df_historial['Fecha_Venta']).dt.date
                fecha_inicio = st.date_input("Analizar desde:", value=pd.to_datetime("2024-01-01").date())
                df_filtrado = df_historial[df_historial['Fecha_Venta'] >= fecha_inicio]
                
                total_eur = df_filtrado['Beneficio_EUR'].sum()
                ops_totales = len(df_filtrado)
                win_rate_global = (len(df_filtrado[df_filtrado['Beneficio_EUR'] > 0]) / ops_totales * 100) if ops_totales > 0 else 0
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Beneficio Neto", f"{total_eur:.2f} €")
                c2.metric("Operaciones Cerradas", ops_totales)
                c3.metric("Win Rate", f"{win_rate_global:.1f}%")
                st.dataframe(df_filtrado[['Ticker', 'Fecha_Venta', 'Beneficio_EUR', 'Rentabilidad_Pct']], use_container_width=True)
        except Exception as e:
            st.error(f"Error en Historial: {e}")
