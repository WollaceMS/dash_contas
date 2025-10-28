import streamlit as st

import streamlit as st

# Carrega os usuários e senhas do secrets.toml
USERS = st.secrets["auth"]

def valida_senha(username, password):
    return USERS.get(username) == password


