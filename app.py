import json
import os
import time
import streamlit as st

# Nastavení stránky
st.set_page_config(
    page_title="Infinity Zone",
    page_icon="♾️",
    layout="wide"
)

# --- UKLÁDÁNÍ DAT (Aby se progress a denní odměna neresetovaly) ---
DATA_FILE = "game_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"coins": 0, "last_daily": 0}

def save_data():
    data = {
        "coins": st.session_state.coins,
        "last_daily": st.session_state.last_daily
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Inicializace stavu ze souboru
if "data_loaded" not in st.session_state:
    saved = load_data()
    st.session_state.coins = saved["coins"]
    st.session_state.last_daily = saved["last_daily"]
    st.session_state.data_loaded = True

# --- STYLY A DESIGN ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
        color: #f8fafc;
    }
    
    /* Hlavička s IZ čtvercem */
    .header-container {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 5px;
    }
    .iz-box {
        background: linear-gradient(135deg, #4F46E5, #06B6D4);
        width: 55px;
        height: 55px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        font-weight: 900;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .main-header {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 25px;
    }
    
    /* Kartička zůstatku */
    .coin-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        padding: 15px 20px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .coin-icon {
        font-size: 2.5rem;
    }
    .coin-info {
        display: flex;
        flex-direction: column;
    }
    .coin-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .coin-value {
        color: #f8fafc;
        font-size: 1.8rem;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# --- HLAVIČKA S IZ ---
st.markdown("""
    <div class="header-container">
        <div class="iz-box">IZ</div>
        <div class="main-header">Infinity Zone</div>
    </div>
    <div class="sub-header">Vítej na hlavním portálu tvojí aplikace</div>
""", unsafe_allow_html=True)

# --- ZŮSTATEK ---
st.markdown(f"""
    <div class="coin-card">
        <div class="coin-icon">🪙</div>
        <div class="coin-info">
            <span class="coin-label">Zůstatek coinů</span>
            <span class="coin-value">{st.session_state.coins:,}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- DENNÍ ODMĚNA ---
st.subheader("🎁 Denní odměna")
current_time = time.time()
cooldown = 86400  # 24 hodin v sekundách

if current_time - st.session_state.last_daily > cooldown:
    if st.button("Vyzvednout denní odměnu (+100 coinů)", use_container_width=True):
        st.session_state.coins += 100
        st.session_state.last_daily = current_time
        save_data()
        st.success("Úspěšně jsi vyzvedl denní odměna +100 coinů!")
        st.rerun()
else:
    remaining = int(cooldown - (current_time - st.session_state.last_daily))
    hours = remaining // 3600
    minutes = (remaining % 3600) // 60
    st.info(f"Další denní odměna bude dostupná za {hours}h {minutes}m.")

# --- TYCOON CLICKER ---
st.subheader("🎮 Tycoon Clicker")
if st.button("🪙 Kliknout pro +1 Coin", use_container_width=True):
    st.session_state.coins += 1
    save_data()
    st.rerun()
