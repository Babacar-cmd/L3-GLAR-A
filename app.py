import streamlit as st
st.set_page_config(page_title="TEST", page_icon="🎓", layout="wide")
st.title("TEST BABACAR - Si tu vois ce message, Cloud marche")
st.success("✅ Streamlit Cloud fonctionne ! Le problème vient de l'ancien app.py")
st.write("Maintenant on peut remettre la version complète")
import sys, os
st.write(f"Python {sys.version}")
st.write(f"Dossier: {os.getcwd()}")
st.write(f"Fichiers: {os.listdir('.')}")
if os.path.exists("assets"):
    st.write(f"Assets: {os.listdir('assets')}")
