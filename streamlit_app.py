import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.signal import find_peaks, savgol_filter
import openai

# Set up your OpenAI API key
openai.api_key = 'your_openai_api_key_here'

def get_gpt3_deduction(functional_groups):
    prompt = f"Given the following functional groups: {', '.join(functional_groups)}, deduce what molecule these groups could be a part of."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

# Streamlit app title
st.title("Chemical Analyzer with AI Deduction")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV file
    data = pd.read_csv(uploaded_file)

    # Select only relevant columns to display
    columns_to_display = ["Wavelength", "Absorbance"]
    data = data[columns_to_display]

    # Display the selected columns as a preview
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

    # Optional: Shift baseline to ensure all values are positive
    min_value = smooth_data.min()
    if min_value < 0:
        smooth_data += abs(min_value)

    # Plot the baseline-corrected and smoothed data
    st.write("Baseline-Corrected and Smoothed FTIR Spectrum:")
    fig_corrected = px.line(x=data['Wavelength'], y=smooth_data, title='Baseline-Corrected FTIR Spectrum',
                            labels={'x': 'Wavenumber (cm⁻¹)', 'y': 'Absorbance'})
    st.plotly_chart(fig_corrected)

    # Identify peaks in the smoothed data
    peaks, _ = find_peaks(smooth_data, height=0.05, width=5)

    # Check if peaks were found
    if len(peaks) > 0:
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

        # Expanded functional group identification based on peak wavenumber
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
            "S=O stretch (sulfones)": (900, 1100),  # Adjusted for overlap into this range
            "O-H bend (carboxylic acids)": (1410, 1440),
            "P=O stretch (phosphates)": (1100, 1200),
            "O-H stretch (carboxylic acids)": (2500, 3300),
            "C-H bend (aromatics)": (700, 900),

            # Low wavenumber groups (100-600 cm⁻¹)
            "C-I stretch (haloalkanes)": (485, 600),
            "C-Br stretch (haloalkanes)": (500, 650),
            "C-Cl stretch (haloalkanes)": (600, 800),  # Overlaps with mid-range
            "Metal-O stretch (inorganics)": (200, 500),
            "Ring deformation (aromatics)": (400, 600),

            # High wavenumber groups (3500+ cm⁻¹)
            "Free O-H stretch (alcohols, phenols)": (3600, 3700),
            "C-H stretch (alkynes, terminal)": (3300, 3400),
            "N-H stretch (amines, high range)": (3500, 3700),

            # Added groups for 900-1000 cm⁻¹ range
            "C-H out-of-plane bend (aromatics)": (900, 1000),
            "C=C-H out-of-plane bend (alkenes)": (900, 990),
            "C-O-C stretch (ethers)": (900, 1300),  # Overlaps, but with a specific band around 1000 cm⁻¹
            "Si-O stretch (silicates, silicones)": (900, 1100),
        }

        identified_groups = []
        for peak in peaks:
            wavenumber = data['Wavelength'].iloc[peak]
            for group, (min_wavenumber, max_wavenumber) in functional_groups.items():
                if min_wavenumber <= wavenumber <= max_wavenumber:
                    identified_groups.append(group)

        # Display identified functional groups
        if identified_groups:
            st.write("Identified Functional Groups:")
            for group in identified_groups:
                st.write(f"{group}")

            # Expanded compound suggestion based on identified functional groups
            compound_lookup = {
                frozenset(["C=O stretch (carbonyl)", "O-H stretch (alcohols)"]): "Carboxylic Acid (e.g., Acetic Acid)",
                frozenset(["C=O stretch (carbonyl)", "C-H stretch (alkanes)"]): "Aldehyde (e.g., Formaldehyde) or Ketone (e.g., Acetone)",
                frozenset(["O-H stretch (alcohols)"]): "Alcohol (e.g., Ethanol) or Phenol",
                frozenset(["N-H stretch (amines)"]): "Primary or Secondary Amine (e.g., Aniline)",
                frozenset(["C=C stretch (alkenes)", "C-H stretch (alkanes)"]): "Alkene (e.g., Ethylene)",
                frozenset(["C≡C stretch (alkynes)", "C-H stretch (alkynes, terminal)"]): "Alkyne (e.g., Acetylene)",
                frozenset(["C-O-C stretch (ethers)", "C-H stretch (alkanes)"]): "Ether (e.g., Diethyl Ether)",
                frozenset(["C≡N stretch (nitriles)", "C-H stretch (alkanes)"]): "Nitrile (e.g., Acetonitrile)",
                frozenset(["S=O stretch (sulfones)", "C-H stretch (alkanes)"]): "Sulfone (e.g., Sulfolane) or Sulfoxide",
                frozenset(["C-H out-of-plane bend (aromatics)", "C-H bend (aromatics)"]): "Aromatic Compound (e.g., Benzene)",
                frozenset(["P=O stretch (phosphates)", "O-H bend (carboxylic acids)"]): "Phosphate Ester",
                frozenset(["C-I stretch (haloalkanes)", "C-H stretch (alkanes)"]): "Haloalkane (e.g., Iodoform)",
                frozenset(["C-Br stretch (haloalkanes)", "C-H stretch (alkanes)"]): "Haloalkane (e.g., Bromoform)",
                frozenset(["Si-O stretch (silicates, silicones)", "C-H stretch (alkanes)"]),
                frozenset(["Si-O stretch (silicates, silicones)", "C-H stretch (alkanes)"]): "Silicone (e.g., Polydimethylsiloxane)",
                frozenset(["O-H stretch (carboxylic acids)", "C=O stretch (carbonyl)"]): "Carboxylic Acid (e.g., Acetic Acid)",
                frozenset(["O-H stretch (carboxylic acids)", "C-O stretch (alcohols, ethers)"]): "Carboxylic Acid",
                frozenset(["N-H stretch (amines, high range)", "C=O stretch (carbonyl)"]): "Amide (e.g., Acetamide)",
                frozenset(["C=C-H out-of-plane bend (alkenes)", "C=C stretch (alkenes)"]): "Alkene (e.g., Butene)",
                frozenset(["C=O stretch (carbonyl)", "C-O stretch (alcohols, ethers)"]): "Ester (e.g., Ethyl Acetate)",
                frozenset(["C-Cl stretch (haloalkanes)", "C-H stretch (alkanes)"]): "Haloalkane (e.g., Chloroform)",
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

            # Optionally, use GPT-3.5 to deduce possible molecules
            if st.button("Ask AI for possible molecule"):
                ai_deduction = get_gpt3_deduction(identified_groups)
                st.write(f"AI suggestion: {ai_deduction}")
        else:
            st.write("No common functional groups identified.")
    else:
        st.write("No peaks were detected. Consider adjusting the peak detection parameters or verifying the dataset.")
