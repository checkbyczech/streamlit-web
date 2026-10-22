import random
import time
import streamlit as st
from supabase import create_client, Client

# --- PŘIPOJENÍ K SUPABASE ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase = None

st.set_page_title("Infinity Zone", layout="centered")

# --- DEFINICE HERNICH DAT (POSTAVY A PACKY) ---
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

# --- STAV HRÁČE ---
if "coins" not in st.session_state:
    st.session_state.coins = 150
if "inventory" not in st.session_state:
    st.session_state.inventory = {k: 0 for k in CHARACTERS.keys()}
if "last_income_time" not in st.session_state:
    st.session_state.last_income_time = time.time()

total_income_per_hour = sum(st.session_state.inventory[k] * CHARACTERS[k]["income"] for k in CHARACTERS)

current_time = time.time()
elapsed_hours = (current_time - st.session_state.last_income_time) / 3600.0
if elapsed_hours > 0:
    earned = elapsed_hours * total_income_per_hour
    st.session_state.coins += earned
    st.session_state.last_income_time = current_time

# --- UI ---
st.title("🌌 Infinity Zone")
st.write("Vítejte v nekonečném vesmíru! Sbírejte postavy, otevírejte packy a budujte svůj pasivní příjem.")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Coiny", f"{st.session_state.coins:.1f}")
col2.metric("⚡ Příjem za hod.", f"{total_income_per_hour} coinů")
col3.metric("📦 Celkem postav", sum(st.session_state.inventory.values()))

st.divider()

tab1, tab2, tab3 = st.tabs(["🛒 Obchod s packy", "👥 Inventář postav", "📜 Přehled rarit"])

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
                    won_char = CHARACTERS[chosen_key]
                    st.success(f"Získal jsi: **{won_char['name']}** ({won_char['rarity']})!")
                    st.balloons()
                else:
                    st.error("Nemáš dostatek coinů!")

with tab2:
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

with tab3:
    st.subheader("Seznam všech možných postav")
    for key, char in CHARACTERS.items():
        with st.expander(f"{char['name']} ({char['rarity']})"):
            st.write(f"**Popis:** {char['desc']}")
            st.write(f"**Pasivní příjem:** {char['income']} coinů za hodinu")

time.sleep(10)
st.rerun()
