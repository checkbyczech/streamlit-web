import random
import time
from supabase import create_client, Client
import streamlit as st

# --- 1. PŘIPOJENÍ K SUPABASE ---
SUPABASE_URL = "https://gesbcerggeosyqzfphom.supabase.co"
SUPABASE_KEY = "sb_publishable_5O_6zjqxUdl7R18l18ZRlQ_kbGSe10F"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. CONFIG HRY A STYLY (POZADÍ) ---
st.set_page_config(page_title="Můj Tycoon", page_icon="🪙", layout="centered")

# CSS pro duhový / plynulý přechod na pozadí
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    h1, h2, h3, p, label, .stMetric label, .stMetric div {
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)


# --- DATABÁZOVÉ FUNKCE ---
def register_user(username, password):
  try:
    supabase.table("users").insert({
        "username": username,
        "password": password,
        "money": 100,
        "last_daily": "0",
    }).execute()
    return True
  except Exception:
    return False


def login_user(username, password):
  response = (
      supabase.table("users")
      .select("*")
      .eq("username", username)
      .eq("password", password)
      .execute()
  )
  if len(response.data) > 0:
    return response.data[0]
  return None


def get_user_data(username):
  res = (
      supabase.table("users")
      .select("*")
      .eq("username", username)
      .execute()
      .data
  )
  return res[0] if res else None


def update_user_db(username, money, last_daily=None):
  data = {"money": money}
  if last_daily is not None:
    data["last_daily"] = str(last_daily)
  supabase.table("users").update(data).eq("username", username).execute()


# --- PŘIHLÁŠENÍ / HLAVNÍ HRA ---
if st.session_state.get("logged_in"):
  username = st.session_state["username"]
  user_data = get_user_data(username)

  money = float(user_data.get("money", 100))
  last_daily_str = user_data.get("last_daily", "0")

  # --- HLAVNÍ STRÁNKA HRY ---
  st.title(f"🪙 Vítej v tycoonu, {username}!")

   st.markdown(
    f"""
    <div style="background: rgba(0, 0, 0, 0.2); padding: 15px; border-radius: 15px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.2);">
        <p style="margin: 0; font-size: 14px; opacity: 0.8;">Tvé coins</p>
        <div style="font-size: 32px; font-weight: bold; display: flex; align-items: center; justify-content: center; gap: 8px;">
            <img src="https://img.icons8.com/color/48/expensive-2--v1.png" width="32" style="vertical-align: middle;">
            <span>{money:,.0f}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
   )

  st.divider()

  # --- DENNÍ ODMĚNA (24 hodin = 86400 sekund) ---
  st.subheader("🎁 Denní odměna (Daily Reward)")

  can_claim = True
  try:
    last_time = float(last_daily_str)
    current_time = time.time()
    # 86400 sekund = 24 hodin
    if current_time - last_time < 86400:
      can_claim = False
      zbylý_čas = 86400 - (current_time - last_time)
      hodiny = int(zbylý_čas // 3600)
      minuty = int((zbylý_čas % 3600) // 60)
  except Exception:
    can_claim = True

  if can_claim:
    if st.button("🎉 Vyzvednout denní odměnu (10 - 100 coins)"):
      reward = random.randint(10, 100)
      money += reward
      now_timestamp = time.time()
      update_user_db(username, money, last_daily=now_timestamp)
      st.balloons()
      st.success(f"Získal jsi odměnu **+{reward} coins**!")
      st.rerun()
  else:
    st.info(
        f"⏳ Dnešní odměnu už máš vybranou! Další si můžeš vyzvednout za"
        f" cca {hodiny}h {minuty}m."
    )

  st.divider()

  # Práce a Odhlášení
  col1, col2 = st.columns(2)
  with col1:
    if st.button("🖱️ Pracovat (+5 coins)", use_container_width=True):
      money += 5
      update_user_db(username, money)  # nemění last_daily
      st.rerun()

  with col2:
    if st.button("🚪 Odhlásit se", use_container_width=True):
      st.session_state["logged_in"] = False
      st.session_state.pop("username", None)
      st.rerun()

else:
  # Přihlašovací obrazovka
  st.title("🔐 Přihlášení do Tycoonu")

  c1, c2 = st.columns(2)
  with c1:
    st.subheader("Přihlášení")
    l_u = st.text_input("Uživatelské jméno", key="l_u")
    l_p = st.text_input("Heslo", type="password", key="l_p")
    if st.button("Vstoupit do hry", use_container_width=True):
      u = login_user(l_u, l_p)
      if u:
        st.session_state["logged_in"] = True
        st.session_state["username"] = l_u
        st.rerun()
      else:
        st.error("Chybné jméno nebo heslo.")

  with c2:
    st.subheader("Nová registrace")
    r_u = st.text_input("Nové jméno", key="r_u")
    r_p = st.text_input("Nové heslo", type="password", key="r_p")
    if st.button("Zaregistrovat", use_container_width=True):
      if r_u and r_p:
        if register_user(r_u, r_p):
          st.success("Registrace proběhla úspěšně!")
        else:
          st.error("Jméno je již zabrané.")
      else:
        st.warning("Vyplň všechna pole.")
