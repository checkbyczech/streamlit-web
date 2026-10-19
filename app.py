import streamlit as st
st.title("Tycoon")
st.write("Toto bude populární...")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffa500;
    }
    </style>
    """,
    unsafe_allow_html=True,)


import sqlite3
import streamlit as st

DB_NAME = "users.db"


def init_db():
  """Vytvoří databázi a tabulku uživatelů, pokud neexistuje."""
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
  conn.commit()
  conn.close()


def register_user(username, password):
  """Zaregistruje nového uživatele do databáze."""
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  try:
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password),
    )
    conn.commit()
    success = True
  except sqlite3.IntegrityError:
    success = False  # Uživatel již existuje
  conn.close()
  return success


def login_user(username, password):
  """Ověří přihlašovací údaje uživatele."""
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT * FROM users WHERE username = ? AND password = ?",
      (username, password),
  )
  user = cursor.fetchone()
  conn.close()
  return user is not None


# --- STREAMLIT APLIKACE ---
st.set_page_config(page_title="Přihlášení", page_icon="🔐", layout="centered")
init_db()

st.title("🔐 Registrace a Přihlášení")

# Výběr akce v postranním panelu
choice = st.sidebar.selectbox("Zvol akci", ["Přihlášení", "Registrace"])

if choice == "Registrace":
  st.subheader("Vytvořit nový účet")
  new_user = st.text_input("Uživatelské jméno")
  new_pass = st.text_input("Heslo", type="password")

  if st.button("Zaregistrovat se"):
    if new_user and new_pass:
      if register_user(new_user, new_pass):
        st.success("Registrace proběhla úspěšně! Nyní se můžeš přihlásit.")
      else:
        st.error("Tohle uživatelské jméno už je obsazené.")
    else:
      st.warning("Vyplň prosím všechna pole.")

elif choice == "Přihlášení":
  st.subheader("Přihlášení do systému")
  username = st.text_input("Uživatelské jméno")
  password = st.text_input("Heslo", type="password")

  if st.button("Přihlásit"):
    if login_user(username, password):
      st.session_state["logged_in"] = True
      st.session_state["username"] = username
      st.success(f"Vítej, {username}!")
      st.rerun()
    else:
      st.error("Nesprávné uživatelské jméno nebo heslo.")

# Obsah zobrazený pouze po přihlášení
if st.session_state.get("logged_in"):
  st.divider()
  st.write(
      f"Jsi úspěšně přihlášen jako: **{st.session_state['username']}**"
  )

  if st.button("Odhlásit se"):
    st.session_state["logged_in"] = False
    st.session_state.pop("username", None)
    st.rerun()
