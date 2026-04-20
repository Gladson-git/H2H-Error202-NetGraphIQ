"""
Simple NetGraphIQ Dashboard - Minimal Working Version
Run with: streamlit run simple_dashboard.py
"""

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import random

# Page config
st.set_page_config(
    page_title="NetGraphIQ - Network Monitor",
    page_icon="📡",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.devices = {}
    st.session_state.connections = []
    st.session_state.anomalies = []

# Title
st.title("📡 NetGraphIQ: Network Monitoring Platform")
st.markdown("*Simple working version - Debug mode*")

# Sidebar
with st.sidebar:
    st.header("🎮 Controls")
    
    if st.button("🔄 Generate Network", use_container_width=True):
        st.success("Network generation clicked!")
        st.session_state.generated = True
    
    st.divider()
    st.info("Debug Mode - Checking imports...")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌐 Network Status")
    
    # Import check
    try:
        import networkx as nx
        st.success("✅ NetworkX imported")
    except Exception as e:
        st.error(f"❌ NetworkX import failed: {e}")
    
    try:
        import matplotlib
        st.success("✅ Matplotlib imported")
    except Exception as e:
        st.error(f"❌ Matplotlib import failed: {e}")
    
    # Create a simple graph for testing
    st.subheader("Test Graph")
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Create a simple test graph
    G = nx.Graph()
    G.add_edge("Router", "Core-Switch")
    G.add_edge("Core-Switch", "Access-Switch")
    G.add_edge("Access-Switch", "IoT-Device")
    
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=2000, font_size=10, font_weight='bold', ax=ax)
    ax.set_title("Test Network Topology")
    
    st.pyplot(fig)

with col2:
    st.subheader("📊 System Status")
    
    st.metric("Status", "Running", delta="✅")
    st.metric("Time", datetime.now().strftime("%H:%M:%S"))
    
    st.subheader("📦 Installed Packages")
    packages = ["streamlit", "networkx", "matplotlib", "numpy", "pandas", "plotly"]
    for pkg in packages:
        try:
            __import__(pkg)
            st.success(f"✅ {pkg}")
        except ImportError:
            st.error(f"❌ {pkg}")

# Bottom section
st.divider()
st.subheader("🚨 Recent Activity")
st.info("Dashboard is running in debug mode. Check terminal for errors.")

if st.button("Test Button"):
    st.success("Button clicked - Dashboard is working!")