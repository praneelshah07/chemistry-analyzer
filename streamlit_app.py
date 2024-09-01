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
    smooth_data = savgol_filter(baseline_corrected, 151, 3)

    # Plot the baseline-corrected and smoothed data
    st.write("Baseline-Corrected and Smoothed FTIR Spectrum:")
    fig_corrected = px.line(x=data['Wavelength'], y=smooth_data, title='Baseline-Corrected FTIR Spectrum',
                            labels={'x': 'Wavenumber (cm⁻¹)', 'y': 'Absorbance'})
    st.plotly_chart(fig_corrected)

    # Identify peaks in the smoothed data
    peaks, _ = find_peaks(smooth_data, height=0.05, width=10)

    # Round the peak absorbances to 4 decimal places and convert to regular Python floats
    rounded_absorbances = [float(round(absorbance, 4)) for absorbance in smooth_data[peaks]]

    # Output the peak indices and values with reduced decimals
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
    # Existing mid-range groups
    "O-H stretch (alcohols)": (3200, 3600),
    "N-H stretch (amines)": (3300, 3500),
    "C=O stretch (carbonyl)": (1700, 1750),
    "C-H stretch (alkanes)": (2850, 2960),
    "C=C stretch (alkenes)": (1600, 1680),
    "C≡C stretch (alkynes)": (2100, 2260),
    "C-O stretch (alcohols, ethers)": (1050, 1150),
    "N-O stretch (nitro compounds)": (1515, 1560),
    "C≡N stretch (nitriles)": (2200, 2260),
    "C-N stretch (amines)": (1180, 1360),
    "S=O stretch (sulfones)": (1300, 1350),
    "O-H bend (carboxylic acids)": (1410, 1440),
    "P=O stretch (phosphates)": (1100, 1200),
    "O-H stretch (carboxylic acids)": (2500, 3300),
    "C-H bend (aromatics)": (700, 900),
    "C-I stretch (haloalkanes)": (485, 600),
    "C-Br stretch (haloalkanes)": (500, 650),
    "C-Cl stretch (haloalkanes)": (600, 800),  # Overlaps with mid-range
    "Metal-O stretch (inorganics)": (200, 500),
    "Ring deformation (aromatics)": (400, 600),
    "C-H stretch (alkynes, terminal)": (3300, 3400),
    "N-H stretch (amines, high range)": (3500, 3700),
}



    identified_groups = []
    for peak in peaks:
        wavenumber = data['Wavelength'].iloc[peak]
        for group, (min_wavenumber, max_wavenumber) in functional_groups.items():
            if min_wavenumber <= wavenumber <= max_wavenumber:
                identified_groups.append(group)

    # Display identified functional groups
    if identified_groups:
        st.write("Possible Identified Functional Groups:")
        for group in identified_groups:
            st.write(f"{group}")

        # Simple compound suggestion based on identified functional groups
        compound_lookup = {
            frozenset(["C=O stretch", "O-H stretch"]): "Carboxylic Acid",
            frozenset(["C=O stretch", "C-H stretch"]): "Aldehyde or Ketone",
            frozenset(["O-H stretch"]): "Alcohol or Phenol",
            # Add more combinations as needed
        }

        matched_compound = None
        for compound, groups in compound_lookup.items():
            if frozenset(identified_groups) == groups:
                matched_compound = compound
                break

        if matched_compound:
            st.write(f"Likely compound: {matched_compound}")
        else:
            st.write("No matching compound found in the database.")
    else:
        st.write("No common functional groups identified.")
