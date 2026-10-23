import json
import random
import time
import streamlit as st
from supabase import create_client, Client

# --- PŘIPOJENÍ K SUPABASE ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    supabase = None
    st.error(f"Chyba připojení k Supabase: {e}")

st.set_page_config(page_title="Infinity Zone", layout="centered")

# --- DEFINICE HERNICH DAT ---
CHARACTERS = {
    "common": {
        "name": "Dimenzionální ztroskotanec",
        "rarity": "Common",
        "income": 1,
        "desc": "Obyčejný poutník, který zabloudil v mezidobí. S hodinkami v ruce neustále hledá cestu zpět domů do své dimenze."
    },
    "rare": {
        "name": "Kvantový přenašeč",
        "rarity": "Rare",
        "income": 5,
        "desc": "Vylepšený bojovník z kyberprostoru s pulzujícím modrým pláštěm. Sleduje digitální stopy a v síti se pohybuje s naprostou lehkostí."
    },
    "super_rare": {
        "name": "Strážkyně nulového bodu",
        "rarity": "Super Rare",
        "income": 20,
        "desc": "Tajemná postava ovládající temnou energii a nebezpečné stíny. Dokáže nahlédnout do budoucnosti pomocí svých záhadných krystalů."
    },
    "epic": {
        "name": "Singulární titan",
        "rarity": "Epic",
        "income": 100,
        "desc": "Masivní strážce vytvořený z čisté energie a odolných krystalů. Jeho tělo dokáže absorbovat obrovské množství poškození v každém boji."
    },
    "mythic": {
        "name": "Akolyt nekonečna",
        "rarity": "Mythic",
        "income": 500,
        "desc": "Vznešený obránce galaxie zahalený do zářivého zlatého brnění. Vyzařuje sílu samotného slunce a chrání ty nejvzácnější dimenze."
    },
    "legendary": {
        "name": "Architekt Infinity",
        "rarity": "Legendary",
        "income": 2500,
        "desc": "Nejvzácnější vesmírná entita vládnoucí síle času i prostoru. Svou neomezenou mocí udržuje rovnováhu v celé Infinity Zone."
    }
}

PACKS = {
    "small": {
        "name": "Malý pack",
        "price": 100,
        "weights": [0.70, 0.25, 0.05, 0.0, 0.0, 0.0],
        "keys": ["common", "rare", "super_rare", "epic", "mythic", "legendary"]
    },
    "large": {
        "name": "Velký pack",
        "price": 500,
        "weights": [0.355, 0.30, 0.20, 0.10, 0.04, 0.005],
        "keys": ["common", "rare", "super_rare", "epic", "mythic", "legendary"]
    }
}

# --- PŘIHLAŠOVACÍ A REGISTRAČNÍ OBRAZOVKA ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 Infinity Zone — Vstup")
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 Přihlášení", "📝 Registrace"])
    
    with auth_tab1:
        st.subheader("Přihlásit se ke svému účtu")
        login_name = st.text_input("Hráčské jméno", key="login_user")
        login_pass = st.text_input("Heslo", type="password", key="login_pass")
        
        if st.button("Vstoupit do hry", key="btn_login"):
            if login_name.strip() and login_pass:
                try:
                    res = supabase.table("players").select("*").eq("id", login_name.strip()).execute()
                    if res.data and len(res.data) > 0:
                        db_user = res.data[0]
                        if db_user.get("password") == login_pass:
                            st.session_state.player_id = login_name.strip()
                            st.session_state.logged_in = True
                            st.session_state.initialized = False
                            st.rerun()
                        else:
                            st.error("Nesprávné heslo!")
                    else:
                        st.error("Tento hráč neexistuje. Zaregistruj se v záložce Registrace.")
                except Exception as e:
                    st.error(f"Chyba při přihlašování: {e}")
            else:
                st.warning("Vyplň jméno i heslo.")

    with auth_tab2:
        st.subheader("Vytvořit nový účet")
        reg_name = st.text_input("Zvol si hráčské jméno", key="reg_user")
        reg_pass = st.text_input("Zvol si heslo", type="password", key="reg_pass")
        
        if st.button("Zaregistrovat a vstoupit", key="btn_reg"):
            if reg_name.strip() and reg_pass:
                try:
                    # Ověření, zda už hráč existuje
                    res = supabase.table("players").select("*").eq("id", reg_name.strip()).execute()
                    if res.data and len(res.data) > 0:
                        st.error("Tento účet již existuje! Zvol jiné jméno nebo se přihlas.")
                    else:
                        # Vytvoření nového hráče
                        initial_data = {
                            "id": reg_name.strip(),
                            "password": reg_pass,
                            "coins": 200,
                            "inventory": json.dumps({k: 0 for k in CHARACTERS.keys()}),
                            "last_daily": 0,
                            "last_income_time": time.time()
                        }
                        supabase.table("players").insert(initial_data).execute()
                        st.session_state.player_id = reg_name.strip()
                        st.session_state.logged_in = True
                        st.session_state.initialized = False
                        st.success("Registrace byla úspěšná! Vstupuji do hry...")
                        st.rerun()
                except Exception as e:
                    st.error(f"Chyba při registraci: {e}")
            else:
                st.warning("Vyplň jméno i heslo.")
                
    st.stop()

PLAYER_ID = st.session_state.player_id

# --- FUNKCE PRO DATABÁZI ---
def load_game_data():
    if not supabase:
        return None
    try:
        res = supabase.table("players").select("*").eq("id", PLAYER_ID).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception as e:
        st.error(f"Chyba při načítání dat: {e}")
    return None

def save_game_data():
    if not supabase:
        return
    try:
        data = {
            "id": PLAYER_ID,
            "coins": int(st.session_state.coins),
            "inventory": json.dumps(st.session_state.inventory),
            "last_daily": float(st.session_state.last_daily),
            "last_income_time": float(st.session_state.last_income_time)
        }
        supabase.table("players").update(data).eq("id", PLAYER_ID).execute()
    except Exception as e:
        st.error(f"Chyba při ukládání dat: {e}")

# --- NAČTENÍ HRÁČE PŘI STARTU ---
if "initialized" not in st.session_state or not st.session_state.initialized:
    db_data = load_game_data()
    if db_data:
        st.session_state.coins = float(db_data.get("coins", 200))
        inv_raw = db_data.get("inventory")
        if isinstance(inv_raw, str):
            st.session_state.inventory = json.loads(inv_raw)
        elif isinstance(inv_raw, dict):
            st.session_state.inventory = inv_raw
        else:
            st.session_state.inventory = {k: 0 for k in CHARACTERS.keys()}
        st.session_state.last_daily = float(db_data.get("last_daily", 0))
        
        lit = db_data.get("last_income_time")
        st.session_state.last_income_time = float(lit) if lit is not None else time.time()
    else:
        st.session_state.coins = 200
        st.session_state.inventory = {k: 0 for k in CHARACTERS.keys()}
        st.session_state.last_daily = 0
        st.session_state.last_income_time = time.time()
        save_game_data()
        
    st.session_state.initialized = True

# Výpočet příjmu
total_income_per_hour = sum(st.session_state.inventory[k] * CHARACTERS[k]["income"] for k in CHARACTERS)

current_time = time.time()
elapsed_hours = (current_time - st.session_state.last_income_time) / 3600.0
if elapsed_hours > 0 and total_income_per_hour > 0:
    earned = elapsed_hours * total_income_per_hour
    st.session_state.coins += earned
    st.session_state.last_income_time = current_time
    save_game_data()
else:
    st.session_state.last_income_time = current_time

# --- HLAVNÍ UI HRY ---
st.title(f"🌌 Infinity Zone — Hráč: {PLAYER_ID}")
if st.button("Odhlásit se"):
    st.session_state.logged_in = False
    st.session_state.initialized = False
    st.rerun()

st.write("Sbírej postavy, otevírej packy, vybírej denní odměny a buduj svůj pasivní příjem.")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Coiny", f"{st.session_state.coins:.2f}")
col2.metric("⚡ Příjem za hod.", f"{total_income_per_hour} coinů")
col3.metric("📦 Celkem postav", sum(st.session_state.inventory.values()))

# Rychlé tlačítko pro +1 coin
if st.button("➕ Získat +1 coin"):
    st.session_state.coins += 1
    save_game_data()
    st.rerun()

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["🛒 Obchod s packy", "🎁 Denní odměna", "👥 Inventář postav", "📜 Přehled rarit"])

with tab1:
    st.subheader("Otevřít balíček")
    col_p1, col_p2 = st.columns(2)
    
    for i, (pack_id, pack_data) in enumerate(PACKS.items()):
        with (col_p1 if i == 0 else col_p2):
            st.markdown(f"### {pack_data['name']}")
            st.write(f"Cena: **{pack_data['price']} coinů**")
            if st.button(f"Koupit a otevřít", key=f"pack_{pack_id}"):
                if st.session_state.coins >= pack_data['price']:
                    st.session_state.coins -= pack_data['price']
                    chosen_key = random.choices(pack_data['keys'], weights=pack_data['weights'])[0]
                    st.session_state.inventory[chosen_key] += 1
                    save_game_data()
                    won_char = CHARACTERS[chosen_key]
                    st.success(f"Získal jsi: **{won_char['name']}** ({won_char['rarity']})!")
                    st.balloons()
                else:
                    st.error("Nemáš dostatek coinů!")

with tab2:
    st.subheader("Vyzvednout denní bonus")
    st.write("Každých 24 hodin si můžeš vyzvednout štědrou porci coinů zdarma na rozjezd.")
    
    now = time.time()
    cooldown = 86400
    time_passed = now - st.session_state.last_daily
    
    if time_passed >= cooldown:
        if st.button("🎁 Vyzvednout denní odměnu (250 coinů)"):
            st.session_state.coins += 250
            st.session_state.last_daily = now
            save_game_data()
            st.success("Úspěšně jsi vyzvednul denní odměnu 250 coinů!")
            st.rerun()
    else:
        remaining = int(cooldown - time_passed)
        hours_left = remaining // 3600
        minutes_left = (remaining % 3600) // 60
        st.info(f"Další denní odměnu si můžeš vyzvednout za {hours_left}h {minutes_left}m.")

with tab3:
    st.subheader("Tvůj tým a sbírka")
    for key, count in st.session_state.inventory.items():
        char = CHARACTERS[key]
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{char['name']}** `[{char['rarity']}]`")
                st.caption(char['desc'])
                st.write(f"Příjem: {char['income']} coinů/h")
            with c2:
                st.markdown(f"### Počet: {count}")

with tab4:
    st.subheader("Seznam všech možných postav")
    for key, char in CHARACTERS.items():
        with st.expander(f"{char['name']} ({char['rarity']})"):
            st.write(f"**Popis:** {char['desc']}")
            st.write(f"**Pasivní příjem:** {char['income']} coinů za hodinu")

time.sleep(10)
st.rerun()
