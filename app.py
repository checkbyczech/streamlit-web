import streamlit as st
import time

# Nastavení stránky
st.set_page_config(
    page_title="Infinity Zone",
    page_icon="♾️",
    layout="wide"
)

# --- STYLY A POZADÍ ---
st.markdown("""
    <style>
    /* Pozadí celé aplikace */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
        color: #f8fafc;
    }
    
    /* Styling hlavního nadpisu Infinity Zone */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 25px;
    }
    
    /* Vlastní kartička pro zůstatek */
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
    .coin-img {
        width: 48px;
        height: 48px;
        object-fit: contain;
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
    
    /* Vycentrování obrázku klikátka */
    .clicker-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# URL obrázku zlaté mince
COIN_IMAGE_URL = "https://img.icons8.com/emoji/96/gold-medal-emoji.png"

# --- INICIALIZACE STAVU ---
if "coins" not in st.session_state:
    st.session_state.coins = 0
if "last_daily" not in st.session_state:
    st.session_state.last_daily = 0

# --- HERNÍ HLAVIČKA ---
st.markdown('<div class="main-header">♾️ Infinity Zone</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Vítej na hlavním portálu tvojí aplikace</div>', unsafe_allow_html=True)

# --- KARTIČKA ZŮSTATKU S OBRÁZKEM MINCE ---
st.markdown(f"""
    <div class="coin-card">
        <img src="{COIN_IMAGE_URL}" class="coin-img" alt="Coin">
        <div class="coin-info">
            <span class="coin-label">Zůstatek coinů</span>
            <span class="coin-value">{st.session_state.coins:,}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- DENNÍ ODMĚNA ---
st.subheader("🎁 Denní odměna")
current_time = time.time()
cooldown = 86400  # 24 hodin

if current_time - st.session_state.last_daily > cooldown:
    if st.button("Vyzvednout denní odměnu (+100 coinů)", use_container_width=True):
        st.session_state.coins += 100
        st.session_state.last_daily = current_time
        st.success("Úspěšně jsi vyzvedl denní odměnu +100 coinů!")
        st.rerun()
else:
    remaining = int(cooldown - (current_time - st.session_state.last_daily))
    hours = remaining // 3600
    minutes = (remaining % 3600) // 60
    st.info(f"Další denní odměna bude dostupná za {hours}h {minutes}m.")

# --- TYCOON CLICKER S OBRÁZKEM MINCE ---
st.subheader("🎮 Tycoon Clicker")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(COIN_IMAGE_URL, width=150)
    if st.button("🪙 Kliknout pro +1 Coin", use_container_width=True):
        st.session_state.coins += 1
        st.rerun()
