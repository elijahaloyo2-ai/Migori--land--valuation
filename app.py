import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point

# --- CONFIGURATION ---
st.set_page_config(page_title="Migori Land Valuation Pro", layout="wide")

st.title("🌍 Migori County: GIS-Based Land Valuation & Revenue System")
st.markdown("""
    *Developed by Elijah Otieno Aloyo (Geoinformatics Professional)*
    ---
""")

# --- SIDEBAR: DATA INPUTS ---
st.sidebar.header("Data Management")
uploaded_cadastral = st.sidebar.file_uploader("Upload Cadastral (GeoJSON/SHP)", type=['geojson', 'json', 'zip'])
uploaded_revenue = st.sidebar.file_uploader("Upload Revenue Registry (CSV)", type=['csv'])

# --- MOCK DATA FOR DEMO ---
# If no data is uploaded, we create a sample for the interview
def get_sample_data():
    data = {
        'Plot_No': ['MIG/001', 'MIG/002', 'MIG/003'],
        'Owner': ['John Doe', 'Jane Smith', 'County Govt'],
        'Base_Value': [500000, 1200000, 0],
        'Latitude': [-1.063, -1.065, -1.060],
        'Longitude': [34.473, 34.475, 34.470]
    }
    df = pd.DataFrame(data)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    return gdf

# --- CORE LOGIC: VALUATION ALGORITHM ---
def calculate_valuation(gdf, road_proximity_bonus):
    # Strategic Logic: Distance-based value increase
    # In a real app, you'd calculate distance to the 'Roads' layer
    gdf['Adjusted_Value'] = gdf['Base_Value'] * (1 + road_proximity_bonus)
    gdf['Estimated_Tax'] = gdf['Adjusted_Value'] * 0.01 # 1% Land Rate
    return gdf

# --- UI LAYOUT ---
col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("Valuation Parameters")
    road_bonus = st.slider("Road Infrastructure Bonus (%)", 0, 50, 10) / 100
    
    if st.button("Run Mass Appraisal"):
        gdf = get_sample_data()
        results = calculate_valuation(gdf, road_bonus)
        st.success("Valuation Roll Updated!")
        st.write(results[['Plot_No', 'Adjusted_Value', 'Estimated_Tax']])

with col1:
    st.subheader("Interactive County Map")
    m = folium.Map(location=[-1.063, 34.473], zoom_start=14)
    
    # Logic to display uploaded data
    display_data = get_sample_data()
    for _, row in display_data.iterrows():
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=f"Plot: {row['Plot_No']}<br>Owner: {row['Owner']}",
            tooltip="Click for Valuation"
        ).add_to(m)
        
    st_folium(m, width=700, height=500)

# --- ARDHISASA INTEGRATION (CONCEPTUAL) ---
st.sidebar.divider()
st.sidebar.subheader("ArdhiSasa API Bridge")
if st.sidebar.button("Fetch Cadastral Data"):
    # This is where the API call would go
    st.sidebar.info("Awaiting API Token from National Land Information Management System (NLIMS)")
    # Example Request Logic:
    # response = requests.get("https://api.ardhisasa.go.ke/v1/parcels", headers={"Auth": "Bearer YOUR_TOKEN"})
