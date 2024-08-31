import streamlit as st
import pandas as pd

st.title("Chemical Analyzer App")

st.write("Upload your chemical data in CSV format to start analyzing.")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV file
    data = pd.read_csv(uploaded_file)

    # Display the first few rows of the data
    st.write("Here is a preview of your data:")
    st.write(data.head())
