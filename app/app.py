import streamlit as st
import pandas as pd
import sys
import os

sys.path.append('C:/SupplyChainAssistant/src')
from pipeline import (
    run_pipeline,
    plot_numeric_distributions,
    plot_categorical_distributions,
    plot_correlation_heatmap,
    analyze_supplier_performance,
    analyze_quality,
    analyze_shipping,
    generate_insights_summary
)

# Page configuration
st.set_page_config(
    page_title="Supply Chain Assistant",
    page_icon="🚚",
    layout="wide"
)

# Header
st.title("🚚 Supply Chain Data Assistant")
st.markdown("Upload your supply chain data and get instant cleaning, analysis and insights.")
st.divider()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/supply-chain.png", width=80)
    st.title("Navigation")
    page = st.radio("Go to", [
        "📁 Upload & Clean",
        "📊 Visualizations", 
        "💡 Insights"
    ])
    st.divider()
    st.markdown("**About**")
    st.markdown("This tool automatically cleans your supply chain data and generates insights.")

# Session state to store data between pages
if 'df_clean' not in st.session_state:
    st.session_state.df_clean = None
if 'df_original' not in st.session_state:
    st.session_state.df_original = None

# ============================================================
# PAGE 1 - UPLOAD AND CLEAN
# ============================================================
if page == "📁 Upload & Clean":
    st.header("📁 Upload & Clean Your Data")
    
    uploaded_file = st.file_uploader(
        "Upload your CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Supported formats: CSV, Excel"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_path = f'C:/SupplyChainAssistant/data/temp_{uploaded_file.name}'
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Show original data preview
        st.subheader("Original Data Preview")
        if uploaded_file.name.endswith('.csv'):
            df_original = pd.read_csv(temp_path)
        else:
            df_original = pd.read_excel(temp_path)
        
        st.dataframe(df_original.head(10), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", df_original.shape[0])
        with col2:
            st.metric("Total Columns", df_original.shape[1])
        with col3:
            st.metric("Missing Values", df_original.isnull().sum().sum())
        
        st.divider()
        
        # Clean button
        if st.button("🧹 Clean My Data", type="primary", use_container_width=True):
            with st.spinner("Running cleaning pipeline..."):
                df_clean = run_pipeline(temp_path)
                st.session_state.df_clean = df_clean
                st.session_state.df_original = df_original
            
            st.success("✅ Data cleaned successfully!")
            
            # Show cleaning summary
            st.subheader("Cleaned Data Preview")
            st.dataframe(df_clean.head(10), use_container_width=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", df_clean.shape[0])
            with col2:
                st.metric("Columns", df_clean.shape[1])
            with col3:
                st.metric("Columns Removed", 
                         df_original.shape[1] - df_clean.shape[1])
            with col4:
                st.metric("Missing Values", 
                         df_clean.isnull().sum().sum())
            
            # Download cleaned data
            st.divider()
            csv = df_clean.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Cleaned Data",
                data=csv,
                file_name="supply_chain_cleaned.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.info("👈 Now go to Visualizations or Insights in the sidebar!")
    
    else:
        # Show instructions when no file uploaded
        st.info("👆 Upload a CSV or Excel file to get started")
        
        st.subheader("What this tool does:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🧹 Clean")
            st.markdown("Fixes column names, data types, missing values, duplicates and inconsistencies automatically")
        with col2:
            st.markdown("### 📊 Visualize")
            st.markdown("Generates distribution charts, categorical breakdowns and correlation heatmaps")
        with col3:
            st.markdown("### 💡 Insights")
            st.markdown("Detects supplier issues, quality problems and shipping inefficiencies automatically")

# ============================================================
# PAGE 2 - VISUALIZATIONS
# ============================================================
elif page == "📊 Visualizations":
    st.header("📊 Data Visualizations")
    
    if st.session_state.df_clean is None:
        st.warning("⚠️ Please upload and clean your data first!")
        st.info("👈 Go to Upload & Clean in the sidebar")
    else:
        df = st.session_state.df_clean
        
        tab1, tab2, tab3 = st.tabs([
            "Numeric Distributions",
            "Categorical Breakdown", 
            "Correlation Heatmap"
        ])
        
        with tab1:
            st.subheader("Numeric Column Distributions")
            fig = plot_numeric_distributions(df)
            st.pyplot(fig)
        
        with tab2:
            st.subheader("Categorical Column Breakdown")
            fig = plot_categorical_distributions(df)
            st.pyplot(fig)
        
        with tab3:
            st.subheader("Correlation Heatmap")
            fig = plot_correlation_heatmap(df)
            st.pyplot(fig)

# ============================================================
# PAGE 3 - INSIGHTS
# ============================================================
elif page == "💡 Insights":
    st.header("💡 Supply Chain Insights")
    
    if st.session_state.df_clean is None:
        st.warning("⚠️ Please upload and clean your data first!")
        st.info("👈 Go to Upload & Clean in the sidebar")
    else:
        df = st.session_state.df_clean
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏭 Supplier",
            "🔍 Quality",
            "🚚 Shipping",
            "📋 Summary"
        ])
        
        with tab1:
            st.subheader("Supplier Performance Analysis")
            fig, supplier_insights = analyze_supplier_performance(df)
            st.pyplot(fig)
            st.subheader("Key Findings")
            for insight in supplier_insights:
                st.warning(f"→ {insight}")
        
        with tab2:
            st.subheader("Quality & Inspection Analysis")
            fig, quality_insights = analyze_quality(df)
            st.pyplot(fig)
            st.subheader("Key Findings")
            for insight in quality_insights:
                st.error(f"→ {insight}") if "CRITICAL" in insight else st.warning(f"→ {insight}")
        
        with tab3:
            st.subheader("Shipping & Route Analysis")
            fig, shipping_insights = analyze_shipping(df)
            st.pyplot(fig)
            st.subheader("Key Findings")
            for insight in shipping_insights:
                st.warning(f"→ {insight}")
        
        with tab4:
            st.subheader("Complete Insights Summary")
            all_insights = supplier_insights + quality_insights + shipping_insights
            st.metric("Total Issues Detected", len(all_insights))
            st.divider()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("### 🏭 Supplier")
                for i in supplier_insights:
                    st.warning(i)
            with col2:
               st.markdown("### 🔍 Quality")
               for i in quality_insights:
                   if "CRITICAL" in i:
                       st.error(i)
                   else:
                       st.warning(i)
            with col3:
                st.markdown("### 🚚 Shipping")
                for i in shipping_insights:
                    st.warning(i)