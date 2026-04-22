"""
NetGraphIQ - Complete Integrated System
Run with: streamlit run run_integrated.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.integrated_dashboard import main

if __name__ == "__main__":
    main()