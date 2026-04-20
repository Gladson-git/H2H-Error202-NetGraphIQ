"""
Debug version of NetGraphIQ Dashboard
Run with: streamlit run run_dashboard_debug.py
"""

import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 Starting dashboard debug mode...")
    
    try:
        print("📡 Importing modules...")
        import streamlit as st
        print("✅ Streamlit imported")
        
        from src.ui.dashboard import LiveDashboard
        print("✅ Dashboard module imported")
        
        print("🎨 Creating dashboard instance...")
        dashboard = LiveDashboard()
        print("✅ Dashboard instance created")
        
        print("🏃 Running dashboard...")
        dashboard.run()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"\nFull traceback:")
        traceback.print_exc()
        
        # Show error in Streamlit as well
        import streamlit as st
        st.error(f"Dashboard Error: {str(e)}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()