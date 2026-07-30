import os

from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    import streamlit as st

    GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", GOOGLE_API_KEY)
except (ImportError, StreamlitSecretNotFoundError):
    pass
