import streamlit as st
import time
import uuid
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
    .inventory-item {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 12px 15px;
        margin-bottom: 10px;
        color: #f8fafc;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Pomocná funkce pro uložení změn do Supabase
def save_to_db():
    if "user_id" in st.session_state:
        try:
            supabase.table("players").update({
                "coins": st.session_state.coins,
                "last_daily": st.session_state.last_daily,
                "inventory": st.session_state.inventory
            }).eq("id", st.session_state.user_id).execute()
        except Exception as e:
            st.error(f"Chyba při ukládání: {e}")

# --- PŘIHLAŠOVACÍ / REGISTRAČNÍ FORMULÁŘ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("""
        <div class="header-container">
            <div class="iz-box">IZ</div>
            <div class="main-header">Infinity Zone</div>
        </div>
        <div class="sub-header">Přihlášení do hry</div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Přihlášení", "📝 Registrace"])
    
    with tab1:
        with st.form("login_form"):
            login_username = st.text_input("Uživatelské jméno")
            login_password = st.text_input("Heslo", type="password")
            login_btn = st.form_submit_button("Přihlásit se")
            
            if login_btn:
                if login_username and login_password:
                    res = supabase.table("players").select("*").eq("username", login_username).eq("password", login_password).execute()
                    if res.data and len(res.data) > 0:
                        user_data = res.data[0]
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_data["id"]
                        st.session_state.username = user_data["username"]
                        st.session_state.coins = user_data.get("coins", 0)
                        st.session_state.last_daily = user_data.get("last_daily", 0.0)
                        st.session_state.inventory = user_data.get("inventory", [])
                        st.success("Úspěšně přihlášen!")
                        st.rerun()
                    else:
                        st.error("Nesprávné jméno nebo heslo!")
                else:
                    st.warning("Vyplň všechna pole.")

    with tab2:
        with st.form("register_form"):
            reg_username = st.text_input("Nové uživatelské jméno")
            reg_password = st.text_input("Nové heslo", type="password")
            reg_btn = st.form_submit_button("Vytvořit účet")
            
            if reg_btn:
                if reg_username and reg_password:
                    existing = supabase.table("players").select("*").eq("username", reg_username).execute()
                    if existing.data and len(existing.data) > 0:
                        st.error("Toto uživatelské jméno je již zabrané!")
                    else:
                        new_id = str(uuid.uuid4())
                        new_user = {
                            "id": new_id,
                            "username": reg_username,
                            "password": reg_password,
                            "coins": 0,
                            "last_daily": 0.0,
                            "inventory": []
                        }
                        supabase.table("players").insert(new_user).execute()
                        st.success("Účet byl úspěšně vytvořen! Teď se můžeš přihlásit v záložce Přihlášení.")
                else:
                    st.warning("Vyplň všechna pole.")

    st.stop()

# --- HLAVNÍ HRA (ZOBRAZÍ SE AŽ PO PŘIHLÁŠENÍ) ---
col_head, col_logout = st.columns([4, 1])
with col_head:
    st.markdown(f"""
        <div class="header-container">
            <div class="iz-box">IZ</div>
            <div class="main-header">Infinity Zone</div>
        </div>
        <div class="sub-header">Vítej zpět, <b>{st.session_state.username}</b>!</div>
    """, unsafe_allow_html=True)

with col_logout:
    if st.button("🚪 Odhlásit se"):
        st.session_state.logged_in = False
        st.rerun()

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
        st.success("Úspěšně jsi vyzvedl denní odměnu +100 coinů!")
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

# --- BATOH (DYNAMICKÝ INVENTÁŘ) ---
with st.expander("🎒 Batoh (Sběratelské předměty)", expanded=False):
    if not st.session_state.get("inventory"):
        st.info("Tvůj batoh je zatím prázdný.")
    else:
        for item in st.session_state.inventory:
            st.markdown(f'<div class="inventory-item">📦 {item}</div>', unsafe_allow_html=True)

# --- NASTAVENÍ ÚČTU ---
with st.expander("⚙️ Nastavení účtu"):
    if st.button("🔄 Začít od začátku (Resetovat postup)", use_container_width=True):
        st.session_state.coins = 0
        st.session_state.last_daily = 0.0
        st.session_state.inventory = []
        save_to_db()
        st.success("Tvůj postup byl úspěšně resetován!")
        st.rerun()
