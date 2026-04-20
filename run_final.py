"""
NetGraphIQ - Final Intelligent Dashboard Launcher
Run with: streamlit run run_final.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.final_dashboard import main

if __name__ == "__main__":
    main()