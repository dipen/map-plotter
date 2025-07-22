import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import subprocess

def get_git_commit_info():
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("utf-8").strip()
        commit_msg = subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).decode("utf-8").strip()
        return commit_hash, commit_msg
    except Exception:
        return None, None

commit_hash, commit_msg = get_git_commit_info()

if commit_hash and commit_msg:
    st.markdown(f"**Version:** `{commit_hash}`<br>**Message:** {commit_msg}", unsafe_allow_html=True)
else:
    st.markdown("**Version information not available.**")

st.title("Asset Location Mapper")

st.markdown("""
Upload an Excel file with the following columns:
- **state**: State name (Redundant)
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
            location = geocode(f"{row['city']}, {row['state']}, India")
            if location:
                return pd.Series([location.latitude, location.longitude])
            else:
                return pd.Series([None, None])
        
        st.info("Geocoding cities. This may take a while for large files.")
        df[['lat', 'lon']] = df.apply(get_lat_lon, axis=1)
        df = df.dropna(subset=['lat', 'lon'])
        
        if not df.empty:
            # India bounds: approx lat 8-37, lon 68-97
            india_center = [22.5937, 78.9629]
            india_bounds = [[8, 68], [37, 97]]
            m = folium.Map(
                location=india_center,
                zoom_start=5,
                min_zoom=4,
                max_zoom=8,
                max_bounds=True,
                dragging=False,
            )
            m.fit_bounds(india_bounds)
            
            min_radius = 5
            max_radius = 16   # biggest dot is not too big
            max_count = df['count'].max()
            for _, row in df.iterrows():
                # Scale radius between min_radius and max_radius
                radius = min_radius + (max_radius - min_radius) * (row['count'] / max_count)
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=radius,
                    popup=f"{row['city']}, {row['state']}: {row['count']}",
                    color='blue',
                    fill=True,
                    fill_color='blue'
                ).add_to(m)
            st.subheader("Asset Map")
            # Make map viewport bigger for better visibility
            st_folium(m, width=1000, height=700)
        else:
            st.warning("No valid city locations found in your data.")