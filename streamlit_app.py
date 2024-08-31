import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

    # Plot the data (assuming it has 'Wavelength' and 'Absorbance' columns)
    st.write("Here is a plot of your data:")
    fig, ax = plt.subplots()
    ax.plot(data['Wavelength'], data['Absorbance'])
    ax.set_xlabel('Wavelength')
    ax.set_ylabel('Absorbance')
    st.pyplot(fig)
