import streamlit as st

st.title("Welcome to My Chemical Analyzer App")

st.write("This is a simple app for a mini project. Click the button below to visit the Streamlit community!")

if st.button('Go to Streamlit Community'):
    st.write('Redirecting to the Streamlit Community...')
    st.markdown('[Streamlit Community](https://discuss.streamlit.io)', unsafe_allow_html=True)

