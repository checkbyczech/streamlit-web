from datetime import datetime, timedelta
import random
from supabase import create_client, Client
import streamlit as st

# --- 1. PŘIPOJENÍ K SUPABASE ---
SUPABASE_URL = "https://gesbcerggeosyqzfphom.supabase.co"
SUPABASE_KEY = "sb_publishable_5O_6zjqxUdl7R18l18ZRlQ_kbGSe10F"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. CONFIG HRY ---
st.set_page_config(page_title="Můj Tycoon", page_icon="🪙", layout="centered")


# --- DATABÁZOVÉ FUNKCE ---
def register_user(username, password):
  try:
    supabase.table("users").insert({
        "username": username,
        "password": password,
        "money": 100,
        "last_daily": None,
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
  if last_daily:
    data["last_daily"] = last_daily
  supabase.table("users").update(data).eq("username", username).execute()


# --- PŘIHLÁŠENÍ / HLAVNÍ HRA ---
if st.session_state.get("logged_in"):
  username = st.session_state["username"]
  user_data = get_user_data(username)

  money = float(user_data.get("money", 100))
  last_daily_str = user_data.get("last_daily")

  # --- HLAVNÍ STRÁNKA HRY ---
  st.title(f"🪙 Vítej v tycoonu, {username}!")

  st.metric(label="Tvé coins", value=f"{money:,.0f} coins")

  st.divider()

  # --- DENNÍ ODMĚNA ---
  st.subheader("🎁 Denní odměna (Daily Reward)")

  can_claim = True
  if last_daily_str:
    try:
      last_daily_dt = datetime.fromisoformat(last_daily_str)
      if datetime.now() - last_daily_dt < timedelta(hours=24):
        can_claim = False
    except Exception:
      can_claim = True

  if can_claim:
    if st.button("🎉 Vyzvednout denní odměnu (10 - 250 coins)"):
      reward = random.randint(10, 250)
      money += reward
      now_str = datetime.now().isoformat()
      update_user_db(username, money, last_daily=now_str)
      st.balloons()
      st.success(f"Získal jsi odměnu **+{reward} coins**!")
      st.rerun()
  else:
    st.info("⏳ Dnešní odměnu už máš vybranou! Vrať se zase zítra.")

  st.divider()

  # Práce a Odhlášení
  col1, col2 = st.columns(2)
  with col1:
    if st.button("🖱️ Pracovat (+10 coins)", use_container_width=True):
      money += 10
      update_user_db(username, money)
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
