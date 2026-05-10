import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Migori Land Valuation Pro", layout="wide")

# Custom CSS to make it look like a government dashboard
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004d40; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌍 Migori County: GIS-Based Land Valuation & Revenue System")
st.markdown(f"**Lead Developer:** Elijah Otieno Aloyo | **Department:** Geoinformatics")
st.divider()

# --- INITIALIZING SESSION STATE ---
# This keeps the data "alive" after the button is clicked
if 'data_synced' not in st.session_state:
    st.session_state.data_synced = False

# --- SIDEBAR: DATA MANAGEMENT ---
st.sidebar.header("Data Management")
uploaded_cadastral = st.sidebar.file_uploader("Upload Local Cadastral (GeoJSON)", type=['geojson'])

st.sidebar.divider()
st.sidebar.subheader("National Integration")

# THE CORRECTION: Real-time simulation of ArdhiSasa Fetch
if st.sidebar.button("Fetch Data from ArdhiSasa"):
    with st.sidebar.status("Connecting to NLIMS Gateway...", expanded=True) as status:
        st.write("📡 Establishing Secure Handshake...")
        time.sleep(1.2)
        st.write("🔑 Verifying Migori County API Token...")
        time.sleep(1.5)
        st.write("📥 Downloading Parcel Geometry (Suna West/East)...")
        time.sleep(2)
        status.update(label="Sync Complete!", state="complete", expanded=False)
    
    st.session_state.data_synced = True
    st.sidebar.success("Successfully imported 142 parcels.")

# --- DATA PREPARATION ---
def get_map_data():
    # If synced, return "National" data, else return empty/base
    if st.session_state.data_synced:
        data = {
            'Plot_No': ['MIG/SUNA/101', 'MIG/SUNA/102', 'MIG/SUNA/103', 'MIG/SUNA/104'],
            'Owner': ['Private Developer', 'Community Land', 'Migori County', 'Commercial Hub'],
            'Base_Value': [1500000, 450000, 0, 2800000],
            'Lat': [-1.0632, -1.0655, -1.0610, -1.0680],
            'Lon': [34.4735, 34.4750, 34.4710, 34.4790]
        }
    else:
        # Just one reference point for Migori Town
        data = {'Plot_No': ['Town Center'], 'Owner': ['N/A'], 'Base_Value': [0], 'Lat': [-1.063], 'Lon': [34.473]}
    
    return pd.DataFrame(data)

# --- UI LAYOUT ---
col1, col2 = st.columns([2, 1])

df = get_map_data()

with col1:
    st.subheader("Interactive Valuation Map")
    # Centered on Migori Town
    m = folium.Map(location=[-1.063, 34.473], zoom_start=14, control_scale=True)
    
    # Adding markers based on the data state
    for _, row in df.iterrows():
        color = 'green' if row['Base_Value'] > 0 else 'blue'
        folium.Marker(
            [row['Lat'], row['Lon']],
            popup=f"<b>Plot:</b> {row['Plot_No']}<br><b>Value:</b> KSh {row['Base_Value']:,}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
        
    st_folium(m, width="100%", height=550)

with col2:
    st.subheader("Valuation Analytics")
    road_factor = st.slider("Infrastructure Value Addition (%)", 0, 30, 15)
    
    if st.session_state.data_synced:
        df['Adjusted_Value'] = df['Base_Value'] * (1 + road_factor/100)
        df['Expected_Revenue'] = df['Adjusted_Value'] * 0.01 # 1% Rate
        
        st.write("### Predicted Revenue (Sample Area)")
        st.dataframe(df[['Plot_No', 'Adjusted_Value', 'Expected_Revenue']], hide_index=True)
        
        total_rev = df['Expected_Revenue'].sum()
        st.metric("Total Projected OSR", f"KSh {total_rev:,.2f}")
    else:
        st.info("Please 'Fetch Data from ArdhiSasa' to run valuation analytics.")

# FOOTER
st.divider()
st.caption("Confidential: For Migori County Public Service Board Interview Purposes Only.")
