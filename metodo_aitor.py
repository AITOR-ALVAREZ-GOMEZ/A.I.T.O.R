import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 18.0", layout="wide")

# --- CSS ESTILO APPLE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
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
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 15px 20px;
        min-height: 140px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.03);
    }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        color: #1d1d1f !important;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
        color: #86868b !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
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
    .rank-box {
        display: flex;
        gap: 6px;
        margin-top: 12px;
        flex-wrap: wrap;
    }
    .tag-on {
        border-radius: 12px;
        padding: 6px 10px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #fff;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .tag-off {
        border-radius: 12px;
        padding: 6px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #8e8e93;
        border: 1px solid #d2d2d7;
        background: #fff;
    }
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
        st.metric("SCORE", str(ev_tot), f"+{ev_plus:.2f}")
        st.caption("Esperanza: Calidad + Ventaja")
        
        h_ev = "<div class='rank-box'>"
        if ev_tot >= 10:
            h_ev += "<div class='tag-on' style='background:#34c759;'>TIER S</div><div class='tag-off'>TIER A</div><div class='tag-off'>DESCARTE</div>"
        elif ev_tot >= 5:
            h_ev += "<div class='tag-off'>TIER S</div><div class='tag-on' style='background:#2b8af7;'>TIER A</div><div class='tag-off'>DESCARTE</div>"
        else:
            h_ev += "<div class='tag-off'>TIER S</div><div class='tag-off'>TIER A</div><div class='tag-on' style='background:#ff3b30;'>DESCARTE</div>"
        h_ev += "</div>"
        st.markdown(h_ev, unsafe_allow_html=True)
    
    # 2. IDT PUNTOS
    with r_cols[1]:
        st.subheader("Fuerza IDT")
        st.metric("PUNTOS", str(idt) + " pts")
        st.caption("Disparo Tactico y Estructura")
        
        h_idt = "<div class='rank-box'>"
        if idt >= 100:
            h_idt += "<div class='tag-on' style='background:#1d1d1f;'>OBLIGATORIA</div><div class='tag-off'>TACTICA</div><div class='tag-off'>BLOQUEADA</div>"
        elif idt >= 85:
            h_idt += "<div class='tag-off'>OBLIGATORIA</div><div class='tag-on' style='background:#ff9500;'>TACTICA</div><div class='tag-off'>BLOQUEADA</div>"
        else:
            h_idt += "<div class='tag-off'>OBLIGATORIA</div><div class='tag-off'>TACTICA</div><div class='tag-on' style='background:#ff3b30;'>BLOQUEADA</div>"
        h_idt += "</div>"
        st.markdown(h_idt, unsafe_allow_html=True)

    # 3. ITE %
    with r_cols[2]:
        st.subheader("Tension ITE")
        st.metric("RIESGO", str(ite) + "%")
        st.caption("Distancia porcentual al Stop")
        
        h_ite = "<div class='rank-box'>"
        if ite <= 5:
            h_ite += "<div class='tag-on' style='background:#34c759;'>OPTIMO</div><div class='tag-off'>LIMITE</div><div class='tag-off'>NO OPERABLE</div>"
        elif ite <= 8:
            h_ite += "<div class='tag-off'>OPTIMO</div><div class='tag-on' style='background:#ff9500;'>LIMITE</div><div class='tag-off'>NO OPERABLE</div>"
        else:
            h_ite += "<div class='tag-off'>OPTIMO</div><div class='tag-off'>LIMITE</div><div class='tag-on' style='background:#ff3b30;'>NO OPERABLE</div>"
        h_ite += "</div>"
        st.markdown(h_ite, unsafe_allow_html=True)

    # --- CALCULADORA DE RIESGO ---
    pct_riesgo = r_pct / 100.0
    p_max = CAPITAL * pct_riesgo
    dif_p = p_buy - p_sl
    n_tit = 0
    if dif_p > 0:
        n_tit = int(p_max / dif_p)
    inv_t = n_tit * p_buy

    st.markdown("---")
    st.subheader(f"Ejecución Recomendada (Capital: {CAPITAL:,.0f} EUR)")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Riesgo Maximo", str(int(p_max)) + " EUR")
    c2.metric("Acciones", str(int(n_tit)) + " titulos")
    c3.metric("Posicion Total", str(int(inv_t)) + " EUR")

    # --- VERDICTO FINAL ---
    if ev_tot < 5 or ite > 8:
        v_c = "#ff3b30"
        v_t = "OPERACION NO VIABLE"
    elif idt >= 100 and ite <= 5:
        v_c = "#1d1d1f"
        v_t = "COMPRA OBLIGATORIA"
    elif idt >= 85 and ite <= 8:
        v_c = "#ff9500"
        v_t = "COMPRA TACTICA"
    else:
        v_c = "#ff3b30"
        v_t = "ARMA BLOQUEADA"
        
    tag_v = f"<div style='text-align:center; margin-top:20px;'><div class='tag-on' style='background:{v_c}; font-size:1.2rem; padding:15px 30px;'>{v_t}</div></div>"
    st.markdown(tag_v, unsafe_allow_html=True)

    # --- GUARDAR ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Guardar en Nube"):
        d_sav = {
            "Ticker": ticker, "Tier": v_t, "EV_Total": ev_tot, 
            "IDT_Puntos": idt, "ITE_Porc": ite, "Veredicto": v_t, 
            "Acciones": n_tit, "Inversion": inv_t
        }
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
    
    # Sub-pestañas para organizar la cartera
    tab_vivas, tab_add, tab_historial = st.tabs(["🟢 Posiciones Vivas", "➕ Añadir a Cartera", "📚 Historial de Rentabilidad"])
    
    with tab_vivas:
        try:
            df_cartera = conn.read(worksheet="Cartera", ttl=0).dropna(how="all")
            
            if df_cartera.empty:
                st.warning("Tu cartera está vacía. Ve a la pestaña '➕ Añadir a Cartera' para registrar tu primera compra.")
            else:
                ticker_sel = st.selectbox("Selecciona Posición Abierta:", df_cartera['Ticker'].tolist())
                datos_ticker = df_cartera[df_cartera['Ticker'] == ticker_sel].iloc[0]
                
                # Cargar tus datos de entrada
                fecha_in = pd.to_datetime(datos_ticker['Fecha_Entrada']).date()
                precio_in = float(datos_ticker['Precio_Entrada'])
                acciones = float(datos_ticker['Num_Acciones'])
                stop_actual = float(datos_ticker['Stop_Actual'])
                
                # Múltiples niveles de ruptura largos
                p_ruptura_s4 = float(datos_ticker['Precio_Ruptura_S4'])
                p_ruptura_s5 = float(datos_ticker['Precio_Ruptura_S5'])
                
                with st.spinner(f"Escaneando {ticker_sel} en tiempo real..."):
                    stock = yf.Ticker(ticker_sel)
                    hist = stock.history(period="1mo")
                    precio_vivo = hist['Close'].iloc[-1]
                
                # MATEMÁTICA DE TU POSICIÓN
                beneficio_eur = (precio_vivo - precio_in) * acciones
                beneficio_pct = ((precio_vivo - precio_in) / precio_in) * 100
                
                # ¿Cuánto tiempo llevas dentro?
                dias_en_posicion = (datetime.date.today() - fecha_in).days
                if dias_en_posicion <= 0: dias_en_posicion = 1
                
                # Distancias a las rupturas largas
                dist_s4 = ((precio_vivo - p_ruptura_s4) / p_ruptura_s4) * 100 if p_ruptura_s4 > 0 else 0
                dist_s5 = ((precio_vivo - p_ruptura_s5) / p_ruptura_s5) * 100 if p_ruptura_s5 > 0 else 0
                
                # PANEL VISUAL DE DATOS
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Precio Actual", f"{precio_vivo:.2f}", f"{beneficio_pct:.2f}% (Latente)")
                col2.metric("Beneficio Neto", f"{beneficio_eur:.2f} €")
                col3.metric("Tiempo en Pos.", f"{dias_en_posicion} días", f"Desde {fecha_in.strftime('%d/%m/%Y')}")
                col4.metric("Aceleración S5", f"{dist_s5:.2f}%", "Distancia al origen S5")
                
                st.markdown("---")
                
                # MOTOR DE DECISIÓN Y ALARMA ROJA
                fase_explosiva = dist_s5 >= 20.0 or dist_s4 >= 15.0
                stop_roto = precio_vivo < stop_actual
                
                st.subheader("🤖 Decisión del Algoritmo")
                if stop_roto:
                    alarma_html = """
                    <style>
                    @keyframes parpadeo_rojo { 0% { background-color: #ff0000; color: white; transform: scale(1); } 50% { background-color: #8b0000; color: yellow; transform: scale(1.02); } 100% { background-color: #ff0000; color: white; transform: scale(1); } }
                    .caja-alarma { animation: parpadeo_rojo 0.8s infinite; padding: 30px; border-radius: 15px; text-align: center; border: 5px solid black; }
                    .texto-alarma { font-size: 40px; font-weight: 900; margin: 0; font-family: 'Arial Black', sans-serif;}
                    </style>
                    <div class="caja-alarma"><p class="texto-alarma">🚨 ¡STOP ROTO! CERRAR POSICIÓN 🚨</p></div>
                    """
                    st.markdown(alarma_html, unsafe_allow_html=True)
                    st.error(f"El precio actual ({precio_vivo:.2f}) ha perforado tu Stop ({stop_actual:.2f}). Vende y registra el resultado en 'Historial'.")
                elif fase_explosiva:
                    st.success(f"🚀 **ACELERACIÓN EXTREMA:** El precio está un {dist_s5:.1f}% por encima de S5. Ajusta el Stop agresivamente (S1 o S2) para no devolver la ganancia.")
                else:
                    st.info("🟢 **TENDENCIA EN DESARROLLO:** Mantén el Stop en sistemas lentos (S3/S4) para darle aire al precio.")
                    
        except Exception as e:
            st.error(f"Error al leer Cartera. Comprueba que las columnas de la pestaña 'Cartera' están bien escritas. Detalles técnicos: {e}")

    # --- NUEVA PESTAÑA: AÑADIR A CARTERA ---
    with tab_add:
        st.markdown("### ➕ Registrar Nueva Compra")
        st.caption("Rellena los datos de tu nueva posición. Se guardarán automáticamente en tu base de datos de Google Sheets.")
        
        with st.form("form_add_cartera"):
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                t_ticker = st.text_input("Ticker (Ej: MSFT, TEMN.SW)").upper()
                t_fecha_in = st.date_input("Fecha de Entrada")
                t_precio_in = st.number_input("Precio de Compra $", min_value=0.0, format="%.2f")
                
            with col_f2:
                t_acciones = st.number_input("Nº de Acciones", min_value=0.0, format="%.2f")
                t_stop = st.number_input("Stop Loss Inicial $", min_value=0.0, format="%.2f")
                t_fecha_s4 = st.date_input("Fecha Ruptura S4")
                
            with col_f3:
                t_precio_s4 = st.number_input("Precio Ruptura S4 $", min_value=0.0, format="%.2f")
                t_fecha_s5 = st.date_input("Fecha Ruptura S5")
                t_precio_s5 = st.number_input("Precio Ruptura S5 $", min_value=0.0, format="%.2f")
                
            st.markdown("<br>", unsafe_allow_html=True)
            btn_add = st.form_submit_button("🚀 Añadir a Cartera")
            
            if btn_add:
                if t_ticker.strip() == "":
                    st.error("⚠️ El campo Ticker es obligatorio.")
                elif t_acciones <= 0 or t_precio_in <= 0:
                    st.error("⚠️ El Precio de Compra y el Nº de Acciones deben ser mayores que cero.")
                else:
                    try:
                        # Leer los datos actuales de la cartera
                        df_cartera = conn.read(worksheet="Cartera", ttl=0)
                        
                        # Crear la nueva fila
                        nueva_posicion = {
                            "Ticker": t_ticker,
                            "Fecha_Entrada": t_fecha_in.strftime("%Y-%m-%d"),
                            "Precio_Entrada": t_precio_in,
                            "Num_Acciones": t_acciones,
                            "Stop_Actual": t_stop,
                            "Fecha_Ruptura_S4": t_fecha_s4.strftime("%Y-%m-%d"),
                            "Precio_Ruptura_S4": t_precio_s4,
                            "Fecha_Ruptura_S5": t_fecha_s5.strftime("%Y-%m-%d"),
                            "Precio_Ruptura_S5": t_precio_s5
                        }
                        
                        # Añadir la fila y actualizar el Excel
                        df_upd = pd.concat([df_cartera, pd.DataFrame([nueva_posicion])], ignore_index=True)
                        conn.update(worksheet="Cartera", data=df_upd)
                        st.success(f"¡Genial! {t_ticker} se ha añadido a tu Cartera en Vivo. Ve a la pestaña 'Posiciones Vivas' para ver la magia.")
                        
                    except Exception as e:
                        st.error(f"Error al guardar. Asegúrate de que la pestaña 'Cartera' de tu Excel tiene las 9 columnas correctas. Detalles: {e}")

    with tab_historial:
        st.markdown("### Contador de Rentabilidad Global")
        try:
            df_historial = conn.read(worksheet="Historial", ttl=0).dropna(how="all")
            if df_historial.empty:
                st.info("Aún no tienes operaciones cerradas en el Historial. Cuando vendas algo, apúntalo en el Excel.")
            else:
                # Convertir fechas para poder filtrar
                df_historial['Fecha_Venta'] = pd.to_datetime(df_historial['Fecha_Venta']).dt.date
                
                # FILTRO DE FECHAS
                fecha_inicio = st.date_input("Analizar rentabilidad desde:", value=pd.to_datetime("2024-01-01").date())
                
                # Filtrar el dataframe
                df_filtrado = df_historial[df_historial['Fecha_Venta'] >= fecha_inicio]
                
                # Calcular Totales
                total_eur = df_filtrado['Beneficio_EUR'].sum()
                ops_ganadoras = len(df_filtrado[df_filtrado['Beneficio_EUR'] > 0])
                ops_totales = len(df_filtrado)
                win_rate_global = (ops_ganadoras / ops_totales * 100) if ops_totales > 0 else 0
                
                # Mostrar el Dashboard de Resultados
                c1, c2, c3 = st.columns(3)
                c1.metric("Beneficio Neto (Periodo)", f"{total_eur:.2f} €")
                c2.metric("Operaciones Cerradas", ops_totales)
                c3.metric("Win Rate de Cartera", f"{win_rate_global:.1f}%")
                
                st.dataframe(df_filtrado[['Ticker', 'Fecha_Venta', 'Beneficio_EUR', 'Rentabilidad_Pct']], use_container_width=True)
                
        except Exception as e:
            st.error(f"Falta la pestaña 'Historial' en el Excel o tiene un error. Detalles: {e}")
