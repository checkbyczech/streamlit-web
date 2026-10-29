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

BASE_PACKS = {
    "small": {
        "name": "Malý pack",
        "base_price": 100,
        "weights": [0.70, 0.25, 0.05, 0.0, 0.0, 0.0],
        "keys": ["common", "rare", "super_rare", "epic", "mythic", "legendary"]
    },
    "large": {
        "name": "Velký pack",
        "base_price": 500,
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
                    res = supabase.table("players").select("*").eq("id", reg_name.strip()).execute()
                    if res.data and len(res.data) > 0:
                        st.error("Tento účet již existuje! Zvol jiné jméno nebo se přihlas.")
                    else:
                        initial_data = {
                            "id": reg_name.strip(),
                            "password": reg_pass,
                            "coins": 200,
                            "inventory": json.dumps({k: 0 for k in CHARACTERS.keys()}),
                            "last_daily": 0,
                            "last_income_time": time.time(),
                            "click_power": 1,
                            "luck": 1,
                            "rebirths": 0
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
            "last_income_time": float(st.session_state.last_income_time),
            "click_power": int(st.session_state.click_power),
            "luck": int(st.session_state.luck),
            "rebirths": int(st.session_state.rebirths)
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
        st.session_state.click_power = int(db_data.get("click_power", 1))
        st.session_state.luck = int(db_data.get("luck", 1))
        st.session_state.rebirths = int(db_data.get("rebirths", 0))
        
        lit = db_data.get("last_income_time")
        st.session_state.last_income_time = float(lit) if lit is not None else time.time()
    else:
        st.session_state.coins = 200
        st.session_state.inventory = {k: 0 for k in CHARACTERS.keys()}
        st.session_state.last_daily = 0
        st.session_state.click_power = 1
        st.session_state.luck = 1
        st.session_state.rebirths = 0
        st.session_state.last_income_time = time.time()
        save_game_data()
        
    st.session_state.initialized = True

# Výpočet příjmu s bonusem za duplikáty a za Rebirth (+25% za každý Rebirth)
base_income_per_hour = 0
for k, count in st.session_state.inventory.items():
    if count > 0:
        b_inc = CHARACTERS[k]["income"]
        char_total_income = b_inc * count * (1 + 0.5 * (count - 1))
        base_income_per_hour += char_total_income

rebirth_multiplier = 1.0 + (st.session_state.rebirths * 0.25)
total_income_per_hour = base_income_per_hour * rebirth_multiplier

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
if st.button("Odhlásit se", key="logout_btn"):
    st.session_state.logged_in = False
    st.session_state.initialized = False
    st.rerun()

st.write("Sbírej postavy, otevírej packy, vybírej denní odměny a buduj svůj pasivní příjem.")

if "click_power" not in st.session_state:
    st.session_state.click_power = 1
if "luck" not in st.session_state:
    st.session_state.luck = 1
if "rebirths" not in st.session_state:
    st.session_state.rebirths = 0

luck_percentage = (st.session_state.luck - 1) * 0.5

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Coiny", f"{int(st.session_state.coins)}")
col2.metric("⚡ Příjem/h", f"{int(total_income_per_hour)}")
col3.metric("🍀 Štěstí", f"+{luck_percentage:.1f}%")
col4.metric("🌌 Rebirthy", f"{st.session_state.rebirths}")

# Klikací tlačítko
click_earned = int(st.session_state.click_power * rebirth_multiplier)
if st.button(f"Získat +{click_earned} coin(y) 👆", use_container_width=True, key="main_click_btn"):
    st.session_state.coins += click_earned
    save_game_data()
    st.rerun()

st.divider()

# Vylepšení síly kliku
upgrade_cost = int(100 * (2 ** (st.session_state.click_power - 1)) * (1 + st.session_state.rebirths * 0.5))
st.write(f"Aktuální síla kliku: **+{st.session_state.click_power} coinů**")

if st.button(f"Vylepšit klikání (Cena: {upgrade_cost} 💰)", key="upgrade_click_btn"):
    if st.session_state.coins >= upgrade_cost:
        st.session_state.coins -= upgrade_cost
        st.session_state.click_power += 1
        save_game_data()
        st.success("Síla kliknutí byla vylepšena!")
        st.rerun()
    else:
        st.error("Na toto vylepšení nemáš dostatek coinů!")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛒 Obchod s packy", "🎁 Denní odměna", "👥 Inventář postav", "📜 Přehled rarit", "🌌 Rebirth"])

with tab1:
    st.subheader("Otevřít balíček")
    st.write("Ceny a odměny packů se automaticky přizpůsobují tvému postupu a počtu Rebirthů!")
    
    luck_cost = int(150 * (1.5 ** (st.session_state.luck - 1)) * (1 + st.session_state.rebirths * 0.5))
    st.markdown(f"**Vylepšit štěstí na packy** (Aktuální bonus: `+{luck_percentage:.1f}%`)")
    if st.button(f"Zvýšit štěstí (+0.5% šance) — Cena: {luck_cost} 💰", key="upgrade_luck_btn"):
        if st.session_state.coins >= luck_cost:
            st.session_state.coins -= luck_cost
            st.session_state.luck += 1
            save_game_data()
            st.success("Štěstí bylo vylepšeno! Šance na lepší postavy v packách vzrostla.")
            st.rerun()
        else:
            st.error("Na vylepšení štěstí nemáš dostatek coinů!")
            
    st.divider()
    
    col_p1, col_p2 = st.columns(2)
    pack_price_multiplier = 1.0 + (st.session_state.rebirths * 2.0)
    
    for i, (pack_id, pack_data) in enumerate(BASE_PACKS.items()):
        current_pack_price = int(pack_data["base_price"] * pack_price_multiplier)
        
        # Výpočet šancí pro zobrazení v info okénku
        weights = list(pack_data['weights'])
        if st.session_state.luck > 1:
            bonus_factor = 1.0 + ((st.session_state.luck - 1) * 0.05)
            if len(weights) >= 6:
                weights[1] *= bonus_factor
                weights[2] *= bonus_factor * 1.2
                weights[3] *= bonus_factor * 1.5
                weights[4] *= bonus_factor * 2.0
                weights[5] *= bonus_factor * 3.0
        total_w = sum(weights)
        percentages = [(w / total_w) * 100 for w in weights]
        
        target_col = col_p1 if i == 0 else col_p2
        with target_col:
            st.markdown(f"### {pack_data['name']}")
            st.write(f"Cena: **{current_pack_price} coinů**")
            
            # Tlačítko nákupu a infografika vedle sebe
            btn_col1, btn_col2 = st.columns([4, 1])
            with btn_col1:
                if st.button(f"Koupit a otevřít", key=f"pack_{pack_id}"):
                    if st.session_state.coins >= current_pack_price:
                        st.session_state.coins -= current_pack_price
                        
                        chosen_key = random.choices(pack_data['keys'], weights=weights)[0]
                        st.session_state.inventory[chosen_key] += 1
                        save_game_data()
                        won_char = CHARACTERS[chosen_key]
                        st.success(f"Získal jsi: **{won_char['name']}** ({won_char['rarity']})!")
                        st.balloons()
                    else:
                        st.error("Nemáš dostatek coinů!")
            with btn_col2:
                with st.popover("ℹ️"):
                    st.markdown(f"**Šance v packu ({pack_data['name']})**")
                    st.caption(f"Aktuální štěstí: +{luck_percentage:.1f}%")
                    st.divider()
                    rarity_names = ["Common", "Rare", "Super Rare", "Epic", "Mythic", "Legendary"]
                    for r_name, p_val in zip(rarity_names, percentages):
                        st.write(f"- **{r_name}**: `{p_val:.2f}%`")

with tab2:
    st.subheader("Vyzvednout denní bonus")
    st.write("Každých 24 hodin si můžeš vyzvednout denní odměnu (5 % z tvých celkových coinů, minimálně však 250 coinů).")
    
    now = time.time()
    cooldown = 86400
    time_passed = now - st.session_state.last_daily
    
    daily_reward = max(250, int(st.session_state.coins * 0.05))
    
    if time_passed >= cooldown:
        if st.button(f"🎁 Vyzvednout denní odměnu ({daily_reward} coinů)", key="daily_bonus_btn"):
            st.session_state.coins += daily_reward
            st.session_state.last_daily = now
            save_game_data()
            st.success(f"Úspěšně jsi vyzvednul denní odměnu {daily_reward} coinů!")
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
                
            if count > 0:
                sell_price = int(char["income"] * 5 * (1 + st.session_state.rebirths * 0.5))
                if st.button(f"Prodat 1ks (+{sell_price} 💰)", key=f"sell_{key}"):
                    st.session_state.inventory[key] -= 1
                    st.session_state.coins += sell_price
                    save_game_data()
                    st.success(f"Prodal jsi {char['name']} za {sell_price} coinů!")
                    st.rerun()

with tab4:
    st.subheader("Seznam všech možných postav")
    for key, char in CHARACTERS.items():
        with st.expander(f"{char['name']} ({char['rarity']})"):
            st.write(f"**Popis:** {char['desc']}")
            st.write(f"**Pasivní příjem:** {char['income']} coinů za hodinu")

with tab5:
    st.subheader("🌌 Kvantový Rebirth")
    st.write("Proveď znovuzrození, obětuj své stávající coiny a postavy a získej **trvalý bonus +25% k příjmu** za každý Rebirth!")
    st.write(f"Cena Rebirthu: **50 000 coinů**")
    st.write(f"Tvůj aktuální bonus z Rebirthů: **+{int(st.session_state.rebirths * 25)}%**")
    
    if st.button("🌌 Provést Rebirth (50 000 💰)", key="rebirth_btn"):
        if st.session_state.coins >= 50000:
            st.session_state.coins = 200  # Startovní coiny
            st.session_state.inventory = {k: 0 for k in CHARACTERS.keys()}  # Reset postav
            st.session_state.click_power = 1  # Reset síly kliku
            st.session_state.luck = 1  # Reset štěstí
            st.session_state.rebirths += 1  # Přičtení Rebirthu
            save_game_data()
            st.success("Gratuluji! Kvantový Rebirth proběhl úspěšně. Začínáš znovu s obřími bonusy!")
            st.balloons()
            st.rerun()
        else:
            st.error("Na Rebirth potřebuješ alespoň 50 000 coinů!")

time.sleep(10)
st.rerun()
