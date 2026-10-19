from supabase import create_client, Client
import streamlit as st

# --- 1. PŘIPOJENÍ K SUPABASE ---
SUPABASE_URL = "https://gesbcerggeosyqzfphom.supabase.co"
SUPABASE_KEY = "sb_publishable_5O_6zjqxUdl7R18l18ZRlQ_kbGSe10F"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. STREAMLIT APLIKACE ---
st.set_page_config(page_title="Můj Tycoon", page_icon="💰", layout="centered")


def register_user(username, password):
  try:
    supabase.table("users").insert({
        "username": username,
        "password": password,
        "money": 100,
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


def update_money(username, new_money):
  supabase.table("users").update({"money": new_money}).eq(
      "username", username
  ).execute()


# --- PŘIHLÁŠENÍ / REGISTRACE ---
if st.session_state.get("logged_in"):
  username = st.session_state["username"]

  st.title(f"💰 Vítej v tyconu, {username}!")

  user_data = (
      supabase.table("users")
      .select("money")
      .eq("username", username)
      .execute()
      .data[0]
  )
  current_money = float(user_data["money"])

  st.metric(label="Tvé peníze", value=f"{current_money:.0f} Kč")

  st.divider()

  if st.button("Pracovat a vydělat 10 Kč 🖱️"):
    current_money += 10
    update_money(username, current_money)
    st.success("Vydělal jsi 10 Kč a stav se uložil do cloudu!")
    st.rerun()

  if st.button("Odhlásit se"):
    st.session_state["logged_in"] = False
    st.session_state.pop("username", None)
    st.rerun()

else:
  st.title("🔐 Přihlášení do Tycoonu")

  col1, col2 = st.columns(2)

  with col1:
    st.subheader("Přihlásit se")
    l_user = st.text_input("Uživatelské jméno", key="l_user")
    l_pass = st.text_input("Heslo", type="password", key="l_pass")

    if st.button("Vstoupit do hry"):
      user = login_user(l_user, l_pass)
      if user:
        st.session_state["logged_in"] = True
        st.session_state["username"] = l_user
        st.rerun()
      else:
        st.error("Nesprávné jméno nebo heslo.")

  with col2:
    st.subheader("Registrace")
    r_user = st.text_input("Nové uživatelské jméno", key="r_user")
    r_pass = st.text_input("Nové heslo", type="password", key="r_pass")

    if st.button("Zaregistrovat"):
      if r_user and r_pass:
        if register_user(r_user, r_pass):
          st.success("Registrace úspěšná! Nyní se můžeš přihlásit.")
        else:
          st.error("Tohle uživatelské jméno už je obsazené.")
      else:
        st.warning("Vyplň obě pole.")
