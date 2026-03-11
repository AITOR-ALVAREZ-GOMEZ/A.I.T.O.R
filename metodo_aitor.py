import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. CONFIGURACION Y ESTILO APPLE ---
st.set_page_config(page_title="AITOR 13.2 Balanced", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp { 
        background-color: #f5f5f7; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
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
    
    /* EFECTO GLOBO Y MEDIDAS IGUALES */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 15px 20px;
        min-height: 140px; /* FUERZA A QUE TODOS MIDAN LO MISMO */
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.03);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 24px rgba(0,0,0,0.08);
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
    
    .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important;
        color: #1d1d1f !important;
        border-radius: 12px !important;
        border
