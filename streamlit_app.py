import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.signal import find_peaks, savgol_filter

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

    # Plot the original data
    st.write("Original FTIR Spectrum:")
    fig = px.line(data, x='Wavelength', y='Absorbance', title='FTIR Spectrum',
                  labels={'Wavelength': 'Wavenumber (cm⁻¹)', 'Absorbance': 'Absorbance'})
    st.plotly_chart(fig)

    # Apply a Savitzky-Golay filter for baseline correction and smoothing
    baseline_corrected = data['Absorbance'] - savgol_filter(data['Absorbance'], 51, 3)
    smooth_data = savgol_filter(baseline_corrected, 101, 3)

    # Plot the baseline-corrected and smoothed data
    st.write("Baseline-Corrected and Smoothed FTIR Spectrum:")
    fig_corrected = px.line(x=data['Wavelength'], y=smooth_data, title='Baseline-Corrected FTIR Spectrum',
                            labels={'x': 'Wavenumber (cm⁻¹)', 'y': 'Absorbance'})
    st.plotly_chart(fig_corrected)

    # Identify peaks in the smoothed data
    peaks, _ = find_peaks(smooth_data, height=0.05, width=10)

    # Round the peak absorbances to 4 decimal places
    rounded_absorbances = [round(absorbance, 4) for absorbance in smooth_data[peaks]]

    # Debugging: Output the peak indices and values with reduced decimals
    st.write(f"Peaks found at indices: {peaks.tolist()}")
    st.write(f"Peak wavenumbers: {data['Wavelength'].iloc[peaks].values.tolist()}")
    st.write(f"Peak absorbances: {rounded_absorbances}")


    # Annotate peaks on the plot
    for peak in peaks:
        fig_corrected.add_annotation(x=data['Wavelength'].iloc[peak], y=smooth_data[peak],
                                     text=f"Peak @ {data['Wavelength'].iloc[peak]:.2f} cm⁻¹",
                                     showarrow=True, arrowhead=1)
    st.plotly_chart(fig_corrected)

    # Functional group identification based on peak wavenumber
    functional_groups = {
        "O-H stretch": (3200, 3600),
        "C=O stretch": (1700, 1750),
        "C-H stretch": (2850, 2960),
        # Add more functional groups and ranges as needed
    }

    # Check which peaks fall within these ranges
    identified_groups = []
    for peak in peaks:
        wavenumber = data['Wavelength'].iloc[peak]
        for group, (min_wavenumber, max_wavenumber) in functional_groups.items():
            if min_wavenumber <= wavenumber <= max_wavenumber:
                identified_groups.append((wavenumber, group))

    # Display identified functional groups
    if identified_groups:
        st.write("Identified Functional Groups:")
        for wavenumber, group in identified_groups:
            st.write(f"Peak @ {wavenumber:.2f} cm⁻¹: {group}")
    else:
        st.write("No common functional groups identified.")
