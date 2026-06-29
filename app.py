import streamlit as st
from serviceprofinder import find_service_pros

st.title("Service Pro Finder")

zip_code = st.text_input("ZIP code")
radius = st.number_input("Radius in miles", min_value=1, value=10)
profession = st.text_input("Service type")

if st.button("Search"):
    if not zip_code or not profession:
        st.error("Please enter both a ZIP code and a service type.")
    else:
        results = find_service_pros(zip_code, radius, profession)
        st.dataframe(results)

