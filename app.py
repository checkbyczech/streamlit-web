import streamlit as st
import time
import base64
import json
from supabase import create_client, Client

st.set_page_config(
    page_title="Infinity Zone",
    page_icon="♾️",
    layout="wide"
)

# --- PŘIPOJENÍ K SUPABASE ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Pro zjednodušení budeme prozatím používat jednoho výchozího hráče "default_player"
PLAYER_ID = "default_player"

# --- STYLY ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
        color: #f8fafc;
    }
    .header-container {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 5px;
    }
    .iz-box {
        background: linear-gradient(135deg, #4F46E5, #06B6D4);
        min-width: 55px;
        width: 55px;
        height: 55px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 900;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #94a3b8;
        margin-bottom: 25px;
    }
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
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .coin-value {
        color: #f8fafc;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .card-slot {
        background: rgba(30, 41, 59, 0.5);
        border: 1px dashed rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- NAČTENÍ DAT ZE SUPABASE ---
if "loaded_from_db" not in st.session_state:
    try:
        response = supabase.table("players").select("*").eq("id", PLAYER_ID).execute()
        if response.data and len(response.data) > 0:
            row = response.data[0]
            st.session_state.coins = row.get("coins", 0)
            st.session_state.last_daily = row.get("last_daily", 0.0)
            st.session_state.inventory = row.get("inventory", [])
        else:
            # Pokud záznam neexistuje, vytvoříme ho
            st.session_state.coins = 0
            st.session_state.last_daily = 0.0
            st.session_state.inventory = []
            supabase.table("players").insert({
                "id": PLAYER_ID,
                "coins": 0,
                "last_daily": 0.0,
                "inventory": []
            }).execute()
        st.session_state.loaded_from_db = True
    except Exception as e:
        st.error(f"Chyba při načítání z databáze: {e}")
        st.session_state.coins = 0
        st.session_state.last_daily = 0.0
        st.session_state.inventory = []

# Pomocná funkce pro uložení změn do Supabase
def save_to_db():
    try:
        supabase.table("players").update({
            "coins": st.session_state.coins,
            "last_daily": st.session_state.last_daily,
            "inventory": st.session_state.inventory
        }).eq("id", PLAYER_ID).execute()
    except Exception as e:
        st.error(f"Chyba při ukládání do databáze: {e}")

# --- INICIALIZACE STAVU (fallback) ---
if "coins" not in st.session_state:
    st.session_state.coins = 0
if "last_daily" not in st.session_state:
    st.session_state.last_daily = 0.0
if "inventory" not in st.session_state:
    st.session_state.inventory = []

# --- HLAVIČKA ---
st.markdown("""
    <div class="header-container">
        <div class="iz-box">IZ</div>
        <div class="main-header">Infinity Zone</div>
    </div>
    <div class="sub-header">Vítej na hlavním portálu tvojí aplikace (Cloudová verze)</div>
""", unsafe_allow_html=True)

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
cooldown = 86400  # 24 hodin

if current_time - st.session_state.last_daily > cooldown:
    if st.button("Vyzvednout denní odměnu (+100 coinů)", use_container_width=True):
        st.session_state.coins += 100
        st.session_state.last_daily = current_time
        save_to_db()
        st.success("Úspěšně jsi vyzvedl denní odměnu +100 coinů a uložil do cloudu!")
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
    save_to_db()
    st.rerun()

# --- INVENTÁŘ KART ---
st.subheader("🃏 Inventář karet")
st.write("Tady najdeš své budoucí karty a sběratelské předměty.")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="card-slot">🔒 Karta #1<br><small>Zatím prázdná</small></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="card-slot">🔒 Karta #2<br><small>Zatím prázdná</small></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="card-slot">🔒 Karta #3<br><small>Zatím prázdná</small></div>', unsafe_allow_html=True)
