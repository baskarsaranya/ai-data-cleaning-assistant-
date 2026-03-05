SUPPLY CHAIN DATA ASSISTANT
============================
Built by: Saranya Baskar
Version: 1.0 (MVP)
Date: March 2026

WHAT IT DOES:
-------------
Automatically cleans supply chain CSV data and generates
insights across supplier performance, quality and shipping.

HOW TO RUN:
-----------
1. Open Command Prompt
2. cd C:\SupplyChainAssistant\app
3. streamlit run app.py
4. Open browser at http://localhost:8501

FEATURES:
---------
- Auto data cleaning pipeline (7 steps)
- Automatic visualizations
- Supplier performance analysis
- Quality & inspection analysis  
- Shipping & route analysis
- Download cleaned data as CSV

PROJECT STRUCTURE:
------------------
data/        - Raw input data
notebooks/   - Development notebooks
src/         - pipeline.py (core logic)
outputs/     - Cleaned data and charts
app/         - app.py (Streamlit UI)

VERSION 2 PLANNED:
------------------
- Smart column detection for any dataset
- Chat with your data feature
- ML model recommendations
- PDF report export