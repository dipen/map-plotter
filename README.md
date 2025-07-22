# City Asset Mapper (Streamlit)

A Streamlit app to upload an Excel file with columns `state`, `city`, and `count`, geocode the cities, and display asset counts on an interactive map.

## Usage

1. Upload your Excel file (`.xlsx`) with columns:
   - `state`
   - `city`
   - `count`

2. The app will geocode cities and display the asset distribution on a map.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud

1. Push this repo to GitHub.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud).
3. Link your repo and deploy!

## Notes

- Geocoding uses [Nominatim](https://nominatim.org/) and is rate-limited.
- Only cities that can be geocoded will appear on the map.