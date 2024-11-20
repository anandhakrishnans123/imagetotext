import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Streamlit UI for synthetic data generation
st.title("Synthetic Data Generator")

# Upload the Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Load original data from uploaded file
    original_data = pd.read_excel(uploaded_file)
    st.success("File successfully loaded!")
    st.write("Preview of Original Data:", original_data.head())
    
    # Input for the number of synthetic rows to generate
    num_synthetic_rows = st.number_input("Number of synthetic rows to generate", min_value=1, step=1, value=10)
    
    if st.button("Generate Synthetic Data"):
        # Initialize an empty dictionary to store synthetic data
        synthetic_data = {}

        # Generate synthetic data dynamically based on column types
        for column in original_data.columns:
            st.write(f"Processing column: {column}")
            if pd.api.types.is_numeric_dtype(original_data[column]):  # For numeric columns
                synthetic_data[column] = np.random.normal(
                    loc=original_data[column].mean(),
                    scale=original_data[column].std(),
                    size=num_synthetic_rows
                )
            elif isinstance(original_data[column].dtype, pd.CategoricalDtype) or original_data[column].dtype == 'object':  # For categorical or string columns
                unique_values = original_data[column].dropna().unique()
                if len(unique_values) > 0:  # Check if there are valid unique values
                    probabilities = original_data[column].dropna().value_counts(normalize=True).reindex(unique_values, fill_value=0).values
                    synthetic_data[column] = np.random.choice(
                        unique_values,
                        size=num_synthetic_rows,
                        p=probabilities
                    )
                else:
                    synthetic_data[column] = [None] * num_synthetic_rows
            elif pd.api.types.is_datetime64_any_dtype(original_data[column]):  # For datetime columns
                if not original_data[column].isna().all():  # Check if the column has valid dates
                    synthetic_data[column] = pd.to_datetime(
                        np.random.choice(
                            pd.date_range(
                                start=original_data[column].min(),
                                end=original_data[column].max()
                            ),
                            size=num_synthetic_rows
                        )
                    )
                else:
                    synthetic_data[column] = [None] * num_synthetic_rows
            else:
                synthetic_data[column] = [None] * num_synthetic_rows  # Handle unsupported columns

        # Convert the synthetic data dictionary to a DataFrame
        synthetic_data_df = pd.DataFrame(synthetic_data)
        st.write("Generated Synthetic Data Preview:", synthetic_data_df)

        # Combine original and synthetic data
        augmented_data = pd.concat([original_data, synthetic_data_df], ignore_index=True)
        st.write("Augmented Data Preview:", augmented_data)

        # Save combined data to a single sheet Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            augmented_data.to_excel(writer, index=False, sheet_name="Augmented Data")

        output.seek(0)
        st.download_button(
            label="Download Augmented Data",
            data=output,
            file_name="augmented_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success(f"{num_synthetic_rows} synthetic rows added successfully!")
