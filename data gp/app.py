import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.title("📡 NASA POWER API - Data Extractor")

# Input coordinates
lat = st.number_input("Latitude", value=30.0444)
lon = st.number_input("Longitude", value=31.2357)

# Select date range
start_date = st.date_input("Start Date", value=datetime(2023, 1, 1))
end_date = st.date_input("End Date", value=datetime(2023, 12, 31))

# Select parameters
all_parameters = {
    "ALLSKY_SFC_SW_DWN": "Solar Irradiance",
    "WS2M": "Wind Speed at 2m",
    "T2M": "Air Temperature at 2m",
    "RH2M": "Relative Humidity at 2m"
}

selected_params = st.multiselect("Select Parameters", options=list(all_parameters.keys()), default=["ALLSKY_SFC_SW_DWN"])

# When button is clicked
if st.button("Fetch Data"):
    if not selected_params:
        st.warning("Please select at least one parameter.")
    else:
        try:
            base_url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
            params = {
                "start": start_date.strftime("%Y%m%d"),
                "end": end_date.strftime("%Y%m%d"),
                "latitude": lat,
                "longitude": lon,
                "parameters": ",".join(selected_params),
                "format": "JSON",
                "community": "RE"
            }

            response = requests.get(base_url, params=params)
            data = response.json()

            # Parse JSON to DataFrame
            raw_data = data['properties']['parameter']
            time_keys = list(data['properties']['parameter'][selected_params[0]].keys())

            df = pd.DataFrame({"datetime": time_keys})
            for param in selected_params:
                values = raw_data[param]
                df[param] = df["datetime"].map(values)

            df["datetime"] = pd.to_datetime(df["datetime"], format="%Y%m%d%H")
            df = df.set_index("datetime")

            st.success("✅ Data fetched successfully!")
            st.dataframe(df)

            # Allow download
            csv = df.reset_index().to_csv(index=False)
            st.download_button("Download CSV", data=csv, file_name="nasa_power_data.csv", mime="text/csv")

        except Exception as e:
            st.error(f"⚠ Error parsing data: {e}")