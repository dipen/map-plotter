import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

st.title("City Asset Mapper")

st.markdown("""
Upload an Excel file with the following columns:
- **state**: State name
- **city**: City name
- **count**: Number of assets in that city
""")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    required_columns = {"state", "city", "count"}
    if not required_columns.issubset(df.columns.str.lower()):
        st.error("Excel file must have columns: state, city, count")
    else:
        # Normalize columns to lowercase
        df.columns = [c.lower() for c in df.columns]
        
        st.write("Preview of data:")
        st.dataframe(df.head())
        
        # Geocoding
        geolocator = Nominatim(user_agent="streamlit_asset_mapper")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        
        def get_lat_lon(row):
            location = geocode(f"{row['city']}, {row['state']}")
            if location:
                return pd.Series([location.latitude, location.longitude])
            else:
                return pd.Series([None, None])
        
        st.info("Geocoding cities. This may take a while for large files.")
        df[['lat', 'lon']] = df.apply(get_lat_lon, axis=1)
        df = df.dropna(subset=['lat', 'lon'])
        
        if not df.empty:
            center = [df['lat'].mean(), df['lon'].mean()]
            m = folium.Map(location=center, zoom_start=5)
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=max(5, min(15, row['count']/10)),
                    popup=f"{row['city']}, {row['state']}: {row['count']}",
                    color='blue',
                    fill=True,
                    fill_color='blue'
                ).add_to(m)
            st.subheader("Asset Map")
            st_folium(m, width=700, height=500)
        else:
            st.warning("No valid city locations found in your data.")