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

import streamlit as st

# Postranní navigace
stranka = st.sidebar.selectbox("Navigace", ["Domů", "Tycoon"])

# Logika přepínání stránek
if stranka == "Domů":
    st.title("🏠 Hlavní stránka")

elif stranka == "Tycoon":
    st.title("🎃 Záložka Tycoon")
    st.write("Tady se bude odehrávat hlavní hra a sbírání kartiček!")
