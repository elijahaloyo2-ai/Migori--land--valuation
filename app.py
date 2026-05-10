import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Migori GIS Valuation Pro", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .stButton>button { background-color: #1a5276; color: white; border-radius: 8px; font-weight: bold; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🗺️ Migori County Spatial Data Infrastructure")
st.markdown("### Land Valuation & Revenue Management Portal")
st.markdown("*Lead Developer: Elijah Otieno Aloyo*")
st.divider()

# --- 2. SESSION STATE MANAGEMENT ---
if 'sync_complete' not in st.session_state:
    st.session_state.sync_complete = False

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.title("🛠️ System Control")

st.sidebar.subheader("National Gateway")
if st.sidebar.button("Sync with ArdhiSasa (NLIMS)"):
    with st.sidebar.status("Authenticating Gateway...", expanded=True) as status:
        time.sleep(1)
        st.write("🛰️ Pulling Parcel Geometry for Migori...")
        time.sleep(1.5)
        status.update(label="Sync Successful!", state="complete", expanded=False)
    st.session_state.sync_complete = True

st.sidebar.divider()
st.sidebar.subheader("Layer Visualization")
st.sidebar.info("Use the layer control icon (top-right of map) to toggle between Satellite, Terrain, and Street views.")

# --- 4. MAP ENGINE ---
def create_map():
    # Centered on Migori Town center
    m = folium.Map(location=[-1.063, 34.473], zoom_start=15, tiles=None)

    # BASE LAYER 1: OpenStreetMap (Standard)
    folium.TileLayer(
        'OpenStreetMap', 
        name="Standard Street Map",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    ).add_to(m)
    
    # BASE LAYER 2: Satellite (Esri World Imagery)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        name='Satellite Imagery',
        attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        overlay=False,
        control=True
    ).add_to(m)

    # BASE LAYER 3: Terrain (OpenTopoMap)
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        name="Terrain/Topography",
        attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
        overlay=False,
        control=True
    ).add_to(m)

    # DYNAMIC DATA: MOCK PARCEL LAYER (Visible only after sync)
    if st.session_state.sync_complete:
        fg_parcels = folium.FeatureGroup(name="Cadastral Parcels")
        
        # Simulated parcels around Migori Suna West/East
        parcels = [
            {"coords": [[-1.062, 34.472], [-1.062, 34.474], [-1.064, 34.474], [-1.064, 34.472]], "id": "MIG/SUNA/001", "val": 1250000},
            {"coords": [[-1.064, 34.472], [-1.064, 34.474], [-1.066, 34.474], [-1.066, 34.472]], "id": "MIG/SUNA/002", "val": 980000},
            {"coords": [[-1.061, 34.475], [-1.061, 34.477], [-1.063, 34.477], [-1.063, 34.475]], "id": "MIG/SUNA/003", "val": 3500000},
        ]
        
        for p in parcels:
            folium.Polygon(
                locations=p['coords'],
                color="yellow",
                weight=2,
                fill=True,
                fill_color="orange",
                fill_opacity=0.3,
                tooltip=f"Parcel ID: {p['id']}",
                popup=f"<b>Current Valuation:</b> KSh {p['val']:,}"
            ).add_to(fg_parcels)
        
        fg_parcels.add_to(m)

    # ADD THE LAYER SWITCHER
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    return m

# --- 5. UI LAYOUT ---
col_map, col_stats = st.columns([3, 1])

with col_map:
    # Display the map
    current_map = create_map()
    st_folium(current_map, width="100%", height=600)

with col_stats:
    st.subheader("Market Insights")
    if not st.session_state.sync_complete:
        st.warning("Awaiting National Sync to generate Valuation Roll.")
    else:
        st.success("Valuation Data Active")
        st.metric("Total Parcels", "3 Selected")
        st.metric("Aggregate Value", "KSh 5.73M")
        
        st.divider()
        st.write("**Revenue Forecast**")
        road_dev = st.checkbox("Apply Road Proximity Bonus (15%)")
        base_rev = 5730000 * 0.01 # 1% rate
        if road_dev:
            base_rev *= 1.15
        st.write(f"Estimated Revenue: **KSh {base_rev:,.2f}**")

st.divider()
st.caption("Developed for Migori County Public Service Board (JG 04 Interview Demonstration).")
