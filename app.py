import streamlit as st
import time

# Nastavení stránky
st.set_page_config(
    page_title="Infinity Zone",
    page_icon="♾️",
    layout="wide"
)

# --- STYLY ---
st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #9CA3AF;
        margin-bottom: 25px;
    }
    .coin-card {
        background-color: #1F2937;
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid #374151;
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
    }
    .coin-icon {
        font-size: 2.2rem;
    }
    .coin-info {
        display: flex;
        flex-direction: column;
    }
    .coin-label {
        color: #9CA3AF;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .coin-value {
        color: #F3F4F6;
        font-size: 1.8rem;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACE STAVU ---
if "coins" not in st.session_state:
    st.session_state.coins = 0
if "last_daily" not in st.session_state:
    st.session_state.last_daily = 0

# --- HERNÍ HLAVIČKA ---
st.markdown('<div class="main-header">♾️ Infinity Zone</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Vítej na hlavním portálu tvojí aplikace</div>', unsafe_allow_html=True)

# --- KARTIČKA ZŮSTATKU ---
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
        st.success("Úspěšně jsi vyzvedl denní odměnu +100 coinů!")
        st.rerun()
else:
    remaining = int(cooldown - (current_time - st.session_state.last_daily))
    hours = remaining // 3600
    minutes = (remaining % 3600) // 60
    st.info(f"Další denní odměna bude dostupná za {hours}h {minutes}m.")

# --- TYCOON CLICKER ---
st.subheader("🎮 Tycoon Clicker")
if st.button("Kliknout pro +1 Coin", use_container_width=True):
    st.session_state.coins += 1
    st.rerun()
