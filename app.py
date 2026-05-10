import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Migori GIS Valuation Pro", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stButton>button { background-color: #1a5276; color: white; border-radius: 8px; }
    .main { background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🗺️ Migori County Spatial Data Infrastructure")
st.markdown("### Land Valuation & Revenue Management Portal")

# --- SESSION STATE ---
if 'sync_complete' not in st.session_state:
    st.session_state.sync_complete = False

# --- SIDEBAR CONTROLS ---
st.sidebar.title("🛠️ Control Panel")

# 1. ARDHISASA INTEGRATION BRIDGE
st.sidebar.subheader("Data Synchronization")
if st.sidebar.button("Sync with National Cadastre (ArdhiSasa)"):
    with st.sidebar.status("Authenticating Gateway...", expanded=True) as status:
        time.sleep(1)
        st.write("🛰️ Pulling Parcel Geometry...")
        time.sleep(2)
        status.update(label="Sync Successful!", state="complete")
    st.session_state.sync_complete = True

# 2. LAYER CONTROLS (Manual Uploads)
st.sidebar.divider()
st.sidebar.subheader("Layer Uploads")
up_roads = st.sidebar.file_uploader("Upload Roads (.geojson)", type=['geojson'])
up_buildings = st.sidebar.file_uploader("Upload Buildings (.geojson)", type=['geojson'])

# --- MAP ENGINE ---
def create_map():
    # Centered on Migori Town
    m = folium.Map(location=[-1.063, 34.473], zoom_start=15, tiles=None)

    # A. BASE LAYERS (The Toggle Options)
    folium.TileLayer('OpenStreetMap', name="Standard Street Map").add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite Imagery (High Res)',
        overlay=False,
        control=True
    ).add_to(m)
    folium.TileLayer('Stamen Terrain', name="Terrain/Topography").add_to(m)

    # B. MOCK PARCEL LAYER (Appears after Sync)
    if st.session_state.sync_complete:
        # We create a FeatureGroup for Parcels
        fg_parcels = folium.FeatureGroup(name="Cadastral Parcels")
        
        # Generating 4 mock parcels around Migori center
        parcels = [
            {"coords": [[-1.062, 34.472], [-1.062, 34.474], [-1.064, 34.474], [-1.064, 34.472]], "id": "MIG/SUNA/001", "val": "1.2M"},
            {"coords": [[-1.064, 34.472], [-1.064, 34.474], [-1.066, 34.474], [-1.066, 34.472]], "id": "MIG/SUNA/002", "val": "0.8M"},
        ]
        
        for p in parcels:
            folium.Polygon(
                locations=p['coords'],
                color="yellow",
                weight=2,
                fill=True,
                fill_color="orange",
                fill_opacity=0.2,
                tooltip=f"Parcel ID: {p['id']}",
                popup=f"<b>Current Valuation:</b> KSh {p['val']}"
            ).add_to(fg_parcels)
        
        fg_parcels.add_to(m)

    # C. ADD LAYER CONTROL (This is the magic button)
    folium.LayerControl().add_to(m)
    return m

# --- DISPLAY ---
col1, col2 = st.columns([3, 1])

with col1:
    st_map = create_map()
    st_folium(st_map, width="100%", height=600)

with col2:
    st.info("💡 **Interview Tip:**")
    st.write("""
    Toggle the icon on the top-right of the map to switch between **Satellite** (for identifying illegal structures) and **Terrain** (for environmental planning). 
    
    Clicking 'Sync' simulates the retrieval of the **Valuation Roll** directly from the National Land Information Management System.
    """)
    
    if st.session_state.sync_complete:
        st.metric("Total Parcels Indexed", "1,240")
        st.metric("Potential Revenue (OSR)", "KSh 14.2M")
